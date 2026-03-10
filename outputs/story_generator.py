"""
outputs/story_generator.py — User Story Üretici
Sahibi: Üye 3 (Çıktı & Döküman Üretimi)

Görev: Gereksinimleri "As a [role], I want [goal], so that [benefit]" formatına dönüştür.
"""

from core.models import AnalysisReport


class StoryGenerator:
    """Gereksinimlerden User Stories üretir."""

    def generate(self, report: AnalysisReport) -> list[dict]:
        """
        Parametreler:
            report (AnalysisReport): Analiz raporu.

        Döndürür:
            list[dict]: Her biri {'role', 'goal', 'benefit', 'acceptance_criteria'} içeren hikaye listesi.
        """
        # TODO: Üye 3 — Her gereksinim için rol, hedef ve fayda alanlarını çıkar
        # TODO: Üye 3 — DOCX ve JSON olarak da dışa aktarma seçeneği ekle
        raise NotImplementedError("StoryGenerator.generate() henüz implemente edilmedi.")
