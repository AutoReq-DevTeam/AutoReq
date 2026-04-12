# 🗺 AutoReq: 6 Haftalık Geliştirme Yol Haritası (Toplam 6 Sprint)

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

| Hafta | Odak Noktası | Ana Hedef |
| :--- | :--- | :--- |
| **Hafta 1** | **Temel Altyapı** | Proje iskeleti, LLM bağlantısı ve Streamlit ana giriş ekranı. |
| **Hafta 2** | **NLP Motoru** | Metinlerin F/NF olarak ayrılması ve Aktör/Nesne tespiti (NER). |
| **Hafta 3** | **Zeka Katmanı** | Prompt Engineering ile çelişki dedektörü ve eksik gereksinim tespiti. |
| **Hafta 4** | **SRS & Dökümantasyon** | ISO 29148 standartlarında PDF raporlama ve User Story üreteci. |
| **Hafta 5** | **Gelişmiş Çıktılar** | BDD senaryoları (Gherkin) ve Product Backlog dışa aktarımı. |
| **Hafta 6** | **Entegrasyon & Final** | Uçtan uca testler, hata ayıklama ve Final Demo hazırlığı. |

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
