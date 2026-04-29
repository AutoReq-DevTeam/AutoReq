# AutoReq — Yazılım Gereksinim Spesifikasyonu (SRS)

| Alan | Değer |
|---|---|
| Doküman türü | Software Requirements Specification (SRS) |
| Standart | ISO/IEC/IEEE 29148:2018 |
| Sürüm | 0.4 |
| Tarih | 2026-04-26 |
| Hazırlayan | AutoReq Ekibi (Galip Efe Öncü, Eren Eyyüpkoca, Halise İncir, Agid Gülsever) |
| Durum | Sprint 5 sonu — Sprint 6 ile birlikte güncellenecek |

---

## 1. Giriş

### 1.1 Amaç

Bu doküman, **AutoReq** adlı yazılım gereksinim analizi sisteminin kapsamını, fonksiyonel ve fonksiyonel olmayan gereksinimlerini, kullanıcı rollerini, kısıtlarını ve doğrulama yaklaşımını tanımlar. Hedef kitle proje ekibi, danışman akademisyen ve değerlendirici jüri üyeleridir.

### 1.2 Kapsam

AutoReq, ham Türkçe gereksinim metnini girdi olarak alıp aşağıdaki çıktıları otonom üreten bir hibrit NLP + LLM sistemidir:

- ISO/IEC/IEEE 29148 uyumlu SRS PDF belgesi
- Önceliklendirilmiş Product Backlog (Excel)
- Agile User Story listesi (DOCX)
- BDD (Gherkin) test senaryoları (`.feature`)
- Çelişki, eksiklik ve muğlaklık analizi raporu

Sistem, paydaşlar arası iletişim hatalarından doğan zaman ve maliyet kaybını azaltmayı amaçlar.

### 1.3 Tanımlar ve Kısaltmalar

| Terim | Açıklama |
|---|---|
| SRS | Software Requirements Specification |
| FR | Functional Requirement (Fonksiyonel Gereksinim) |
| NFR | Non-Functional Requirement (Fonksiyonel Olmayan Gereksinim) |
| NER | Named Entity Recognition (Adlandırılmış Varlık Tanıma) |
| LLM | Large Language Model (Büyük Dil Modeli) |
| BDD | Behavior-Driven Development |
| DoD | Definition of Done |
| Pipeline | Metin girişinden çıktı üretimine kadarki uçtan uca işlem akışı |

### 1.4 Referanslar

- ISO/IEC/IEEE 29148:2018 — Systems and Software Engineering — Life Cycle Processes — Requirements Engineering
- Proje yol haritası: `docs/ROADMAP_AND_ISSUES.md`
- Mimari rehber: `docs/AGENT_GUIDE.md`
- Özellik takibi: `docs/FEATURES.md`

---

## 2. Genel Tanım

### 2.1 Ürün Perspektifi

AutoReq, tarayıcı üzerinden çalışan **Streamlit** tabanlı bağımsız bir web uygulamasıdır. Ana bileşenler:

- **Çekirdek NLP motoru** — Stanza Türkçe modeli ile cümle bölme, tokenizasyon, lemmatization, NER
- **Sınıflandırma katmanı** — Anahtar kelime + ML hibrit yaklaşımıyla F/NFR ayrımı
- **LLM analiz katmanı** — Google Gemini API üzerinden çelişki, eksiklik ve muğlaklık tespiti
- **Çıktı üretim katmanı** — fpdf2, openpyxl, python-docx tabanlı dosya üreticileri
- **Kullanıcı arayüzü** — Streamlit çoklu sayfa mimarisi

### 2.2 Kullanıcı Sınıfları

| Rol | Birincil Aksiyon |
|---|---|
| İş Analisti | Müşteri görüşme metnini sisteme girer, üretilen SRS'i indirir. |
| Kalite Mühendisi (QA) | Çelişki ve eksiklik raporlarını inceler, BDD senaryolarını test planına alır. |
| Proje Yöneticisi | Önceliklendirilmiş Backlog'u sprint planlamasında kullanır. |
| Yazılım Mimarı | NFR'leri ve gap analizini değerlendirir, mimari kararlar alır. |
| Paydaş / Müşteri | Üretilen SRS PDF'i inceler ve görüşlerinin doğru yansıdığını doğrular. |

### 2.3 İşletim Ortamı

