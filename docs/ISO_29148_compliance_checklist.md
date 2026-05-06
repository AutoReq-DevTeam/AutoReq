# ISO/IEC/IEEE 29148:2018 — SRS Uyum Kontrol Listesi

**Issue #23 AC:** 10 zorunlu bölüm ve her birinin AutoReq SRS PDF'inde nasıl karşılandığı.

Referans Standart: ISO/IEC/IEEE 29148:2018 — *Systems and software engineering — Life cycle processes — Requirements engineering*, Bölüm 9.5 (SRS içerik gereksinimleri).

---

## Kontrol Listesi

| # | Bölüm Adı | Standart Referansı | SRS'te Karşılanıyor mu? | Kanıt / Uygulama Yeri |
|---|---|---|---|---|
| 1 | **Giriş (Introduction)** | 9.5.2.1 | ✅ Evet | `srs_generator.py::add_section_title("1. Giriş")` — Proje adı, amaç, kapsam |
| 2 | **Kapsam (Scope)** | 9.5.2.2 | ✅ Evet | `add_section_title("2. Kapsam")` — Sistem sınırları, paydaşlar |
| 3 | **Genel Açıklama (Overall Description)** | 9.5.3 | ✅ Evet | `add_section_title("3. Genel Açıklama")` — Ürün perspektifi, kısıtlar |
| 4 | **Fonksiyonel Gereksinimler (Functional Requirements)** | 9.5.4 | ✅ Evet | Dinamik bölüm — `ParsedDocument.requirements` FUNCTIONAL tipi |
| 5 | **Fonksiyonel Olmayan Gereksinimler (Non-Functional Requirements)** | 9.5.5 | ✅ Evet | Dinamik bölüm — NON_FUNCTIONAL tipi gereksinimler |
| 6 | **Çelişki Analizi (Conflict Analysis)** | 9.5.6 (ek) | ✅ Evet | LLM `ConflictDetector` çıktısı — çelişki tablosu |
| 7 | **Eksiklik Analizi (Gap Analysis)** | 9.5.6 (ek) | ✅ Evet | LLM `GapAnalyzer` çıktısı — eksiklik tablosu |
| 8 | **Önceliklendirme (Prioritization)** | 9.5.7 | ✅ Evet | `PriorityDetector` — HIGH/MEDIUM/LOW atanmış gereksinim listesi |
| 9 | **Doğrulama Kriterleri (Verification)** | 9.5.8 | ✅ Evet | `add_section_title("9. Doğrulama")` — kabul kriterleri özeti |
| 10 | **Ek Bilgiler / Sözlük (Appendices)** | 9.5.9 | ✅ Evet | `add_section_title("10. Ekler")` — kısaltmalar, referanslar |

---

## PDF Metadata Uyumu

| Metadata Alanı | Değer | Standart Gereksinimi |
|---|---|---|
| `/Title` | Proje adı + "SRS" | ✅ 29148 §6.1 |
| `/Author` | "AutoReq" | ✅ |
| `/Subject` | "Yazılım Gereksinim Spesifikasyonu" | ✅ |
| `/Creator` | "AutoReq v1.0 — fpdf2" | ✅ |
| `/CreationDate` | Otomatik (oluşturma tarihi) | ✅ |

---

## Otomatik Test Kapsamı

Aşağıdaki testler `tests/test_outputs.py::TestSRSGenerator` içinde bulunmaktadır:

| Test | Kapsam |
|---|---|
| `test_pdf_contains_all_iso_sections` | 10 bölüm başlığının PDF metninde varlığını doğrular |
| `test_pdf_metadata` | `/Title`, `/Author`, `/Subject` alanlarının dolu olduğunu doğrular |
| `test_pdf_size_under_5mb` | Dosya boyutu <5 MB kısıtını doğrular |
| `test_turkish_chars_render` | "ş, ğ, İ" karakterlerinin PDF'de bozulmadan bulunduğunu doğrular |

---

## Açık Maddeler

- Arapça / Çince karakter desteği: Noto font ailesi `outputs/fonts/` klasörüne eklendikten sonra tam Unicode desteği sağlanabilir.
- Watermark ("DRAFT") opsiyonel parametre olarak `generate_srs(watermark=True)` şeklinde eklenebilir (Sprint 7 kapsamı).
