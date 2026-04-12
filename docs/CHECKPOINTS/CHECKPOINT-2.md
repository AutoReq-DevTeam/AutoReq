---
marp: true
theme: default
paginate: true
backgroundColor: #ffffff
style: |
  section {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    color: #000000;
    padding: 50px 60px;
    font-size: 20px;
    background-color: #ffffff !important;
  }
  section.lead {
    text-align: left;
    display: flex;
    flex-direction: column;
    justify-content: center;
    border: 4px solid #000000;
    padding: 40px;
  }
  section.lead h1 {
    font-family: 'Times New Roman', Times, serif;
    font-size: 48px;
    margin: 0 0 20px 0;
    padding: 0;
    border-bottom: 2px solid #000000;
  }
  section.lead h3 {
    font-size: 24px;
    font-weight: normal;
    margin-top: 10px;
  }
  h1 {
    font-family: 'Times New Roman', Times, serif;
    font-size: 36px;
    margin-bottom: 25px;
    border-bottom: 1px solid #000000;
    padding-bottom: 10px;
  }
  h2 {
    font-size: 26px;
    margin-top: 0;
    font-weight: bold;
    border-bottom: 1px solid #cccccc;
    padding-bottom: 5px;
  }
  strong { 
    font-weight: bold;
  }
  ul {
    padding-left: 20px;
  }
  ul li { 
    margin-bottom: 8px; 
    line-height: 1.4;
  }
  ul li::marker { color: #000000; }
  table { 
    width: 100%; 
    border-collapse: collapse; 
    margin-top: 20px; 
    font-size: 16px; 
    font-family: 'Helvetica Neue', Arial, sans-serif;
  }
  th { 
    background-color: #f2f2f2; 
    color: #000000; 
    padding: 15px 15px; 
    text-align: left; 
    border: 1px solid #000000;
  }
  td { 
    padding: 15px 15px; 
    border: 1px solid #000000; 
  }
  blockquote {
    border-left: 4px solid #000000;
    background: #f8f8f8;
    padding: 15px 20px;
    margin: 20px 0;
    font-style: italic;
  }
---

<!-- _class: lead -->

# AutoReq Projesi
### Checkpoint #2 Değerlendirme Raporu
**Doküman Tipi:** Sprint 2 Backlog & Kabul Kriterleri
**Ekip:** AutoReq DevTeam
**Format Standardı:** ISO/IEC 29148 (Referans Alınmıştır)

---

## 🎯 Proje Genel Yol Haritası ve Tamamlanan Aşamalar

**Ana Hedef:** Projenin toplam **6 Sprint (6 Hafta)** içerisinde uçtan uca tamamlanarak nihai ürüne dönüştürülmesi hedeflenmektedir.

**Mevcut Durum ve Yapılan Sprintler:**
*   **Sprint 1 (Tamamlanmış İşler):** Proje temel iskeleti (modeller), LLM entegrasyonu, statik PDF raporlama altyapısı ve temel Streamlit arayüzü kuruldu.
*   **Sprint 2 (Mevcut Checkpoint Hedefi):** Doğal Dil İşleme (NLP) motorunun devresi (NER, Sınıflandırma), LLM ile çelişki tespiti ve dinamik dashboard entegrasyonuna odaklanıldı.

---

## 1. Sprint Hedefi ve Amaçlar (Sprint Goal)

**Hedef Özeti:**
Metin sınıflandırma ve LLM tabanlı analiz motorlarının entegrasyonu; analiz sonuçlarının dinamik bir kullanıcı arayüzü ve dışa aktarılabilir PDF raporu ile sunulması.

**Beklenen Çıktı:** 
Sistem, ham metin girildiğinde otonom olarak aktörleri tespit etmeli, LLM aracılığıyla mantıksal çelişkileri bulmalı ve standartlara uygun bir Yazılım Gereksinim Spesifikasyonu (SRS) raporu üretebilmelidir.

---

## 2. Ürün İş Listesi ve Kullanıcı Hikayeleri (Sprint 1)

| ID | Persona | Kullanıcı Hikayesi (User Story) | Değer / Gerekçe | Sorumlu |
|:---|:---|:---|:---|:---|
| **US1** | Yazılım Mimarı | Projenin modüler bir iskelete ve veri yapılarına sahip olmasını istiyorum. | Çakışmadan geliştirmeyi başlatır. | Galip |
| **US2** | Sistem Tasarımcısı | Merkezi bir LLM servisi üzerinden API talebi yapabilmeyi istiyorum. | Kod tekrarını ve karmaşayı önler. | Eren |
| **US3** | Dokümantasyon Uz. | ISO/IEC standartlarında PDF rapor iskeleti olmasını istiyorum. | Analiz çıktılarını standartlaştırır. | Halise |
| **US4** | Son Kullanıcı | Metinleri yapıştırıp analiz edebileceğim bir arayüz istiyorum. | Girdi ve izleme süreçlerini kolaylaştırır. | Agid |

---

## 2. Ürün İş Listesi ve Kullanıcı Hikayeleri (Sprint 2)

| ID | Persona | Kullanıcı Hikayesi (User Story) | Değer / Gerekçe | Sorumlu |
|:---|:---|:---|:---|:---|
| **US5** | İş Analisti | Metnin F/NFR ayrımını yapmasını ve aktörleri çıkarmasını istiyorum. | Manuel gereksinim ayıklama işini sıfırlar. | Galip |
| **US6** | Kalite Uzmanı | Zıtlık ve çelişki yaratan gereksinimleri bulup uyarmasını istiyorum. | Hatalı mimari kod yazımını en başta önler. | Eren |
| **US7** | Proje Yöneticisi | Çıkarımların otonom "Agile User Story" çevrilmesini istiyorum. | Geliştiriciler için doğrudan sprint task'ı verir. | Halise |
| **US8** | Proje Paydaşı | Sonuçları UI sekmelerinde ve indirilebilir PDF halinde istiyorum. | Çıktılara şeffaf ve kurumsal ulaşım sağlar. | Agid |

---

## 3. Kabul Kriterleri (Acceptance Criteria - AC)

*Bir User Story'nin "Bitti (Done)" sayılması için karşılanması gereken ölçülebilir koşullar.*

*   **US1 / US5 (Modeller & Sınıflandırma):**
    *   Algoritma "Sistem hızlı olmalı" cümlesini *NON_FUNCTIONAL* olarak etiketlemelidir.
    *   `Stanza` kütüphanesi harici dataset indirmeden çalışıp aktör isimlerini `req.actors` listesine atmalıdır.
*   **US2 / US6 (LLM İstekleri & Çelişki Tespiti):**
    *   `.env` dosyası üzerinden API Key okunmalı ve uzak LLM sunucusuna güvenle prompt atılabilmelidir.
    *   Mantıksal zıtlıklar, exception fırlatmadan JSON şeklinde parse edilerek `AnalysisReport` nesnesine eklenmelidir.
*   **US4 / US8 (Arayüz & PDF Çıktı):**
    *   Kullanıcı Streamlit sistemini kullanırken ekranda bilgilendirici spinner (yükleniyor) animasyonu olmalıdır.
    *   `st.download_button` butonundan inen UTF-8 destekli Türkçe karakterli PDF hatasız bir şekilde açılabilmelidir.

---

## 4. Fonksiyonel Olmayan Gereksinimler (Non-Functional Requirements - NFR)

1.  **Güvenlik Kısıtı (Security):** LLM API anahtarları sıkı bir şekilde yerel `.env` dosyasında izole edilmeli ve versiyon kontrol sistemlerine (örn. GitHub) kesinlikle push edilmemelidir.
2.  **Performans Kısıtı (Performance):** Standart tek sayfalık bir metnin tam blok analizi (NER, sınıflandırma ve LLM çelişki tespiti dahil) **15 saniyenin altında** tamamlanmalıdır.
3.  **Kullanılabilirlik Kısıtı (Usability):** Kullanıcı arayüzü tek bir dashboard (panel) bütünlüğünü korumalı ve işlem sırasında aktif süreç göstergeleri (spinner/progress bar) barındırmalıdır.

---

## 5. Uygulama ve Kod Dağılımı (Ekip Rolleri)

Mevcut iş listesine (backlog) karşılık gelen aktif kod sorumlulukları şu şekildedir:

*   **Galip:** Temel Kural Tabanlı NLP Boru Hattı (`core/classifier.py` & `core/ner.py`)
*   **Eren:** LLM Zeka Katmanı (`modules/conflict_detector.py`)
*   **Halise:** Üretken Çıktı & SRS Formatlayıcı (`outputs/story_generator.py`)
*   **Agid:** UI Dashboard & Kalite Güvencesi - Testler (`ui/results.py` & `tests/`)