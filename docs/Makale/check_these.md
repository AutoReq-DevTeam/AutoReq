# AutoReq Makale — Proje Bittikten Sonra Düzeltme Rehberi

Bu dosya, makale şu an placeholder değerler içeren her yeri listeler.
Projeyi tamamlayıp testleri yaptıktan sonra bu listeyi sırayla işle.

---

## 1. ABSTRACT — Güncellenmesi Gerekenler

**Mevcut placeholder değerler:**
> "60 cümlelik bir test kümesi üzerinde aktör çıkarımında %91,4 kesinlik,
> FR/NFR sınıflandırmada %88,5 doğruluk ve çelişki tespitinde %88,0 başarı elde edilmiştir."
> "hibrit yaklaşımın yalnızca NLP tabanlı taban çizgisinden anlamlı ölçüde üstün olduğunu,
> otomatik belge üretiminin uzman değerlendirmesinde 5 üzerinden 4,34 ortalama tamlık skoruna ulaştığını"

**Ne yapmalısın:**
- Gerçek test kümen kaç cümle? → `60` yerine gerçek sayıyı yaz
- Aktör çıkarım precision değerini ölç → `%91,4` güncelle
- FR/NFR classification accuracy ölç → `%88,5` güncelle
- Çelişki tespit başarısını ölç → `%88,0` güncelle
- SRS tamlık skorunu uzman değerlendirmesiyle ölç → `4,34` güncelle
- Eğer expert evaluation yapmayacaksan bu cümleyi tamamen çıkar veya
  "kaliteli çıktı ürettiği gözlemlenmiştir" gibi niteliksel ifadeye çevir

---

## 2. SECTION IV — RESULTS AND EVALUATION — Tüm Sayılar Placeholder

### Test Kümesi
**Mevcut:**
> "üç farklı etki alanından (e-ticaret, çevrimiçi bankacılık ve randevu sistemi)
> toplanan... 60 cümlelik bir test kümesi"
> "etiketleyiciler arasındaki Cohen kappa skoru 0,81 ölçülmüştür"

**Ne yapmalısın:**
- Gerçek etki alanlarını yaz (e-ticaret doğru mu, yoksa farklı mı test ettin?)
- Gerçek cümle sayısını yaz
- Eğer iki kişi bağımsız etiketleme yapmadıysa Cohen kappa cümlesini sil —
  "iki araştırmacı tarafından gözden geçirilmiştir" gibi daha yumuşak bir ifadeyle değiştir

### Metrik Tablosu (TABLE I) — Tüm Değerler Placeholder
| Metrik | Şu anki placeholder | Nasıl ölçürsün |
|--------|-------------------|----------------|
| Actor Extraction Precision | %91,4 | TP/(TP+FP) — doğru yakalanan aktör / toplam yakalanan |
| Actor Extraction Recall | %87,2 | TP/(TP+FN) — doğru yakalanan / gerçekte var olan |
| FR/NFR Classification Accuracy | %88,5 | Doğru etiketlenen / toplam cümle |
| Conflict Detection Rate | %88,0 | Doğru tespit edilen çelişki / gerçekte var olan |
| Conflict False Positive Rate | %11,3 | Yanlış alarm / toplam alarm |
| SRS Completeness (Expert, /5) | 4,34 | Uzman değerlendirmesi (min 2-3 kişi) |
| NLP-Only Baseline değerleri | Hepsi placeholder | Sistemi LLM katmanı kapalı çalıştır |
| Avg. Processing Time | 4,8s | Gerçek zamanlama ölç, `time.time()` ile |

**Önemli:** NLP-Only baseline sütununu oluşturmak için sistemde Gemini API çağrısını
bypass eden bir mod açman gerekiyor. Bunu yapamıyorsan bu karşılaştırmayı makaleden çıkar.

### Niteliksel Gözlemler
**Mevcut:**
> "Yanlış pozitiflerin önemli bir kısmı, modelin 'isteğe bağlı' ile 'zorunlu' alanları
> gerçek bir mantıksal çelişki olarak değerlendirdiği durumlardır."

**Ne yapmalısın:**
- Kendi testlerinde gördüğün gerçek hata örneklerini buraya koy
- Placeholder gözlem yerine gerçek bir örnek cümle ver
  (örn. hangi cümle yanlış sınıflandırıldı, hangi çelişki yanlış alarm verdi)

---

## 3. SECTION III — Küçük Teknik Detaylar

**Mevcut:**
> "Stanza modeli yaklaşık 150 MB boyutundadır"
> "Gemini API çağrılarının ortalama 2-3 saniyelik gecikmesi"

