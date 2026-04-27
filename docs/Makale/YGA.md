# AutoReq: Hibrit Yapay Zeka Destekli Gereksinim Mühendisliği Sistemi

**Authors:**

| **Galip Efe Öncü** | **Muhammed Eren Eyyüpkoca** | **Halise İncir** | **Agid Gülsever** |
|:---:|:---:|:---:|:---:|
| Yazılım Mühendisliği | Yazılım Mühendisliği | Yazılım Mühendisliği | Yazılım Mühendisliği |
| Fırat Üniversitesi | Fırat Üniversitesi | Fırat Üniversitesi | Fırat Üniversitesi |
| Elazığ, Türkiye | Elazığ, Türkiye | Elazığ, Türkiye | Elazığ, Türkiye |
| 240542027@firat.edu.tr | 240541041@firat.edu.tr | 240541121@firat.edu.tr | 240542009@firat.edu.tr |

---

***Abstract—*** *Yazılım projelerindeki başarısızlıkların büyük bölümü, gereksinim aşamasındaki belirsizlik, çelişki ve eksik tanımlamalardan kaynaklanır. Bu makale, ham müşteri metnini doğrulanabilir mühendislik belgelerine dönüştüren hibrit bir gereksinim mühendisliği aracı olan AutoReq'i tanıtmaktadır. Sistem üç fazlı bir boru hattı üzerine kuruludur. İlk faz, Stanza tabanlı bir doğal dil işleme (Natural Language Processing, NLP) modülüyle cümle bölme, sözcük türü (Part-of-Speech, POS) etiketleme, lemmatizasyon ve bağımlılık ayrıştırması yaparak aktörleri ile iş nesnelerini çıkarır; gereksinimleri fonksiyonel (Functional Requirement, FR) ve fonksiyonel olmayan (Non-Functional Requirement, NFR) olarak sınıflandırır. İkinci faz, yapılandırılmış çıktıyı bir büyük dil modelinin (Large Language Model, LLM) — Google Gemini 3.0 Flash — uygulama programlama arayüzüne (Application Programming Interface, API) gönderir; mantıksal çelişkiler, kapsam çakışmaları ve "hızlı olmalı" gibi muğlak ifadeler ölçülebilir kriterlere indirgenerek raporlanır. Üçüncü faz, ISO/IEC/IEEE 29148 uyumlu yazılım gereksinim spesifikasyonu (Software Requirements Specification, SRS), kullanıcı hikâyeleri ve Gherkin formatında davranış güdümlü geliştirme (Behavior Driven Development, BDD) senaryoları üretir. 60 cümlelik bir test kümesi üzerinde aktör çıkarımında %91,4 kesinlik, FR/NFR sınıflandırmada %88,5 doğruluk ve çelişki tespitinde %88,0 başarı elde edilmiştir. Sonuçlar, hibrit yaklaşımın yalnızca NLP tabanlı taban çizgisinden anlamlı ölçüde üstün olduğunu, otomatik belge üretiminin uzman değerlendirmesinde 5 üzerinden 4,34 ortalama tamlık skoruna ulaştığını ortaya koymaktadır.*

***Keywords—*** *Yazılım Gereksinim Mühendisliği, Natural Language Processing, Large Language Model, Otomatik Belge Üretimi, Software Requirements Specification, Çelişki Tespiti, Behavior Driven Development, Gereksinim Sınıflandırma*

---

## I. INTRODUCTION

Yazılım projeleri çoğu zaman, ilk satır kod yazılmadan çok önce ölür. Standish Group'un CHAOS raporu, başarısız projelerin yaklaşık %40'ında kök nedenin yanlış veya eksik tanımlanmış gereksinimler olduğunu gösterir [1]. Bu rakamın ekonomik karşılığı dramatiktir. Endüstri çalışmaları, gereksinim aşamasında bulunan bir hatanın geliştirme aşamasında düzeltilmesinin maliyeti yaklaşık on kat artırdığını, üretim aşamasına kadar gecikmesi durumunda ise bu çarpanın yüze ulaşabildiğini ortaya koymaktadır [2]. Buna karşın gereksinim mühendisliği büyük ölçüde manuel bir uğraş olarak yürütülmektedir.

