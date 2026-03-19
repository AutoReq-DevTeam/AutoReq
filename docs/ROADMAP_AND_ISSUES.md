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
    - [ ] `requirements.txt` dosyasını `spaCy`, `streamlit`, `langchain`, `python-dotenv` kütüphaneleriyle güncelle.
    - [ ] `core/models.py` içinde `Requirement`, `ParsedDocument` ve `AnalysisReport` dataclass'larını finalize et.
    - [ ] `core/preprocessor.py` içine Türkçe stop-words temizleme ve temel normalizasyon kodlarını yaz.
    - [ ] `app.py` üzerinde modüllerin entegrasyonu için merkezi `process_text()` fonksiyonunu tanımla.

### 🟠 Issue #2: LLM Bağlantı Altyapısı ve Servis Katmanı
*   **Sorumlu:** **Eren Eyyüpkoca**
*   **Özet:** Sistemin LLM (OpenAI/Ollama) ile güvenli ve hızlı iletişim kurmasını sağlamak.
*   **Görevler:**
    - [ ] **LLM Pazar Araştırması:** Mevcut en ucuz/ücretsiz (Groq, OpenRouter, Google Gemini vb.) ve en güçlü/hızlı LLM API sağlayıcısını belirle.
    - [ ] `modules/llm_client.py` oluştur; LangChain veya doğrudan API kullanarak merkezi talep yapısını kur.
    - [ ] `.env.example` dosyası oluştur ve API anahtarı yönetimini dökümante et.
    - [ ] Çelişki tespiti için ilk sistem prompt'larını (System Messages) tasarla.
    - [ ] Modüller için temel loglama (logging) yapısını kur.

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
