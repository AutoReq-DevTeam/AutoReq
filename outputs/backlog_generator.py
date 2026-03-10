"""
outputs/backlog_generator.py — Öncelik Sıralayıcı (Product Backlog Üretici)
Sahibi: Üye 3 (Rapor ve Çıktı Aşaması)

Senin Görevin:
Yazılım ekibi hangi işi önce yapmalı? Müşteri hepsini 'Acil' diyebilir ama biz biliyoruz ki 'Kayıt Olma' işlemi, 'Tema Rengi Seçme' işleminden daha önemlidir.
Senin işin, bizim kurallarımıza (örn: fonksiyonel şeyler her zaman görsel şeylerden daha acildir) göre her isteğe bir puan vermek ve bunları en önemliden en önemsize doğru sıralamak.

Çıktı: "Ekibin 'ilk buradan başlayalım' diyebileceği puanlanmış, sıralı bir Excel/Tablo listesi."
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