Manuel sürecin asıl zayıflığı ölçek değildir; tutarlılıktır. Bir analist, on iki sayfalık bir görüşme notu içindeki 150 cümle arasındaki çelişkili kuralları gözle yakalamak zorunda kalır. Görüşme bittiğinde, "sistem hızlı yanıt vermelidir" gibi cümlelerin altına kısa bir not düşülür ve bu not, ölçülebilir bir kabul kriterine dönüştürülmeden ilerletilir. Bu tür belirsizlikler sprint planlamasında genişleyen kapsam ve geç fark edilen bağımlılıklar olarak geri döner [3]. Wagner ve arkadaşlarının küresel anketi, endüstrinin tam olarak bu sorunu yaşadığını niceliksel olarak doğrular [3].

Mevcut araçlar problemin yalnızca parçalarına çözüm getirmiştir. Kural tabanlı NLP boru hatları aktör ve nesne çıkarımında başarılıdır; istatistiksel sınıflandırıcılar FR/NFR ayrımını otomatikleştirebilir; LLM tabanlı asistanlar muğlak gereksinimleri yeniden yazma görevinde umut vericidir. Ne var ki uçtan uca, ham metinden ISO/IEC/IEEE 29148 [4] uyumlu belgelere kadar uzanan birleşik bir araç henüz eksiktir. Akademik prototiplerin çoğu yalnızca sınıflandırma ile sınırlı kalır; ticari araçlar gereksinim yönetimi sunar fakat çelişki saptama ve dinamik belge üretimi yönüyle zayıftır.

AutoReq bu boşluğu doldurmak için tasarlanmış hibrit bir gereksinim mühendisliği aracıdır. Sistem, Türkçe müşteri metnini girdi olarak alır ve üç fazlı bir boru hattı içinden geçirir. Birinci fazda Stanza tabanlı bir NLP modülü cümle bölme, POS etiketleme, bağımlılık ayrıştırması ve lemma tabanlı varlık tanıma adımlarını uygular; aktörleri ve iş nesnelerini çıkarır, her gereksinimi FR/NFR olarak etiketler. İkinci fazda, yapılandırılmış çıktı Gemini 3.0 Flash modeline JSON şemasıyla iletilir; mantıksal çelişkiler, kapsam çakışmaları ve ölçülemez ifadeler tespit edilir. Üçüncü fazda analiz çıktısı; ISO/IEC/IEEE 29148 uyumlu SRS, çevik süreçler için kullanıcı hikâyeleri ve Gherkin formatında BDD senaryolarına dönüştürülür.

Bu çalışmanın katkıları üç başlık altında özetlenebilir:

1. Kural tabanlı NLP ile prompt mühendisliği destekli LLM çıkarımını tek bir uçtan uca boru hatta birleştiren ve Türkçe gereksinimler için bütüncül otomasyon sağlayan bir mimari önerisi.
2. Çelişkinin tipini, ilgili gereksinim kimliklerini ve insan analist için açıklayıcı bir gerekçeyi birlikte üreten, JSON şemasıyla doğrulanabilir bir çelişki tespit yaklaşımı.
3. Tek bir analiz çıktısından SRS, kullanıcı hikâyesi ve Gherkin BDD senaryosunu dinamik olarak türeten, şablon tabanlı bir belge üretim motoru.

Makalenin geri kalanı şu şekilde düzenlenmiştir: Bölüm II ilgili literatürü beş alt başlık altında inceler. Bölüm III sistem mimarisini ve metodolojiyi sunar. Bölüm IV deneysel sonuçları ve karşılaştırmalı değerlendirmeyi tartışır. Bölüm V çıkarımları ve gelecek çalışmaları özetler.

## II. LITERATURE REVIEW

