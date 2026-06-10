"""
scripts/benchmark_20.py — NLP vs Hibrit sistem karşılaştırmalı zaman ölçümü
20 cümle üzerinde cümle başına ortalama süreyi hesaplar.
Gerçek LLM çağrıları Katman 3'e düşen belirsiz cümleler için tetiklenir.
"""

import sys
import time
import os
from pathlib import Path

# .env yükle
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

# Proje kökünü path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

# Streamlit bağımlılığını mock'la
import unittest.mock as mock
st_mock = mock.MagicMock()
sys.modules["streamlit"] = st_mock

# ── 20 test cümlesi ──────────────────────────────────────────────────────────
# Katman dağılımı:
#   1-7  → Katman 1 (FR verb regex)         : hızlı, LLM yok
#   8-13 → Katman 2 (NFR keyword/pattern)   : hızlı, LLM yok
#  14-20 → Katman 3 (LLM belirsiz)          : FR verb YOK, NFR keyword YOK
SENTENCES = [
    # ── Katman 1: Açık FR fiil sonekleri ──────────────────────────────────────
    "Kullanıcı sisteme kullanıcı adı ve şifresiyle giriş yapabilmelidir.",
    "Kullanıcı sepetine ürün ekleyebilmeli ve ödeme adımına geçebilmelidir.",
    "Admin panelinden yeni ürün eklenebilmeli ve mevcut ürünler güncellenebilmelidir.",
    "Müşteri, iade talebini oluşturabilmeli ve iade sürecini takip edebilmelidir.",
    "Sistem yöneticisi, kullanıcı rollerini atayabilmeli ve yetkileri düzenleyebilmelidir.",
    "Kullanıcı, profil fotoğrafını yükleyebilmeli ve önizleme görebilmelidir.",
    "İndirim kuponu yalnızca bir kez kullanılabilmelidir.",
    # ── Katman 2: NFR keyword / sayısal pattern ───────────────────────────────
    "Sistem, eş zamanlı en fazla 10.000 kullanıcıyı desteklemelidir.",
    "API yanıt süresi 200 ms'yi geçmemelidir.",
    "Kredi kartı bilgileri sunucuda saklanmamalı; yalnızca tokenize hali tutulmalıdır.",
    "Uygulama %99,9 uptime sağlamalı ve kesintisiz hizmet vermelidir.",
    "Veriler AES-256 şifrelemesiyle güvenli şekilde saklanmalıdır.",
    "Hata oranı aylık %0,1'i aşmamalıdır.",
    # ── Katman 3: Belirsiz → LLM çağrısı ─────────────────────────────────────
    # (FR verb soneki YOK, NFR keyword YOK → Katman 3 tetiklenir)
    "Platform düzenleyici gereklilikleri karşılamalıdır.",
    "Veri aktarımları bölgesel veri koruma yasalarına uygun olmalıdır.",
    "Uygulama çok dilli olmalıdır.",
    "Sistem mobil cihazlara tam uyumlu olmalıdır.",
    "Raporlar PDF formatında dışa aktarılabilir olmalıdır.",
    "Arayüz farklı ekran boyutlarına adapte olmalıdır.",
    "Belgeler otomatik olarak arşivlenmelidir.",
]

assert len(SENTENCES) == 20, "Tam olarak 20 cümle olmalı"


def _classify_nlp_only(text_lower, classifier):
    """Katman 1 + Katman 2 — LLM yok."""
    from core.classifier import _FR_VERB_RE
    has_nfr_num = any(p.search(text_lower) for p in classifier.nfr_numeric_patterns)
    has_strong_nfr_kw = classifier._has_strong_nfr_kw(text_lower)
    has_nfr_kw = has_strong_nfr_kw or any(
        kw in text_lower for kw in classifier._ambiguous_nfr_keywords
    )
    if _FR_VERB_RE.search(text_lower) and not has_strong_nfr_kw and not has_nfr_num:
        return "FUNCTIONAL", False   # (tip, llm_kullanıldı_mı)
    if has_nfr_kw or has_nfr_num:
        return "NON_FUNCTIONAL", False
    return "FUNCTIONAL", False  # belirsiz → NLP-only modda varsayılan


def run_nlp_only(sentences, preprocessor, classifier, ner, priority):
    """Sadece NLP katmanları (Stanza + regex/keyword). LLM yok."""
    from core.models import Requirement
    times = []
    for sent in sentences:
        t0 = time.perf_counter()
        doc = preprocessor.nlp(sent)
        tokens, lemmas, pos_tags = [], [], []
        for stanza_sent in doc.sentences:
            for word in stanza_sent.words:
                w = word.text.lower()
                if w not in preprocessor.stop_words and word.upos != "PUNCT":
                    tokens.append(w)
                    lemmas.append(word.lemma.lower() if word.lemma else w)
                    pos_tags.append(word.upos)
        req = Requirement(id="REQ_TMP", text=sent, tokens=tokens,
                          lemmas=lemmas, pos_tags=pos_tags, source_index=0)
        req.req_type, _ = _classify_nlp_only(sent.lower(), classifier)
        req = ner.recognize(req)
        req = priority.detect(req)
        times.append(time.perf_counter() - t0)
    return times


