"""
core/preprocessor.py — Metin Ön İşleme
Sahibi: Üye 1 (NLP Core & Preprocessing)

Görev: Ham metni tokenize et, temizle ve normalleştir.
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
