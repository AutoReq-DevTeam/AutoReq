# 🚀 AutoReq: Otomatik Yazılım Gereksinim Analizörü

Bu dosya, projenin teknoloji stratejisini, özellik listesini ve geliştirme yol haritasını içerir.

## 🧠 Teknoloji Stratejisi: Hibrit Yaklaşım (NLP + LLM)
AutoReq, performans ve maliyet verimliliği için geleneksel **NLP** tekniklerini, derin anlamsal analiz ve yaratıcı içerik üretimi için ise **LLM** (Large Language Models) teknolojisini bir arada kullanır.

### 🔍 NLP (Doğal Dil İşleme - spaCy / NLTK)
*Hız, yapısal analiz ve lokal veri işleme için kullanılır.*
- **Metin Ön İşleme:** Cümle bazlı tokenizasyon, temizleme ve normalizasyon.
- **Varlık Tespiti (NER):** Aktörlerin (Kullanıcı, Sistem) ve temel nesnelerin hızlıca yakalanması.
- **Yapısal Sınıflandırma:** Gereksinimlerin temel türlerine göre (Fonksiyonel / Teknik) ayrıştırılması.

### 🤖 LLM (Yapay Zeka - GPT / Llama / Claude)
*Mantıksal çıkarım, çelişki tespiti ve yaratıcı dökümantasyon için kullanılır.*
- **Çelişki & Belirsizlik Analizi:** Mantıksal zıtlıkların tespiti ve "muğlak" ifadelerin sezilmesi.
- **Eksiklik Analizi:** Sektörel bilgiye dayanarak eksik kalan senaryoların uyarılması.
- **İçerik Üretimi:** User Story, BDD Senaryosu ve SRS dökümanlarının profesyonel dille yazılması.

## 🛠 Temel Özellikler (MVP)
- [ ] **Metin Ayrıştırma (NLP):** Cümle bazlı ayrıştırma.
- [ ] **Sınıflandırma (NLP + LLM):** Hibrit model ile kategorizasyon.
- [ ] **Varlık Tespiti (NLP):** Aktör ve nesne haritalama.

## 🧠 Akıllı Modüller (LLM Destekli)
- [ ] **Çelişki Tespiti:** Mantıksal zıtlıkların uyarılması.
- [ ] **Eksiklik Analizi:** Standart şablonlara göre öneri sunma.
- [ ] **İyileştirme Önerileri:** Ölçülebilir kriterlere dönüştürme.

## 📂 Çıktılar (Outputs)
- [ ] **Otomatik SRS:** PDF formatında Yazılım Gereksinim Dökümanı.
- [ ] **User Stories:** LLM ile zenginleştirilmiş kullanıcı hikayeleri.
- [ ] **BDD Senaryoları:** Gherkin formatında test senaryoları.

## 🏗 Teknoloji Yığını
- **Dil:** Python 3.x
- **NLP:** spaCy / NLTK
- **LLM Entegrasyonu:** LangChain / OpenAI API / Ollama (Local)
- **Arayüz:** Streamlit
- **Versiyon Kontrol:** GitHub (Scrum Framework)