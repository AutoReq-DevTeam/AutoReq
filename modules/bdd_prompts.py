"""
modules/bdd_prompts.py — BDD Gherkin Senaryo Üretici Prompt Sistemi
Sorumlu: Halise İncir

Açıklama:
Fonksiyonel gereksinimleri Gherkin formatında BDD test senaryolarına
dönüştürmek için kullanılan persona, JSON şeması ve prompt builder'larını içerir.

Referans: conflict_prompts.py şablonunu takip eder.
"""

from __future__ import annotations

from core.models import Requirement

# ---------------------------------------------------------------------------
# Persona
# ---------------------------------------------------------------------------

CORE_BDD_GENERATOR_PERSONA: str = """
Sen, AutoReq aracı için çalışan uzman bir QA Mühendisi ve BDD (Behaviour-Driven
Development) Test Senaryosu Yazarısın. Birincil görevin, teknik yazılım gereksinim
cümlelerini Gherkin formatında iki senaryo içeren BDD test taslakları üretmektir:

1. **Happy Path (Başarılı Senaryo):** Gereksinimin başarıyla tamamlandığı normal akış.
2. **Negative Scenario (Olumsuz Senaryo):** Geçersiz girdi veya sınır durumu.

DAVRANIŞ KURALLARI:
- Çıktı JSON olmalı; iki ayrı Gherkin senaryo bloğu içermeli.
- Her senaryoda zorunlu anahtar kelimeler: Feature:, Scenario:, Given, When, Then.
- Türkçe gereksinim gelirse Türkçe senaryo üret; İngilizce gelirse İngilizce üret.
- Her Given/When/Then tek satır ve ölçülebilir olmalı.
- ASLA gereksinimde olmayan işlev için senaryo yazma.
- And/But adımları opsiyoneldir; karmaşıklık artırmak için kullan.
""".strip()

# ---------------------------------------------------------------------------
# JSON Şeması (System Prompt içine gömülür)
# ---------------------------------------------------------------------------

BDD_GENERATION_SYSTEM_PROMPT: str = """
## Görev

Sana tek bir yazılım gereksinim cümlesi ve o gereksinim hakkında bağlam bilgisi verilecek.
Bu gereksinim için Gherkin formatında iki senaryo içeren bir JSON nesnesi döndür:
1. happy_path: Başarılı akış (olumlu senaryo).
2. negative_scenario: Başarısız veya sınır durumu (olumsuz senaryo).

## Çıktı Formatı (kesinlikle bu yapıya uy)

```json
{
  "feature_title": "Kullanıcı Girişi",
  "happy_path": {
    "scenario_title": "Geçerli kimlik bilgileri ile başarılı giriş",
    "given": ["Kullanıcı giriş sayfasındadır", "Kullanıcı kayıtlı bir hesaba sahiptir"],
    "when": ["Kullanıcı doğru e-posta ve şifreyi girer", "Kullanıcı Giriş Yap butonuna tıklar"],
    "then": ["Kullanıcı ana sayfaya yönlendirilmeli", "Oturum açma başarı mesajı gösterilmeli"]
  },
  "negative_scenario": {
    "scenario_title": "Hatalı şifre ile giriş denemesi",
    "given": ["Kullanıcı giriş sayfasındadır"],
    "when": ["Kullanıcı doğru e-posta ancak yanlış şifre girer", "Kullanıcı Giriş Yap butonuna tıklar"],
    "then": ["Hata mesajı gösterilmeli", "Kullanıcı giriş sayfasında kalmalı"]
  }
}
```

## Kurallar

- Sadece JSON döndür; açıklama veya markdown dışında metin ekleme.
- `feature_title`: Gereksinimi özetleyen kısa başlık (3-6 kelime).
- `happy_path.scenario_title` ve `negative_scenario.scenario_title`: Senaryonun amacını belirtir.
- `given`, `when`, `then`: Her biri string listesi; en az 1 en fazla 4 madde.
- Türkçe gereksinim → Türkçe çıktı; İngilizce → İngilizce.
""".strip()

# ---------------------------------------------------------------------------
# Prompt Builder'lar
# ---------------------------------------------------------------------------


def build_bdd_generation_system_prompt() -> str:
    """Persona ve JSON şemasını birleştirerek tam system prompt döndürür.

    Returns:
        str: LLMClient.chat() için system_prompt parametresi.
    """
    return f"{CORE_BDD_GENERATOR_PERSONA}\n\n{BDD_GENERATION_SYSTEM_PROMPT}"


