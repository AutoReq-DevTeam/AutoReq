"""
Prompt builder string snapshots — no live LLM (Issue #22, syrupy).
"""

from __future__ import annotations

import pytest

from modules.bdd_prompts import (
    build_bdd_generation_system_prompt,
    build_bdd_generation_user_prompt,
)
from modules.conflict_detector import _format_requirements_block
from modules.conflict_prompts import (
    build_conflict_detection_system_prompt,
    build_pairwise_conflict_user_prompt,
)
from modules.gap_prompts import build_gap_analysis_system_prompt, build_gap_analysis_user_prompt
from modules.improver_prompts import build_improvement_system_prompt, build_improvement_user_prompt
from modules.story_prompts import (
    build_story_generation_system_prompt,
    build_story_generation_user_prompt,
)
from tests.regression.golden_utils import (
    first_requirement_from_sample_text,
    list_golden_sample_ids,
    load_sample_text,
    parsed_document_from_sample_text,
)


def test_snapshot_conflict_detection_system_prompt(snapshot: object) -> None:
    """Full conflict system prompt string is frozen."""
    assert build_conflict_detection_system_prompt() == snapshot


def test_snapshot_gap_analysis_system_prompt(snapshot: object) -> None:
    """Full gap system prompt string is frozen."""
    assert build_gap_analysis_system_prompt() == snapshot


def test_snapshot_improvement_system_prompt(snapshot: object) -> None:
    """Full improver system prompt string is frozen."""
    assert build_improvement_system_prompt() == snapshot


def test_snapshot_story_generation_system_prompt(snapshot: object) -> None:
    """Full user-story system prompt string is frozen."""
    assert build_story_generation_system_prompt() == snapshot


def test_snapshot_bdd_generation_system_prompt(snapshot: object) -> None:
    """Full BDD system prompt string is frozen."""
    assert build_bdd_generation_system_prompt() == snapshot


@pytest.mark.parametrize("sample_id", list_golden_sample_ids())
def test_snapshot_pairwise_conflict_user_prompt(snapshot: object, sample_id: str) -> None:
    """Per golden sample: conflict user prompt built from formatted block."""
    raw = load_sample_text(sample_id)
    doc = parsed_document_from_sample_text(raw)
    block = _format_requirements_block(doc)
    prompt = build_pairwise_conflict_user_prompt(block, len(doc.requirements))
    assert prompt == snapshot


@pytest.mark.parametrize("sample_id", list_golden_sample_ids())
def test_snapshot_gap_analysis_user_prompt(snapshot: object, sample_id: str) -> None:
    """Per golden sample: gap user prompt without domain hint."""
    raw = load_sample_text(sample_id)
    doc = parsed_document_from_sample_text(raw)
    block = _format_requirements_block(doc)
    prompt = build_gap_analysis_user_prompt(block, len(doc.requirements))
    assert prompt == snapshot


def test_snapshot_gap_analysis_user_prompt_with_domain_hint(snapshot: object) -> None:
    """Gap user prompt with optional domain_hint branch covered."""
    raw = load_sample_text("01")
    doc = parsed_document_from_sample_text(raw)
    block = _format_requirements_block(doc)
    prompt = build_gap_analysis_user_prompt(
        block,
        len(doc.requirements),
        domain_hint="B2C e-ticaret",
    )
    assert prompt == snapshot


@pytest.mark.parametrize("sample_id", list_golden_sample_ids())
def test_snapshot_improvement_user_prompt(snapshot: object, sample_id: str) -> None:
    """Improver user prompt for first line of each golden sample."""
    raw = load_sample_text(sample_id)
    doc = parsed_document_from_sample_text(raw)
    first_line = doc.requirements[0].text if doc.requirements else ""
    assert build_improvement_user_prompt(first_line) == snapshot


@pytest.mark.parametrize("sample_id", list_golden_sample_ids())
def test_snapshot_story_generation_user_prompt(snapshot: object, sample_id: str) -> None:
    """Story user prompt from synthetic Requirement per golden file."""
    raw = load_sample_text(sample_id)
    req = first_requirement_from_sample_text(raw)
    assert build_story_generation_user_prompt(req) == snapshot


@pytest.mark.parametrize("sample_id", list_golden_sample_ids())
def test_snapshot_bdd_generation_user_prompt(snapshot: object, sample_id: str) -> None:
    """BDD user prompt from synthetic Requirement per golden file."""
    raw = load_sample_text(sample_id)
    req = first_requirement_from_sample_text(raw)
    assert build_bdd_generation_user_prompt(req) == snapshot
