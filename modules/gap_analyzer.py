"""
modules/gap_analyzer.py — Eksik Gereksinim Analizörü
Sorumlu: Eren Eyyüpkoca

Açıklama:
Mevcut gereksinimleri analiz ederek, sistemin bütünlüğü için kritik olan ancak
atlanmış özellikleri (örn: kayıt var ama şifre sıfırlama yok) tespit eder ve öneriler sunar.

LLM entegrasyonu için prompt katmanı: modules/gap_prompts.py
- build_gap_analysis_system_prompt() — persona + standart senaryo referansı + JSON şeması
- build_gap_analysis_user_prompt(...) — gereksinim bloğu ve isteğe bağlı domain_hint
"""

from core.models import ParsedDocument


class GapAnalyzer:
    """Eksik gereksinimleri tespit eder ve öneri sunar."""

    def analyze(self, doc: ParsedDocument) -> list[dict]:
        """
        Parametreler:
            doc (ParsedDocument): Üye 1'den gelen ayrıştırılmış belge.

        Döndürür:
            list[dict]: Her biri {'missing_area', 'suggestion', 'severity'} içeren boşluk listesi.
        """
        # TODO: Üye 2 — Mevcut gereksinimleri analiz edip projenin kapsamını belirle (E-ticaret, Fintech, vb.)
        # TODO: Üye 2 — LLM kullanarak "Dünya standartlarında bu tip bir sistemde ne eksik olabilir?" sorusuna yanıt ara
        # TODO: Üye 2 — Eksik iş akışlarını (örn: "Giriş var ama Şifremi Unuttum yok") raporla
        raise NotImplementedError("GapAnalyzer.analyze() henüz implemente edilmedi.")
