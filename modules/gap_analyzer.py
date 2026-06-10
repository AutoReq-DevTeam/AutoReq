"""
modules/gap_analyzer.py — Eksik Gereksinim Analizörü
Sorumlu: Eren Eyyüpkoca

Açıklama:
Mevcut gereksinimleri analiz ederek, sistemin bütünlüğü için kritik olan ancak
atlanmış özellikleri (örn: kayıt var ama şifre sıfırlama yok) tespit eder ve öneriler sunar.

LLM entegrasyonu için prompt katmanı: modules/gap_prompts.py
- build_gap_analysis_system_prompt() — persona + standart senaryo referansı + JSON şeması
- build_gap_analysis_user_prompt(...) — gereksinim bloğu ve isteğe bağlı domain_hint
"""

from __future__ import annotations

from typing import List, Optional

from core.models import ParsedDocument

from .analysis_report_parsing import gaps_payload_to_report_dicts
from .gap_prompts import build_gap_analysis_system_prompt, build_gap_analysis_user_prompt
from .llm_client import LLMClient, LLMClientError
from .llm_response_utils import extract_json_object, sort_by_confidence
from .logging_utils import get_module_logger

_log = get_module_logger("gap_analyzer")

GAP_CONFIDENCE_THRESHOLD = 0.5


def _deduplicate_gaps(rows: list[dict]) -> list[dict]:
    """Aynı missing_area'ya sahip gap'leri tekilleştirir; en yüksek confidence'lıyı tutar."""
    seen: dict[str, dict] = {}
    no_area: list[dict] = []

    for row in rows:
        area = (row.get("missing_area") or "").strip().lower()
        if not area:
            no_area.append(row)
            continue
        if area not in seen:
            seen[area] = row
        else:
            existing_conf = float(seen[area]["confidence"]) if "confidence" in seen[area] else 1.0
            new_conf = float(row["confidence"]) if "confidence" in row else 1.0
            if new_conf > existing_conf:
                seen[area] = row

    return list(seen.values()) + no_area


def _post_process_gaps(
    rows: list[dict],
    threshold: float = GAP_CONFIDENCE_THRESHOLD,
) -> list[dict]:
    """Gap listesine confidence filtresi + dedup + sıralama uygular."""
    rows = [
        r for r in rows
        if (float(r["confidence"]) if "confidence" in r else 1.0) >= threshold
    ]
    rows = _deduplicate_gaps(rows)
    rows = sort_by_confidence(rows)
    return rows


# Minimum anlamlı eksiklik için: yalnızca giriş/kimlik ifadesi varken kurtarma adımı yoksa.
_LOGIN_MARKERS: tuple[str, ...] = (
    "giriş",
    "login",
    "oturum",
    "kimlik doğrulama",
    "sign in",
    "signin",
)
_RECOVERY_MARKERS: tuple[str, ...] = (
    "şifre sıfırla",
    "şifremi unuttum",
    "parola sıfırla",
    "parola yenile",
    "şifre yenile",
    "mfa",
    "2fa",
    "iki faktör",
    "two-factor",
    "password reset",
    "hesap kurtarma",
)


def _format_requirements_block(doc: ParsedDocument) -> str:
    """
    ParsedDocument içindeki gereksinimleri LLM user prompt'u için metin haline getirir.

    Parametreler:
        doc: Ayrıştırılmış belge.

    Döndürür:
        Gereksinim satırlarından oluşan metin bloğu.
    """
    if not doc.requirements:
        return "(Bu belgede ayrıştırılmış gereksinim yok.)"
    lines: List[str] = []
    for req in doc.requirements:
        lines.append(f"- [{req.id}] ({req.req_type}) <requirement_text>{req.text.strip()}</requirement_text>")
    return "\n".join(lines)


def _combined_requirement_text(doc: ParsedDocument) -> str:
    """Ham metin ve tüm gereksinim cümlelerini tek dizgede birleştirir (küçük harf)."""
    parts: List[str] = [doc.raw_text or ""]
    parts.extend(req.text for req in doc.requirements)
    return " ".join(parts).lower()


