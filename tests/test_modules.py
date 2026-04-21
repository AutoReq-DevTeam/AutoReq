"""
tests/test_modules.py — Akıllı Modül Testleri
Sahibi: Üye 4 (Test koordinasyonu) + Üye 2 (içerik)
"""

from __future__ import annotations

from unittest.mock import MagicMock

from core.models import ParsedDocument, Requirement
from modules.gap_analyzer import GapAnalyzer
from modules.llm_client import LLMResponse


class TestConflictDetector:
    def test_detects_contradiction(self):
        # TODO: Üye 4 — Zıt ifadeler içeren bir belgede çelişki tespit edilmeli
        pass


class TestGapAnalyzer:
    def test_detects_missing_password_reset(self) -> None:
        """Mock LLM: giriş var, parola sıfırlama eksik — normalize gap satırları üretilmeli."""
        payload_json = """
        {
          "gaps": [
            {
              "id": "G1",
              "scenario": "authentication",
              "missing_area": "Parola sıfırlama akışı",
              "related_standard_step": "Parola sıfırlama",
              "suggestion": "Kullanıcı parolasını unuttuğunda e-posta ile sıfırlama bağlantısı alabilmelidir.",
              "severity": "high",
              "rationale": "Yalnızca giriş tanımlı; hesap kurtarma yok."
            }
          ],
          "meta": { "inferred_context": "test", "confidence": "high", "total_gaps": 1 }
        }
        """
        mock_client = MagicMock()
        mock_client.chat.return_value = LLMResponse(content=payload_json, raw={})

        doc = ParsedDocument(
            raw_text="Kullanıcı giriş yapabilmeli.",
            requirements=[
                Requirement(
                    id="REQ_001",
                    text="Kullanıcı giriş yapabilmeli.",
                    req_type="FUNCTIONAL",
                )
            ],
            total_sentences=1,
        )

        analyzer = GapAnalyzer(llm_client=mock_client)
        result = analyzer.analyze(doc)

        assert len(result) >= 1
        first = result[0]
        assert first["missing_area"]
        assert first["suggestion"]
        assert first["severity"] in ("high", "medium", "low")
        mock_client.chat.assert_called_once()

    def test_fallback_when_llm_returns_empty_gaps_for_login_only(self) -> None:
        """LLM boş gaps döndürdüğünde tek giriş gereksiniminde minimum hesap kurtarma gap'i eklenmeli."""
        mock_client = MagicMock()
        mock_client.chat.return_value = LLMResponse(
            content='{"gaps": [], "meta": {"confidence": "high", "total_gaps": 0}}',
            raw={},
        )

        doc = ParsedDocument(
            raw_text="",
            requirements=[
                Requirement(
                    id="REQ_001",
                    text="Kullanıcı giriş yapabilmeli.",
                    req_type="FUNCTIONAL",
                )
            ],
            total_sentences=1,
        )

        analyzer = GapAnalyzer(llm_client=mock_client)
        result = analyzer.analyze(doc)

        assert len(result) >= 1
        assert "parola" in result[0]["missing_area"].lower() or "hesap" in result[0]["missing_area"].lower()
        assert result[0]["severity"] == "high"

    def test_empty_requirements_returns_empty_without_llm(self) -> None:
        mock_client = MagicMock()
        doc = ParsedDocument(raw_text="", requirements=[], total_sentences=0)
        analyzer = GapAnalyzer(llm_client=mock_client)
        assert analyzer.analyze(doc) == []
        mock_client.chat.assert_not_called()


class TestRequirementImprover:
    def test_improves_vague_requirement(self):
        # TODO: Üye 4 — "Hızlı olmalı" ifadesi ölçülebilir öneriye dönüşmeli
        pass
