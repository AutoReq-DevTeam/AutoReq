"""
modules/conflict_detector.py — Çelişki ve Mantık Hatası Dedektifi
Sahibi: Üye 2 (Akıllı Kontrol Modülü)

Senin Görevin:
Müşteriler bazen ne istediklerini bilmezler ve kendi kendileriyle çelişirler.
Örneğin yukarıda "Kullanıcılar şifre girmeden sisteme girebilsin" derken, aşağıda "Sistem son derece güvenli olmalı" diyebilir.
Senin işin, bu birbiriyle zıtlaşan, teknik olarak imkansız olan istekleri yan yana koyup "Hop, burada bir mantık hatası var!" diye uyarı verecek kodu yazmak.

Çıktı: "Hatalı isteklerin altı çizilmiş bir hata raporu."
"""

from core.models import ParsedDocument, AnalysisReport


class ConflictDetector:
    """Gereksinimler arası çelişkileri tespit eder."""

    def detect(self, doc: ParsedDocument) -> list[dict]:
        """
        Parametreler:
            doc (ParsedDocument): Üye 1'den gelen ayrıştırılmış belge.

        Döndürür:
            list[dict]: Her biri {'req_ids', 'conflict_type', 'reason'} içeren çelişki listesi.
        """
        # TODO: Üye 2 — Zıt anahtar kelime çiftlerini tespit et (örn: "her zaman" vs "asla")
        # TODO: Üye 2 — Aynı aktöre ait çelişen izin kurallarını bul
        # TODO: Üye 2 — Belirsiz/muğlak ifadeleri uyar
        raise NotImplementedError("ConflictDetector.detect() henüz implemente edilmedi.")
