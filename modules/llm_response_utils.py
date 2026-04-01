"""
modules/llm_response_utils.py — LLM metin yanıtlarından JSON çıkarma
"""

from __future__ import annotations

import json
from typing import Any


def extract_json_object(text: str) -> dict[str, Any]:
    """
    Model çıktısından tek bir JSON nesnesi çıkarır.
    Düz JSON veya metin içindeki ilk {...} bloğu denenir.
    """
    stripped = text.strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(stripped[start : end + 1])
        except json.JSONDecodeError:
            pass
    raise ValueError("LLM çıktısından geçerli JSON ayrıştırılamadı.")


__all__ = ["extract_json_object"]
