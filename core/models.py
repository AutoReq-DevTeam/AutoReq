"""
core/models.py — Ortak Veri Modelleri (Dataclasses)
Sahibi: Üye 1  |  Tüm üyeler bu dosyayı okur, değiştirmek için PR açılır.

Bu dosyadaki modeller, modüller arası veri akışını standartlaştırır.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Requirement:
    """Tek bir gereksinim cümlesini temsil eder."""

    id: str
    text: str
    req_type: str = "UNKNOWN"  # "FUNCTIONAL" | "NON_FUNCTIONAL" | "UNKNOWN"
    actors: List[str] = field(default_factory=list)  # Her nesne için yeni bir liste oluşturur
    objects: List[str] = field(default_factory=list)
    priority: Optional[str] = None  # "HIGH" | "MEDIUM" | "LOW"

    original_text: str = ""  # Orijinal metin
    tokens: List[str] = field(default_factory=list)  # Token'lar
    lemmas: List[str] = field(default_factory=list)  # Lemmalar
    pos_tags: List[str] = field(default_factory=list)  # POS etiketleri
    source_index: int = 0  # Metin içindeki cümle sıra numarası (0, 1, 2...)


@dataclass
class ParsedDocument:
    """Üye 1 → Üye 2 arası veri transferi.
    Ham metni cümlelere ayırır ve her cümleden bir requirement oluşturup bu sınıfa koyar
    """

    raw_text: str
    requirements: List[Requirement] = field(default_factory=list)
    language: str = "tr"

    total_sentences: int = 0  # Toplam cümle sayısı
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())  # İşleme zamanı


@dataclass
class AnalysisReport:
    """Üye 2 → Üye 3 arası veri transferi.
    LLM analiz sonuçlarını tutar
    """

    parsed_doc: ParsedDocument
    conflicts: List[dict] = field(default_factory=list)  # Çelişkiler
    gaps: List[dict] = field(default_factory=list)  # Eksikler
    improvements: List[dict] = field(default_factory=list)  # İyileştirmeler
