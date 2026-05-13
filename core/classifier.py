"""
core/classifier.py — Gereksinim Sınıflandırıcı

Hibrit 3 katmanlı mimari:
  Katman 1 — FR sinyal tespiti: Türkçe eylem fiili var + NFR keyword yok → FUNCTIONAL
  Katman 2 — NFR keyword + sayısal regex → NON_FUNCTIONAL
  Katman 3 — LLM few-shot: sadece ikisi de karar veremediğinde (belirsiz vakalar)
"""

import re

from .models import Requirement

# Türkçe gereksinim cümlelerinde kullanıcı eylemi bildiren fiil sonekleri.
# Bu sonekler fonksiyonel gereksinimin açık sinyalidir.
_FR_VERB_RE = re.compile(
    r"\b\w+(?:abilmeli|ebilmeli|abilmelidir|ebilmelidir"
    r"|abilir|ebilir|yapmalı|etmeli|görmeli|almalı|vermeli"
    r"|oluşturmalı|silmeli|güncellemeli|görüntülemeli)\b",
    re.IGNORECASE,
)

_CLASSIFICATION_SYSTEM_PROMPT = """\
Sen bir yazılım gereksinim analisti uzmansın.
Verilen Türkçe gereksinim cümlesini FUNCTIONAL veya NON_FUNCTIONAL olarak sınıflandır.

FUNCTIONAL  : Sistemin yapması gereken eylemler, kullanıcı işlemleri, iş özellikleri.
NON_FUNCTIONAL: Performans, güvenlik, güvenilirlik, uyumluluk, ölçeklenebilirlik, erişilebilirlik.

Örnekler:
- "Kullanıcı sisteme giriş yapabilmeli." → FUNCTIONAL
- "Admin kullanıcı silebilmeli." → FUNCTIONAL
- "Kullanıcı arayüzden rapor indirebilmeli." → FUNCTIONAL
- "Sistem 3 saniyede yanıt vermeli." → NON_FUNCTIONAL
- "Veriler şifrelenmiş olarak saklanmalıdır." → NON_FUNCTIONAL
- "Sistem %99.9 uptime sağlamalı." → NON_FUNCTIONAL
- "Uygulama tüm modern tarayıcılarda hatasız çalışmalıdır." → NON_FUNCTIONAL

Yalnızca "FUNCTIONAL" veya "NON_FUNCTIONAL" döndür. Başka hiçbir şey yazma.\
"""


