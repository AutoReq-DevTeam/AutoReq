# 🧭 AGENT_GUIDE — AutoReq için Yapay Zeka Modeli Öğreticisi

> **Bu dosyanın amacı:** Bir AI kodlama asistanının (özellikle düşük/orta kapasiteli modellerin) **tek bir dosyayı okuyarak** projenin tamamına hakim olmasını sağlamaktır. Kodu açmadan önce bu dosyayı sonuna kadar oku. Burada her modülün **ne yaptığı**, **hangi sözleşmelere uyduğu**, **hangi tuzakların bulunduğu** ve **bir özelliği değiştirirken nereyi değiştirmen gerektiği** anlatılır.
>
> **Son güncelleme:** 2026-04-19 · **Hedef kitle:** AI kodlama ajanları + yeni katılan geliştiriciler
>
> 📌 **Not:** Diğer dökümanlar (README.md, CONTEXT.md, FEATURES.md, ROADMAP_AND_ISSUES.md, TEAM.md) hâlâ geçerli ve daha kısa özetler sunar. Bu dosya onların **en kapsamlı, kod-doğruluğu denetlenmiş, ajan dostu** versiyonudur.

---

## 0. 30 Saniyede Proje

- **Ne?** AutoReq, ham Türkçe müşteri metnini alıp **yapılandırılmış yazılım gereksinim dökümanlarına** (SRS, çelişki raporu, eksiklik analizi, user story, BDD, backlog) dönüştüren **hibrit bir NLP + LLM** uygulamasıdır.
- **Çalıştırma:** `streamlit run app.py` → `http://localhost:8501`
- **Beyin:** `core/` (Stanza tabanlı NLP) + `modules/` (Google Gemini tabanlı LLM analizi)
- **Yüz:** `ui/` (Streamlit dashboard, sekmeli sonuç paneli)
- **Çıktı:** `outputs/` (PDF SRS + diğer üreticiler)
- **Dil:** Tüm NLP ve UI **Türkçe** odaklıdır. Stanza Türkçe modeli zorunludur.
- **Lisans:** GNU GPL v3.

---

## 1. Tek Bakışta Mimari (Layered Pipeline)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    app.py  (Orchestrator / Streamlit)               │
│      load_nlp_pipeline()  +  process_text()  +  Streamlit akışı     │
└──────────┬───────────────┬───────────────┬────────────────┬─────────┘
           │               │               │                │
       Layer 1          Layer 2         Layer 3          Layer 4
       core/            modules/        outputs/         ui/
       NLP             LLM Analiz      Döküman          Streamlit
       (Stanza)        (Gemini)        Üretimi          Bileşenleri
```

**Veri akışı sözleşmesi (DTO zinciri):**

```
str (raw_text)
   ↓ TextPreprocessor.process()
ParsedDocument(requirements=[Requirement, ...])
   ↓ RequirementClassifier.classify()  (her Requirement için)
   ↓ EntityRecognizer.recognize()      (her Requirement için)
ParsedDocument (artık req.req_type, req.actors, req.objects dolu)
   ↓ AnalysisReport(parsed_doc=..., conflicts=[], gaps=[], improvements=[])
