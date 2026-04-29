"""
core/priority_detector.py — Gereksinim Öncelik Belirleyici
Sorumlu: Üye 1 (NLP & Preprocessing)

Açıklama:
Bir gereksinimin ham metnindeki anahtar kelimelere göre öncelik düzeyi atar.
HIGH: kritiklik/güvenlik/zorunluluk bildiren kelimeler
LOW : isteğe bağlı/gelecek plan belirten kelimeler
MEDIUM: yukarıdaki iki kategoriye girmeyen nötr gereksinimler
"""

from modules.logging_utils import get_module_logger

from .models import Requirement

_log = get_module_logger("priority_detector")

# Python'un yerleşik .lower() metodu Türkçe büyük İ (U+0130) harfini
# "i" + birleştirici nokta (U+0069 + U+0307) çiftine çevirir; bu nedenle
# "İleride".lower() != "ileride" karşılaştırması başarısız olur.
# Aşağıdaki dönüşüm tablosu Türkçeye özgü büyük/küçük harf eşleşmesini
# standart ASCII değerlerine indirgemeden önce düzeltir.
_TR_UPPER_TO_LOWER = str.maketrans("İIÇÖÜŞĞ", "iıçöüşğ")


def _normalize(text: str) -> str:
    """Türkçe büyük harf normalizasyonu sonrası küçük harfe çevirir."""
    return text.translate(_TR_UPPER_TO_LOWER).lower()


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
        "mahremiyet",
        "must",
        "zorunlu",
    })

    LOW_KEYWORDS: frozenset = frozenset({
        "tercihen",
        "isteğe bağlı",
        "ileride",
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
        text_lower = _normalize(req.text)

        for keyword in self.HIGH_KEYWORDS:
            if keyword in text_lower:
                req.priority = "HIGH"
                _log.debug(
                    "HIGH öncelik atandı | req_id={} keyword={}",
                    req.id,
                    keyword,
                )
                return req

        for keyword in self.LOW_KEYWORDS:
            if keyword in text_lower:
                req.priority = "LOW"
                _log.debug(
                    "LOW öncelik atandı | req_id={} keyword={}",
                    req.id,
                    keyword,
                )
                return req

        req.priority = "MEDIUM"
        _log.debug("MEDIUM öncelik atandı | req_id={}", req.id)
        return req
