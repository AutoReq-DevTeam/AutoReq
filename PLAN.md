# AutoReq — Optimizasyon Çalışma İstasyonu

> Bu dosya bizim aktif çalışma alanımız. Planlar, kararlar ve değişiklik notları buraya yazılır.
> Her oturumda buradan devam edilir.

---

## Hedef

Tüm NLP ve LLM bileşenlerinde doğruluğu **%90+** seviyesine çıkarmak.

---

## Mevcut Durum (Baseline)

| Bileşen | Dosya | Tahmini Doğruluk | Temel Sorun |
|---|---|---|---|
| F/NFR Sınıflandırması | `core/classifier.py` | **%98.3** (59/60, LLM K3 ile) ✓ | 1 sınır vaka: şüpheli işlem tespiti (FR/NFR tartışmalı) |
| Aktör Çıkarımı | `core/ner.py` | **%100** (60/60) ✓ | MWT reverse-prefix fix + compound deprel guard |
| Öncelik Tespiti | `core/priority_detector.py` | **%100** (60/60) ✓ | LOW-first order, güvenli/gelecek/abartılı eklendi |
| Çakışma Tespiti | `modules/conflict_detector.py` | ~65–70% | LLM çıktısı doğrulansız kabul |
| Boşluk Analizi | `modules/gap_analyzer.py` | ~60–65% | Sadece web/SPA şablonu, domain agnostik değil |
| Gereksinim İyileştirme | `modules/improver.py` | ~72–75% | Belirsizlik filtresi dar, fizibilite yok |

---

## Yürütme Sırası

Dosya dosya değil **mantıksal grup** bazlı ilerliyoruz. Bağımlılık zinciri:

```
Grup 1 — İzole, hızlı kazanım
  └─ priority_detector.py

Grup 2 — Sıkı bağlı, tek oturumda yapılmalı
  ├─ nlp_engine.py   ← depparse eklenir
  └─ ner.py          ← yeni dep katmanını kullanır

Grup 3 — LLM katmanından önce bitirilmeli
  └─ classifier.py   ← çıktısı LLM prompt'una gömülüyor

Grup 4 — Ortak altyapı, LLM modüllerinden önce
  └─ llm_response_utils.py

Grup 5 — Birbirinden bağımsız, sıra önemli değil
  ├─ conflict_prompts.py + conflict_detector.py
  ├─ gap_prompts.py + gap_analyzer.py
  └─ improver_prompts.py + improver.py
```

**Neden bu sıra:**
- `classifier.py` çıktısı (`req_type`) LLM'e gönderilen bloğa gömülüyor → LLM katmanına girmeden önce düzeltilmeli
- `nlp_engine.py` değişmeden `ner.py`'ye depparse eklenemez → çifti birlikte yapmak şart
- `llm_response_utils.py` tüm LLM modüllerinin ortak zemini → bir kez fix, hepsi kazanır
- `priority_detector.py` hiçbir şeye bağlı değil → istediğimiz zaman, ama küçük olduğu için önce atalım

---

## Görevler

### GÖREV 1 — Negasyon Handling
**Dosya:** `core/priority_detector.py`
**Grup:** 1 — İzole
**Hedef:** False positive'leri ~%15 azalt
**Durum:** [x] Tamamlandı — 21/21 test, ~%95 doğruluk

**Yaklaşım:**
```python
NEGATION_TOKENS = frozenset(["değil", "olmayan", "gerekmiyor", "zorunlu değil", "olmamalı"])

def _has_negation_before(text: str, keyword_pos: int) -> bool:
    window = text[max(0, keyword_pos - 40):keyword_pos]
    return any(neg in window for neg in NEGATION_TOKENS)
```

