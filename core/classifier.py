"""
core/classifier.py — Gereksinim Sınıflandırıcı
Sorumlu: Üye 1 (NLP & Preprocessing)

Açıklama:
Bu modül, metindeki gereksinimlerin "Fonksiyonel" mi yoksa "Fonksiyonel Olmayan (NFR)"
mi olduğunu belirler. Projenin MVP aşaması gereği Makine Öğrenmesi (Scikit-Learn) yerine
"Heuristic (Sezgisel / Kural Tabanlı)" bir mimari kullanılmıştır. Elimizde modeli eğitecek
orijinal (NFR/FR) Türkçe veri seti bulunmadığından, basit ve hızlı olan kural tabanlı
kelime eşleştirme en optimize yoldur (KISS prensibi).
"""

import re

from .models import Requirement


class RequirementClassifier:
    """Gereksinimleri F / NFR olarak sınıflandırır."""

    def __init__(self) -> None:
        """NFR anahtar kelime kümesiyle sınıflandırıcıyı başlatır."""
        # Kural tabanlı sınıflandırma için Non-Functional Keyword (NFR) kelime havuzu.
        # frozenset kullanılır — her classify() çağrısında O(1) üyelik kontrolü sağlar
        # (list ile aynı eleman sayısında O(N) olurdu).
        self.nfr_keywords: frozenset = frozenset([
            # Performans
            "hızlı", "saniye", "performans", "gecikme", "milisaniye", "mili saniye",
            "eş zamanlı", "eşzamanlı", "yanıt süresi", "throughput",
            # Güvenlik
            "güvenli", "kripto", "ssl", "korunmalı", "güvenlik", "mahremiyet",
            # Yetkilendirme & ölçeklenebilirlik
            "yetki", "ölçek", "kapasite",
            # Erişilebilirlik & süreklilik
            "kesintisiz", "ulaşılabilir", "uptime", "erişilebilir", "yedek",
            # Kullanılabilirlik
            "kullanıcı dostu", "arayüz", "responsive", "kullanılabilirlik",
            # Uyumluluk
            "uyumluluk", "standart",
            # Güvenilirlik
            "crash", "hata oranı",
            # Kısıtlama ifadeleri — ölçülebilir eşiklerin NFR sinyali
            "kaldırabilmeli", "desteklemelidir", "uyumlu olmalı", "uyumlu olmali",
            "geçmemelidir", "geçmemeli", "aşmamalı", "aşmamali",
            "en fazla", "en az", "minimum", "maksimum", "en çok", "en geç",
            "karşılamalıdır", "sağlamalıdır",
            "altında", "üzerinde",
        ])

        # Sayısal eşik pattern'ları: "%0.1 crash oranı", "10.000 kullanıcı" gibi
        # somut kriter içeren cümleleri yakalamak için regex kullanılır.
        self.nfr_numeric_patterns: list = [
            re.compile(r'%\s*\d'),                                                   # %0.1, %99
            re.compile(r'\d\s*%'),                                                   # 99.9%
            re.compile(r'\d[\d,\.]*\s*(ms\b|sn\b|milisaniye|mili\s*saniye)'),       # zaman eşiği (ms/sn)
            re.compile(r'\d[\d,\.]*\s*(eş\s*zamanlı|eşzamanlı|concurrent)'),        # eş zamanlı kullanıcı
            re.compile(r'\d{1,3}\.\d{3}\s*(kullanıcı|istek|işlem|bağlantı|kayıt)'), # 10.000 kullanıcı
        ]

    def classify(self, requirement: Requirement) -> Requirement:
        """Gereksinimi FUNCTIONAL veya NON_FUNCTIONAL olarak etiketler.

        Gereksinim metni boşsa req_type değiştirilmeden döndürülür.

        Parametreler:
            requirement: Sınıflandırılacak Requirement nesnesi.

        Döndürür:
            Requirement: req_type alanı güncellenmiş nesne (in-place).
        """
        text = requirement.text.strip()
        if not text:
            # Boş metin — sınıflandırma yapılamaz, mevcut değeri koru
            return requirement

        # Python'da string eşleştirmesi büyük/küçük harf duyarlı olduğu için
        # önce metni küçük harfe çeviriyoruz.
        text_lower = text.lower()

        # frozenset O(1) üyelik kontrolü sağlar.
        is_nfr = any(keyword in text_lower for keyword in self.nfr_keywords)

        # Keyword eşleşmesi yoksa sayısal threshold pattern'larını dene.
        if not is_nfr:
            is_nfr = any(pattern.search(text_lower) for pattern in self.nfr_numeric_patterns)

        requirement.req_type = "NON_FUNCTIONAL" if is_nfr else "FUNCTIONAL"
        return requirement