def build_bdd_generation_user_prompt(requirement: Requirement) -> str:
    """Tek bir gereksinim için BDD senaryosu user prompt'u üretir.

    Args:
        requirement: Gherkin senaryosuna dönüştürülecek Requirement nesnesi.

    Returns:
        str: LLMClient.chat() için user_prompt parametresi.
    """
    actors_str = ", ".join(requirement.actors) if requirement.actors else "belirtilmemiş"
    objects_str = ", ".join(requirement.objects) if requirement.objects else "belirtilmemiş"
    priority_str = requirement.priority or "MEDIUM"

    return (
        f"Gereksinim ID  : {requirement.id}\n"
        f"Gereksinim Tipi: {requirement.req_type}\n"
        f"Öncelik        : {priority_str}\n"
        f"Tespit Edilen Aktörler: {actors_str}\n"
        f"Tespit Edilen Nesneler: {objects_str}\n\n"
        f"Gereksinim Metni:\n{requirement.text.strip()}\n\n"
        "Bu gereksinim için iki Gherkin BDD senaryosu (happy path + negative) JSON olarak üret."
    )


BDD_BATCH_SYSTEM_PROMPT: str = """
## Görev

Sana birden fazla yazılım gereksinimi verilecek. Her biri için Gherkin formatında
iki senaryo üret ve tüm sonuçları tek bir JSON dizisi olarak döndür.

## Çıktı Formatı (kesinlikle bu yapıya uy)

```json
[
  {
    "req_id": "REQ_001",
    "feature_title": "Kullanıcı Girişi",
    "happy_path": {
      "scenario_title": "Geçerli kimlik bilgileri ile başarılı giriş",
      "given": ["Kullanıcı giriş sayfasındadır"],
      "when": ["Kullanıcı doğru e-posta ve şifreyi girer"],
      "then": ["Kullanıcı ana sayfaya yönlendirilmeli"]
    },
    "negative_scenario": {
      "scenario_title": "Hatalı şifre ile giriş denemesi",
      "given": ["Kullanıcı giriş sayfasındadır"],
      "when": ["Kullanıcı yanlış şifre girer"],
      "then": ["Hata mesajı gösterilmeli"]
    }
  }
]
```

## Kurallar

- Sadece JSON dizisi döndür; başka metin ekleme.
- Her gereksinim için listede tam olarak bir öğe olmalı; `req_id` alanı girişle eşleşmeli.
- `given`, `when`, `then`: Her biri string listesi; en az 1, en fazla 4 madde.
- Türkçe gereksinim → Türkçe çıktı.
- ASLA gereksinimde olmayan işlev için senaryo yazma.
""".strip()


def build_bdd_generation_batch_system_prompt() -> str:
    """Toplu BDD üretimi için persona + görev promptunu birleştirir.

    Returns:
        str: LLMClient.chat() için system_prompt parametresi.
    """
    return f"{CORE_BDD_GENERATOR_PERSONA}\n\n{BDD_BATCH_SYSTEM_PROMPT}"


def build_bdd_generation_batch_user_prompt(requirements: "list[Requirement]") -> str:
    """Birden fazla gereksinim için toplu BDD user prompt üretir.

    Args:
        requirements: Gherkin senaryosuna dönüştürülecek Requirement listesi.

    Returns:
        str: LLMClient.chat() için user_prompt parametresi.
    """
    lines = []
    for r in requirements:
        actors_str = ", ".join(r.actors) if r.actors else "belirtilmemiş"
        priority_str = r.priority or "MEDIUM"
        lines.append(
            f"[{r.id}] Tip: {r.req_type} | Öncelik: {priority_str} | Aktörler: {actors_str}\n"
            f"Metin: {r.text.strip()}"
        )
    items_block = "\n\n".join(lines)
    return (
        f"Aşağıdaki {len(requirements)} gereksinim için JSON dizisi üret.\n\n"
        f"{items_block}"
    )


__all__ = [
    "CORE_BDD_GENERATOR_PERSONA",
    "BDD_GENERATION_SYSTEM_PROMPT",
    "BDD_BATCH_SYSTEM_PROMPT",
    "build_bdd_generation_system_prompt",
    "build_bdd_generation_user_prompt",
    "build_bdd_generation_batch_system_prompt",
    "build_bdd_generation_batch_user_prompt",
]
