# AutoReq Geliştirme ve İyileştirme Raporu

Bu rapor, AutoReq projesinde gerçekleştirilen faz bazlı düzeltmeleri ve geliştirmeleri doğrulamaları ile birlikte sunmaktadır.

---

## Faz 1: Engelleyici Hataların Düzeltilmesi (Blocker/P0 Fixes) — TAMAMLANDI

Faz 1 kapsamında projenin kararlılığını, güvenliğini ve veri akış doğruluğunu engelleyen tüm P0 seviyesindeki kritik hatalar giderilmiş ve doğrulanmıştır.

### Gerçekleştirilen Değişiklikler ve Düzeltmeler

1. **Tek Başına Fiillerin Sınıflandırılması (Standalone Functional Verbs):**
   - `core/classifier.py` dosyasındaki `_FR_VERB_RE` düzenli ifadesi `\w+` yerine `\w*` olarak güncellenerek "silmeli", "yapmalı" gibi ek veya ön takı bulunmayan tekil fiillerin ve `-melidir/-malıdır` varyasyonlarının doğru sınıflandırılması sağlandı.

2. **Türkçe Karakter Uyumlu Küçük Harfe Dönüştürme (Turkish Lowercasing):**
   - `core/nlp_engine.py` içinde `I/ı` ve `İ/i` dönüşümlerini doğru yapan ve `U+0307` birleştirici üst nokta karakterlerini temizleyen merkezi bir `turkish_lower()` fonksiyonu yazıldı.
   - Bu fonksiyon `preprocessor.py`, `ner.py` ve `classifier.py` içinde anahtar kelime eşleşmelerinde kullanılarak Türkçe karakter duyarlılığından kaynaklanan hatalar engellendi.

3. **KVKK Uyumlu Maskeleme Katmanı (KVKK Compliance Masking):**
   - `core/preprocessor.py` içinde harici LLM'lere veri gönderilmeden önce T.C. Kimlik Numaralarını (`[TC_KIMLIK_NO]`) ve kişi adlarını (`[KISI_ADI]`) maskeleyen düzenli ifade (regex) tabanlı yerel bir KVKK maskeleme katmanı geliştirildi.
   - Cümle başındaki kelimelerin (örneğin "Giriş ekranında...") isim olarak yanlış maskelenmesini engellemek için cümle başı analizi ve istisna listesi (exclusion list) mekanizması entegre edildi.

4. **Geliştirilmiş Gereksinim Akışı (Improved Requirements Flow):**
   - `core/pipeline.py` akışı değiştirilerek, ilk önce `RequirementImprover` toplu (batch) olarak çalıştırıldı. Sonrasındaki Çelişki (Conflict), Eksiklik (Gap) analizleri ve BDD/Story/Backlog doküman üreticileri bu iyileştirilmiş gereksinim listesini kullanacak şekilde bağlandı.

5. **Bellek İçi Belge Üretimi (In-Memory Document Generation):**
   - PDF, DOCX, XLSX ve JSON üreten tüm dışa aktarıcılar (`outputs/exporters.py`, `srs_generator.py`, `bdd_generator.py` vb.) `in_memory=True` parametresi alarak `io.BytesIO` bellek içi tampon dönüştürecek şekilde güncellendi. Streamlit indirme butonları bu tamponları doğrudan tüketecek şekilde yapılandırılarak eşzamanlı kullanıcı çakışmaları ve disk sızıntısı engellendi.

6. **İş Parçacığı Güvenli UI Uyarıları (Thread-Safe UI Warnings):**
   - `core/pipeline.py` içinde arka planda koşan çıktı üretici thread'lerin doğrudan `st.session_state` nesnesini mutasyona uğratması engellendi. Değerler ve oluşan hata uyarıları ana thread'e döndürülerek `st.session_state` güncellemeleri yalnızca ana Streamlit iş parçacığından güvenli bir şekilde yapıldı.

7. **JSON Dışa Aktarım Yarış Durumu (JSON Exporter Race Condition):**
   - `pipeline.py` içindeki `export_report_json` çağrısı, gereksinim iyileştirme adımının tamamlanmasından sonraya ertelenerek `analysis_report.json` raporunun güncel iyileştirilmiş metinleri içermesi garanti altına alındı.

8. **LLM Modeli Ad Çözümlemesi (LLMClient Model Name Resolution):**
   - `modules/llm_client.py` içinde native Gemini API sağlayıcısı seçildiğinde model isminin başındaki `google/` gibi OpenRouter ön ekleri otomatik olarak temizlendi ve API anahtarı durumuna göre varsayılan modeller dinamik olarak belirlendi.

9. **Kalıcı XSS Güvenlik Açığı Önleme (Stored XSS Mitigation):**
   - `ui/components.py` içinde `st.markdown(..., unsafe_allow_html=True)` ile dinamik olarak render edilen gereksinim metinleri, çelişki detayları, eksiklik senaryoları ve değişim farkları `html.escape()` fonksiyonu ile filtrelenerek XSS açıkları tamamen kapatıldı.

10. **Prompt Enjeksiyon Koruması (Prompt Injection Shield):**
    - `modules/` dizinindeki tüm LLM prompt şablonlarında (`improver_prompts.py`, `bdd_prompts.py`, `conflict_prompts.py`, `gap_prompts.py`, `story_prompts.py`) girdi olarak verilen gereksinim değişkenleri `<requirement_text>...</requirement_text>` XML etiketleri içine alındı. LLM'e bu etiket dışındaki komutları yok sayması ve içeriği sadece girdi verisi olarak işlemesi talimatı verildi.

### Doğrulama ve Test Sonuçları

- Projedeki tüm birim (unit) ve çıktı (output) testleri `pytest` ile koşturulmuş ve **62 testin tamamı başarıyla geçmiştir**.