AnalysisReport
   ↓ ConflictDetector.analyze(doc)  → conflicts listesi (henüz app.py'a bağlı DEĞİL)
   ↓ GapAnalyzer.analyze(doc)       → ❌ stub (NotImplementedError)
   ↓ RequirementImprover.improve()  → ❌ stub (NotImplementedError)
AnalysisReport (zenginleştirilmiş)
   ↓ render_results(report)
Streamlit Sekmeli UI
   ↓ outputs/srs_generator.py (CLI script — şu an UI'dan tetiklenmiyor)
PDF Çıktı
```

> ⚠️ **Kritik gerçek:** `app.py → process_text()` SADECE `core/` katmanını çağırır. `ConflictDetector` kodda hazır ama `process_text()` içinde **çağrılmıyor**. UI'da "Çelişkiler" sekmesi her zaman boş gözükür. Bu, ROADMAP'teki tamamlanmamış entegrasyondur.

---

## 2. Dizin Haritası — Tam Liste

```
AutoReq/
├── app.py                       ★ Streamlit giriş noktası (orchestrator)
├── requirements.txt             Python bağımlılıkları (google-generativeai dahil — Gemini LLM için zorunlu)
├── .env.example                 GEMINI_API_KEY ve model adı şablonu
├── README.md                    Genel proje tanıtımı (İngilizce)
├── LICENSE                      GNU GPL v3
│
├── core/                        Layer 1 — NLP Ön İşleme (Üye 1: Galip)
│   ├── __init__.py              TextPreprocessor, RequirementClassifier, EntityRecognizer, ParsedDocument export
│   ├── models.py                ★ Ortak DTO: Requirement, ParsedDocument, AnalysisReport
│   ├── preprocessor.py          Stanza tr pipeline: tokenize→pos→lemma + stopword temizliği
│   ├── classifier.py            Heuristic FR/NFR sınıflandırıcı (kelime listesi tabanlı)
│   └── ner.py                   Stanza NER + lemma sözlüğü (actor / object) + fallback
│
├── modules/                     Layer 2 — Akıllı Analiz (Üye 2: Eren)
│   ├── __init__.py              ConflictDetector, GapAnalyzer, RequirementImprover, build_analysis_report_from_llm export
│   ├── llm_client.py            ★ Merkezi Gemini istemcisi (LLMClient, LLMResponse, LLMClientError)
│   ├── conflict_detector.py     ✅ Tamamlanmış: pairwise çelişki analizi
│   ├── conflict_prompts.py      Persona + JSON şeması + user prompt builder (çelişki için)
│   ├── gap_analyzer.py          ❌ STUB — analyze() NotImplementedError fırlatır
│   ├── gap_prompts.py           ✅ Hazır promptlar (gap_analyzer henüz kullanmıyor)
│   ├── improver.py              ❌ STUB — improve() NotImplementedError fırlatır
│   ├── analysis_report_parsing.py  LLM JSON → AnalysisReport.conflicts/gaps dict normalizer
│   ├── llm_response_utils.py    extract_json_object() — markdown fence'leri vs. tolere eder
│   └── logging_utils.py         get_module_logger("ad") + log_with_context() — Loguru wrapper
│
├── outputs/                     Layer 3 — Döküman Üretimi (Üye 3: Halise)
│   ├── __init__.py              SRSGenerator, StoryGenerator, BacklogGenerator, BDDGenerator export
│   ├── srs_generator.py         ⚠ Statik PDF (her zaman aynı şablon, dinamik değil) + Windows font yolu hardcoded
│   ├── story_generator.py       ❌ STUB
│   ├── backlog_generator.py     ❌ STUB
│   ├── bdd_generator.py         ❌ STUB
│   ├── logo_generator.py        Pillow ile logo PNG üretici (CLI script)
│   ├── logo.png                 Üretilmiş logo (SRS PDF header'ında kullanılır)
│   ├── srs_taslak.pdf           Önceden üretilmiş statik şablon
│   └── generated/               Runtime PDF'leri (gitignore'lı, şu an boş)
│
├── ui/                          Layer 4 — Streamlit Bileşenleri (Üye 4: Agid)
│   ├── __init__.py              (boş — şahsi import'lar dosyalara bırakılmış)
│   ├── dashboard.py             Giriş ekranı: text_area + Demo butonu + Analiz butonu + sidebar
│   ├── results.py               Sekmeli sonuç paneli: Gereksinimler / Çelişkiler+Eksiklikler / İyileştirmeler / İndirme
│   └── components.py            req_card(), priority_badge(), download_button() yardımcı bileşenleri
│
├── tests/                       Pytest test takımı (Üye 4: Agid)
│   ├── conftest.py              sys.path'a proje kökünü ekler
│   ├── test_core.py             ⚠ ÇOĞU STUB; bazıları YANLIŞ (NotImplementedError bekliyor ama fonksiyonlar artık IMPLEMENTED)
│   ├── test_modules.py          ⚠ Sadece test_gap_analyzer_not_implemented gerçek
│   └── test_outputs.py          ⚠ Tamamen TODO
│
├── data/
│   ├── samples/                 ⚠ BOŞ (README'de bahsedilen ornek_gereksinim.txt mevcut DEĞİL)
│   └── templates/               ⚠ BOŞ (README'de bahsedilen requirement_template.json mevcut DEĞİL)
│
└── docs/
    ├── AGENT_GUIDE.md           ★ Bu dosya — AI ajan öğreticisi (Türkçe)
    ├── CONTEXT.md               Mimari ve sözleşmeler (İngilizce, kısa)
    ├── FEATURES.md              Özellik listesi ve durum (İngilizce)
    ├── ROADMAP_AND_ISSUES.md    Sprint backlog ve issue takibi (Türkçe)
    ├── TEAM.md                  Ekip rolleri ve RACI (Türkçe)
    ├── CHECKPOINTS/             Marp slide deck'leri (sunum, Türkçe)
    │   ├── CHECKPOINT-1.md      Stratejik vizyon
    │   └── CHECKPOINT-2.md      Sprint 2 değerlendirmesi
    └── Makale/
        └── YGA.md               Akademik makale taslağı (Türkçe)
```

> **Eklenen yıldız (★)** = "Bu dosyayı önce oku" anlamına gelir.

---

## 3. Veri Modelleri — `core/models.py` (Sözleşme Boundary)

Bu üç dataclass **modüller arası ortak dildir**. Hiçbir modül kendi formatını dayatamaz; herhangi birinde değişiklik yapan kişi **PR'da tüm üyelerin onayını** almalıdır.

### 3.1 `Requirement`

| Alan | Tip | Açıklama |
|---|---|---|
| `id` | `str` | `"REQ_001"`, `"REQ_002"` (sıfır dolgulu üç haneli) |
| `text` | `str` | Cümlenin orijinal hali |
| `req_type` | `str` | `"FUNCTIONAL"` \| `"NON_FUNCTIONAL"` \| `"UNKNOWN"` (varsayılan) |
| `actors` | `List[str]` | NER ile bulunan aktör lemmaları (`["kullanıcı", "sistem"]`) |
| `objects` | `List[str]` | NER ile bulunan nesne lemmaları (`["şifre", "form"]`) |
| `priority` | `Optional[str]` | `"HIGH"` \| `"MEDIUM"` \| `"LOW"` \| `None` |
| `original_text` | `str` | Boş string varsayılan; preprocessor şu an doldurmuyor |
| `tokens` | `List[str]` | Stopword'siz, küçük harfli kelimeler |
| `lemmas` | `List[str]` | Kelimelerin kökleri |
| `pos_tags` | `List[str]` | UPOS etiketleri |
| `source_index` | `int` | Metin içindeki cümle sıra numarası (0-tabanlı) |

### 3.2 `ParsedDocument`

| Alan | Tip | Açıklama |
|---|---|---|
| `raw_text` | `str` | Kullanıcının girdiği orijinal metin |
| `requirements` | `List[Requirement]` | Cümle başına bir Requirement |
| `language` | `str` | `"tr"` (sabit, tek dil destekleniyor) |
| `total_sentences` | `int` | Stanza'nın bulduğu cümle sayısı |
| `created_at` | `str` | ISO 8601 timestamp (otomatik üretilir) |

### 3.3 `AnalysisReport`

| Alan | Tip | Açıklama |
|---|---|---|
| `parsed_doc` | `ParsedDocument` | Üst kademe DTO (içinde requirement'lar) |
| `conflicts` | `List[dict]` | Her dict en az `req_ids`, `conflict_type`, `reason` içerir |
| `gaps` | `List[dict]` | Her dict en az `missing_area`, `suggestion`, `severity` içerir |
| `improvements` | `List[dict]` | Her dict en az `original`, `improved`, `reason` içerir |

> 🚨 **Mutable default tuzağı:** Tüm liste alanları `field(default_factory=list)` kullanır. Asla `= []` yazma — Python listeleri referans paylaşır ve tüm `Requirement`'lar aynı listeye yazar. Bu kural projedeki **#1 hata kaynağıdır**.

### 3.4 Conflict dict şeması (LLM normalize edilmiş)

```python
{
  "req_ids": ["REQ_001", "REQ_003"],          # zorunlu
  "conflict_type": "logic",                   # zorunlu (logic|business_rule|performance|security|usability|other)
  "reason": "Kısa özet\n\nDetaylı açıklama",  # zorunlu (short_summary + detailed_explanation birleşik)
  "id": "C1",                                  # opsiyonel
  "severity": "high",                          # opsiyonel
  "suggested_resolution": "...",               # opsiyonel
}
```

### 3.5 Gap dict şeması (LLM normalize edilmiş)

```python
{
  "missing_area": "Şifre sıfırlama akışı",   # zorunlu
  "suggestion": "Şu cümle eklenebilir: ...", # zorunlu
  "severity": "high|medium|low",             # zorunlu (default: medium)
  "id": "G1",                                # opsiyonel
  "scenario": "authentication",              # opsiyonel
  "related_standard_step": "...",            # opsiyonel
  "rationale": "...",                        # opsiyonel
}
```

---

## 4. Modül Modül Detaylı Açıklama

### 4.1 `app.py` — Orchestrator

**Görevi:** Streamlit girişi + NLP pipeline'ı belleğe yükleme + `process_text()` orchestration.

**İçerdiği fonksiyonlar:**
- `load_nlp_pipeline()` — `@st.cache_resource` ile dekoratörlüdür. Stanza modellerini RAM'e **bir kez** yükler. `{"preprocessor", "classifier", "ner"}` dict döner.
- `process_text(raw_text: str) -> AnalysisReport` — Pipeline'ı çalıştırır:
  1. `preprocessor.process(raw_text)` → `ParsedDocument`
  2. Her requirement için `classifier.classify(req)` ve `ner.recognize(req)` (in-place değiştirir)
  3. Boş `conflicts/gaps/improvements` ile `AnalysisReport` döner

**UI akışı:**
- `render_dashboard()` çağrılır → `(user_text, analyze_clicked)` döner
- "Analiz Et" tıklanırsa: `time.sleep(2)` (yapay gecikme — kaldırılabilir) + spinner + `process_text` çağrılır
- Sonuç `st.session_state.analysis_report`'a yazılır → `render_results(report)` ile gösterilir

**🚨 Eksiklikler (modeller bunu bilmeli):**
1. `ConflictDetector`, `GapAnalyzer`, `RequirementImprover` **hiç çağrılmaz**. Bağlamak için Sprint 3'e bakılır.
2. `time.sleep(2)` debug amaçlı bırakılmış olabilir — production'da silinmeli.
3. SRS PDF üretimi `outputs/generated/`'a hiç yazılmıyor. UI o klasörden okuyor → "PDF bulunamadı" uyarısı verir.

---

### 4.2 `core/preprocessor.py` — `TextPreprocessor`

**Yaptığı:** Ham metin → `ParsedDocument(requirements=[Requirement, ...])`

**Adımlar:**
1. `re.sub(r"\s+", " ", raw_text).strip()` — fazla boşluk temizliği
2. Boş metinde sadece `ParsedDocument(raw_text=raw_text)` döner (asla crash etmez)
3. `stanza.Pipeline("tr", processors="tokenize,pos,lemma")` ile cümlelere böler
4. Her cümleye `REQ_NNN` id'si verir
5. Her kelime için: stopword + PUNCT değilse → `tokens`, `lemmas`, `pos_tags`'e ekler

**Bağımlılıklar:**
- Stanza **Türkçe modeli** — manuel: `python -c "import stanza; stanza.download('tr')"` (~150 MB)
- NLTK **stopwords** korpusu — ilk çağırışta otomatik indirilir

**Tuzaklar:**
- `print("Stanza indiriliyor...")` ve `print("Stanza indirildi.")` satırları **production kodda kalmış**. Loguru'ya çevrilmeli.
- Constructor'da Stanza yüklenir; bu nedenle `@st.cache_resource` kritiktir, yoksa her UI etkileşiminde model yeniden yüklenir.

---

### 4.3 `core/classifier.py` — `RequirementClassifier`

**Yaptığı:** `Requirement.req_type` alanını `"FUNCTIONAL"` veya `"NON_FUNCTIONAL"` olarak doldurur.

**Algoritma:** Saf heuristic — `requirement.text.lower()` içinde aşağıdaki **NFR keyword listesinden** herhangi biri geçerse `NON_FUNCTIONAL`, aksi halde `FUNCTIONAL`.

**NFR keyword'leri:** `hızlı, saniye, performans, güvenli, şifre, kripto, ssl, yetki, ölçek, kesintisiz, ulaşılabilir, uptime, erişilebilir, kullanıcı, dostu, arayüz, responsive, gecikme, milisaniye, korunmalı, yedek, uyumluluk, standart, kapasite, mili saniye, kullanılabilirlik, güvenlik`

**🚨 Bilinen yanlış-pozitif:** `"kullanıcı"` ve `"şifre"` kelimeleri NFR sayılır → "Kullanıcı giriş yapabilmeli" cümlesi yanlışlıkla NFR olur. Bu ML modeline geçirildiğinde düzelecek (Backlog 3.5 Pydantic + scikit-learn).

**Genişletme noktası:** Yeni NFR kelimeleri sadece `nfr_keywords` listesine eklenir. Test eklemek için `tests/test_core.py::TestRequirementClassifier`.

---

### 4.4 `core/ner.py` — `EntityRecognizer`

**Yaptığı:** `Requirement.actors` ve `Requirement.objects` listelerini doldurur.

**Algoritma:**
1. Stanza `tr` pipeline'ını yükler (`tokenize,mwt,pos,lemma,ner`)
2. Her kelimenin **lemmasına** bakar, sözlüklerle karşılaştırır:
   - **Actor lemmaları:** `{kullanıcı, sistem, yönetici, admin, müşteri, ziyaretçi, cihaz, uygulama, istemci}`
   - **Object lemmaları:** `{şifre, form, e-posta, eposta, sepet, hesap, rapor, buton, sayfa, ekran, veri, veritabanı, dosya, belge, mesaj, bildirim, fatura, şifremi unuttum, link}`
3. **Set kullanır** (duplicate eleme), sonunda `list()`'e çevirir
4. **Fallback:** Stanza yüklenemezse (`self.nlp = None`) düz `text.lower() in` substring matching kullanır → asla crash etmez (Graceful Degradation)

**Tuzaklar:**
- Stanza pipeline'ı hem `TextPreprocessor`'da hem `EntityRecognizer`'da **ayrı ayrı** instantiate edilir → bellek 2x kullanılır. İleride tek pipeline'a indirgenebilir.
- `logger = logging.getLogger(__name__)` kullanır — projedeki diğer modüller Loguru kullanıyor, bu **istisna**dır.

---

### 4.5 `modules/llm_client.py` — `LLMClient` (Merkezi Facade)

**Görevi:** Google Gemini SDK'sını (`google-generativeai`) tek bir interface arkasına saklar. Tüm LLM çağrıları buradan geçer.

**Constructor parametreleri ve varsayılanları:**

| Parametre | Varsayılan | Kaynak |
|---|---|---|
| `provider` | `"gemini"` | (sadece bu destekleniyor) |
| `model_name` | `gemini-3.0-flash` | `GEMINI_MODEL_NAME` env veya parametre |
| `api_key` | — (zorunlu) | `GEMINI_API_KEY` env veya parametre |
| `max_output_tokens` | `2048` | parametre |
| `temperature` | `0.2` | parametre (düşük = deterministik) |

**Hata politikası:** 
- API key yoksa → `LLMClientError` (init'te)
- Provider gemini değilse → `ValueError`
- `google-generativeai` paketi kurulu değilse → `LLMClientError` (lazy import sırasında)
- Çağrı sırasında her hata → `LLMClientError` ile sarmalanır

**Ana metod:**
```python
client.chat(system_prompt: str, user_prompt: str, *, metadata=None, history=None) -> LLMResponse
```

`LLMResponse(content: str, raw: dict)` döner. **Diğer modüller `raw` alanına asla bağımlı olmamalıdır** — sadece debug/log için.

**Bağımlılık:** `google-generativeai` paketi `requirements.txt` içinde tanımlıdır → `pip install -r requirements.txt` yeterlidir. Eğer paket eksikse `LLMClient.__init__` net bir `LLMClientError` fırlatır.

---

### 4.6 `modules/conflict_detector.py` — `ConflictDetector` ✅

**Görevi:** "Hangi gereksinimler birbiriyle çelişiyor?" sorusunu LLM'e sorar.

**Sınıflar:**
- `ConflictDetector(llm_client: Optional[LLMClient] = None)` — LLM istemcisi DI ile enjekte edilebilir (test için kritik).
- `PairwiseConflictAnalysis(conflicts, meta, raw_llm)` — tam dönüş tipi (dataclass).

**Public metodlar (3 tane, hepsi aynı işi yapar farklı return tipleriyle):**
- `analyze_pairwise(doc) -> PairwiseConflictAnalysis` — tam sonuç (meta dahil)
- `analyze(doc) -> list[dict]` — sadece çelişki listesi (geriye uyumlu)
- `detect(doc) -> list[dict]` — `analyze()`'ın alias'ı (geriye uyumlu)

**İç akış:**
1. Boş `doc.requirements` → erken dönüş, boş sonuç
2. `_format_requirements_block()` → `- [REQ_001] (FUNCTIONAL) ...` formatında metin
3. `build_pairwise_conflict_user_prompt(block, n)` → user prompt
4. `build_conflict_detection_system_prompt()` → system prompt (persona + JSON şeması)
5. `LLMClient.chat()` → ham metin
6. `extract_json_object(text)` → dict (markdown fence'leri tolere eder)
7. `conflicts_payload_to_report_dicts(payload)` → `AnalysisReport.conflicts` formatına normalize eder
8. `meta.total_requirements` her zaman gerçek sayı ile **override edilir** (LLM yanlış sayarsa korunmak için)

**🚨 Hata davranışı:** LLM JSON döndüremezse `LLMClientError` fırlatır → `app.py`'da yakalanmıyor → tüm UI çöker. ROADMAP Issue #6'da uyarılan sorun. Çözüm: `try/except LLMClientError → conflicts=[]` ile değiştirilebilir.

---

### 4.7 `modules/conflict_prompts.py`

**İki sabit:**
- `CORE_CONFLICT_ANALYZER_PERSONA` — "Sen, AutoReq aracı için çalışan uzman bir Gereksinim Çelişki Analizörü'sün..."
- `CONFLICT_DETECTION_SYSTEM_PROMPT` — Görev tanımı + JSON şeması (yukarıdaki Conflict dict şeması ile birebir uyumlu)

**İki fonksiyon:**
- `build_conflict_detection_system_prompt() -> str` — yukarıdaki ikisini `\n\n` ile birleştirir
- `build_pairwise_conflict_user_prompt(requirements_block: str, requirement_count: int) -> str` — gereksinim bloğunu ve sayısını gömer

**Prompt tasarım kuralı:** LLM'den gelen JSON şu yapıyı izler (model bunu **birebir** üretmek zorundadır):

```json
{
  "conflicts": [{"id": "C1", "severity": "high", "type": "logic", "requirements": ["REQ_001", "REQ_003"], "short_summary": "...", "detailed_explanation": "...", "suggested_resolution": "..."}],
  "meta": {"total_requirements": 0, "total_conflicts": 0, "confidence": "high"}
}
```

`analysis_report_parsing.conflicts_payload_to_report_dicts()` bu yapıyı `AnalysisReport.conflicts` formatına çevirir.

---

### 4.8 `modules/gap_analyzer.py` ❌ STUB + `modules/gap_prompts.py` ✅

**Durum:** `GapAnalyzer.analyze(doc)` her zaman `NotImplementedError("GapAnalyzer.analyze() henüz implemente edilmedi.")` fırlatır.

**Promptlar hazır:** `build_gap_analysis_system_prompt()` ve `build_gap_analysis_user_prompt(block, n, *, domain_hint=None)` kullanıma hazır. Sadece `gap_analyzer.py` içinde `ConflictDetector`'ın yaptığı 7-adımlık akışı tekrarlamak gerekiyor:

1. Boş doc → boş dönüş
2. `_format_requirements_block(doc)`
3. `build_gap_analysis_user_prompt(...)` + `build_gap_analysis_system_prompt()`
4. `LLMClient().chat(...)`
5. `extract_json_object(response.content)`
6. `gaps_payload_to_report_dicts(payload)` → `AnalysisReport.gaps` listesi
7. Dönüş

**Referans senaryolar (prompt içinde):** authentication, authorization, account, data_privacy, security_ux, notifications, other.

---

### 4.9 `modules/improver.py` ❌ STUB

`RequirementImprover.improve(requirement)` → `NotImplementedError`. Henüz prompt katmanı bile yazılmamış. Future work.

---

### 4.10 `modules/analysis_report_parsing.py`

**Tüm LLM JSON normalize işlemleri burada.** Şu fonksiyonlar:

| Fonksiyon | Girdi | Çıktı |
|---|---|---|
| `conflicts_payload_to_report_dicts(data)` | LLM JSON dict | `list[dict]` (AnalysisReport sözleşmesi) |
| `gaps_payload_to_report_dicts(data)` | LLM JSON dict | `list[dict]` |
| `parse_conflicts_llm_text(text)` | Ham LLM string | `list[dict]` |
| `parse_gaps_llm_text(text)` | Ham LLM string | `list[dict]` |
| `build_analysis_report_from_llm(parsed_doc, *, conflicts_llm_text=, gaps_llm_text=, conflicts_payload=, gaps_payload=)` | Karışık | Dolu `AnalysisReport` |

**Tasarım ilkesi:** LLM çıktısı bozuksa **default değerler** kullanılır. `severity` `{high, medium, low}` dışındaysa `medium`'a normalize edilir. Eksik alanlar `"-"` veya `"(Açıklama yok.)"` olur.

---

### 4.11 `modules/llm_response_utils.py`

Tek fonksiyon: `extract_json_object(text: str) -> dict[str, Any]`.

1. Önce `json.loads(text.strip())` dener
2. Başarısız olursa metindeki ilk `{` ile son `}` arasını kesip dener
3. Yine olmazsa `ValueError("LLM çıktısından geçerli JSON ayrıştırılamadı.")`

**Neden gerekli?** Gemini bazen ` ```json ... ``` ` markdown fence'leriyle veya açıklayıcı metin ekleyerek döner. Bu fonksiyon her ikisini de tolere eder.

---

### 4.12 `modules/logging_utils.py`

Loguru wrapper'ı:
- `get_module_logger("conflict_detector")` → `logger.bind(module="conflict_detector")` döner
- `log_with_context(module, level, message, *, request_id=None, **extra)` → ek context bağlama

**Konvansiyon:** Tüm `modules/` dosyaları `_log = get_module_logger("modul_adı")` pattern'ini kullanır. `core/ner.py` istisnadır (stdlib `logging` kullanır — ileride uyumlulaştırılmalı).

---

### 4.13 `outputs/srs_generator.py` ⚠ Statik

**Şu anki durum:** `SRSGenerator(FPDF)` sınıfı + `generate_srs()` fonksiyonu. CLI olarak çalışır:
```bash
python outputs/srs_generator.py
```

**Ürettiği:** `outputs/srs_taslak.pdf` (her seferinde aynı içerik, 10 başlık + "Bu bölüm otomatik analiz sonuçlarıyla doldurulacaktır." placeholder)

**🚨 Bilinen sorunlar:**
1. **Hardcoded Windows font yolu:** `C:\Windows\Fonts\arial.ttf`. Linux/macOS'ta düşer → Helvetica fallback (Türkçe karakter bozulur).
2. **Dinamik veri YOK:** `AnalysisReport`'tan veri almıyor. ROADMAP Issue #7 bu görevi listeliyor.
3. **`outputs/generated/`'a yazmıyor:** `outputs/srs_taslak.pdf`'e yazıyor. UI ise `outputs/generated/*.pdf` arıyor → her zaman "bulunamadı" uyarısı.
4. `os.startfile(output_path)` Windows'a özgüdür, Linux/macOS'ta sessizce başarısız olur.

---

### 4.14 `outputs/{story,backlog,bdd}_generator.py` ❌ Hepsi Stub

Sınıflar (`StoryGenerator`, `BacklogGenerator`, `BDDGenerator`) ve `generate(report)` metotları var; hepsi `NotImplementedError` fırlatır.

---

### 4.15 `outputs/logo_generator.py`

CLI script. Pillow ile `outputs/logo.png` üretir. SRS PDF header'ında kullanılır. Tek seferlik üretim için tutuluyor.

---

### 4.16 `ui/dashboard.py` — Giriş Ekranı

`render_dashboard() -> (user_text, analyze_clicked)`:
- Başlık + sidebar + Demo butonu (sabit demo metni yükler) + Analiz Et butonu + text_area
- `st.session_state.user_input` ve `st.session_state.analysis_report` keys'lerini başlatır
- **Demo metni:** "Kullanıcı sisteme kayıt olabilmeli.\nŞifresini sıfırlayabilmeli.\nAdmin kullanıcıları yönetebilmeli."

---

### 4.17 `ui/results.py` — Sonuç Paneli

`render_results(report)`:
- 4 sekme: **Gereksinimler** / **Çelişkiler & Eksiklikler** / **İyileştirme Önerileri** / **İndirilebilir Çıktılar**
- Çelişkiler, eksiklikler, iyileştirmeler boşsa "bulunamadı" uyarısı
- Dict/non-dict items'ı tolere eder (tip kontrolüyle)
- PDF indirme: `outputs/generated/*.pdf` glob'lar, ilkini sunar

**🚨 İnce hata:** `_safe_get(req_dict, "type", "FUNCTIONAL")` yazılmış ama Requirement'ın alan adı `req_type`. Bu yüzden tüm gereksinimler UI'da `FUNCTIONAL` olarak gözükür (default fallback). Doğrusu `_safe_get(req_dict, "req_type", "UNKNOWN")` olmalı.

---

### 4.18 `ui/components.py` — Yeniden Kullanılabilir Bileşenler

- `req_card(req_id, text, req_type)` — yeşil/mavi ikon + ID + tür + metin kart
- `priority_badge(priority)` — kırmızı/sarı/yeşil emoji rozet
- `download_button(label, data, filename, mime)` — `st.download_button` wrapper'ı

---

## 5. Çevre Değişkenleri & Kurulum

### 5.1 `.env` dosyası

```env
GEMINI_API_KEY=your_key_here          # ZORUNLU (LLM özellikleri için)
GEMINI_MODEL_NAME=gemini-3.0-flash    # OPSİYONEL (varsayılan)
```

**Anahtar nereden alınır?** [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

**Hangi özellikler API key OLMADAN çalışır?**
- ✅ Preprocessor, Classifier, NER, UI dashboard, statik SRS PDF
- ❌ ConflictDetector (init'te `LLMClientError` fırlatır)

### 5.2 Kurulum (yeniden çıkartılabilir)

```bash
# 1) Repo
git clone https://github.com/AutoReq-DevTeam/AutoReq.git
cd AutoReq

# 2) Sanal ortam
python -m venv venv
venv\Scripts\activate           # Windows
# source venv/bin/activate      # Linux / macOS

# 3) Bağımlılıklar
pip install -r requirements.txt    # google-generativeai dahil

# 4) Stanza Türkçe modeli (~150 MB, bir kerelik)
python -c "import stanza; stanza.download('tr')"

# 5) .env oluştur
copy .env.example .env          # Windows
# cp .env.example .env          # Linux / macOS
# .env içine GEMINI_API_KEY yapıştır

# 6) Çalıştır
streamlit run app.py            # http://localhost:8501
```

### 5.3 Test çalıştırma

```bash
pytest tests/ -v
pytest tests/ -v --cov=core --cov=modules --cov=outputs
```

**🚨 Bilinen test failure'ları (`main` dalında):**
- `test_classifier_raises_not_implemented` — fonksiyon artık IMPLEMENT edilmiş, test güncel değil → FAIL
- `test_ner_raises_not_implemented` — aynı sebep → FAIL
- Bu testler ROADMAP Issue #8'de "revize edilecek" olarak işaretli.

---

## 6. Kodlama Konvansiyonları

### 6.1 İsimlendirme

| Eleman | Konvansiyon | Örnek |
|---|---|---|
| Modül dosyası | `snake_case.py` | `conflict_detector.py` |
| Sınıf | `PascalCase` | `RequirementClassifier` |
| Fonksiyon / metod | `snake_case` | `process_text()` |
| Sabit | `UPPER_SNAKE_CASE` | `CORE_CONFLICT_ANALYZER_PERSONA` |
| Dataclass alanı | `snake_case` | `req_type`, `source_index` |
| Private metod | `_leading_underscore` | `_chat_gemini`, `_run_pairwise_llm_analysis` |
| Requirement ID | `REQ_NNN` (3-haneli, 0-padded) | `REQ_001`, `REQ_042` |

### 6.2 Docstring & type hint

- **Her** public fonksiyon/sınıf docstring almalı (TR veya EN, modülün diline uygun)
- Tüm fonksiyon imzaları **type hint'li** olmalı (parametre + dönüş)
- Dataclass'larda **mutable default** = `field(default_factory=list)` (asla `= []`)

### 6.3 Hata yönetimi

| Senaryo | Pattern |
|---|---|
| Henüz implement edilmemiş özellik | `raise NotImplementedError("ModulName.method() henüz ...")` |
| LLM hatası | `LLMClientError(RuntimeError)` — yakala + context ile yeniden fırlat |
| Eksik API key | Init'te `LLMClientError` (kurulum talimatlı) |
| Eksik NLP modeli | `logger.warning()` + `self.nlp = None` + fallback path |
| LLM JSON parse hatası | `ValueError` → `LLMClientError`'a sarmala |
| Boş input | Boş DTO döndür (`ParsedDocument(raw_text=...)`) — asla crash etme |

### 6.4 Logging

- **Modüller (`modules/`):** Loguru via `get_module_logger("ad")`
- **`core/ner.py`:** stdlib `logging` (istisna — ileride uyumlulaştırılacak)
- **Asla `print()`** — `core/preprocessor.py`'deki "Stanza indiriliyor..." print'leri TODO

### 6.5 Git akışı

```
Dallar:    main → develop → feature/uye[n]-aciklama
Commits:   feat: | fix: | docs: | test: | prompt:
PR:        En az 1 reviewer onayı
```

### 6.6 Klasör sahipliği

| Klasör | Sahip | Üye |
|---|---|---|
| `core/` + `app.py` | NLP & Preprocessing | Üye 1 — Galip Efe Öncü |
| `modules/` | Akıllı Analiz | Üye 2 — Eren Eyyüpkoca |
| `outputs/` | Döküman Üretimi | Üye 3 — Halise İncir |
| `ui/` + `tests/` | UI & Test | Üye 4 — Agid Gülsever |
| `core/models.py` | **Paylaşılan** — 4 üyenin onayı şart | — |

---

## 7. Modüller Arası İş Akışı (Bir Özelliği Eklerken Yapılacaklar)

### 7.1 Yeni bir NLP özelliği (örn. yeni NFR keyword)

1. `core/classifier.py` → `nfr_keywords` listesine ekle
2. `tests/test_core.py::TestRequirementClassifier::test_non_functional_classification` → assertion ekle
3. PR aç → Üye 1 onayı yeterli

### 7.2 Yeni bir LLM analizi (örn. priority detector)

1. `modules/priority_prompts.py` oluştur — `CORE_*_PERSONA` + `*_SYSTEM_PROMPT` + `build_*_user_prompt()`
2. `modules/priority_detector.py` oluştur — `ConflictDetector` template'ini takip et:
   - `__init__(self, llm_client: Optional[LLMClient] = None)` — DI
   - `_get_client()`, `_format_requirements_block()`, `_run_*()` private helpers
   - Public: `analyze(doc) -> list[dict]`
3. `modules/analysis_report_parsing.py` → yeni `*_payload_to_report_dicts()` ekle
4. `core/models.py::AnalysisReport` → yeni alan **(gerekiyorsa)** — tüm üyelerin onayı
5. `app.py::process_text()` → analizi çağır
6. `ui/results.py` → yeni sekme veya bölüm
7. `tests/test_modules.py` → mock-based test

### 7.3 Yeni bir döküman çıktısı (örn. JSON export)

1. `outputs/json_exporter.py` oluştur — `JSONExporter.generate(report) -> Path`
2. Çıktıyı `outputs/generated/`'a yaz (gitignore'da)
3. `outputs/__init__.py` → export ekle
4. `ui/results.py::with tab4` → yeni download_button
5. `tests/test_outputs.py` → format testi

---

## 8. Tuzaklar & Dikkat Edilmesi Gerekenler (Priority Liste)

| # | Konu | Detay |
|---|---|---|
| 1 | **Mutable default** | Dataclass'larda `= []` yazma. Her zaman `field(default_factory=list)`. |
| 2 | **ConflictDetector app.py'a bağlı değil** | UI'da Çelişkiler sekmesi her zaman boş. `process_text()`'i güncelle. |
| 3 | **`req_type` vs `type` UI bug'ı** | `ui/results.py:_safe_get(req_dict, "type", ...)` → `"req_type"` olmalı. |
| 4 | **SRS dinamik değil** | `outputs/srs_generator.py` her seferinde aynı statik PDF üretir. |
| 5 | **SRS yanlış klasöre yazıyor** | `outputs/srs_taslak.pdf` üretiliyor; UI `outputs/generated/*.pdf` bekliyor. |
| 6 | **Windows font hardcoding** | `C:\Windows\Fonts\arial.ttf` → cross-platform değil. Türkçe karakter bozulur. |
| 7 | **Stanza model 2x yükleniyor** | `TextPreprocessor` ve `EntityRecognizer` ayrı pipeline yükler. Bellek 2x. |
| 8 | **`time.sleep(2)` `app.py`'da** | Yapay gecikme. Production'da silinmeli. |
| 9 | **Test stubları yanlış** | `test_*_raises_not_implemented` testleri artık güncel değil → FAIL. |
| 10 | **Logging hibrit kullanım** | Loguru/stdlib logging karışımı (`core/ner.py` istisna). |
| 11 | **`data/samples/` ve `data/templates/` boş** | Eski README'de bahsedilen dosyalar mevcut değil. |
| 12 | **Türkçe-only** | Tüm prompt'lar, NLP, UI Türkçe. İngilizce desteği için ayrı sprint gerekir. |
| 13 | **LLM hatası UI'yı çökertir** | `LLMClientError` `app.py`'da yakalanmıyor. |
| 14 | **Classifier yanlış-pozitif** | "kullanıcı" ve "şifre" NFR sayılır → çoğu fonksiyonel cümle yanlış sınıflanır. |

---

## 9. Hızlı "Nereye Bakmalıyım?" Tablosu

| Soru | Cevap |
|---|---|
| Yeni Requirement alanı eklemek istiyorum | `core/models.py::Requirement` |
| Yeni NFR kelimesi eklemek istiyorum | `core/classifier.py::nfr_keywords` |
| Yeni aktör/nesne eklemek istiyorum | `core/ner.py::actor_lemmas` veya `object_lemmas` |
| LLM modelini değiştirmek istiyorum | `.env` → `GEMINI_MODEL_NAME` |
| Yeni LLM provider eklemek istiyorum | `modules/llm_client.py::__init__` + yeni `_chat_*()` |
| Conflict prompt'unu iyileştirmek istiyorum | `modules/conflict_prompts.py` |
| Gap analyzer'ı tamamlamak istiyorum | `modules/gap_analyzer.py` (`ConflictDetector` template'i) |
| UI'a yeni sekme eklemek istiyorum | `ui/results.py::st.tabs(...)` |
| SRS PDF'ini dinamikleştirmek istiyorum | `outputs/srs_generator.py::generate_srs()` |
| Pipeline'a yeni adım eklemek istiyorum | `app.py::process_text()` |
| Yeni test eklemek istiyorum | `tests/test_{core,modules,outputs}.py` |

---

## 10. Önerilen Sonraki Görevler (Priority Order, Düşük Modeller İçin İdeal)

1. **🟢 Kolay — `app.py` entegrasyonu:** `process_text()` içinde `ConflictDetector().analyze(doc)` çağrısını `try/except LLMClientError` ile sarmalı, `report.conflicts` doldur.
2. **🟢 Kolay — UI bug'ı:** `ui/results.py:_safe_get(req_dict, "type", ...)` → `"req_type"` (tek satır değişikliği).
3. **🟢 Kolay — Test düzeltmeleri:** `tests/test_core.py::test_classifier_raises_not_implemented` ve `test_ner_raises_not_implemented` testlerini gerçek davranışa göre yeniden yaz.
4. **🟡 Orta — `GapAnalyzer`:** `ConflictDetector` şablonunu birebir kopyala, `gap_prompts`'ı kullan.
5. **🟡 Orta — `print()` → Loguru:** `core/preprocessor.py` ve `outputs/srs_generator.py`'deki tüm `print()` çağrılarını `_log.info()` ile değiştir.
6. **🟡 Orta — SRS dinamikleştirme:** `outputs/srs_generator.py::generate_srs()` → `generate_srs(report: AnalysisReport, output_path: Optional[Path] = None)` imzasına çevir, başlık placeholder'larını gerçek veriyle doldur, `outputs/generated/`'a yaz.
7. **🟠 Zor — Cross-platform font:** `srs_generator.py` font logic'ini OS'a göre ayır (Windows: arial, Linux: DejaVuSans, macOS: HelveticaNeue).
8. **🟠 Zor — `RequirementImprover`:** Few-shot prompting ile muğlak cümleleri ölçülebilir hale çevir.
9. **🔴 Çok Zor — ML classifier:** `scikit-learn` ile gerçek FR/NFR sınıflandırıcısı (Türkçe annotated dataset gerekir).

---

## 11. Diğer Dökümanlarla İlişki

| Dosya | Ne için okurum? |
|---|---|
| `README.md` | Proje tanıtımı, kurulum, kullanım (genel kitle) |
| `docs/CONTEXT.md` | Mimari özet (geliştirici, İngilizce) |
| `docs/FEATURES.md` | Özellik durumu (Definition of Done) |
| `docs/TEAM.md` | Kim ne yapıyor (RACI matrisi) |
| `docs/ROADMAP_AND_ISSUES.md` | Sprint backlog, açık görevler |
| `docs/CHECKPOINTS/*.md` | Sunum slide'ları (Marp formatında) |
| `docs/Makale/YGA.md` | Akademik makale |
| **`docs/AGENT_GUIDE.md`** | **Bu dosya — AI ajanları için kapsamlı öğretici** |

---

## 12. Son Söz (Modeller İçin)

Bir özelliği değiştirmeden önce **bu sırayla** ilerlemeni öneririm:

1. Bu dosyada (AGENT_GUIDE.md) ilgili modülün bölümünü oku
2. `core/models.py`'a göz at — DTO sözleşmesini ihlal etmediğinden emin ol
3. Hedef dosyayı `Read` aracıyla aç
4. Değişikliği yap → ilgili test dosyasına assertion ekle
5. `pytest tests/test_<modul>.py -v` ile doğrula
6. Logging eklediysen Loguru kullan, NLP modülü değilse `print()` koyma

Bu projenin **#1 felsefesi**: *"Better software starts with better requirements."* Senin de **#1 felsefen**: *"Better code starts with better understanding."* Önce oku, sonra yaz.

— *AutoReq-DevTeam, 2026*