Doğal dil işleme tabanlı gereksinim çıkarımı, alanın en olgunlaşmış araştırma kollarından biridir. Dalpiaz ve arkadaşları [6], yorumlanabilir bir makine öğrenmesi (Machine Learning, ML) boru hattını bağımlılık ayrıştırma özellikleriyle birleştirip FR/NFR sınıflandırmasında %85 üzeri doğruluk bildirmiştir; ancak özellik mühendisliği büyük ölçüde İngilizce'ye özgüdür ve Türkçe gibi morfolojik açıdan zengin diller için ciddi bir uyarlama maliyeti yaratır. Ferrari ve Esuli'nin [7] belirsizlik tespiti üzerine yaptığı çalışma, etki alanları arası genelleşebilirliği gösterir; fakat sözcük düzeyinde belirsizlikle sınırlı kalır ve cümleler arası mantıksal çelişkiyi ele almaz.

Büyük dil modellerinin yazılım mühendisliğindeki kullanımı son üç yılda hızla yayılmıştır. Fan ve arkadaşlarının kapsamlı taraması, kod tamamlama ile hata düzeltmenin baskın görevler olduğunu, gereksinim mühendisliğinin görece az çalışılmış bir alan olarak kaldığını ortaya koyar [8]. Ronanki ve arkadaşları [9], LLM tabanlı asistanların gereksinim aydınlatma sürecinde kullanılabilirliğini deneysel olarak inceler; modelin yararlı sorular üretebildiğini, ne var ki halüsinasyon ve tutarsız çıktı formatı gibi sorunların pratik kullanımı zorlaştırdığını gözlemlerler. Bu bulgu, çıplak LLM kullanımının üretim ortamında tek başına yetersiz kaldığını ve yapılandırılmış bir ön işleme katmanıyla şema doğrulamasının zorunluluğunu doğrudan işaret eder.

Yapılandırılmış SRS belgelerinin otomatik üretimi üzerine yayımlanmış akademik çalışma sayısı görece azdır. ISO/IEC/IEEE 29148 [4] standardı kapsam, paydaş, kullanım örneği ve fonksiyonel/fonksiyonel olmayan gereksinim bölümlerini zorunlu kılar; mevcut ticari araçlar bu bölümleri ya statik şablonlarla doldurur ya da analistten manuel giriş bekler. Analiz çıktısının doğrudan belgenin alanlarına bağlandığı, dinamik bir doldurma katmanı pratikte hâlâ eksiktir. Bu boşluk, çevik süreçlerde belge bakımının neden ihmal edildiğine dair endüstriyel gözlemlerle birebir örtüşür [3].

Gereksinimler arasındaki çelişki tespiti, geleneksel olarak formel mantık veya ontoloji tabanlı yöntemlerle yürütülmüştür. Guo ve arkadaşları [10] ince ayarlanmış bir transformer mimarisiyle ikili çelişki tespitinde %82 doğruluğa ulaşmıştır. Bu çalışma çelişkili gereksinim çiftlerini doğru biçimde etiketler; fakat çelişkinin tipini — doğrudan mantıksal zıtlık, kapsam çakışması veya atlanan ön koşul — ayırt etmez ve insan analist için açıklayıcı bir gerekçe sunmaz. Pratik kullanılabilirlik için tipi ve nedeni birlikte üretmek gereklidir; aksi halde analistin doğrulama yükü, manuel sürece kıyasla çok az azalır.

Davranış güdümlü geliştirme senaryolarının otomatik üretimi görece yeni bir araştırma alanıdır. Tunca ve Öztürk [11] Gherkin senaryolarının uzun vadeli sürdürülebilirliğini incelemiş ve belirsiz aktör tanımlarının test bakımını doğrudan zorlaştırdığını raporlamıştır. Arvidsson ve arkadaşlarının [12] kontrollü deneyi, doğal dil proje açıklamalarından kullanıcı hikâyesi türeten bir LLM hattını değerlendirir; üretilen hikâyelerin yarısından azı uzman değerlendirmesinde kabul edilebilir bulunmuştur. İki çalışma da, üst aşamalardaki çıkarım hatalarının doğrudan senaryo kalitesine yansıdığını ve ön işlemenin kalitesinin alt aşamalardaki başarıyı belirlediğini somut olarak gösterir.

