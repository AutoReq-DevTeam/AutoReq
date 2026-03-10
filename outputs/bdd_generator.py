"""
outputs/bdd_generator.py — Test Senaryosu Yazıcı (BDD Üretici)
Sahibi: Üye 3 (Rapor ve Çıktı Aşaması)

Senin Görevin:
Yazılımcının kodunun doğru çalışıp çalışmadığını test etmemiz lazım.
Bunu İngilizce Gherkin formatında şöyle yazıyoruz:
- GIVEN (Diyelim ki sistemde bir kullanıcı var)
- WHEN (Kullanıcı 'Sil' butonuna bastığında)
- THEN (Kullanıcının hesabı silinmelidir)
Senin işin gereksinimleri bu üçlü İngilizce şablona oturtup .feature uzantılı dosyalar yaratmak.

Çıktı: "Yazılımcının kodunu test edeceği, Given/When/Then formatında İngilizce test dosyaları."
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
