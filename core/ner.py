"""
core/ner.py — Varlık ve Nesne Ayıklayıcı (NER)
Sorumlu: Üye 1 (NLP & Preprocessing)

Açıklama:
Cümle içerisinden aktörleri (Kullanıcı, Sistem, vb.) ve temel nesneleri (Kredi Kartı, Sipariş vb.)
tespit eder. Bu bilgiler, gereksinimlerin kapsamını ve etkileşim noktalarını
belirlemek için kullanılır.
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