def _append_auth_recovery_gap_if_needed(doc: ParsedDocument, gaps: list[dict]) -> list[dict]:
    """
    LLM boş döndüyse ve belgede giriş/kimlik doğrulama var ancak kurtarma/MFA vb. yoksa
    standart bir 'parola sıfırlama / hesap kurtarma' eksikliği ekler (AC #3).

    Parametreler:
        doc: Ayrıştırılmış belge.
        gaps: Normalize edilmiş gap satırları.

    Döndürür:
        Gerekirse tek satır eklenmiş gap listesi.
    """
    if gaps:
        return gaps
    text = _combined_requirement_text(doc)
    if not any(m in text for m in _LOGIN_MARKERS):
        return gaps
    if any(m in text for m in _RECOVERY_MARKERS):
        return gaps
    return gaps + [
        {
            "missing_area": "Parola sıfırlama / hesap kurtarma akışı",
            "suggestion": (
                "Kullanıcılar parolalarını unuttuklarında güvenli bir şifre sıfırlama "
                "(ör. e-posta bağlantısı veya doğrulama kodu) ile hesaplarına yeniden erişebilmelidir."
            ),
            "severity": "high",
            "scenario": "authentication",
            "rationale": (
                "Belgede giriş/kimlik doğrulama ifadesi var; standart kimlik senaryolarında "
                "parola kurtarma veya alternatif kurtarma adımı tanımlanmamış görünüyor."
            ),
        }
    ]


class GapAnalyzer:
    """Eksik gereksinimleri tespit eder ve öneri sunar."""

    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        """
        Parametreler:
            llm_client: Dışarıdan enjekte edilebilir istemci (test veya tekil ömür için).
                        Verilmezse analyze çağrısında LLMClient oluşturulur.
        """
        self._llm_client = llm_client

    def _get_client(self) -> LLMClient:
        """Lazy LLM istemcisi döndürür."""
        if self._llm_client is None:
            # Hız ve düşük maliyet için Gemini 2.5 Flash kullanıyoruz
            self._llm_client = LLMClient(model_name="google/gemini-2.5-flash", max_output_tokens=8192)
        return self._llm_client

    def analyze(self, doc: ParsedDocument, *, domain_hint: Optional[str] = None) -> list[dict]:
        """
        LLM ile belgedeki standart senaryolara göre eksik gereksinim (gap) analizi yapar.

        Parametreler:
            doc: Üye 1'den gelen ayrıştırılmış belge.
            domain_hint: İsteğe bağlı alan bağlamı (ör. B2C e-ticaret).

        Döndürür:
            Her biri en az {'missing_area', 'suggestion', 'severity'} içeren gap listesi.
        """
        _log.info("Gap analizi başladı | requirements={}", len(doc.requirements) if doc.requirements else 0)

        if not doc.requirements:
            _log.info("Gap analizi atlandı: gereksinim listesi boş.")
            return []

        from .gap_prompts import DOMAIN_REFERENCES
        n = len(doc.requirements)
        block = _format_requirements_block(doc)
        user_prompt = build_gap_analysis_user_prompt(block, n, domain_hint=domain_hint)
        
        refs_str = "\n\n".join(DOMAIN_REFERENCES.values())
        system_prompt = f"{build_gap_analysis_system_prompt()}\n\n## Standart Kontrol Listeleri:\n{refs_str}"
        client = self._get_client()

        try:
            response = client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                metadata={
                    "module": "gap_analyzer",
                    "action": "gap_analysis",
                    "analysis_question": "which_standard_steps_missing",
                },
            )
        except LLMClientError:
            _log.exception("LLM çağrısı başarısız (gap analizi).")
            raise

        try:
            payload = extract_json_object(response.content)
        except ValueError as exc:
            _log.error(
                "LLM çıktısı JSON olarak çözülemedi | preview={}",
                response.content[:500] if response.content else "",
            )
            raise LLMClientError(f"Gap analizi çıktısı işlenemedi: {exc}") from exc

        rows = gaps_payload_to_report_dicts(payload)
        meta_raw = payload.get("meta")

        # Post-processing: confidence filtresi + dedup + sıralama
        raw_count = len(rows)
        rows = _post_process_gaps(rows)
        if raw_count != len(rows):
            _log.debug(
                "Post-processing sonrası gap sayısı düşürüldü | önce={} sonra={}",
                raw_count,
                len(rows),
            )

        if isinstance(meta_raw, dict) and meta_raw.get("total_gaps") != len(rows):
            _log.debug(
                "meta.total_gaps ile liste uzunluğu uyumsuz; satır sayısı esas alındı | reported={} actual={}",
                meta_raw.get("total_gaps"),
                len(rows),
            )

        rows = _append_auth_recovery_gap_if_needed(doc, rows)

        inferred = (meta_raw or {}).get("system_type", "?") if isinstance(meta_raw, dict) else "?"
        _log.info(
            "Gap analizi bitti | gaps={} system_type={} confidence={}",
            len(rows),
            inferred,
            (meta_raw or {}).get("confidence") if isinstance(meta_raw, dict) else "?",
        )
        return rows
