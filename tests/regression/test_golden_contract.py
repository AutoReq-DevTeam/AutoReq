"""
Golden dataset structural validation — no LLM (Issue #22).
"""

from __future__ import annotations

import json
from pathlib import Path

from tests.regression.golden_utils import EXPECTED_DIR, SAMPLE_DIR, list_golden_sample_ids


def test_golden_sample_count_matches_expected() -> None:
    """Exactly the same number of .txt samples and .json expectations."""
    txts = list(SAMPLE_DIR.glob("sample_*.txt"))
    jsons = list(EXPECTED_DIR.glob("sample_*.json"))
    assert len(txts) == 20
    assert len(jsons) == 20


def test_golden_expected_schema() -> None:
    """Each expected JSON has AnalysisReport-shaped conflict/gap dicts."""
    valid_conflict_types = {
        "logic",
        "business_rule",
        "performance",
        "security",
        "usability",
        "other",
    }
    valid_severity = {"high", "medium", "low"}
    for sample_id in list_golden_sample_ids():
        path = EXPECTED_DIR / f"sample_{sample_id}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "conflicts" in data and isinstance(data["conflicts"], list)
        assert "gaps" in data and isinstance(data["gaps"], list)
        for c in data["conflicts"]:
            assert "req_ids" in c and isinstance(c["req_ids"], list)
            assert c.get("conflict_type") in valid_conflict_types
            assert "reason" in c and isinstance(c["reason"], str) and c["reason"].strip()
        for g in data["gaps"]:
            for key in ("missing_area", "suggestion", "severity"):
                assert key in g
            assert g["severity"] in valid_severity
