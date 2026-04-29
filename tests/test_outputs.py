"""
tests/test_outputs.py — Çıktı Modülü Testleri
Sahibi: Üye 4 (Test koordinasyonu) + Üye 3 (içerik)

Testler mock LLM kullanır; gerçek API çağrısı yapılmaz.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest

from core.models import AnalysisReport, ParsedDocument, Requirement


# ---------------------------------------------------------------------------
# Yardımcı Fabrikalar
# ---------------------------------------------------------------------------


def _make_requirement(
    req_id: str = "REQ_001",
    text: str = "Kullanıcı sisteme giriş yapabilmeli.",
    req_type: str = "FUNCTIONAL",
    actors: Optional[list] = None,
    objects: Optional[list] = None,
    priority: Optional[str] = "MEDIUM",
) -> Requirement:
    return Requirement(
        id=req_id,
        text=text,
        req_type=req_type,
        actors=actors or ["kullanıcı"],
        objects=objects or ["sistem"],
        priority=priority,
    )


def _make_report(requirements: Optional[list] = None) -> AnalysisReport:
    if requirements is None:
        requirements = [_make_requirement()]
    doc = ParsedDocument(
        raw_text="Test metni.",
        requirements=requirements,
        total_sentences=len(requirements),
    )
    return AnalysisReport(parsed_doc=doc)


# ---------------------------------------------------------------------------
# StoryGenerator Testleri
# ---------------------------------------------------------------------------


class TestStoryGenerator:
    """StoryGenerator.generate() için birim testler."""

    def _mock_llm_client(self, story_payload: dict) -> MagicMock:
        """Verilen payload'ı dönen sahte LLMClient üretir."""
        from modules.llm_client import LLMResponse

        mock_client = MagicMock()
        mock_response = LLMResponse(
            content=json.dumps(story_payload),
            raw={"provider": "mock", "usage_metadata": {"input_tokens": 0, "output_tokens": 0}},
        )
        mock_client.chat.return_value = mock_response
        return mock_client

    def test_generate_returns_list_of_dicts(self) -> None:
        """generate() FUNCTIONAL gereksinim için role/goal/benefit/ac içeren dict döndürmeli."""
        from outputs.story_generator import StoryGenerator

        payload = {
            "role": "kullanıcı",
            "goal": "sisteme giriş yapabilmek",
            "benefit": "kişisel hesabıma erişebilmek",
            "acceptance_criteria": ["Giriş formu hatasız çalışmalı."],
        }
        mock_client = self._mock_llm_client(payload)
        report = _make_report()

        generator = StoryGenerator(llm_client=mock_client)
        stories = generator.generate(report)

        assert isinstance(stories, list)
        assert len(stories) == 1
        story = stories[0]
        assert story["req_id"] == "REQ_001"
        assert story["role"] == "kullanıcı"
        assert story["goal"] == "sisteme giriş yapabilmek"
        assert story["benefit"] == "kişisel hesabıma erişebilmek"
        assert isinstance(story["acceptance_criteria"], list)
        assert len(story["acceptance_criteria"]) >= 1

    def test_generate_skips_nfr_requirements(self) -> None:
        """generate() NON_FUNCTIONAL gereksinimleri atlamalı."""
        from outputs.story_generator import StoryGenerator

        nfr_req = _make_requirement(
            req_id="REQ_001",
            text="Sistem 200ms altında yanıt vermeli.",
            req_type="NON_FUNCTIONAL",
        )
        report = _make_report(requirements=[nfr_req])

        # LLM client'ın çağrılmaması bekleniyor
        mock_client = MagicMock()
        generator = StoryGenerator(llm_client=mock_client)
        stories = generator.generate(report)

        assert stories == []
        mock_client.chat.assert_not_called()

    def test_generate_empty_report_returns_empty(self) -> None:
        """Boş ParsedDocument verildiğinde generate() boş liste döndürmeli."""
        from outputs.story_generator import StoryGenerator

        doc = ParsedDocument(raw_text="", requirements=[], total_sentences=0)
        report = AnalysisReport(parsed_doc=doc)

        mock_client = MagicMock()
        generator = StoryGenerator(llm_client=mock_client)
        stories = generator.generate(report)

        assert stories == []
        mock_client.chat.assert_not_called()

    def test_generate_uses_fallback_on_llm_error(self) -> None:
        """LLM hatası durumunda fallback dict dönmeli; exception fırlatılmamalı."""
        from modules.llm_client import LLMClientError
        from outputs.story_generator import StoryGenerator

        mock_client = MagicMock()
        mock_client.chat.side_effect = LLMClientError("API hatası")

        report = _make_report()
        generator = StoryGenerator(llm_client=mock_client)
        stories = generator.generate(report)

        # Fallback ile en az 1 story dönmeli
        assert len(stories) == 1
        assert stories[0]["req_id"] == "REQ_001"
        # Fallback işareti
        assert "(LLM analizi mevcut değil)" in stories[0]["benefit"]


