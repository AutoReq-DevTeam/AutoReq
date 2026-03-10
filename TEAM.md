# 👥 AutoReq – Ekip & Görev Dağılımı

> **Metodoloji:** Scrum | **Sprint Süresi:** 2 hafta | **Ekip:** 4 Kişi  
> Her üye kendi modülünden tam sorumludur. Modüller arası iletişim `interface` katmanı üzerinden sağlanır.

---

## 🗂 Sorumluluk Matrisi (RACI)

| Sorumluluk Matrisi | Üye 1 | Üye 2 | Üye 3 | Üye 4 |
|---|:---:|:---:|:---:|:---:|
| NLP Core & Preprocessing | **R** | C | I | I |
| Akıllı Analiz Modülleri | I | **R** | C | I |
| Çıktı & Döküman Üretimi | I | C | **R** | I |
| UI / Streamlit Arayüzü | C | I | I | **R** |
| Testler | C | C | C | **R** |
| `app.py` (entegrasyon) | **R** | C | C | C |

> **R** = Responsible (Sorumlu) | **C** = Consulted (Danışılan) | **I** = Informed (Bilgilendirilen)

---

## 🧑‍💻 Üye 1 — NLP Core & Preprocessing

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
Çıkış                     : ParsedDocument dataclass
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
Kullanılacak Kütüphaneler : spaCy, pandas, pydantic
Giriş                     : ParsedDocument (Üye 1'den gelir)
Çıkış                     : AnalysisReport dataclass
Şablonlar                 : data/templates/ dizininden okunur
```

### Kabul Kriterleri
- Çelişki tespiti en az 5 farklı çelişki türünü yakalamalıdır
- Eksik gereksinim analizi `data/templates/` altındaki şablona dayanmalıdır
- Her sonuç için açıklayıcı bir `reason` alanı üretilmelidir

---

## 🧑‍💻 Üye 3 — Çıktı & Döküman Üretimi

**Çalışma Dizini:** `outputs/`

### Görevler
- [ ] `srs_generator.py` — IEEE 830 standardına uygun PDF formatında SRS belgesi üretimi
- [ ] `story_generator.py` — "As a [role], I want [goal], so that [benefit]" formatında User Story üretimi
- [ ] `backlog_generator.py` — Öncelik skoru hesaplayarak sıralı Product Backlog üretimi
- [ ] `bdd_generator.py` — Given / When / Then formatında BDD test senaryosu üretimi
- [ ] `outputs/__init__.py` — Modül dışa aktarımları

### Teknik Detaylar
```
Kullanılacak Kütüphaneler : fpdf2, reportlab, python-docx, openpyxl
Giriş                     : AnalysisReport (Üye 2'den gelir)
Çıkış                     : PDF / DOCX / XLSX / Gherkin dosyaları
Şablonlar                 : data/templates/ dizininden okunur
```

### Kabul Kriterleri
- PDF çıktısı geçerli bir IEEE 830 yapısına sahip olmalıdır
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
2. **Commit Convention:** `feat:`, `fix:`, `docs:`, `test:` önekleri kullanılacak
3. **Pull Request:** Her PR en az 1 başka üye tarafından incelenmelidir
4. **Interface Anlaşması:** Modüller arası `dataclass` tanımları `core/models.py` dosyasında tutulur

---

*Son Güncelleme: Mart 2026 | AutoReq-DevTeam*
