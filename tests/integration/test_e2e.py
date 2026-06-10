"""
tests/integration/test_e2e.py — Uçtan Uca Entegrasyon Testleri

Issue #21 AC: process_text() <15s, report.parsed_doc.requirements non-empty.

Bu testler gerçek NLP motorunu kullanır (Stanza). LLM yok (GEMINI_API_KEY unset).
Paralel çıktı üreticileri (SRS, XLSX, DOCX) mock'lanarak dosya sistemi kirlenmez.
"""

import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

SAMPLES_DIR = Path(__file__).parent.parent.parent / "data" / "samples"


@pytest.fixture(scope="module")
def eticaret_text():
    path = SAMPLES_DIR / "ornek_eticaret.txt"
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def bankacilik_text():
    path = SAMPLES_DIR / "ornek_bankacilik.txt"
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def egitim_text():
    path = SAMPLES_DIR / "ornek_egitim.txt"
    return path.read_text(encoding="utf-8")


def _run_pipeline(text, monkeypatch):
    """Call process_text() with output generators mocked (no filesystem side-effects)."""
    import core.pipeline as pm

    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(pm, "generate_srs", MagicMock())
    monkeypatch.setattr(pm, "export_backlog_xlsx", MagicMock())
    monkeypatch.setattr(pm, "export_stories_docx", MagicMock())
    monkeypatch.setattr(pm, "export_report_json", MagicMock())
    monkeypatch.setattr(pm, "BacklogGenerator", MagicMock())
    monkeypatch.setattr(pm, "StoryGenerator", MagicMock())
    monkeypatch.setattr(pm, "BDDGenerator", MagicMock())

    start = time.monotonic()
    report = pm.process_text(text)
    elapsed = time.monotonic() - start
    return report, elapsed


def test_e2e_eticaret_report_structure(eticaret_text, monkeypatch):
    """process_text() on e-ticaret sample produces a non-empty AnalysisReport."""
    from core.models import AnalysisReport

    report, _ = _run_pipeline(eticaret_text, monkeypatch)
    assert isinstance(report, AnalysisReport)
    assert len(report.parsed_doc.requirements) > 0, (
        "E-ticaret örneği en az 1 gereksinim üretmeli."
    )


def test_e2e_eticaret_under_15s(eticaret_text, monkeypatch):
    """Issue #21 AC: process_text() on a sample file must complete in <15 seconds."""
    _, elapsed = _run_pipeline(eticaret_text, monkeypatch)
    assert elapsed < 15.0, (
        f"Pipeline {elapsed:.2f}s sürdü — NFR hedefi <15s aşıldı."
    )


def test_e2e_bankacilik_report_structure(bankacilik_text, monkeypatch):
    """process_text() on bankacılık sample produces a non-empty AnalysisReport."""
    from core.models import AnalysisReport

    report, _ = _run_pipeline(bankacilik_text, monkeypatch)
    assert isinstance(report, AnalysisReport)
    assert len(report.parsed_doc.requirements) > 0


def test_e2e_egitim_report_structure(egitim_text, monkeypatch):
    """process_text() on eğitim sample produces a non-empty AnalysisReport."""
    from core.models import AnalysisReport

    report, _ = _run_pipeline(egitim_text, monkeypatch)
    assert isinstance(report, AnalysisReport)
    assert len(report.parsed_doc.requirements) > 0


def test_e2e_requirements_have_types(eticaret_text, monkeypatch):
    """Each requirement must have a req_type of FUNCTIONAL, NON_FUNCTIONAL, or UNKNOWN."""
    report, _ = _run_pipeline(eticaret_text, monkeypatch)
    valid_types = {"FUNCTIONAL", "NON_FUNCTIONAL", "UNKNOWN"}
    for req in report.parsed_doc.requirements:
        assert req.req_type in valid_types, (
            f"Geçersiz req_type '{req.req_type}' — REQ {req.id}"
        )


def test_e2e_requirements_have_priority(eticaret_text, monkeypatch):
    """Each requirement must have a priority assigned (HIGH, MEDIUM, or LOW)."""
    report, _ = _run_pipeline(eticaret_text, monkeypatch)
    for req in report.parsed_doc.requirements:
        assert req.priority in ("HIGH", "MEDIUM", "LOW"), (
            f"Priority atanmamış — REQ {req.id}"
        )
