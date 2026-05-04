import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from modules.llm_client import LLMClient, LLMClientError, LLMResponse


@pytest.fixture
def mock_llm_normal() -> MagicMock:
    """
    LLM mock that returns minimal valid JSON for conflict-style responses.

    Returns:
        MagicMock: Client with ``chat`` returning :class:`LLMResponse`.
    """
    client = MagicMock(spec=LLMClient)
    payload = (
        '{"conflicts":[],"meta":{"total_requirements":1,"total_conflicts":0,"confidence":"high"}}'
    )
    client.chat.return_value = LLMResponse(content=payload, raw={})
    return client


@pytest.fixture
def mock_llm_empty() -> MagicMock:
    """
    LLM mock returning empty model text.

    Returns:
        MagicMock: Client whose ``chat`` yields empty ``content``.
    """
    client = MagicMock(spec=LLMClient)
    client.chat.return_value = LLMResponse(content="", raw={})
    return client


@pytest.fixture
def mock_llm_malformed() -> MagicMock:
    """
    LLM mock returning syntactically invalid JSON.

    Returns:
        MagicMock: Client whose ``chat`` yields broken JSON text.
    """
    client = MagicMock(spec=LLMClient)
    client.chat.return_value = LLMResponse(content='{"key":}', raw={})
    return client


@pytest.fixture
def mock_llm_rate_limit() -> MagicMock:
    """
    LLM mock simulating HTTP 429 / rate limit.

    Returns:
        MagicMock: Client whose ``chat`` raises :class:`LLMClientError`.
    """
    client = MagicMock(spec=LLMClient)
    client.chat.side_effect = LLMClientError("429 Too Many Requests")
    return client


@pytest.fixture
def mock_llm_with_markdown() -> MagicMock:
    """
    LLM mock returning JSON wrapped in a markdown fence.

    Returns:
        MagicMock: Client simulating Gemini-style fenced output.
    """
    client = MagicMock(spec=LLMClient)
    fenced = '```json\n{"ok": true}\n```'
    client.chat.return_value = LLMResponse(content=fenced, raw={})
    return client
