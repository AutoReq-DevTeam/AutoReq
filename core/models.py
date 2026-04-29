"""
core/models.py — Ortak Veri Modelleri (Pydantic v2 BaseModel)
Sahibi: Üye 1  |  Tüm üyeler bu dosyayı okur, değiştirmek için PR açılır.

Bu dosyadaki modeller, modüller arası veri akışını standartlaştırır.
Pydantic v2 kullanılır; geçersiz alan değerleri ValidationError fırlatır.
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Requirement(BaseModel):
    """Tek bir gereksinim cümlesini temsil eder.

    Pydantic v2 BaseModel kullanılarak tip doğrulaması sağlanmıştır.
    validate_assignment=True ile in-place atamalar da doğrulanır
    (req.req_type = 'FUNCTIONAL' gibi kullanımlar güvenlidir).
    """

    model_config = {"validate_assignment": True}

    id: str
    text: str
    req_type: Literal["FUNCTIONAL", "NON_FUNCTIONAL", "UNKNOWN"] = "UNKNOWN"
    actors: List[str] = Field(default_factory=list)
    objects: List[str] = Field(default_factory=list)
    priority: Optional[Literal["HIGH", "MEDIUM", "LOW"]] = None
    original_text: str = ""
    tokens: List[str] = Field(default_factory=list)
    lemmas: List[str] = Field(default_factory=list)
    pos_tags: List[str] = Field(default_factory=list)
    source_index: int = 0


class ParsedDocument(BaseModel):
    """Üye 1 → Üye 2 arası veri transferi.

    Ham metni cümlelere ayırır ve her cümleden bir Requirement oluşturup tutar.
    """

    raw_text: str
    requirements: List[Requirement] = Field(default_factory=list)
    language: str = "tr"
    total_sentences: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class AnalysisReport(BaseModel):
    """Üye 2 → Üye 3 arası veri transferi.

    LLM analiz sonuçlarını tutar.

    conflicts öğeleri (modules.analysis_report_parsing ile üretilir): en az
    req_ids, conflict_type, reason; isteğe bağlı id, severity, suggested_resolution.

    gaps öğeleri: en az missing_area, suggestion, severity; isteğe bağlı id,
    scenario, related_standard_step, rationale.

    improvements öğeleri: original, improved, reason.
    """

    parsed_doc: ParsedDocument
    conflicts: List[dict] = Field(default_factory=list)
    gaps: List[dict] = Field(default_factory=list)
    improvements: List[dict] = Field(default_factory=list)
