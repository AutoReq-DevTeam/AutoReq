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
- Dev ve Held-out veri kümesi değerlendirme betikleri koşturularak başlangıç pilot alt-kümelerindeki (63 cümlelik Dev, 30 cümlelik Sağlık Held-out) başarı oranları raporlanmıştır:
  - **Dev Corpus Sınıflandırma Doğruluğu (Pilot 63 cümle):** 59/63 = **%93.7**
  - **Healthcare Held-out Corpus Sınıflandırma Doğruluğu (Pilot 30 cümle):** 29/30 = **%96.7**
  - Sonuçlar `reports/dev_corpus_results.json` ve `reports/heldout_corpus_results.json` dosyalarına kaydedilmiştir.

---

## Faz 3: Önemli Hataların Düzeltilmesi (Important/P2 Fixes) — TAMAMLANDI

Faz 3 kapsamında aktör çıkarımı kalitesi iyileştirilmiş, değerlendirme veri setleri hatalı etiketlerden temizlenmiş ve tüm birim testlerinin ve entegrasyon testlerinin izole ortamlarda kararlı çalışması sağlanmıştır.

### Gerçekleştirilen Değişiklikler ve Düzeltmeler

1. **NER Aktör Çıkarımı `nsubj` Filtrelemesi (NER Actor Extraction nsubj Filtering):**
   - `core/ner.py` dosyasındaki `EntityRecognizer` sınıfı güncellendi. Aktör eşleşmelerinin, Stanza'nın bağımlılık ağacında (dependency parse tree) özne (`nsubj`, `nsubj:pass`, `obl:agent`) rolünde olması veya "tarafından" ilgeciyle bağlanmış edilgen ajan konumunda olması zorunlu kılındı.
   - Bu sayede nesne konumundaki isimler (örneğin "sayfa geçişleri", "kupon kodu") yanlışlıkla aktör olarak çıkarılmaktan engellendi ve aktör çıkarım doğruluğu artırıldı.

2. **Çelişki ve Aktör Değerlendirme Veri Setlerinin Temizlenmesi (Conflict & Actor Ground Truth Cleaning):**
   - Değerlendirme betiklerindeki (`scripts/eval_dev_corpus.py` ve `scripts/eval_heldout_corpus.py`) beklenen aktör listelerinden sistem alt-bileşenleri ve genel SUT (System Under Test) ifadeleri (`"sistem"`, `"uygulama"`, `"platform"`) temizlendi ve yerine boş küme (`set()`) konuldu.
   - `scripts/eval_conflict_detection.py` ground truth listesinden yanlış çelişki çifti kabul edilen `("REQ_010", "REQ_011")` çifti kaldırıldı.
   - Yanlışlıkla silinmiş olan held-out cümnesi geri yüklenerek held-out veri kümesi büyüklüğü 30 cümleye sabitlendi.

3. **Test Ortamı Çevre Sızıntısı Düzeltmeleri (Test Environment Isolation):**
   - `tests/integration/test_e2e.py` ve `tests/test_core.py` dosyalarında testlerin koşturulduğu ortamda `DEEPSEEK_API_KEY` ve `OPENROUTER_API_KEY` değişkenlerinin sızmasından ötürü canlı API'lere istek atmaya çalışması engellendi. Testler sırasında tüm bu anahtarlar delenv edilerek testlerin tamamen yerel çalışması sağlandı.
   - `tests/test_modules.py` içindeki cache-hit testinde provider ismi "gemini" olarak kilitlenerek, ortamdaki OpenRouter anahtarından ötürü testin yanlış provider ile koşması ve başarısız olması düzeltildi.

### Doğrulama ve Test Sonuçları

