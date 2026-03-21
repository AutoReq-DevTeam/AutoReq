"""
core/preprocessor.py — Metin Ön İşleme Modülü
Sorumlu: Üye 1 (NLP & Preprocessing)

Açıklama:
Ham metinleri temizleyerek analize hazır hale getirir. Gereksiz karakter temizliği,
normalizasyon ve cümle bazlı ayrıştırma (tokenization) işlemlerinden sorumludur.
"""

import re
import stanza
import nltk
from nltk.corpus import stopwords
from .models import ParsedDocument, Requirement


class TextPreprocessor:
    """Ham metni ayrıştırır ve Requirement listesine dönüştürür."""

    def __init__(self):
        """
        Sınıf başlatıldığında Stanza sadece bir kere indirilir ve başlatılır.
        Bu sayede her seferinde indirme işlemi yapılmaz ve hız kazanılır.
        """
        print("Stanza indiriliyor...")

        # Türkçe için pipeline
        # processors="tokenize,pos,lemma" → cümlelere ayırır, kelimelerin türünü belirler, köklerini bulur
        self.nlp = stanza.Pipeline("tr", processors="tokenize,pos,lemma", verbose=False)

        # NLTK stopwords listesini hazırlar, eğer inik değil ise indirir
        try:
            nltk.data.find("corpora/stopwords")
        except LookupError:
            nltk.download("stopwords", quiet=True)

        # NLTK'dan gelen stop-words bir List tipindedir, biz bunu daha hızlı işlem yapabilmek için set'e çeviriyoruz
        # Eğer List olarak kalsaydı her kelime için listeyi baştan sona taraması gerekirdi bu da O(N) karmaşıklığa yol açardı
        # Set olarak kullanınca O(1) karmaşıklıkta işlem yaparız
        self.stop_words = set(stopwords.words("turkish"))
        print("Stanza indirildi.")

    def process(self, raw_text: str) -> ParsedDocument:
        """
        Parametreler:
            raw_text (str): Müşteriden gelen ham metin.

        Döndürür:
            ParsedDocument: Ayrıştırılmış gereksinim listesi.
        """
        # re.sub: birden fazla boşluğu tek boşluğa indirir
        # strip: baştaki ve sondaki boşlukları siler
        clean_text = re.sub(r"\s+", " ", raw_text).strip()

        # Eğer metin boşsa sistemi yormamak için boş bir ParsedDocument döndür
        if not clean_text:
            return ParsedDocument(raw_text=raw_text)

        # Metni stanzaya veriyoruz
        doc = self.nlp(clean_text)

        # Sonuçların toparlanacağı boş liste
        parsed_reqs = []

        # Stanzanın bulduğu her cümleyi tek tek dolaşıyoruz
        for i, sent in enumerate(doc.sentences):
            tokens = []  # Stop-words içermeyen kelimeler
            lemmas = []  # Kelimelerin kökleri
            pos_tags = []  # Kelimelerin türleri (isim, fiil, sıfat vb.)

            # Cümledeki her bir kelimeye bakıyoruz
            for word in sent.words:
                word_text = word.text.lower()  # Küçük harflere çevrilir

                # Eğer kelime stop-word ve noktalama işareti değilse
                if word_text not in self.stop_words and word.upos != "PUNCT":  # PUNCT = punctuation
                    tokens.append(word_text)  # Orijinal halini listeye ekle
                    lemmas.append(word.lemma.lower())  # Kökünü ekler
                    pos_tags.append(word.upos)  # Türünü ekler

            # Elimizdeki verilerle requirement nesnesini oluşturuyoruz
            req = Requirement(
                id=f"REQ_{i + 1:03d}",  # 001, 002, 003... formatında ID atar
                text=sent.text,  # Cümlenin orijinal metni
                tokens=tokens,  # Stop-words içermeyen kelimeler
                lemmas=lemmas,  # Kelimelerin kökleri
                pos_tags=pos_tags,  # Kelimelerin türleri (isim, fiil, sıfat vb.)
                source_index=i,  # Cümlenin sıra numarası
            )
            parsed_reqs.append(req)  # Oluşturulan requirement nesnesini listeye ekle

        # Son olarak, tüm verileri ParsedDocument nesnesine koyup döndürüyoruz
        return ParsedDocument(
            raw_text=raw_text,  # Ham metin
            requirements=parsed_reqs,  # Ayrıştırılmış gereksinimler
            language="tr",  # Dil
            total_sentences=len(doc.sentences),  # Toplam cümle sayısı
        )
