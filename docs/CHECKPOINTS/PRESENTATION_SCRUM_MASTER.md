# AutoReq

## Üçüncü Sunum — Scrum Master Raporu

Otonom Yazılım Gereksinim Analizi ve SRS Üretim Sistemi

Checkpoint-3 & Checkpoint-4 Değerlendirmesi · Sprint 3–5 Çıktıları

---

## Açılış ve Bağlam

İlk iki sunumda ekibi ve **AutoReq**'in problem tanımını paylaşmıştık: ham gereksinim metninden **ISO/IEC/IEEE 29148** uyumlu SRS belgesi, çelişki ve eksiklik analizi, Agile Backlog otonom üretmek.

Bugün önce **Checkpoint-3** (Modelleme ve Akış) konularını, ardından **Checkpoint-4** (SRS Taslağı, İzlenebilirlik ve Test Planı) konularını sunacağız. Son olarak ekibimiz Sprint 3'ten 5'e kadar olan çıktılarını kısaca paylaşacak.

**Proje takvimi:** 6 sprint × 1 hafta — şu anda Sprint 5 sonu.

**Ekip:**
- Galip Efe Öncü — NLP / Çekirdek mimari
- Eren Eyyüpkoca — LLM modülleri
- Halise İncir — Çıktı modülleri
- Agid Gülsever — UI ve Test

---

## CHECKPOINT-3: Use Case ve Senaryolar

**Birincil aktör:** İş Analisti

**Birincil akış:** Metni gir → Analiz et → SRS, Backlog ve BDD çıktılarını indir.

| Senaryo | Tip | Akış |
|---|---|---|
| 1 | Normal | Analist metni yapıştırır; pipeline sınıflandırma, NER ve LLM analizini çalıştırır; SRS PDF ve Backlog XLSX dosyaları üretilir. |
| 2 | İstisna | Yüklenen `.docx` dosyası bozuk; sistem kullanıcıya format uyarısı gösterir, oturum çökmez. |
| 3 | Hata | LLM API anahtarı eksik veya servis hatası; pipeline boş çelişki/eksiklik listesiyle devam eder, kullanıcı arayüzünde uyarı gösterilir. |

Her üç senaryo da Sprint 3 / Issue #9'un kabul kriterleriyle birebir kodlandı ve tamamlandı.

---

## CHECKPOINT-3: Arayüz ve Pipeline Akışı

**Streamlit çoklu sayfa mimarisi:** Girdi → Analiz → Sonuçlar → Export.

Yan panelde canlı sayaçlar: gereksinim sayısı, çelişki sayısı, eksiklik sayısı, oturum maliyeti.

**Pipeline sıra akışı:**

1. Kullanıcı metni `app.py` üzerinden yüklenir.
2. Preprocessor metni temizler ve cümlelere ayırır.
3. Classifier her cümleyi Fonksiyonel veya Fonksiyonel Olmayan olarak etiketler.
4. NER aktör ve nesne varlıklarını çıkarır.
5. PriorityDetector her gereksinime HIGH / MEDIUM / LOW önceliği atar.
6. LLM tabanlı modüller çalışır: ConflictDetector, GapAnalyzer ve RequirementImprover.
7. Çıktı üreticileri devreye girer: SRSGenerator, BacklogGenerator, StoryGenerator ve BDDGenerator.
8. Tüm sonuçlar arayüze ve indirilebilir dosyalara yansıtılır.

---

## CHECKPOINT-3: Veri ve Nesne Modeli

`core/models.py` dosyası Sprint 5 / Issue #17 ile **Pydantic v2**'ye taşındı. Üç temel varlık üzerinden veri akışı yönetilir:

| Varlık | Açıklama | Önemli Alanlar |
|---|---|---|
| Requirement | Tek bir gereksinim cümlesi. | id, metin, tür (FUNCTIONAL / NON_FUNCTIONAL / UNKNOWN), öncelik (HIGH / MEDIUM / LOW), aktörler, nesneler |
| ParsedDocument | Bir analiz oturumundaki tüm gereksinimler. | requirements listesi |
| AnalysisReport | Pipeline'ın tüm çıktısı. | parsed_doc, conflicts, gaps, improvements |

Pydantic v2 sayesinde geçersiz tür ve değer atamaları runtime'da değil, sınırda yakalanır; `validate_assignment` her atama için doğrulamayı tetikler.

---

## CHECKPOINT-3: Kısıtlar ve Riskler

