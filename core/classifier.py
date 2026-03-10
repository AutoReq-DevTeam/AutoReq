"""
core/classifier.py — Gereksinim Sınıflandırıcı
Sahibi: Üye 1 (NLP Core & Preprocessing)

Görev: Her gereksinimi Fonksiyonel (F) veya Fonksiyonel Olmayan (NFR) olarak etiketle.
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
