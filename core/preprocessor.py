"""
core/preprocessor.py — Metin Temizleyici ve Düzenleyici
Sahibi: Üye 1 (Metin Hazırlık)

Senin Görevin:
Sana müşteriden gelen karmakarışık, imla kurallarına uyulmamış uzunca bir yazı verilecek.
Senin buradaki görevin bir editör gibi davranmak:
1. Gereksiz boşlukları, anlamsız karakterleri sil.
2. Noktalama işaretlerini ve büyük/küçük harfleri düzgün bir standarda oturt.
3. Uzun metni, bilgisayarın kolayca okuyabileceği kelimelere ve cümlelere ayır.

Çıktı: "Tertemiz, bilgisayarın işlemeye hazır olduğu bir veri seti."
"""

from .models import ParsedDocument, Requirement


class TextPreprocessor:
    """Ham metni ayrıştırır ve Requirement listesine dönüştürür."""

    def process(self, raw_text: str) -> ParsedDocument:
        """
        Parametreler:
            raw_text (str): Müşteriden gelen ham metin.

        Döndürür:
            ParsedDocument: Ayrıştırılmış gereksinim listesi.
        """
        # TODO: Üye 1 — spaCy ile cümle tokenizasyonu yap
        # TODO: Üye 1 — Noktalama, büyük/küçük harf normalizasyonu
        # TODO: Üye 1 — Gereksiz boşluk ve karakterleri temizle
        raise NotImplementedError("TextPreprocessor.process() henüz implemente edilmedi.")