| Kategori | Kısıt |
|---|---|
| Zaman | 6 sprint × 1 hafta; sprint sonu burndown takibi. |
| Veri | Türkçe metin; ISO 29148 uyumu; çoklu dosya formatı (TXT, DOCX, PDF). |
| Etik ve gizlilik | API anahtarları `.env` içinde izole; depoya gönderim yasak (NFR-1). |
| Teknik | LLM rate-limit (retry + backoff, Issue #18); pipeline süresi 15 saniyenin altında (NFR-2); bellek tavanı 800 MB. |

Sprint 3–5 boyunca daha önce ertelenen tüm issue'lar tamamlandı. Sprint 6'da performans optimizasyonu, %70 test kapsamı ve final demo hazırlığı hedeflenmektedir.

---

## CHECKPOINT-3: Problem → Çözüm Akışı

**Problem:** Manuel SRS yazımı tutarsızlık, eksik gereksinim ve ölçülemeyen kalite kriterleri üretir.

**Çözüm:** AutoReq otonom analizi sonucunda standart SRS, önceliklendirilmiş Backlog ve BDD test senaryoları üretilir.

**Akış:** Manuel SRS yazımı → Tutarsızlık, eksik gereksinim ve ölçülemeyen NFR → AutoReq otonom analizi → Standart SRS, önceliklendirilmiş Backlog ve BDD senaryoları.

---

## CHECKPOINT-4: SRS Taslağı

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
- Dinamik üretim (`AnalysisReport` → PDF) Sprint 3 / Issue #11 kapsamında tamamlandı.
- User Story (DOCX) ve BDD senaryoları (`.feature`) Sprint 4 / Issue #15 ile eklendi.
- Product Backlog (XLSX) ve çoklu format export Sprint 5 / Issue #19 ile tamamlandı.
- Çıktı yolu: `outputs/generated/srs_{timestamp}.pdf`.

---

## CHECKPOINT-4: İzlenebilirlik Matriksi

| User Story | Kod Modülü | Test |
|---|---|---|
| US1 — Veri modeli | `core/models.py` | `TestModels` (10 test) |
| US5 — F/NFR sınıflandırma | `core/classifier.py` | `TestRequirementClassifier` |
| US5 — NER (aktör/nesne) | `core/ner.py` | `TestEntityRecognizer` |
| Sprint 4 — Önceliklendirme (#13) | `core/priority_detector.py` | `TestPriorityDetector` (3 senaryo) |
| US6 — Çelişki tespiti | `modules/conflict_detector.py` | `TestConflictDetector` |
| Sprint 3 — Eksiklik analizi (#10) | `modules/gap_analyzer.py` | `TestGapAnalyzer` |
| Sprint 4 — Improver (#14) | `modules/improver.py` | `TestRequirementImprover` |
| Sprint 5 — LLM Cache (#18) | `modules/llm_cache.py` | `TestLLMClient::test_cache_hit` |
| US3, US7 — SRS PDF | `outputs/srs_generator.py` | `TestSRSGenerator` |
| Sprint 4 — Story + BDD (#15) | `outputs/story_generator.py`, `outputs/bdd_generator.py` | `TestStoryGenerator`, `TestBDDGenerator` |
| Sprint 5 — Backlog (#19) | `outputs/backlog_generator.py` | `TestBacklogGenerator` |
| US4, US8 — UI Dashboard | `ui/dashboard.py`, `ui/results.py` | UI doğrulamaları |

---

## CHECKPOINT-4: Test Planı

| Katman | Konum | Hedef |
|---|---|---|
| Birim test | `tests/test_core.py`, `tests/test_modules.py`, `tests/test_outputs.py` | Saf fonksiyonlar ve mock LLM |
| Entegrasyon | `tests/integration/test_e2e.py` (Sprint 6 / #21) | `process_text()` 15 saniyenin altında |
| Regresyon (prompt) | `tests/regression/` (Sprint 6 / #22) | 20 örnek üzerinde golden snapshot |
| Kabul (BDD) | `outputs/generated/scenarios.feature` (Sprint 4 / #15) | Her FR için en az bir başarılı + bir hata senaryosu |

**Şu anki durum:** Tüm birim testler PASS. Sprint 6'da entegrasyon ve regresyon testleri ile toplam %70+ kapsam hedeflenmektedir.

---

## CHECKPOINT-4: Sürüm Notları ve Değişiklik Yönetimi

| Sürüm | Tarih | Öne Çıkan Çıktılar |
|---|---|---|
| v0.1 | Sprint 1-2 sonu | Proje iskeleti, LLM client, statik SRS, F/NFR sınıflandırma, NER. |
| v0.2 | Sprint 3 sonu | Pipeline entegrasyonu, GapAnalyzer, hata toleransı, dinamik SRS PDF. |
| v0.3 | Sprint 4 sonu | Loguru migrasyonu, PriorityDetector, RequirementImprover, Story + BDD üreteçleri, çelişki/gap görselleştirme. |
| v0.4 | Sprint 5 sonu | Pydantic v2, örnek veri seti, LLM cache ve maliyet takibi, Backlog üreteci, çoklu format export, dosya yükleme, UI 2.0. |
| v0.5 | Sprint 6 (planlı) | Performans optimizasyonu, %70 test kapsamı, ISO 29148 uyum doğrulaması, demo. |

---

## Sprint 3 — Stabilizasyon ve Entegrasyon

| Üye | Issue | Yapılan |
|---|---|---|
| Galip Efe | #9 — Pipeline entegrasyonu | `process_text()` içinde ConflictDetector ve GapAnalyzer çağrıları, hata toleransı, paylaşılan `core/nlp_engine.py` (tek Stanza pipeline) tamamlandı. |
| Eren | #10 — GapAnalyzer | `gap_analyzer.py::analyze()` 7 adımlı akışla tamamlandı; DI için constructor parametresi, `domain_hint` desteği, mock'lu unit test eklendi. |
| Halise | #11 — Dinamik SRS PDF | `generate_srs(report)` imzası, `outputs/generated/` klasörü, OS-aware font yolu ve bölüm helper'ları tamamlandı. |
| Agid | #12 — UI bug ve test modernizasyonu | `ui/results.py::_safe_get` fix, eski testlerin gerçek davranış testlerine çevrilmesi, sidebar API key uyarısı, mock fixture tamamlandı. |

**Değerlendirme:** Sprint 3'ün dört issue'su da eksiksiz tamamlandı. ✅

---

## Sprint 4 — Üretken Çıktılar

| Üye | Issue | Yapılan |
|---|---|---|
| Galip Efe | #13 — Loguru ve PriorityDetector | Tüm `print()` çağrıları Loguru'ya geçirildi; `core/priority_detector.py` (HIGH/MEDIUM/LOW kural seti) `app.py`'a entegre edildi; 3 senaryo testi yazıldı. |
| Eren | #14 — Improver | `modules/improver.py` ve `improver_prompts.py` (3 few-shot örnek), `vague_keywords` ön filtresi, mock'lu unit test PASS. `app.py::process_text()` entegrasyonu tamamlandı. |
| Halise | #15 — Story ve BDD üreteçleri | `story_generator.py` ve `bdd_generator.py` tamamlandı; DOCX export ve `scenarios.feature` çıktısı üretime alındı. |
| Agid | #16 — Çelişki ve Gap görselleştirme | `conflict_card`, `gap_card`, `improvement_diff_card`, severity rozetleri ve mock LLM testleri tamamlandı. |

**Değerlendirme:** Sprint 4'ün dört issue'su da eksiksiz tamamlandı. ✅

---

## Sprint 5 — Backlog, Veri ve UI 2.0

| Üye | Issue | Yapılan |
|---|---|---|
| Galip Efe | #17 — Pydantic ve örnek veri | `core/models.py` Pydantic v2 BaseModel migrasyonu, Literal kısıtları, üç domain örneği, `requirement_template.json`, 10 yeni test ve UI sample dropdown tamamlandı. |
| Eren | #18 — LLM cache ve maliyet | `modules/llm_cache.py` (sha256 key), exponential backoff retry, `usage_metadata` (token + maliyet), sidebar oturum maliyeti metric'i tamamlandı. |
| Halise | #19 — Backlog ve çoklu format export | `BacklogGenerator` (priority scoring), XLSX/DOCX/JSON exporter ve dört download butonu tamamlandı. |
| Agid | #20 — Çoklu sayfa UI | Dosya yükleme (.txt/.docx/.pdf), `st.file_uploader`, sidebar canlı sayaçlar ve UI geliştirmeleri tamamlandı. |

**Değerlendirme:** Sprint 5'in dört issue'su da tamamlandı. ✅

---

## Sprint 1 – 5 Genel Durum

| Sprint | Galip | Eren | Halise | Agid |
|---|---|---|---|---|
| Sprint 1 | ✅ | ✅ | ✅ | ✅ |
| Sprint 2 | ✅ | ✅ | ✅ | ✅ |
| Sprint 3 | ✅ | ✅ | ✅ | ✅ |
| Sprint 4 | ✅ | ✅ | ✅ | ✅ |
| Sprint 5 | ✅ | ✅ | ✅ | ✅ |

**Tamamlanan issue sayısı:** 20 / 20

- Galip Efe — 5/5
- Eren — 5/5
- Halise — 5/5
- Agid — 5/5

---

## Sprint 6 Önizlemesi

Sprint 6 son sprint olup, ürünü demo-ready hale getirme odaklıdır:

| Üye | Issue | Hedef |
|---|---|---|
| Galip Efe | #21 | Pipeline performansı 15 saniyenin altına indirme, uçtan uca entegrasyon testleri. |
| Eren | #22 | Prompt regresyon suite, golden snapshot testleri ve LLM mock fixture kütüphanesi. |
| Halise | #23 | ISO/IEC/IEEE 29148 uyum doğrulaması, PDF kalite testleri, cross-platform font. |
| Agid | #24 | %70+ test kapsamı, bug bash, demo senaryoları ve sunum materyalleri. |

---

## Kapanış

Sprint 1'den 5'e kadar AutoReq'in **tüm modülleri** tamamlandı: NLP motoru, LLM analiz pipeline'ı, Pydantic v2 doğrulaması, LLM cache ve maliyet takibi, dinamik SRS PDF üretimi, User Story ve BDD üreteçleri, Product Backlog üreteci, çoklu format export ve dosya yükleme destekli UI.

Tüm ekip üyeleri sorumluluklarını eksiksiz yerine getirdi. **Çekirdek pipeline çalışır durumda** ve canlı demoya hazır.

Sprint 6 sonunda hocamıza ISO 29148 uyumlu SRS PDF, önceliklendirilmiş Backlog ve BDD senaryoları üreten **demo-ready** bir AutoReq sunacağız.

Sorularınızı bekliyoruz. Teşekkür ederiz.
