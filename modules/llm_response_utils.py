"""
modules/llm_response_utils.py — LLM metin yanıtlarından JSON çıkarma
"""

from __future__ import annotations

import json
import re
from typing import Any


def _clean_markdown_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json|json5)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def extract_json_object(text: str) -> Any:
    """
    Model çıktısından JSON verisini çıkarır (dict veya list olabilir).
    Geriye dönük uyumluluk için ismi extract_json_object bırakılmıştır.
    """
    cleaned = _clean_markdown_json(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    first_brace = cleaned.find("{")
    first_bracket = cleaned.find("[")
    
    start_idx = -1
    end_idx = -1
    
    if first_brace != -1 and (first_bracket == -1 or first_brace < first_bracket):
        start_idx = first_brace
        end_idx = cleaned.rfind("}")
    elif first_bracket != -1:
        start_idx = first_bracket
        end_idx = cleaned.rfind("]")
        
    if start_idx != -1 and end_idx > start_idx:
        try:
            return json.loads(cleaned[start_idx : end_idx + 1])
        except json.JSONDecodeError:
            pass
            
    raise ValueError("LLM çıktısından geçerli JSON ayrıştırılamadı.")


__all__ = ["extract_json_object"]
