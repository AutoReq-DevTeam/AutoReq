---
marp: true
theme: default
paginate: true
backgroundColor: #ffffff
style: |
  section {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    color: #334155;
    padding: 50px;
    font-size: 24px;
    background-color: #ffffff !important;
  }
  section.lead {
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }
  section.lead h1 {
    color: #0f172a !important;
    font-size: 80px;
    margin: 0;
    padding: 0;
    border-bottom: none !important;
    background: none;
    -webkit-text-fill-color: #0f172a !important;
  }
  section.lead h3 {
    color: #2563eb !important;
    font-size: 32px;
    margin-top: 10px;
  }
  section.lead p, section.lead strong, section.lead em {
    color: #475569 !important;
  }
  h1 {
    color: #0f172a;
    font-size: 56px;
    margin-bottom: 20px;
    border-bottom: none;
    display: inline-block;
  }
  h2 {
    color: #1e3a8a;
    font-size: 38px;
    margin-top: 0;
    font-weight: 800;
  }
  strong {
    color: #2563eb;
    font-weight: 700;
  }
  footer {
    font-size: 14px;
    color: #94a3b8;
    border-top: 1px solid #e2e8f0;
    padding-top: 10px;
  }
  blockquote {
    border-left: 10px solid #3b82f6;
    background: #f8fafc;
    padding: 20px 30px;
    margin: 20px 0;
    border-radius: 0 12px 12px 0;
    color: #1e40af;
    font-style: italic;
  }
  ul li::marker {
    color: #3b82f6;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
  }
  th {
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 15px;
    text-align: left;
    border-bottom: 2px solid #cbd5e1;
  }
  td {
    padding: 15px;
    border-bottom: 1px solid #e2e8f0;
  }
---

<!-- _class: lead -->

# AutoReq
### Checkpoint #1: Stratejik Vizyon ve Problem Analizi

**AutoReq DevTeam**  
*Mühendislik Standartlarını Yapay Zeka ile Yeniden Tanımlıyoruz*

<!-- footer: AutoReq Project | Mart 2026 -->

---

## 🧐 Problem Tanımı
**Gereksinim Analizindeki "Gri Alanlar"**

*   **Belirsizlik:** Müşteriden gelen ham metinler genellikle çelişkili ve teknik derinlikten yoksundur.
*   **Dökümantasyon Yükü:** Manuel SRS hazırlama süreci haftalar sürebilir.
*   **Hata Maliyeti:** Yanlış anlaşılan tek bir madde, projenin finalinde %30-40 ek maliyet yaratır.

> *"Projelerin yaklaşık yarısı, yanlış veya eksik tanımlanmış gereksinimler nedeniyle bütçe ve zaman sınırlarını aşmaktadır."*

---

## 👥 Paydaşlar ve Personalar
**Gerçek Sorunlar, Gerçek Çözümler**

*   **Ürün Sahipleri / İş Analistleri:**
    *   *İhtiyaç:* Hızlı prototipleme ve döküman standardizasyonu.
    *   *Fayda:* Rutin dökümantasyon yükünün otomatize edilmesi.
*   **Mühendislik Ekipleri:**
    *   *İhtiyaç:* Net, ölçülebilir ve doğrudan koda dökülebilir talimatlar.
    *   *Fayda:* "Bu özellik aslında ne yapmalı?" sorusunun ortadan kalkması.

---

## 🏗 Proje Kapsamı
**Neye Odaklanıyoruz?**

| ✅ In-Scope | ❌ Out-of-Scope |
| :--- | :--- |
| NLP destekli **Varlık ve Aktör** tespiti | Otomatik kaynak kod üretimi |
| **ISO/IEC/IEEE 29148** uyumlu çıktı üretimi | Grafiksel UI tasarımı (Mockup) |
| Mantıksal **Çelişki ve Eksiklik** analizi | Sesli komut veya mülakat analizi |
| F/NFR Sınıflandırma motoru | Veritabanı yönetim sistemleri |

<!-- footer: Vizyon: Yapılandırılmış ve ölçülebilir mühendislik çıktıları. -->

---

## 📈 Başarı Metrikleri (KPIs)

1.  **Süreç Optimizasyonu:** Manuel dökümantasyon hazırlama süresinde ortalama **%40 - %50** zaman tasarrufu.
2.  **Sınıflandırma Doğruluğu:** F/NFR ayrımında **%75 - %80** F1-Skoru.
3.  **Analitik Derinlik:** Kritik mantıksal çelişkilerin (L1 seviyesi) en az **%70**'inin sistem tarafından uyarılması.
4.  **Standart Uyumu:** Çıktıların ISO 29148 şablonlarına **%100** yapısal uyumu.

---

<!-- _class: lead center -->
**Teşekkür Ederiz!**
