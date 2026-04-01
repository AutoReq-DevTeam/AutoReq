"""
modules/analysis_report_parsing.py — LLM JSON çıktılarını AnalysisReport sözleşmesine dönüştürme

AnalysisReport.conflicts: her dict en az
  req_ids, conflict_type, reason (+ isteğe bağlı id, severity, suggested_resolution)

AnalysisReport.gaps: her dict en az
  missing_area, suggestion, severity (+ isteğe bağlı id, scenario, related_standard_step, rationale, meta)
"""

from __future__ import annotations

from typing import Any, Optional

from core.models import AnalysisReport, ParsedDocument

from .llm_response_utils import extract_json_object


def conflicts_payload_to_report_dicts(data: dict[str, Any]) -> list[dict]:
    """
    Çelişki LLM şemasındaki 'conflicts' listesini AnalysisReport.conflicts öğelerine çevirir.
    """
    rows: list[dict] = []
    for c in data.get("conflicts") or []:
        if not isinstance(c, dict):
            continue
        req_ids = c.get("requirements") or []
        if not isinstance(req_ids, list):
            req_ids = [str(req_ids)]
        ctype = str(c.get("type") or "other")
        summary = (c.get("short_summary") or "").strip()
        detail = (c.get("detailed_explanation") or "").strip()
        if summary and detail:
            reason = f"{summary}\n\n{detail}"
        else:
            reason = summary or detail or "(Açıklama yok.)"

        row: dict[str, Any] = {
            "req_ids": req_ids,
            "conflict_type": ctype,
            "reason": reason,
        }
        if c.get("id"):
            row["id"] = c["id"]
        if c.get("severity"):
            row["severity"] = c["severity"]
        if c.get("suggested_resolution"):
            row["suggested_resolution"] = c["suggested_resolution"]
        rows.append(row)
    return rows


def gaps_payload_to_report_dicts(data: dict[str, Any]) -> list[dict]:
    """
    Gap LLM şemasındaki 'gaps' listesini AnalysisReport.gaps öğelerine çevirir.
    """
    rows: list[dict] = []
    for g in data.get("gaps") or []:
        if not isinstance(g, dict):
            continue
        missing = str(g.get("missing_area") or "").strip() or "(tanımsız alan)"
        suggestion = str(g.get("suggestion") or "").strip()
        sev = str(g.get("severity") or "medium").lower()
        if sev not in {"high", "medium", "low"}:
            sev = "medium"

        row: dict[str, Any] = {
            "missing_area": missing,
            "suggestion": suggestion,
            "severity": sev,
        }
        if g.get("id"):
            row["id"] = g["id"]
        if g.get("scenario"):
            row["scenario"] = g["scenario"]
        if g.get("related_standard_step"):
            row["related_standard_step"] = g["related_standard_step"]
        if g.get("rationale"):
            row["rationale"] = g["rationale"]
        rows.append(row)
    return rows


def parse_conflicts_llm_text(llm_text: str) -> list[dict]:
    """Ham LLM metnini JSON'a çevirip conflicts listesine dönüştürür."""
    payload = extract_json_object(llm_text)
    return conflicts_payload_to_report_dicts(payload)


def parse_gaps_llm_text(llm_text: str) -> list[dict]:
    """Ham LLM metnini JSON'a çevirip gaps listesine dönüştürür."""
    payload = extract_json_object(llm_text)
    return gaps_payload_to_report_dicts(payload)


def build_analysis_report_from_llm(
    parsed_doc: ParsedDocument,
    *,
    conflicts_llm_text: Optional[str] = None,
    gaps_llm_text: Optional[str] = None,
    conflicts_payload: Optional[dict[str, Any]] = None,
    gaps_payload: Optional[dict[str, Any]] = None,
) -> AnalysisReport:
    """
    LLM yanıtlarını ayrıştırır ve AnalysisReport nesnesini doldurur.

    Öncelik: açıkça verilen payload sözlükleri, yoksa ham metin (parse edilir).
    Metin veya payload yoksa ilgili liste boş kalır.
    """
    conflicts: list[dict] = []
    if conflicts_payload is not None:
        conflicts = conflicts_payload_to_report_dicts(conflicts_payload)
    elif conflicts_llm_text and conflicts_llm_text.strip():
        conflicts = parse_conflicts_llm_text(conflicts_llm_text)

    gaps: list[dict] = []
    if gaps_payload is not None:
        gaps = gaps_payload_to_report_dicts(gaps_payload)
    elif gaps_llm_text and gaps_llm_text.strip():
        gaps = parse_gaps_llm_text(gaps_llm_text)

    return AnalysisReport(parsed_doc=parsed_doc, conflicts=conflicts, gaps=gaps)


__all__ = [
    "conflicts_payload_to_report_dicts",
    "gaps_payload_to_report_dicts",
    "parse_conflicts_llm_text",
    "parse_gaps_llm_text",
    "build_analysis_report_from_llm",
]
