"""Smoke tests for shared LLM mock fixtures (Issue #22)."""

from __future__ import annotations

import pytest

from modules.llm_client import LLMClientError
from modules.llm_response_utils import extract_json_object


def test_mock_llm_normal_returns_parseable_json(mock_llm_normal: object) -> None:
    """Normal mock yields JSON object via extract_json_object."""
    res = mock_llm_normal.chat(system_prompt="s", user_prompt="u")
    obj = extract_json_object(res.content)
    assert "conflicts" in obj


def test_mock_llm_empty_content(mock_llm_empty: object) -> None:
    """Empty mock returns empty string."""
    res = mock_llm_empty.chat(system_prompt="s", user_prompt="u")
    assert res.content == ""


def test_mock_llm_malformed_is_not_parseable(mock_llm_malformed: object) -> None:
    """Malformed JSON from mock fails extraction."""
    res = mock_llm_malformed.chat(system_prompt="s", user_prompt="u")
    with pytest.raises(ValueError):
        extract_json_object(res.content)


def test_mock_llm_rate_limit_raises(mock_llm_rate_limit: object) -> None:
    """Rate-limit mock surfaces LLMClientError."""
    with pytest.raises(LLMClientError):
        mock_llm_rate_limit.chat(system_prompt="s", user_prompt="u")


def test_mock_llm_markdown_wrapped_json(mock_llm_with_markdown: object) -> None:
    """Markdown-fenced JSON is tolerated by extract_json_object."""
    res = mock_llm_with_markdown.chat(system_prompt="s", user_prompt="u")
    obj = extract_json_object(res.content)
    assert obj.get("ok") is True
