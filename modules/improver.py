"""
modules/improver.py — Muğlak Kelime Temizleyicisi
Sahibi: Üye 2 (Akıllı Kontrol Modülü)

Senin Görevin:
Yazılımcılar yuvarlak lafları sevmez. Müşteri "Sistem çok süper hızlı açılmalı" dediğinde yazılımcı ne yapacağını bilemez.
Senin işin metindeki "hızlı", "kolay", "hemen", "güzel" gibi ölçülemeyen (muğlak) kelimeleri tespit etmek.
Ardından bunları ölçülebilir, teknik bir dile çevirmek (Örn: "Sistem açılış süresi < 1 saniye olmalıdır").

Çıktı: "Daha teknik ve net yazılmış, düzeltilmiş profesyonel cümleler."
"""

from core.models import Requirement


class RequirementImprover:
    """Muğlak gereksinimleri ölçülebilir hale getirir."""

    def improve(self, requirement: Requirement) -> dict:
        """
        Parametreler:
            requirement (Requirement): İyileştirilecek gereksinim.

        Döndürür:
            dict: {'original', 'improved', 'reason'} alanları olan öneri dict'i.
        """
        # TODO: Üye 2 — Muğlak ifade sözlüğü oluştur (hızlı, kolay, düzgün, vs.)
        # TODO: Üye 2 — Her muğlak ifadeye ölçülebilir alternatif öner
        #               Örn: "hızlı" → "2 saniyenin altında yanıt vermeli"
        raise NotImplementedError("RequirementImprover.improve() henüz implemente edilmedi.")
