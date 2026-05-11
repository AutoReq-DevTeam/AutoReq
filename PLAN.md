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
| F/NFR Sınıflandırması | `core/classifier.py` | ~65–70% | Keyword-only, ML yok, bağlam körü |
| Aktör Çıkarımı | `core/ner.py` | ~78–82% | Hardcoded sözlük, dep parsing yok |
| Öncelik Tespiti | `core/priority_detector.py` | ~70–75% | Negasyon görmez ("gerekli değil" → HIGH) |
| Çakışma Tespiti | `modules/conflict_detector.py` | ~65–70% | LLM çıktısı doğrulansız kabul |
| Boşluk Analizi | `modules/gap_analyzer.py` | ~60–65% | Sadece web/SPA şablonu, domain agnostik değil |
| Gereksinim İyileştirme | `modules/improver.py` | ~72–75% | Belirsizlik filtresi dar, fizibilite yok |

---

## Öncelikli İyileştirme Planı

### GÖREV 1 — F/NFR Sınıflandırıcısını Yeniden Yaz
**Dosya:** `core/classifier.py`
**Hedef doğruluk:** %90+
**Durum:** [ ] Planlandı

**Yaklaşım — Hibrit katmanlı mimari:**
```
Gereksinim
   │
   ├─► Katman 1: Keyword + Regex (hızlı, deterministik)
   │       Hit → NFR döndür (kesin, LLM'e gitme)
   │
   ├─► Katman 2: Belirsizlik skoru hesapla
   │       Açık FR işaretleri var mı? (eylem fiili, kullanıcı eylemi)
   │       Açık NFR işaretleri var mı? (metrik, sayısal eşik)
   │
   └─► Katman 3 (sadece belirsiz vakalarda): LLM few-shot classification
           Sistem promptu: "Bu gereksinim fonksiyonel mi yoksa fonksiyonel dışı mı?"
           Örnek çiftler → güvenilir karar
```

**Önerilen few-shot örnekler (LLM için):**
- "Kullanıcı giriş yapabilmeli" → FUNCTIONAL
- "Sistem 3 saniye içinde yanıt vermeli" → NON_FUNCTIONAL
- "Veriler şifrelenmiş saklanmalı" → NON_FUNCTIONAL (örtülü, zor case)
- "Admin kullanıcı silebilmeli" → FUNCTIONAL

**Notlar:**
- LLM yalnızca keyword ve regex'in çözemediği vakalara girmeli
- Tüm kararlar `confidence` skoru ile dönmeli: `(type, confidence: 0.0-1.0)`
- Maliyet kontrolü için: sadece `~30%` girdi LLM'e ulaşmalı

---

### GÖREV 2 — Aktör Çıkarımını Güçlendir
**Dosya:** `core/ner.py`
**Hedef doğruluk:** %90+
**Durum:** [ ] Planlandı

**Yaklaşım — Dependency parsing entegrasyonu:**
```python
# Şu an: POS tag + prefix substring matching (kırılgan)
# Önerilen: Stanza dep processor ekle, nsubj bağını yakala

# nlp_engine.py'de pipeline'a "depparse" ekle:
# processors = "tokenize,mwt,pos,lemma,depparse"

# ner.py'de yeni katman:
def _extract_by_dependency(self, sentence):
    for word in sentence.words:
        if word.deprel == "nsubj":  # Türkçe özne
            return self._resolve_actor(word)
```

**Ek iyileştirmeler:**
- `actor_lemmas` setini genişlet: domain-agnostik genel roller ekle
  (koordinatör, yetkili, sorumlu, temsilci, operatör, teknisyen)
- Possessive ekleri temizle: "müşterinin" → "müşteri"
- Compound NP birleştirme: "sistem yöneticisi" → tek aktör olarak yakala

**Notlar:**
- Stanza Türkçe dep modeli mevcut, sadece pipeline'a eklenmesi gerekiyor
- `get_shared_stanza_pipeline()` içinde processor listesi güncellenecek
- Mevcut 3 katmanlı yapı korunacak, dep parsing Katman 1.5 olarak girecek

---

### GÖREV 3 — Negasyon Handling (Priority Detector)
**Dosya:** `core/priority_detector.py`
**Hedef:** False positive'leri ~%15 azalt
**Durum:** [ ] Planlandı

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

### GÖREV 4 — LLM Prompt Kalitesini Artır
**Dosya:** `modules/conflict_prompts.py`, `modules/gap_prompts.py`, `modules/improver_prompts.py`
**Durum:** [ ] Planlandı

**4a — Çakışma tespiti (`conflict_prompts.py`):**
- Per-conflict confidence skoru zorunlu hale getir (şu an sadece meta-level var)
- Minimum confidence threshold: 0.6 altındaki çakışmaları filtrele
- Post-process: Semantic benzer çakışmaları tekilleştir

**4b — Boşluk analizi (`gap_prompts.py`):**
- Referans şablonu statik değil, **LLM önce domain inferr etsin:**
  ```
  Adım 1: "Bu hangi tür sistem? (web app / API / mobil / masaüstü / IoT)"
  Adım 2: Domain'e göre uygun referans listesini seç
  Adım 3: Gereksinimlerle karşılaştır
  ```
- Mevcut 6-maddelik web/SPA şablonu sadece web domain'inde kullanılsın

**4c — Gereksinim iyileştirme (`improver_prompts.py`):**
- Belirsizlik anahtar kelime listesini genişlet:
  `{"responsive", "scalable", "efficient", "robust", "user-friendly", "esnek", "ölçeklenebilir", "verimli"}`
- LLM önerisine fizibilite notu ekle: "Bu metrik mevcut altyapıyla gerçekçi mi?"

---

### GÖREV 5 — LLM Çıktı Validasyonu
**Dosya:** `modules/llm_response_utils.py`, `modules/conflict_detector.py`, `modules/gap_analyzer.py`
**Durum:** [ ] Planlandı

**Yaklaşım:**
- LLM'den dönen requirement ID'lerinin gerçekten mevcut olduğunu kontrol et
- `extract_json_object()` fonksiyonunu daha robust hale getir:
  brace counting yerine regex-based extraction
- Conflict/gap öğelerini sıralı confidence'a göre döndür

---

## Tartışma Notları

*(Bu bölüme geri bildirimler ve kararlar eklenir)*

- **[2026-05-11]** Hibrit yaklaşım benimsendi: keyword hızlı path + LLM belirsiz vakalar.
  Dependency parsing için Stanza'ya `depparse` processor eklenecek.

---

## Karar Bekleyenler

| Konu | Seçenek A | Seçenek B | Karar |
|---|---|---|---|
| Classifier LLM modeli | Gemini 2.5 Flash (hızlı) | DeepSeek (ucuz) | ❓ |
| Dep parsing Stanza yük artışı | Kabul et | Opsiyonel tut | ❓ |
| Confidence threshold (conflict) | 0.6 | 0.7 | ❓ |

---

## Tamamlananlar

*(Bitti olarak işaretlenenler buraya taşınır)*

---
