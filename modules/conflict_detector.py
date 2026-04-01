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
from .llm_response_utils import extract_json_object
from .logging_utils import get_module_logger

_log = get_module_logger("conflict_detector")


def _format_requirements_block(doc: ParsedDocument) -> str:
    """ParsedDocument içindeki gereksinimleri LLM user prompt'u için metin haline getirir."""
    if not doc.requirements:
        return "(Bu belgede ayrıştırılmış gereksinim yok.)"
    lines: List[str] = []
    for req in doc.requirements:
        lines.append(f"- [{req.id}] ({req.req_type}) {req.text.strip()}")
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
            self._llm_client = LLMClient()
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
        meta_raw = payload.get("meta")
        meta: dict[str, Any] = dict(meta_raw) if isinstance(meta_raw, dict) else {}
        # Tutarlılık: belgedeki gerçek gereksinim sayısı
        meta.setdefault("total_requirements", n)
        if meta.get("total_requirements") != n:
            meta["total_requirements_reported_by_llm"] = meta.get("total_requirements")
            meta["total_requirements"] = n
        meta.setdefault("total_conflicts", len(rows))

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
