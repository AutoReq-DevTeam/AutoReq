"""
outputs/backlog_generator.py — Product Backlog Üretici
Sahibi: Üye 3 (Çıktı & Döküman Üretimi)

Görev: Öncelik skoru hesaplayarak sıralı Product Backlog oluştur.
"""

from core.models import AnalysisReport


class BacklogGenerator:
    """Gereksinimlerden önceliklendirilmiş Product Backlog üretir."""

    def generate(self, report: AnalysisReport) -> list[dict]:
        """
        Parametreler:
            report (AnalysisReport): Analiz raporu.

        Döndürür:
            list[dict]: Öncelik sırasına göre sıralı backlog öğeleri.
        """
        # TODO: Üye 3 — Her gereksinim için öncelik skoru hesapla (F > NFR, kritiklik bazlı)
        # TODO: Üye 3 — Excel / CSV dışa aktarımı ekle
        raise NotImplementedError("BacklogGenerator.generate() henüz implemente edilmedi.")
