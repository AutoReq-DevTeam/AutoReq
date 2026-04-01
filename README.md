<div align="center">

# 🚀 AutoReq

### Otomatik Yazılım Gereksinim Analizörü

*Ham müşteri metinlerini yapılandırılmış mühendislik dökümanlarına dönüştüren NLP ve LLM destekli otomasyon asistanı.*

---

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Stanza](https://img.shields.io/badge/Stanza-NLP-09A3D5?style=for-the-badge)](https://stanfordnlp.github.io/stanza/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg?style=for-the-badge)](./LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Development-orange?style=for-the-badge)]()

</div>

---

## 📖 İçindekiler

- [Proje Hakkında](#-proje-hakkında)
- [Proje Vizyonu](#-proje-vizyonu)
- [Özellikler](#-özellikler)
- [Teknoloji Yığını](#-teknoloji-yığını)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Çıktılar](#-çıktılar)
- [Geliştirme Yol Haritası](#-geliştirme-yol-haritası)
- [Katkıda Bulunma](#-katkıda-bulunma)
- [Lisans](#-lisans)

---

## 📌 Proje Hakkında

AutoReq, yazılım geliştirme sürecindeki en zorlu ve zaman alıcı aşamalardan biri olan **gereksinim mühendisliğini** otomatize etmek için tasarlanmış, hibrit bir yapay zeka (NLP + LLM) aracıdır.

Müşterilerden gelen belirsiz ham metinleri alır; **Stanza** ile yapısal analiz yapar ve **LLM** (GPT/Llama) modülleriyle mantıksal derinlik katarak endüstri standartlarına uygun belgelere dönüştürür.

---

## 🔭 Proje Vizyonu

> *"Müşteriden gelen ham metinleri Doğal Dil İşleme (NLP) ile analiz ederek, hatasız ve yapılandırılmış mühendislik dökümanlarına dönüştüren bir otomasyon asistanı."*

AutoReq'in nihai hedefi, bir yazılım projesinin başındaki belirsizlik duvarını yıkarak hem geliştirici ekipleri hem de ürün sahipleri için net, ölçülebilir ve izlenebilir gereksinim belgeleri ortaya çıkarmaktır.

---

## 🎯 Proje Gereksinimleri (Requirements & NFR)

### Fonksiyonel Gereksinimler (Functional Requirements)
- **Metin Analizi:** Sistem, kullanıcının girdiği serbest formattaki metni kabul etmeli ve işleyebilmelidir.
- **Aktör ve Nesne Tespiti (NER):** Sistem, verilen metindeki "Kullanıcı, Sistem, Yönetici, Veritabanı" gibi ana aktörleri ve objeleri tespit etmelidir.
- **Sınıflandırma:** Sistem, çıkarttığı gereksinimleri "Fonksiyonel" veya "Fonksiyonel Olmayan (NFR)" olarak etiketlemelidir.
- **Çelişki Uyarıları:** Sistem, LLM desteği kullanarak mantıksal olarak birbiriyle çelişen maddeleri kırmızı uyarı olarak kullanıcıya raporlamalıdır.
- **Dışa Aktarma:** Analiz sonucunda oluşan tüm çıktılar, ISO/IEC/IEEE 29148 standartlarına uygun bir **PDF dökümanı** olarak indirebilmelidir.

### Fonksiyonel Olmayan Gereksinimler (Non-Functional Requirements - NFR)
- **Performans (Performance):** Metin analiz süreci (LLM istekleri ve NER süreçleri dahil) tek bir sayfa uzunluğundaki metinler için **maksimum 15 saniye** sürmelidir.
- **Güvenlik (Security):** LLM API (OpenAI/Groq vb.) erişim anahtarları asla kaynak koda (GitHub'a) gömülmemeli, sistem ortam değişkeni (env) üzerinden şifreli bir şekilde okunmalıdır.
- **Kullanılabilirlik (Usability):** Uygulama arayüzü (Streamlit), arka planda çalışan süreçleri göstermek adına bir yüklenme (spinner/progress) ibaresi göstermelidir. Dil modeli analizlerinin tamamı Türkçe yapılmaktadır.

---

## ✨ Özellikler

[Tüm detaylı özellik listesini görmek için tıklayınız.](./docs/FEATURES.md)

### 🛠 Temel Özellikler (MVP)

| Özellik | Açıklama | Durum |
|---|---|---|
| **Metin Ayrıştırma** | Cümle bazlı tokenizasyon ve metin temizleme | 🔲 Planlandı |
| **Sınıflandırma** | Gereksinimlerin Fonksiyonel / Fonksiyonel Olmayan olarak kategorize edilmesi | 🔲 Planlandı |
| **Varlık Tespiti (NER)** | Aktörlerin (Kullanıcı, Sistem) ve Nesnelerin otomatik belirlenmesi | 🔲 Planlandı |

### 🧠 Akıllı Analiz Modülleri

| Modül | Açıklama | Durum |
|---|---|---|
| **Çelişki Tespiti** | Mantıksal zıtlıkların ve belirsiz ifadelerin uyarılması | 🔲 Planlandı |
| **Eksiklik Analizi** | Standart şablonlara göre eksik gereksinimlerin tespiti ve öneriler *(örn: Giriş var, Şifre Sıfırlama yok)* | 🔲 Planlandı |
| **İyileştirme Önerileri** | *"Hızlı olmalı"* gibi muğlak ifadelerin somut ve ölçülebilir kriterlere dönüştürülmesi | 🔲 Planlandı |

---

## 🏗 Teknoloji Yığını

```
AutoReq
├── Dil          → Python 3.x
├── NLP          → Stanza / NLTK
├── Arayüz       → Streamlit
└── Versiyon     → GitHub (Scrum Framework)
```

| Katman | Teknoloji | Amaç |
|---|---|---|
| **Programlama Dili** | Python 3.x | Temel uygulama geliştirme |
| **NLP Motoru** | Stanza / NLTK | Yapısal analiz, NER, tokenizasyon |
| **Zeka Katmanı** | LLM (OpenAI / Ollama) | Çelişki tespiti, döküman üretimi |
| **Web Arayüzü** | Streamlit | İnteraktif kullanıcı arayüzü |
| **Proje Yönetimi** | GitHub + Scrum | Versiyon kontrolü ve agile süreç |

---

## ⚙️ Kurulum

> **Not:** Proje aktif geliştirme aşamasındadır. Aşağıdaki adımlar yakında güncellenecektir.

**Ön Koşullar:**
- Python 3.8 veya üzeri
- pip paket yöneticisi

```bash
# 1. Depoyu klonlayın
git clone https://github.com/AutoReq-DevTeam/AutoReq.git
cd AutoReq

# 2. Sanal ortam oluşturun (önerilir)
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Stanza dil modelini indirin
python -c "import stanza; stanza.download('tr')"
```

---

## 🚀 Kullanım

```bash
# Streamlit arayüzünü başlatın
streamlit run app.py
```

Tarayıcınızda `http://localhost:8501` adresini açın, ham gereksinim metninizi yapıştırın ve analizi başlatın.

---

## 📂 Çıktılar

AutoReq analiz işlemi tamamlandığında aşağıdaki formatları otomatik olarak üretir:

| Çıktı | Format | Açıklama |
|---|---|---|
| **SRS Belgesi** | PDF | ISO/IEC/IEEE 29148 standardına uygun Yazılım Gereksinim Spesifikasyonu |
| **User Stories** | Metin / Export | *"As a user, I want..."* formatında çevik hikayeler |
| **Product Backlog** | Liste / Export | Önceliklendirilmiş sprint iş listesi |
| **BDD Senaryoları** | Gherkin | *Given-When-Then* formatında test senaryoları |

---

## 🗺 Geliştirme Yol Haritası

```
Phase 1 – MVP (Temel Analiz Motoru)
├── [ ] Metin ön işleme pipeline'ı
├── [ ] Fonksiyonel / Fonksiyonel Olmayan sınıflandırıcı
└── [ ] NER ile aktör ve nesne tespiti

Phase 2 – Akıllı Modüller
├── [ ] Çelişki ve belirsizlik dedektörü
├── [ ] Eksiklik analizi ve öneri motoru
└── [ ] Muğlak ifade iyileştirici

Phase 3 – Çıktı & Entegrasyon
├── [ ] Otomatik SRS PDF üretimi
├── [ ] User Story & Backlog dışa aktarımı
├── [ ] BDD senaryo üreteci
└── [ ] Jira / Trello entegrasyonu (opsiyonel)
```

[Detaylı yol haritası ve haftalık görev dağılımı için tıklayınız.](./docs/ROADMAP_AND_ISSUES.md)

---

## 🤝 Katkıda Bulunma

Her türlü katkıya açığız! Katkıda bulunmadan önce lütfen aşağıdaki adımları izleyin:

1. Bu depoyu **fork**'layın
2. Yeni bir **feature branch** oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi **commit**'leyin (`git commit -m 'feat: yeni özellik eklendi'`)
4. Branch'inizi **push**'layın (`git push origin feature/yeni-ozellik`)
5. Bir **Pull Request** açın

Geliştirme sürecimiz **Scrum** framework'ü üzerine kurulu olup sprint döngüleri GitHub üzerinden takip edilmektedir.

[Geliştirme ekibi ve roller hakkında detaylı bilgi için tıklayınız.](./docs/TEAM.md)

---

## 📄 Lisans

Bu proje **GNU GPLv3 Lisansı** ile lisanslanmıştır. Detaylar için [LICENSE](./LICENSE) dosyasına bakınız.

---

<div align="center">

**AutoReq-DevTeam** tarafından ❤️ ile geliştirilmektedir.

*Daha iyi yazılım, daha net gereksinimlerle başlar.*

</div>