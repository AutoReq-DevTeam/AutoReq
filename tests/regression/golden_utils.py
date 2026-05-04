"""Golden sample helpers for prompt regression tests (Issue #22)."""

from __future__ import annotations

from pathlib import Path

from core.models import ParsedDocument, Requirement

GOLDEN_ROOT: Path = Path(__file__).resolve().parents[1] / "golden"
SAMPLE_DIR: Path = GOLDEN_ROOT / "sample_requirements"
EXPECTED_DIR: Path = GOLDEN_ROOT / "expected"


def list_golden_sample_ids() -> list[str]:
    """
    Return sorted two-digit IDs (e.g. '01'..'20') for sample_*.txt files.

    Returns:
        list[str]: Basenames without prefix/suffix, zero-padded.
    """
    paths = sorted(SAMPLE_DIR.glob("sample_*.txt"))
    return [p.stem.replace("sample_", "") for p in paths]


def load_sample_text(sample_id: str) -> str:
    """
    Read raw requirements text for a golden sample.

    Args:
        sample_id: Two-digit id matching ``sample_{id}.txt``.

    Returns:
        str: File contents (UTF-8).
    """
    path = SAMPLE_DIR / f"sample_{sample_id}.txt"
    return path.read_text(encoding="utf-8")


def parsed_document_from_sample_text(raw_text: str) -> ParsedDocument:
    """
    Split non-empty lines into FUNCTIONAL Requirement rows with REQ_NNN ids.

    Args:
        raw_text: Multi-line Turkish requirement text.

    Returns:
        ParsedDocument: Populated ``requirements`` and ``total_sentences``.
    """
    lines = [ln.strip() for ln in raw_text.strip().splitlines() if ln.strip()]
    requirements: list[Requirement] = []
    for i, line in enumerate(lines):
        requirements.append(
            Requirement(
                id=f"REQ_{i + 1:03d}",
                text=line,
                req_type="FUNCTIONAL",
                priority="MEDIUM",
            )
        )
    return ParsedDocument(raw_text=raw_text, requirements=requirements, total_sentences=len(lines))


def first_requirement_from_sample_text(raw_text: str) -> Requirement:
    """
    Build a single Requirement from the first non-empty line (story/BDD prompts).

    Args:
        raw_text: Multi-line sample text.

    Returns:
        Requirement: First sentence as REQ_001, UNKNOWN type, MEDIUM priority.
    """
    doc = parsed_document_from_sample_text(raw_text)
    if not doc.requirements:
        return Requirement(id="REQ_001", text="(boş)", req_type="UNKNOWN", priority="MEDIUM")
    first = doc.requirements[0]
    return Requirement(
        id="REQ_001",
        text=first.text,
        req_type="UNKNOWN",
        priority="MEDIUM",
        actors=["kullanıcı"],
        objects=["sistem"],
    )
