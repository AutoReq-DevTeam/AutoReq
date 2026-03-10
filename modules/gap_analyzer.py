"""
modules/gap_analyzer.py — Eksiklik Analizi
Sahibi: Üye 2 (Akıllı Analiz Modülleri)

Görev: Standart şablonlara göre eksik gereksinim alanlarını tespit et ve öner.
Şablon dosyası: data/templates/requirement_template.json
"""

from core.models import ParsedDocument


class GapAnalyzer:
    """Eksik gereksinimleri tespit eder ve öneri sunar."""

    def analyze(self, doc: ParsedDocument) -> list[dict]:
        """
        Parametreler:
            doc (ParsedDocument): Üye 1'den gelen ayrıştırılmış belge.

        Döndürür:
            list[dict]: Her biri {'missing_area', 'suggestion', 'severity'} içeren boşluk listesi.
        """
        # TODO: Üye 2 — data/templates/ altındaki şablonu yükle
        # TODO: Üye 2 — Şablondaki zorunlu alanları mevcut gereksinimlerle karşılaştır
        # TODO: Üye 2 — Eksik alanlar için öneri oluştur (örn: Login var → Password Reset öner)
        raise NotImplementedError("GapAnalyzer.analyze() henüz implemente edilmedi.")
