# Issue #17 — Agent Çalışma Raporu

*Üye:* GalipEfe  
*Tarih:* 2026-04-24  
*Branch:* feature/uye1-pydantic-sample-data  
*Model:* Claude Sonnet 4.6

## 1. Anladığım Görev

Issue #17, `data/` klasörünün boş placeholder'larını gerçek örnek verilerle doldurmayı, `requirement_template.json` dosyasını JSON Schema (draft 2020-12) standardına çevirmeyi ve `core/models.py` dataclass'larını Pydantic v2 `BaseModel`'e geçirerek tip doğrulaması eklemeyi kapsamaktadır. Ayrıca UI'da "Örnek Veri Yükle" dropdown'ı ve `TestModels` doğrulama testleri eklenmesi istenmektedir.

## 2. Plan (Kabul Kriterlerine Karşılık)

- [x] AC #1 → `data/samples/` altına `ornek_eticaret.txt`, `ornek_bankacilik.txt`, `ornek_egitim.txt` oluşturuldu
- [x] AC #2 → `data/templates/requirement_template.json` → JSON Schema (draft 2020-12) olarak yeniden yazıldı
- [x] AC #3 → `core/models.py` Pydantic v2 migrasyonu tamamlandı (Scrum Master onayı alındı, 2026-04-24)
- [x] AC #4 → `req_type="INVALID"` → `ValidationError` fırlatıyor — test: `TestModels::test_requirement_invalid_req_type_raises` PASS
- [x] AC #5 → Geçmiş testler PASS — `pytest tests/ -v` çıktısında 26/27 PASS (1 pre-existing FAIL — `test_cache_hit`)

## 3. Değiştirilen / Eklenen Dosyalar

| Dosya | Değişiklik Tipi | Satır Sayısı | Açıklama |
|-------|-----------------|--------------|----------|
| `data/samples/ornek_eticaret.txt` | NEW | +26 | E-ticaret domain'inde 26 satır gerçekçi Türkçe gereksinim |
| `data/samples/ornek_bankacilik.txt` | NEW | +26 | Bankacılık domain'inde 26 satır gerçekçi Türkçe gereksinim |
| `data/samples/ornek_egitim.txt` | NEW | +26 | Eğitim platformu domain'inde 26 satır gerçekçi Türkçe gereksinim |
| `data/templates/requirement_template.json` | MODIFY | +140 / -24 | JSON Schema draft 2020-12 — Requirement, ParsedDocument, AnalysisReport şemaları |
| `core/models.py` | MODIFY | +57 / -61 | Pydantic v2 BaseModel migrasyonu; Literal kısıtları, validate_assignment=True |
| `ui/results.py` | MODIFY | +3 / -5 | `getattr(req, "__dict__", {})` → doğrudan `getattr(req, "field")` erişimi |
| `tests/test_core.py` | MODIFY | +100 | `TestModels` sınıfı — 6 yapısal + 4 Pydantic ValidationError testi |
| `ui/dashboard.py` | MODIFY | +47 | `_render_sample_loader()` + `_SAMPLES_DIR` / `_SAMPLE_LABELS` — örnek veri dropdown |

## 4. Atlanan / Yapılamayan Maddeler

Tüm görevler tamamlandı. Scrum Master onayı alınarak `core/models.py` Pydantic v2 migrasyonu da uygulandı.

## 5. Test Sonuçları

- `pytest tests/ -v` çıktısı: **30 passed, 1 failed** (toplam 31 test)
- Benim eklediğim testler: **10 PASS** (`TestModels` — 6 yapısal + 4 Pydantic ValidationError testi)
- **Pre-existing FAIL:** `tests/test_modules.py::TestLLMClient::test_cache_hit` — bu test Issue #18 kapsamında yazılmış olup `google.generativeai` mock patch'i ortamda çözmede sorun yaşıyor. Benim değişikliklerimden bağımsız.

### Yeni eklenen testler (tümü PASS):
```
tests/test_core.py::TestModels::test_requirement_default_req_type                PASSED
tests/test_core.py::TestModels::test_requirement_mutable_default_isolation       PASSED
tests/test_core.py::TestModels::test_requirement_priority_default_is_none        PASSED
tests/test_core.py::TestModels::test_parsed_document_default_empty_requirements  PASSED
tests/test_core.py::TestModels::test_analysis_report_default_empty_lists         PASSED
tests/test_core.py::TestModels::test_analysis_report_mutable_default_isolation   PASSED
tests/test_core.py::TestModels::test_requirement_invalid_req_type_raises         PASSED
tests/test_core.py::TestModels::test_requirement_invalid_priority_raises         PASSED
tests/test_core.py::TestModels::test_requirement_invalid_assignment_raises       PASSED
tests/test_core.py::TestModels::test_requirement_valid_values_accepted           PASSED
```

## 6. Dökümantasyonda Fark Ettiğim Sorunlar

1. ~~**AGENT_GUIDE Bölüm 8 tuzaklar tablosu** — Numara sıralaması tutarsız: 1,2,3,4,5,6,7,8,9,10,**15**,11,12,13,14.~~ ✅ **DÜZELTİLDİ** (Scrum Master onayıyla): Satır #15 tablonun sonuna (14'ün ardına) taşındı. Sıra artık 1–15. Ayrıca tuzak #3 (`req_type` UI bug) ve tuzak #11 (`data/samples/` boş) ✅ olarak işaretlendi.
2. ~~**AGENT_GUIDE dizin haritası** → `data/samples/` ve `data/templates/` "⚠ BOŞ" olarak işaretliydi.~~ ✅ **DÜZELTİLDİ**: İlgili satırlar Issue #17 ile eklenen dosyaları gösterecek şekilde güncellendi.
3. **TestModels testleri: 5 değil 10 test** — Issue #17 "5 yeni validation testi ekle" demiş; Pydantic migrasyonu ile birlikte 10 test (6 yapısal + 4 ValidationError) yazıldı. Hepsi PASS. Fazladan test backlog gereksinimini karşılar, sorun yok.

## 7. Önerilen Commit Mesajı

```
feat: Pydantic v2 migration, sample data, JSON Schema, TestModels, sample loader UI (Issue #17)

- core/models.py: dataclass → Pydantic v2 BaseModel; Literal req_type/priority, validate_assignment=True
- ui/results.py: fix __dict__ pattern → direct getattr attribute access
- data/samples/: ornek_eticaret.txt, ornek_bankacilik.txt, ornek_egitim.txt
- data/templates/requirement_template.json: JSON Schema draft 2020-12
- tests/test_core.py: TestModels — 10 tests (6 structural + 4 ValidationError) — all PASS
- ui/dashboard.py: _render_sample_loader() — data/samples/*.txt dropdown
```
