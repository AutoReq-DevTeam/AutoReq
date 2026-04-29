"""
outputs/story_generator.py — User Story Üretim Modülü
Sorumlu: Halise İncir

Açıklama:
Analiz edilen fonksiyonel gereksinimleri çevik (Agile) geliştirme süreçlerine
uygun "User Story" formatına dönüştürür.

Çıktı formatı:
    [
        {
            "req_id":              "REQ_001",
            "role":                "kullanıcı",
            "goal":                "sisteme giriş yapabilmek",
            "benefit":             "kişisel hesabıma erişebilmek",
            "acceptance_criteria": ["...", "..."]
        },
        ...
    ]

Notlar:
- Sadece req_type == "FUNCTIONAL" olan gereksinimler işlenir (token tasarrufu).
- LLM çağrısı başarısız olursa ilgili gereksinim için fallback dict döner;
  pipeline çökmez (graceful degradation).
"""

from __future__ import annotations

from typing import List, Optional

from loguru import logger

from core.models import AnalysisReport, Requirement
from modules.llm_client import LLMClient, LLMClientError
from modules.llm_response_utils import extract_json_object
from modules.story_prompts import (
    build_story_generation_system_prompt,
    build_story_generation_user_prompt,
)

_log = logger.bind(module="story_generator")


def _make_fallback_story(req: Requirement) -> dict:
    """LLM çağrısı başarısız olduğunda kullanılan temel user story sözlüğü.

    Args:
        req: Dönüştürülemeyen Requirement nesnesi.

    Returns:
        dict: Temel alanları doldurulmuş user story.
    """
    role = req.actors[0] if req.actors else "kullanıcı"
    return {
        "req_id": req.id,
        "role": role,
        "goal": req.text.strip(),
        "benefit": "(LLM analizi mevcut değil)",
        "acceptance_criteria": [f"{req.text.strip()} işlevi çalışır durumda olmalı."],
    }


def _normalize_story(req_id: str, raw: dict) -> dict:
    """LLM'den dönen ham dict'i sözleşmeye uygun hale getirir.

    Eksik alanlar varsayılan değerlerle doldurulur; tip uyumsuzlukları giderilir.

    Args:
        req_id: Gereksinim kimliği (REQ_NNN).
        raw: LLM'den gelen ham sözlük.

    Returns:
        dict: role, goal, benefit, acceptance_criteria, req_id alanları dolu story.
    """
    role = raw.get("role") or "kullanıcı"
    goal = raw.get("goal") or "(hedef belirtilmedi)"
    benefit = raw.get("benefit") or "(fayda belirtilmedi)"

    ac_raw = raw.get("acceptance_criteria", [])
    if isinstance(ac_raw, list):
        acceptance_criteria: List[str] = [str(item) for item in ac_raw if item]
    else:
        acceptance_criteria = [str(ac_raw)] if ac_raw else []

    if not acceptance_criteria:
        acceptance_criteria = ["İlgili işlev hatasız çalışmalı."]

    return {
        "req_id": req_id,
        "role": role,
        "goal": goal,
        "benefit": benefit,
        "acceptance_criteria": acceptance_criteria,
    }


class StoryGenerator:
    """Fonksiyonel gereksinimlerden Agile User Story'leri üretir.

    LLM (Gemini) kullanarak "As a [role], I want [action] so that [benefit]"
    formatında user story'ler üretir. Sadece FUNCTIONAL gereksinimleri işler.

    Args:
        llm_client: Dışarıdan enjekte edilebilir LLM istemcisi (test/DI için).
                    Verilmezse generate() çağrısında otomatik oluşturulur.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        self._llm_client = llm_client

    def _get_client(self) -> LLMClient:
        """Lazy-init: istemciyi ilk ihtiyaç anında oluşturur.

        Returns:
            LLMClient: Yapılandırılmış LLM istemcisi.

        Raises:
            LLMClientError: API key tanımlı değilse.
        """
        if self._llm_client is None:
            self._llm_client = LLMClient()
        return self._llm_client

    def _generate_single_story(self, req: Requirement) -> dict:
        """Tek bir gereksinim için LLM'e çağrı yapar ve normalize edilmiş story döner.

        Args:
            req: User story'e dönüştürülecek Requirement.

        Returns:
            dict: Normalize edilmiş user story sözlüğü.
        """
        system_prompt = build_story_generation_system_prompt()
        user_prompt = build_story_generation_user_prompt(req)

        client = self._get_client()

        try:
            response = client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                metadata={
                    "module": "story_generator",
                    "action": "generate_user_story",
                    "req_id": req.id,
                },
            )
        except LLMClientError:
            _log.exception("LLM çağrısı başarısız (user story üretimi) | req_id={}", req.id)
            raise

        try:
            raw = extract_json_object(response.content)
        except ValueError as exc:
            _log.error(
                "LLM çıktısı JSON olarak çözülemedi | req_id={} preview={}",
                req.id,
                response.content[:300] if response.content else "",
            )
            raise LLMClientError(f"User story çıktısı işlenemedi: {exc}") from exc

        return _normalize_story(req.id, raw)

    def generate(self, report: AnalysisReport) -> List[dict]:
        """AnalysisReport içindeki FUNCTIONAL gereksinimleri User Story'lere dönüştürür.

        Her gereksinim için LLM'e ayrı çağrı yapılır. LLM hatası durumunda
        o gereksinim için fallback dict eklenir; pipeline çökmez.

        Args:
            report: NLP ve LLM analizleri tamamlanmış rapor nesnesi.

        Returns:
            list[dict]: Her biri {'req_id', 'role', 'goal', 'benefit',
                        'acceptance_criteria'} içeren user story listesi.
                        Yalnızca FUNCTIONAL gereksinimler dahil edilir.
        """
        functional_reqs = [
            req
            for req in report.parsed_doc.requirements
            if req.req_type == "FUNCTIONAL"
        ]

        if not functional_reqs:
            _log.info(
                "User story üretimi atlandı: FUNCTIONAL gereksinim yok "
                "| toplam_gereksinim={}",
                len(report.parsed_doc.requirements),
            )
            return []

        _log.info(
            "User story üretimi başlatıldı | functional_count={}",
            len(functional_reqs),
        )

        stories: List[dict] = []

        for req in functional_reqs:
            try:
                story = self._generate_single_story(req)
                stories.append(story)
                _log.debug("User story üretildi | req_id={}", req.id)
            except (LLMClientError, ValueError) as exc:
                _log.warning(
                    "User story üretilemedi, fallback kullanılıyor | req_id={} hata={}",
                    req.id,
                    exc,
                )
                stories.append(_make_fallback_story(req))

        _log.info("User story üretimi tamamlandı | stories={}", len(stories))
        return stories
