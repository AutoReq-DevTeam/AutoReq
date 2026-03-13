"""
core/preprocessor.py — Metin Ön İşleme Modülü
Sorumlu: Üye 1 (NLP & Preprocessing)

Açıklama:
Ham metinleri temizleyerek analize hazır hale getirir. Gereksiz karakter temizliği, 
normalizasyon ve cümle bazlı ayrıştırma (tokenization) işlemlerinden sorumludur.
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