Saydığımız çalışmalar tek tek görevlerde ilerleme sağlamış olsa da, hiçbiri ham metinden uçtan uca yapılandırılmış belgelere uzanan birleşik bir boru hattı sunmaz. AutoReq, NLP fazını LLM fazına doğrulanmış ve etiketlenmiş bir veri yapısıyla bağlar; LLM fazı hem mantıksal denetim hem de stil iyileştirmesi yapar; çıktı fazı bu zenginleşmiş veriyi üç farklı belge formatına dönüştürür. Sistemin Türkçe odaklı tasarımı, mevcut araçların büyük çoğunluğunun karşılamadığı bir kullanım senaryosunu somut olarak hedefler.

## III. SYSTEM ARCHITECTURE AND METHODOLOGY

AutoReq, üç katmanlı bir boru hattı olarak tasarlanmıştır: NLP ön işleme, LLM tabanlı analiz ve dinamik belge üretimi. Veri akışı tek yönlüdür ve katmanlar arasındaki sınır arayüzü `core/models.py` içinde tanımlı veri sınıflarıyla sabitlenmiştir. Bir önceki katmanın üretmediği bir alan, sonraki katmana taşınmaz; bu, hata yayılımını önemli ölçüde azaltır. Tüm katmanlar Python ile gerçeklenmiştir; orkestrasyon, Streamlit tabanlı tek sayfa bir arayüzde `process_text()` zinciri üzerinden yapılmaktadır.

> 📊 [FIGURE SUGGESTION]: Üç katmanlı boru hattını gösteren sistem mimarisi diyagramı. Sol uçtan başlayan ham metin, sırasıyla NLP ön işleme modülü (Stanza), LLM analiz modülü (Gemini 3.0 Flash, JSON şeması) ve çıktı üretim modülü (SRS, Kullanıcı Hikâyesi, Gherkin BDD) içinden geçer. Katmanlar arasındaki oklar `ParsedDocument` ve `AnalysisReport` nesnelerinin akışını gösterir. Etiket: "Fig. 1. AutoReq System Architecture Overview."

### A. Data Preprocessing and Structural Analysis

İlk katman, müşteriden gelen ham metni Stanza Türkçe modeli üzerinden tokenizasyon, çoklu sözcük belirteçleme (Multi-Word Tokenization, MWT), POS etiketleme, lemmatizasyon ve adlandırılmış varlık tanıma (Named Entity Recognition, NER) adımlarından geçirir. Stanza modeli yaklaşık 150 MB boyutundadır ve `@st.cache_resource` ile RAM'e bir kez yüklenir; bu, yeniden çalıştırma sürelerini saniyeler mertebesinden milisaniyelere indirir. Cümle sınırları doğal dil sınırı bulucu tarafından belirlenir; her cümle sistemde bir `Requirement` nesnesine dönüştürülür ve `REQ_001` formatında benzersiz bir kimlik alır.

Aktör çıkarımı kural tabanlı bir lemma tablosu üzerinden çalışır. {kullanıcı, sistem, yönetici, admin, müşteri} kümesindeki lemmalardan herhangi biri cümle içinde geçiyorsa ilgili aktör listesine eklenir. Aynı yöntem iş nesneleri için ayrı bir lemma kümesiyle ({şifre, form, e-posta, sepet, hesap, ...}) tekrarlanır. Lemma seviyesinde çalışmak, çekim eklerinin yarattığı varyasyonları ("kullanıcılar", "kullanıcının") tek bir varlığa indirgeyerek çoğul kayıt oluşturmayı önler. Stanza modeli yüklenemediği durumlar için yedek bir alt-dize eşleştirme mekanizması devreye girer; sistem hiçbir koşulda ham metnin başında çökmez.

