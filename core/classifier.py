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

    def __init__(self):
        # Kural tabanlı sınıflandırma için Non-Functional Keyword (NFR) kelime havuzu
        self.nfr_keywords = [
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
            "kullanıcı",
            "dostu",
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
        ]

    def classify(self, requirement: Requirement) -> Requirement:
        """
        Gelen metni alır, eğer metin içinde güvenlik, hız veya arayüzle alakalı
        özel kalite kelimeleri geçiyorsa onu NFR (Fonksiyonel Olmayan) yapar.
        """
        # Python'da string eşleştirmesi büyük/küçük harf duyarlı (Case-Sensitive) olduğu için
        # önce gereksinim metnini tamamen küçük harfe (.lower()) çeviriyoruz.
        # Böylece "Hızlı" ile "hızlı" karmaşasından kurtuluyoruz.
        text_to_check = requirement.text.lower()

        # 'any()' fonksiyonu bir Python generator (üreteç) ile çalışır.
        # Cümlenin içinde self.nfr_keywords listesinden HERHANGİ BİRİ eşleşirse True döner.
        # Bu yaklaşım arka planda for döngüsüyle tek tek bakmaktan daha performanslıdır.
        is_nfr = any(keyword in text_to_check for keyword in self.nfr_keywords)

        if is_nfr:
            requirement.req_type = "NON_FUNCTIONAL"
        else:
            # Standart bir yazılım davranışı belirtiyorsa FUNCTIONAL kabul ediyoruz
            requirement.req_type = "FUNCTIONAL"

        return requirement