# ---------------------------------------------------------------------------
# SRSGenerator Testleri
# ---------------------------------------------------------------------------


class TestSRSGenerator:
    """generate_srs() için birim testler."""

    def test_generate_srs_creates_pdf_file(self, tmp_path: Path) -> None:
        """generate_srs() verilen yolda .pdf dosyası oluşturmalı."""
        from outputs.srs_generator import generate_srs

        report = _make_report()
        output_path = tmp_path / "test_srs.pdf"

        result_path = generate_srs(report=report, output_path=output_path)

        assert result_path.exists(), "PDF dosyası oluşturulmalıydı."
        assert result_path.suffix == ".pdf"
        assert result_path.stat().st_size > 0, "PDF dosyası boş olmamalı."

    def test_generate_srs_returns_path_object(self, tmp_path: Path) -> None:
        """generate_srs() Path nesnesi döndürmeli."""
        from outputs.srs_generator import generate_srs

        report = _make_report()
        output_path = tmp_path / "test_srs_path.pdf"
        result = generate_srs(report=report, output_path=output_path)

        assert isinstance(result, Path)

    def test_generate_srs_static_demo_without_report(self, tmp_path: Path) -> None:
        """report=None ile çağrıldığında statik demo PDF üretilmeli."""
        from outputs.srs_generator import generate_srs

        output_path = tmp_path / "demo_srs.pdf"
        result_path = generate_srs(report=None, output_path=output_path)

        assert result_path.exists()
        assert result_path.stat().st_size > 0

    def test_generate_srs_auto_creates_generated_dir(self, tmp_path: Path, monkeypatch) -> None:
        """output_path belirtilmezse outputs/generated/ klasörü otomatik oluşturulmalı."""
        from outputs import srs_generator as sg_module

        # __file__'ı tmp_path'e yönlendir ki generated/ orada oluşsun
        fake_srs_path = tmp_path / "fake_srs_generator.py"
        fake_srs_path.touch()

        # Path(__file__).parent'ı tmp_path'e çevir
        monkeypatch.setattr(sg_module, "__file__", str(fake_srs_path))

        report = _make_report()
        result_path = sg_module.generate_srs(report=report, output_path=None)

        # generated klasörünün oluştuğunu doğrula
        generated_dir = tmp_path / "generated"
        assert generated_dir.exists()
        assert result_path.parent == generated_dir


# ---------------------------------------------------------------------------
# BDDGenerator Stub Testi (ileride doldurulacak)
# ---------------------------------------------------------------------------


class TestBDDGenerator:
    def test_gherkin_format(self) -> None:
        """BDDGenerator.generate() NotImplementedError fırlatmalı (henüz stub)."""
        from outputs.bdd_generator import BDDGenerator

        report = _make_report()
        generator = BDDGenerator()

        with pytest.raises(NotImplementedError):
            generator.generate(report)
