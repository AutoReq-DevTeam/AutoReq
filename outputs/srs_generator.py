"""
outputs/srs_generator.py — SRS PDF Üretici
Sahibi: Üye 3 (Çıktı & Döküman Üretimi)

Görev: IEEE 830 standardına uygun SRS belgesi oluştur ve PDF olarak kaydet.
Çıktı: outputs/generated/srs_<timestamp>.pdf
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
        # TODO: Üye 3 — fpdf2 ile IEEE 830 şablonunu yükle
        # TODO: Üye 3 — Bölümleri doldur: Giriş, Genel Tanım, Gereksinimler
        # TODO: Üye 3 — PDF olarak kaydet → output_path/srs_<timestamp>.pdf
        raise NotImplementedError("SRSGenerator.generate() henüz implemente edilmedi.")
