"""
modules/improver.py — Gereksinim İyileştirme Modülü
Sorumlu: Eren Eyyüpkoca

Açıklama:
"Hızlı", "kolay" gibi ölçülemeyen (muğlak) ifadeleri tespit eder ve bu ifadeleri
teknik, ölçülebilir kriterlere dönüştürmek için LLM önerileri üretir.
"""

from __future__ import annotations

import concurrent.futures
import re
from typing import Any, Optional

from core.models import Requirement

from .improver_prompts import (
    build_improvement_system_prompt,
    build_improvement_user_prompt,
    build_improvement_batch_system_prompt,
    build_improvement_batch_user_prompt,
)
from .llm_client import LLMClient, LLMClientError
from .llm_response_utils import extract_json_object
from .logging_utils import get_module_logger

_log = get_module_logger("improver")

_NO_VAGUE_REASON = (
    "Gereksinim metninde muğlak anahtar kelime tespit edilmedi; "
    "LLM çağrısı atlandı (token tasarrufu)."
)

# Ön filtre: yalnızca bu kelimelerden en az biri metinde geçerse LLM çağrılır.
vague_keywords = frozenset(
    {
        # Türkçe — performans
        "hızlı", "hızlıca",
        # Türkçe — kullanılabilirlik
        "kolay", "kolayca", "kolaylıkla", "sezgisel", "kullanıcı dostu", "kullanışlı",
        # Türkçe — genel kalite
        "iyi", "kötü", "basit", "güzel", "şık", "modern",
        # Türkçe — boyut
        "büyük", "küçük",
        # Türkçe — sağlamlık/güvenlik
        "güvenli", "sağlam", "kararlı", "stabil",
        # Türkçe — verimlilik/ölçek
        "verimli", "etkili", "esnek", "ölçeklenebilir", "performanslı",
        # İngilizce
        "fast", "quick", "simple", "easy", "good", "better", "best",
        "secure", "safe", "responsive", "scalable", "efficient",
        "robust", "user-friendly", "intuitive", "clean",
    }
)

# Önceden derlenmiş regex'ler (tek kelimelik anahtar kelimeler için)
_VAGUE_PATTERNS: list[tuple[str, re.Pattern]] = [
    (kw, re.compile(r"(?<!\w)" + re.escape(kw) + r"(?!\w)", re.IGNORECASE))
    for kw in vague_keywords
    if " " not in kw and "-" not in kw
]
_VAGUE_MULTIWORD: list[str] = [
    kw for kw in vague_keywords if " " in kw or "-" in kw
]


def _text_has_vague_keyword(text: str) -> bool:
    """Gereksinim metninde muğlak anahtar kelime var mı kontrol eder (kelime sınırı duyarlı)."""
    lower = (text or "").lower()
    for kw, pat in _VAGUE_PATTERNS:
        if pat.search(lower):
            return True
    return any(kw in lower for kw in _VAGUE_MULTIWORD)


def _detected_vague_terms(text: str) -> list[str]:
    """Metindeki tüm eşleşen muğlak anahtar kelimeleri döndürür."""
    lower = (text or "").lower()
    found: list[str] = []
    for kw, pat in _VAGUE_PATTERNS:
        if pat.search(lower):
            found.append(kw)
    for kw in _VAGUE_MULTIWORD:
        if kw in lower:
            found.append(kw)
    return found


def _coerce_str(value: Any, fallback: str) -> str:
    """
    LLM alanını güvenle stringe çevirir; boş veya hatalı tiplerde yedek değer döner.

    Parametreler:
        value: Ayrıştırılmış JSON alanı.
        fallback: Geçerli string yoksa kullanılacak değer.

    Döndürür:
        str: Kırpılmış metin veya `fallback`.
    """
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


_IMPROVER_CHUNK_SIZE = 20


