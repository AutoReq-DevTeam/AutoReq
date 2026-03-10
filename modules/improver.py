"""
modules/improver.py — İyileştirme Önerileri
Sahibi: Üye 2 (Akıllı Analiz Modülleri)

Görev: "Hızlı olmalı" gibi muğlak ifadeleri ölçülebilir kriterlere dönüştür.
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
