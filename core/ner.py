"""
core/ner.py — Varlık Tanıma (Named Entity Recognition)
Sahibi: Üye 1 (NLP Core & Preprocessing)

Görev: Metindeki aktörleri (Kullanıcı, Admin, Sistem) ve nesneleri tespit et.
"""

from .models import Requirement


class EntityRecognizer:
    """spaCy NER kullanarak metindeki varlıkları tanır."""

    def recognize(self, requirement: Requirement) -> Requirement:
        """
        Parametreler:
            requirement (Requirement): İşlenecek gereksinim.

        Döndürür:
            Requirement: actors ve objects alanları doldurulmuş gereksinim.
        """
        # TODO: Üye 1 — spaCy NER pipeline'ı yükle
        # TODO: Üye 1 — Aktör listesini tespit et → requirement.actors
        # TODO: Üye 1 — Nesne listesini tespit et → requirement.objects
        raise NotImplementedError("EntityRecognizer.recognize() henüz implemente edilmedi.")
