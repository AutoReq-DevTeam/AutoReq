"""
outputs/bdd_generator.py — BDD ve Test Senaryosu Üretici
Sorumlu: Halise İncir

Açıklama:
Gereksinimleri "Given-When-Then" (Gherkin) formatındaki test senaryolarına dönüştürür. 
Sistemin doğrulanabilirliğini artırmak için teknik test taslakları sağlar.
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
