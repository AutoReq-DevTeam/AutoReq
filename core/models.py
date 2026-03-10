"""
core/models.py — Ortak Veri Modelleri (Dataclasses)
Sahibi: Üye 1  |  Tüm üyeler bu dosyayı okur, değiştirmek için PR açılır.

Bu dosyadaki modeller, modüller arası veri akışını standartlaştırır.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Requirement:
    """Tek bir gereksinim cümlesini temsil eder."""

    id: str
    text: str
    req_type: str = "UNKNOWN"  # "FUNCTIONAL" | "NON_FUNCTIONAL" | "UNKNOWN"
    actors: List[str] = field(default_factory=list)
    objects: List[str] = field(default_factory=list)
    priority: Optional[str] = None  # "HIGH" | "MEDIUM" | "LOW"


@dataclass
class ParsedDocument:
    """Üye 1 → Üye 2 arası veri transferi."""

    raw_text: str
    requirements: List[Requirement] = field(default_factory=list)
    language: str = "tr"


@dataclass
class AnalysisReport:
    """Üye 2 → Üye 3 arası veri transferi."""

    parsed_doc: ParsedDocument
    conflicts: List[dict] = field(default_factory=list)
    gaps: List[dict] = field(default_factory=list)
    improvements: List[dict] = field(default_factory=list)
