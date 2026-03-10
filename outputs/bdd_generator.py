"""
outputs/bdd_generator.py — BDD Senaryo Üretici
Sahibi: Üye 3 (Çıktı & Döküman Üretimi)

Görev: Given-When-Then formatında BDD test senaryoları oluştur.
"""

from core.models import AnalysisReport


class BDDGenerator:
    """Gereksinimlerden Gherkin formatında BDD senaryoları üretir."""

    def generate(self, report: AnalysisReport) -> list[str]:
        """
        Parametreler:
            report (AnalysisReport): Analiz raporu.

        Döndürür:
            list[str]: Gherkin formatında senaryo metinleri.
        """
        # TODO: Üye 3 — Her gereksinim için Given/When/Then taslakları çıkar
        # TODO: Üye 3 — .feature dosyası olarak kaydet
        raise NotImplementedError("BDDGenerator.generate() henüz implemente edilmedi.")
