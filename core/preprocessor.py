"""
core/preprocessor.py — Metin Ön İşleme Modülü
Sorumlu: Üye 1 (NLP & Preprocessing)

Açıklama:
Ham metinleri temizleyerek analize hazır hale getirir. Gereksiz karakter temizliği,
normalizasyon ve cümle bazlı ayrıştırma (tokenization) işlemlerinden sorumludur.
"""

import re
import nltk
from nltk.corpus import stopwords
from loguru import logger

from .models import ParsedDocument, Requirement
from .nlp_engine import get_shared_stanza_pipeline, turkish_lower

_log = logger.bind(module="preprocessor")

# Maksimum girdi uzunluğu (karakter sayısı); aşılırsa uyarı verilip kırpılır
_MAX_TEXT_LENGTH: int = 100_000


class TextPreprocessor:
    """Ham metni ayrıştırır ve Requirement listesine dönüştürür."""

    def __init__(self) -> None:
        """
        Sınıf başlatıldığında paylaşılan Stanza pipeline kullanılır ve
        NLTK stopwords listesi hazırlanır.
        """
        _log.info("TextPreprocessor başlatılıyor...")

        # Paylaşılan Stanza pipeline'ı kullan (bellek tasarrufu)
        self.nlp = get_shared_stanza_pipeline()

        # NLTK stopwords listesini hazırlar, eğer inik değil ise indirir
        try:
            nltk.data.find("corpora/stopwords")
        except LookupError:
            nltk.download("stopwords", quiet=True)

        # NLTK'dan gelen stop-words bir List tipindedir, biz bunu daha hızlı işlem yapabilmek için set'e çeviriyoruz
        # Eğer List olarak kalsaydı her kelime için listeyi baştan sona taraması gerekirdi bu da O(N) karmaşıklığa yol açardı
        # Set olarak kullanınca O(1) karmaşıklıkta işlem yaparız
        self.stop_words = set(stopwords.words("turkish"))
        _log.info("TextPreprocessor hazır.")

    def process(self, raw_text: str) -> ParsedDocument:
        """Ham metni ayrıştırır ve Requirement listesine dönüştürür.

        Parametreler:
            raw_text (str): Müşteriden gelen ham metin.

        Döndürür:
            ParsedDocument: Ayrıştırılmış gereksinim listesi.
        """
        if not isinstance(raw_text, str):
            _log.warning("process() str dışında girdi aldı ({}); boş doküman döndürülüyor.", type(raw_text))
            return ParsedDocument(raw_text="")

        # re.sub: birden fazla boşluğu tek boşluğa indirir
        # strip: baştaki ve sondaki boşlukları siler
        clean_text = re.sub(r"\s+", " ", raw_text).strip()

        # KVKK Maskeleme Katmanı
        clean_text = self.mask_kvkk(clean_text)

        # Eğer metin boşsa sistemi yormamak için boş bir ParsedDocument döndür
        if not clean_text:
            return ParsedDocument(raw_text=raw_text)

        # Aşırı uzun girdiler Stanza'yı yavaşlatır; uyarı ver ve kırp
        if len(clean_text) > _MAX_TEXT_LENGTH:
            _log.warning(
                "Girdi çok uzun ({} karakter); ilk {} karaktere kırpılıyor.",
                len(clean_text),
                _MAX_TEXT_LENGTH,
            )
            clean_text = clean_text[:_MAX_TEXT_LENGTH]

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
                word_text = turkish_lower(word.text)  # Küçük harflere çevrilir

                # Eğer kelime stop-word ve noktalama işareti değilse
                if word_text not in self.stop_words and word.upos != "PUNCT":  # PUNCT = punctuation
                    tokens.append(word_text)  # Orijinal halini listeye ekle
                    lemmas.append(turkish_lower(word.lemma) if word.lemma else word_text)  # Kökünü ekler
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

    def mask_kvkk(self, text: str) -> str:
        """TC Kimlik No ve şahıs isimlerini regex ile maskeler (KVKK uyumluluğu için)."""
        if not text:
            return text

        # 1. TC Kimlik No maskeleme (11 haneli, 0 ile başlamayan sayılar)
        text = re.sub(r"\b[1-9]\d{10}\b", "[TC_KIMLIK_NO]", text)

        # 2. Ünvan/Hitap içeren isimleri maskeleme (Sayın Ahmet Yılmaz, Dr. Ayşe vb.)
        text = re.sub(
            r"\b(?:Sayın|Sn\.|Dr\.|Doç\.|Prof\.|Av\.|Ecz\.)\s+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)*)\b",
            lambda m: m.group(0).replace(m.group(1), "[KISI_ADI]"),
            text
        )
        text = re.sub(
            r"\b([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)*)\s+(?:Bey|Hanım)\b",
            lambda m: m.group(0).replace(m.group(1), "[KISI_ADI]"),
            text
        )

        # 3. Şahıs isimlerini maskeleme (büyük harfle başlayan kelime dizilimleri)
        exclude_words = {
            "Sistem", "Sistemi", "Sisteminin", "Uygulama", "Uygulaması", "Uygulamasının",
            "Platform", "Platformu", "Kullanıcı", "Kullanıcısı", "Müşteri", "Müşterisi",
            "Yönetici", "Yöneticisi", "Admin", "Arayüz", "Arayüzü", "Veri", "Verisi",
            "Taban", "Tabanı", "Rapor", "Raporu", "Dosya", "Dosyası", "Talep", "Talebi",
            "İzin", "İzni", "Ödeme", "Ödemesi", "Sipariş", "Siparişi", "Ürün", "Ürünü",
            "Kredi", "Kart", "Kartı", "Android", "iOS", "Windows", "Linux", "TLS", "SLA",
            "GDPR", "KVKK", "EFT", "PDF", "Word", "Excel", "Gherkin", "BDD", "SRS", "Stanza",
            "API", "JSON", "BytesIO", "XML", "XSS", "Hasta", "Hastası", "Doktor", "Doktoru",
            "Hemşire", "Hemşiresi", "Eczacı", "Eczacısı", "Laborant", "Laborantı", "Diyetisyen",
            "Fizyoterapist", "Hekim", "Hekimi", "Yazılım", "Yazılımı", "Geliştirici", "Geliştiricisi",
            "Test", "Testi", "Analist", "Analisti", "Tasarım", "Tasarımı", "Proje", "Projesi",
            "IK", "İk", "Finans", "Finansı", "Kargo", "Kargosu", "Firma", "Firması",
            "Sayfa", "Sayfası", "Buton", "Butonu", "Ekran", "Ekranı", "Hesap", "Hesabı",
            "Profil", "Profili", "Bu", "Her", "Bir", "Tüm", "Eğer", "Şayet", "Aksi",
            "Diğer", "İlk", "Son", "Yeni", "Geçerli", "Aynı", "Hızlı", "Stok", "Stoku",
            "Sayın", "Sn", "Dr", "Prof", "Doç", "Av", "Ecz", "Bey", "Hanım",
            "Oracle", "PostgreSQL", "MySQL", "MongoDB", "Docker", "Git", "GitHub", "GitLab"
        }

        # Cümle başlarını tespit etmek için
        sentence_starts = [m.start() for m in re.finditer(r"(?:^|[\.\?\!]\s+)", text)]

        # Büyük harfle başlayan kelime gruplarını yakala
        def replace_names(match):
            full_match = match.group(0)
            start_idx = match.start()
            
            # Cümle başında mı başlıyor?
            is_at_start = any(start_idx == idx or (idx < start_idx and text[idx:start_idx].isspace()) for idx in sentence_starts)
            
            words = full_match.split()
            cleaned_words = [w for w in words if re.sub(r"[^\w\s]", "", w) not in exclude_words]
            
            if not cleaned_words:
                return full_match
            
            # Cümle başındaysa ve sadece tek kelimeyse (örn: "Giriş...") maskeleme
            if is_at_start and len(cleaned_words) < 2 and len(words) == len(cleaned_words):
                return full_match
                
            # Kelimeleri [KISI_ADI] ile değiştir
            first_name_word = cleaned_words[0]
            last_name_word = cleaned_words[-1]
            
            start_pos = full_match.find(first_name_word)
            end_pos = full_match.find(last_name_word) + len(last_name_word)
            
            return full_match[:start_pos] + "[KISI_ADI]" + full_match[end_pos:]

        text = re.sub(
            r"\b[A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)*\b",
            replace_names,
            text
        )
        return text

