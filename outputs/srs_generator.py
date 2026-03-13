"""
outputs/srs_generator.py — PDF SRS Üretim Modülü
Sorumlu: Halise İncir

Açıklama:
Final analiz verilerini kullanarak ISO/IEC/IEEE 29148 standartlarına uygun profesyonel 
Yazılım Gereksinim Spesifikasyonu (SRS) dökümanı üretir.
"""

from core.models import AnalysisReport


class SRSGenerator:
    """Analiz raporundan PDF SRS belgesi üretir."""

    def generate(self, report: AnalysisReport, output_path: str = "outputs/generated/") -> str:
        """
        Parametreler:
            report       (AnalysisReport): Üye 2'den gelen analiz raporu.
            output_path  (str)           : Çıktı dizini.

        Döndürür:
            str: Oluşturulan PDF dosyasının tam yolu.
        """
        # TODO: Üye 3 — fpdf2 ile ISO/IEC/IEEE 29148 şablonunu oluştur
        # TODO: Üye 3 — Bölümleri doldur: Giriş, Genel Tanım, Sistem Özellikleri, Gereksinimler
        # TODO: Üye 3 — PDF olarak kaydet → output_path/srs_<timestamp>.pdf
        raise NotImplementedError("SRSGenerator.generate() henüz implemente edilmedi.")
