"""
outputs/backlog_generator.py — Önceliklendirme ve Backlog Üretici
Sorumlu: Halise İncir

Açıklama:
Analiz edilen gereksinimleri, mantıksal öncelik kuralları çerçevesinde puanlar ve
sıralar. Geliştirme ekibi için optimize edilmiş bir işlem listesi oluşturur.

Çıktı formatı (list[dict]):
    [
        {
            "req_id":        "REQ_001",
            "title":         "Kullanıcı sisteme giriş yapabilmeli.",
            "priority_score": 4.5,
            "story_points":  3,
            "type":          "FUNCTIONAL",
            "depends_on":    [],
        },
        ...
    ]

Skorlama formülü:
    priority_score = priority_weight × type_weight × conflict_penalty

    priority_weight  : HIGH=3, MEDIUM=2, LOW=1  (None → MEDIUM varsayılan)
    type_weight      : FUNCTIONAL=1.0, NON_FUNCTIONAL=0.7, UNKNOWN=0.8
    conflict_penalty : Çelişki listesinde geçen req_id'lere ×1.5 (önce çözülsün)

Story points hesabı (basit heuristic):
    score ≥ 5 → 8 puan
    score ≥ 3 → 5 puan
    score ≥ 2 → 3 puan
    diğer     → 1 puan
"""

from __future__ import annotations

from typing import List, Set

from loguru import logger

from core.models import AnalysisReport, Requirement

_log = logger.bind(module="backlog_generator")

# ---------------------------------------------------------------------------
# Ağırlık sabitleri
# ---------------------------------------------------------------------------

_PRIORITY_WEIGHT: dict[str, float] = {
    "HIGH": 3.0,
    "MEDIUM": 2.0,
    "LOW": 1.0,
}

_TYPE_WEIGHT: dict[str, float] = {
    "FUNCTIONAL": 1.0,
    "NON_FUNCTIONAL": 0.7,
    "UNKNOWN": 0.8,
}

_CONFLICT_MULTIPLIER: float = 1.5


# ---------------------------------------------------------------------------
# Yardımcı Fonksiyonlar
# ---------------------------------------------------------------------------


def _collect_conflicted_req_ids(report: AnalysisReport) -> Set[str]:
    """Çelişki listesindeki tüm req_id'leri bir küme olarak döner.

    Args:
        report: AnalysisReport nesnesi.

    Returns:
        set[str]: Çelişki içeren gereksinim ID'lerinin kümesi.
    """
    conflicted: Set[str] = set()
    for conflict in report.conflicts:
        req_ids = conflict.get("req_ids", [])
        if isinstance(req_ids, list):
            conflicted.update(str(rid) for rid in req_ids)
    return conflicted


def _compute_priority_score(
    req: Requirement,
    conflicted_req_ids: Set[str],
) -> float:
    """Tek bir gereksinim için öncelik skorunu hesaplar.

    Args:
        req: Değerlendirilecek Requirement.
        conflicted_req_ids: Çelişki içeren req_id kümesi.

    Returns:
        float: Hesaplanan öncelik skoru (yüksek = önce yapılmalı).
    """
    priority_weight = _PRIORITY_WEIGHT.get(req.priority or "MEDIUM", 2.0)
    type_weight = _TYPE_WEIGHT.get(req.req_type, 0.8)
    conflict_penalty = _CONFLICT_MULTIPLIER if req.id in conflicted_req_ids else 1.0
    return round(priority_weight * type_weight * conflict_penalty, 2)


def _score_to_story_points(score: float) -> int:
    """Öncelik skoruna göre story points hesaplar.

    Args:
        score: _compute_priority_score() tarafından döndürülen skor.

    Returns:
        int: Fibonacci benzeri story points tahmini (1, 3, 5, 8).
    """
    if score >= 5.0:
        return 8
    if score >= 3.0:
        return 5
    if score >= 2.0:
        return 3
    return 1


def _build_backlog_item(
    req: Requirement,
    conflicted_req_ids: Set[str],
) -> dict:
    """Tek bir gereksinim için backlog öğesi sözlüğü oluşturur.

    Args:
        req: Kaynak Requirement nesnesi.
        conflicted_req_ids: Çelişki içeren req_id kümesi.

    Returns:
        dict: {req_id, title, priority_score, story_points, type, depends_on}
    """
    score = _compute_priority_score(req, conflicted_req_ids)
    return {
        "req_id": req.id,
        "title": req.text.strip(),
        "priority_score": score,
        "story_points": _score_to_story_points(score),
        "type": req.req_type,
        "depends_on": [],  # Bağımlılık analizi mevcut pipeline'da yok; placeholder
    }


# ---------------------------------------------------------------------------
# BacklogGenerator Sınıfı
# ---------------------------------------------------------------------------


class BacklogGenerator:
    """Gereksinimlerden önceliklendirilmiş Product Backlog üretir.

    Skorlama formülü:
        priority_score = priority_weight × type_weight × conflict_penalty

    Çelişki listesinde geçen gereksinimler önce çözülmesi gerektiğinden
    ×1.5 çarpanı uygulanır ve sıralamada üste çıkar.
    """

    def generate(self, report: AnalysisReport) -> List[dict]:
        """AnalysisReport'tan önceliklendirilmiş Product Backlog üretir.

        Her gereksinim için:
        - priority_weight: HIGH=3, MEDIUM=2, LOW=1 (None → MEDIUM)
        - type_weight: FUNCTIONAL=1.0, NON_FUNCTIONAL=0.7, UNKNOWN=0.8
        - conflict_penalty: çelişkili req_id'lerde ×1.5

        Sonuç priority_score'a göre azalan sırayla döner.

        Args:
            report: NLP ve LLM analizleri tamamlanmış AnalysisReport nesnesi.

        Returns:
            list[dict]: Her biri {req_id, title, priority_score, story_points,
                        type, depends_on} içeren, sıralı backlog öğe listesi.
                        Gereksinim yoksa boş liste döner.
        """
        requirements = report.parsed_doc.requirements

        if not requirements:
            _log.info("Backlog üretimi atlandı: gereksinim yok.")
            return []

        conflicted_req_ids = _collect_conflicted_req_ids(report)
        _log.info(
            "Backlog üretimi başlatıldı | gereksinim_sayısı={} çelişkili={}",
            len(requirements),
            len(conflicted_req_ids),
        )

        items = [_build_backlog_item(req, conflicted_req_ids) for req in requirements]

        # priority_score'a göre azalan sırala (yüksek skor → önce)
        items.sort(key=lambda x: x["priority_score"], reverse=True)

        _log.info("Backlog üretimi tamamlandı | öğe_sayısı={}", len(items))
        return items
