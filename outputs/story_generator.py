"""
outputs/story_generator.py — User Story Üretim Modülü
Sorumlu: Halise İncir

Açıklama:
Analiz edilen gereksinimleri çevik (agile) geliştirme süreçlerine uygun 
"User Story" formatına dönüştürür. Rol, hedef ve fayda bileşenlerini ayrıştırır.
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
