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

from .models import Requirement


class RequirementClassifier:
    """Gereksinimleri F / NFR olarak sınıflandırır."""

    def __init__(self) -> None:
        """NFR anahtar kelime kümesiyle sınıflandırıcıyı başlatır."""
        # Kural tabanlı sınıflandırma için Non-Functional Keyword (NFR) kelime havuzu.
        # frozenset kullanılır — her classify() çağrısında O(1) üyelik kontrolü sağlar
        # (list ile aynı eleman sayısında O(N) olurdu).
        self.nfr_keywords: frozenset = frozenset([
            "hızlı",
            "saniye",
            "performans",
            "güvenli",
            "şifre",
            "kripto",
            "ssl",
            "yetki",
            "ölçek",
            "kesintisiz",
            "ulaşılabilir",
            "uptime",
            "erişilebilir",
            "kullanıcı dostu",
            "arayüz",
            "responsive",
            "gecikme",
            "milisaniye",
            "korunmalı",
            "yedek",
            "uyumluluk",
            "standart",
            "kapasite",
            "mili saniye",
            "kullanılabilirlik",
            "güvenlik",
        ])

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

        requirement.req_type = "NON_FUNCTIONAL" if is_nfr else "FUNCTIONAL"
        return requirement
