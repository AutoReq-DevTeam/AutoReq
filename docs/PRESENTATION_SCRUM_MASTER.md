# AutoReq

## Üçüncü Sunum — Scrum Master Raporu

Otonom Yazılım Gereksinim Analizi ve SRS Üretim Sistemi

Sprint 1 – Sprint 5 Özeti ve Modelleme & Test Çıktıları

---

## Açılış ve Bağlam

İlk iki sunumda ekibi ve **AutoReq**'in problem tanımını paylaşmıştık: ham gereksinim metninden **ISO/IEC/IEEE 29148** uyumlu SRS belgesi, çelişki ve eksiklik analizi, Agile Backlog otonom üretmek.

Bugün önce sistemin **modelleme ve akış** tarafını, ardından **SRS taslağı, izlenebilirlik ve test planını** sunacağız. Son olarak ekibimiz Sprint 1'den 5'e kadar olan çıktılarını kısaca paylaşacak.

**Proje takvimi:** 6 sprint × 1 hafta — şu anda Sprint 5 sonu.

**Ekip:**
- Galip Efe Öncü — NLP / Çekirdek mimari
- Eren Eyyüpkoca — LLM modülleri
- Halise İncir — Çıktı modülleri
- Agid Gülsever — UI ve Test

---

## Use Case ve Senaryolar

**Birincil aktör:** İş Analisti

**Birincil akış:** Metni gir → Analiz et → SRS, Backlog ve BDD çıktılarını indir.

| Senaryo | Tip | Akış |
|---|---|---|
| 1 | Normal | Analist metni yapıştırır; pipeline sınıflandırma, NER ve LLM analizini çalıştırır; SRS PDF ve Backlog XLSX dosyaları üretilir. |
| 2 | İstisna | Yüklenen `.docx` dosyası bozuk; sistem kullanıcıya format uyarısı gösterir, oturum çökmez. |
| 3 | Hata | LLM API anahtarı eksik veya servis hatası; pipeline boş çelişki/eksiklik listesiyle devam eder, kullanıcı arayüzünde uyarı gösterilir. |

Her üç senaryo da Sprint 3 / Issue #9'un kabul kriterleriyle birebir kodlandı.

---

## Arayüz ve Pipeline Akışı

