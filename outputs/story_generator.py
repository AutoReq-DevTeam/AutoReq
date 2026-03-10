"""
outputs/story_generator.py — Hikayeci (User Story Üretici)
Sahibi: Üye 3 (Rapor ve Çıktı Aşaması)

Senin Görevin:
Yazılımcılar uzun metinler yerine kısa görev notlarını sever. Bu notlara 'User Story' denir.
Senin işin elimizdeki gereksinimleri şu formata çevirmek:
'Bir [Rol] olarak, [Bunu yapmak] istiyorum, çünkü [Bana şöyle bir faydası var].'
Örnek: Bir "Öğrenci" olarak "notlarımı görmek" istiyorum çünkü "durumumu takip etmeliyim".

Çıktı: "Yazılımcıların önüne yapıştırılacak görev post-it'leri gibi kısa hikayeler."
"""

from core.models import AnalysisReport


class StoryGenerator:
    """Gereksinimlerden User Stories üretir."""

    def generate(self, report: AnalysisReport) -> list[dict]:
        """
        Parametreler:
            report (AnalysisReport): Analiz raporu.

        Döndürür:
            list[dict]: Her biri {'role', 'goal', 'benefit', 'acceptance_criteria'} içeren hikaye listesi.
        """
        # TODO: Üye 3 — Her gereksinim için rol, hedef ve fayda alanlarını çıkar
        # TODO: Üye 3 — DOCX ve JSON olarak da dışa aktarma seçeneği ekle
        raise NotImplementedError("StoryGenerator.generate() henüz implemente edilmedi.")
