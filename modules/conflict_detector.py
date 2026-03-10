"""
modules/conflict_detector.py — Çelişki Tespiti
Sahibi: Üye 2 (Akıllı Analiz Modülleri)

Görev: Gereksinimler arasındaki mantıksal çelişkileri ve zıtlıkları tespit et.
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
