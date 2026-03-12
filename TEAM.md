# 👥 AutoReq – Ekip & Görev Dağılımı

> **Metodoloji:** Scrum | **Sprint Süresi:** 2 hafta | **Ekip:** 4 Kişi  
> Her üye kendi modülünden tam sorumludur. Modüller arası iletişim `interface` katmanı üzerinden sağlanır.

---

## 🗂 Sorumluluk Matrisi (RACI)

| Sorumluluk Matrisi | Üye 1 | Üye 2 | Üye 3 | Üye 4 |
|---|:---:|:---:|:---:|:---:|
| NLP Core & Preprocessing | **R** | C | I | I |
| Akıllı Analiz (NLP + LLM) | I | **R** | C | I |
| Çıktı Üretimi (LLM Destekli) | I | C | **R** | I |
| LLM Entegrasyonu (Genel) | C | **R** | **R** | I |
| UI & Uygulama Entegrasyonu | C | I | I | **R** |
| Testler (Unit & Prompt Test) | C | C | C | **R** |
| `app.py` (Orchestration) | **R** | C | C | C |

> **R** = Responsible (Sorumlu) | **C** = Consulted (Danışılan) | **I** = Informed (Bilgilendirilen)

---

## 🧑‍💻 Galip Efe Öncü — NLP Core & Preprocessing

**Çalışma Dizini:** `core/` + `app.py`

### Görevler
- [ ] `preprocessor.py` — Ham metin temizleme, tokenizasyon, normalizasyon
- [ ] `classifier.py` — Fonksiyonel vs. Fonksiyonel Olmayan gereksinim sınıflandırıcı (scikit-learn)
- [ ] `ner.py` — Named Entity Recognition; aktör (Kullanıcı, Sistem, Admin) ve nesne tespiti (spaCy)
- [ ] `core/__init__.py` — Modül dışa aktarımları
- [ ] `app.py` — Ana Streamlit giriş noktası; tüm modülleri birleştirir ve sistemi sen ayağa kaldırırsın

### Teknik Detaylar
```
Kullanılacak Kütüphaneler : spaCy, NLTK, scikit-learn
Temel Sınıf               : TextProcessor
Giriş                     : Ham string (müşteri metni)
Çıkış                     : ParsedDocument dataclass (Yapısal analiz tamamlanmış)
```

### Kabul Kriterleri
- 100 kelimelik bir metni < 1 saniyede işlemelidir
- NER doğruluğu ≥ %80 olmalıdır
- Her fonksiyon docstring ve type hint içermelidir

---

## 🧑‍💻 Üye 2 — Akıllı Analiz Modülleri

**Çalışma Dizini:** `modules/`

### Görevler
- [ ] `conflict_detector.py` — Gereksinimlerdeki mantıksal çelişkileri ve zıtlıkları tespit et
- [ ] `gap_analyzer.py` — Eksik gereksinimleri standart şablonlarla karşılaştırarak bul ve öner
- [ ] `improver.py` — "Hızlı olmalı", "kolay olmalı" gibi muğlak ifadeleri ölçülebilir kriterlere çevir
- [ ] `modules/__init__.py` — Modül dışa aktarımları

### Teknik Detaylar
```
Kullanılacak Kütüphaneler : LangChain, OpenAI/Ollama API, spaCy, pydantic
Giriş                     : ParsedDocument (Üye 1'den gelir)
Çıkış                     : AnalysisReport dataclass (Mantıksal ve anlamsal analiz eklenmiş)
Şablonlar & Promptlar     : data/templates/ ve prompts/ dizinlerinden okunur
```

### Kabul Kriterleri
- Çelişki tespiti hem kelime bazlı (NLP) hem de mantıksal (LLM) düzeyde çalışmalıdır
- LLM yanıt süreleri optimize edilmeli ve "hallucination" kontrolü yapılmalıdır
- Her analiz sonucu için tutarlı bir `reason` alanı üretilmelidir

