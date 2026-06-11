# AutoReq Kapsamlı NLP ve LLM Değerlendirme Raporu

**Tarih:** 11 Haziran 2026  
**Durum:** Tamamlandı  
**Veri Klasörü:** `data/evaluation/`  
**Rapor Dosyaları:** `reports/*.json`  

---

## 📊 Genel Metrikler ve Özet

Bu rapor, AutoReq projesindeki Doğal Dil İşleme (NLP) ve Büyük Dil Modeli (LLM) tabanlı analiz modüllerinin performansını ölçmek amacıyla **genişletilmiş veri kümeleri** üzerinde yapılan test sonuçlarını sunmaktadır.

| Değerlendirme Kategorisi | Veri Seti Büyüklüğü | Aktör NER F1-Skoru | Sınıflandırma Doğruluğu | Çelişki Yakalama (Recall) |
| :--- | :--- | :--- | :--- | :--- |
| **Geliştirme Kümesi (Dev)** | 244 Cümle (8 Domain) | %86.5 | %94.7 | — |
| **Görülmemiş Küme (Heldout)** | 113 Cümle (Sağlık & Otomotiv) | %50.0 | %87.6 | — |
| **Çelişki Tespiti (Conflicts)** | 50 Çift (153 Cümle) | — | — | **%98.0** (Precision: %94.2) |

---

## 1. Geliştirme Veri Kümesi Performansı (Dev Corpus)

Geliştirme veri kümesi, projenin üzerinde çalıştırılarak optimize edildiği 8 farklı sektöre ait **244 Türkçe gereksinim cümlesinden** oluşmaktadır.

* **Toplam Cümle:** 244
* **Gereksinim Sınıflandırma Başarısı (FR/NFR):** %94.7 (231 / 244 doğru tahmin)
* **Aktör Tanıma (NER) Başarısı:**
  * **Precision (Hassasiyet):** %92.4
  * **Recall (Duyarlılık):** %81.2
  * **F1-Skoru:** %86.5

### Sektörel (Domain) Kırılım Tablosu

| Sektör (Domain) | Cümle Sayısı | Sınıflandırma Doğruluğu | Aktör NER Hassasiyeti | Aktör NER Duyarlılığı |
| :--- | :---: | :---: | :---: | :---: |
| **Bankacılık** | 10 | %100.0 | %100.0 | %100.0 |
| **Kurumsal Portal** | 13 | %100.0 | %100.0 | %100.0 |
| **Eğitim** | 12 | %83.3 | %100.0 | %100.0 |
| **E-Ticaret** | 13 | %100.0 | %83.3 | %71.4 |
| **Mobil Uygulama** | 15 | %86.7 | %0.0 * | %0.0 * |
| **IoT** | 61 | %96.7 | %93.8 | %78.9 |
| **SaaS** | 60 | %95.0 | %90.9 | %83.3 |
| **Oyun** | 60 | %93.3 | %91.3 | %84.0 |

*\* Not: Mobil veri kümesinde beklenen aktör bulunmadığı (boş liste olduğu) için metrik matematiksel olarak %0 çıkmıştır, bu bir hata değildir.*

---

## 2. Görülmemiş Sektör Performansı (Heldout Corpus)

Sistemin hiç görmediği alanlardaki genelleme yeteneğini test etmek amacıyla Sağlık ve Otomotiv (Otonom Sürüş) alanından **113 cümle** koşturulmuştur.

* **Toplam Cümle:** 113 (30 Sağlık + 83 Otomotiv)
* **Sınıflandırma Doğruluğu:** %87.6 (99 / 113 doğru tahmin)
* **Aktör Tanıma (NER) Başarısı:**
  * **Precision (Hassasiyet):** %61.9
  * **Recall (Duyarlılık):** %41.9
  * **F1-Skoru:** %50.0

