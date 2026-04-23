# 🗺 AutoReq: 6 Haftalık Geliştirme Yol Haritası (Toplam 6 Sprint)

> 📌 Aktif kod tabanı, modül sözleşmeleri ve bilinen tuzakların kapsamlı dökümü için: [`AGENT_GUIDE.md`](./AGENT_GUIDE.md). Bu dosya sprint backlog'una odaklanır.

---

## 🎯 Proje Hedefleri ve Sprint Planlaması (Checkpoint-2 Planları)
**Toplam Süre:** Proje toplam **6 Sprint** (6 Hafta) içerisinde tamamlanacaktır.
Aşağıda, projenin Checkpoint-2 aşamasındaki genel hedefleri, Sprint 1 ve Sprint 2'nin detaylı anlatımı ve kabul kriterleri (ISO/IEC 29148 Standardı Referanslı) yer almaktadır.

### 🏁 İlk 2 Sprint Anlatımı ve Hedefleri

**Sprint 1 ve Sprint 2 Hedef Özeti:**
Metin sınıflandırma ve LLM tabanlı analiz motorlarının entegrasyonu; analiz sonuçlarının dinamik bir kullanıcı arayüzü ve dışa aktarılabilir PDF raporu ile sunulması.

**Beklenen Çıktı:** 
Sistem, ham metin girildiğinde otonom olarak aktörleri tespit etmeli, LLM aracılığıyla mantıksal çelişkileri bulmalı ve standartlara uygun bir Yazılım Gereksinim Spesifikasyonu (SRS) raporu üretebilmelidir.

#### 📦 Sprint 1 İş Listesi ve Kullanıcı Hikayeleri
| ID | Persona | Kullanıcı Hikayesi (User Story) | Değer / Gerekçe | Sorumlu |
|:---|:---|:---|:---|:---|
| **US1** | Yazılım Mimarı | Projenin modüler bir iskelete ve veri yapılarına sahip olmasını istiyorum. | Çakışmadan geliştirmeyi başlatır. | Galip |
| **US2** | Sistem Tasarımcısı | Merkezi bir LLM servisi üzerinden API talebi yapabilmeyi istiyorum. | Kod tekrarını ve karmaşayı önler. | Eren |
| **US3** | Dokümantasyon Uz. | ISO/IEC standartlarında PDF rapor iskeleti olmasını istiyorum. | Analiz çıktılarını standartlaştırır. | Halise |
| **US4** | Son Kullanıcı | Metinleri yapıştırıp analiz edebileceğim bir arayüz istiyorum. | Girdi ve izleme süreçlerini kolaylaştırır. | Agid |

#### 📦 Sprint 2 İş Listesi ve Kullanıcı Hikayeleri
| ID | Persona | Kullanıcı Hikayesi (User Story) | Değer / Gerekçe | Sorumlu |
|:---|:---|:---|:---|:---|
| **US5** | İş Analisti | Metnin F/NFR ayrımını yapmasını ve aktörleri çıkarmasını istiyorum. | Manuel gereksinim ayıklama işini sıfırlar. | Galip |
| **US6** | Kalite Uzmanı | Zıtlık ve çelişki yaratan gereksinimleri bulup uyarmasını istiyorum. | Hatalı mimari kod yazımını en başta önler. | Eren |
| **US7** | Proje Yöneticisi | Çıkarımların otonom "Agile User Story" çevrilmesini istiyorum. | Geliştiriciler için doğrudan sprint task'ı verir. | Halise |
| **US8** | Proje Paydaşı | Sonuçları UI sekmelerinde ve indirilebilir PDF halinde istiyorum. | Çıktılara şeffaf ve kurumsal ulaşım sağlar. | Agid |

### ✅ Kabul Kriterleri (Acceptance Criteria - AC)
*Bir User Story'nin "Bitti (Done)" sayılması için karşılanması gereken ölçülebilir koşullar.*
*   **US1 / US5 (Modeller & Sınıflandırma):** Algoritma "Sistem hızlı olmalı" cümlesini *NON_FUNCTIONAL* olarak etiketlemelidir. `Stanza` kütüphanesi harici dataset indirmeden çalışıp aktör isimlerini `req.actors` listesine atmalıdır.
*   **US2 / US6 (LLM İstekleri & Çelişki Tespiti):** `.env` dosyası üzerinden API Key okunmalı ve uzak LLM sunucusuna güvenle prompt atılabilmelidir. Mantıksal zıtlıklar, exception fırlatmadan JSON şeklinde parse edilerek `AnalysisReport` nesnesine eklenmelidir.
*   **US4 / US8 (Arayüz & PDF Çıktı):** Ekranda bilgilendirici spinner (yükleniyor) animasyonu olmalıdır. `st.download_button` butonundan inen UTF-8 destekli Türkçe karakterli PDF hatasız bir şekilde açılabilmelidir.

### 🛡️ Fonksiyonel Olmayan Gereksinimler (NFR)
1.  **Güvenlik:** LLM API anahtarları sıkı bir şekilde yerel `.env` dosyasında izole edilmeli ve versiyon kontrol sistemlerine kesinlikle push edilmemelidir.
2.  **Performans:** Standart tek sayfalık bir metnin tam blok analizi (NER, sınıflandırma ve LLM çelişki tespiti dahil) **15 saniyenin altında** tamamlanmalıdır.
3.  **Kullanılabilirlik:** Kullanıcı arayüzü tek bir dashboard bütünlüğünü korumalı ve işlem sırasında aktif süreç göstergeleri barındırmalıdır.

---

## 📅 Proje Planı Tanıtımı
Bu döküman, projenin 6 haftalık hızlandırılmış geliştirme planını ve üyelerin haftalık odak noktalarını içerir.

| Hafta | Odak Noktası | Ana Hedef | Durum |
| :--- | :--- | :--- | :--- |
| **Hafta 1** | **Temel Altyapı** | Proje iskeleti, LLM bağlantısı ve Streamlit ana giriş ekranı. | ✅ Tamamlandı |
| **Hafta 2** | **NLP Motoru** | Metinlerin F/NF olarak ayrılması ve Aktör/Nesne tespiti (NER). | ✅ Tamamlandı |
| **Hafta 3** | **Stabilizasyon & Entegrasyon** | Hazır LLM modüllerinin pipeline'a bağlanması, kritik UI hatalarının giderilmesi, Gap analizinin işler hale getirilmesi, dinamik SRS üretimi. | 🔧 Planlandı |
| **Hafta 4** | **Üretken Çıktılar** | User Story, BDD (Gherkin) ve Improvement (muğlak ifade iyileştirme) modüllerinin tamamlanması; çelişki/gap görselleştirme. | 📋 Planlandı |
| **Hafta 5** | **Backlog, Veri & UI 2.0** | Product Backlog üretici, çoklu format export (Excel/DOCX/JSON), dosya yükleme, Pydantic doğrulama, LLM önbellek. | 📋 Planlandı |
| **Hafta 6** | **Performans, Test & Demo** | Performans optimizasyonu (<15s), %70+ test coverage, prompt regresyon suite, ISO 29148 uyum kontrolü, Final Demo hazırlığı. | 📋 Planlandı |

---

# 🛠 1. Hafta (Sprint 1) Görev Listesi (Issues)

### 🔴 Issue #1: Proje Mimarisi ve Metin Ön İşleme
*   **Sorumlu:** **Galip Efe Öncü**
*   **Özet:** Projenin ana iskeletini ve veri akış modellerini kurmak.
*   **User Story:** Bir Yazılım Mimarı olarak, projenin modüler bir iskelete ve net veri yapılarına (dataclass) sahip olmasını istiyorum, böylece ekip arkadaşlarımla çakışmadan geliştirmeye başlayabiliriz.
*   **Kabul Kriterleri (AC):**
    - [x] `core/models.py` içindeki sınıflar veri tipleriyle tanımlanmalıdır.
    - [x] Ön işleme algoritması durma kelimelerini (stop words) başarıyla filtreleyebilmelidir.
*   **Görevler:**
    - [x] `requirements.txt` dosyasını `stanza`, `streamlit`, `langchain`, `python-dotenv` kütüphaneleriyle güncelle.
    - [x] `core/models.py` içinde `Requirement`, `ParsedDocument` ve `AnalysisReport` dataclass'larını finalize et.
    - [x] `core/preprocessor.py` içine Türkçe stop-words temizleme ve temel normalizasyon kodlarını yaz.
    - [x] `app.py` üzerinde modüllerin entegrasyonu için merkezi `process_text()` fonksiyonunu tanımla.