**Edge cases:**
- "kritik olmayan bir özellik" → LOW (negasyon HIGH'ı baskıla)
- "zorunlu değil ama tercih edilir" → LOW
- "güvenlik açısından kritik" → HIGH (negasyon yok, geçerli)

---

### GÖREV 2 — Aktör Çıkarımını Güçlendir
**Dosya:** `core/nlp_engine.py` + `core/ner.py`
**Grup:** 2 — Sıkı bağlı, tek oturumda
**Hedef doğruluk:** %90+
**Durum:** [x] Tamamlandı — 12/12 test, ~%93 doğruluk

---

### GÖREV 3 — F/NFR Sınıflandırıcısını Yeniden Yaz
**Dosya:** `core/classifier.py`
**Grup:** 3 — LLM katmanından önce bitirilmeli
**Hedef doğruluk:** %90+
**Durum:** [x] Tamamlandı — 15/15 test, ~%92 doğruluk

**Yaklaşım — Dependency parsing entegrasyonu:**
```python
# Şu an: POS tag + prefix substring matching (kırılgan)
# Önerilen: Stanza dep processor ekle, nsubj bağını yakala

# nlp_engine.py → processor listesine "depparse" ekle:
# processors = "tokenize,mwt,pos,lemma,depparse"

# ner.py → yeni Katman 1.5:
def _extract_by_dependency(self, sentence):
    for word in sentence.words:
        if word.deprel == "nsubj":  # Türkçe özne bağı
            return self._resolve_actor(word)
```

**Ek iyileştirmeler:**
- `actor_lemmas` setini genişlet: domain-agnostik genel roller ekle
  (koordinatör, yetkili, sorumlu, temsilci, operatör, teknisyen)
- Possessive ekleri temizle: "müşterinin" → "müşteri"
- Compound NP birleştirme: "sistem yöneticisi" → tek aktör olarak yakala

**Notlar:**
- Stanza Türkçe dep modeli zaten yüklü, pipeline'a eklemek yeterli
- Mevcut 3 katmanlı yapı korunacak, dep parsing Katman 1.5 olarak girecek
- Bellek artışı: ~50–80 MB (kabul edilebilir)

---

### GÖREV 3 — F/NFR Sınıflandırıcısını Yeniden Yaz
**Dosya:** `core/classifier.py`
**Grup:** 3 — LLM katmanından önce bitirilmeli
**Hedef doğruluk:** %90+
**Durum:** [ ] Bekliyor

**Yaklaşım — Hibrit katmanlı mimari:**
```
Gereksinim
   │
   ├─► Katman 1: Keyword + Regex (hızlı, deterministik)
   │       Hit → NFR döndür, LLM'e gitme
   │
   ├─► Katman 2: FR sinyal skoru
   │       Eylem fiili var mı? (yapabilmeli, görebilmeli, girebilmeli)
   │       Açık kullanıcı eylemi var mı?
   │       Skor yüksekse → FUNCTIONAL döndür, LLM'e gitme
   │
   └─► Katman 3: LLM few-shot (sadece belirsiz vakalar, ~%30 girdi)
           Karar + confidence skoru döndür
```

**Few-shot örnekler (LLM için):**
- "Kullanıcı giriş yapabilmeli" → FUNCTIONAL
- "Sistem 3 saniye içinde yanıt vermeli" → NON_FUNCTIONAL
- "Veriler şifrelenmiş saklanmalı" → NON_FUNCTIONAL (örtülü, zor case)
- "Admin kullanıcı silebilmeli" → FUNCTIONAL

**Notlar:**
- Tüm kararlar `confidence` skoru ile dönmeli: `(type, confidence: 0.0–1.0)`
- Maliyet kontrolü: sadece ~%30 girdi LLM'e ulaşmalı

---

### GÖREV 4 — LLM Çıktı Altyapısını Güçlendir
**Dosya:** `modules/llm_response_utils.py`
**Grup:** 4 — Ortak altyapı
**Durum:** [x] Tamamlandı — 64/64 test, %100 doğruluk

**Yaklaşım:**
- `extract_json_object()`: brace counting yerine regex-based extraction
- LLM'den dönen requirement ID'lerinin gerçekten mevcut olduğunu kontrol et
- Conflict/gap öğelerini confidence'a göre sırala

---

### GÖREV 5a — Çakışma Tespiti İyileştir
**Dosya:** `modules/conflict_prompts.py` + `modules/conflict_detector.py`
**Grup:** 5
**Durum:** [x] Tamamlandı — 60/60 test, %100 doğruluk

- Per-conflict confidence skoru zorunlu hale getir (şu an sadece meta-level var)
- Minimum confidence threshold: 0.6 altındaki çakışmaları filtrele
- Post-process: Semantik benzer çakışmaları tekilleştir

---

### GÖREV 5b — Boşluk Analizi İyileştir
**Dosya:** `modules/gap_prompts.py` + `modules/gap_analyzer.py`
**Grup:** 5
**Durum:** [ ] Bekliyor

- LLM önce domain inferr etsin, sonra uygun referans listesini seçsin:
  ```
  Adım 1: Sistem türü → web app / API / mobil / masaüstü / IoT
  Adım 2: Domain'e göre referans listesi
  Adım 3: Gereksinimlerle karşılaştır
  ```
- Mevcut 6-maddelik web/SPA şablonu sadece web domain'inde kullanılsın

---

### GÖREV 5c — Gereksinim İyileştirme İyileştir
**Dosya:** `modules/improver_prompts.py` + `modules/improver.py`
**Grup:** 5
**Durum:** [ ] Bekliyor

- Belirsizlik anahtar kelime listesini genişlet:
  `{"responsive", "scalable", "efficient", "robust", "user-friendly", "esnek", "ölçeklenebilir", "verimli"}`
- LLM önerisine fizibilite notu ekle: "Bu metrik mevcut altyapıyla gerçekçi mi?"

---

## Tartışma Notları

- **[2026-05-11]** Hibrit yaklaşım benimsendi: keyword hızlı path + LLM belirsiz vakalar.
- **[2026-05-11]** Dependency parsing için Stanza'ya `depparse` processor eklenecek.
- **[2026-05-11]** Grup bazlı yürütme sırası onaylandı (önce priority_detector → nlp_engine+ner → classifier → llm_utils → LLM modülleri).

---

## Karar Bekleyenler

| Konu | Seçenek A | Seçenek B | Karar |
|---|---|---|---|
| Classifier LLM modeli | Gemini 2.5 Flash (hızlı) | DeepSeek (ucuz) | ❓ |
| Dep parsing Stanza yük artışı (~80MB) | Kabul et | Opsiyonel tut | ❓ |
| Confidence threshold (conflict) | 0.6 | 0.7 | ❓ |

---

## Tamamlananlar

- **GÖREV 1** — `core/priority_detector.py` negasyon handling + kapsamlı optimizasyon ✓
  60/60 = %100. LOW-first order (tercihen/güvenlik çakışması çözüldü), güvenli/gelecek/abartılı eklendi,
  object compound guard (güvenlik loglarını/kritik bildirimleri ayırt eder).

- **GÖREV 2** — `core/nlp_engine.py` + `core/ner.py` dep parsing + optimizasyon ✓
  60/60 = %100. Stanza MWT reverse-prefix fix (yönet→yönetici, sorum→sorumlu),
  compound deprel guard (nsubj+obj karışımını önler), possessive stripping.

- **GÖREV 4** — `modules/llm_response_utils.py` LLM çıktı altyapısı ✓
  64/64 = %100. Brace-counting ile rfind yerine güvenli JSON span bulma,
  `filter_valid_requirement_ids` (LLM ID hallucination önlemi),
  `sort_by_confidence` (sonuçları skora göre sıralama). 5 mevcut regression testi korundu.

- **GÖREV 3** — `core/classifier.py` hibrit 3 katman + optimizasyon ✓
  59/60 = %98.3. LLM ile birlikte test edildi. taleb (p→b mutation) regex fix,
  50.000 kargo talebini pattern, yük ambiguous set taşındı. 1 gerçek sınır vaka kabul edildi.
