# 🚀 AutoReq: Otomatik Yazılım Gereksinim Analizörü

Bu dosya, projenin teknik detaylarını, özellik listesini ve geliştirme yol haritasını içerir.

## 📌 Proje Vizyonu
Müşteriden gelen ham metinleri Doğal Dil İşleme (NLP) ile analiz ederek, hatasız ve yapılandırılmış mühendislik dökümanlarına dönüştüren bir otomasyon asistanı.

## 🛠 Temel Özellikler (MVP)
- [ ] **Metin Ayrıştırma:** Cümle bazlı tokenizasyon ve temizleme.
- [ ] **Sınıflandırma:** Gereksinimlerin Fonksiyonel / Fonksiyonel Olmayan olarak ayrılması.
- [ ] **Varlık Tespiti (NER):** Aktörlerin (Kullanıcı, Sistem) ve Nesnelerin belirlenmesi.

## 🧠 Akıllı Modüller
- [ ] **Çelişki Tespiti:** Mantıksal zıtlıkların ve belirsiz ifadelerin uyarılması.
- [ ] **Eksiklik Analizi:** Standart şablonlara göre (Login var, Pass reset yok gibi) öneri sunma.
- [ ] **İyileştirme Önerileri:** "Hızlı olmalı" gibi muğlak ifadelerin ölçülebilir hale getirilmesi.

## 📂 Çıktılar (Outputs)
- [ ] **Otomatik SRS:** PDF formatında Yazılım Gereksinim Dökümanı.
- [ ] **User Stories:** "As a user, I want..." formatında çevik hikayeler.
- [ ] **Product Backlog:** Önceliklendirilmiş iş listesi (B-serisi çıktı).
- [ ] **BDD Senaryoları:** Given-When-Then formatında test senaryoları.

## 🏗 Teknoloji Yığını
- **Dil:** Python 3.x
- **NLP:** spaCy / NLTK
- **Arayüz:** Streamlit
- **Versiyon Kontrol:** GitHub (Scrum Framework)