### Otomotiv Alanındaki Düşüşün Analizi (NER Hatası)
Otomotiv veri kümesinde aktör duyarlılığının (Recall) %41.9 seviyesine gerilemesinin temel sebebi, mevcut NER modülünün (`core/ner.py`) **kural tabanlı sözlük (lemma lookup) eşleştirmelerine bağımlı olmasıdır**. 
* **Örnek Hata:** Cümledeki `radar sensörü` veya `gösterge paneli` aktör olarak beklenirken, sözlükte bu birleşik kelimeler tanımlı olmadığı için yerel Stanza NER modülü sadece `radar` veya `gösterge panel` kelimelerini çekmiş, bu durum metriklerde eşleşme hatası (FP/FN) olarak yazılmıştır.
* **Gelecek Çalışma Önerisi:** NER katmanının kural tabanlı sözlükten kurtarılarak, transformers/BERT tabanlı bir yerel model veya LLM tabanlı bir extractor ile değiştirilmesi gerekmektedir.

---

## 3. Çelişki Tespiti Değerlendirmesi (Conflict Detection)

50 adet kasıtlı olarak birbiriyle çelişen gereksinim çifti ve araya serpiştirilen kontrol (çelişkisiz) cümleleri dahil toplam **153 gereksinim** üzerinde batched LLM analizi uygulanmıştır.

* **Ground Truth Çelişki Çifti:** 50
* **Sistem Tarafından Bulunan Çift:** 52
* **Doğru Tespit (TP - True Positive):** 49
* **Yanlış Alarm (FP - False Positive):** 3
* **Kaçırılan Çelişki (FN - False Negative):** 1

### Başarı Metrikleri
* **Çelişki Yakalama Oranı (Recall / Detection Rate):** **%98.0**
* **Çelişki Doğruluk Oranı (Precision):** **%94.2**
* **F1-Skoru:** **%96.1**
* **Yanlış Alarm Oranı (False Positive Rate):** %5.8

### Detaylı Hata Analizi

#### A. Kaçırılan Çelişki (1 Adet)
* **Çift:** `('REQ_122', 'REQ_123')`
  * `REQ_122`: *"Sistem, tüm kullanıcı arayüzü metinlerini dinamik olarak çevirmelidir."*
  * `REQ_123`: *"Sistem, yalnızca İngilizce ve Türkçe dillerini desteklemelidir."*
* **Neden Kaçtı?** Doğrudan kelime düzeyinde bir zıtlık bulunmamaktadır. Dolaylı bir mantıksal kapsam sınırlandırma çelişkisi olduğu için LLM'in dikkatinden kaçmıştır.

#### B. Yanlış Alarmlar (False Positives - 3 Adet)
1. `('REQ_064', 'REQ_132')`:
   * `REQ_064`: *"Çalışan kendi izin taleplerini sisteme girebilmelidir."*
   * `REQ_132`: *"Sistem, tüm kullanıcıların kendi verilerini düzenlemesine izin vermelidir."*
   * *Açıklama:* Çelişki olmamasına rağmen, LLM yetki yönetimi kapsamından dolayı bunu yanlışlıkla çelişki olarak etiketlemiştir.
2. `('REQ_099', 'REQ_100')` ve `('REQ_099', 'REQ_101')`:
   * `REQ_099` (Şifre uzunluk kısıtı olmaması) ile `REQ_100`/`REQ_101` (Kullanıcı verilerinin güvenli sunucuda barındırılması) arasında güvenlik politikası uyumsuzluğu algılanmıştır.

---

## 4. Pytest Entegrasyon ve Regresyon Testleri

Mekanik ve yazılımsal kararlılığı ölçen birim (unit) ve entegrasyon testlerinin tamamı yeşildir.

* **Toplam Koşturulan Test:** 190 / 190
* **Snapshot Testleri:** 106 / 106
* **Durum:** **Başarılı (Passed)**
* **Çalışma Süresi:** 501.52 saniye (Testler tamamen izole ve stabil çalışmaktadır.)