---

## 🧑‍💻 Üye 3 — Çıktı & Döküman Üretimi

**Çalışma Dizini:** `outputs/`

### Görevler
- [ ] `srs_generator.py` — ISO/IEC/IEEE 29148 standardına uygun PDF formatında SRS belgesi üretimi
- [ ] `story_generator.py` — "As a [role], I want [goal], so that [benefit]" formatında User Story üretimi
- [ ] `backlog_generator.py` — Öncelik skoru hesaplayarak sıralı Product Backlog üretimi
- [ ] `bdd_generator.py` — Given / When / Then formatında BDD test senaryosu üretimi
- [ ] `outputs/__init__.py` — Modül dışa aktarımları

### Teknik Detaylar
```
Kullanılacak Kütüphaneler : fpdf2, reportlab, python-docx, LangChain (İçerik Yazımı)
Giriş                     : AnalysisReport (Üye 2'den gelir)
Çıkış                     : PDF / DOCX / XLSX / Gherkin dosyaları
Prompt Stratejisi         : Belirlenen mühendislik standartlarına göre döküman üretimi
```

### Kabul Kriterleri
- PDF çıktısı geçerli bir ISO/IEC/IEEE 29148 yapısına sahip olmalıdır
- Her çıktı formatı için ayrı unit test yazılmalıdır
- Dosyalar `outputs/generated/` altına kaydedilmelidir

---

## 🧑‍💻 Üye 4 — UI / Arayüz & Uygulama Entegrasyonu

**Çalışma Dizini:** `ui/` + `tests/`

### Görevler
- [ ] `ui/dashboard.py` — Ana ekran; metin girişi, analiz butonu, ilerleme çubuğu
- [ ] `ui/results.py` — Analiz sonuçlarını sekmeli/panelli gösterim
- [ ] `ui/components.py` — Yeniden kullanılabilir UI bileşenleri (kartlar, rozetler, tablolar)
- [ ] `tests/` — Her modül için pytest tabanlı unit testleri
- [ ] `ui/__init__.py` — Modül dışa aktarımları

### Teknik Detaylar
```
Kullanılacak Kütüphaneler : Streamlit, pandas
Giriş                     : Kullanıcı metin girişi
Çıkış                     : İnteraktif dashboard + indirilebilir dosyalar
Port                      : localhost:8501 (varsayılan)
```

### Kabul Kriterleri
- Streamlit uygulaması hatasız `streamlit run app.py` ile çalışmalıdır
- Test coverage ≥ %70 olmalıdır
- UI; metin giriş ekranı, analiz ekranı ve sonuç ekranı olmak üzere 3 sayfadan oluşmalıdır

---

## 📅 Scrum Takvimi (Önerilen)

```
Sprint 0  (Hafta 1)   → Ortam kurulumu, repo yapısı, interface anlaşmaları
Sprint 1  (Hafta 2-3) → MVP: Preprocessing + Sınıflandırma + Temel UI
Sprint 2  (Hafta 4-5) → Akıllı modüller + SRS çıktısı
Sprint 3  (Hafta 6-7) → User Stories + BDD + Backlog çıktıları
Sprint 4  (Hafta 8)   → Test & entegrasyon, demo hazırlığı
```

---

## 🔗 Ortak Kurallar

1. **Branch Stratejisi:** `main` → `develop` → `feature/uye[n]-ozellik-adi`
2. **Commit Convention:** `feat:`, `fix:`, `docs:`, `test:`, `prompt:` önekleri kullanılacak
3. **Pull Request:** Her PR en az 1 başka üye tarafından incelenmelidir
4. **Interface Anlaşması:** Modüller arası `dataclass` tanımları `core/models.py` dosyasında tutulur
5. **API Güvenliği:** API anahtarları asla koda gömülmez, `.env` dosyasında saklanır

---

*Son Güncelleme: Mart 2026 | AutoReq-DevTeam*