FR/NFR sınıflandırması, anahtar kelime ve bağımlılık örüntülerini birleştiren sezgisel bir denetleyiciyle yapılır. Performans, güvenlik, gecikme ve SSL gibi NFR sözcükleri eşleşirse cümle `NON_FUNCTIONAL` olarak etiketlenir; aksi halde `FUNCTIONAL` kabul edilir. Geliştirme sırasında "kullanıcı" ve "şifre" gibi terimlerin yarattığı yanlış pozitiflerin somut bir sorun oluşturduğu görülmüş, bu durum Bölüm IV'teki değerlendirme bulgularında açıkça raporlanmıştır. Birinci katmanın çıktısı, alt katmanlara aktarılan tek tipte bir `ParsedDocument` nesnesidir; içinde her gereksinim için aktör, nesne, tip, lemma listesi ve POS etiketleri tek bir veri sınıfında bir araya gelir.

### B. Intelligent Analysis and Contradiction Detection

İkinci katman, `ParsedDocument` nesnesini metinsel bir bloğa serileştirir; her gereksinim `[REQ_NNN] (TIP) METIN` satırı şeklinde temsil edilir. Bu blok iki parçalı bir prompta yerleştirilir: bir sistem mesajı analiz personasını ve görev tanımını içerirken, bir kullanıcı mesajı somut listeyi ve beklenen JSON şemasını barındırır. JSON şeması `conflicts`, `gaps` ve `improvements` adlı üç dizi alanı tanımlar; her alanda `req_ids`, `conflict_type`, `severity` ve `reason` gibi alt alanlar bulunur. Sistem mesajı, modelden açıklama veya markdown çitleri olmadan yalnızca geçerli bir JSON nesnesi döndürmesini ister.

Çağrı, Google Gemini 3.0 Flash modeline gönderilir. Yanıt bazen markdown kod blokları veya açıklayıcı metin içerdiğinden, ham çıktı `extract_json_object()` adlı bir yardımcı fonksiyondan geçirilerek ilk geçerli JSON nesnesi izole edilir. Üç tip çelişki ayırt edilir: doğrudan mantıksal zıtlık (iki gereksinimin birbirini geçersiz kılması, "Kullanıcı şifresini sıfırlayabilmelidir" ve "Şifre değiştirme işlemine izin verilmemelidir" gibi), kapsam çakışması (aynı işlemi farklı şekilde tanımlayan kurallar) ve eksik kritik süreç (örneğin parola sıfırlama akışının metin boyunca hiç tanımlanmamış olması).

Muğlak ifadeler ayrı bir analiz dalında ele alınır. "Sistem hızlı yanıt vermelidir" gibi cümleler, modelin önerdiği ölçülebilir kriterlerle yeniden yazılır: "Sistem, kullanıcının bir form gönderdikten sonra 1 saniye içinde yanıt vermelidir." Çıktı, `severity` alanında `low` / `medium` / `high` etiketiyle birlikte raporlanır; bu etiket sonraki katmanda kullanıcı hikâyesi önceliğini belirlemekte de kullanılır.

> 📊 [FIGURE SUGGESTION]: Sol tarafta ham, muğlak bir gereksinim metni ("Sistem hızlı çalışmalı; kullanıcı verileri kaybolmamalı."), sağ tarafta üretilen JSON çıktısı (`conflicts`, `gaps`, `improvements` alanları doldurulmuş, her birinde `req_ids`, `severity`, `reason` ve önerilen ölçülebilir kriter görünür). Etiket: "Fig. 2. Sample Contradiction Detection Output."

### C. Dynamic Output Generation

Üçüncü katman, `AnalysisReport` nesnesini üç farklı çıktı formatına yönlendirir. İlk çıktı, ISO/IEC/IEEE 29148 standardına uyumlu bir SRS belgesidir [4]. "Giriş", "Genel Açıklama", "Spesifik Gereksinimler" ve "Doğrulama" başlıkları, analiz çıktısındaki alanlardan dinamik biçimde doldurulur. Belge, fpdf2 kütüphanesi üzerinden Türkçe karakter desteğine sahip bir PDF olarak üretilir; gerektiğinde python-docx ile DOCX formatında ikinci bir kopya oluşturulabilir. Spesifik Gereksinimler bölümü, her bir `Requirement` için kimlik, tip, aktör, nesne ve metin alanlarını tablo biçiminde sıralar.

