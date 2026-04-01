# 🗺 AutoReq: 6 Haftalık Geliştirme Yol Haritası

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
*   **Görevler:**
    - [x] `requirements.txt` dosyasını `spaCy`, `streamlit`, `langchain`, `python-dotenv` kütüphaneleriyle güncelle.
    - [x] `core/models.py` içinde `Requirement`, `ParsedDocument` ve `AnalysisReport` dataclass'larını finalize et.
    - [x] `core/preprocessor.py` içine Türkçe stop-words temizleme ve temel normalizasyon kodlarını yaz.
    - [x] `app.py` üzerinde modüllerin entegrasyonu için merkezi `process_text()` fonksiyonunu tanımla.

### 🟠 Issue #2: LLM Bağlantı Altyapısı ve Servis Katmanı
*   **Sorumlu:** **Eren Eyyüpkoca**
*   **Özet:** Sistemin LLM (OpenAI/Ollama) ile güvenli ve hızlı iletişim kurmasını sağlamak.
*   **Görevler:**
    - [x] **LLM Pazar Araştırması:** Mevcut en ucuz/ücretsiz (Groq, OpenRouter, Google Gemini vb.) ve en güçlü/hızlı LLM API sağlayıcısını belirle.
    - [x] `modules/llm_client.py` oluştur; LangChain veya doğrudan API kullanarak merkezi talep yapısını kur.
    - [x] `.env.example` dosyası oluştur ve API anahtarı yönetimini dökümante et.
    - [x] Çelişki tespiti için ilk sistem prompt'larını (System Messages) tasarla.
    - [x] Modüller için temel loglama (logging) yapısını kur.

### 🟡 Issue #3: SRS PDF Motoru ve Mühendislik Şablonu
*   **Sorumlu:** **Halise İncir**
*   **Özet:** Otomatik üretilecek dökümanların teknik altyapısını kurmak.
*   **Görevler:**
    - [ ] `outputs/srs_generator.py` oluştur ve `fpdf2` kütüphanesi ile boş bir taslak üretmeyi test et.
    - [ ] ISO/IEC/IEEE 29148 standardındaki 10 temel başlığı (Giriş, Kapsam, Fonksiyonel Gereksinimler vb.) koda dök.
    - [ ] PDF çıktısı için kurumsal bir logo ve sayfa numaralandırma yapısı ekle.
    - [ ] Türkçe karakterlerin (ş, ğ, ı, İ) PDF'de sorunsuz çıkması için font yükleme kodunu yaz.

### 🔵 Issue #4: UI Dashboard ve Test Altyapısı
*   **Sorumlu:** **Agid Gülsever**
*   **Özet:** Kullanıcının etkileşime gireceği arayüzü ve projenin test disiplinini kurmak.
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
*   **Görevler:**
    - [ ] `core/classifier.py` içerisindeki `classify()` fonksiyonunu kural tabanlı (veya scikit-learn kullanarak) doldur; gereksinimleri `FUNCTIONAL`/`NON_FUNCTIONAL` yap.
    - [ ] `core/ner.py` içerisinde `spaCy` NER kullanarak "Kullanıcı", "Sistem" gibi aktörleri bulup `req.actors` listesine ekle.
    - [ ] Metindeki ana nesneleri (örn: şifre, form, e-posta) tespit edip `req.objects` listesine ekle.
    - [ ] `app.py` içerisindeki `NotImplementedError` veren `classifier` ve `ner` geçişini sağlayan kod satırlarını aktif hale getir.

### 🟠 Issue #6: Çelişki ve Eksiklik Analiz Yapay Zeka (LLM) Motoru
*   **Sorumlu:** **Eren Eyyüpkoca**
*   **Özet:** LLM API kullanarak gereksinimler arası mantıksal hataları/eksikleri bulma altyapısını kurmak.
*   **Görevler:**
    - [ ] `modules/conflict_detector.py` içindeki `analyze()` fonksiyonunda `LLMClient` sınıfını entegre et.
    - [ ] Hazırladığın system prompt'ları kullanarak gereksinimleri LLM'e gönderip "Hangi gereksinimler birbiriyle çelişiyor?" analizini kur.
    - [ ] `modules/gap_analyzer.py` için standart senaryolarda (giriş, yetkilendirme vs.) "eksik" olan adımları bulan prompt mimarisi kurgula.
    - [ ] LLM'den dönen sonuçları parse et ve `AnalysisReport` nesnesinin `conflicts` ile `gaps` listelerine uygun bir dict yapısıyla ekle.

### 🟡 Issue #7: User Story Üreteci ve Dinamik SRS Çıktısı
*   **Sorumlu:** **Halise İncir**
*   **Özet:** "As a [role], I want..." hikayelerini üretmek ve SRS şablonunu dinamikleştirmek.
*   **Görevler:**
    - [ ] `outputs/story_generator.py` içine fonksiyonel gereksinimleri Agile User Story formatına çeviren kodları yaz (bunun için LLMClient'ı kullanabilirsin).
    - [ ] Geçen hafta oluşturduğun statik `srs_generator.py` fonksiyonunu, Üye 2'den dönen gerçek `AnalysisReport` verileriyle akıllıca dolduracak şekilde dinamikleştir.
    - [ ] `app.py` üzerinde analiz bittiğinde SRS PDF'inin arka planda oluşturulmasını sağlayan fonksiyon çağrısını yap.

### 🔵 Issue #8: Sonuçların Görselleştirilmesi ve Analiz Raporu Sekmeleri
*   **Sorumlu:** **Agid Gülsever**
*   **Özet:** Sistemden dönen tam teşekküllü analiz raporunun arayüzde profesyonelce sergilenmesi.
*   **Görevler:**
    - [ ] Düzene sokulan `ui/results.py` içerisindeki tab'ları, `report.conflicts` ve `report.gaps` verilerini dict içinden okuyup listeleyecek şekilde (for/while vb.) doldur.
    - [ ] `ui/components.py` içinde `req_card()` adında bir bileşen fonksiyonu yarat ve gereksinimleri sıradan metin değil bu şık component'lerle ekrana bas.
    - [ ] "İndirilebilir Çıktılar" sekmesine, `outputs` modülüyle oluşturulan PDF dosyası için indirme (`st.download_button`) butonu ekle.
    - [ ] Core modüller (`classifier.py` ve `ner.py`) için en az birer tane mantıksal (assertion içeren) test yaz.