def run_hybrid(sentences, preprocessor, classifier, ner, priority):
    """Tam hibrit: NLP + Katman 3 LLM (belirsiz cümleler için)."""
    from core.models import Requirement
    from core.classifier import _FR_VERB_RE
    times = []
    llm_flags = []
    for sent in sentences:
        # LLM çağrısını izle
        original_fn = classifier._classify_with_llm
        llm_called = [False]
        def _tracked(text, _orig=original_fn):
            llm_called[0] = True
            return _orig(text)
        classifier._classify_with_llm = _tracked

        t0 = time.perf_counter()
        doc = preprocessor.nlp(sent)
        tokens, lemmas, pos_tags = [], [], []
        for stanza_sent in doc.sentences:
            for word in stanza_sent.words:
                w = word.text.lower()
                if w not in preprocessor.stop_words and word.upos != "PUNCT":
                    tokens.append(w)
                    lemmas.append(word.lemma.lower() if word.lemma else w)
                    pos_tags.append(word.upos)
        req = Requirement(id="REQ_TMP", text=sent, tokens=tokens,
                          lemmas=lemmas, pos_tags=pos_tags, source_index=0)
        req = classifier.classify(req)
        req = ner.recognize(req)
        req = priority.detect(req)
        times.append(time.perf_counter() - t0)
        llm_flags.append(llm_called[0])

        classifier._classify_with_llm = original_fn  # geri yükle
    return times, llm_flags


def print_table(sentences, nlp_times, hybrid_times, llm_flags):
    header = (f"{'#':>2}  {'Cümle (ilk 52 karakter)':<54}  "
              f"{'NLP (ms)':>9}  {'Hibrit (ms)':>11}  {'LLM?':>5}  {'Ek yük':>8}")
    print(header)
    print("-" * len(header))
    for i, (sent, nt, ht, llm) in enumerate(zip(sentences, nlp_times, hybrid_times, llm_flags), 1):
        overhead = (ht - nt) * 1000
        llm_mark = "✓" if llm else "-"
        print(f"{i:>2}  {sent[:52]:<54}  {nt*1000:>9.1f}  {ht*1000:>11.1f}  {llm_mark:>5}  {overhead:>+8.1f}")


def main():
    print("=" * 90)
    print("AutoReq — 20 Cümle Benchmark: NLP vs Hibrit (Gerçek LLM)")
    print("=" * 90)

    llm_ok = bool(os.getenv("GEMINI_API_KEY") or os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENROUTER_API_KEY"))
    print(f"\n  API key durumu : {'✓ Yüklendi' if llm_ok else '✗ Bulunamadı — LLM devre dışı'}")

    print("\n[1/3] NLP modülleri yükleniyor (Stanza, NLTK)...")
    from core.preprocessor import TextPreprocessor
    from core.classifier import RequirementClassifier
    from core.ner import EntityRecognizer
    from core.priority_detector import PriorityDetector

    preprocessor = TextPreprocessor()
    classifier_nlp = RequirementClassifier()
    classifier_hybrid = RequirementClassifier()
    ner = EntityRecognizer()
    priority = PriorityDetector()
    print("    Modüller hazır.")

    # Isınma turu: Stanza JIT gecikmesini yok et
    for s in SENTENCES[:3]:
        preprocessor.nlp(s)

    # ── NLP-ONLY ────────────────────────────────────────────────────────────
    print("\n[2/3] NLP-ONLY çalışıyor (20 cümle)...")
    nlp_times = run_nlp_only(SENTENCES, preprocessor, classifier_nlp, ner, priority)
    print(f"    Tamamlandı. Toplam: {sum(nlp_times)*1000:.1f} ms")

    # ── HİBRİT ──────────────────────────────────────────────────────────────
    print("\n[3/3] HİBRİT çalışıyor (20 cümle, gerçek LLM dahil)...")
    hybrid_times, llm_flags = run_hybrid(SENTENCES, preprocessor, classifier_hybrid, ner, priority)
    llm_count = sum(llm_flags)
    print(f"    Tamamlandı. Toplam: {sum(hybrid_times)*1000:.1f} ms  |  LLM çağrısı: {llm_count}/20")

    # ── TABLO ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 90)
    print("DETAYLI SONUÇLAR")
    print("=" * 90)
    print_table(SENTENCES, nlp_times, hybrid_times, llm_flags)

    # ── ÖZET ────────────────────────────────────────────────────────────────
    avg_nlp = sum(nlp_times) / len(nlp_times) * 1000
    avg_hybrid = sum(hybrid_times) / len(hybrid_times) * 1000

    nlp_no_llm = [t for t, f in zip(hybrid_times, llm_flags) if not f]
    nlp_with_llm = [t for t, f in zip(hybrid_times, llm_flags) if f]

    print("\n" + "=" * 90)
    print("ÖZET")
    print("=" * 90)
    print(f"  Toplam cümle                           : {len(SENTENCES)}")
    print(f"  LLM tetiklenen cümle (Katman 3)        : {llm_count}")
    print(f"  NLP ortalama cümle başına              : {avg_nlp:.2f} ms")
    print(f"  Hibrit ortalama cümle başına           : {avg_hybrid:.2f} ms")
    print(f"  LLM ek yük (ortalama, tüm 20 cümle)   : {avg_hybrid - avg_nlp:+.2f} ms")
    if nlp_with_llm:
        avg_llm_sent = sum(nlp_with_llm) / len(nlp_with_llm) * 1000
        avg_nlp_sent = sum(nlp_no_llm) / len(nlp_no_llm) * 1000 if nlp_no_llm else avg_nlp
        print(f"  LLM çağrılan cümle ort. süresi        : {avg_llm_sent:.2f} ms")
        print(f"  LLM çağrılmayan cümle ort. süresi     : {avg_nlp_sent:.2f} ms")
        print(f"  LLM saf ek yükü (sadece LLM cümleleri): {avg_llm_sent - avg_nlp:.2f} ms")
    print(f"  Hız farkı (Hibrit/NLP)                 : {avg_hybrid/avg_nlp:.2f}x")
    print("=" * 90)


if __name__ == "__main__":
    main()
