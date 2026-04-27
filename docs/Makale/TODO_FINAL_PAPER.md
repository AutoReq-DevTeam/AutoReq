# TODO — Makalenin Final Sürümü İçin Yapılacaklar

> **Amaç:** `docs/Makale/YGA.md` dosyasındaki **placeholder (uydurma) sayılar ve iddialar**, proje tamamen bittikten sonra **gerçek ölçüm sonuçlarıyla** değiştirilecek. Bu dosya, o aşamada hangi yerlerin hangi verilerle güncelleneceğini ve ölçümlerin nasıl yapılacağını adım adım anlatır.
>
> **Son kontrol tarihi:** 2026-04-27
> **Sorumlu:** [doldurulacak]
> **Hedef tamamlanma:** [doldurulacak]

---

## 0. Ön Koşullar (Ölçümden Önce Tamamlanması Gerekenler)

Aşağıdaki bileşenler şu an `NotImplementedError` veya stub durumdadır. Ölçümler **bunlar bitmeden** anlamlı olmaz:

- [ ] `modules/gap_analyzer.py` — `GapAnalyzer.analyze()` implement edilecek
- [ ] `modules/improver.py` — `RequirementImprover.improve()` implement edilecek
- [ ] `outputs/story_generator.py` — `StoryGenerator` implement edilecek
- [ ] `outputs/bdd_generator.py` — `BDDGenerator` implement edilecek
- [ ] `outputs/srs_generator.py` — Statik PDF yerine **dinamik veriyle** doldurulacak (şu an sadece template)
- [ ] `app.py` → `process_text()` içinde `ConflictDetector` çağrısı **bağlanacak** (şu an `conflicts=[]` dönüyor)
- [ ] `core/classifier.py` — NFR keyword listesinden `"kullanıcı"` ve `"şifre"` çıkarılacak veya bağımlılık örüntüsüyle iyileştirilecek (yanlış pozitif sorunu)

> Bu bileşenler bitmeden Bölüm IV'teki "User Story tamlığı" veya "BDD üretimi" gibi metrikler ölçülemez.

---

## 1. Test Verisi Hazırlığı

### 1.1 `data/samples/test_set.csv` oluştur

Şema:

```
id,text,actors,objects,req_type
REQ_001,"Kullanıcı sisteme e-posta ve şifre ile giriş yapabilmelidir.","kullanıcı","e-posta;şifre",FUNCTIONAL
REQ_002,"Sistem 1 saniye içinde yanıt vermelidir.","sistem","",NON_FUNCTIONAL
...
```

- **En az 60 cümle** topla. Üç etki alanından dengeli dağılım önerilir:
  - 20 cümle e-ticaret (sepet, ödeme, ürün, sipariş)
  - 20 cümle çevrimiçi bankacılık (havale, hesap, doğrulama)
  - 20 cümle randevu / rezervasyon sistemi
- Cümlelerin **iki kişi tarafından bağımsız** etiketlenmesi gerekir (Cohen kappa hesabı için).
- Anlaşmazlık olan cümlelerde üçüncü bir kişi karar versin.

### 1.2 `data/samples/conflict_pairs.csv` oluştur

Şema:

```
pair_id,req_id_a,req_id_b,is_conflict,conflict_type,reason
P001,REQ_001,REQ_015,true,LOGICAL,"REQ_001 girişe izin verir, REQ_015 girişi yasaklar"
P002,REQ_002,REQ_007,false,,
...
```

- **15-20 gerçekten çelişen çift** + **30-40 çelişmeyen çift** = ~50 çift toplam
- `conflict_type` değerleri: `LOGICAL`, `SCOPE_OVERLAP`, `MISSING_PREREQ`

### 1.3 `data/samples/srs_eval_inputs/` klasörü

İçine 5-10 farklı kısa müşteri metni koy (her biri 8-15 cümlelik). Bu metinler **uzman değerlendirmesinde** SRS üretimi için girdi olarak kullanılacak.

---

## 2. Değerlendirme Betiği

`scripts/evaluate.py` dosyası oluştur. Yapması gerekenler:

```python
# scripts/evaluate.py iskeleti

import csv
from core.preprocessor import TextPreprocessor
from core.classifier import RequirementClassifier
from core.ner import EntityRecognizer
from modules.conflict_detector import ConflictDetector
from modules.llm_client import LLMClient

def evaluate_classification(test_set):
    # FR/NFR accuracy: doğru tahmin sayısı / toplam
    ...

def evaluate_entity_extraction(test_set):
    # Aktör ve nesne için precision / recall
    # TP = ground truth ∩ tahmin
    # FP = tahmin - ground truth
    # FN = ground truth - tahmin
    ...

def evaluate_conflict_detection(conflict_pairs):
    # Detection rate = doğru tespit edilen çelişkili çift / toplam çelişkili çift
    # False positive rate = yanlış tespit edilen / toplam çelişkisiz çift
    ...

def measure_processing_time(test_set):
    # Her dokümanı baştan sona geçir, ortalama saniye
    # Hem NLP-only hem hibrit modu için ayrı ayrı
    ...

if __name__ == "__main__":
    # Tüm metrikleri hesapla, sonuçları reports/evaluation_results.json'a yaz
```

Çıktı dosyası: `reports/evaluation_results.json`

---

## 3. Uzman Değerlendirmesi (SRS Tamlık Skoru)

- 3 değerlendirici bul (öğretim üyesi, sınıf arkadaşı, mezun mühendis vb.)
- Her birine `data/samples/srs_eval_inputs/` içindeki 5-10 metni AutoReq'le SRS'e çevirip ver
- Şu rubrik üzerinden 5'lik ölçekte puanlamalarını iste:
  - **Tamlık (Completeness):** ISO/IEC/IEEE 29148'in zorunlu bölümleri var mı?
  - **Doğruluk (Correctness):** Üretilen gereksinimler girdiyle uyumlu mu?
  - **Okunabilirlik (Readability):** Belge profesyonel bir SRS gibi okunuyor mu?
- Her metin için ortalama, sonra tüm metinlerin ortalaması = final skor

> Not: Karşılaştırma için aynı 5-10 metni **NLP-only** modda da çalıştır ve ayrıca puanlatma yap.

---

## 4. Makalede Güncellenecek Yerler

> Aşağıdaki tüm bölümlerde **şu anki sayılar uydurmadır** ve gerçek ölçüm sonuçlarıyla değiştirilmelidir.

### 4.1 Abstract (`YGA.md` ~ satır 16)

**Şu anki cümle:**
> "60 cümlelik bir test kümesi üzerinde aktör çıkarımında %91,4 kesinlik, FR/NFR sınıflandırmada %88,5 doğruluk ve çelişki tespitinde %88,0 başarı elde edilmiştir. Sonuçlar... uzman değerlendirmesinde 5 üzerinden 4,34 ortalama tamlık skoruna ulaştığını ortaya koymaktadır."

**Yapılacak:** Cümleyi `evaluation_results.json` içinden gelen gerçek değerlerle yeniden yaz. Test kümesinin gerçek boyutu 60 değilse onu da güncelle.

### 4.2 Bölüm IV — RESULTS AND EVALUATION (tamamı)

Bu bölümün **her sayısal iddiası uydurmadır**. Sırayla güncellenecek:

| Konum | Şu Anki Değer | Kaynak |
|---|---|---|
| Test kümesi boyutu | 60 cümle | `test_set.csv` satır sayısı |
| Etki alanı sayısı | 3 (e-ticaret, bankacılık, randevu) | Verinin gerçek dağılımı |
| Cohen kappa | 0,81 | İki etiketleyici arasında hesapla |
| Aktör precision | %91,4 | `evaluate_entity_extraction` çıktısı |
| Aktör recall | %87,2 | aynı |
| Nesne precision | %84,6 | aynı |
| Nesne recall | %81,0 | aynı |
| FR/NFR accuracy | %88,5 | `evaluate_classification` çıktısı |
| Çelişki detection rate | %88,0 | `evaluate_conflict_detection` çıktısı |
| Çelişki false positive rate | %11,3 | aynı |
| SRS tamlık skoru | 4,34 / 5 | Uzman ortalaması |

### 4.3 Tablo I — Karşılaştırma Tablosu

Tüm satırlar uydurmadır. Gerçek ölçümle değiştir:

| Metric | NLP-Only Baseline | AutoReq (Hybrid) |
|---|---|---|
| Actor Extraction Precision (%) | ?? | ?? |
| Actor Extraction Recall (%) | ?? | ?? |
| FR/NFR Classification Accuracy (%) | ?? | ?? |
| Conflict Detection Rate (%) | 0,0 (NLP yapamaz) | ?? |
| Conflict False Positive Rate (%) | — | ?? |
| SRS Completeness (Expert, /5) | ?? | ?? |
| Avg. Processing Time (s/document) | ?? | ?? |

