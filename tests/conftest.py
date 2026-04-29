import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_llm_client():
    from modules.llm_client import LLMResponse
    client = MagicMock()
    # Varsayılan olarak boş veya genel bir JSON dönecek şekilde ayarlanabilir
    mock_response = LLMResponse(
        content='{}',
        raw={"provider": "mock", "usage_metadata": {"input_tokens": 0, "output_tokens": 0}},
    )
    client.chat.return_value = mock_response
    return client