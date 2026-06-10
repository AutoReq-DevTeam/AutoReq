# AutoReq — Kontrol Noktası 5
## Demo, Kanıt, Akademik Çıktı

AutoReq Geliştirici Ekibi

---

## Çalışan Demo (MVP)

- Streamlit arayüzü, tek `process_text()` girişi
- Türkçe paydaş metni → Tek tıkla 4 farklı artefakt üretimi
- SRS (PDF/DOCX) · Kullanıcı Hikâyeleri · Gherkin BDD · Backlog (XLSX)
- Lemma tabanlı aktör çıkarımı + dependency-parse (özne odaklı `nsubj` filtrelemeli) ikinci geçiş
- Yerel KVKK maskeleme katmanı (T.C. Kimlik No ve İsim gizleme)
- Bellek içi belge üretimi (`io.BytesIO`) sayesinde eşzamanlı çakışmaların önlenmesi
- 3 katmanlı FR/NFR: fonksiyonel fiil → NFR regex → LLM fallback
- 3 LLM modülü paralel: ConflictDetector · GapAnalyzer · RequirementImprover

---

## Demo — 1. Giriş Ekranı

Paydaş metninin yapıştırıldığı Streamlit arayüzü.

![Giriş ekranı](../input_screen.png)

---

## Demo — 2. Analiz Ekranı

Stanza önişleme + 3 LLM modülünün paralel çalıştığı analiz adımı.

![Analiz ekranı](../analysis_screen.png)

---

## Demo — 3. Gereksinim Sonuçları

Cümle bazında aktör, iş nesnesi, FR/NFR etiketi ve iyileştirilmiş ifade.

![Gereksinim sonuçları](../results_req_screen.png)

---

## Demo — 4. Çelişki & Boşluk Sonuçları

ConflictDetector tipli çelişkileri, GapAnalyzer eksik akışları (domain kontrol listeleri enjeksiyonlu) raporluyor.

![Çelişki sonuçları](../results_conflicts_screen.png)

---

## Demo — 5. Dışa Aktarma

Tek geçişten 4 artefakt: ISO 29148 SRS (PDF/DOCX) · User Story · Gherkin · Backlog.

![Dışa aktarma](../export_screen.png)

---

## Kanıt — Geliştirme Korpusu (63 Cümle / 5 Alan)

| Ölçüt | Sonuç |
|---|---|
| Aktör — Precision | %36.7 |
| Aktör — Recall | %73.3 |
| Aktör — F1 Skoru | %48.9 |
| FR/NFR Sınıflandırma Doğruluğu | %92.1 |
| Çelişki Tespiti (Recall) | %100.0 (TP: 5, FN: 0) |
| Çelişki Tespiti Kesinlik (Precision) | %83.3 (FP: 1) |
| Yanlış Pozitif Oranı (FPR) | %16.7 |

---

## Kanıt — Genelleme (Sağlık, 30 Cümle Held-out)

Geliştirme ve optimizasyon süreçleri dışında tutuldu; sistem bu alanı ilk kez testte gördü.

| Ölçüt | Sonuç |
|---|---|
| FR/NFR Doğruluğu | %96.7 |
| Aktör Precision | %50.0 |
| Aktör Recall | %78.9 |
| Aktör F1 Skoru | %61.2 |

KVKK uyumluluğu · SLA hedefleri · tıbbi veri şifreleme gibi alana özgü NFR örüntüleri başarıyla yakalandı.

---

## Kanıt — Ablation

- LLM modülleri kapalı → Çelişki tespiti **%0**
- NLP-yalnız: **0.68 sn/cümle**
- Hibrit (LLM fallback dahil ortalama): **1.15 sn/cümle**
- LLM Fallback (Layer 3) işletilen cümleler: **2.45 sn/cümle**

LLM katmanı mantıksal analiz için vazgeçilmezdir; oluşan ek gecikme tekil belge kullanımında kullanıcı deneyimini etkilememektedir.

---

## Akademik Paket

- IEEE formatında tam Türkçe makale taslağı (`docs/Makale/article_TR.txt`)
- Abstract · İlgili Çalışmalar · Mimari · Değerlendirme · Sonuç
- 11 referans, 4 figür ve 2 metrik tablosu
- Held-out sağlık korpusu ile genelleme deneyi
- Karşılaştırma tablosu ile literatürdeki konumun belirlenmesi

---

## Özet

Gereksinim hataları, yazılım projelerinin başarısızlığında başlıca nedenlerden biridir; paydaş görüşmelerini açık ve doğrulanabilir dokümanlara çevirme süreci ise uzun yıllardır temelde değişmedi. Bu çalışmada **Türkçe** girdileri uçtan uca otomatik işleyen **AutoReq** boru hattı sunulmaktadır — mevcut araçların büyük çoğunluğunun Türkçeyi desteklememesi literatürde göz ardı edilen bir boşluktur.

Sistem üç katmandan oluşur: Stanza tabanlı önişleme (cümle bölme, Türkçe küçük harfe dönüştürme, KVKK maskeleme, aktör/iş nesnesi çıkarımı, FR/NFR etiketleme); Gemini 2.5 Flash üzerinden paralel çalışan üç LLM modülü (ConflictDetector, GapAnalyzer, RequirementImprover); ve **ISO/IEC/IEEE 29148** uyumlu SRS, kullanıcı hikâyeleri, Gherkin BDD senaryoları ile ürün backlog'unu tek geçişte üreten üretim katmanı.

Beş alanı kapsayan 63 cümlelik geliştirme korpusunda **%92.1 FR/NFR doğruluğu**, aktör çıkarımında **%36.7 precision / %73.3 recall** ve **%100 çelişki tespiti** (%83.3 kesinlik, TP=5, FP=1) elde edilmiştir. Ayrı tutulan 30 cümlelik sağlık korpusunda FR/NFR doğruluğu **%96.7**'ye, aktör duyarlılığı ise **%78.9**'a (%50.0 kesinlik) ulaşmıştır.

---

## Teşekkürler
