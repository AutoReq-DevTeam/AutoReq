"""
modules/conflict_detector.py — Çelişki ve Mantık Analizörü
Sorumlu: Eren Eyyüpkoca

Açıklama:
Gereksinimler arasındaki mantıksal çelişkileri ve teknik zıtlıkları tespit eder. 
NLP ve LLM tekniklerini kullanarak belgelerdeki uyumsuzlukları raporlar.
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
        # TODO: Üye 2 — Zıt anahtar kelime çiftlerini tespit et (Lokal NLP)
        # TODO: Üye 2 — LLM kullanarak mantıksal ve anlamsal çelişkileri tespit et
        # TODO: Üye 2 — Belirsiz/muğlak ifadeleri sezgilere dayalı (LLM) olarak uyar
        raise NotImplementedError("ConflictDetector.detect() henüz implemente edilmedi.")