class RequirementClassifier:
    """Gereksinimleri F / NFR olarak sınıflandırır (hibrit 3 katman)."""

    def __init__(self) -> None:
        # Katman 2: NFR anahtar kelime kümesi.
        # "arayüz" ve "standart" çıkarıldı — FR cümlelerinde false positive üretiyordu.
        # "hızlı" ambiguous sete taşındı — "Hızlı ödeme" gibi özellik adlarında FR.
        # "en fazla/az" regex pattern'a taşındı — "birden fazla" substring false positive'i engeller.
        self.nfr_keywords: frozenset = frozenset([
            # Performans ("performans" ambiguous sete taşındı — İK domain'inde FR olabilir)
            "saniye", "gecikme", "milisaniye", "mili saniye",
            "eş zamanlı", "eşzamanlı", "yanıt süresi", "throughput",
            # Güvenlik
            "güvenli", "güvenlik", "kripto", "ssl", "korunmalı", "mahremiyet",
            "şifrelen", "şifreli", "şifreleme", "yetkisiz erişim",
            # Güvenlik — veri saklama kısıtları
            "saklanmamalı", "tutulmamalı", "tokenize", "token hali", "tokenlanmış",
            # Ölçeklenebilirlik & kapasite
            "ölçek", "kapasite",
            # Erişilebilirlik & süreklilik
            "kesintisiz", "ulaşılabilir", "uptime", "erişilebilir", "yedek",
            "hatasız çalış", "çökmemeli", "çökmeli",
            # Kullanılabilirlik
            "kullanılabilirlik", "responsive",
            # Güvenilirlik
            "crash", "hata oranı", "yedeklenmiş",
            # Kısıtlama ifadeleri
            "kaldırabilmeli", "desteklemelidir",
            "geçmemelidir", "geçmemeli", "aşmamalı", "aşmamali",
            "minimum", "maksimum", "en çok", "en geç",
            "karşılamalıdır", "sağlamalıdır",
        ])

        # Katman 2: Sayısal eşik pattern'ları
        # "en fazla / en az" regex olarak: kelime sınırlı eşleşme ("birden fazla" false positive'i önler)
        self.nfr_numeric_patterns: list = [
            re.compile(r'%\s*\d'),
            re.compile(r'\d\s*%'),
            re.compile(r'\d[\d,\.]*\s*(ms\b|sn\b|milisaniye|mili\s*saniye)'),
            re.compile(r'\d[\d,\.]*\s*(eş\s*zamanlı|eşzamanlı|concurrent)'),
            re.compile(r'\d{1,3}\.\d{3}\s*(?:\w+\s+)?(kullanıcı|istek|işlem|bağlantı|kayıt|talep|taleb|sipariş|mesaj)'),
            re.compile(r'\ben\s+fazla\s+(?=\d|%)'),
            re.compile(r'\ben\s+az\s+(?=\d|%)'),
        ]

        # FR cümlelerinde nesne olarak da geçebilen ambiguous keyword'ler.
        # "hızlı" eklendi: "Hızlı ödeme için X kaydedilebilmelidir" → FR fiili varsa FR.
        self._ambiguous_nfr_keywords: frozenset = frozenset({
            "güvenlik", "yedek", "erişilebilir", "yük", "hızlı", "performans",
        })

        # "güvenli" → "güvenlik" substring çakışmasını önler (güvenlik ambiguous sette).
        self._guvenli_re = re.compile(r'güvenli(?!k)')

        self._llm = None  # lazy init

    def _has_strong_nfr_kw(self, text_lower: str) -> bool:
        """Güçlü NFR keyword eşleşmesi — güvenli/güvenlik substring çakışması giderilmiş."""
        for kw in (self.nfr_keywords - self._ambiguous_nfr_keywords):
            if kw == "güvenli":
                if self._guvenli_re.search(text_lower):
                    return True
            elif kw in text_lower:
                return True
        return False

    def _get_llm(self):
        """LLM client'ı ilk kullanımda başlatır."""
        if self._llm is None:
            try:
                from modules.llm_client import LLMClient
                self._llm = LLMClient()
            except Exception:
                self._llm = False  # başlatılamadı, tekrar deneme
        return self._llm if self._llm else None

    def _classify_with_llm(self, text: str) -> str | None:
        """Katman 3: LLM few-shot sınıflandırma. Başarısız olursa None döner."""
        llm = self._get_llm()
        if not llm:
            return None
        try:
            response = llm.chat(
                system_prompt=_CLASSIFICATION_SYSTEM_PROMPT,
                user_prompt=f'Gereksinim: "{text}"',
            )
            text_out = (response.content if hasattr(response, "content") else str(response)).strip().upper()
            if "NON_FUNCTIONAL" in text_out:
                return "NON_FUNCTIONAL"
            if "FUNCTIONAL" in text_out:
                return "FUNCTIONAL"
        except Exception:
            pass
        return None

    def classify(self, requirement: Requirement) -> Requirement:
        """Gereksinimi FUNCTIONAL veya NON_FUNCTIONAL olarak etiketler."""
        text = requirement.text.strip()
        if not text:
            return requirement

        text_lower = text.lower()

        has_nfr_num = any(p.search(text_lower) for p in self.nfr_numeric_patterns)
        has_strong_nfr_kw = self._has_strong_nfr_kw(text_lower)
        has_nfr_kw = has_strong_nfr_kw or any(
            kw in text_lower for kw in self._ambiguous_nfr_keywords
        )

        # Katman 1: Açık FR eylemi var + güçlü NFR sinyali yok → FUNCTIONAL
        # Ambiguous keyword'ler (güvenlik, yedek) tek başlarına K1'i bloklamaz;
        # nesne konumunda geçebilirler ("güvenlik loglarını görüntüleyebilmeli").
        if _FR_VERB_RE.search(text_lower) and not has_strong_nfr_kw and not has_nfr_num:
            requirement.req_type = "FUNCTIONAL"
            return requirement

        # Katman 2: NFR keyword veya sayısal eşik → NON_FUNCTIONAL
        if has_nfr_kw or has_nfr_num:
            requirement.req_type = "NON_FUNCTIONAL"
            return requirement

        # Katman 3: Belirsiz — LLM'e sor
        llm_result = self._classify_with_llm(text)
        requirement.req_type = llm_result if llm_result else "FUNCTIONAL"
        return requirement