**Streamlit çoklu sayfa mimarisi (Sprint 5 / Issue #20 hedefi):** Girdi → Analiz → Sonuçlar → Export.

Yan panelde canlı sayaçlar: gereksinim sayısı, çelişki sayısı, eksiklik sayısı, oturum maliyeti.

**Pipeline sıra akışı:**

1. Kullanıcı metni `app.py` üzerinden yüklenir.
2. Preprocessor metni temizler ve cümlelere ayırır.
3. Classifier her cümleyi Fonksiyonel veya Fonksiyonel Olmayan olarak etiketler.
4. NER aktör ve nesne varlıklarını çıkarır.
5. PriorityDetector her gereksinime HIGH / MEDIUM / LOW önceliği atar.
6. LLM tabanlı modüller paralel çalışır: ConflictDetector, GapAnalyzer ve RequirementImprover.
7. Çıktı üreticileri devreye girer: SRSGenerator, BacklogGenerator ve BDDGenerator.
8. Tüm sonuçlar arayüze ve indirilebilir dosyalara yansıtılır.

---

## Veri ve Nesne Modeli

`core/models.py` dosyası Sprint 5 / Issue #17 ile **Pydantic v2**'ye taşındı. Üç temel varlık üzerinden veri akışı yönetilir:

| Varlık | Açıklama | Önemli Alanlar |
|---|---|---|
| Requirement | Tek bir gereksinim cümlesi. | id, metin, tür (FUNCTIONAL / NON_FUNCTIONAL / UNKNOWN), öncelik (HIGH / MEDIUM / LOW), aktörler, nesneler |
| ParsedDocument | Bir analiz oturumundaki tüm gereksinimler. | requirements listesi |
| AnalysisReport | Pipeline'ın tüm çıktısı. | parsed_doc, conflicts, gaps, improvements |

Pydantic v2 sayesinde geçersiz tür ve değer atamaları runtime'da değil, sınırda yakalanır; `validate_assignment` her atama için doğrulamayı tetikler.

---

## Kısıtlar ve Riskler

| Kategori | Kısıt |
|---|---|
| Zaman | 6 sprint × 1 hafta; sprint sonu burndown takibi. |
| Veri | Türkçe metin; ISO 29148 uyumu; çoklu dosya formatı (TXT, DOCX, PDF). |
| Etik ve gizlilik | API anahtarları `.env` içinde izole; depoya gönderim yasak (NFR-1). |
| Teknik | LLM rate-limit (retry + backoff, Issue #18); pipeline süresi 15 saniyenin altında (NFR-2, Issue #21); bellek tavanı 800 MB. |

**Aktif riskler:**
- Halise hattındaki çıktı modülleri (Issue #11, #15, #19) Sprint 6'ya devredildi.
- Agid hattındaki UI 2.0 ve görselleştirme (Issue #12, #16, #20) Sprint 6'ya devredildi.

---

## Problem ve Çözüm Akışı

**Problem:** Manuel SRS yazımı tutarsızlık, eksik gereksinim ve ölçülemeyen kalite kriterleri üretir.

**Çözüm:** AutoReq otonom analizi sonucunda standart SRS, önceliklendirilmiş Backlog ve BDD test senaryoları üretilir.

**Akış:** Manuel SRS yazımı → Tutarsızlık, eksik gereksinim ve ölçülemeyen NFR → AutoReq otonom analizi → Standart SRS, önceliklendirilmiş Backlog ve BDD senaryoları.

---

## SRS Taslağı

`outputs/srs_generator.py` modülü, **fpdf2** kütüphanesi üzerine kuruludur ve ISO/IEC/IEEE 29148 standardının on zorunlu bölümünü kapsar:

1. Introduction
2. Scope
3. Definitions
4. Use Case
5. Functional Requirements
6. Non-Functional Requirements
7. Interface Requirements
8. Data Model
9. Constraints
10. Verification

- Türkçe karakter desteği Sprint 1 / Issue #3'te tamamlandı.
- Dinamik üretim (`AnalysisReport` → PDF) Sprint 3 / Issue #11 kapsamında.
- Çıktı yolu: `outputs/generated/srs_{timestamp}.pdf`.

---

## İzlenebilirlik Matriksi

| User Story | Kod Modülü | Test |
|---|---|---|
| US1 — Veri modeli | `core/models.py` | `tests/test_core.py::TestModels` (10 test) |
| US5 — F/NFR sınıflandırma | `core/classifier.py` | `TestRequirementClassifier::test_non_functional_classification` |
| US5 — NER (aktör/nesne) | `core/ner.py` | `TestEntityRecognizer` |
| Sprint 4 — Önceliklendirme (#13) | `core/priority_detector.py` | `TestPriorityDetector` (3 senaryo) |
| US6 — Çelişki tespiti | `modules/conflict_detector.py` | `TestConflictDetector::test_detects_contradiction` |
| Sprint 3 — Eksiklik analizi (#10) | `modules/gap_analyzer.py` | `TestGapAnalyzer::test_detects_missing_password_reset` |
| Sprint 4 — Improver (#14) | `modules/improver.py` | `TestRequirementImprover::test_improves_vague_requirement` |
| Sprint 5 — LLM Cache (#18) | `modules/llm_cache.py` | `TestLLMClient::test_cache_hit` |
| US3, US7 — SRS PDF | `outputs/srs_generator.py` | `TestSRSGenerator` |
| US4, US8 — UI Dashboard | `ui/dashboard.py`, `ui/results.py` | manuel doğrulama + UI testleri |

---

## Test Planı

| Katman | Konum | Hedef |
|---|---|---|
| Birim test | `tests/test_core.py`, `tests/test_modules.py`, `tests/test_outputs.py` | Saf fonksiyonlar ve mock LLM |
| Entegrasyon | `tests/integration/test_e2e.py` (Sprint 6 / #21) | `process_text()` 15 saniyenin altında |
| Regresyon (prompt) | `tests/regression/` (Sprint 6 / #22) | 20 örnek üzerinde golden snapshot |
| Kabul (BDD) | `outputs/generated/scenarios.feature` (Sprint 4 / #15) | Her FR için en az bir başarılı + bir hata senaryosu |

**Şu anki durum:** `pytest tests/ -v` çıktısı 30 PASS / 1 FAIL (`test_cache_hit` ortam sorunu Sprint 6'da çözülecek).

**Sprint 6 hedefi:** toplam test kapsamı %70 ve üzeri.

---

## Sürüm Notları

| Sürüm | Tarih | Öne Çıkan Çıktılar |
|---|---|---|
| v0.1 | Sprint 1-2 sonu | Proje iskeleti, LLM client, statik SRS, F/NFR sınıflandırma, NER. |
| v0.2 | Sprint 3 sonu | Pipeline entegrasyonu, GapAnalyzer, hata toleransı. |
| v0.3 | Sprint 4 sonu | Loguru migrasyonu, PriorityDetector, RequirementImprover (few-shot). |
| v0.4 | Sprint 5 sonu | Pydantic v2, örnek veri seti, LLM cache ve maliyet takibi. |
| v0.5 | Sprint 6 (planlı) | Performans optimizasyonu, %70 test kapsamı, ISO 29148 uyum doğrulaması, demo. |

---

## Sprint 1 — Temel Altyapı

| Üye | Issue | Yapılan | Yapılmayan |
|---|---|---|---|
| Galip Efe | #1 — Mimari ve Preprocessor | `core/models.py` dataclass'ları, `core/preprocessor.py` (Stanza + TR stop-words), `requirements.txt`, `app.py::process_text()` iskeleti tamamlandı. | — |
| Eren | #2 — LLM Client | `modules/llm_client.py` (Gemini), `.env` ve `.env.example`, çelişki sistem promptları, temel logging tamamlandı. | — |
| Halise | #3 — SRS PDF iskeleti | `outputs/srs_generator.py` (fpdf2), ISO 29148 başlıkları, sayfa numaralandırma, Türkçe font desteği tamamlandı. | — |
| Agid | #4 — UI ve Test altyapısı | — | UI tabs, text_area, Demo butonu, ilk unit testler ve spinner Sprint 2 ve 3'e devredildi. |

**Değerlendirme:** Sprint 1'in dört issue'sundan üçü tamamlandı. Agid'in UI temel iskeleti Sprint 2'ye, testler Sprint 3 / Issue #12'ye taşındı.

---

## Sprint 2 — NLP Motoru

| Üye | Issue | Yapılan | Yapılmayan |
|---|---|---|---|
| Galip Efe | #5 — Classifier ve NER | `core/classifier.py` (kural + ML hibrit), `core/ner.py` (Stanza), `req.actors` ve `req.objects` doldurma tamamlandı. | — |
| Eren | #6 — Çelişki ve Gap promptları | `modules/conflict_detector.py::analyze()`, gap prompt mimarisi, `AnalysisReport.conflicts` parse edildi. | JSON parse hatası Sprint 3 / Issue #9'da çözüldü. `GapAnalyzer.analyze()` Sprint 3 / Issue #10'a kaydı. |
| Halise | #7 — User Story ve dinamik SRS | — | `outputs/story_generator.py`, dinamik SRS dolumu ve `app.py` PDF tetikleme Sprint 3 / Issue #11'e devredildi. |
| Agid | #8 — UI Sonuç ve Download | `ui/results.py` (tabs ve listing), `ui/components.py::req_card()`, `st.download_button` tamamlandı. | Çekirdek modül unit testleri "NotImplementedError" beklediği için fail; revizyon Sprint 3 / Issue #12'ye devredildi. |

**Değerlendirme:** Galip ve Agid sprintini kapattı. Eren büyük oranda tamamladı. Halise'nin Issue #7'si bütünüyle Sprint 3'e devredildi.

---

## Sprint 3 — Stabilizasyon ve Entegrasyon

| Üye | Issue | Yapılan | Yapılmayan |
|---|---|---|---|
| Galip Efe | #9 — Pipeline entegrasyonu | `process_text()` içinde ConflictDetector ve GapAnalyzer çağrıları, hata toleransı, paylaşılan `core/nlp_engine.py` (tek Stanza pipeline) tamamlandı. | — |
| Eren | #10 — GapAnalyzer | `gap_analyzer.py::analyze()` 7 adımlı akışla tamamlandı; DI için constructor parametresi, `domain_hint` desteği, mock'lu unit test eklendi. | — |
| Halise | #11 — Dinamik SRS PDF | — | `generate_srs(report)` imzası, `outputs/generated/` klasörü, OS-aware font yolu ve bölüm helper'ları Sprint 6'ya devredildi. |
| Agid | #12 — UI bug ve test modernizasyonu | — | `ui/results.py::_safe_get` fix, eski testlerin gerçek davranış testlerine çevrilmesi, sidebar API key uyarısı, mock fixture Sprint 6'ya devredildi. |

---

## Sprint 4 — Üretken Çıktılar

| Üye | Issue | Yapılan | Yapılmayan |
|---|---|---|---|
| Galip Efe | #13 — Loguru ve PriorityDetector | Tüm `print()` çağrıları Loguru'ya geçirildi; `core/priority_detector.py` (HIGH/MEDIUM/LOW kural seti) `app.py`'a entegre edildi; 3 senaryo testi yazıldı. | — |
| Eren | #14 — Improver | `modules/improver.py` ve `improver_prompts.py` (3 few-shot örnek), `vague_keywords` ön filtresi, mock'lu unit test PASS. | `app.py::process_text()` içine `improver.improve(req)` entegrasyonu Galip'e delege edildi. |
| Halise | #15 — Story ve BDD üreteçleri | — | `story_generator.py`, `bdd_generator.py`, DOCX export, `scenarios.feature` çıktısı Sprint 6'ya devredildi. |
| Agid | #16 — Çelişki ve Gap görselleştirme | — | `conflict_card`, `gap_card`, `improvement_diff_card`, severity rozetleri ve mock LLM testleri Sprint 6'ya devredildi. |

---

## Sprint 5 — Backlog, Veri ve UI 2.0

| Üye | Issue | Yapılan | Yapılmayan |
|---|---|---|---|
| Galip Efe | #17 — Pydantic ve örnek veri | `core/models.py` Pydantic v2 BaseModel migrasyonu, Literal kısıtları, `validate_assignment=True`, üç domain örneği (e-ticaret, bankacılık, eğitim), `requirement_template.json` (JSON Schema 2020-12), 10 yeni `TestModels` testi ve UI sample dropdown tamamlandı. | — |
| Eren | #18 — LLM cache ve maliyet | `modules/llm_cache.py` (sha256 key), 3 kez exponential backoff retry, `LLMResponse.usage_metadata` (token + maliyet), sidebar oturum maliyeti metric'i tamamlandı. | `test_cache_hit` ortam sorunu Sprint 6'da çözülecek. |
| Halise | #19 — Backlog ve çoklu format export | — | `BacklogGenerator` (priority scoring), XLSX/DOCX/JSON exporter ve dört download butonu Sprint 6'ya devredildi. |
| Agid | #20 — Çoklu sayfa UI | — | `st.navigation` dört sayfa, DOCX/PDF upload, sidebar canlı sayaçlar ve `ui/state.py` Sprint 6'ya devredildi. |

---

## Sprint 1 – 5 Genel Durum

| Sprint | Galip | Eren | Halise | Agid |
|---|---|---|---|---|
| Sprint 1 | Tamamlandı | Tamamlandı | Tamamlandı | Sprint 2 ve 3'e devredildi |
| Sprint 2 | Tamamlandı | Büyük oranda tamamlandı | Sprint 3'e devredildi | Tamamlandı (test revizyonu hariç) |
| Sprint 3 | Tamamlandı | Tamamlandı | Sprint 6'ya devredildi | Sprint 6'ya devredildi |
| Sprint 4 | Tamamlandı | Tamamlandı | Sprint 6'ya devredildi | Sprint 6'ya devredildi |
| Sprint 5 | Tamamlandı | Tamamlandı | Sprint 6'ya devredildi | Sprint 6'ya devredildi |

**Tamamlanan issue sayısı:** 11 / 20

- Galip Efe — 5/5
- Eren — 5/5
- Halise — 1/5
- Agid — 1/5

---

## Riskler ve Sprint 6 Önizlemesi

**Aktif riskler:**

1. **Halise hattı** — Dinamik SRS, Story/BDD, Backlog ve ISO 29148 doğrulama Sprint 6'da yoğunlaştı. Refactor ve ek geliştirici desteği planlandı.
2. **Agid hattı** — UI 2.0, görselleştirme, çoklu sayfa mimarisi ve bug bash aynı sprintte. Önceliklendirme: önce Issue #12 ve #16.
3. **`test_cache_hit`** — Eren tarafında ortam kaynaklı, Sprint 6'da `pytest-mock` ile çözülecek.

**Sprint 6 hedefleri:**

- Pipeline performansı 15 saniyenin altına (Galip)
- Prompt regresyon suite ve golden snapshot (Eren)
- Devir alınmış dört Halise issue'sunun kapatılması
- %70 test kapsamı, bug bash ve demo materyalleri (Agid)

---

## Kapanış

Sprint 1'den 5'e kadar AutoReq'in temel mimarisini, NLP motorunu, LLM analiz pipeline'ını, Pydantic doğrulamasını ve LLM cache ile maliyet takibini hayata geçirdik.

Halise ve Agid taraflarındaki çıktı ve UI işleri Sprint 6'da yoğunlaşmış olsa da, **çekirdek pipeline çalışır durumda** ve canlı demoya hazır.

Sprint 6 sonunda hocamıza ISO 29148 uyumlu SRS PDF, önceliklendirilmiş Backlog ve BDD senaryoları üreten **demo-ready** bir AutoReq sunacağız.

Sorularınızı bekliyoruz. Teşekkür ederiz.
