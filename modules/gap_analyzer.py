"""
modules/gap_analyzer.py — Unutulan Özellikleri Bulan Sistem
Sahibi: Üye 2 (Akıllı Kontrol Modülü)

Senin Görevin:
Müşteri bir alışveriş uygulaması istemiş olabilir. Ürün eklemeyi yazmış, satın almayı yazmış ama "Sepeti boşalt" butonunu istemeyi unutmuş!
Senin işin, bizim sistemdeki standart e-ticaret (veya diğer proje) kalıplarına bakarak müşterinin midesine yazmayı unuttuğu, 'Burada kesin eksik var, sisteme kayıt var ama şifremi unuttum özelliği yok' dediğin detayları tespit edip önermek.

Çıktı: "Müşterinin yazmayı unuttuğu özelliklerin bir tavsiye listesi."
"""

from core.models import ParsedDocument


class GapAnalyzer:
    """Eksik gereksinimleri tespit eder ve öneri sunar."""

    def analyze(self, doc: ParsedDocument) -> list[dict]:
        """
        Parametreler:
            doc (ParsedDocument): Üye 1'den gelen ayrıştırılmış belge.

        Döndürür:
            list[dict]: Her biri {'missing_area', 'suggestion', 'severity'} içeren boşluk listesi.
        """
        # TODO: Üye 2 — Mevcut gereksinimleri analiz edip projenin kapsamını belirle (E-ticaret, Fintech, vb.)
        # TODO: Üye 2 — LLM kullanarak "Dünya standartlarında bu tip bir sistemde ne eksik olabilir?" sorusuna yanıt ara
        # TODO: Üye 2 — Eksik iş akışlarını (örn: "Giriş var ama Şifremi Unuttum yok") raporla
        raise NotImplementedError("GapAnalyzer.analyze() henüz implemente edilmedi.")
