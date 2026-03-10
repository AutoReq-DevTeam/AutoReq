"""
core/classifier.py — Gereksinim Sınıflandırıcı (Etiketleyici)
Sahibi: Üye 1 (Metin Hazırlık)

Senin Görevin:
Tertemiz hale gelmiş cümleler sana gelecek. Senin işin bu cümlelere iki farklı etiket yapıştırmak:
- 'F' (Fonksiyonel): Eğer cümle sistemin yapacağı bir işten bahsediyorsa (Örn: "Kullanıcı giriş yapabilmeli")
- 'NFR' (Fonksiyonel Olmayan): Eğer cümle hız, güvenlik, dil gibi kalite şartlarından bahsediyorsa (Örn: "Sistem en geç 2 saniyede açılmalı", "Şifreler güvenli tutulmalı")

Çıktı: "Her cümlenin ne tür bir istek olduğunu belirten etiketli liste."
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
