# Prompt Versiyonlama Prosedürü

**Issue #22 AC:** Prompt değişiklik prosedürünü belgele.

---

## Genel Kural

Tüm LLM prompt'ları `modules/*_prompts.py` dosyalarında merkezi olarak tanımlanır. Bu dosyalardaki değişiklikler **kırıcı değişiklik (breaking change)** sayılır ve aşağıdaki prosedür izlenmelidir.

---

## Adım Adım Prosedür

### 1. Değişikliği Dalda Yap

```bash
git checkout -b prompt/my-improvement
# modules/conflict_prompts.py içinde değişikliği yap
```

### 2. Snapshot Testlerini Çalıştır

```bash
pytest tests/regression/ -v
```

Eğer snapshot değişmişse testler `FAILED` verir. Bu beklenen davranıştır — değişikliği kasıtlı yapıyorsan bir sonraki adıma geç.

### 3. Snapshot'ı Güncelle (Kasıtlı Değişiklik)

```bash
pytest tests/regression/ --snapshot-update
```

Bu komut `tests/regression/__snapshots__/` altındaki `.ambr` dosyalarını günceller.

### 4. Değişikliği Gözden Geçir

```bash
git diff tests/regression/__snapshots__/
```

Diff'i okuyarak:
- Yeni prompt daha spesifik, daha kısa veya daha Türkçe mi?
- İstenmeyen format değişikliği var mı (başlık, JSON anahtarı)?

### 5. PR'da Kanıt Sun

PR açıklamasına ekle:
- Eski prompt ile yeni prompt arasındaki fark
- Değişiklik gerekçesi (kalite, dil, format düzeltme)
- Etkilenen modül ve test adı

### 6. CI Onayı

`.github/workflows/test.yml` içindeki `regression` job'u PR'da otomatik çalışır. Snapshot güncel değilse CI başarısız olur.

---

## Önemli Kurallar

| Kural | Gerekçe |
|---|---|
| Prompt değişikliği = snapshot güncelleme | Regresyonu otomatik yakala |
| Prompt'a Türkçe dışı direktif ekleme | Çıktı dili kontrolü için |
| JSON format anahtarlarını değiştirmeden önce parser'ı güncelle | `modules/analysis_report_parsing.py` JSON anahtar eşleşmelerine bağımlıdır |
| `--snapshot-update` sadece kasıtlı değişikliklerde | Yanlışlıkla update = gizli regresyon |

---

## Snapshot Dosya Konumu

```
tests/regression/__snapshots__/
└── test_prompt_snapshots.ambr   ← syrupy formatı, okunabilir diff
```

Snapshot'lar versiyon kontrolündedir (`git`). Her PR'da diff incelenmelidir.
