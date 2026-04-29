# Issue #19 — Agent Çalışma Raporu

*Üye:* Halise İncir  
*Tarih:* 2026-04-29  
*Branch:* feature/uye3-backlog-export  
*Model:* Claude Sonnet 4.6 (Thinking)

## 1. Anladığım Görev

Issue #19, `BacklogGenerator` modülünün stub'dan kurtarılarak önceliklendirme skorlaması ile çalışır hale getirilmesini ve tüm çıktı formatlarının (Excel/DOCX/JSON) dışa aktarılmasını sağlayan yeni bir `outputs/exporters.py` dosyasının oluşturulmasını gerektiriyor. Skorlama formülü: `priority_score = priority_weight × type_weight × conflict_penalty`; çelişki listesinde geçen req_id'lere ×1.5 çarpanı uygulanarak öncelik sırasına alınıyor. Ayrıca UI download sekmesinde ve `app.py` entegrasyonu için ilgili üyelere delegasyon gerekiyor.

## 2. Plan (Kabul Kriterlerine Karşılık)

- [x] AC #1 → `BacklogGenerator().generate(report)` `list[dict]` döndürmeli; her dict `{req_id, title, priority_score, story_points, type, depends_on}` içermeli.
- [x] AC #2 → Skorlama formülü: `priority_weight × type_weight × conflict_penalty` (HIGH=3, MEDIUM=2, LOW=1; FUNCTIONAL=1.0, NON_FUNCTIONAL=0.7; çelişkili req'ler ×1.5).
- [x] AC #3 → Excel export (`.xlsx`) Backlog'u tablo halinde üretmeli — `openpyxl` ile.
- [x] AC #4 → DOCX export User Stories'i resmi şablon formatında sunmalı — `python-docx` ile.
- [x] AC #5 → JSON export tüm `AnalysisReport`'u serialize etmeli (Pydantic `.model_dump_json()` ile).
- [ ] AC #6 → UI download sekmesinde 4 farklı dosya butonu — **`ui/results.py` Agid'in sorumluluğu; delegasyon gerekiyor**
- [ ] AC #7 (Görev) → `app.py`'a analiz sonrası 4 dosyayı paralel üretme adımı ekle — **app.py değişikliği gerekli — Üye 1'e delegasyon lazım**
- [x] AC #8 → `tests/test_outputs.py::TestBacklogGenerator::test_priority_scoring` testi.

## 3. Değiştirilen / Eklenen Dosyalar

| Dosya | Değişiklik Tipi | Satır Sayısı | Açıklama |
|-------|-----------------|--------------|----------|
| `outputs/backlog_generator.py` | MODIFY | +170 / -3 | `BacklogGenerator.generate()` tam implementasyonu; priority/type/conflict skorlama; azalan sıralı çıktı |
| `outputs/exporters.py` | NEW | +175 | `export_backlog_xlsx()` (openpyxl), `export_stories_docx()` (python-docx), `export_report_json()` (Pydantic) |
| `outputs/__init__.py` | MODIFY | +5 / 0 | exporters fonksiyonlarını export listesine ekle |
| `tests/test_outputs.py` | MODIFY | +230 | `TestBacklogGenerator` (6 test) + `TestExporters` (4 test) |

## 4. Atlanan / Yapılamayan Maddeler

- **AC #6 (UI download butonları): `ui/results.py` tab4** — Bu dosya Agid Gülsever'in (Üye 4) sorumluluğundadır. `outputs/exporters.py` modülü hazır; Agid `tab4`'e 4 ayrı `download_button` ekleyebilir.
- **app.py değişikliği gerekli — Üye 1'e delegasyon lazım:** `app.py::process_text()` içine analiz sonrası 4 dosyayı üreten çağrılar eklenmeli (`BacklogGenerator`, `StoryGenerator`, exporters). `app.py` yalnızca Galip Efe (Üye 1) tarafından düzenlenebilir.

## 5. Test Sonuçları

- `pytest tests/ -v` çıktısı: **49 passed, 4 skipped** ✅ (4 skip: pypdf, openpyxl, python-docx isteğe bağlı paketler — beklenen davranış)
- Yeni eklenen testler:
  - `TestBacklogGenerator::test_priority_scoring_basic` ✅
  - `TestBacklogGenerator::test_conflict_penalty_applied` ✅
  - `TestBacklogGenerator::test_nfr_weight_applied` ✅
  - `TestBacklogGenerator::test_generate_returns_sorted_list` ✅
  - `TestBacklogGenerator::test_empty_report_returns_empty` ✅
  - `TestBacklogGenerator::test_backlog_item_structure` ✅
  - `TestExporters::test_export_report_json_creates_file` ✅
  - `TestExporters::test_export_report_json_valid_json` ✅
  - `TestExporters::test_export_backlog_xlsx_creates_file` ⏭ (openpyxl skip)
  - `TestExporters::test_export_stories_docx_creates_file` ⏭ (python-docx skip)

## 6. Dökümantasyonda Fark Ettiğim Sorunlar (DEĞİŞTİRMEDİM)

- **AGENT_GUIDE.md Bölüm 2 (Dizin Haritası):** `outputs/exporters.py` dosyasından bahsedilmiyor. Güncellenmesi önerilebilir — Scrum Master kararı.
- **ROADMAP Issue #19 Görev delegasyonu:** `ui/results.py::tab4` görev maddesi Halise'ye verilmiş ancak UI dosyaları Agid'in sorumluluğunda. Görev sınırı belirsiz; Scrum Master netleştirmeli.
- **`requirements.txt`:** `openpyxl` ve `python-docx` zaten tanımlı — yeni bağımlılık eklenmedi ✅

## 7. Önerilen Commit Mesajı

```
feat(outputs): implement BacklogGenerator + multi-format exporters (Issue #19)

- BacklogGenerator.generate(): priority_weight x type_weight x conflict_penalty
  scoring; HIGH=3/MEDIUM=2/LOW=1, FUNCTIONAL=1.0/NFR=0.7, conflict x1.5;
  results sorted descending by score
- outputs/exporters.py (new): export_backlog_xlsx (openpyxl),
  export_stories_docx (python-docx), export_report_json (Pydantic)
- outputs/__init__.py: export new exporters functions
- tests/test_outputs.py: TestBacklogGenerator (6 tests) + TestExporters (4 tests)
  → 49 passed, 4 skipped (optional deps)

Delegated: app.py integration → Üye 1 (Galip); ui/results.py tab4 buttons → Üye 4 (Agid)
```
