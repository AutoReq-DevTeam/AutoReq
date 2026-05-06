# AutoReq — 10 Dakikalık Demo Senaryosu

**Hedef Kitle:** Proje sponsoru, ürün sahibi, potansiyel kullanıcılar  
**Süre:** 10 dakika  
**Gereksinimler:** `streamlit run app.py`, GEMINI_API_KEY set, Demo Modu aktif

---

## Dakika Dakika Akış

### Dakika 0–1 — Giriş ve Bağlam
**Ne yapılır:** Uygulama açılır, demo modu aktif edilir.

- Sidebar'da **Demo Modu** checkbox'ını işaretle → "Demo Modu Aktif" yeşil rozeti görünür.
- Slayt: "AutoReq — Gereksinimleri otomatik analiz eden yapay zeka destekli araç."
- Vurgu: Manuel gereksinim analizi haftalarca sürer; AutoReq bunu dakikalar içinde yapar.

---

### Dakika 1–2 — Girdi Sayfası
**Ne yapılır:** Demo senaryosu yüklenir.

- **Girdi** sayfasına git.
- Dropdown'dan **"Demo: E-Ticaret (Çelişki)"** seç → yükle.
- Text area'da gereksinimlerin göründüğünü göster.
- Vurgu: `.txt`, `.docx`, `.pdf` formatlarını destekliyor; sürükle-bırak ile yükleme yapılabilir.

---

### Dakika 2–4 — Analiz
**Ne yapılır:** Analiz başlatılır, pipeline adımları canlı izlenir.

- **Analiz** sayfasına geç → "Analizi Başlat" butonuna bas.
- Status bar'ın adımları göster: Stanza ön işleme → çelişki analizi → eksiklik analizi → iyileştirme.
- Vurgu: Tüm pipeline <15 saniyede tamamlanıyor.

---

### Dakika 4–6 — Sonuçlar: Gereksinimler ve Çelişkiler
**Ne yapılır:** Sonuçlar sayfası incelenir.

- **Sonuçlar** sayfasına geç.
- "Gereksinimler" sekmesinde: FUNCTIONAL / NON_FUNCTIONAL ayrımı, HIGH/MEDIUM/LOW öncelik.
- "Çelişkiler" sekmesinde: E-Ticaret senaryosunda ödeme sayfasına erişim çelişkisi göster.
- Vurgu: LLM hangi iki gereksinimin çeliştiğini ve neden çeliştiğini Türkçe açıklıyor.

---

### Dakika 6–7 — Eksiklikler ve İyileştirmeler
**Ne yapılır:** Gap analizi ve otomatik iyileştirme gösterilir.

- "Eksiklikler" sekmesinde: Tespit edilen güvenlik / erişilebilirlik boşlukları.
- "İyileştirmeler" sekmesinde: Muğlak gereksinim → ölçülebilir gereksinim diff view.
- Vurgu: "Sistem hızlı olmalı" → "Sistem, %95 oranında 2 saniye altında yanıt vermeli."

---

### Dakika 7–9 — Dışa Aktarım
**Ne yapılır:** Üretilen belgeler indirilir.

- **Dışa Aktarım** sayfasına geç.
- 4 dosyayı göster:
  - **SRS PDF** — ISO/IEC/IEEE 29148 uyumlu, bölümler, metadata dolu.
  - **Backlog XLSX** — Skorlanmış ve önceliklendirilmiş product backlog.
  - **Stories DOCX** — Agile user story formatında.
  - **JSON** — Tam analiz raporu (API entegrasyonu için).
- Vurgu: Sıfır manuel düzenleme → doğrudan Jira/Confluence'a aktarılabilir.

---

### Dakika 9–10 — Kapanış ve Q&A
**Ne yapılır:** Özet verilir, sorular alınır.

- Sidebar metrikleri göster: Gereksinim sayısı, çelişki sayısı, eksiklik sayısı, tahmini maliyet.
- Vurgu: "Bir analist için 2 günlük iş → AutoReq ile 2 dakika."
- Soru süresi.

---

## Demo Öncesi Kontrol Listesi

- [ ] `GEMINI_API_KEY` `.env` dosyasına girildi mi?
- [ ] `streamlit run app.py` hatasız açılıyor mu?
- [ ] Demo Modu sidebar'da görünüyor mu?
- [ ] `data/demo_scenarios/` altında 5 senaryo dosyası mevcut mu?
- [ ] İnternet bağlantısı stabil mi? (Gemini API için gerekli)
- [ ] `outputs/generated/` klasörü yazılabilir mi?

---

## Yedek Senaryo (LLM Yoksa)

API key mevcut değilse:

1. Sadece NLP analizi çalışır (sınıflandırma + önceliklendirme).
2. Çelişki / eksiklik sekmeleri boş gelir — "API Key tanımlı değil" uyarısı gösterilir.
3. SRS PDF statik demo olarak üretilir.
4. Bu senaryoyu "offline mod" olarak sunabilirsiniz.
