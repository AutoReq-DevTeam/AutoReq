"""
modules/improver.py — Gereksinim İyileştirme Modülü
Sorumlu: Eren Eyyüpkoca

Açıklama:
"Hızlı", "kolay" gibi ölçülemeyen (muğlak) ifadeleri tespit eder ve bu ifadeleri 
teknik, ölçülebilir kriterlere dönüştürmek için öneriler üretir.
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
        # TODO: Üye 2 — Muğlak ifade sözlüğü (NLP tabanlı ön kontrol)
        # TODO: Üye 2 — LLM (Few-shot prompting) kullanarak muğlak ifadeleri teknik metne dönüştür
        #               Örn: "süper hızlı olsun" → LLM → "Sistem yanıt süresi 500ms altında olmalıdır"
        raise NotImplementedError("RequirementImprover.improve() henüz implemente edilmedi.")