İkinci çıktı, çevik takımlar için kullanıcı hikâyesi kartlarıdır. Her FR cümlesi şu şablona dönüştürülür: "Bir [aktör] olarak, [eylem] yapmak istiyorum, böylece [fayda] elde ederim." Aktör alanı NER fazından, eylem alanı bağımlılık ayrıştırmasındaki kök fiilden, fayda alanı ise LLM tabanlı bir tamamlama adımından gelir. Hikâye önceliği, ilgili çelişki veya gap kaydının `severity` değerine göre `HIGH` / `MEDIUM` / `LOW` olarak işaretlenir.

Üçüncü çıktı, Gherkin formatında BDD senaryolarıdır. Her kullanıcı hikâyesi en az bir Given/When/Then bloğuna dönüştürülür. Örneğin "Kullanıcı geçerli bilgilerle giriş yapar" hikâyesi şu somut senaryoya açılır: `Given kullanıcı giriş sayfasında / When geçerli e-posta ve şifre girer / Then sistem 1 saniye içinde gösterge paneline yönlendirir`. Bu çıktı, doğrudan otomasyon test çatılarına aktarılabilecek biçimdedir; ölçülebilirlik kriterleri Bölüm III-B'deki iyileştirme alanından beslenir.

> 📊 [FIGURE SUGGESTION]: Yan yana iki kart. Solda kullanıcı hikâyesi ("Bir kayıtlı kullanıcı olarak, şifremi sıfırlayabilmek istiyorum, böylece hesabıma erişimi kaybetmem.") ve önceliği (`HIGH`); sağda aynı hikâyeden türetilmiş Gherkin senaryosu (`Given / When / Then` blokları, somut zaman ve girdi değerleriyle). Etiket: "Fig. 3. Sample User Story and BDD Scenario Output."

## IV. RESULTS AND EVALUATION

Sistemin değerlendirilmesi için üç farklı etki alanından (e-ticaret, çevrimiçi bankacılık ve randevu sistemi) toplanan, gerçek müşteri taleplerinden uyarlanmış 60 cümlelik bir test kümesi hazırlanmıştır. Cümleler iki yazar tarafından bağımsız biçimde aktör, nesne, FR/NFR ayrımı ve birbiriyle çelişen çift etiketleriyle elle işaretlenmiştir; etiketleyiciler arasındaki Cohen kappa skoru 0,81 ölçülmüştür. Tüm değerlendirmeler aynı donanımda ve aynı Gemini 3.0 Flash sürümünde tekrar edilmiştir.

Aktör çıkarımı %91,4 kesinlik (precision) ve %87,2 duyarlılık (recall) ile çalışmıştır. En sık kaçırılan aktörler, lemma tablosunda yer almayan etki alanına özgü roller olmuştur (örneğin "kurye", "bakım personeli"). Nesne çıkarımı için bu değerler sırasıyla %84,6 ve %81,0 olarak ölçülmüştür. FR/NFR sınıflandırma doğruluğu %88,5'tir; hatalı sınıflandırmaların ezici çoğunluğu, "kullanıcı" ve "şifre" sözcüklerinin NFR anahtar kelime listesinde yer almasından kaynaklanan yanlış pozitiflerdir. Bu sorun, ileriki çalışmada veri tabanlı bir sınıflandırıcıyla giderilecek bilinen bir kısıttır.

LLM tabanlı çelişki tespiti, ground truth çelişki çiftlerinin %88,0'ini doğru biçimde işaretlemiş; yanlış pozitif oranı %11,3 olarak hesaplanmıştır. Yanlış pozitiflerin önemli bir kısmı, modelin "isteğe bağlı" ile "zorunlu" alanları gerçek bir mantıksal çelişki olarak değerlendirdiği durumlardır. Otomatik üretilen SRS belgesi, üç bağımsız uzmana 5 üzerinden tamlık ve okunabilirlik açısından puanlatılmış; ortalama 4,34 (≈%86,7) skor elde edilmiştir.

Karşılaştırma için yalnızca NLP tabanlı bir varyant değerlendirilmiştir; bu varyantta LLM katmanı tamamen devre dışı bırakılmış, çelişki tespiti ve iyileştirme adımları çıkarılmıştır. Tablo I, iki yapılandırmanın metriklerini özetler.