- İşletim sistemi: Windows 10+, Linux (Ubuntu 22.04+), macOS 13+
- Python: 3.10+
- Tarayıcı: Chrome, Edge, Firefox güncel sürüm
- İnternet bağlantısı: LLM çağrıları için zorunlu
- Bellek: minimum 4 GB RAM (Stanza modeli sonrası), 800 MB altı pipeline ayak izi

### 2.4 Varsayımlar ve Bağımlılıklar

- Kullanıcı geçerli bir Google Gemini API anahtarına sahiptir.
- Girdi metni Türkçe ve UTF-8 kodlamasındadır.
- Stanza Türkçe modeli ilk çalıştırmada otomatik indirilir.
- LLM servisi 99% uptime ile erişilebilir kabul edilir; servis kesintilerinde sistem çelişki/eksiklik listelerini boş döndürerek devam eder.

---

## 3. Fonksiyonel Gereksinimler

| ID | Başlık | Açıklama | Öncelik |
|---|---|---|---|
| FR-01 | Metin Girişi | Sistem, kullanıcının bir metin alanına ham Türkçe gereksinim metni yapıştırmasına izin vermelidir. | HIGH |
| FR-02 | Dosya Yükleme | Sistem, `.txt`, `.docx` ve `.pdf` formatlarındaki dosyaları yükleyip metni otomatik çıkarmalıdır. | MEDIUM |
| FR-03 | Ön İşleme | Sistem, metni cümlelere ayırmalı, durma kelimelerini temizlemeli ve lemmatization uygulamalıdır. | HIGH |
| FR-04 | Gereksinim Sınıflandırma | Sistem, her cümleyi `FUNCTIONAL`, `NON_FUNCTIONAL` veya `UNKNOWN` olarak etiketlemelidir. | HIGH |
| FR-05 | Aktör ve Nesne Tespiti | Sistem, NER ile aktörleri (Kullanıcı, Yönetici…) ve nesneleri (şifre, sepet…) çıkarmalıdır. | HIGH |
| FR-06 | Önceliklendirme | Sistem, anahtar kelime analiziyle her gereksinime HIGH / MEDIUM / LOW önceliği atamalıdır. | MEDIUM |
| FR-07 | Çelişki Tespiti | Sistem, LLM kullanarak gereksinimler arası mantıksal çelişkileri yakalamalı ve raporlamalıdır. | HIGH |
| FR-08 | Eksiklik Analizi | Sistem, kimlik doğrulama, yetkilendirme, hata yönetimi gibi standart akışlarda eksiklikleri tespit etmelidir. | HIGH |
| FR-09 | Muğlaklık İyileştirme | Sistem, "hızlı olmalı" gibi ölçülemeyen ifadeleri ölçülebilir kriterlere dönüştürmelidir. | MEDIUM |
| FR-10 | SRS PDF Üretimi | Sistem, ISO/IEC/IEEE 29148'in 10 zorunlu bölümünü içeren bir SRS PDF üretmelidir. | HIGH |
| FR-11 | User Story Üretimi | Sistem, fonksiyonel gereksinimleri "As a … I want … so that …" formatına çevirmelidir. | MEDIUM |
| FR-12 | BDD Senaryosu Üretimi | Sistem, her FR için Gherkin formatında en az bir başarılı ve bir hata senaryosu üretmelidir. | MEDIUM |
| FR-13 | Product Backlog Üretimi | Sistem, gereksinimleri öncelik skoruyla sıralanmış bir Backlog'a dönüştürmelidir. | MEDIUM |
| FR-14 | Çoklu Format Export | Sistem, çıktıları PDF, XLSX, DOCX ve JSON formatlarında dışa aktarmalıdır. | MEDIUM |
| FR-15 | Sonuç Görselleştirme | Sistem, gereksinimleri, çelişkileri ve eksiklikleri arayüzde kart bileşenleriyle göstermelidir. | HIGH |
| FR-16 | Oturum Maliyet Takibi | Sistem, oturumda harcanan token ve tahmini maliyeti yan panelde göstermelidir. | LOW |

---

## 4. Fonksiyonel Olmayan Gereksinimler