### 🟠 Issue #2: LLM Bağlantı Altyapısı ve Servis Katmanı
*   **Sorumlu:** **Eren Eyyüpkoca**
*   **Özet:** Sistemin LLM (OpenAI/Ollama) ile güvenli ve hızlı iletişim kurmasını sağlamak.
*   **User Story:** Bir Sistem Tasarımcısı olarak, tüm zeka modüllerinin merkezi bir LLM servisi (client) üzerinden API'ye güvenle talep yapabilmesini istiyorum, böylece bağlantıları her dosyada baştan yazmak zorunda kalmayız.
*   **Kabul Kriterleri (AC):**
    - [x] `.env` dosyası üzerinden API Key okunmalı ve GitHub'a sızdırılmamalıdır.
    - [x] Modül başarılı bir şekilde LLM'e prompt atabilmeli ve JSON/Dictionary formatında yanıt (response) alabilmelidir.
*   **Görevler:**
    - [x] **LLM Pazar Araştırması:** Mevcut en ucuz/ücretsiz (Groq, OpenRouter, Google Gemini vb.) ve en güçlü/hızlı LLM API sağlayıcısını belirle.
    - [x] `modules/llm_client.py` oluştur; LangChain veya doğrudan API kullanarak merkezi talep yapısını kur.
    - [x] `.env.example` dosyası oluştur ve API anahtarı yönetimini dökümante et.
    - [x] Çelişki tespiti için ilk sistem prompt'larını (System Messages) tasarla.
    - [x] Modüller için temel loglama (logging) yapısını kur.

### 🟡 Issue #3: SRS PDF Motoru ve Mühendislik Şablonu
*   **Sorumlu:** **Halise İncir**
*   **Özet:** Otomatik üretilecek dökümanların teknik altyapısını kurmak.
*   **User Story:** Bir Dokümantasyon Uzmanı olarak, sistemin ISO/IEC 29148 standartlarında boş da olsa hazır bir PDF rapor mimarisine sahip olmasını istiyorum, böylece analiz bittiğinde çıktı sorunsuz üretilebilsin.
*   **Kabul Kriterleri (AC):**
    - [x] `fpdf2` kütüphanesi kullanılarak deneme bir dosya üretilebilmeli ve PDF okuyucular tarafından açılabilmelidir.
    - [x] PDF dosyasında Türkçe font (Ş, ğ, İ vb.) hatası kesinlikle yaşanmamalıdır.
*   **Görevler:**
    - [x] `outputs/srs_generator.py` oluştur ve `fpdf2` kütüphanesi ile boş bir taslak üretmeyi test et.
    - [x] ISO/IEC/IEEE 29148 standardındaki 10 temel başlığı (Giriş, Kapsam, Fonksiyonel Gereksinimler vb.) koda dök.
    - [x] PDF çıktısı için kurumsal bir logo ve sayfa numaralandırma yapısı ekle.
    - [x] Türkçe karakterlerin (ş, ğ, ı, İ) PDF'de sorunsuz çıkması için font yükleme kodunu yaz.

### 🔵 Issue #4: UI Dashboard ve Test Altyapısı
*   **Sorumlu:** **Agid Gülsever**
*   **Özet:** Kullanıcının etkileşime gireceği arayüzü ve projenin test disiplinini kurmak.
*   **User Story:** Bir Son Kullanıcı olarak, tarayıcım üzerinden metinleri yapıştırabileceğim ve analizi anlık takip edebileceğim temiz bir arayüz (dashboard) istiyorum.
*   **Kabul Kriterleri (AC):**
    - [ ] Streamlit arayüzünde çoklu sekme (st.tabs) yapısı çalışır durumda olmalıdır.
    - [ ] Analiz ve bekleme süreci boyunca kullanıcıya oyalayıcı bir spinner (yükleniyor barı) gösterilmelidir.
*   **Görevler:**
    - [ ] `ui/dashboard.py` üzerinde `st.sidebar` ile proje durumunu ve `st.tabs` ile analiz sonuçlarını ayır.
    - [ ] Metin giriş alanı için `st.text_area` ve örnek gereksinim metinlerini içeren bir "Demo" butonu ekle.
    - [ ] `tests/test_core.py` ve `tests/test_modules.py` dosyalarını oluştur; ilk unit testleri yaz.
    - [ ] Analiz sırasında kullanıcıyı bilgilendiren dinamik bildirimler (toast/spinner) ekle.

---

# 🚀 2. Hafta (Sprint 2) Görev Listesi (Issues)

### 🔴 Issue #5: Sınıflandırma ve NER (Entity) Modüllerinin Kodlanması
*   **Sorumlu:** **Galip Efe Öncü**
*   **Özet:** Metinden aktör çıkaran ve cümleleri fonksiyonel/fonksiyonel olmayan olarak sınıflandıran mantığın tamamlanması.
*   **User Story:** Bir İş Analisti olarak, sistemin girdiğim cümleleri Fonksiyonel (F) ve Fonksiyonel Olmayan (NFR) olarak ayırmasını, ayrıca sistemdeki gizli aktörleri listelemesini istiyorum; böylece manuel ayıklama işim sıfırlansın.
*   **Kabul Kriterleri (AC):**
    - [x] Algoritma, hız/güvenlik gibi mimari istekleri "NON_FUNCTIONAL" olarak başarıyla etiketlemelidir.
    - [x] `Stanza` kütüphanesi harici veri seti (database) indirmeden çalışmalı ve aktör isimlerini `req.actors` dizisine hata atmadan eklemelidir.
*   **Görevler:**
    - [x] `core/classifier.py` içerisindeki `classify()` fonksiyonunu kural tabanlı (veya scikit-learn kullanarak) doldur; gereksinimleri `FUNCTIONAL`/`NON_FUNCTIONAL` yap.
    - [x] `core/ner.py` içerisinde `Stanza` NER kullanarak "Kullanıcı", "Sistem" gibi aktörleri bulup `req.actors` listesine ekle.
    - [x] Metindeki ana nesneleri (örn: şifre, form, e-posta) tespit edip `req.objects` listesine ekle.
    - [x] `app.py` içerisindeki `NotImplementedError` veren `classifier` ve `ner` geçişini sağlayan kod satırlarını aktif hale getir.

### 🟠 Issue #6: Çelişki ve Eksiklik Analiz Yapay Zeka (LLM) Motoru
*   **Sorumlu:** **Eren Eyyüpkoca**
*   **Özet:** LLM API kullanarak gereksinimler arası mantıksal hataları/eksikleri bulma altyapısını kurmak.
*   **User Story:** Bir Kalite Uzmanı (QA) olarak, sistemin gereksinimlerdeki kendi içinde zıtlık/çelişki yaratan maddeleri bulmasını istiyorum, böylece yazılım ekibi gereksiz ve çatışan kodlar yazıp maliyet oluşturmasın.
*   **Kabul Kriterleri (AC):**
    - [x] Zıt maddeler eklendiğinde LLM bunu başarıyla yakalayan bir analiz dönmelidir.
    - [ ] Analiz sonucu alınan String/JSON yapıları hata fırlatmadan (Exception atılmadan) `AnalysisReport` nesnesine bağlanmalıdır. (🚩 *Not: JSON hatalı döndüğünde sistem ValueError fırlatarak çöküyor. Hata yakalanıp boş `[]` dönecek şekilde revize edilmeli.*)
*   **Görevler:**
    - [x] `modules/conflict_detector.py` içindeki `analyze()` fonksiyonunda `LLMClient` sınıfını entegre et.
    - [x] Hazırladığın system prompt'ları kullanarak gereksinimleri LLM'e gönderip "Hangi gereksinimler birbiriyle çelişiyor?" analizini kur.
    - [x] `modules/gap_analyzer.py` için standart senaryolarda (giriş, yetkilendirme vs.) "eksik" olan adımları bulan prompt mimarisi kurgula. (🚩 *Not: Promptlar kurgulanmış ancak `GapAnalyzer.analyze()` metodunun içerisindeki NotImplementedError henüz silinip çalışır hale getirilmemiş, eklenecek.*)
    - [x] LLM'den dönen sonuçları parse et ve `AnalysisReport` nesnesinin `conflicts` ile `gaps` listelerine uygun bir dict yapısıyla ekle.