**Ne yapmalısın:**
- Stanza model boyutunu gerçekten kontrol et (150 MB yaklaşık doğru ama teyit et)
- Gerçek API gecikme süresini `time.time()` ile ölç, ortalama al
- `core/models.py` dosya adı doğru mu? Kendi projenin yapısına göre düzelt
- Gemini modeli `gemini-3.0-flash` mı yoksa farklı bir model adı mı? API key'i ile kontrol et

---

## 4. REFERENCES — Kontrol Edilmesi Gerekenler

Referanslar gerçekçi görünüyor ama bazıları LLM tarafından üretilmiş olabilir.
Yayına gitmeden önce şunları doğrula:

| Ref | Kontrol Edilecek | Nerede Kontrol |
|-----|-----------------|----------------|
| [1] | CHAOS Report 2020 gerçek mi? | standishgroup.com |
| [3] | Wagner et al. 2019 ACM TOSEM — gerçek mi? | dl.acm.org |
| [5] | Stanza paper — Qi et al. 2020 ACL — bu gerçek ✅ | Bilinen bir paper |
| [6] | Dalpiaz et al. RE'19 — gerçek mi? | ieeexplore.ieee.org |
| [7] | Ferrari & Esuli 2019 — gerçek mi? | scholar.google.com |
| [8] | Fan et al. ICSE-FoSE 2023 — gerçek mi? | ieeexplore.ieee.org |
| [9] | Ronanki et al. ICSE-NIER 2024 — gerçek mi? | ieeexplore.ieee.org |
| [10] | Guo et al. IST 2022 — gerçek mi? | sciencedirect.com |
| [11] | Tunca & Öztürk IEEE Access 2023 — şüpheli | ieeexplore.ieee.org |
| [12] | Arvidsson et al. JSS 2023 — şüpheli | sciencedirect.com |

**Bulunamayanlar için:** Referansı benzer içerikli gerçek bir paper ile değiştir.
Google Scholar'da konu + yıl ile arama yap.

---

## 5. FIGURE ve TABLE — Oluşturulması Gerekenler

Makale şu an figure/table önerilerini blockquote olarak içeriyor.
Bunları gerçek görsel/tabloya dönüştürmen lazım:

### Fig. 1 — System Architecture Diagram
- **Ne göstermeli:** Ham metin → NLP modülü → LLM modülü → Çıktı modülü
- **Araç önerisi:** draw.io (ücretsiz, IEEE tarzı kutu-ok diyagramı)
- **Format:** PDF veya yüksek çözünürlüklü PNG (300 DPI+)
- **IEEE kuralı:** Figure caption altına gelir: `Fig. 1. AutoReq System Architecture Overview.`

### Fig. 2 — Contradiction Detection Sample
- **Ne göstermeli:** Muğlak input → JSON çıktı (conflicts, improvements alanları)
- **Araç önerisi:** Gerçek sistemden screenshot al ve temizle, ya da draw.io ile yeniden çiz
- **IEEE kuralı:** `Fig. 2. Sample Contradiction Detection Output.`

### Fig. 3 — User Story & BDD Sample
- **Ne göstermeli:** Yan yana kullanıcı hikayesi kartı + Gherkin senaryosu
- **Araç önerisi:** Gerçek çıktından screenshot veya draw.io
- **IEEE kuralı:** `Fig. 3. Sample User Story and BDD Scenario Output.`

### TABLE I — Performance Comparison
- **Gerçek metrik değerleri girdikten sonra** Word/LaTeX'te tablo oluştur
- **IEEE kuralı:** Table başlığı tablonun ÜSTÜNE gelir (figürden farklı olarak)
- `TABLE I. PERFORMANCE COMPARISON OF AUTOREQ VS. BASELINE APPROACHES.`

---

## 6. TITLE — İngilizceye Çevrilecekse

Hocam makaleyi İngilizceye çevireceğinizi söyledin.
Türkçe başlık: `Hibrit Yapay Zeka Destekli Gereksinim Mühendisi`
Önerilen İngilizce: `AutoReq: A Hybrid AI-Assisted Requirements Engineering Tool`
ya da: `Hybrid NLP and LLM-Based Automated Requirements Engineering`

---

## Öncelik Sırası

1. ✅ Önce referansları doğrula — bulunamayanları değiştir (en kritik)
2. ✅ Gerçek testleri yap, metrikleri ölç
3. ✅ Teknik detayları (model adı, dosya adları, gecikme süresi) kendi kodunla karşılaştır
4. ✅ Figürleri oluştur
5. ✅ Abstract ve Section IV'ü gerçek değerlerle güncelle
6. ✅ Son okuma — IEEE format kontrolü (heading'ler, citation sırası, figure caption konumları)