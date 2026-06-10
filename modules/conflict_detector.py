"""
modules/conflict_detector.py — Çelişki ve Mantık Analizörü
Sorumlu: Eren Eyyüpkoca

Açıklama:
Gereksinimler arasındaki mantıksal çelişkileri ve teknik zıtlıkları tespit eder.
NLP ve LLM tekniklerini kullanarak belgelerdeki uyumsuzlukları raporlar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from core.models import ParsedDocument

from .analysis_report_parsing import conflicts_payload_to_report_dicts
from .conflict_prompts import (
    build_conflict_detection_system_prompt,
    build_pairwise_conflict_user_prompt,
)
from .llm_client import LLMClient, LLMClientError
from .llm_response_utils import (
    extract_json_object,
    filter_valid_requirement_ids,
    sort_by_confidence,
)
from .logging_utils import get_module_logger

_log = get_module_logger("conflict_detector")

CONFIDENCE_THRESHOLD = 0.6


def _deduplicate_conflicts(rows: list[dict]) -> list[dict]:
    """Aynı gereksinim çiftini kapsayan çakışmaları tekilleştirir.

    Aynı frozenset(req_ids) birden fazla kayıtta görünüyorsa yalnızca
    en yüksek confidence'lı olanı tutar.
    """
    seen: dict[frozenset, dict] = {}
    no_ids: list[dict] = []

    for row in rows:
        ids = row.get("req_ids")
        if not ids:
            no_ids.append(row)
            continue
        key = frozenset(str(i) for i in ids)
        if key not in seen:
            seen[key] = row
        else:
            existing_conf = float(seen[key]["confidence"]) if "confidence" in seen[key] else 1.0
            new_conf = float(row["confidence"]) if "confidence" in row else 1.0
            if new_conf > existing_conf:
                seen[key] = row

    return list(seen.values()) + no_ids


def _post_process_conflicts(
    rows: list[dict],
    valid_ids: set[str],
    threshold: float = CONFIDENCE_THRESHOLD,
) -> list[dict]:
    """Conflict listesine filtre + dedup + sıralama uygular.

    Adımlar (sırayla):
    1. Geçersiz requirement ID'leri içeren satırları at (hallucination önlemi)
    2. confidence < threshold olan satırları at
    3. Aynı req_ids kümesine sahip duplikatları tekilleştir
    4. confidence'a göre azalan sırada sırala
    """
    rows = filter_valid_requirement_ids(rows, valid_ids, id_keys=("req_ids",))
    rows = [
        r for r in rows
        if (float(r["confidence"]) if "confidence" in r else 1.0) >= threshold
    ]
    rows = _deduplicate_conflicts(rows)
    rows = sort_by_confidence(rows)
    return rows


def _format_requirements_block(doc: ParsedDocument) -> str:
    """ParsedDocument içindeki gereksinimleri LLM user prompt'u için metin haline getirir."""
    if not doc.requirements:
        return "(Bu belgede ayrıştırılmış gereksinim yok.)"
    lines: List[str] = []
    for req in doc.requirements:
        lines.append(f"- [{req.id}] ({req.req_type}) <requirement_text>{req.text.strip()}</requirement_text>")
    return "\n".join(lines)


@dataclass
class PairwiseConflictAnalysis:
    """
    "Hangi gereksinimler birbiriyle çelişiyor?" LLM analizinin tam sonucu.

    Öznitelikler:
        conflicts: Her kayıtta en az req_ids, conflict_type, reason.
        meta: LLM'in döndürdüğü meta (total_requirements, total_conflicts, confidence).
        raw_llm: Ayrıştırılmış tam JSON (izlenebilirlik / hata ayıklama).
    """

    conflicts: list[dict]
    meta: dict[str, Any] = field(default_factory=dict)
    raw_llm: Optional[dict[str, Any]] = None


