"""
modules/llm_response_utils.py — LLM metin yanıtlarından JSON çıkarma ve sonuç işleme
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


def _find_json_span(text: str, open_char: str) -> tuple[int, int] | None:
    """Brace counting ile ilk tam JSON object/array'in [start, end) aralığını bulur.

    rfind yaklaşımının aksine string literal içindeki brace'leri yok sayar
    ve LLM'in JSON'dan sonra yazdığı açıklama metnini doğru keser.
    """
    close_char = "}" if open_char == "{" else "]"
    start = text.find(open_char)
    if start == -1:
        return None

    depth = 0
    in_string = False
    i = start
    while i < len(text):
        c = text[i]
        if in_string:
            if c == "\\":
                i += 2  # escape sequence — sonraki karakteri atla
                continue
            if c == '"':
                in_string = False
        else:
            if c == '"':
                in_string = True
            elif c == open_char:
                depth += 1
            elif c == close_char:
                depth -= 1
                if depth == 0:
                    return (start, i + 1)
        i += 1
    return None


def extract_json_object(text: str) -> Any:
    """LLM çıktısından JSON verisini çıkarır (dict veya list olabilir).

    Desteklenen formatlar:
    - Saf JSON
    - Markdown code block (```json ... ```)
    - JSON etrafında açıklama metni
    - İç içe (nested) JSON yapıları

    Raises:
        ValueError: Geçerli JSON bulunamazsa.
    """
    cleaned = _clean_markdown_json(text)

    # 1. Direkt parse dene
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 2. İlk tam { } veya [ ] bloğunu brace-counting ile bul
    brace_span = _find_json_span(cleaned, "{")
    bracket_span = _find_json_span(cleaned, "[")

    # Her ikisi de bulunursa daha önce başlayanı seç
    span: tuple[int, int] | None = None
    if brace_span and bracket_span:
        span = brace_span if brace_span[0] <= bracket_span[0] else bracket_span
    elif brace_span:
        span = brace_span
    elif bracket_span:
        span = bracket_span

    if span:
        try:
            return json.loads(cleaned[span[0]: span[1]])
        except json.JSONDecodeError:
            pass

    raise ValueError("LLM çıktısından geçerli JSON ayrıştırılamadı.")


def filter_valid_requirement_ids(
    items: list[dict[str, Any]],
    valid_ids: set[str],
    id_keys: tuple[str, ...] = ("requirement_ids", "req_ids", "ids"),
) -> list[dict[str, Any]]:
    """LLM'in uydurduğu gereksinim ID'lerini içeren kayıtları filtreler.

    Her item için `id_keys` içindeki anahtar kontrol edilir. Bulunan ID listesinin
    en az biri valid_ids içindeyse kayıt tutulur; hiçbiri yoksa atılır.
    ID alanı yoksa kayıt olduğu gibi korunur.

    Args:
        items: Conflict veya gap listesi (her biri dict).
        valid_ids: Belgede gerçekten var olan gereksinim ID'leri.
        id_keys: ID listesini tutabilecek anahtar adları.

    Returns:
        Geçerli ID içeren kayıtlar; sıra korunur.
    """
    if not valid_ids:
        return items

    result: list[dict[str, Any]] = []
    for item in items:
        id_field: list | None = None
        for key in id_keys:
            if key in item:
                id_field = item[key]
                break

        if id_field is None:
            # ID alanı yok → koruyucu taraf olarak tut
            result.append(item)
            continue

        ids = id_field if isinstance(id_field, list) else [id_field]
        if any(str(i) in valid_ids for i in ids):
            result.append(item)

    return result


def sort_by_confidence(
    items: list[dict[str, Any]],
    confidence_key: str = "confidence",
    descending: bool = True,
) -> list[dict[str, Any]]:
    """Kayıtları confidence skoruna göre sıralar.

    Confidence değeri eksik veya dönüştürülemez ise 0.0 kabul edilir.

    Args:
        items: Sıralanacak dict listesi.
        confidence_key: Confidence skorunu tutan anahtar adı.
        descending: True → yüksekten düşüğe (default); False → tersine.

    Returns:
        Sıralanmış yeni liste; orijinal liste değiştirilmez.
    """
    def _score(item: dict) -> float:
        if confidence_key not in item:
            return 1.0
        try:
            return float(item[confidence_key])
        except (TypeError, ValueError):
            return 0.0

    return sorted(items, key=_score, reverse=descending)


__all__ = [
    "extract_json_object",
    "filter_valid_requirement_ids",
    "sort_by_confidence",
]
