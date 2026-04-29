"""
tests/test_modules.py — Akıllı Modül Testleri
Sahibi: Üye 4 (Test koordinasyonu) + Üye 2 (içerik)
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from core.models import ParsedDocument, Requirement
from modules.gap_analyzer import GapAnalyzer
from modules.improver import RequirementImprover
from modules.llm_cache import LLMPromptCache
from modules.llm_client import LLMClient, LLMResponse


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


class TestLLMClient:
    def test_cache_hit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Aynı prompt ile ikinci chat çağrısı API'ye gitmeden önbellekten dönmeli."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-cache-key")

        mock_response = MagicMock()
        mock_response.text = '{"cached": false}'
        mock_um = MagicMock()
        mock_um.prompt_token_count = 100
        mock_um.candidates_token_count = 50
        mock_response.usage_metadata = mock_um

        with patch("google.generativeai.configure"):
            with patch("google.generativeai.GenerativeModel") as mock_gen:
                send = mock_gen.return_value.start_chat.return_value.send_message
                send.return_value = mock_response

                isolated = LLMPromptCache(default_ttl_seconds=3600)
                client = LLMClient(prompt_cache=isolated)

                first = client.chat("system prompt", "user prompt")
                second = client.chat("system prompt", "user prompt")

                assert send.call_count == 1
                assert first.content == second.content
                assert first.raw["usage_metadata"]["input_tokens"] == 100
                assert first.raw["usage_metadata"]["output_tokens"] == 50
                assert "estimated_cost_usd" in first.raw["usage_metadata"]
                assert second.raw["usage_metadata"].get("cache_hit") is True
                assert second.raw["usage_metadata"]["input_tokens"] == 0
                assert "usage" in first.raw and "usage" in second.raw


class TestRequirementImprover:
    def test_improves_vague_requirement(self) -> None:
        """Mock LLM: muğlak hız ifadesi sayısal eşik içeren metne dönüşmeli."""
        llm_json = """
        {
          "improved": "Sistem, 1000 eşzamanlı kullanıcı yükünde p95 yanıt süresi 500 ms altında olmalıdır.",
          "reason": "Hız beklentisi, eşzamanlı kullanıcı ve p95 gecikme eşiği ile ölçülebilir hale getirildi."
        }
        """
        mock_client = MagicMock()
        mock_client.chat.return_value = LLMResponse(content=llm_json, raw={})

        req = Requirement(
            id="REQ_001",
            text="Sistem hızlı olmalı",
            req_type="FUNCTIONAL",
        )
        improver = RequirementImprover(llm_client=mock_client)
        result = improver.improve(req)

        assert result["original"] == "Sistem hızlı olmalı"
        assert "500" in result["improved"] or "ms" in result["improved"].lower()
        assert result["reason"]
        assert set(result.keys()) == {"improved", "original", "reason"}
        mock_client.chat.assert_called_once()

    def test_skips_llm_when_no_vague_keyword(self) -> None:
        """Metinde muğlak anahtar kelime yoksa LLM çağrılmamalı, original==improved olmalı."""
        mock_client = MagicMock()
        req = Requirement(
            id="REQ_001",
            text="Kullanıcı e-posta adresiyle giriş yapabilmelidir.",
            req_type="FUNCTIONAL",
        )
        improver = RequirementImprover(llm_client=mock_client)
        result = improver.improve(req)

        assert result["original"] == result["improved"]
        assert "token" in result["reason"].lower() or "atlandı" in result["reason"].lower()
        mock_client.chat.assert_not_called()
