# 📋 AutoReq — Açık Görev Audit Raporu

> **Oluşturma:** 2026-05-06 (otomatik — `grep "- \[ \]" ROADMAP_AND_ISSUES.md` + `grep "🟡 Açık" bug_bash_results.md`)
>
> **Kullanım:** Bu dosyayı PERF / UI / TEST ajanlarına "mevcut context" olarak ver. ROADMAP'ın tamamını verme.

---

## 🔴 Açık Kod Görevleri (Ajan Yapabilir)

| # | Issue | Görev | Hedef Dosya |
|---|---|---|---|
| 1 | #21 | `asyncio` / batched chat araştırması ve uygulaması | `modules/llm_client.py`, `app.py::process_text()` |
| 2 | #23 | PDF watermark opsiyonel parametre | `outputs/srs_generator.py` |
| 3 | #23 | Cross-platform Unicode font (Noto) desteği | `outputs/fonts/` (yeni klasör), `outputs/srs_generator.py` |

## 🟡 Açık Manuel Görevler (Ajan Yapamaz)

| # | Görev | Not |
|---|---|---|
| M1 | Drag & drop UX testi (3 format) | Manuel test gerekiyor |
| M2 | `docs/demo_script.md` tamamlama | Ekip görevi |
| M3 | README.md ekran görüntüleri | Screenshot gerekiyor |
| M4 | Bug bash session | Ekip görevi |

## 🟡 Açık Limitler (bug_bash_results.md)

| ID | Sorun | Öncelik | Ajan Görevi |
|---|---|---|---|
| LIMIT-001 | Arapça/Çince font eksik (Noto Sans) | Low | Düşük öncelik |
| LIMIT-002 | LLM çağrıları senkron (async yok) | Medium | **PERF ajanı hedefi** |
| LIMIT-003 | PDF watermark varsayılan kapalı | Low | PERF ajanı sonrası |
| LIMIT-004 | README ekran görüntüsü yok | Low | Manuel |

---

## 📊 Test Coverage Durumu (Sprint 7 Sonu)

| Paket | Coverage | Hedef |
|---|---|---|
| `core/` | %89 | ✅ |
| `modules/` | %75 | 🟡 → %80+ hedef |
| `outputs/` | %83 | ✅ |
| **Toplam** | **%81** | ✅ |

**TEST ajanı için hedef:** `modules/` %75 → %80+

---

## 🎯 Ajan Çalıştırma Sırası

```
1. PERF Ajanı  → LIMIT-002 (async LLM)     → modules/llm_client.py + app.py
2. UI Ajanı    → ui/results.py              → layout + veri sorunları
3. UI Ajanı    → ui/dashboard.py            → file upload + demo mode çakışma
4. UI Ajanı    → ui/components.py           → accessibility + card kalitesi
5. TEST Ajanı  → modules/ coverage %75→%80  → test_modules.py + gap_analyzer.py
```
