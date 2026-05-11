"""
core/priority_detector.py — Gereksinim Öncelik Belirleyici
Sorumlu: Üye 1 (NLP & Preprocessing)

Açıklama:
Bir gereksinimin ham metnindeki anahtar kelimelere göre öncelik düzeyi atar.
HIGH: kritiklik/güvenlik/zorunluluk bildiren kelimeler
LOW : isteğe bağlı/gelecek plan belirten kelimeler
MEDIUM: yukarıdaki iki kategoriye girmeyen nötr gereksinimler
"""

import re

from modules.logging_utils import get_module_logger

from .models import Requirement

_log = get_module_logger("priority_detector")

# Python'un yerleşik .lower() metodu Türkçe büyük İ (U+0130) harfini
# "i" + birleştirici nokta (U+0069 + U+0307) çiftine çevirir; bu nedenle
# "İleride".lower() != "ileride" karşılaştırması başarısız olur.
# Aşağıdaki dönüşüm tablosu Türkçeye özgü büyük/küçük harf eşleşmesini
# standart ASCII değerlerine indirgemeden önce düzeltir.
_TR_UPPER_TO_LOWER = str.maketrans("İIÇÖÜŞĞ", "iıçöüşğ")

_NEGATION_TOKENS = frozenset({
    "değil", "olmayan", "olmamalı", "olmaması", "gerekmiyor",
    "gerekmez", "zorunlu değil", "şart değil", "not", "abartılı",
})

# HIGH keywords that can appear as object-noun modifiers (not as constraints).
# E.g. "güvenlik loglarını görüntüleyebilmeli" — güvenlik is the object noun,
# not a security constraint signal.
_OBJECT_COMPOUND_PATTERNS: dict[str, re.Pattern] = {
    "güvenlik": re.compile(r"\bgüvenli[kğ]\s+\w*(?:log|rapor|kayd)"),
    "güvenli":  re.compile(r"\bgüvenli[kğ]\s+\w*(?:log|rapor|kayd)"),
    "kritik":   re.compile(r"\bkritik\s+\w*(?:bildirim|mesaj)"),
}


def _normalize(text: str) -> str:
    """Türkçe büyük harf normalizasyonu sonrası küçük harfe çevirir."""
    return text.translate(_TR_UPPER_TO_LOWER).lower()


def _negated(text: str, keyword_start: int, keyword: str) -> bool:
    """Keyword etrafındaki 60 karakterlik pencerede negasyon token'ı var mı bakar.

    Hem öncesi ("şart değil") hem sonrası ("güvenlik olmamalı") kontrol edilir.
    """
    keyword_end = keyword_start + len(keyword)
    window = text[max(0, keyword_start - 60): min(len(text), keyword_end + 60)]
    return any(neg in window for neg in _NEGATION_TOKENS)


class PriorityDetector:
    """Kelime listesi tabanlı gereksinim öncelik sınıflandırıcısı.

    HIGH_KEYWORDS içeren gereksinimler HIGH,
    LOW_KEYWORDS içerenler LOW,
    geri kalanlar MEDIUM önceliği alır.
    Öncelik belirleme deterministiktir ve LLM gerektirmez.
    """

    HIGH_KEYWORDS: frozenset = frozenset({
        "kritik",
        "mutlaka",
        "asla",
        "şart",
        "güvenlik",
        "güvenli",
        "mahremiyet",
        "must",
        "zorunlu",
    })

    LOW_KEYWORDS: frozenset = frozenset({
        "tercihen",
        "isteğe bağlı",
        "ileride",
        "gelecek",
        "opsiyonel",
        "nice-to-have",
    })

    def detect(self, req: Requirement) -> Requirement:
        """Gereksinim metnindeki anahtar kelimelere göre priority alanını doldurur.

        HIGH_KEYWORDS listesinde bir eşleşme bulunursa HIGH,
        LOW_KEYWORDS listesinde eşleşme bulunursa LOW,
        hiçbiri eşleşmezse MEDIUM atanır. Arama büyük/küçük harf duyarsızdır.

        Parametreler:
            req: Önceliği atanacak Requirement nesnesi.

        Döndürür:
            Requirement: priority alanı dolu (HIGH/MEDIUM/LOW) gereksinim.
        """
        text_lower = _normalize(req.text.strip())

        if not text_lower:
            req.priority = "MEDIUM"
            _log.debug("Bo\u015f metin \u2014 MEDIUM \u00f6ncelik atand\u0131 | req_id={}", req.id)
            return req

        # LOW check first: optional/future markers override HIGH keywords.
        for keyword in self.LOW_KEYWORDS:
            if keyword in text_lower:
                req.priority = "LOW"
                _log.debug(
                    "LOW \u00f6ncelik atand\u0131 | req_id={} keyword={}",
                    req.id,
                    keyword,
                )
                return req

        for keyword in self.HIGH_KEYWORDS:
            idx = text_lower.find(keyword)
            if idx == -1:
                continue
            if _negated(text_lower, idx, keyword):
                continue
            obj_pat = _OBJECT_COMPOUND_PATTERNS.get(keyword)
            if obj_pat and obj_pat.search(text_lower):
                continue
            req.priority = "HIGH"
            _log.debug(
                "HIGH \u00f6ncelik atand\u0131 | req_id={} keyword={}",
                req.id,
                keyword,
            )
            return req

        req.priority = "MEDIUM"
        _log.debug("MEDIUM \u00f6ncelik atand\u0131 | req_id={}", req.id)
        return req