class RequirementImprover:
    """
    Muğlak gereksinimleri ölçülebilir hale getirir.

    `improve` dönüşü `AnalysisReport.improvements` sözleşmesine uyar:
    en az `original`, `improved`, `reason` alanları.
    Muğlak gereksinimler chunk'lara bölünerek paralel LLM çağrılarıyla işlenir.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        """
        Parametreler:
            llm_client: Test veya özel konfigürasyon için dışarıdan enjekte edilen istemci.
        """
        self._llm_client = llm_client

    def _get_client(self) -> LLMClient:
        if self._llm_client is None:
            # Hız ve düşük maliyet için Gemini 2.5 Flash kullanıyoruz
            self._llm_client = LLMClient(model_name="google/gemini-2.5-flash")
        return self._llm_client

    def _process_chunk(self, chunk: list[Requirement]) -> dict[str, dict[str, str]]:
        """Tek bir chunk için LLM çağrısı yapar; {req_id: result} döner."""
        system_prompt = build_improvement_batch_system_prompt()
        user_prompt = build_improvement_batch_user_prompt([(r.id, r.text) for r in chunk])
        client = self._get_client()

        chunk_results: dict[str, dict[str, str]] = {}

        response = client.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata={"module": "improver", "action": "batch_vague_to_measurable"},
        )
        payload = extract_json_object(response.content)
        items = payload if isinstance(payload, list) else []

        returned_ids: set = set()
        for item in items:
            if not isinstance(item, dict):
                continue
            req_id = item.get("req_id", "")
            returned_ids.add(req_id)
            original = next((r.text.strip() for r in chunk if r.id == req_id), "")
            row: dict[str, Any] = {
                "original": original,
                "improved": _coerce_str(item.get("improved"), original),
                "reason": _coerce_str(item.get("reason"), "(Açıklama yok.)"),
            }
            if item.get("feasibility"):
                row["feasibility"] = _coerce_str(item["feasibility"], "")
            vt = item.get("vague_terms")
            if isinstance(vt, list):
                row["vague_terms"] = [str(v) for v in vt if v]
            chunk_results[req_id] = row

        for req in chunk:
            if req.id not in returned_ids:
                _log.warning("Chunk yanıtında req_id eksik | req_id={}", req.id)
                original = req.text.strip()
                chunk_results[req.id] = {
                    "original": original,
                    "improved": original,
                    "reason": "Toplu LLM yanıtında bu gereksinim döndürülmedi.",
                    "vague_terms": _detected_vague_terms(original),
                }

        return chunk_results

    def improve_batch(self, requirements: list[Requirement]) -> list[dict[str, str]]:
        """
        Muğlak gereksinimleri chunk'lara bölerek paralel LLM çağrılarıyla iyileştirir.

        Muğlak anahtar kelime içermeyen gereksinimler LLM'e gönderilmez.

        Parametreler:
            requirements: İyileştirilecek Requirement listesi.

        Döndürür:
            list[dict]: Her biri `original`, `improved`, `reason` içeren liste (giriş sırasıyla).
        """
        results: dict[str, dict[str, str]] = {}
        vague_reqs: list[Requirement] = []

        for req in requirements:
            original = (req.text or "").strip()
            if not original or not _text_has_vague_keyword(original):
                results[req.id] = {
                    "original": original,
                    "improved": original,
                    "reason": _NO_VAGUE_REASON,
                }
            else:
                vague_reqs.append(req)

        if vague_reqs:
            chunks = [vague_reqs[i:i + _IMPROVER_CHUNK_SIZE] for i in range(0, len(vague_reqs), _IMPROVER_CHUNK_SIZE)]

            if len(chunks) == 1:
                try:
                    results.update(self._process_chunk(chunks[0]))
                except (LLMClientError, ValueError) as exc:
                    _log.exception("İyileştirme chunk başarısız | hata={}", exc)
                    for req in chunks[0]:
                        original = req.text.strip()
                        results[req.id] = {"original": original, "improved": original, "reason": f"LLM hatası: {exc}"}
            else:
                _log.info("İyileştirme {} chunk'a bölündü, paralel işleniyor", len(chunks))
                with concurrent.futures.ThreadPoolExecutor(max_workers=len(chunks)) as executor:
                    futures = [executor.submit(self._process_chunk, chunk) for chunk in chunks]
                    for i, future in enumerate(futures):
                        try:
                            results.update(future.result())
                        except (LLMClientError, ValueError) as exc:
                            _log.warning("İyileştirme chunk {} başarısız | hata={}", i, exc)
                            for req in chunks[i]:
                                original = req.text.strip()
                                results[req.id] = {"original": original, "improved": original, "reason": f"LLM hatası: {exc}"}

        return [results[req.id] for req in requirements]

    def improve(self, requirement: Requirement) -> dict[str, str]:
        """
        Gereksinim metnini analiz eder; muğlaksa LLM ile iyileştirir.

        Parametreler:
            requirement: İyileştirilecek gereksinim DTO'su.

        Döndürür:
            dict: `original`, `improved`, `reason` anahtarları (tümü str).
        """
        original = (requirement.text or "").strip()
        if not original:
            return {
                "original": original,
                "improved": original,
                "reason": "Boş gereksinim metni; işlem uygulanmadı.",
            }

        if not _text_has_vague_keyword(original):
            return {
                "original": original,
                "improved": original,
                "reason": _NO_VAGUE_REASON,
            }

        system_prompt = build_improvement_system_prompt()
        user_prompt = build_improvement_user_prompt(original)
        client = self._get_client()

        try:
            response = client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                metadata={"module": "improver", "action": "vague_to_measurable"},
            )
        except LLMClientError as exc:
            _log.exception("LLM çağrısı başarısız (gereksinim iyileştirme).")
            return {
                "original": original,
                "improved": original,
                "reason": f"LLM çağrısı tamamlanamadı: {exc}",
            }

        try:
            payload: dict[str, Any] = extract_json_object(response.content)
        except ValueError as exc:
            _log.error(
                "LLM çıktısı JSON olarak çözülemedi | preview={}",
                response.content[:500] if response.content else "",
            )
            return {
                "original": original,
                "improved": original,
                "reason": f"Model çıktısı işlenemedi: {exc}",
            }

        improved = _coerce_str(payload.get("improved"), original)
        reason = _coerce_str(payload.get("reason"), "(Açıklama yok.)")

        result: dict[str, Any] = {
            "original": original,
            "improved": improved,
            "reason": reason,
            "vague_terms": _detected_vague_terms(original),
        }
        if payload.get("feasibility"):
            result["feasibility"] = _coerce_str(payload["feasibility"], "")

        _log.info("Gereksinim iyileştirme tamamlandı | req_id={}", requirement.id)
        return result
