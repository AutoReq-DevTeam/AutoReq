# 🤖 AutoReq — Final Polish Agent Sistemi

> **Amaç:** Projenin tamamlanmış hali üzerinde **son kontroller ve iyileştirmeler** için hangi ajanın ne yapacağını, context penceresine neyin dahil edileceğini ve token tasarrufunu nasıl sağlayacağını tanımlar.
>
> **Temel kural:** Her ajan **tek bir dosya/modül/sorumluluk** alır. Geniş context açma yasaktır; sadece ihtiyaç duyulan dosyalar eklenir.

---

## 🗂 Agent Haritası

| Ajan | Sorumluluk | Context Girdisi | Çıktı |
|---|---|---|---|
| **AUDIT** | Bilinen sorunları ve açık limitleri tara | `bug_bash_results.md` + `ROADMAP_AND_ISSUES.md` (sadece açık ✗ satırları) | `AUDIT_REPORT.md` |
| **PERF** | AI hız darboğazlarını çöz | `performance_report.md` + hedef modül (1 dosya) | Düzeltilmiş kod |
| **UI** | UI/UX sorunlarını tespit et ve düzelt | `ui/` dizini (1 dosya/seferinde) + `AGENT_GUIDE.md §4.16-4.18` | Düzeltilmiş UI kodu |
| **TEST** | Coverage boşluklarını kapat | `bug_bash_results.md` coverage tablosu + `tests/` (hedef dosya) | Yeni test kodu |

---

## 1. AUDIT Ajanı

### Görev
`ROADMAP_AND_ISSUES.md` içindeki `[ ]` (tamamlanmamış) maddeleri ve `bug_bash_results.md` içindeki `🟡 Açık` kısıtları tarayıp önceliklendirilmiş bir aksiyon listesi üret.

### Prompt Şablonu

```
Sen bir yazılım kalite denetçisisin. Aşağıdaki iki belgeyi oku ve YALNIZCA açık/tamamlanmamış maddeleri listele.

--- BUG_BASH_RESULTS (Açık Sorunlar Bölümü) ---
[bug_bash_results.md içeriği — sadece "Düşük Önem / Açık Sorunlar" ve "Bilinen Kısıtlar" bölümleri]

--- ROADMAP (Tamamlanmamış görevler) ---
[ROADMAP_AND_ISSUES.md içinden yalnızca `- [ ]` satırları — grep ile çek]

## Çıktı Formatı
Aşağıdaki JSON yapısını üret ve başka hiçbir şey yazma:

{
  "critical": [{"id": "...", "desc": "...", "owner_file": "..."}],
  "medium":   [{"id": "...", "desc": "...", "owner_file": "..."}],
  "low":      [{"id": "...", "desc": "...", "owner_file": "..."}]
}
```

### Token Tasarrufu İpuçları
- `grep "- \[ \]" docs/ROADMAP_AND_ISSUES.md` ile sadece açık satırları çek (~15 satır vs 587 satır)
- `bug_bash_results.md` zaten küçük — tamamını ver
- Bu ajan **kod yazmaz**, sadece liste üretir

---

## 2. PERF Ajanı

### Görev
`performance_report.md`'de belgelenen açık öneri maddeleri ve `bug_bash_results.md::LIMIT-002` (async LLM) sorununu çöz.

### Hedef Sorunlar (bilinen)
- **LIMIT-002:** `ConflictDetector`, `GapAnalyzer`, `RequirementImprover` sıralı çalışıyor → paralel yapılabilir
- **Öneri #1:** `core/ner.py` şu an Stanza çıktısını tekrar parse ediyor; `TextPreprocessor.process()` içinde entegre edilebilir
- **Öneri #3:** Quantized Stanza modeli

### Prompt Şablonu — LIMIT-002 (Async LLM)

