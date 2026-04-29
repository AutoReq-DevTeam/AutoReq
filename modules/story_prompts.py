"""
modules/story_prompts.py — User Story Üretici Prompt Sistemi
Sorumlu: Halise İncir

Açıklama:
Fonksiyonel gereksinimleri Agile User Story formatına dönüştürmek için
kullanılan persona, JSON şeması ve prompt builder'larını içerir.
"""

from __future__ import annotations

from core.models import Requirement

# ---------------------------------------------------------------------------
# Persona
# ---------------------------------------------------------------------------

CORE_STORY_GENERATOR_PERSONA: str = """
Sen, AutoReq aracı için çalışan uzman bir Çevik (Agile) Gereksinim Analisti ve
User Story Yazarısın. Birincil görevin, teknik yazılım gereksinim cümlelerini
ürün ekiplerinin anlayabileceği, sprint backlog'una doğrudan atılabilecek
"User Story" kartlarına dönüştürmektir.

DAVRANIŞ KURALLARI:
- Her zaman "Bir [rol] olarak, [fayda] sağlamak amacıyla [hedef] yapabilmek istiyorum." yaklaşımına uygun, DİLİ TAMAMEN TÜRKÇE olan User Story üret. İngilizce terimler kullanma ("As a", "I want", "so that" KESİNLİKLE YASAKTIR).
- Çıktılar %100 Türkçe olmalı.
- Rol (Actor) boşsa "kullanıcı" veya "user" kullan.
- Benefit (so that) kısmı gerçek iş değerini belirtmeli; teknik detay içermemeli.
- acceptance_criteria en az 1, en fazla 3 madde olmalı; "olmalı" / "should" kipinde yaz.
- ASLA uydurma gereksinim ekleme; sadece sana verilen gereksinim üzerinden yaz.
""".strip()

# ---------------------------------------------------------------------------
# JSON Şeması (System Prompt içine gömülür)
# ---------------------------------------------------------------------------

STORY_DETECTION_SYSTEM_PROMPT: str = """
## Görev

Sana tek bir yazılım gereksinim cümlesi ve o gereksinim hakkında bağlam bilgisi verilecek.
Bu gereksinimi Agile User Story formatında bir JSON nesnesi olarak döndür.

## Çıktı Formatı (kesinlikle bu yapıya uy)

```json
{
  "role": "kullanıcı",
  "goal": "sisteme giriş yapabilmek",
  "benefit": "kişisel hesabıma erişebilmek",
  "acceptance_criteria": [
    "Geçerli kullanıcı adı ve şifre ile giriş yapıldığında ana sayfaya yönlendirilmeli",
    "Hatalı şifre girildiğinde anlamlı hata mesajı gösterilmeli"
  ]
}
```

## Kurallar

- Sadece JSON döndür; başka metin ekleme.
- `role`: Gereksinim metnindeki aktör (actor). Yoksa "kullanıcı" yaz. (İngilizce kullanma)
- `goal`: Kullanıcının sistemden beklentisi veya yapmak istediği eylem. Örn: "sisteme giriş yapabilmek"
- `benefit`: Bu eylemin kullanıcıya sağlayacağı iş değeri. Örn: "kişisel hesabıma güvenle erişebilmek"
- `acceptance_criteria`: Kabul kriterleri. Liste formatında, 1-3 madde, ölçülebilir. Türkçe yazılacak.
""".strip()


# ---------------------------------------------------------------------------
# Prompt Builder'lar
# ---------------------------------------------------------------------------


def build_story_generation_system_prompt() -> str:
    """Persona ve JSON şemasını birleştirerek tam system prompt döndürür.

    Returns:
        str: LLMClient.chat() için system_prompt parametresi.
    """
    return f"{CORE_STORY_GENERATOR_PERSONA}\n\n{STORY_DETECTION_SYSTEM_PROMPT}"


def build_story_generation_user_prompt(requirement: Requirement) -> str:
    """Tek bir gereksinim için user prompt üretir.

    Args:
        requirement: Dönüştürülecek Requirement nesnesi.

    Returns:
        str: LLMClient.chat() için user_prompt parametresi.
    """
    actors_str = ", ".join(requirement.actors) if requirement.actors else "belirtilmemiş"
    objects_str = ", ".join(requirement.objects) if requirement.objects else "belirtilmemiş"
    priority_str = requirement.priority or "MEDIUM"

    return (
        f"Gereksinim ID : {requirement.id}\n"
        f"Gereksinim Tipi: {requirement.req_type}\n"
        f"Öncelik        : {priority_str}\n"
        f"Tespit Edilen Aktörler: {actors_str}\n"
        f"Tespit Edilen Nesneler: {objects_str}\n\n"
        f"Gereksinim Metni:\n{requirement.text.strip()}\n\n"
        "Bu gereksinimi Agile User Story formatında JSON olarak üret."
    )


__all__ = [
    "CORE_STORY_GENERATOR_PERSONA",
    "STORY_DETECTION_SYSTEM_PROMPT",
    "build_story_generation_system_prompt",
    "build_story_generation_user_prompt",
]