class ConflictDetector:
    """Gereksinimler arası çelişkileri tespit eder."""

    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        """
        Parametreler:
            llm_client: Dışarıdan enjekte edilebilir istemci (test veya tekil ömür için).
                        Verilmezse analyze çağrısında LLMClient oluşturulur.
        """
        self._llm_client = llm_client

    def _get_client(self) -> LLMClient:
        if self._llm_client is None:
            # Hız ve düşük maliyet için Gemini 2.5 Flash kullanıyoruz
            self._llm_client = LLMClient(model_name="google/gemini-2.5-flash", max_output_tokens=8192)
        return self._llm_client

    def _run_pairwise_llm_analysis(self, doc: ParsedDocument) -> PairwiseConflictAnalysis:
        """
        Hazırlanan system prompt + pairwise user prompt ile LLM çağrısı yapar;
        çelişki satırları ve meta ile PairwiseConflictAnalysis döndürür.
        """
        n = len(doc.requirements)
        block = _format_requirements_block(doc)
        user_prompt = build_pairwise_conflict_user_prompt(block, n)

        client = self._get_client()
        system_prompt = build_conflict_detection_system_prompt()

        try:
            response = client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                metadata={
                    "module": "conflict_detector",
                    "action": "pairwise_conflict_analysis",
                    "analysis_question": "which_requirements_conflict",
                },
            )
        except LLMClientError:
            _log.exception("LLM çağrısı başarısız (pairwise çelişki analizi).")
            raise

        try:
            payload = extract_json_object(response.content)
        except ValueError as exc:
            _log.error(
                "LLM çıktısı JSON olarak çözülemedi | preview={}",
                response.content[:500] if response.content else "",
            )
            raise LLMClientError(f"Çelişki analizi çıktısı işlenemedi: {exc}") from exc

        rows = conflicts_payload_to_report_dicts(payload)

        # Post-processing: ID validasyonu + confidence filtresi + dedup + sıralama
        valid_ids = {req.id for req in doc.requirements}
        raw_count = len(rows)
        rows = _post_process_conflicts(rows, valid_ids)
        if raw_count != len(rows):
            _log.debug(
                "Post-processing sonrası conflict sayısı düşürüldü | önce={} sonra={}",
                raw_count,
                len(rows),
            )

        meta_raw = payload.get("meta")
        meta: dict[str, Any] = dict(meta_raw) if isinstance(meta_raw, dict) else {}
        # Tutarlılık: belgedeki gerçek gereksinim sayısı
        meta.setdefault("total_requirements", n)
        if meta.get("total_requirements") != n:
            meta["total_requirements_reported_by_llm"] = meta.get("total_requirements")
            meta["total_requirements"] = n
        meta["total_conflicts"] = len(rows)  # post-process sonrası gerçek sayı

        _log.info(
            "Çiftler arası çelişki analizi tamamlandı | conflicts={} confidence={}",
            len(rows),
            meta.get("confidence", "?"),
        )

        return PairwiseConflictAnalysis(conflicts=rows, meta=meta, raw_llm=payload)

    def analyze_pairwise(self, doc: ParsedDocument) -> PairwiseConflictAnalysis:
        """
        "Hangi gereksinimler birbiriyle çelişiyor?" sorusuna yanıt üreten tam analiz.

        System prompt (build_conflict_detection_system_prompt) ve
        build_pairwise_conflict_user_prompt ile gereksinimler LLM'e gönderilir.

        Parametreler:
            doc (ParsedDocument): Ayrıştırılmış belge.

        Döndürür:
            PairwiseConflictAnalysis: conflicts listesi ve LLM meta bilgisi.
        """
        if not doc.requirements:
            _log.info("Çiftler arası çelişki analizi atlandı: gereksinim listesi boş.")
            return PairwiseConflictAnalysis(
                conflicts=[],
                meta={
                    "total_requirements": 0,
                    "total_conflicts": 0,
                    "confidence": "high",
                },
                raw_llm={"conflicts": [], "meta": {"total_requirements": 0, "total_conflicts": 0}},
            )
        return self._run_pairwise_llm_analysis(doc)

    def analyze(self, doc: ParsedDocument) -> list[dict]:
        """
        LLM ile belgedeki gereksinimler arası çelişkileri analiz eder.

        İçeride analyze_pairwise ile aynı akış kullanılır; yalnızca çelişki
        listesini döndürür (geriye dönük uyumluluk).

        Parametreler:
            doc (ParsedDocument): Ayrıştırılmış belge.

        Döndürür:
            list[dict]: Her biri en az {'req_ids', 'conflict_type', 'reason'} içeren çelişki listesi.
        """
        return self.analyze_pairwise(doc).conflicts

    def detect(self, doc: ParsedDocument) -> list[dict]:
        """
        Geriye dönük uyumluluk: analyze() ile aynı davranır.

        Parametreler:
            doc (ParsedDocument): Üye 1'den gelen ayrıştırılmış belge.

        Döndürür:
            list[dict]: Her biri {'req_ids', 'conflict_type', 'reason'} (+ isteğe bağlı ek alanlar).
        """
        return self.analyze(doc)