**NLP-only baseline nasıl çalıştırılır:**
- `evaluate.py`'a bir flag ekle: `--mode nlp_only`
- Bu modda `ConflictDetector` ve LLM tabanlı iyileştirme çağrılmasın
- Aynı metriği iki kez ölç, tabloyu doldur

### 4.4 Bölüm IV'teki Niteliksel Gözlemler

Şu anki metinde "yanlış pozitiflerin önemli bir kısmı isteğe bağlı / zorunlu alan ayrımından kaynaklanıyor" gibi spesifik gözlemler var. **Gerçek ölçümden sonra bunları doğrula:**

- Yanlış pozitiflerin **gerçek nedenlerini** ölçüm verisinden çıkar
- "kullanıcı / şifre" yanlış pozitif iddiasını gerçek hatalı sınıflandırma örnekleriyle destekle
- Eğer bulduğun nedenler farklıysa metni yeniden yaz

### 4.5 Bölüm V — CONCLUSION

**Şu anki cümle:**
> "...sınıflandırma ve aktör çıkarımında %88-91 aralığında performans gösterdiğini..."

Bu aralığı gerçek değerlere göre güncelle. Gemini gecikmesi 2-3 saniye iddiasını da gerçek ölçümle doğrula (`measure_processing_time` çıktısı).

---

## 5. İsteğe Bağlı İyileştirmeler

Süre kalırsa makaleyi daha güçlü kılacak eklemeler:

- [ ] **Hata analizi** — Bölüm IV'e "Error Analysis" alt başlığı ekle: en sık karşılaşılan 3-4 hata türünü örneklerle göster
- [ ] **Kappa skorunun yorumu** — 0,81 yerine gerçek kappa hesaplandıktan sonra değeri yorumla (Landis & Koch ölçeği)
- [ ] **İstatistiksel anlamlılık** — Hibrit vs. NLP-only farkı için McNemar testi veya bootstrap güven aralığı
- [ ] **Gerçek figürleri çiz** — Şu an Fig. 1, Fig. 2, Fig. 3 sadece blockquote öneri olarak duruyor. Final sürümde:
  - Fig. 1: drawio veya Mermaid ile mimari diyagram
  - Fig. 2: gerçek bir input/output ekran görüntüsü
  - Fig. 3: gerçek user story + Gherkin örneği ekran görüntüsü

---

## 6. Final Kontrol Listesi (Submit Etmeden Önce)

- [ ] Abstract'taki tüm sayılar gerçek
- [ ] Bölüm IV'teki tüm sayılar gerçek
- [ ] Tablo I gerçek değerlerle dolu
- [ ] `data/samples/test_set.csv` repository'de mevcut ve gitignore'lanmamış
- [ ] `scripts/evaluate.py` çalışıyor ve aynı sayıları üretebiliyor (tekrarlanabilirlik)
- [ ] `reports/evaluation_results.json` commit'lenmiş
- [ ] Üç figür gerçekten çizilmiş ve PDF'e gömülmüş
- [ ] Tüm `[N]` referansları metinde geçiyor (orphan referans yok)
- [ ] Yazar bilgileri ve e-postalar doğru
- [ ] Word count 2 500-3 500 aralığında
- [ ] IEEE A4 conference şablonuna LaTeX/Word'de aktarıldı

---

## 7. Notlar

- Gerçek ölçümleri yaptıktan sonra elde edilen sayıların **placeholder'a yakın çıkmasını beklemeyin.** Aktör çıkarımı %75 de çıkabilir, %95 de. Her iki durum da makale için kabul edilebilir — yeter ki dürüstçe raporlanmış olsun.
- Eğer bir metrik beklenmedik biçimde düşük çıkarsa (örn. çelişki tespiti %50), bunu gizlemek yerine **Bölüm IV'ün limitations kısmında** açık şekilde tartışın. Hakemler düşük ama dürüst sayıları, yüksek ama şüpheli sayılara tercih eder.
- Final ölçüm bittiğinde bu dosyanın en üstündeki tüm checkboxlar işaretlenmiş olmalı, sonra dosya `docs/Makale/archive/` altına taşınabilir.
