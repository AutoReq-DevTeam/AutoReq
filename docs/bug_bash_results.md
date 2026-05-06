# AutoReq — Bug Bash Sonuçları ve Bilinen Sorunlar

**Tarih:** 2026-05-05  
**Katılımcılar:** Sprint 6 tamamlanması sonrası otomatik derleme + Sprint 7 kod incelemesi

---

## Kritik Sorunlar (Çözüldü)

### BUG-001: `google.generativeai` Deprecation (Çözüldü — Sprint 7)
- **Önem:** Critical
- **Açıklama:** `google.generativeai` paketi tüm desteğini sonlandırdı; `google.genai` paketine geçiş gerekiyordu.
- **Etki:** Paket PyPI'dan kaldırıldığında tüm Gemini API çağrıları başarısız olurdu.
- **Çözüm:** `modules/llm_client.py` yeni `google.genai` SDK'sına (`Client` + `generate_content`) taşındı; `requirements.txt` güncellendi.
- **Durum:** ✅ Çözüldü

### BUG-002: `ui/state.py` Yanlış Session State Anahtarları (Çözüldü — Sprint 5)
- **Önem:** High
- **Açıklama:** `ui/state.py` `cost_usd` başlatıyordu; `app.py` ve `llm_client.py` `total_cost_usd` + `total_tokens_used` kullanıyordu.
- **Etki:** Maliyet göstergesi her zaman $0.00 ve 0 token gösteriyordu.
- **Çözüm:** `init_state()` doğru anahtarları başlatacak şekilde düzeltildi.
- **Durum:** ✅ Çözüldü

### BUG-003: Arch Linux'ta Türkçe Karakter PDF Hatası (Çözüldü — Sprint 2)
- **Önem:** Critical
- **Açıklama:** `/usr/share/fonts/truetype/dejavu/` yolu Arch Linux'ta mevcut değil; font bulunamadığında `FPDFUnicodeEncodingException`.
- **Etki:** SRS PDF üretimi tüm Arch/Manjaro sistemlerinde çöküyordu.
- **Çözüm:** `/usr/share/fonts/TTF/` Arch Linux yolu font aday listesine eklendi.
- **Durum:** ✅ Çözüldü

---

## Orta Önem Sorunlar (Çözüldü)

### BUG-004: `dashboard.py` Tekrar Eden Session State Başlatma (Çözüldü — Sprint 5)
- **Önem:** Medium
- **Açıklama:** `render_dashboard()` içinde `init_state()` ile zaten başlatılan anahtarlar tekrar kontrol ediliyordu.
- **Çözüm:** Tekrar eden null-check'ler kaldırıldı; `app.py` başlangıcında `init_state()` çağrısı yeterli.
- **Durum:** ✅ Çözüldü

### BUG-005: `gap_card()` Türkçe Metin ile DuplicateWidgetID (Çözüldü — Sprint 4)
- **Önem:** Medium
- **Açıklama:** Uzun Türkçe metinleri içeren gap kartları 255 karakter Streamlit widget key limitini aşıyordu.
- **Çözüm:** `hashlib.md5` ile 12 karakterlik hash key kullanılmaya başlandı.
- **Durum:** ✅ Çözüldü

---

## Düşük Önem / Açık Sorunlar

### BUG-006: `fpdf2` `ln=True` DeprecationWarning (Sessizleştirildi — Sprint 2)
- **Önem:** Low
- **Açıklama:** Eski `ln=1` parametresi kaldırılıp `new_x="LMARGIN", new_y="NEXT"` ile değiştirildi.
- **Durum:** ✅ Çözüldü

### BUG-007: `core/pipeline.py` %0 Test Coverage (Çözüldü — Sprint 6)
- **Önem:** High
- **Açıklama:** Ana pipeline orkestrasyonu hiç test edilmiyordu.
- **Çözüm:** `TestPipeline` sınıfı 7 yeni test ile eklendi; pipeline coverage %89'a çıktı.
- **Durum:** ✅ Çözüldü

---

## Bilinen Kısıtlar (Kapatılmadı)

### LIMIT-001: Arapça / Çince Karakter Desteği Eksik
- **Önem:** Low (kapsam dışı)
- **Açıklama:** Noto Sans font ailesi `outputs/fonts/` klasörüne eklenmedi; Latin dışı alfabeler PDF'de bozulabilir.
- **Geçici Çözüm:** Türkçe + ASCII DejaVuSans ile tam çalışıyor.
- **Durum:** 🟡 Açık — Sprint 8 kapsamı

### LIMIT-002: LLM Çağrıları Senkron (Async Yok)
- **Önem:** Low
- **Açıklama:** `ConflictDetector`, `GapAnalyzer`, `RequirementImprover` sıralı çalışıyor; büyük belgelerde gecikme artabilir.
- **Geçici Çözüm:** LLM önbelleği (24h TTL) aynı girdi için tekrar API çağrısını önlüyor.
- **Durum:** 🟡 Açık — Sprint 8 kapsamı

### LIMIT-003: PDF Watermark Varsayılan Kapalı
- **Önem:** Low
- **Açıklama:** `generate_srs(draft_watermark=False)` — pipeline watermark olmadan üretiyor.
- **Not:** `draft_watermark=True` parametresi ile kullanılabilir; UI'da toggle eklenmedi.
- **Durum:** 🟡 Açık — gelecek sprint

### LIMIT-004: README Ekran Görüntüleri Eksik
- **Önem:** Low
- **Açıklama:** `docs/screenshots/` klasörü ve README görselleri henüz eklenmedi.
- **Neden:** Uygulama çalışırken manuel screenshot gerekiyor.
- **Durum:** 🟡 Açık — demo sonrası

---

## Test Coverage Özeti (Sprint 7 Sonrası)

| Paket | Coverage |
|---|---|
| `core/` | %89 |
| `modules/` | %75 |
| `outputs/` | %83 |
| **Toplam** | **%81** |

**Test sayısı:** 187 (tümü pass)
