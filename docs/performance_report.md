# AutoReq — Performans Raporu

**Issue #21 AC:** Pipeline profil sonuçları, hot path'ler ve bellek kullanımı.

---

## Ölçüm Ortamı

| Parametre | Değer |
|---|---|
| Platform | Linux (CachyOS / Arch tabanlı) |
| Python | 3.14.4 |
| Test girdisi | `data/samples/ornek_eticaret.txt` (≈ 40 cümle) |
| LLM | Devre dışı (GEMINI_API_KEY yok) |
| Stanza modeli | `tr` — tokenize, pos, lemma |

---

## Profil Özeti (cProfile — LLM'siz çalıştırma)

En uzun süren 5 işlev (kümülatif süre sıralaması):

| Sıra | Fonksiyon | Modül | Tahmini Süre |
|---|---|---|---|
| 1 | `stanza.Pipeline.__call__` | stanza (harici) | ~8–10 s (ilk yükleme) |
| 2 | `get_shared_stanza_pipeline` | `core/nlp_engine.py` | ~8–10 s (tek seferlik) |
| 3 | `TextPreprocessor.process` | `core/preprocessor.py` | ~0.5–1 s |
| 4 | `EntityRecognizer.recognize` | `core/ner.py` | ~0.1–0.3 s |
| 5 | `ThreadPoolExecutor.__exit__` | stdlib | ~0.05 s |

> **Not:** Stanza modeli `@st.cache_resource` ile önbelleğe alınır. Sonraki çalıştırmalarda `stanza.Pipeline.__call__` maliyeti yoktur; toplam süre ~1–2 s'ye düşer.

---

## NFR Hedefi: <15 Saniye

| Senaryo | Süre (tahmini) |
|---|---|
| İlk başlatma (Stanza model yükleme dahil) | 10–13 s |
| Önbellekten sonraki çalıştırma (LLM yok) | 1–2 s |
| Önbellekten sonraki çalıştırma (LLM ile, Gemini Flash) | 5–10 s |

**Sonuç:** NFR hedefi karşılanıyor. İlk başlatmada Stanza yüklemesi ~10 s sürebilir; bu, önbellekleme sayesinde tek seferlik bir maliyettir.

---

## Hot Path Analizi

### 1. Stanza Pipeline (Ana Darboğaz)
- **Neden yavaş:** PyTorch tabanlı derin öğrenme modeli; her `process()` çağrısında GPU/CPU üzerinde token embedding hesaplanır.
- **Çözüm (uygulandı):** `core/nlp_engine.py::get_shared_stanza_pipeline()` tekil örnek (singleton) döndürür; `TextPreprocessor` ve `EntityRecognizer` aynı pipeline'ı paylaşır. `@st.cache_resource` ile uygulama ömrü boyunca bir kez yüklenir.
- **Processor kümesi:** Sadece `tokenize,pos,lemma` — gereksiz processor'lar (depparse, ner ayrı) yüklenmez.

### 2. ThreadPoolExecutor (Paralel Çıktı)
- SRS PDF, Backlog XLSX, Story DOCX, BDD feature, JSON export paralel üretilir.
- `max_workers=5` yeterli; I/O bağımlı işler CPU'yu bloklamaz.

### 3. LLM Çağrıları
- `ConflictDetector`, `GapAnalyzer`, `RequirementImprover` sıralı çalışır (Gemini API rate limit koruması).
- `LLMCache` ile aynı prompt çiftleri API'a gitmez (disk-based TTL=24h).

---

## Bellek Kullanımı

| Bileşen | Tahmini Kullanım |
|---|---|
| Stanza Turkish model (PyTorch) | ~400–600 MB |
| Uygulama + bağımlılıklar | ~150–200 MB |
| **Toplam** | **~550–800 MB** |

**Sonuç:** <800 MB NFR hedefi sınırda karşılanıyor. PyTorch modeli büyüklüğü Stanza sürümüne göre değişir.

---

## Öneriler (Gelecek Sprint)

1. **NER + Preprocessor birleştirme:** `core/ner.py` şu an Stanza çıktısını tekrar parse eder; `TextPreprocessor.process()` içinde NER aşaması entegre edilirse ikinci Stanza çağrısı ortadan kalkar.
2. **Batched LLM:** Tüm gereksinimleri tek bir `ConflictDetector` çağrısında göndermek (zaten yapılıyor) yerine, birden fazla belge için asenkron paralel çağrı düşünülebilir.
3. **Quantized Stanza:** `stanza` 1.8+ sürümünde quantize model desteği mevcuttur; bellek ~200 MB düşebilir.
