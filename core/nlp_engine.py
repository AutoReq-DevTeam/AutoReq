"""
core/nlp_engine.py — Paylaşılan NLP Pipeline Motoru
Sorumlu: Üye 1 (NLP & Preprocessing)

Açıklama:
TextPreprocessor ve EntityRecognizer'ın ayrı ayrı Stanza pipeline yüklemesi
bellek kullanımını 2x artırıyordu. Bu modül, tek bir paylaşılan Stanza
pipeline oluşturarak bellek tüketimini yarıya indirir.

Kullanım:
    from core.nlp_engine import get_shared_stanza_pipeline
    nlp = get_shared_stanza_pipeline()
"""

from __future__ import annotations

from typing import Optional

import stanza
from loguru import logger

_log = logger.bind(module="nlp_engine")

# Modül düzeyinde singleton — ilk çağrıda oluşturulur
_shared_pipeline: Optional[stanza.Pipeline] = None


def get_shared_stanza_pipeline() -> stanza.Pipeline:
    """Paylaşılan Stanza Türkçe pipeline'ını döndürür (singleton).

    İlk çağrıda pipeline oluşturulur ve modül düzeyinde saklanır.
    Sonraki çağrılar aynı nesneyi döndürür — bellek tekrar harcanmaz.

    Döndürür:
        stanza.Pipeline: tokenize, mwt, pos, lemma, ner processor'larıyla
        yüklenmiş Türkçe pipeline.
    """
    global _shared_pipeline
    if _shared_pipeline is None:
        _log.info("Stanza Türkçe pipeline yükleniyor (tek seferlik)...")
        _shared_pipeline = stanza.Pipeline(
            lang="tr",
            processors="tokenize,mwt,pos,lemma,ner",
            use_gpu=False,
            verbose=False,
        )
        _log.info("Stanza Türkçe pipeline başarıyla yüklendi.")
    return _shared_pipeline
