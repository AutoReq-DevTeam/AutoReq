# Hibrit Yapay Zeka Destekli Gereksinim Mühendisi

**Özet**—Yazılım geliştirme süreçlerinde kritik bir öneme sahip olan gereksinim analizinde geleneksel yöntemler kullanmak oldukça zaman alıcıdır ve insan kaynaklı hatalara açıktır. Bu projede, Doğal Dil İşleme (Natural Language Processing - NLP) ve Büyük Dil Modeli (Large Language Models - LLM) teknolojilerini birleştirerek hibrit bir sistem sunulmaktadır. Sistem; metin ön işlemesi için NLP, mantıksal çelişki tespitleri ve otomatik belge üretimi için LLM kullanmaktadır. Proje, gereksinim mühendisliği aşamasındaki iş yükünü azaltıp kaliteyi arttırmayı hedeflemektedir. 

**Anahtar Kelimeler**—Yazılım Gereksinim Mühendisliği, Natural Language Processing, Large Language Model, Otomatik Metin Analizi, Software Requirements Specification, Çelişki Tespiti

## I. GİRİŞ

Günümüz yazılım projelerindeki başarısızlıkların birçoğu, manuel olarak yönetilen gereksinimlerin yanlış veya eksik tanımlanmış olmasından kaynaklanır. Manuel olarak yürütülen gereksinim mühendisliği süreçleri mantıksal hatalara son derece açıktır ve yüzlerce kuralın birbiriyle çelişip çelişmediğini saptamak insan gözüyle oldukça zordur. 

Bu çalışmada geliştirilen "AutoReq", geleneksel Doğal Dil İşleme (NLP) metotları ile Büyük Dil Modellerinin (LLM) mantıksal ayrıştırma gücünü birleştirip hibrit bir yaklaşım sunar. Sistem, ham metinlerden aktör ve nesneleri çıkarır, fonksiyonel gereksinimleri sınıflandırır ve mantık hatalarını raporlar. Analiz sonucunda ISO/IEC/IEEE 29148 standartlarına uygun Yazılım Gereksinim Spesifikasyonu (Software Requirements Specification - SRS) belgeleri ve Davranış Güdümlü Geliştirme (Behavior Driven Development - BDD) test senaryolarını dinamik olarak oluşturur.
 
Projenin geri kalanı şu şekilde planlanmıştır: Bölüm II’de sistem mimarisi ve metodolojisi sunulmaktadır. Bölüm III’te elde edilen analiz sonuçları ve sistemin performansı tartışılmaktadır. Son bölümde ise gelecek çalışmalar ve sonuçlar yer almaktadır.

## II. KULLANIM KOLAYLIĞI

AutoReq, karmaşık yazılım gereksinim analizi süreçlerini otomatikleştirerek yazılım ekipleri için yüksek düzeyde kullanım kolaylığı sağlar. Sistem, teknik olmayan paydaşların bile gereksinimleri kolayca analiz etmesine ve doğrulanmış belgeler elde etmesine olanak tanır.

**A. Spesifikasyon Bütünlüğünün Korunması**

Gereksinim mühendisliğinde spesifikasyonların bütünlüğünün korunması kritik bir adımdır. AutoReq, insan kaynaklı hataları minimize ederek gereksinimler arasındaki mantıksal çelişkileri otomatik olarak tespit eder. NLP ve LLM tabanlı hibrit motoru sayesinde sistem, tanımlanan fonksiyonel gereksinimlerin birbiriyle çatışmamasını garanti altına alır. Bu yaklaşımla üretilen SRS belgeleri ve BDD test senaryoları, standartlar dahilinde projenin tutarlılığını ve güvenilirliğini sürekli olarak korur.