| ID | Kategori | Gereksinim | Doğrulama Yöntemi |
|---|---|---|---|
| NFR-01 | Performans | Tek sayfalık metnin (≈100 cümle) tam analizi 15 saniyenin altında tamamlanmalıdır. | `tests/integration/test_e2e.py` zaman ölçümü |
| NFR-02 | Performans | NLP-only ön işleme 100 kelime için 1 saniyenin altında olmalıdır. | Birim test + cProfile |
| NFR-03 | Performans | Stanza modeli yalnızca bir kez yüklenmeli (`@st.cache_resource`), Streamlit yenilemelerinde tekrar yüklenmemelidir. | Manuel doğrulama + log incelemesi |
| NFR-04 | Bellek | Sistem ayak izi ilk Stanza yüklemesi sonrası 800 MB'ı aşmamalıdır. | `psutil` ölçümü, performance raporu |
| NFR-05 | Güvenlik | LLM API anahtarları yerel `.env` dosyasında izole edilmeli, depoya gönderilmemelidir. | `.gitignore` denetimi, kod incelemesi |
| NFR-06 | Güvenilirlik | LLM hatası, rate-limit veya API anahtarı eksikliği durumunda sistem çökmemeli; çelişki/eksiklik listesi boş olarak dönmeli ve kullanıcıya bilgilendirici uyarı gösterilmelidir. | Unit test (mock LLM hata yolları) |
| NFR-07 | Güvenilirlik | LLM çağrıları en az 3 kez exponential backoff (1s, 2s, 4s) ile yeniden denenmelidir. | `test_llm_retry` |
| NFR-08 | Maliyet | Aynı `(system_prompt + user_prompt)` çiftiyle yapılan ikinci çağrı API'ye gitmeden önbellekten dönmelidir. | `TestLLMClient::test_cache_hit` |
| NFR-09 | Kullanılabilirlik | Arayüz tek bir dashboard bütünlüğünde olmalı; analiz sırasında kullanıcıya yükleniyor göstergesi sunulmalıdır. | Manuel UX testi |
| NFR-10 | Yerelleştirme | Türkçe karakterler (ş, ğ, ı, İ, ö, ü, ç) tüm çıktılarda (PDF, DOCX, XLSX, UI) bozulmadan render edilmelidir. | `test_turkish_chars_render` |
| NFR-11 | Sürdürülebilirlik | Tüm üretim kodu Loguru logging kullanmalı; `print()` ifadelerine yer verilmemelidir. | Statik kod taraması |
| NFR-12 | Test Edilebilirlik | Toplam test kapsamı %70 ve üzerinde olmalı; `core/`, `modules/` ve `outputs/` modüllerinin her biri minimum %65 kapsamı sağlamalıdır. | `pytest --cov` raporu |
| NFR-13 | Standart Uyumu | Üretilen SRS PDF, ISO/IEC/IEEE 29148'in 10 zorunlu başlığını içermeli ve `pypdf` ile parse edildiğinde tüm başlıklar doğrulanabilmelidir. | `test_pdf_contains_all_iso_sections` |
| NFR-14 | Veri Doğrulama | Tüm veri modelleri Pydantic v2 doğrulamasından geçmeli; geçersiz değerler runtime'da değil sınırda yakalanmalıdır. | `TestModels` (10 test) |

---

## 5. Arayüz Gereksinimleri

### 5.1 Kullanıcı Arayüzü

