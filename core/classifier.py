"""
core/classifier.py — Gereksinim Sınıflandırıcı
Sorumlu: Üye 1 (NLP & Preprocessing)

Açıklama:
Analiz edilen gereksinim cümlelerini türlerine göre (Fonksiyonel / Fonksiyonel Olmayan) 
etiketler. Bu sınıflandırma, dökümantasyon ve önceliklendirme aşamaları 
için temel veriyi sağlar.
"""

from .models import Requirement


class RequirementClassifier:
    """Gereksinimleri F / NFR olarak sınıflandırır."""

    def classify(self, requirement: Requirement) -> Requirement:
        """
        Parametreler:
            requirement (Requirement): Sınıflandırılacak gereksinim.

        Döndürür:
            Requirement: req_type alanı güncellenmiş gereksinim.
        """
        # TODO: Üye 1 — scikit-learn ile sınıflandırıcı modeli eğit/yükle
        # TODO: Üye 1 — Anahtar kelime tabanlı kural seti (fallback)
        raise NotImplementedError("RequirementClassifier.classify() henüz implemente edilmedi.")