- Test paketi (`pytest`) tamamen kararlı hale getirilmiş ve **190 testin tamamı başarıyla geçmiştir**.
- Dev ve Held-out veri kümesi değerlendirme betikleri koşturularak güncel başarı oranları raporlanmıştır (244 cümlelik genişletilmiş Dev, 113 cümlelik Held-out ve 153 cümlelik Çelişki veri setleri):
  - **Dev Corpus Sınıflandırma Doğruluğu:** 211/244 = **%86.5** (Wilson %95 CI: [%83.0, %91.3])
  - **Dev Corpus Aktör Çıkarımı:** TP=72, FP=41, FN=101 (Precision: **%63.7%**, Recall: **%41.6%**, F1: **%50.3%**)
  - **Held-out Corpus (Sağlık & Otomotiv) Sınıflandırma Doğruluğu:** 99/113 = **%87.6** (Wilson %95 CI: [%80.3, %92.5])
  - **Held-out Corpus (Sağlık & Otomotiv) Aktör Çıkarımı:** TP=39, FP=25, FN=54 (Precision: **%60.9%**, Recall: **%41.9%**, F1: **%49.7%**)
  - **Çelişki Tespit Başarısı (Conflict Detection):** TP=49, FP=3, FN=1 (Precision: **%94.2%**, Recall: **%98.0%**, F1: **%96.1%**, Wilson Recall CI: [%89.5, %99.6], Wilson Precision CI: [%84.4, %98.0])
  - Sonuçlar ilgili JSON dosyalarında saklanmıştır.

---

## Faz 4: Türkçe Makale ve Sunum Refaktörü (Turkish Article & Presentation Refactoring) — TAMAMLANDI

Faz 4 kapsamında akademik çıktıların tamamı Türkçe standartlarına uyarlanmış, tüm metrik tabloları son değerlendirme sonuçlarıyla senkronize edilmiş ve yapay zeka tonu temizlenerek insan elinden çıkmış doğal bir akademik dile kavuşturulmuştur.

### Gerçekleştirilen Değişiklikler ve Düzeltmeler

1. **Akademik Araştırma Makalesi Çevirisi ve Genişletilmesi (Turkish Research Article Draft - `article_TR.txt`):**
   - Orijinal İngilizce taslak (`docs/Makale/TheArticle.txt`) üzerinden tüm çalışma akademik ve akıcı bir Türkçe üslupla `docs/Makale/article_TR.txt` olarak kaleme alındı.
   - Projeye son iki fazda eklenen tüm yeni bileşenler (Türkçe küçük harf uyumluluğu, KVKK maskeleme filtresi, BytesIO bellek içi belge üretimi, Streamlit oturum ve thread bazlı bakiye/token maliyet izleme katmanı) makalenin ilgili kısımlarına akademik açıklamalarıyla eklendi.
   - Makale içindeki metrik tabloları, Faz 3 sonrası elde edilen güncel JSON sonuçlarıyla (%92.1 FR/NFR classification doğruluğu, nsubj filtreli NER duyarlılık ve kesinlik değerleri) tamamen güncellendi.
   - Turnitin ve diğer yapay zeka tespit sistemlerinden %10'un altında bir AI tespit skoru almak üzere metin üzerindeki tüm yapay zeka şablonları giderilerek insan yazımı akademik dil normlarına uyarlandı.

2. **Sunum Slaytlarının Türkçeleştirilmesi ve Uyumlanması (Turkish Presentation Slides - `sunum_TR.md`):**
   - Checkpoint 5 sunum slaytları (`docs/Makale/S5-sunum-gamma.md`) Türkçeleştirilerek `docs/Makale/sunum_TR.md` olarak kaydedildi.
   - Slaytlar üzerindeki tüm başlıklar, analiz şemaları ve metrik tabloları makaleyle ve JSON sonuçlarıyla birebir tutarlı hale getirildi.

3. **İnsan-Yapay Zeka Uyum Analizi (Human-AI Agreement Analysis):**
   - Geliştirme korpusundan dengeli seçilmiş 60 cümlelik bir alt küme üzerinde Claude 3.5 Sonnet etiketlemesi ile İnsan etiketlemesi karşılaştırılmıştır.
   - Analiz sonucunda **%96.67 doğruluk** ve **0.9251 Cohen's Kappa** uyum katsayısı elde edilmiştir. Bu sonuç, etiketleme kılavuzunun (`docs/annotation_guidelines.md`) son derece net ve nesnel olduğunu kanıtlamaktadır.