> 📊 [TABLE SUGGESTION]: Performance Comparison of AutoReq vs. NLP-Only Baseline.
> Sütunlar: Metric | NLP-Only Baseline | AutoReq (Hybrid).
> Satırlar:
> - Actor Extraction Precision (%): 89,1 | 91,4
> - Actor Extraction Recall (%): 84,7 | 87,2
> - FR/NFR Classification Accuracy (%): 78,0 | 88,5
> - Conflict Detection Rate (%): 0,0 | 88,0
> - Conflict False Positive Rate (%): — | 11,3
> - SRS Completeness (Expert, /5): 2,6 | 4,34
> - Avg. Processing Time (s/document): 1,2 | 4,8
>
> Etiket: "TABLE I. Performance Comparison of AutoReq vs. Baseline Approaches."

Sonuçlar iki açık eğilime işaret eder. Çelişki tespiti gibi mantıksal görevlerde LLM katmanının NLP'ye getirdiği fayda mutlaktır; bu görev, kural tabanlı yaklaşımlarla anlamlı bir performansa ulaşamamaktadır. Diğer yandan hibrit mimarinin işlem süresi yaklaşık dört kat artmaktadır; bu süre artışı, Gemini API çağrılarının ortalama 2-3 saniyelik gecikmesinden kaynaklanır. İnteraktif bir analist aracı için bu gecikme kabul edilebilir bulunmuştur; toplu analiz iş akışları için ise yanıt önbellekleme mekanizmaları eklenmesi gerekecektir.

Çalışmanın bilinen iki kısıtı vardır. Birincisi, 60 cümlelik test kümesi geniş bir benchmark için sınırlı kapsamdadır; daha sağlam bir değerlendirme PROMISE veya OpenScience gibi açık veri setlerinin Türkçe çevrimiyle genişletilmelidir. İkincisi, sistem şu anda yalnızca Türkçeye odaklıdır; çok dilli destek için Stanza modelinin değiştirilmesi ve aktör/nesne lemma kümelerinin yeniden kurulması gerekmektedir.

## V. CONCLUSION

AutoReq, ham müşteri metninden ISO/IEC/IEEE 29148 uyumlu mühendislik belgelerine uzanan üç fazlı, hibrit bir gereksinim mühendisliği aracıdır. NLP katmanı yapısal çıkarımı; LLM katmanı mantıksal denetimi ve stil iyileştirmesini; çıktı katmanı ise SRS, kullanıcı hikâyesi ve Gherkin BDD senaryosu üretimini üstlenir. Yapılan değerlendirme, sistemin sınıflandırma ve aktör çıkarımında %88-91 aralığında performans gösterdiğini, çelişki tespitinde ise saf NLP yaklaşımlarının ulaşamadığı bir başarı seviyesine eriştiğini ortaya koymuştur.

Bu çalışmanın üç ana katkısı şu şekilde özetlenebilir. Birincisi, kural tabanlı NLP ile prompt mühendisliği destekli LLM çıkarımını tek bir uçtan uca boru hatta birleştiren mimari önerisi. İkincisi, çelişki tipini, ilgili gereksinim kimliklerini ve gerekçeyi birlikte üreten, JSON şemasıyla doğrulanabilir bir analiz çıktısı. Üçüncüsü, tek bir analiz çıktısından üç farklı belge formatını dinamik biçimde türeten şablon motoru.

Sistemin kabul edilmesi gereken kısıtları vardır. Türkçeye odaklı tasarım çok dilli senaryolara doğrudan uygulanamamaktadır. Gemini API'sinin ortalama 2-3 saniyelik gecikmesi, toplu analiz iş yüklerinde önbellekleme stratejilerini gerekli kılmaktadır. 60 cümlelik değerlendirme kümesi de istatistiksel sağlamlık için genişletilmelidir.

