"""
core/ner.py — Cümledeki Rolleri ve Nesneleri Ayıklayıcı
Sahibi: Üye 1 (Metin Hazırlık)

Senin Görevin:
Sana gelen cümlenin içinde 'kim, ne yapıyor?' sorusunun cevabını cımbızla çekmek.
Örneğin: "Müşteri sisteme kredi kartı ile ödeme yapabilmelidir" cümlesi geldiğinde:
- Aktör (Rol): "Müşteri", "Sistem"
- Nesne: "kredi kartı", "ödeme"
kısımlarını bulup listeye yazacaksın. (Bunun için spaCy kütüphanesini kullanacaksın).

Çıktı: "Cümledeki ana karakterlerin ve anahtar elemanların listesi."
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
