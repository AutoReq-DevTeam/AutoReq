"""
outputs/backlog_generator.py — Önceliklendirme ve Backlog Üretici
Sorumlu: Halise İncir

Açıklama:
Analiz edilen gereksinimleri, mantıksal öncelik kuralları çerçevesinde puanlar ve 
sıralar. Geliştirme ekibi için optimize edilmiş bir işlem listesi oluşturur.
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
