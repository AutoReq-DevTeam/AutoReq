# AutoReq — Checkpoint 5
## Demo, Kanıt, Akademik Çıktı

AutoReq Devs

---

## Çalışan Demo (MVP)

- Streamlit arayüzü, tek `process_text()` girişi
- Türkçe paydaş metni → 4 artefakt tek tıkla
- SRS (PDF/DOCX) · User Story · Gherkin BDD · Backlog (XLSX)
- Lemma tabanlı aktör çıkarımı + dependency-parse ikinci geçiş
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

ConflictDetector tipli çelişkileri, GapAnalyzer eksik akışları raporluyor.

![Çelişki sonuçları](../results_conflicts_screen.png)

---

## Demo — 5. Dışa Aktarma

Tek geçişten 4 artefakt: SRS (PDF/DOCX) · User Story · Gherkin · Backlog.

![Dışa aktarma](../export_screen.png)

---

## Kanıt — Geliştirme Korpusu (63 cümle / 5 alan)

| Ölçüt | Sonuç |
|---|---|
| Aktör — Precision | 89.1% |
| Aktör — Recall | 82.2% |
| FR/NFR sınıflandırma | 90.5% |
| Çelişki tespiti | 100.0% |
| Yanlış pozitif (çelişki) | 0.0% |

---

## Kanıt — Genelleme (Sağlık, 30 cümle held-out)

Geliştirme ve optimizasyon dışında tutuldu; sistem bu alanı hiç görmedi.

| Ölçüt | Sonuç |
|---|---|
| FR/NFR doğruluğu | 96.7% |
| Aktör recall | 90.5% |
| Aktör F1 | 65.5% |

KVKK · SLA · tıbbi veri şifreleme gibi NFR örüntüleri yakalandı.

---

## Kanıt — Ablation

- LLM modülleri kapalı → çelişki tespiti **%0**
- NLP-yalnız: **0.84 sn/cümle**
- Hibrit: **3.64 sn/cümle**

LLM katmanı mantıksal analiz için vazgeçilmez; gecikme tek doküman kullanımında sorun değil.

---

## Akademik Paket

- IEEE formatında tam makale taslağı
- Abstract · İlgili Çalışmalar · Mimari · Değerlendirme · Sonuç
- 11 referans, 4 figür
- Held-out sağlık korpusu ile genelleme deneyi
- Karşılaştırma tablosu ile literatürdeki konum

---

## Özet

Gereksinim hataları, yazılım projelerinin başarısızlığında başlıca nedenlerden biridir; paydaş görüşmelerini açık ve doğrulanabilir dokümanlara çevirme süreci ise yıllardır temelde değişmedi. Bu çalışmada **Türkçe** girdileri uçtan uca otomatik işleyen **AutoReq** pipeline'ı sunulmaktadır — mevcut araçların büyük çoğunluğunun Türkçeyi desteklememesi göz ardı edilen bir boşluktur.

Sistem üç katmandan oluşur: Stanza tabanlı önişleme (cümle bölme, aktör/iş nesnesi çıkarımı, FR/NFR etiketleme); Gemini 2.5 Flash üzerinden paralel çalışan üç LLM modülü (ConflictDetector, GapAnalyzer, RequirementImprover); ve **ISO/IEC/IEEE 29148** uyumlu SRS, kullanıcı hikâyeleri, Gherkin BDD senaryoları ile ürün backlog'unu tek geçişte üreten üretim katmanı.

Beş alanı kapsayan 63 cümlelik geliştirme korpusunda aktör çıkarımında **%89.1 precision / %82.2 recall**, **%90.5 FR/NFR doğruluğu**, **%100 çelişki tespiti** ve **%0 yanlış pozitif** elde edilmiştir. Ayrı tutulan 30 cümlelik sağlık korpusunda FR/NFR doğruluğu **%96.7**'ye, aktör recall'u **%90.5**'e ulaşmıştır.

---

## Teşekkürler
