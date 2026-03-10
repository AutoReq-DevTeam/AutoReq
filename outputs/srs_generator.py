"""
outputs/srs_generator.py — Sözleşme Yazıcı (PDF Üretici)
Sahibi: Üye 3 (Rapor ve Çıktı Aşaması)

Senin Görevin:
Artık elimizde tertemiz, hatalarından arındırılmış bir yazılım gereksinim listesi var.
Senin işin bunu alıp, sanki büyük bir şirket için yazılmış resmi bir proje dokümanına (SRS) dönüştürmek ve PDF olarak kaydetmek.
(Bunun için fpdf2 gibi kütüphaneler kullanacaksın).

Çıktı: "Müşteriye sunulmaya hazır, çok şık ve resmi bir PDF belgesi."
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
