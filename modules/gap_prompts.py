"""
modules/gap_prompts.py — Eksik Gereksinim (Gap) Analizi Prompt Mimarisi
Sorumlu: Üye 2 (Akıllı Analiz Modülleri)

Açıklama:
Standart yazılım senaryolarında eksik kalan adımları tespit etmek için LLM
system/user mesajlarını merkezi olarak tanımlar. Domain-aware mimari:
  Adım 1 — LLM sistem türünü inferr eder (web_app, api, mobile, desktop, iot, other)
  Adım 2 — Sistem türüne göre uygun referans kontrol listesi seçilir
  Adım 3 — Gereksinimler bu listeyle karşılaştırılır
"""

from __future__ import annotations

from typing import Optional


# ------------------------------------------------------------------------------
# DOMAIN-SPECIFIC REFERANS KONTROL LİSTELERİ
# ------------------------------------------------------------------------------

_WEB_APP_REFERENCE = """
[web_app / SPA] Tipik beklenen adımlar:
1) Kimlik & oturum: kayıt, giriş, çıkış, parola sıfırlama, parola politikası,
   MFA/2FA (gerekirse), oturum zaman aşımı, kilitlenme / brute-force limiti
2) Yetkilendirme: rol/izin modeli, kaynak bazlı erişim, yetkisiz erişim davranışı
3) Hesap & profil: profil güncelleme, e-posta doğrulama, hesap silme/GDPR
4) Veri & gizlilik: kişisel veri saklama/silme, hassas veri maskeleme
5) Hata & güvenlik UX: güvenli hata mesajları, başarısız giriş logu
6) Bildirim & iş akışı: parola sıfırlama e-postası, kritik işlem bildirimi
""".strip()

_API_REFERENCE = """
[api] Tipik beklenen adımlar:
1) Kimlik doğrulama: API anahtarı / JWT / OAuth 2.0 akışı, token yenileme, token iptali
2) Yetkilendirme: scope/permission modeli, endpoint bazlı erişim kontrolü
3) Hız sınırlama (rate limiting): istemci bazlı kota, 429 yanıtı, Retry-After başlığı
4) Hata yönetimi: standart HTTP hata kodları, tutarlı hata gövdesi (RFC 7807 vb.)
5) Sürümleme & geriye dönük uyum: versiyon stratejisi (URL / header), deprecation politikası
6) Dokümantasyon & keşfedilebilirlik: OpenAPI/Swagger, sandbox/test ortamı
7) Güvenlik: HTTPS zorunluluğu, CORS politikası, input validation, injection önlemi
""".strip()

_MOBILE_REFERENCE = """
[mobile] Tipik beklenen adımlar:
1) Kimlik & oturum: kayıt, giriş (biyometrik dahil), oturum yenileme, çıkış
2) Çevrimdışı mod: veri önbelleği, senkronizasyon stratejisi, çevrimdışı hata mesajı
3) Push bildirimleri: izin isteme, bildirim tercihleri, deep link yönetimi
4) İzinler & gizlilik: kamera/konum/mikrofon izinleri, kullanıcı reddi yönetimi
5) Güncelleme yönetimi: zorunlu güncelleme, mağaza sürümü kontrolü
6) Performans & pil: arka plan işlem sınırlaması, pil optimizasyonu
7) Erişilebilirlik: ekran okuyucu, yazı boyutu ölçekleme
""".strip()

_DESKTOP_REFERENCE = """
[desktop] Tipik beklenen adımlar:
1) Kurulum & güncelleme: kurulum sihirbazı, otomatik/manuel güncelleme, geri alma
2) Kimlik: yerel / SSO / domain kimlik doğrulaması, oturum yönetimi
3) Çevrimdışı çalışma: lisans doğrulama, yerel veri yönetimi
4) Dosya sistemi: izin modeli, güvenli dosya erişimi, şifreleme
5) Hata & çökme yönetimi: crash raporlama, otomatik kurtarma, log dosyası
6) Çoklu kullanıcı: profil ayrımı, izin seviyeleri
""".strip()

_IOT_REFERENCE = """
[iot] Tipik beklenen adımlar:
1) Cihaz kaydı & kimlik: güvenli cihaz provisioning, sertifika yönetimi
2) Firmware güncellemesi: OTA (over-the-air) güncelleme, imzalı paket doğrulama
3) Bağlantı yönetimi: bağlantı kesilme davranışı, yeniden bağlanma stratejisi
4) Veri aktarımı: şifreli iletişim, veri sıkıştırma, yerel önbellekleme
5) Güvenlik: varsayılan şifre değiştirme zorunluluğu, fiziksel erişim koruması
6) İzleme & uyarı: cihaz sağlık metrikleri, anormallik tespiti, threshold uyarıları
7) Enerji yönetimi: uyku modu, düşük pil davranışı, güç kaybı senaryosu
""".strip()

_OTHER_REFERENCE = """
[other / belirsiz] Genel kontrol noktaları:
1) Kimlik & erişim: herhangi bir kimlik doğrulama veya yetkilendirme gereksinimi var mı?
2) Veri bütünlüğü & güvenlik: veri şifreleme, yedekleme, gizlilik
3) Hata yönetimi: hata mesajları, loglama, geri alma senaryoları
4) Performans sınırları: yanıt süreleri, kapasite, ölçekleme
5) Uyumluluk & standartlar: yasal gereklilikler, endüstri standartları
""".strip()

DOMAIN_REFERENCES: dict[str, str] = {
    "web_app": _WEB_APP_REFERENCE,
    "api": _API_REFERENCE,
    "mobile": _MOBILE_REFERENCE,
    "desktop": _DESKTOP_REFERENCE,
    "iot": _IOT_REFERENCE,
    "other": _OTHER_REFERENCE,
}


