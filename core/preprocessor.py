"""
core/preprocessor.py — Metin Ön İşleme Modülü
"""

import re
import nltk
from nltk.corpus import stopwords
from loguru import logger

from .models import ParsedDocument, Requirement
from .nlp_engine import get_shared_stanza_pipeline

_log = logger.bind(module="preprocessor")


class TextPreprocessor:
    """Ham metni ayrıştırır ve Requirement listesine dönüştürür."""

    def __init__(self) -> None:
        _log.info("TextPreprocessor başlatılıyor...")

        self.nlp = get_shared_stanza_pipeline()

        try:
            nltk.data.find("corpora/stopwords")
        except LookupError:
            nltk.download("stopwords", quiet=True)

        self.stop_words = set(stopwords.words("turkish"))
        _log.info("TextPreprocessor hazır.")

    def process(self, raw_text: str) -> ParsedDocument:

        clean_text = re.sub(r"\s+", " ", raw_text).strip()

        if not clean_text:
            return ParsedDocument(raw_text=raw_text)

        doc = self.nlp(clean_text)

        parsed_reqs = []

        for i, sent in enumerate(doc.sentences):
            tokens = []
            lemmas = []
            pos_tags = []

            for word in sent.words:
                # 🔥 NULL SAFE TÜM ALANLAR
                word_text = (word.text or "").lower()
                lemma = (word.lemma or word.text or "").lower()
                upos = word.upos or "X"

                # 🔥 BURASI KRİTİK FIX
                if word_text and word_text not in self.stop_words and upos != "PUNCT":
                    tokens.append(word_text)
                    lemmas.append(lemma)
                    pos_tags.append(upos)

            req = Requirement(
                id=f"REQ_{i + 1:03d}",
                text=sent.text or "",
                tokens=tokens,
                lemmas=lemmas,
                pos_tags=pos_tags,
                source_index=i,
            )
            parsed_reqs.append(req)

        return ParsedDocument(
            raw_text=raw_text,
            requirements=parsed_reqs,
            language="tr",
            total_sentences=len(doc.sentences),
        )