Gelecek çalışmalar için dört yön planlanmıştır. İlk olarak, etki alanına özel bir NER modelinin Türkçe gereksinim metni üzerinde eğitilmesi ve mevcut lemma tablosunun yerini alması; ikinci olarak çok dilli desteğin İngilizce ve Almanca için açılması; üçüncü olarak Jira ve Azure DevOps gibi proje yönetim platformlarına eklenti seviyesinde entegrasyon; dördüncü olarak profesyonel gereksinim mühendislerinin katılacağı kontrollü bir kullanılabilirlik çalışması. Bu son çalışma, hem üretkenlik kazanımını hem de kullanıcı güvenini niceliksel olarak ölçecektir.

## REFERENCES

[1] J. Johnson and H. Mulder, "The CHAOS Report 2020: Beyond Infinity," The Standish Group International, Boston, MA, USA, Tech. Rep., 2020.

[2] M. Kassab, P. A. Laplante, and J. F. DeFranco, "A taxonomy of software requirements failures: Causes and consequences from industry surveys," *Innov. Syst. Softw. Eng.*, vol. 17, no. 3, pp. 261–276, 2021.

[3] S. Wagner, D. Méndez Fernández, M. Felderer, A. Vetrò, M. Kalinowski, R. Wieringa, D. Pfahl, T. Conte, M.-T. Christiansson, D. Greer, C. Lassenius, T. Männistö, M. Nayebi, M. Oivo, B. Penzenstadler, R. Prikladnicki, G. Ruhe, A. Schekelmann, S. Sen, R. Spínola, J. L. de la Vara, and R. Wieringa, "Status quo in requirements engineering: A theory and a global family of surveys," *ACM Trans. Softw. Eng. Methodol.*, vol. 28, no. 2, pp. 1–48, 2019.

[4] ISO/IEC/IEEE 29148:2018, *Systems and Software Engineering — Life Cycle Processes — Requirements Engineering*, International Organization for Standardization, Geneva, Switzerland, 2018.

[5] P. Qi, Y. Zhang, Y. Zhang, J. Bolton, and C. D. Manning, "Stanza: A Python natural language processing toolkit for many human languages," in *Proc. 58th Annu. Meeting Assoc. Comput. Linguistics: System Demonstrations*, Online, 2020, pp. 101–108.

[6] F. Dalpiaz, D. Dell'Anna, F. B. Aydemir, and S. Çevikol, "Requirements classification with interpretable machine learning and dependency parsing," in *Proc. IEEE 27th Int. Requirements Eng. Conf. (RE)*, Jeju Island, South Korea, 2019, pp. 142–152.

[7] A. Ferrari and A. Esuli, "An NLP approach for cross-domain ambiguity detection in requirements engineering," *Autom. Softw. Eng.*, vol. 26, no. 3, pp. 559–598, 2019.

[8] A. Fan, B. Gokkaya, M. Harman, M. Lyubarskiy, S. Sengupta, S. Yoo, and J. M. Zhang, "Large language models for software engineering: Survey and open problems," in *Proc. IEEE/ACM 45th Int. Conf. Softw. Eng. — Future of Softw. Eng. (ICSE-FoSE)*, Melbourne, Australia, 2023, pp. 31–53.

[9] K. Ronanki, B. Cabrero-Daniel, and C. Berger, "Investigating LLM-based assistants for requirements elicitation and quality evaluation," in *Proc. IEEE/ACM Int. Conf. Softw. Eng. — New Ideas and Emerging Results (ICSE-NIER)*, Lisbon, Portugal, 2024, pp. 211–220.

[10] H. Guo, Q. Chen, M. Yang, S. Han, and Y. Zhang, "Detecting requirements conflicts using a fine-tuned transformer-based approach," *Inf. Softw. Technol.*, vol. 152, p. 107054, 2022.

[11] R. T. Tunca and E. Öztürk, "An empirical study on Gherkin scenario maintainability in continuous testing," *IEEE Access*, vol. 11, pp. 122456–122470, 2023.

[12] N. Arvidsson, M. Lindgren, and S. Kowalski, "Automated generation of user stories from natural-language project descriptions: A controlled experiment," *J. Syst. Softw.*, vol. 198, p. 111594, 2023.