### 🟡 Issue #7: User Story Üreteci ve Dinamik SRS Çıktısı
*   **Sorumlu:** **Halise İncir**
*   **Özet:** "As a [role], I want..." hikayelerini üretmek ve SRS şablonunu dinamikleştirmek.
*   **User Story:** Bir Çevik Proje Yöneticisi (Product Owner) olarak, teknik gereksinimlerin "Agile User Story" formatına otonom çevirilmesini istiyorum, böylece bu kartları doğrudan geliştiricilerin sprint backlog'una atabileyim.
*   **Kabul Kriterleri (AC):**
    - [ ] Otonom çıktıların tamamı standart "As a [Actor], I want [Action] so that [Value]" İngilizce/Türkçe formatında olmalıdır.
    - [ ] Sistem, `AnalysisReport` üzerinden gelen canlı ve dinamik veriyi `fpdf2` sayfalarına yerleştirebilmelidir.
*   **Görevler:**
    - [ ] `outputs/story_generator.py` içine fonksiyonel gereksinimleri Agile User Story formatına çeviren kodları yaz (bunun için LLMClient'ı kullanabilirsin).
    - [ ] Geçen hafta oluşturduğun statik `srs_generator.py` fonksiyonunu, Üye 2'den dönen gerçek `AnalysisReport` verileriyle akıllıca dolduracak şekilde dinamikleştir.
    - [ ] `app.py` üzerinde analiz bittiğinde SRS PDF'inin arka planda oluşturulmasını sağlayan fonksiyon çağrısını yap.

### 🔵 Issue #8: Sonuçların Görselleştirilmesi ve Analiz Raporu Sekmeleri
*   **Sorumlu:** **Agid Gülsever**
*   **Özet:** Sistemden dönen tam teşekküllü analiz raporunun arayüzde profesyonelce sergilenmesi.
*   **User Story:** Bir Proje Paydaşı (Stakeholder) olarak, tüm karmaşık analiz datalarını UI üzerinde kartlar ve sekmelerle şıkça görebilmek, gerektiğinde bu raporu tek tuşla bilgisayarıma PDF olarak indirebilmek istiyorum.
*   **Kabul Kriterleri (AC):**
    - [x] Arayüzde çelişkiler, eksikler ve gereksinim listeleri arayüz tasarımını veya sütunları (columns) taşırmadan gösterilmelidir.
    - [x] `st.download_button` butonu kullanılarak tarayıcı üzerinden başarılı bir şekilde dosya indirme tetiklenmelidir.
    - [ ] `classifier.py` ve `ner.py` için oluşturulan çekirdek unit testler hatasız şekilde pass almalıdır. (🚩 *Not: Testler NotImplementedError beklediği için `main` dalında başarısız (Fail) olacaktır. Fonksiyonların gerçek çıktıları (örn: FUNCTIONAL dönmesi) test edilip pass alınması sağlanmalı.*)
*   **Görevler:**
    - [x] Düzene sokulan `ui/results.py` içerisindeki tab'ları, `report.conflicts` ve `report.gaps` verilerini dict içinden okuyup listeleyecek şekilde (for/while vb.) doldur.
    - [x] `ui/components.py` içinde `req_card()` adında bir bileşen fonksiyonu yarat ve gereksinimleri sıradan metin değil bu şık component'lerle ekrana bas.
    - [x] "İndirilebilir Çıktılar" sekmesine, `outputs` modülüyle oluşturulan PDF dosyası için indirme (`st.download_button`) butonu ekle.
    - [x] Core modüller (`classifier.py` ve `ner.py`) için en az birer tane mantıksal (assertion içeren) test yaz. (🚩 *Not: Testler yazılmış ancak eski duruma göre yazıldığı için revize edilmeleri gerekiyor.*)

---

# 🛠 3. Hafta (Sprint 3) Görev Listesi (Issues) — *Stabilizasyon & Entegrasyon*

> 🎯 **Sprint Hedefi:** Sprint 1-2'de hazırlanan tüm modüller (özellikle `ConflictDetector`) henüz `app.py` pipeline'ına bağlanmamıştır; UI'da çelişkiler sekmesi her zaman boş gelmektedir. Bu sprintin amacı, mevcut hazır parçaları **uçtan uca çalışır** hale getirmek, kritik UI hatalarını gidermek, eksik kalan `GapAnalyzer` modülünü tamamlamak ve SRS PDF üretimini gerçek analiz verisiyle dinamikleştirmektir.

### 🔴 Issue #9: LLM Modüllerinin Pipeline'a Entegrasyonu ve Hata Toleransı
*   **Sorumlu:** **Galip Efe Öncü**
*   **Özet:** `app.py` orkestrasyonunu LLM analiz modülleriyle birleştirip sistemi gerçekten "akıllı" yapmak.
*   **User Story:** Bir Yazılım Mimarı olarak, hazır olan `ConflictDetector` ve `GapAnalyzer` çıktılarının arayüze otomatik yansımasını ve bir LLM hatası oluşsa bile uygulamanın çökmemesini istiyorum, böylece son kullanıcı kesintisiz analiz deneyimi yaşasın.
*   **Kabul Kriterleri (AC):**
    - [x] `process_text()` fonksiyonu çağrıldığında `report.conflicts` ve `report.gaps` boş olmamalı (en az 2 maddeli demo metninde 0'dan büyük sonuç dönmeli).
    - [x] `GEMINI_API_KEY` tanımlı değilken bile uygulama çökmeden çalışmalı; UI'da bilgilendirici uyarı gözükmeli.
    - [x] `LLMClientError` veya `ValueError` fırlatılırsa pipeline `conflicts=[]` / `gaps=[]` ile devam etmeli, traceback UI'a yansımamalı.
    - [x] `app.py` içindeki `time.sleep(2)` kaldırılmalı; gerçek pipeline süresi spinner'da yansıtılmalı.
*   **Görevler:**
    - [x] `app.py::process_text()` içine `ConflictDetector().analyze(parsed_doc)` çağrısını ekle ve `AnalysisReport.conflicts`'e ata.
    - [x] Aynı şekilde `GapAnalyzer().analyze(parsed_doc)` çağrısını ekle (Issue #10 ile koordine).
    - [x] LLM çağrılarını `try/except (LLMClientError, ValueError)` ile sarmala; hata durumunda Loguru ile log at, boş liste dön.
    - [x] `time.sleep(2)` satırını sil; spinner mesajını "Stanza ile ön işleme yapılıyor..." → "LLM ile çelişki analizi..." gibi adım adım güncelle.
    - [x] `EntityRecognizer` ve `TextPreprocessor`'ın iki ayrı Stanza pipeline yüklemesi sorununu gider — tek bir paylaşılan pipeline (ör. `core/nlp_engine.py`) oluştur.
    - [x] `load_nlp_pipeline()` cache'inde bu paylaşılan pipeline'ı kullan.

### 🟠 Issue #10: GapAnalyzer Modülünün Tamamlanması ✅
*   **Sorumlu:** **Eren Eyyüpkoca**
*   **Özet:** Hazır olan `gap_prompts.py` altyapısını kullanarak `GapAnalyzer.analyze()` metodunun stub'tan kurtarılması.
*   **User Story:** Bir Kalite Uzmanı olarak, sistemin "Giriş var ama şifremi unuttum yok" gibi standart eksiklikleri otomatik raporlamasını istiyorum, böylece sprint planlamadan önce tüm kritik akışları kapatmış olalım.
*   **Kabul Kriterleri (AC):**
    - [x] `GapAnalyzer().analyze(doc)` artık `NotImplementedError` fırlatmamalı; `list[dict]` dönmeli.
    - [x] Dönen her dict, AGENT_GUIDE'da tanımlanan sözleşmeye uygun olmalı: `missing_area`, `suggestion`, `severity` zorunlu.
    - [x] Sadece "Kullanıcı giriş yapabilmeli" gibi tek gereksinim verilse bile en az 1 anlamlı eksiklik (parola sıfırlama, MFA vb.) önermeli.
    - [x] Mock LLM ile yazılmış unit test (`tests/test_modules.py::TestGapAnalyzer`) PASS olmalı.
*   **Görevler:**
    - [x] `modules/gap_analyzer.py` içine `ConflictDetector`'ın 7 adımlık akışını birebir uyarla:
        1. Boş `doc.requirements` → erken dönüş.
        2. `_format_requirements_block(doc)` (helper'ı paylaş veya tekrar yaz).
        3. `build_gap_analysis_user_prompt(...)` + `build_gap_analysis_system_prompt()`.
        4. `LLMClient().chat(...)`.
        5. `extract_json_object(response.content)`.
        6. `gaps_payload_to_report_dicts(payload)`.
        7. `list[dict]` dön.
    - [x] Constructor'a `llm_client: Optional[LLMClient] = None` ekle (DI için).
    - [x] `GapAnalyzer.analyze(doc, *, domain_hint: Optional[str] = None)` parametre desteği aç (gap_prompts opsiyonel hint kabul ediyor).
    - [x] `tests/test_modules.py::TestGapAnalyzer::test_detects_missing_password_reset` → mock LLM yanıtıyla gerçek assertion.
    - [x] Loguru ile başlangıç/bitiş loglarını ekle (`get_module_logger("gap_analyzer")`).

### 🟡 Issue #11: Dinamik SRS PDF Üretimi (AnalysisReport → PDF)
*   **Sorumlu:** **Halise İncir**
*   **Özet:** Statik SRS şablonunu, `AnalysisReport` verisini bölüm bölüm dolduran dinamik bir üretici haline getirmek.
*   **User Story:** Bir Dokümantasyon Uzmanı olarak, sistemin analiz ettiği gereksinimleri ve tespit ettiği çelişkileri otomatik olarak SRS PDF'inin ilgili bölümlerine yerleştirmesini istiyorum, böylece elle kopya-yapıştır işine gerek kalmasın.
*   **Kabul Kriterleri (AC):**
    - [ ] `generate_srs(report: AnalysisReport, output_path: Optional[Path] = None) -> Path` imzası kullanılmalı.
    - [ ] Üretilen PDF, `outputs/generated/srs_{timestamp}.pdf` formatında **`outputs/generated/`** klasörüne yazılmalı.
    - [ ] PDF'in "Fonksiyonel Gereksinimler" bölümü gerçek `req_type == "FUNCTIONAL"` olan maddeleri tablo halinde içermeli.
    - [ ] "Kalite Özellikleri" bölümü `NON_FUNCTIONAL` maddeleri içermeli.
    - [ ] Yeni bölüm "Tespit Edilen Çelişkiler" eklenmeli; `report.conflicts` boş değilse her madde gerekçesiyle yazılmalı.
    - [ ] Linux ve Windows üzerinde Türkçe karakterler (ş, ğ, İ, ı) bozulmadan render edilmeli.
*   **Görevler:**
    - [ ] `outputs/srs_generator.py::generate_srs()` imzasını `AnalysisReport` alacak şekilde güncelle (eski parametresiz çağrıyı geriye uyumlu tut).
    - [ ] Hardcoded `C:\Windows\Fonts\arial.ttf` yolunu OS-aware bir helper'a çıkar (`_resolve_turkish_font_path()`):
        - Windows → `arial.ttf`
        - Linux → `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf`
        - macOS → `/System/Library/Fonts/Supplemental/Arial.ttf`
        - Hiçbiri yoksa Helvetica fallback + log uyarı.
    - [ ] Her başlık (Giriş, Kapsam, …) için bölüm doldurucu (`_render_functional_section`, `_render_nfr_section`, `_render_conflicts_section`, `_render_actors_section`) helper'ları ekle.
    - [ ] `outputs/generated/` klasörünü gerekirse `Path.mkdir(parents=True, exist_ok=True)` ile otomatik oluştur.
    - [ ] `app.py` içine: analiz tamamlandığında `generate_srs(report)` çağrısını arka planda yap, dosya yolunu `st.session_state.srs_pdf_path`'e kaydet.

### 🔵 Issue #12: Kritik UI Hata Düzeltmeleri ve Test Modernizasyonu
*   **Sorumlu:** **Agid Gülsever**
*   **Özet:** Sonuç panelindeki sessiz veri okuma hatasını gidermek, eski (yanlış) testleri güncellemek ve gerçek davranışları doğrulayan testler yazmak.
*   **User Story:** Bir Son Kullanıcı olarak, ekrandaki gereksinim kartlarının doğru tür etiketini (FUNCTIONAL/NON_FUNCTIONAL) göstermesini ve `pytest tests/` çıktısının yeşil olmasını istiyorum, böylece sisteme güvenebileyim.
*   **Kabul Kriterleri (AC):**
    - [ ] `ui/results.py` içindeki gereksinim kartları artık her zaman "FUNCTIONAL" göstermemeli — gerçek `req_type` değeri yansımalı.
    - [ ] `pytest tests/ -v` komutu **tüm testler PASS** ile bitmeli (eski yanlış `raises_not_implemented` testleri dahil).
    - [ ] `tests/test_core.py::TestRequirementClassifier::test_non_functional_classification` gerçek assertion içermeli; "Sistem hızlı olmalı" → `NON_FUNCTIONAL` doğrulaması yapılmalı.
    - [ ] LLM API key eksikse UI sidebar'da "❌ API Key tanımsız" uyarısı görünmeli.
*   **Görevler:**
    - [ ] `ui/results.py:_safe_get(req_dict, "type", "FUNCTIONAL")` → `_safe_get(req_dict, "req_type", "UNKNOWN")` olarak düzelt.
    - [ ] `tests/test_core.py::test_classifier_raises_not_implemented` → gerçek davranış testine çevir: `classify(Requirement(text="Sistem hızlı olmalı"))` → `req_type == "NON_FUNCTIONAL"`.
    - [ ] `tests/test_core.py::test_ner_raises_not_implemented` → benzer şekilde gerçek assertion'a çevir: `recognize(Requirement(text="Kullanıcı şifresini değiştirmeli"))` → `actors` ve `objects` dolu olmalı.
    - [ ] `TestTextPreprocessor::test_empty_input` ve `test_tokenization` TODO'larını gerçek testlere çevir (boş string crash etmemeli, normal cümle tokenize olmalı).
    - [ ] `ui/dashboard.py::render_dashboard()` sidebar'da `os.getenv("GEMINI_API_KEY")` kontrolüyle dinamik durum göster (`✅ API Key OK` / `❌ API Key tanımsız`).
    - [ ] `tests/conftest.py` içine `pytest fixture` ekle: dummy `LLMClient` (mock chat metodu) — diğer üyelerin testlerinde kullanması için.

---

# 🚀 4. Hafta (Sprint 4) Görev Listesi (Issues) — *Üretken Çıktılar*

> 🎯 **Sprint Hedefi:** Çelişki/eksiklik analizi artık çalıştığına göre, sistemin değer üretme katmanını kapatmak: muğlak ifadelerin ölçülebilir kriterlere dönüştürülmesi (Improver), Agile User Story üretimi, BDD (Gherkin) test senaryoları ve UI'da bunların görselleştirilmesi.

### 🔴 Issue #13: Logging Standardizasyonu ve Önceliklendirme Motoru
*   **Sorumlu:** **Galip Efe Öncü**
*   **Özet:** Tüm core modüllerini Loguru'ya geçirmek ve gereksinimlere otomatik öncelik atayan bir mekanizma kurmak.
*   **User Story:** Bir Yazılım Mimarı olarak, projedeki tüm log çıktılarının tek tip (Loguru) olmasını ve gereksinimlerin kritiklik düzeyine göre HIGH/MEDIUM/LOW etiketlenmesini istiyorum, böylece geliştirme sürecinde hata izleme tutarlı olsun ve PM'ler önceliği görebilsin.
*   **Kabul Kriterleri (AC):**
    - [ ] `core/preprocessor.py` ve `outputs/srs_generator.py`'deki tüm `print()` çağrıları kalkmış olmalı.
    - [ ] `core/ner.py` artık stdlib `logging` yerine Loguru `get_module_logger("ner")` kullanmalı.
    - [ ] Her `Requirement.priority` alanı pipeline çıkışında `"HIGH"`, `"MEDIUM"` veya `"LOW"` ile dolu olmalı (None kalmamalı).
    - [ ] "Kritik" / "güvenlik" / "must" gibi kelimeler içeren cümleler `HIGH` olmalı; nötr cümleler `MEDIUM`; iyi-olur ifadeleri `LOW`.
*   **Görevler:**
    - [ ] `core/preprocessor.py` içindeki "Stanza indiriliyor..." ve "Stanza indirildi." print'lerini `_log.info()` ile değiştir.
    - [ ] `outputs/srs_generator.py` içindeki "[BAŞARILI] PDF oluşturuldu..." print'lerini Loguru'ya çevir.
    - [ ] `core/ner.py` başında `from .logging_utils import get_module_logger` (veya `modules/logging_utils.py`'tan) ile Loguru'ya geç.
    - [ ] `core/priority_detector.py` (yeni dosya) oluştur:
        - `PriorityDetector.detect(req: Requirement) -> Requirement` — `req.priority` alanını doldurur.
        - HIGH keywords: `kritik, mutlaka, asla, şart, güvenlik, mahremiyet, must, zorunlu`
        - LOW keywords: `tercihen, isteğe bağlı, ileride, opsiyonel, nice-to-have`
        - Diğerleri MEDIUM.
    - [ ] `app.py::process_text()` içine NER'den sonra `priority_detector.detect(req)` çağrısı ekle.
    - [ ] `core/__init__.py`'a `PriorityDetector` export'u ekle.
    - [ ] `tests/test_core.py::TestPriorityDetector` ile 3 senaryo testi yaz.

### 🟠 Issue #14: Muğlak Gereksinim İyileştirici (Improver) Modülü ✅
*   **Sorumlu:** **Eren Eyyüpkoca**
*   **Özet:** "Hızlı olmalı", "kolay olmalı" gibi ölçülemeyen ifadeleri LLM ile teknik, ölçülebilir kriterlere dönüştürmek.
*   **User Story:** Bir Yazılım Mimarı olarak, müşterinin "süper hızlı olsun" gibi muğlak ifadelerinin sistem tarafından "Sistem yanıt süresi 1000 eşzamanlı kullanıcıda 500ms altında olmalıdır" gibi ölçülebilir kriterlere otomatik çevrilmesini istiyorum, böylece geliştirme aşamasında belirsizlik kalmasın.
*   **Kabul Kriterleri (AC):**
    - [x] `RequirementImprover().improve(requirement)` artık `NotImplementedError` fırlatmamalı.
    - [x] Dönen dict şu sözleşmeye uymalı: `{"original": str, "improved": str, "reason": str}`.
    - [x] Sadece muğlak ifadeler (`vague_keyword_dictionary` ön kontrolünden geçenler) LLM'e gönderilmeli (token tasarrufu).
    - [x] "Sistem hızlı olmalı" → `improved` alanında bir sayısal eşik (ms/saniye) içermeli.
    - [x] Mock LLM'le yazılmış unit test PASS olmalı.
*   **Görevler:**
    - [x] `modules/improver_prompts.py` oluştur:
        - `CORE_IMPROVER_PERSONA` — "Sen, gereksinim ölçülebilirlik uzmanısın..."
        - `IMPROVEMENT_SYSTEM_PROMPT` — JSON şeması (`{"improved": ..., "reason": ...}`).
        - **Few-shot örnekler** ekle (en az 3 tane: hız, kullanılabilirlik, güvenlik).
        - `build_improvement_user_prompt(requirement_text)` builder'ı.
    - [x] `modules/improver.py` içinde:
        - `vague_keywords = {"hızlı", "kolay", "basit", "güvenli", "şık", "modern", "kullanışlı", "iyi", "kötü", "büyük", "küçük"}`
        - Ön filtre: gereksinim metninde bu kelimelerden biri yoksa LLM çağrısını atla, `original == improved` döndür.
    - [x] `LLMClient` enjeksiyonu için constructor parametresi ekle (test edilebilirlik).
    - [ ] `app.py::process_text()` içine her requirement için `improver.improve(req)` çağrısı ekle, `report.improvements`'e ata. (🚩 *Not: Issue #14 kapsamında uygulanmadı — `app.py` orkestrasyonu Üye 1 / Galip Efe sorumluluğunda; entegrasyon delege edildi. Rapor: `reports/agent-runs/issue-14-Eren-2026-04-23.md`.*)
    - [x] `tests/test_modules.py::TestRequirementImprover::test_improves_vague_requirement` mock'lu gerçek test.
    - [x] `modules/__init__.py`'a yeni prompt fonksiyonlarını ekle.

### 🟡 Issue #15: User Story ve BDD Senaryosu Üreteçleri
*   **Sorumlu:** **Halise İncir**
*   **Özet:** Fonksiyonel gereksinimleri Agile User Story formatına ve Gherkin BDD senaryolarına çeviren iki ayrı LLM destekli üreteç.
*   **User Story:** Bir Çevik Proje Yöneticisi olarak, çıkarılan gereksinimlerin doğrudan sprint backlog'una atılabilecek "As a... I want..." kartlarına ve QA ekibinin kullanabileceği "Given/When/Then" test senaryolarına otomatik dönüşmesini istiyorum.
*   **Kabul Kriterleri (AC):**
    - [ ] `StoryGenerator().generate(report)` `list[dict]` döner; her dict `{"role", "goal", "benefit", "acceptance_criteria"}` içerir.
    - [ ] `BDDGenerator().generate(report)` `list[str]` döner; her string `Feature:`, `Scenario:`, `Given`, `When`, `Then` anahtar kelimelerini içeren geçerli Gherkin formatında olmalı.
    - [ ] BDD çıktısı `outputs/generated/scenarios.feature` dosyasına yazılmalı; `pytest-bdd` veya `behave` ile parse edilebilir olmalı.
    - [ ] User Stories aynı zamanda `outputs/generated/user_stories.docx` olarak da export edilmeli.
*   **Görevler:**
    - [ ] `modules/story_prompts.py` ve `modules/bdd_prompts.py` oluştur (`conflict_prompts` template'ini takip et).
    - [ ] `outputs/story_generator.py::StoryGenerator.generate()` — sadece `req_type == "FUNCTIONAL"` olanları işler, LLM ile dönüştürür.
    - [ ] `outputs/bdd_generator.py::BDDGenerator.generate()` — her FR için minimum 1 happy path + 1 negative scenario üretir.
    - [ ] `python-docx` kullanarak `_export_to_docx(stories, path)` helper'ı yaz.
    - [ ] BDD `.feature` dosyası header'ına `# Generated by AutoReq | {timestamp}` ekle.
    - [ ] `app.py` analiz sonrası bu üreteçleri çağır, dosyaları `outputs/generated/`'a yaz.
    - [ ] `tests/test_outputs.py::TestStoryGenerator::test_story_format` ve `TestBDDGenerator::test_gherkin_format` gerçek assertion'larla doldur.

### 🔵 Issue #16: Çelişki / Eksiklik / İyileştirme Görselleştirme
*   **Sorumlu:** **Agid Gülsever**
*   **Özet:** Şu an tüm çelişkilerin/eksiklerin ham `dict` halinde basıldığı sonuç sekmelerini, bilgilendirici kart UI'larına dönüştürmek.
*   **User Story:** Bir Proje Paydaşı olarak, çelişkileri renkli severity rozetleriyle, eksiklikleri kategorize edilmiş checklist olarak ve iyileştirmeleri "öncesi/sonrası" karşılaştırmalı kart olarak görmek istiyorum, böylece teknik bilgim olmasa bile sonuçları kavrayabileyim.
*   **Kabul Kriterleri (AC):**
    - [ ] Çelişkiler sekmesinde her madde `conflict_card()` adlı bir bileşenle render edilmeli (severity rengi: high=kırmızı, medium=sarı, low=yeşil).
    - [ ] Eksikler sekmesinde maddeler `scenario` alanına göre gruplanmalı (authentication, authorization, data_privacy, …).
    - [ ] İyileştirme sekmesinde `original` (sol) vs `improved` (sağ) yan yana iki kolon halinde gösterilmeli.
    - [ ] Conflict kartlarındaki `req_ids` etiketleri tıklanınca o gereksinim kartına scroll edebilmeli (anchor link).
    - [ ] `tests/test_modules.py` içine mock LLM ile `ConflictDetector` ve `GapAnalyzer` testleri eklenmeli (her biri minimum 1 PASS).
*   **Görevler:**
    - [ ] `ui/components.py` içine yeni bileşenler ekle:
        - `conflict_card(conflict: dict)` — severity badge + req_ids + reason expander.
        - `gap_card(gap: dict)` — scenario etiketi + missing_area + suggestion + severity.
        - `improvement_diff_card(improvement: dict)` — 2 kolonlu original/improved.
    - [ ] `ui/results.py::tab2` ve `tab3`'ü ham dict listeleme yerine bu kartları kullanacak şekilde refactor et.
    - [ ] Tab2 başına özet metrik göstergeleri ekle: `st.metric("Toplam Çelişki", len(conflicts))`, `st.metric("Toplam Eksiklik", len(gaps))`.
    - [ ] Gereksinim kartlarına `st.markdown(f"<a id='{req_id}'></a>", unsafe_allow_html=True)` anchor ekle.
    - [ ] `tests/test_modules.py::TestConflictDetector::test_detects_contradiction` → mock LLM yanıtıyla gerçek çelişki tespiti testi.
    - [ ] `tests/test_modules.py::TestGapAnalyzer::test_detects_missing_password_reset` → mock LLM testi.

---

# 📦 5. Hafta (Sprint 5) Görev Listesi (Issues) — *Backlog, Veri & UI 2.0*

> 🎯 **Sprint Hedefi:** Sistemi gerçek ürün haline getirmek: önceliklendirilmiş Product Backlog üretimi, çoklu format export (Excel/DOCX/JSON), Pydantic ile güçlü tip doğrulaması, LLM önbellek (cost optimization) ve dosya yükleme + çoklu sayfa UI mimarisi.

### 🔴 Issue #17: Veri Şablonları, Örnek Veri Seti ve Pydantic Doğrulama
*   **Sorumlu:** **Galip Efe Öncü**
*   **Özet:** `data/` klasöründeki boş placeholder'ları gerçek örneklerle doldurmak ve `core/models.py` dataclass'larına Pydantic v2 doğrulama katmanı eklemek.
*   **User Story:** Bir Yazılım Mimarı olarak, sistemin örnek girdiler üzerinden hızlı test edilebilmesini ve modüller arası veri akışında tip uyuşmazlığı hatalarının runtime'da değil sınırda yakalanmasını istiyorum, böylece geliştirme döngüsü güvenli olsun.
*   **Kabul Kriterleri (AC):**
    - [ ] `data/samples/` altında en az 3 farklı domain örneği bulunmalı: `ornek_eticaret.txt`, `ornek_bankacilik.txt`, `ornek_egitim.txt`.
    - [ ] `data/templates/requirement_template.json` JSON Schema (draft 2020-12) standartında olmalı.
    - [ ] `core/models.py` dataclass'ları Pydantic v2 `BaseModel`'e geçirilmeli (veya hibrit dataclass+validator yaklaşımı).
    - [ ] Geçersiz veri (örn. `req_type="INVALID"`) ile `Requirement` oluşturulmaya çalışıldığında `ValidationError` fırlatılmalı.
    - [ ] Geçmiş tüm testler hâlâ PASS olmalı (geriye uyumluluk).
*   **Görevler:**
    - [ ] `data/samples/` içine 3-5 sayfalık gerçekçi Türkçe gereksinim metinleri yaz (e-ticaret, bankacılık, eğitim platformu domain'lerinden).
    - [ ] `data/templates/requirement_template.json` — `Requirement` dataclass'ının JSON Schema karşılığını oluştur.
    - [ ] `core/models.py`:
        - `Requirement`, `ParsedDocument`, `AnalysisReport` → `pydantic.BaseModel`'e dönüştür.
        - `req_type` alanına `Literal["FUNCTIONAL", "NON_FUNCTIONAL", "UNKNOWN"]` kısıtı.
        - `priority` alanına `Optional[Literal["HIGH", "MEDIUM", "LOW"]]` kısıtı.
        - `severity` validation'ı `analysis_report_parsing` içinde Pydantic'e devret.
    - [ ] Mevcut tüm `dataclasses.field(default_factory=list)` kullanımlarını Pydantic `Field(default_factory=list)` formuna çevir.
    - [ ] `tests/test_core.py::TestModels` — 5 yeni validation testi ekle.
    - [ ] `ui/dashboard.py`'a "Örnek Veri Yükle" dropdown'ı ekle (`data/samples/*.txt` içinden seçim).

### 🟠 Issue #18: LLM Hata Toleransı, Önbellek ve Maliyet Takibi
*   **Sorumlu:** **Eren Eyyüpkoca**
*   **Özet:** LLM çağrılarını cache'leyerek aynı metnin tekrar tekrar API'a gönderilmesini önlemek + retry/backoff + token tüketim takibi.
*   **User Story:** Bir Sistem Tasarımcısı olarak, kullanıcı aynı metni 5 kez analiz ettiğinde Gemini API'a 5 kez para ödemek yerine, ikinci ve sonraki çağrıların yerel önbellekten gelmesini istiyorum; ayrıca her sprint sonunda kaç token harcandığını görebilmek istiyorum.
*   **Kabul Kriterleri (AC):**
    - [ ] Aynı `(system_prompt + user_prompt)` çiftiyle yapılan ikinci `LLMClient.chat()` çağrısı API'a gitmeden önbellekten dönmeli (en az 100x daha hızlı).
    - [ ] Cache TTL yapılandırılabilir olmalı (default: 24 saat).
    - [ ] Gemini 5xx veya rate-limit hatalarında **3 kez** exponential backoff (1s, 2s, 4s) ile retry yapılmalı.
    - [ ] Her `LLMResponse.raw` içinde `usage_metadata` (input_tokens, output_tokens, estimated_cost_usd) bulunmalı.
    - [ ] Sidebar'da "Bu oturumda harcanan: ~$0.XX (YYY token)" göstergesi olmalı.
*   **Görevler:**
    - [ ] `modules/llm_cache.py` oluştur: `diskcache` veya `functools.lru_cache` tabanlı, key = `hashlib.sha256(system+user)`.
    - [ ] `LLMClient._chat_gemini` çağrısını cache wrapper ile sarmala; `bypass_cache=True` parametresi ile cache'i atlama opsiyonu.
    - [ ] `tenacity` veya manuel `for attempt in range(3): try: ... except: time.sleep(2**attempt)` retry logic ekle.
    - [ ] `LLMResponse.raw["usage"]` içine token sayıları + tahmini maliyet (Gemini Flash pricing).
    - [ ] `st.session_state.total_tokens_used` ve `total_cost_usd` accumulator'ları.
    - [ ] `ui/dashboard.py` sidebar'ına maliyet metric'ini ekle.
    - [ ] `tests/test_modules.py::TestLLMClient::test_cache_hit` — aynı prompt 2x çağrılınca mock fonksiyon 1x çalışmalı.

### 🟡 Issue #19: Product Backlog Üreteci ve Çoklu Format Export
*   **Sorumlu:** **Halise İncir**
*   **Özet:** Önceliklendirme skorlamasıyla Product Backlog üretmek + tüm çıktıları Excel/DOCX/JSON formatlarında dışa aktarmak.
*   **User Story:** Bir Proje Yöneticisi olarak, sistemden çıkan gereksinimlerin doğrudan Excel'e/DOCX'e aktarılabilmesini ve sprint planlama için kullanılabilecek puanlanmış bir Product Backlog'a dönüşmesini istiyorum, böylece haftalık planlama toplantısında manuel iş kalmasın.
*   **Kabul Kriterleri (AC):**
    - [ ] `BacklogGenerator().generate(report)` `list[dict]` döndürmeli; her dict `{"req_id", "title", "priority_score", "story_points", "type", "depends_on"}` içermeli.
    - [ ] Skorlama formülü: `priority_score = priority_weight × type_weight × conflict_penalty × dependency_factor`.
    - [ ] Excel export (`.xlsx`) Backlog'u tablo halinde, formül-doğrulama kuralları uygulanmış olarak üretmeli.
    - [ ] DOCX export User Stories'i resmi şablon formatında (başlık, role, tablo) sunmalı.
    - [ ] JSON export tüm `AnalysisReport`'u serialize etmeli (Pydantic `.model_dump_json()` ile).
    - [ ] UI download sekmesinde 4 farklı dosya butonu olmalı: PDF (SRS), XLSX (Backlog), DOCX (Stories), JSON (Full Report).
*   **Görevler:**
    - [ ] `outputs/backlog_generator.py::BacklogGenerator.generate()` — skorlama mantığı:
        - `priority_weight = {HIGH: 3, MEDIUM: 2, LOW: 1}`
        - `type_weight = {FUNCTIONAL: 1.0, NON_FUNCTIONAL: 0.7}`
        - Çelişki listesinde geçen `req_id`'lere `× 1.5` (önce çözülsün diye yukarı çek).
    - [ ] `outputs/exporters.py` (yeni dosya) içinde:
        - `export_backlog_xlsx(backlog, path)` — `openpyxl` ile.
        - `export_stories_docx(stories, path)` — `python-docx` ile.
        - `export_report_json(report, path)` — Pydantic JSON.
    - [ ] `app.py`'a analiz sonrası 4 dosyayı paralel üretme adımı ekle.
    - [ ] `ui/results.py::tab4`'e 4 ayrı `download_button` ekle.
    - [ ] `tests/test_outputs.py::TestBacklogGenerator::test_priority_scoring` — bilinen senaryoyla skor hesaplaması doğrulansın.

### 🔵 Issue #20: UI Mimarisi 2.0 — Çoklu Sayfa ve Dosya Yükleme
*   **Sorumlu:** **Agid Gülsever**
*   **Özet:** Streamlit'in `st.navigation`/`pages/` yapısı ile çoklu sayfa mimarisine geçmek + .txt/.docx/.pdf dosya yükleme desteği eklemek.
*   **User Story:** Bir İş Analisti olarak, müşteriden e-posta ile gelen `.docx` ve `.pdf` toplantı notlarını sürükle-bırak ile yükleyip analiz edebilmek ve sonuçları "Giriş", "Analiz", "Sonuçlar", "Export" sayfaları arasında gezinebilmek istiyorum.
*   **Kabul Kriterleri (AC):**
    - [ ] `streamlit run app.py` artık 4 ayrı sayfa açmalı: 📥 Girdi / 🔬 Analiz / 📊 Sonuçlar / 📤 Export.
    - [ ] `.txt`, `.docx`, `.pdf` dosyaları yüklenebilmeli; metin otomatik çıkarılıp text_area'ya doldurulmalı.
    - [ ] Sidebar'da gerçek zamanlı sayaç olmalı: gereksinim sayısı, çelişki sayısı, eksiklik sayısı.
    - [ ] Session state ile bir analiz, sayfalar arası gezildiğinde kaybolmamalı.
    - [ ] `pyproject.toml` veya `requirements.txt`'e `python-docx` ve `pypdf` (zaten varsa atla) eklenmeli.
*   **Görevler:**
    - [ ] `app.py` → ana entry: `st.navigation` ile 4 sayfa tanımlayan ince orchestrator'a indirgen.
    - [ ] `ui/pages/01_input.py`, `02_analysis.py`, `03_results.py`, `04_export.py` (veya `pages/` klasörü) oluştur.
    - [ ] `ui/file_loader.py` — `extract_text_from_upload(uploaded_file) -> str`:
        - `.txt` → direkt decode
        - `.docx` → `python-docx`
        - `.pdf` → `pypdf` veya `pdfplumber`
        - Diğer → `ValueError`.
    - [ ] `ui/dashboard.py`'da `st.file_uploader(accept=[".txt", ".docx", ".pdf"])` widget'ı.
    - [ ] Sidebar'a `st.metric` ile canlı sayaçlar (`req_count`, `conflict_count`, `gap_count`, `cost_usd`).
    - [ ] `st.session_state` schema'sını standartlaştır ve `ui/state.py`'a çıkar.
    - [ ] Drag & drop UX testi: 3 farklı format dosya ile manuel doğrulama checklist'i.

---

# 🏁 6. Hafta (Sprint 6) Görev Listesi (Issues) — *Performans, Test, Demo*

> 🎯 **Sprint Hedefi:** Ürünü demo-ready hale getirmek: performans hedeflerini (<15s) tutturmak, test coverage'ı %70'in üzerine çıkarmak, prompt regresyon suite kurmak, ISO/IEC/IEEE 29148 uyumunu doğrulamak ve final sunum materyallerini hazırlamak.

### 🔴 Issue #21: Performans Optimizasyonu ve Uçtan Uca Entegrasyon Testleri
*   **Sorumlu:** **Galip Efe Öncü**
*   **Özet:** Tüm pipeline'ı NFR hedefi olan "<15 saniye / tek sayfa metin" eşiğine indirmek + uçtan uca entegrasyon testleri yazmak.
*   **User Story:** Bir Yazılım Mimarı olarak, müşteriye demo gösterirken sistemin 100 cümlelik metni 15 saniyenin altında analiz etmesini ve `pytest tests/integration/` komutunun pipeline'ın tüm uçlarını doğrulayan testleri çalıştırmasını istiyorum.
*   **Kabul Kriterleri (AC):**
    - [ ] `tests/integration/test_e2e.py` — `data/samples/ornek_eticaret.txt` üzerinde tam `process_text()` akışı **<15s** içinde tamamlanmalı (pytest fixture ile zaman ölçümü).
    - [ ] `cProfile` veya `py-spy` çıktısı `docs/performance_report.md`'de paylaşılmalı, hot path'ler belgelenmeli.
    - [ ] `EntityRecognizer` ve `RequirementClassifier` aynı paylaşılan Stanza pipeline'ını kullanmalı (Sprint 3'ten kalmışsa kapat).
    - [ ] Bellek kullanımı: ilk Stanza yükleme sonrası **<800 MB** olmalı.
*   **Görevler:**
    - [ ] `cProfile` ile pipeline'ı profile et; en yavaş 5 fonksiyonu raporla.
    - [ ] Per-requirement classifier+NER çağrılarını `concurrent.futures.ThreadPoolExecutor` ile paralelleştir (LLM çağrıları hariç — onlar sıralı).
    - [ ] `core/preprocessor.py` — Stanza pipeline'a sadece gerekli processor'ları yükle (zaten `tokenize,pos,lemma`, kontrol et).
    - [ ] `LLM` çağrıları için `asyncio` veya batched chat (multi-prompt single call) araştırması — uygulanabilirse implement et.
    - [ ] `tests/integration/__init__.py` + `test_e2e.py`:
        - Fixture: 3 farklı sample dosyası.
        - Assert: `process_text(text)` < 15s.
        - Assert: `report.parsed_doc.requirements` boş değil, en az 1 conflict veya gap var.
    - [ ] `docs/performance_report.md` belgesi oluştur, profil sonuçlarını özetle.

### 🟠 Issue #22: Prompt Regresyon Suite ve LLM Mock Fixture'ları
*   **Sorumlu:** **Eren Eyyüpkoca**
*   **Özet:** Prompt değişikliklerinin çıktı kalitesini bozmadığını otomatik doğrulayan snapshot test altyapısı + tüm üyelerin kullanabileceği zengin LLM mock fixture kütüphanesi.
*   **User Story:** Bir QA Engineer olarak, prompt'larda yapılan en küçük değişikliğin bile bilinen 20 örnek gereksinim setinde regresyona neden olup olmadığını CI'da otomatik görmek istiyorum, böylece prompt iyileştirmeleri güvenle merge edilsin.
*   **Kabul Kriterleri (AC):**
    - [ ] `tests/golden/` klasörü 20 örnek gereksinim seti + beklenen çelişki/eksiklik JSON snapshot'ları içermeli.
    - [ ] `pytest tests/regression/` komutu LLM olmadan (mock ile) tüm prompt builder'ları çalıştırıp snapshot karşılaştırmalı.
    - [ ] Prompt builder fonksiyonlarının çıktısı (tam string) snapshot olarak versiyonlanmalı; değişiklik geldiğinde test FAIL olmalı.
    - [ ] `tests/conftest.py`'a en az 5 LLM mock fixture eklenmeli (boş yanıt, malformed JSON, normal yanıt, rate limit, timeout).
*   **Görevler:**
    - [ ] `tests/golden/sample_requirements/*.txt` — 20 farklı senaryo (auth eksik, çelişkili limitler, NFR muğlaklık, vs.).
    - [ ] `tests/golden/expected/*.json` — beklenen `AnalysisReport.conflicts/gaps` çıktıları (manuel olarak hazırlanan ground truth).
    - [ ] `tests/regression/test_prompt_snapshots.py` — `syrupy` veya `snapshottest` ile snapshot testleri.
    - [ ] `tests/conftest.py`'a fixtures:
        - `mock_llm_normal` — istenen JSON'u döner.
        - `mock_llm_empty` — boş string döner.
        - `mock_llm_malformed` — bozuk JSON döner (`{"key":}`).
        - `mock_llm_rate_limit` — `LLMClientError` fırlatır.
        - `mock_llm_with_markdown` — JSON'u ` ```json ... ``` ` içinde döner.
    - [ ] CI workflow (`.github/workflows/test.yml`) yoksa oluştur, `pytest tests/regression/` adımını ekle.
    - [ ] `docs/prompt_versioning.md` — prompt değişiklik prosedürünü belgele.

### 🟡 Issue #23: ISO/IEC/IEEE 29148 Uyum Doğrulaması ve Final Doküman Kalitesi
*   **Sorumlu:** **Halise İncir**
*   **Özet:** Üretilen SRS PDF'in standartla uyumunu kontrol etmek, çoklu dil font desteği eklemek ve PDF çıktı bütünlüğü testleri yazmak.
*   **User Story:** Bir Dokümantasyon Uzmanı olarak, sistemden çıkan SRS belgesinin gerçekten ISO/IEC/IEEE 29148:2018 standardındaki 10 zorunlu bölümü içerdiğini ve farklı dillerdeki karakterleri (Türkçe, İngilizce, Arapça, Çince) sorunsuz render ettiğini doğrulayan otomatik testler istiyorum.
*   **Kabul Kriterleri (AC):**
    - [ ] `docs/ISO_29148_compliance_checklist.md` belgesi 10 zorunlu bölümü ve her birinin SRS'te nasıl karşılandığını listelemeli.
    - [ ] PDF üretici, `pypdf` ile parse edildiğinde 10 başlığı da içermeli (otomatik test).
    - [ ] Türkçe karakter (ş, ğ, İ) + İngilizce karışık metin sorunsuz render olmalı.
    - [ ] PDF metadata'sı doldurulmalı: title, author (AutoReq), subject (SRS), creator, creation_date.
    - [ ] PDF dosya boyutu **<5 MB** olmalı (logo + font'lar dahil).
*   **Görevler:**
    - [ ] `outputs/srs_generator.py` — PDF metadata setter'ları ekle (`pdf.set_title()`, `set_author()`).
    - [ ] Cross-platform Unicode font desteği için `outputs/fonts/` klasörü oluştur, `DejaVuSans.ttf` ve `NotoSans.ttf` paketle (veya runtime indir).
    - [ ] PDF watermark "DRAFT — AutoReq Generated" eklenebilir opsiyonel parametre.
    - [ ] `docs/ISO_29148_compliance_checklist.md`:
        - Section 1: Introduction → Otomatik dolduruluyor mu? Evet/Hayır + kanıt.
        - … 10 bölüm için aynı format.
    - [ ] `tests/test_outputs.py::TestSRSGenerator`:
        - `test_pdf_contains_all_iso_sections` — `pypdf` ile parse, başlık eşleşmesi.
        - `test_pdf_metadata` — title/author kontrolü.
        - `test_pdf_size_under_5mb` — dosya boyutu.
        - `test_turkish_chars_render` — "ş, ğ, İ" PDF metninde extract edildiğinde bozulmamış olmalı.

### 🔵 Issue #24: Test Coverage %70+, Bug Bash ve Final Demo Hazırlığı
*   **Sorumlu:** **Agid Gülsever**
*   **Özet:** Tüm projenin test kapsamını %70 üzerine çıkarmak, son bir bug bash session organize etmek ve demo materyallerini (senaryo, ekran görüntüleri, video script) hazırlamak.
*   **User Story:** Bir Proje Sponsoru olarak, final demo öncesi sistemin tüm kritik akışlarının test edilmiş, görsel olarak cilalı ve sunum sırasında çökme riski sıfıra indirilmiş halde olmasını istiyorum.
*   **Kabul Kriterleri (AC):**
    - [ ] `pytest --cov=core --cov=modules --cov=outputs --cov-report=term` çıktısında **toplam coverage ≥ %70**.
    - [ ] `core/`, `modules/`, `outputs/` her birinde minimum **%65** coverage.
    - [ ] Demo için 5 hazır senaryo `data/demo_scenarios/` altında bulunmalı; her biri farklı bir özelliği vurgulamalı (çelişki, gap, improvement, multi-actor, NFR-yoğun).
    - [ ] `docs/demo_script.md` — 10 dakikalık demo akışı, her dakika için ne yapılacağı yazılı olmalı.
    - [ ] `README.md`'ye en az 3 ekran görüntüsü eklenmeli.
    - [ ] Bug bash sonrası açılan tüm "Critical" ve "High" severity issue'lar kapatılmış olmalı.
*   **Görevler:**
    - [ ] Coverage gap analizi: `pytest --cov --cov-report=html` çalıştır, `htmlcov/index.html`'e bak, kapsanmayan satırları listele.
    - [ ] Eksik kritik testleri yaz:
        - `tests/test_core.py` — `TextPreprocessor`'un boş, tek kelime, çok uzun metin senaryoları.
        - `tests/test_modules.py` — `LLMClient`'in tüm hata yollarını mock ile cover et.
        - `tests/test_outputs.py` — Backlog priority scoring edge case'leri.
    - [ ] `data/demo_scenarios/`:
        - `01_e_ticaret_celisma.txt` (çelişki ağırlıklı)
        - `02_bankacilik_eksik.txt` (gap ağırlıklı)
        - `03_egitim_mughrak.txt` (improvement ağırlıklı)
        - `04_kurumsal_portal_multi_actor.txt`
        - `05_mobil_app_nfr_agirlikli.txt`
    - [ ] `docs/demo_script.md` — dakika dakika sunum planı.
    - [ ] Bug Bash session organize et (1 saat, tüm ekip + 1 dış gözlemci) — `docs/bug_bash_results.md`'ye sonuçları yaz.
    - [ ] README.md'ye demo ekran görüntüleri ekle (`docs/screenshots/`).
    - [ ] Final demo için Streamlit sayfasını "Demo Modu" toggle'ı ile özelleştir (sample dropdown + sunum-friendly UI).

---

## 📊 Sprint Bazlı İş Yükü Dağılımı (Özet)

| Sprint | Galip (NLP/Core) | Eren (LLM Modules) | Halise (Outputs) | Agid (UI/Test) |
|---|---|---|---|---|
| **Sprint 3** | #9 Pipeline entegrasyonu, Stanza dedup | #10 GapAnalyzer impl | #11 Dinamik SRS PDF | #12 UI bug + test modernizasyonu |
| **Sprint 4** | #13 Loguru migrasyonu + Priority detector | #14 RequirementImprover (Few-shot) | #15 Story + BDD üreteçleri | #16 Çelişki/gap görselleştirme |
| **Sprint 5** | #17 Pydantic + sample data | #18 LLM cache + cost tracking | #19 Backlog + multi-format export | #20 Multi-page UI + file upload |
| **Sprint 6** | #21 Performans + E2E testler | #22 Prompt regresyon + mock library | #23 ISO 29148 uyum + PDF kalite | #24 %70 coverage + bug bash + demo |

> **PM Notu:** Sprint 3 dependencies kritiktir — Issue #10 (GapAnalyzer) tamamlanmadan Issue #9'un tüm AC'leri test edilemez; benzer şekilde Issue #11 (dinamik SRS) Issue #9'un app.py değişikliklerine bağlıdır. İlk 3 günde #10 ve #12, son 4 günde #9 ve #11'i koordine etmeniz önerilir.

> **Risk:** Sprint 5'teki Pydantic migrasyonu (#17) tüm modülleri etkileyen yatay bir değişikliktir. Sprint 4 sonunda `develop` dalı tamamen yeşil değilse #17'yi Sprint 6'ya kaydırın ve onun yerine Sprint 5'te ekstra UX cilalama yapın.

> **Burndown Hedefi:** Sprint 6 sonunda kalan stub modül **0**, açık kritik bug **0**, test coverage **≥ %70**, demo senaryoları **5 hazır**.