Streamlit çoklu sayfa mimarisi (Sprint 5 / Issue #20):

1. **Girdi Sayfası** — Metin alanı, dosya yükleme alanı, örnek veri açılır listesi.
2. **Analiz Sayfası** — Pipeline ilerleme göstergesi, adım adım durum mesajları.
3. **Sonuçlar Sayfası** — Gereksinimler, çelişkiler, eksiklikler ve iyileştirmeler için sekmeler.
4. **Export Sayfası** — PDF, XLSX, DOCX ve JSON için indirme butonları.

Yan panel: API anahtarı durumu, gereksinim sayısı, çelişki sayısı, eksiklik sayısı, oturum maliyeti.

### 5.2 Yazılım Arayüzü

| Bileşen | Sürüm | Amaç |
|---|---|---|
| Stanza | ≥ 1.7 | Türkçe NLP pipeline (tokenize, POS, lemma, NER) |
| Google Gemini API | v1 | LLM çağrıları (çelişki, eksiklik, muğlaklık) |
| fpdf2 | ≥ 2.7 | SRS PDF üretimi |
| openpyxl | ≥ 3.1 | Backlog Excel export |
| python-docx | ≥ 1.1 | User Story DOCX export |
| Pydantic | ≥ 2.5 | Veri doğrulama |
| Streamlit | ≥ 1.32 | Web arayüzü |

### 5.3 İletişim Arayüzü

- LLM API çağrıları HTTPS üzerinden, JSON gövdeyle yapılır.
- Yerel önbellek `diskcache` üzerinden, 24 saat TTL ile çalışır.

---

## 6. Kısıtlar

| Tip | Kısıt |
|---|---|
| Zaman | Proje toplamda 6 sprint × 1 hafta sürede tamamlanacaktır. |
| Veri | Girdi metni Türkçe, UTF-8 kodlamalı olmalıdır. Çoklu dil desteği kapsam dışıdır. |
| Etik / Gizlilik | Müşteri metinleri yerel olarak işlenir; LLM çağrılarına gönderilen veriler API sağlayıcısının gizlilik politikasına tabidir. API anahtarları depoya gönderilemez. |
| Teknik | LLM rate-limit ve token maliyeti birincil teknik kısıtlardır. Sistem önbellek + retry stratejisiyle bu kısıtları yumuşatır. |
| Akademik | ISO/IEC/IEEE 29148:2018 standardı baz alınmalıdır. |

---

## 7. Doğrulama

### 7.1 Test Stratejisi

| Katman | Konum | Hedef |
|---|---|---|
| Birim test | `tests/test_core.py`, `tests/test_modules.py`, `tests/test_outputs.py` | Saf fonksiyonlar ve mock LLM yolları |
| Entegrasyon | `tests/integration/test_e2e.py` | `process_text()` 15 saniyenin altında tamamlanmalı |
| Regresyon (prompt) | `tests/regression/` | 20 örnek üzerinde golden snapshot |
| Kabul (BDD) | `outputs/generated/scenarios.feature` | Her FR için 1 başarılı + 1 hata senaryosu |

### 7.2 Definition of Done

Bir gereksinim aşağıdaki maddeler karşılandığında "Tamamlandı" sayılır:

- Kod `develop` dalına en az bir gözden geçirici onayıyla merge edilir.
- İlgili Issue'nun tüm kabul kriterleri karşılanır.
- En az bir geçerli birim test PASS verir.
- Mevcut testlerde regresyon yoktur.
- Özellik Streamlit arayüzü üzerinden erişilebilirdir.

### 7.3 İzlenebilirlik

| User Story | Modül | Test |
|---|---|---|
| US1 — Veri modeli | `core/models.py` | `TestModels` (10 test) |
| US5 — F/NFR ayrımı | `core/classifier.py` | `TestRequirementClassifier` |
| US5 — NER | `core/ner.py` | `TestEntityRecognizer` |
| Sprint 4 — Önceliklendirme | `core/priority_detector.py` | `TestPriorityDetector` |
| US6 — Çelişki | `modules/conflict_detector.py` | `TestConflictDetector` |
| Sprint 3 — Eksiklik | `modules/gap_analyzer.py` | `TestGapAnalyzer` |
| Sprint 4 — Improver | `modules/improver.py` | `TestRequirementImprover` |
| Sprint 5 — LLM Cache | `modules/llm_cache.py` | `TestLLMClient::test_cache_hit` |
| US3, US7 — SRS PDF | `outputs/srs_generator.py` | `TestSRSGenerator` |
| US4, US8 — Dashboard | `ui/dashboard.py`, `ui/results.py` | UI doğrulamaları |

---

## 8. Değişiklik Yönetimi

| Sürüm | Tarih | Değişiklik |
|---|---|---|
| v0.1 | Sprint 1-2 sonu | İskelet, LLM client, statik SRS, F/NFR sınıflandırma, NER. |
| v0.2 | Sprint 3 sonu | Pipeline entegrasyonu, GapAnalyzer, hata toleransı. |
| v0.3 | Sprint 4 sonu | Loguru migrasyonu, PriorityDetector, RequirementImprover (few-shot). |
| **v0.4** | **Sprint 5 sonu** | **Pydantic v2, örnek veri seti, LLM cache ve maliyet takibi.** |
| v0.5 | Sprint 6 (planlı) | Performans optimizasyonu, %70 test kapsamı, ISO 29148 uyum doğrulaması, demo. |

---

## 9. Onay

| Rol | İsim | Tarih |
|---|---|---|
| Scrum Master | — | 2026-04-26 |
| Çekirdek mimari sorumlusu | Galip Efe Öncü | 2026-04-26 |
| LLM modül sorumlusu | Eren Eyyüpkoca | 2026-04-26 |
| Çıktı modülü sorumlusu | Halise İncir | 2026-04-26 |
| UI ve test sorumlusu | Agid Gülsever | 2026-04-26 |