---

## Faz 2: Kritik Hataların Düzeltilmesi (Critical/P1 Fixes) — TAMAMLANDI

Faz 2 kapsamında projenin performansını, kullanılabilirliğini ve akademik tutarlılığını etkileyen P1 düzeyindeki kritik maddeler başarıyla çözümlenmiş ve doğrulanmıştır.

### Gerçekleştirilen Değişiklikler ve Düzeltmeler

1. **Stanza NER Modülünün Devre Dışı Bırakılması (Stanza Neural NER Processor):**
   - `core/nlp_engine.py` dosyasındaki Stanza pipeline yapılandırmasından kullanılmayan `'ner'` işlemcisi kaldırıldı. Bu değişiklik sayesinde bellek kullanımı yaklaşık 300MB azaltıldı ve uygulama açılış/çalışma hızında önemli performans artışı sağlandı.

2. **Dinamik Domain Kontrol Listelerinin LLM'e Enjeksiyonu (Gaps References Checklists):**
   - `modules/gap_analyzer.py` içinde `DOMAIN_REFERENCES` listesi dinamik olarak okunarak Gap Analyzer sistem promptuna eklendi. Böylece LLM, sistem türüne (web_app, api, mobile, desktop, iot, other) göre eksik gereksinimleri çok daha doğru ve referans listelere bağlı kalarak tespit edebilmektedir.

3. **Otomatik Türkçe Font Kurulumu (Turkish SRS Fonts):**
   - `outputs/fonts/download_fonts.py` betiği oluşturularak, Türkçe karakter uyumlu `DejaVuSans.ttf` ve `DejaVuSans-Bold.ttf` fontlarının Setasign tFPDF raw GitHub reposundan otomatik olarak indirilmesi sağlandı.
   - `app.py` başlangıcına bu betiği tetikleyen bir hook eklenerek, headless Linux sunucularında Türkçe PDF oluşturulurken yaşanan çökme ve karakter bozulması problemleri tamamen çözüldü.

4. **Uyumlu Gherkin BDD Sözdizimi (Gherkin BDD Syntax):**
   - `outputs/bdd_generator.py` içinde birden fazla `Feature:` bloğu üretilmesi engellendi. Üretilen tüm senaryolar tek bir ana `Feature: AutoReq Yazılım Gereksinim Test Senaryoları` bloğu altında toplanarak Cucumber, Behave ve pytest-bdd gibi standart Gherkin test koşucularıyla %100 uyumlu hale getirildi.

5. **Türkçe User Story ve Kabul Kriteri Şablonları (Turkish User Story Templates):**
   - `outputs/exporters.py` dosyasındaki DOCX dışa aktarım şablonu Türkçe standartlarına uyarlandı.
   - İngilizce `As a [role], I want [goal] so that [benefit].` şablonu `Bir [rol] olarak, [fayda] amacıyla [hedef] istiyorum.` şeklinde ve `Acceptance Criteria` başlığı `Kabul Kriterleri:` olarak değiştirildi.

6. **Story Points Skor Eşlemesi (Score Point Mapping):**
   - `outputs/backlog_generator.py` içindeki Fibonacci tabanlı Story Points (SP) eşlemesinde 8 SP için gereken minimum skor 5.0'dan 4.0'a düşürüldü. Böylece çelişkili olmayan durumlardaki matematiksel erişilememe problemi giderilerek yüksek öncelikli gereksinimlerin 8 SP alabilmesi sağlandı.

7. **Oturum İzoleli LLM Sayaçları (Session-Isolated Counters):**
   - `modules/llm_client.py` içindeki global `_pending_tokens` ve `_pending_cost` değişkenleri kaldırılarak yerine Streamlit session ID bazlı çalışan bir sözlük (`_session_usages`) ve thread-local storage (`_thread_local`) mimarisi kuruldu.
   - Bu sayede çoklu kullanıcı ortamında farklı tarayıcı sekmelerinden gelen LLM kullanım ve maliyet verilerinin birbirine karışması (multi-user data leakage) tamamen engellendi.

8. **Güvenli Bağımlılık Güncellemeleri (Dependency CVE Upgrades):**
   - `requirements.txt` dosyasındaki tüm paket sürümleri `==` ile kilitlendi. Python 3.14.5 ile uyumlu güncel ve güvenli kütüphane sürümleri (`streamlit==1.57.0`, `nltk==3.9.4`, `stanza==1.11.1`, `scikit-learn==1.8.0`, vb.) tanımlanarak CVE açıkları giderildi ve duplicate tanımlamalar temizlendi.

9. **Etiketleme Yanlılığı ve Metrik Tutarlılığı (Annotation Bias Mitigation):**
   - `docs/annotation_guidelines.md` kılavuzu oluşturuldu. Burada iki bağımsız etiketleyici (rater) arasındaki karar uyumunu ölçen Cohen's Kappa ($\kappa$) hesaplama adımları, formülü, yorumlama aralıkları ve metrik uyumsuzluklarını düzeltme süreçleri tanımlandı.

### Doğrulama ve Test Sonuçları

- Birim ve çıktı testleri (`pytest`) başarıyla tamamlanmıştır (62 passed).
- Dev ve Held-out veri kümesi değerlendirme betikleri koşturularak başarı oranları raporlanmıştır:
  - **Dev Corpus Sınıflandırma Doğruluğu:** 59/63 = **%93.7**
  - **Healthcare Held-out Corpus Sınıflandırma Doğruluğu:** 29/30 = **%96.7**
  - Sonuçlar `reports/dev_corpus_results.json` ve `reports/heldout_corpus_results.json` dosyalarına kaydedilmiştir.