```
Sen bir Python performans uzmanısın. Aşağıdaki kısıtlı context'i oku.

## Proje Mimarisi (kısa özet)
- `app.py::process_text()` içinde ConflictDetector, GapAnalyzer, RequirementImprover SIRAYLA çalışıyor
- Her biri `LLMClient.chat()` çağırıyor (Gemini API — IO-bound)
- `core/pipeline.py` ThreadPoolExecutor kullanıyor ama LLM çağrıları için değil

## Hedef Dosya
[modules/llm_client.py — tamamını ver: ~200 satır]
[app.py::process_text() fonksiyonu — sadece o fonksiyon: ~40 satır]

## Görev
`process_text()` içindeki 3 LLM çağrısını `asyncio.gather()` veya `ThreadPoolExecutor` ile paralel yap.
Kısıtlar:
- `LLMClient.chat()` sync kalabilir; wrapper async olsun
- Mevcut `try/except (LLMClientError, ValueError)` bloklarını koru
- Loguru loglama pattern'ini değiştirme
- Gemini API rate-limit koruması: max 3 eşzamanlı istek

Sadece değişmesi gereken kod bloklarını ver. Tüm dosyaları yeniden yazma.
```

### Token Tasarrufu İpuçları
- `modules/llm_client.py` ~200 satır — tamamını ver (merkezi bağımlılık, kesilmez)
- `app.py`'dan sadece `process_text()` fonksiyonunu kes-yapıştır et (~40 satır)
- `performance_report.md` ve `bug_bash_results.md::LIMIT-002` bölümünü ver
- **AGENT_GUIDE.md verme** — özet zaten prompt içinde mevcut

---

## 3. UI Ajanı

### Görev
`ui/` klasöründeki bilinen sorunları ve genel UX eksikliklerini tespit edip düzelt. Her çalıştırmada **tek bir UI dosyasını** işle.

### Bilinen Sorunlar (AGENT_GUIDE.md §4.17'den)
- `ui/results.py`: `_safe_get(req_dict, "type", "FUNCTIONAL")` → `"req_type"` (✅ düzeltildi mi?)
- `ui/results.py`: İyileştirme sekmesinde `original` vs `improved` karşılaştırma layout kalitesi
- `ui/dashboard.py`: Demo modu aktifken `st.file_uploader` ile çakışma var mı?
- `ui/components.py`: `conflict_card()`, `gap_card()` bileşenlerinde accessibility (aria) eksikliği

### Prompt Şablonu — UI/UX İncelemesi

```
Sen bir Streamlit UI/UX uzmanısın. Aşağıdaki TEK dosyayı incele.

## Proje Bağlamı (kısa)
AutoReq: Türkçe metin → SRS dökümanı dönüştürücü. Streamlit dashboard.
4 sekme: Gereksinimler / Çelişkiler & Eksiklikler / İyileştirmeler / Export

## İncelenecek Dosya
[ui/results.py — tamamı: ~250 satır]

## Görev
Şu kriterlere göre bu dosyayı denetle:
1. **Veri okuma hataları:** `_safe_get` çağrılarında yanlış alan adı var mı?
2. **Boş durum yönetimi:** Listeler boşken kullanıcıya ne gösteriliyor?
3. **Layout sorunları:** `st.columns` nesting, responsive olmayan sabit genişlikler
4. **Erişilebilirlik:** Renk-bağımlı bilgi (severity sadece renk ile mi gösteriliyor?)
5. **Streamlit anti-pattern:** `st.experimental_*` kullanımı, session state yanlış kullanımı

Her sorun için:
- Sorunun bulunduğu satır numarası
- 1 cümle açıklama
- Düzeltilmiş kod snippet'i (sadece değişen satırlar)

Sorun bulamazsan "✅ Bu dosyada tespit edilen sorun yok" yaz.
```