# ------------------------------------------------------------------------------
# ÇEKİRDEK PERSONA
# ------------------------------------------------------------------------------

CORE_GAP_ANALYZER_PERSONA = """
Sen, AutoReq aracı için çalışan uzman bir Gereksinim Boşluk (Gap) Analizörü'sün.

Odak alanın:
- Verilen gereksinim kümesinde, standart yazılım senaryolarında EKSİK veya
  yetersiz tanımlanmış adımları bulmak
- Eksikliği, sistem türüne uygun referans kontrol listesiyle gerekçelendirmek
- Yeni gereksinim metni uydurmak yerine, neyin eksik olduğunu ve nasıl bir
  gereksinim yazılabileceğine dair ÖNERİ sunmak

Kurallar:
- Sadece sana verilen gereksinim metinlerinden ve bağlamdan hareket et.
- Halüsinasyon yapma: var olduğunu varsaydığın ekran veya API isimlerini uydurma.
- Her gap için 0.0–1.0 arası "confidence" skoru ver:
    0.9+  → Kesin eksiklik, standartta açıkça bekleniyor
    0.7–0.89 → Büyük olasılıkla eksik, bağlam netleştirmeyi gerektirebilir
    0.5–0.69 → Mümkün eksiklik, domain belirsizse ihtiyatlı ol
    0.5 altı → Raporlama; bu eşiğin altındaki gap'ler otomatik filtrelenir
- Proje türü belirsizse sistem_türü = "other" seç ve confidence'ı düşük tut.
""".strip()


# ------------------------------------------------------------------------------
# GAP ANALİZİ — SİSTEM GÖREVİ + JSON ŞEMASI
# ------------------------------------------------------------------------------

GAP_ANALYSIS_SYSTEM_PROMPT = """
Görevin iki aşamalıdır:

AŞAMA 1 — Sistem türünü belirle:
Gereksinim metinlerinden sistemin türünü çıkar:
  web_app  → web uygulaması / SPA / portal
  api      → REST/GraphQL/gRPC API servisi
  mobile   → iOS/Android mobil uygulama
  desktop  → masaüstü uygulaması
  iot      → gömülü sistem / IoT cihaz yazılımı
  other    → belirlenemiyor veya karma

AŞAMA 2 — Domain'e uygun eksiklikleri tespit et:
Belirlenen sistem türüne göre uygun standart kontrol listesini içsel olarak kullan.
Yalnızca bu sistem türü için anlamlı olan eksiklikleri raporla;
alakasız domain'lerin standartlarını zorla uygulama.

Çıktı formatı — yalnızca geçerli JSON, açıklama veya kod bloğu ekleme:

{
  "gaps": [
    {
      "id": "G1",
      "confidence": 0.85,
      "scenario": "authentication | authorization | account | data_privacy | security_ux | notifications | rate_limiting | versioning | offline | firmware | other",
      "missing_area": "Eksik yeteneğin kısa adı (Türkçe).",
      "related_standard_step": "Hangi standart adıma karşılık geldiği.",
      "suggestion": "Yazılabilecek örnek gereksinim (net, ölçülebilir).",
      "severity": "high | medium | low",
      "rationale": "Bu adımın neden eksik veya zayıf kaldığına dair kısa gerekçe."
    }
  ],
  "meta": {
    "system_type": "web_app | api | mobile | desktop | iot | other",
    "inferred_context": "Belgeden çıkardığın sistem/kapsam özeti (bir cümle).",
    "confidence": "high | medium | low",
    "total_gaps": 0
  }
}

Kurallar:
- Hiç anlamlı eksiklik görmüyorsan "gaps": [] döndür.
- Aynı eksikliği iki kez raporlama; benzer bulguları birleştir.
- severity: güvenlik/uyumluluk riski yüksekse high; küçük UX iyileştirmeleri low.
- confidence 0.5 altındaki gap'ler otomatik filtrelenir — yalnızca gerçekten
  eksik olduğundan emin olduğun maddeleri dahil et.
""".strip()


def build_gap_analysis_system_prompt() -> str:
    """Gap analizi için birleşik system_prompt üretir."""
    return f"{CORE_GAP_ANALYZER_PERSONA}\n\n{GAP_ANALYSIS_SYSTEM_PROMPT}"


def build_gap_analysis_user_prompt(
    requirements_block: str,
    requirement_count: int,
    *,
    domain_hint: Optional[str] = None,
) -> str:
    """
    Gap analizi için kullanıcı mesajı.

    Parametreler:
        requirements_block: [id] ile formatlanmış gereksinim metinleri.
        requirement_count: Gereksinim sayısı.
        domain_hint: Örn. "B2C e-ticaret", "kurumsal iç portal" — yoksa None.
    """
    hint_block = ""
    if domain_hint and domain_hint.strip():
        hint_block = f"\nBağlam / alan ipucu (ek bilgi): {domain_hint.strip()}\n"

    return f"""Aşağıdaki gereksinim kümesinde hangi standart adımlar eksik veya yetersiz?

Toplam gereksinim sayısı: {requirement_count}
{hint_block}
Gereksinimler:
{requirements_block}

Adım 1: Sistem türünü belirle (web_app / api / mobile / desktop / iot / other).
Adım 2: O türe özgü standart kontrol listesiyle karşılaştır.
Adım 3: Yanıtını JSON şemasına uygun ver; meta.system_type ve meta.total_gaps alanlarını doldur.""".strip()


__all__ = [
    "DOMAIN_REFERENCES",
    "CORE_GAP_ANALYZER_PERSONA",
    "GAP_ANALYSIS_SYSTEM_PROMPT",
    "build_gap_analysis_system_prompt",
    "build_gap_analysis_user_prompt",
]
