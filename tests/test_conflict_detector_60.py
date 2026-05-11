"""60 bağımsız vaka ile conflict_detector post-processing doğruluk testi.

Tüm vakalar deterministik (LLM çağrısı yok):
  conflicts_payload_to_report_dicts — 20 vaka
  _post_process_conflicts           — 30 vaka (filtre + dedup + sıralama)
  ConflictDetector mock entegrasyon — 10 vaka
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from modules.analysis_report_parsing import conflicts_payload_to_report_dicts
from modules.conflict_detector import (
    CONFIDENCE_THRESHOLD,
    ConflictDetector,
    _deduplicate_conflicts,
    _post_process_conflicts,
)
from core.models import ParsedDocument, Requirement


# ---------------------------------------------------------------------------
# Yardımcılar
# ---------------------------------------------------------------------------

def _req(rid: str) -> Requirement:
    return Requirement(id=rid, text=f"Gereksinim {rid}")


def _doc(*ids: str) -> ParsedDocument:
    return ParsedDocument(raw_text=" ".join(ids), requirements=[_req(i) for i in ids])


def _conflict(req_ids: list, confidence: float | None = None, ctype: str = "logic") -> dict:
    c: dict[str, Any] = {
        "requirements": req_ids,
        "type": ctype,
        "short_summary": "Özet",
        "detailed_explanation": "Açıklama",
    }
    if confidence is not None:
        c["confidence"] = confidence
    return c


# ---------------------------------------------------------------------------
# 1) conflicts_payload_to_report_dicts — 20 vaka
# ---------------------------------------------------------------------------

PARSING_CASES: list[tuple[dict, list]] = [
    # Temel dönüşüm
    (
        {"conflicts": [_conflict(["R1", "R2"], 0.9)]},
        [{"req_ids": ["R1", "R2"], "conflict_type": "logic",
          "reason": "Özet\n\nAçıklama", "confidence": 0.9}],
    ),
    # confidence yok → satırda confidence alanı olmamalı
    (
        {"conflicts": [_conflict(["R1"], None)]},
        [{"req_ids": ["R1"], "conflict_type": "logic", "reason": "Özet\n\nAçıklama"}],
    ),
    # Boş conflicts listesi
    ({"conflicts": []}, []),
    # conflicts anahtarı yok
    ({}, []),
    # None conflicts
    ({"conflicts": None}, []),
    # severity ve suggested_resolution taşınmalı
    (
        {"conflicts": [{
            "requirements": ["R1", "R2"], "type": "security",
            "short_summary": "S", "detailed_explanation": "D",
            "severity": "high", "suggested_resolution": "Çözüm",
            "confidence": 0.75,
        }]},
        [{"req_ids": ["R1", "R2"], "conflict_type": "security",
          "reason": "S\n\nD", "severity": "high",
          "suggested_resolution": "Çözüm", "confidence": 0.75}],
    ),
    # id alanı taşınmalı
    (
        {"conflicts": [{"id": "C1", "requirements": ["R3"], "type": "logic",
                        "short_summary": "S", "detailed_explanation": "D",
                        "confidence": 0.8}]},
        [{"req_ids": ["R3"], "conflict_type": "logic", "reason": "S\n\nD",
          "id": "C1", "confidence": 0.8}],
    ),
    # Sadece short_summary (detailed_explanation yok)
    (
        {"conflicts": [{"requirements": ["R1"], "type": "other",
                        "short_summary": "Kısa özet", "confidence": 0.65}]},
        [{"req_ids": ["R1"], "conflict_type": "other",
          "reason": "Kısa özet", "confidence": 0.65}],
    ),
    # Sadece detailed_explanation
    (
        {"conflicts": [{"requirements": ["R2"], "type": "other",
                        "detailed_explanation": "Uzun açıklama"}]},
        [{"req_ids": ["R2"], "conflict_type": "other", "reason": "Uzun açıklama"}],
    ),
    # requirements string (liste değil) → listeye çevrilmeli
    (
        {"conflicts": [{"requirements": "R1", "type": "logic",
                        "short_summary": "S", "confidence": 0.7}]},
        [{"req_ids": ["R1"], "conflict_type": "logic",
          "reason": "S", "confidence": 0.7}],
    ),
    # confidence string → float'a çevrilmeli
    (
        {"conflicts": [_conflict(["R1", "R2"]) | {"confidence": "0.82"}]},
        [{"req_ids": ["R1", "R2"], "conflict_type": "logic",
          "reason": "Özet\n\nAçıklama", "confidence": 0.82}],
    ),
    # confidence geçersiz string → alanı atla
    (
        {"conflicts": [_conflict(["R1"]) | {"confidence": "yüksek"}]},
        [{"req_ids": ["R1"], "conflict_type": "logic", "reason": "Özet\n\nAçıklama"}],
    ),
    # İkiden fazla gereksinim
    (
        {"conflicts": [_conflict(["R1", "R2", "R3"], 0.95)]},
        [{"req_ids": ["R1", "R2", "R3"], "conflict_type": "logic",
          "reason": "Özet\n\nAçıklama", "confidence": 0.95}],
    ),
    # Birden fazla conflict
    (
        {"conflicts": [
            _conflict(["R1", "R2"], 0.9),
            _conflict(["R3", "R4"], 0.7),
        ]},
        [
            {"req_ids": ["R1", "R2"], "conflict_type": "logic",
             "reason": "Özet\n\nAçıklama", "confidence": 0.9},
            {"req_ids": ["R3", "R4"], "conflict_type": "logic",
             "reason": "Özet\n\nAçıklama", "confidence": 0.7},
        ],
    ),
    # Dict olmayan conflict öğesi → atlanmalı
    (
        {"conflicts": [_conflict(["R1"], 0.9), "bozuk veri", None]},
        [{"req_ids": ["R1"], "conflict_type": "logic",
          "reason": "Özet\n\nAçıklama", "confidence": 0.9}],
    ),
    # type alanı yok → "other" varsayılan
    (
        {"conflicts": [{"requirements": ["R1"], "short_summary": "S"}]},
        [{"req_ids": ["R1"], "conflict_type": "other", "reason": "S"}],
    ),
    # requirements boş liste
    (
        {"conflicts": [{"requirements": [], "type": "logic", "short_summary": "S",
                        "confidence": 0.8}]},
        [{"req_ids": [], "conflict_type": "logic", "reason": "S", "confidence": 0.8}],
    ),
    # İki conflict: biri confidence var, biri yok
    (
        {"conflicts": [
            _conflict(["R1"], 0.9),
            _conflict(["R2"], None),
        ]},
        [
            {"req_ids": ["R1"], "conflict_type": "logic",
             "reason": "Özet\n\nAçıklama", "confidence": 0.9},
            {"req_ids": ["R2"], "conflict_type": "logic", "reason": "Özet\n\nAçıklama"},
        ],
    ),
    # confidence 0.0 → taşınmalı
    (
        {"conflicts": [_conflict(["R1"], 0.0)]},
        [{"req_ids": ["R1"], "conflict_type": "logic",
          "reason": "Özet\n\nAçıklama", "confidence": 0.0}],
    ),
    # conflict_type bilinmeyen değer → olduğu gibi geçer
    (
        {"conflicts": [_conflict(["R1"], 0.8, ctype="custom_type")]},
        [{"req_ids": ["R1"], "conflict_type": "custom_type",
          "reason": "Özet\n\nAçıklama", "confidence": 0.8}],
    ),
]


# ---------------------------------------------------------------------------
# 2) _post_process_conflicts — 30 vaka
# ---------------------------------------------------------------------------

def _row(req_ids: list, confidence: float | None = None) -> dict:
    r: dict[str, Any] = {"req_ids": req_ids, "conflict_type": "logic", "reason": "R"}
    if confidence is not None:
        r["confidence"] = confidence
    return r


VALID_IDS = {"R1", "R2", "R3", "R4", "R5"}

POST_CASES: list[tuple[list, set, list]] = [
    # Temel geçen vaka (confidence ≥ 0.6 + valid IDs)
    ([_row(["R1", "R2"], 0.9)], VALID_IDS, [_row(["R1", "R2"], 0.9)]),
    # confidence < 0.6 → filtrelenmeli
    ([_row(["R1", "R2"], 0.5)], VALID_IDS, []),
    # Eşik tam 0.6 → geçmeli
    ([_row(["R1", "R2"], 0.6)], VALID_IDS, [_row(["R1", "R2"], 0.6)]),
    # Geçersiz ID → filtrelenmeli
    ([_row(["X99", "X100"], 0.9)], VALID_IDS, []),
    # Kısmen geçerli ID (R1 var, X99 yok) → tutulmalı
    ([_row(["R1", "X99"], 0.9)], VALID_IDS, [_row(["R1", "X99"], 0.9)]),
    # Boş liste → boş döner
    ([], VALID_IDS, []),
    # Tümü geçerli ve yeterli confidence
    (
        [_row(["R1", "R2"], 0.9), _row(["R3", "R4"], 0.75)],
        VALID_IDS,
        [_row(["R1", "R2"], 0.9), _row(["R3", "R4"], 0.75)],
    ),
    # Sıralama: düşük confidence önce verilmiş, yüksek önce gelmeli
    (
        [_row(["R3", "R4"], 0.7), _row(["R1", "R2"], 0.9)],
        VALID_IDS,
        [_row(["R1", "R2"], 0.9), _row(["R3", "R4"], 0.7)],
    ),
    # confidence yok → 1.0 varsayılan → geçmeli
    ([_row(["R1", "R2"])], VALID_IDS, [_row(["R1", "R2"])]),
    # Karma: biri filtreli, biri geçerli
    (
        [_row(["R1", "R2"], 0.3), _row(["R3", "R4"], 0.8)],
        VALID_IDS,
        [_row(["R3", "R4"], 0.8)],
    ),
    # Dedup: aynı req_ids → yüksek confidence'lı kalmalı
    (
        [_row(["R1", "R2"], 0.7), _row(["R1", "R2"], 0.9)],
        VALID_IDS,
        [_row(["R1", "R2"], 0.9)],
    ),
    # Dedup: farklı sıra ama aynı set → dedup
    (
        [_row(["R2", "R1"], 0.8), _row(["R1", "R2"], 0.7)],
        VALID_IDS,
        [_row(["R2", "R1"], 0.8)],
    ),
    # Dedup: üç tekrar → en yüksek kalmalı
    (
        [_row(["R1", "R2"], 0.6), _row(["R1", "R2"], 0.75), _row(["R1", "R2"], 0.65)],
        VALID_IDS,
        [_row(["R1", "R2"], 0.75)],
    ),
    # Dedup + filtre: tekrar ama biri 0.4 → 0.4 filtrelenir, 0.7 kalır
    (
        [_row(["R1", "R2"], 0.4), _row(["R1", "R2"], 0.7)],
        VALID_IDS,
        [_row(["R1", "R2"], 0.7)],
    ),
    # Farklı pairs → iki ayrı conflict kalmalı
    (
        [_row(["R1", "R2"], 0.9), _row(["R3", "R4"], 0.8)],
        VALID_IDS,
        [_row(["R1", "R2"], 0.9), _row(["R3", "R4"], 0.8)],
    ),
    # Geçersiz IDs + low confidence: ikisi de gitmeli
    (
        [_row(["X1"], 0.3), _row(["X2", "X3"], 0.9)],
        VALID_IDS,
        [],
    ),
    # valid_ids boşsa ID filtresi geçer ama confidence filtresi uygulanır
    (
        [_row(["X99"], 0.9), _row(["X100"], 0.4)],
        set(),
        [_row(["X99"], 0.9)],
    ),
    # Üç conflict, sıralama doğrulanmalı
    (
        [_row(["R1", "R2"], 0.65), _row(["R3", "R4"], 0.95), _row(["R2", "R3"], 0.8)],
        VALID_IDS,
        [_row(["R3", "R4"], 0.95), _row(["R2", "R3"], 0.8), _row(["R1", "R2"], 0.65)],
    ),
    # req_ids boş liste → ID filtresi geçer (id_field None değil, boş liste)
    (
        [_row([], 0.8)],
        VALID_IDS,
        [],
    ),
    # confidence tam 0.59 → filtrelenmeli (< 0.6)
    ([_row(["R1", "R2"], 0.59)], VALID_IDS, []),
    # Tek geçerli, tek geçersiz confidence
    (
        [_row(["R1", "R2"], 0.9), _row(["R3", "R4"], 0.59)],
        VALID_IDS,
        [_row(["R1", "R2"], 0.9)],
    ),
    # Tüm conflictler geçersiz IDs + yüksek confidence
    (
        [_row(["Z1", "Z2"], 0.95), _row(["Z3"], 0.8)],
        VALID_IDS,
        [],
    ),
    # Beş conflict: 2 filtreli, 1 duplikat, 2 geçerli — doğru sonuç
    (
        [
            _row(["R1", "R2"], 0.9),
            _row(["R1", "R2"], 0.7),   # duplikat, daha düşük → atılır
            _row(["R3", "R4"], 0.4),   # confidence < 0.6 → atılır
            _row(["Z9"], 0.95),        # geçersiz ID → atılır
            _row(["R2", "R5"], 0.75),
        ],
        VALID_IDS,
        [_row(["R1", "R2"], 0.9), _row(["R2", "R5"], 0.75)],
    ),
    # Dedup: aynı pair, biri confidence yok (1.0 kabul) → 1.0 > 0.9 → confidence yok olan kalır
    (
        [_row(["R1", "R2"], 0.9), _row(["R1", "R2"])],
        VALID_IDS,
        [_row(["R1", "R2"])],   # confidence=None → 1.0 > 0.9 → bu kalır
    ),
    # req_ids yok (None) → ID filtresi atlar, confidence filtresi uygulanır
    (
        [{"conflict_type": "logic", "reason": "R", "confidence": 0.8}],
        VALID_IDS,
        [{"conflict_type": "logic", "reason": "R", "confidence": 0.8}],
    ),
    # req_ids yok + düşük confidence → confidence filtresi atar
    (
        [{"conflict_type": "logic", "reason": "R", "confidence": 0.4}],
        VALID_IDS,
        [],
    ),
    # Sadece duplikat — her ikisi de geçerli confidence → yüksek kalır
    (
        [_row(["R4", "R5"], 0.85), _row(["R4", "R5"], 0.62)],
        VALID_IDS,
        [_row(["R4", "R5"], 0.85)],
    ),
    # Büyük batch: 5 farklı pair, hepsi geçerli (threshold=0.6), sıralama doğrulanmalı
    (
        [
            _row(["R1", "R2"], 0.72),
            _row(["R2", "R3"], 0.88),
            _row(["R3", "R4"], 0.64),
            _row(["R4", "R5"], 0.91),
            _row(["R1", "R5"], 0.77),
        ],
        VALID_IDS,
        [
            _row(["R4", "R5"], 0.91),
            _row(["R2", "R3"], 0.88),
            _row(["R1", "R5"], 0.77),
            _row(["R1", "R2"], 0.72),
            _row(["R3", "R4"], 0.64),
        ],
    ),
    # Threshold 0.8 → 0.72, 0.64, 0.75 filtrelenir; 0.85, 0.88, 0.91 kalır
    (
        [_row(["R1", "R2"], 0.75), _row(["R3", "R4"], 0.85)],
        VALID_IDS,
        [_row(["R3", "R4"], 0.85)],
    ),
    # Her şey filtrelenir (confidence=0.0 falsy ama gerçek sıfır olarak değerlendirilmeli)
    (
        [_row(["R1", "R2"], 0.1), _row(["R3", "R4"], 0.0)],
        VALID_IDS,
        [],
    ),
]

# 28 ve 29 numaralı vakalar 0.8 threshold kullanır
POST_THRESHOLD_OVERRIDES = {28: 0.6, 29: 0.8}


# ---------------------------------------------------------------------------
# 3) ConflictDetector mock entegrasyon — 10 vaka
# ---------------------------------------------------------------------------

def _make_detector_with_mock(llm_response: str) -> ConflictDetector:
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.content = llm_response
    mock_client.chat.return_value = mock_resp
    return ConflictDetector(llm_client=mock_client)


INTEGRATION_CASES: list[tuple[str, list[str], int]] = [
    # (LLM JSON, belgedeki gereksinim IDleri, beklenen conflict sayısı)
    # Tümü geçerli + yüksek confidence
    (
        '{"conflicts": [{"requirements": ["R1","R2"], "type":"logic",'
        '"short_summary":"S","confidence":0.9}], "meta":{}}',
        ["R1", "R2", "R3"],
        1,
    ),
    # confidence < 0.6 → filtreli, 0 conflict
    (
        '{"conflicts": [{"requirements": ["R1","R2"], "type":"logic",'
        '"short_summary":"S","confidence":0.4}], "meta":{}}',
        ["R1", "R2"],
        0,
    ),
    # Hallucinated ID → filtreli
    (
        '{"conflicts": [{"requirements": ["X99","X100"], "type":"logic",'
        '"short_summary":"S","confidence":0.9}], "meta":{}}',
        ["R1", "R2"],
        0,
    ),
    # İki conflict: biri filtreli, biri geçerli
    (
        '{"conflicts": ['
        '{"requirements":["R1","R2"],"type":"logic","short_summary":"S","confidence":0.85},'
        '{"requirements":["R1","R2"],"type":"logic","short_summary":"S","confidence":0.3}'
        '], "meta":{}}',
        ["R1", "R2", "R3"],
        1,
    ),
    # Duplikat aynı pair → 1 kalır
    (
        '{"conflicts": ['
        '{"requirements":["R1","R2"],"type":"logic","short_summary":"S","confidence":0.7},'
        '{"requirements":["R2","R1"],"type":"logic","short_summary":"S","confidence":0.8}'
        '], "meta":{}}',
        ["R1", "R2"],
        1,
    ),
    # Boş conflicts
    ('{"conflicts": [], "meta":{}}', ["R1", "R2"], 0),
    # Markdown fenced JSON
    (
        '```json\n{"conflicts": [{"requirements":["R1","R2"],"type":"logic",'
        '"short_summary":"S","confidence":0.75}], "meta":{}}\n```',
        ["R1", "R2"],
        1,
    ),
    # meta.total_conflicts güncellenmeli (LLM 2 dedi ama 1'i filtrelendi)
    (
        '{"conflicts": ['
        '{"requirements":["R1","R2"],"type":"logic","short_summary":"S","confidence":0.9},'
        '{"requirements":["R3","R4"],"type":"logic","short_summary":"S","confidence":0.3}'
        '], "meta":{"total_requirements":4,"total_conflicts":2,"confidence":"high"}}',
        ["R1", "R2", "R3", "R4"],
        1,
    ),
    # confidence yok → 1.0 varsayılan → geçer
    (
        '{"conflicts": [{"requirements":["R1","R2"],"type":"logic","short_summary":"S"}],'
        '"meta":{}}',
        ["R1", "R2"],
        1,
    ),
    # Gereksinim listesi boş → ConflictDetector direkt boş döner (LLM çağrısı yok)
    ("", [], 0),
]


# ---------------------------------------------------------------------------
# Çalıştırıcı
# ---------------------------------------------------------------------------

def _subset_match(result: dict, expected: dict) -> bool:
    """Beklenen her alan sonuçta var mı ve eşit mi kontrol eder."""
    for k, v in expected.items():
        if k not in result:
            return False
        if result[k] != v:
            return False
    return True


def run():
    total = 0
    failures = []

    # --- 1) conflicts_payload_to_report_dicts ---
    print("=== conflicts_payload_to_report_dicts — 20 vaka ===")
    for i, (payload, expected) in enumerate(PARSING_CASES, 1):
        total += 1
        result = conflicts_payload_to_report_dicts(payload)
        ok = result == expected
        mark = "OK" if ok else "XX"
        print(f"{mark} {i:2} payload_conflicts={len(payload.get('conflicts') or [])} → {len(result)} satır")
        if not ok:
            failures.append(("PARSE", i, payload, result, expected))

    # --- 2) _post_process_conflicts ---
    print("\n=== _post_process_conflicts — 30 vaka ===")
    for i, (rows, valid_ids, expected) in enumerate(POST_CASES, 1):
        total += 1
        threshold = POST_THRESHOLD_OVERRIDES.get(i, CONFIDENCE_THRESHOLD)
        result = _post_process_conflicts(rows, valid_ids, threshold=threshold)
        ok = result == expected
        mark = "OK" if ok else "XX"
        confs = [r.get("confidence", "?") for r in rows]
        print(f"{mark} {i:2} girdi={len(rows)} conf={confs} → {len(result)} kaldı")
        if not ok:
            failures.append(("POST", i, rows, result, expected))

    # --- 3) ConflictDetector entegrasyon ---
    print("\n=== ConflictDetector mock entegrasyon — 10 vaka ===")
    for i, (llm_json, req_ids, expected_count) in enumerate(INTEGRATION_CASES, 1):
        total += 1
        try:
            if not req_ids:
                # Boş belge → direkt test
                det = ConflictDetector()
                doc = _doc()
                result_obj = det.analyze_pairwise(doc)
            else:
                det = _make_detector_with_mock(llm_json)
                doc = _doc(*req_ids)
                result_obj = det.analyze_pairwise(doc)
            got_count = len(result_obj.conflicts)
            ok = got_count == expected_count
        except Exception as e:
            ok = False
            got_count = f"HATA: {e}"
        mark = "OK" if ok else "XX"
        print(f"{mark} {i:2} reqs={req_ids} → conflicts={got_count} (beklenen={expected_count})")
        if not ok:
            failures.append(("INTEG", i, llm_json[:60], got_count, expected_count))

    # --- Özet ---
    passed = total - len(failures)
    pct = passed / total * 100
    print(f"\nDoğruluk: {passed}/{total} = %{pct:.1f}")
    if failures:
        print(f"\nBaşarısız ({len(failures)}):")
        for group, i, inp, got, exp in failures:
            print(f"  [{group}#{i}]")
            print(f"    got = {got!r}")
            print(f"    exp = {exp!r}")


if __name__ == "__main__":
    run()