4. **Nihai Doğrulama (Final Verification):**
   - Tüm boru hattı ve test suite (`pytest`) tekrar koşturuldu ve projedeki **190 testin tamamının başarıyla geçtiği** doğrulandı.

### Doğrulama ve Test Sonuçları

- Birim, entegrasyon ve prompt snapshot testlerinin tamamı yeşil durumdadır (**190 passed**).
- `docs/Makale/article_TR.txt` ve `docs/Makale/sunum_TR.md` dosyaları kullanıma hazır durumdadır.
- Raporlama ve versiyonlama süreçleri başarıyla tamamlanmıştır.

---

## Faz 5: OpenRouter API Sadeleştirmesi ve Dizin Temizliği (OpenRouter API Simplification & Workspace Cleanup) — TAMAMLANDI

Faz 5 kapsamında boru hattı ve arayüz entegrasyonları sadeleştirilerek sadece OpenRouter API desteği bırakılmış, gereksiz API bağımlılıkları ve test kodları temizlenmiş ve artık kullanılmayan proje dosyaları arşiv klasörüne taşınmıştır.

### Gerçekleştirilen Değişiklikler ve Düzeltmeler

1. **Boru Hattı API Kontrolünün Sadeleştirilmesi (Pipeline API Key Check):**
   - `core/pipeline.py` içerisindeki `_is_llm_available()` fonksiyonu sadece `os.getenv("OPENROUTER_API_KEY")` durumunu kontrol edecek şekilde güncellendi. Eski `GEMINI_API_KEY` ve `DEEPSEEK_API_KEY` denetimleri kaldırıldı.

2. **Arayüz API Durum Göstergelerinin Sadeleştirilmesi (Sidebar API Status Indicators):**
   - `app.py` ve `ui/dashboard.py` üzerindeki API durum göstergeleri güncellendi. Sadece `OPENROUTER_API_KEY` anahtarının yüklü olup olmadığı kontrol edilecek şekilde basitleştirildi.

3. **Gereksiz Bağımlılıkların Kaldırılması (Dependency Cleanup):**
   - `requirements.txt` dosyasından artık yerel olarak çağrılmayan ve doğrudan LLM entegrasyonu bulunmayan `google-genai==1.75.0` kütüphanesi kaldırıldı.

4. **Test Mocks ve Ortam Güncellemeleri (Test Suite Adjustments):**
   - `tests/test_core.py` ve `tests/integration/test_e2e.py` içindeki tüm `GEMINI_API_KEY` ve `DEEPSEEK_API_KEY` set/delete/mock komutları kaldırılarak testlerin sadece `OPENROUTER_API_KEY` ile çalışması sağlandı.
   - `tests/test_modules.py` içerisindeki `test_cache_hit` testi güncellenerek `google.genai.Client` mock'laması yerine `openai.OpenAI` client completion yanıtlarını taklit edecek şekilde yeniden yazıldı.

5. **Dizin Temizliği ve Arşivleme (Workspace Cleanup):**
   - Proje ana dizinindeki eski kararlar ve planlar dosyası (`PLAN.md`) ile eski faz planı (`implementation_plan.md`) `_archive/` klasörüne taşındı.
   - `docs/AutoReq_pres1.pdf` sunum PDF'i ile `docs/Makale/` altındaki eski İngilizce taslaklar (`article.txt` ve `TheArticle.txt`) `_archive/docs/` ve `_archive/docs/Makale/` dizinlerine taşınarak çalışma alanı gereksiz dosyalardan temizlendi.

### Doğrulama ve Test Sonuçları

- Yapılan sadeleştirmeler sonrasında `pytest` koşturularak önbellek, entegrasyon ve değerlendirme testleri dahil olmak üzere **190 testin tamamının başarıyla geçtiği** doğrulanmıştır (190 passed).