### Token Tasarrufu İpuçları
- Her çalıştırmada 1 dosya: `results.py` VEYA `dashboard.py` VEYA `components.py`
- `AGENT_GUIDE.md` verme — proje bağlamını prompt içine özetle (5-6 satır yeterli)
- `ui/` dosyaları 150-300 satır aralığında — tamamını ver, kırpma
- UI ajanını 3 ayrı çalıştırmada kullan (3 dosya × 1 çalıştırma)

---

## 4. TEST Ajanı

### Görev
`bug_bash_results.md` coverage tablosundaki düşük modülleri ve `ROADMAP_AND_ISSUES.md`'deki test TODO'larını hedef al.

### Hedef Alanlar
- `modules/` coverage: %75 → %80+ hedef
- `tests/test_outputs.py` → hâlâ TODO olan bölümler var mı?
- Entegrasyon testlerinde LLM mock kullanımı

### Prompt Şablonu

```
Sen bir Python test uzmanısın (pytest). Aşağıdaki dosyaları oku.

## Mevcut Coverage
- core/: %89
- modules/: %75  ← HEDEF
- outputs/: %83

## İncelenecek Dosyalar
[tests/test_modules.py — tamamı]
[modules/gap_analyzer.py — tamamı]  (coverage düşükse)

## Görev
`modules/gap_analyzer.py` için eksik test senaryolarını belirle ve yaz:
- Mevcut testleri tekrar etme
- Her yeni test için: mock LLM yanıtını hazırla + assertion yaz
- `conftest.py`'daki fixture'ları kullan (`mock_llm_normal`, `mock_llm_empty` vb.)

Kısıtlar:
- Gerçek API çağrısı yapma — her zaman mock kullan
- `pytest.fixture` scope'u `function` olsun
- Yeni dosya açma — mevcut `test_modules.py`'a ekle

Sadece yeni test fonksiyonlarını ver.
```

### Token Tasarrufu İpuçları
- Hedef modülü (`gap_analyzer.py`) + test dosyasını (`test_modules.py`) ver
- `conftest.py`'ı özetle: fixture isimlerini listele, içeriğini verme
- Coverage raporunu sadece sayısal tablo olarak ver

---

## 🔄 Önerilen Çalıştırma Sırası

```
1. AUDIT Ajanı          → AUDIT_REPORT.md oluştur
2. UI Ajanı × 3         → results.py, dashboard.py, components.py
3. PERF Ajanı           → async LLM parallelization
4. TEST Ajanı           → modules/ coverage artır
```

**Neden bu sıra?**
- AUDIT önce: neyin bozuk olduğunu bil, sonra düzelt
- UI erken: insan gözü için kritik, test gerektirmez
- PERF ortada: async değişiklik test değişikliği gerektirebilir
- TEST sonda: hem yeni kodu hem eski kodu kapsar

---

## ⚡ Genel Token Optimizasyon Kuralları

| Kural | Neden |
|---|---|
| `AGENT_GUIDE.md` tam olarak verme | 41KB / 732 satır — her ajanın kendi özeti var |
| Tek seferinde tek sorumluluk | Karışık context → daha kötü çıktı + daha uzun prompt |
| `grep` ile filtrelenmiş ROADMAP | 587 satır → ~15 satır açık görev |
| Çıktı formatını JSON veya diff olarak iste | Serbest metin → gereksiz açıklama token'ları |
| "Sadece değişen satırları ver" talimatı | 200 satır yeniden yazmak yerine 20 satır diff |
| Bilinen bug'ları prompt içinde özetle | Ajanın kendi keşfetmesini bekleme |

---

## 📋 AUDIT_REPORT.md Şablonu (Ajan Çıktısı)

Bu dosyayı AUDIT ajanı oluşturacak. Manuel oluşturmak için:

```bash
# Açık görevleri hızlıca listele
grep -n "\- \[ \]" docs/ROADMAP_AND_ISSUES.md

# Açık bug'ları listele  
grep -n "🟡 Açık" docs/bug_bash_results.md
```

---

*Son güncelleme: 2026-05-06 | Yazar: Sonnet 4.6*
