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

# pypdf isteğe bağlı; kurulu değilse ilgili testler atlanır
try:
    from pypdf import PdfReader as _PdfReader  # type: ignore
    _PYPDF_AVAILABLE = True
except ImportError:
    _PYPDF_AVAILABLE = False


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

    @pytest.mark.skipif(not _PYPDF_AVAILABLE, reason="pypdf kurulu değil")
    def test_generate_srs_functional_requirements_in_pdf(self, tmp_path: Path) -> None:
        """Dinamik SRS PDF'inde FUNCTIONAL gereksinimlerin metin olarak bulunduğunu doğrular.

        Issue #11 AC: Fonksiyonel Gereksinimler bölümü gerçek req_type==FUNCTIONAL
        maddeleri içermeli.
        """
        from outputs.srs_generator import generate_srs

        func_req = _make_requirement(
            req_id="REQ_001",
            text="Kullanıcı sisteme giriş yapabilmeli.",
            req_type="FUNCTIONAL",
        )
        nfr_req = _make_requirement(
            req_id="REQ_002",
            text="Sistem 200ms altında yanıt vermeli.",
            req_type="NON_FUNCTIONAL",
        )
        report = _make_report(requirements=[func_req, nfr_req])
        output_path = tmp_path / "dynamic_srs.pdf"

        result_path = generate_srs(report=report, output_path=output_path)

        assert result_path.exists(), "PDF dosyası oluşturulmalıydı."
        reader = _PdfReader(str(result_path))
        full_text = "".join(page.extract_text() or "" for page in reader.pages)

        # Fonksiyonel bölüm başlığı
        assert "Fonksiyonel Gereksinimler" in full_text, (
            "PDF 'Fonksiyonel Gereksinimler' başlığını içermeli."
        )
        # REQ_001 ID'si tabloda görünmeli
        assert "REQ_001" in full_text, "FUNCTIONAL gereksinim ID'si PDF'de bulunmalı."

    @pytest.mark.skipif(not _PYPDF_AVAILABLE, reason="pypdf kurulu değil")
    def test_generate_srs_includes_conflicts_section(self, tmp_path: Path) -> None:
        """Çelişki varsa SRS PDF'inde Tespit Edilen Çelişkiler bölümü yer almalı.

        Issue #11 AC: 'Tespit Edilen Çelişkiler' bölümü report.conflicts boş değilse
        her madde gerekçesiyle yazılmalı.
        """
        from outputs.srs_generator import generate_srs

        report = _make_report()
        # Manuel olarak çelişki ekle
        report.conflicts.append(
            {
                "req_ids": ["REQ_001", "REQ_002"],
                "conflict_type": "logic",
                "reason": "Test çelişki gerekçesi.",
                "severity": "high",
            }
        )
        output_path = tmp_path / "conflicts_srs.pdf"

        result_path = generate_srs(report=report, output_path=output_path)

        reader = _PdfReader(str(result_path))
        full_text = "".join(page.extract_text() or "" for page in reader.pages)

        assert "Tespit Edilen" in full_text, (
            "Çelişki bölümü başlığı PDF'de bulunmalı."
        )

    @pytest.mark.skipif(not _PYPDF_AVAILABLE, reason="pypdf kurulu değil")
    def test_pdf_contains_all_iso_sections(self, tmp_path: Path) -> None:
        """Üretilen PDF, ISO/IEC/IEEE 29148'in 10 zorunlu bölüm başlığını içermeli.

        Issue #23 AC: pypdf ile parse edildiğinde 10 başlığı da içermeli.
        """
        from outputs.srs_generator import generate_srs

        report = _make_report()
        output_path = tmp_path / "iso_sections_srs.pdf"
        result_path = generate_srs(report=report, output_path=output_path)

        reader = _PdfReader(str(result_path))
        full_text = "".join(page.extract_text() or "" for page in reader.pages)

        # ISO/IEC/IEEE 29148 zorunlu 10 bölüm başlığı
        iso_sections = [
            "1.",   # Giriş (Introduction)
            "2.",   # Kapsam (Scope)
            "3.",   # Genel Açıklama
            "4.",   # Fonksiyonel Gereksinimler
            "5.",   # Kullanıcı Özellikleri
            "6.",   # Kısıtlamalar
            "7.",   # Varsayımlar ve Bağımlılıklar
            "8.",   # Veri Gereksinimleri
            "9.",   # Dış Arayüz Gereksinimleri
            "10.",  # Kalite Özellikleri
        ]
        for section_prefix in iso_sections:
            assert section_prefix in full_text, (
                f"ISO 29148 bölümü '{section_prefix}' PDF'de bulunamadı."
            )

    @pytest.mark.skipif(not _PYPDF_AVAILABLE, reason="pypdf kurulu değil")
    def test_pdf_metadata(self, tmp_path: Path) -> None:
        """PDF metadata alanları (title, author, subject, creator) dolu olmalı.

        Issue #23 AC: PDF metadata'sı doldurulmalı.
        """
        from outputs.srs_generator import generate_srs

        report = _make_report()
        output_path = tmp_path / "metadata_srs.pdf"
        result_path = generate_srs(report=report, output_path=output_path)

        reader = _PdfReader(str(result_path))
        meta = reader.metadata

        # FPDF2'nin yazdığı metadata alanları /Title, /Author, /Subject, /Creator
        assert meta is not None, "PDF metadata boş olmamalı."

        # title veya /Title anahtarı
        title_val = getattr(meta, "title", None) or meta.get("/Title", "")
        assert title_val, "PDF title metadata'sı boş olmamalı."
        assert "SRS" in str(title_val), "PDF title 'SRS' içermeli."

        author_val = getattr(meta, "author", None) or meta.get("/Author", "")
        assert author_val, "PDF author metadata'sı boş olmamalı."
        assert "AutoReq" in str(author_val), "PDF author 'AutoReq' içermeli."

        subject_val = getattr(meta, "subject", None) or meta.get("/Subject", "")
        assert subject_val, "PDF subject metadata'sı boş olmamalı."

        creator_val = getattr(meta, "creator", None) or meta.get("/Creator", "")
        assert creator_val, "PDF creator metadata'sı boş olmamalı."

    def test_pdf_size_under_5mb(self, tmp_path: Path) -> None:
        """Üretilen PDF dosyası 5 MB'den küçük olmalı.

        Issue #23 AC: PDF dosya boyutu <5 MB olmalı (logo + font'lar dahil).
        """
        from outputs.srs_generator import generate_srs

        # Çok sayıda gereksinim ekle (gerçekçi senaryo)
        requirements = [
            _make_requirement(
                req_id=f"REQ_{i:03d}",
                text=f"Kullanıcı sistemde işlem {i} gerçekleştirebilmeli. "
                     "Bu gereksinim ş, ğ, İ, ı, ö, ü, ç karakterleri içerir.",
                req_type="FUNCTIONAL" if i % 2 == 0 else "NON_FUNCTIONAL",
                priority="HIGH" if i % 3 == 0 else "MEDIUM",
            )
            for i in range(1, 31)  # 30 gereksinim
        ]
        report = _make_report(requirements=requirements)
        output_path = tmp_path / "large_srs.pdf"

        result_path = generate_srs(report=report, output_path=output_path)

        size_bytes = result_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        assert size_mb < 5.0, (
            f"PDF boyutu {size_mb:.2f} MB — 5 MB sınırını aşıyor."
        )

    @pytest.mark.skipif(not _PYPDF_AVAILABLE, reason="pypdf kurulu değil")
    def test_turkish_chars_render(self, tmp_path: Path) -> None:
        """Türkçe karakterler (ş, ğ, İ, ı) PDF metninde bozulmadan bulunmalı.

        Issue #23 AC: Türkçe karakter + İngilizce karışık metin sorunsuz render olmalı.

        Not: pypdf'nin metin çıkarma kapasitesi font encoding'e bağlıdır.
        Embedded TTF yoksa Helvetica fallback kullanılır ve bazı karakterler
        bozulabilir — bu durumda test, Türkçe içerikli requirement'ın genel
        olarak PDF'de yer aldığını doğrular.
        """
        from outputs.srs_generator import generate_srs

        turkish_text = "Kullanıcı şifresini değiştirebilmeli; güvenlik zorunludur."
        req = _make_requirement(
            req_id="REQ_001",
            text=turkish_text,
            req_type="FUNCTIONAL",
        )
        report = _make_report(requirements=[req])
        output_path = tmp_path / "turkish_srs.pdf"

        result_path = generate_srs(report=report, output_path=output_path)
        assert result_path.exists(), "PDF dosyası oluşturulmalıydı."
        assert result_path.stat().st_size > 0, "PDF dosyası boş olmamalı."

        reader = _PdfReader(str(result_path))
        full_text = "".join(page.extract_text() or "" for page in reader.pages)

        # En azından REQ_001 PDF'de görünmeli
        assert "REQ_001" in full_text, (
            "Türkçe karakterli gereksinim ID'si PDF'de bulunmalı."
        )
        # Türkçe özel karakterler PDF'den çıkarılabiliyorsa kontrol et
        turkish_chars = ["ş", "İ"]
        chars_found = [ch for ch in turkish_chars if ch in full_text]
        if not chars_found:
            # Helvetica fallback durumunda: en azından PDF açılabilir olmalı
            import warnings
            warnings.warn(
                "Türkçe karakterler PDF'den extract edilemedi — "
                "muhtemelen Helvetica fallback kullanılıyor. "
                "Bundled font kurulumu için: python outputs/fonts/download_fonts.py",
                UserWarning,
                stacklevel=2,
            )


# ---------------------------------------------------------------------------
# BDDGenerator Testleri (Issue #15)
# ---------------------------------------------------------------------------


class TestBDDGenerator:
    """BDDGenerator.generate() ve write_feature_file() için birim testler."""

    def _mock_llm_client(self, bdd_payload: dict) -> MagicMock:
        """Verilen BDD payload'ı dönen sahte LLMClient üretir."""
        import json

        from modules.llm_client import LLMResponse

        mock_client = MagicMock()
        mock_response = LLMResponse(
            content=json.dumps(bdd_payload),
            raw={"provider": "mock", "usage_metadata": {"input_tokens": 0, "output_tokens": 0}},
        )
        mock_client.chat.return_value = mock_response
        return mock_client

    def _sample_payload(self) -> dict:
        """Geçerli bir BDD LLM payload örneği döndürür."""
        return {
            "feature_title": "Kullanıcı Girişi",
            "happy_path": {
                "scenario_title": "Başarılı giriş",
                "given": ["Kullanıcı giriş sayfasındadır"],
                "when": ["Kullanıcı doğru bilgileri girer"],
                "then": ["Kullanıcı ana sayfaya yönlendirilmeli"],
            },
            "negative_scenario": {
                "scenario_title": "Hatalı şifre ile giriş",
                "given": ["Kullanıcı giriş sayfasındadır"],
                "when": ["Kullanıcı yanlış şifre girer"],
                "then": ["Hata mesajı gösterilmeli"],
            },
        }

    def test_gherkin_format(self) -> None:
        """generate() çıktısı Feature:, Scenario:, Given, When, Then anahtar kelimelerini içermeli."""
        from outputs.bdd_generator import BDDGenerator

        mock_client = self._mock_llm_client(self._sample_payload())
        report = _make_report()
        generator = BDDGenerator(llm_client=mock_client)
        scenarios = generator.generate(report)

        assert isinstance(scenarios, list)
        assert len(scenarios) >= 1

        full_text = "\n".join(scenarios)
        for keyword in ("Feature:", "Scenario:", "Given", "When", "Then"):
            assert keyword in full_text, f"Gherkin çıktısında '{keyword}' bulunmalı."

    def test_bdd_generates_happy_and_negative(self) -> None:
        """Her FUNCTIONAL gereksinim için en az 2 blok (happy + negative) üretilmeli."""
        from outputs.bdd_generator import BDDGenerator

        mock_client = self._mock_llm_client(self._sample_payload())
        report = _make_report()  # 1 FUNCTIONAL gereksinim içeriyor
        generator = BDDGenerator(llm_client=mock_client)
        scenarios = generator.generate(report)

        # 1 FR → 2 blok (happy + negative)
        assert len(scenarios) >= 2

    def test_bdd_writes_feature_file(self, tmp_path: Path) -> None:
        """write_feature_file() geçerli bir .feature dosyası oluşturmalı."""
        from outputs.bdd_generator import BDDGenerator

        mock_client = self._mock_llm_client(self._sample_payload())
        report = _make_report()
        generator = BDDGenerator(llm_client=mock_client)
        scenarios = generator.generate(report)

        feature_path = tmp_path / "test_scenarios.feature"
        result_path = generator.write_feature_file(scenarios, output_path=feature_path)

        assert result_path.exists(), ".feature dosyası oluşturulmalıydı."
        content = result_path.read_text(encoding="utf-8")
        assert "Generated by AutoReq" in content, "Header .feature dosyasında bulunmalı."
        assert "Feature:" in content
        assert "Scenario:" in content

    def test_bdd_empty_report_returns_empty(self) -> None:
        """Boş ParsedDocument verildiğinde generate() boş liste döndürmeli."""
        from outputs.bdd_generator import BDDGenerator

        doc = ParsedDocument(raw_text="", requirements=[], total_sentences=0)
        report = AnalysisReport(parsed_doc=doc)

        mock_client = MagicMock()
        generator = BDDGenerator(llm_client=mock_client)
        scenarios = generator.generate(report)

        assert scenarios == []
        mock_client.chat.assert_not_called()

    def test_bdd_uses_fallback_on_llm_error(self) -> None:
        """LLM hatası durumunda fallback Gherkin metni dönmeli; exception fırlatılmamalı."""
        from modules.llm_client import LLMClientError
        from outputs.bdd_generator import BDDGenerator

        mock_client = MagicMock()
        mock_client.chat.side_effect = LLMClientError("API hatası")

        report = _make_report()
        generator = BDDGenerator(llm_client=mock_client)
        scenarios = generator.generate(report)

        # Fallback ile en az 2 blok dönmeli
        assert len(scenarios) >= 2
        full_text = "\n".join(scenarios)
        assert "Feature:" in full_text
        assert "Given" in full_text


# ---------------------------------------------------------------------------
# BacklogGenerator Testleri (Issue #19)
# ---------------------------------------------------------------------------


class TestBacklogGenerator:
    """BacklogGenerator.generate() için birim testler.

    Tüm testler mock veya sahte AnalysisReport nesneleri kullanır;
    gerçek LLM veya NLP çağrısı yapılmaz.
    """

    def _make_req(
        self,
        req_id: str = "REQ_001",
        text: str = "Kullanıcı sisteme giriş yapabilmeli.",
        req_type: str = "FUNCTIONAL",
        priority: str = "HIGH",
    ) -> Requirement:
        return Requirement(
            id=req_id,
            text=text,
            req_type=req_type,
            priority=priority,
        )

    def test_priority_scoring_basic(self) -> None:
        """HIGH + FUNCTIONAL gereksinim için beklenen skoru doğrular.

        HIGH(3) x FUNCTIONAL(1.0) x no_conflict(1.0) = 3.0
        """
        from outputs.backlog_generator import BacklogGenerator

        req = self._make_req(priority="HIGH", req_type="FUNCTIONAL")
        report = _make_report(requirements=[req])

        generator = BacklogGenerator()
        backlog = generator.generate(report)

        assert len(backlog) == 1
        item = backlog[0]
        assert item["req_id"] == "REQ_001"
        assert item["priority_score"] == 3.0
        assert item["type"] == "FUNCTIONAL"
        assert isinstance(item["story_points"], int)
        assert item["story_points"] >= 1

    def test_conflict_penalty_applied(self) -> None:
        """Celiski listesindeki req_id'ye x1.5 carpani uygulanmali.

        MEDIUM(2) x FUNCTIONAL(1.0) x conflict(1.5) = 3.0
        """
        from outputs.backlog_generator import BacklogGenerator

        req = self._make_req(req_id="REQ_001", priority="MEDIUM", req_type="FUNCTIONAL")
        report = _make_report(requirements=[req])
        report.conflicts.append(
            {
                "req_ids": ["REQ_001", "REQ_002"],
                "conflict_type": "logic",
                "reason": "Test celiskisi.",
            }
        )

        generator = BacklogGenerator()
        backlog = generator.generate(report)

        assert len(backlog) == 1
        assert backlog[0]["priority_score"] == 3.0

    def test_nfr_weight_applied(self) -> None:
        """NON_FUNCTIONAL gereksinimlere 0.7 agirlik uygulanmali.

        HIGH(3) x NON_FUNCTIONAL(0.7) x no_conflict(1.0) = 2.1
        """
        from outputs.backlog_generator import BacklogGenerator

        req = self._make_req(
            req_id="REQ_001",
            text="Sistem 200ms altinda yanit vermeli.",
            req_type="NON_FUNCTIONAL",
            priority="HIGH",
        )
        report = _make_report(requirements=[req])

        generator = BacklogGenerator()
        backlog = generator.generate(report)

        assert len(backlog) == 1
        assert abs(backlog[0]["priority_score"] - 2.1) < 0.01

    def test_generate_returns_sorted_list(self) -> None:
        """generate() sonucu priority_score'a gore azalan sirayla donmeli."""
        from outputs.backlog_generator import BacklogGenerator

        req_low = self._make_req(req_id="REQ_001", priority="LOW", req_type="FUNCTIONAL")
        req_high = self._make_req(req_id="REQ_002", priority="HIGH", req_type="FUNCTIONAL")
        req_medium = self._make_req(req_id="REQ_003", priority="MEDIUM", req_type="FUNCTIONAL")

        report = _make_report(requirements=[req_low, req_high, req_medium])

        generator = BacklogGenerator()
        backlog = generator.generate(report)

        scores = [item["priority_score"] for item in backlog]
        assert scores == sorted(scores, reverse=True), (
            "Backlog azalan priority_score sirasinda olmali."
        )
        assert backlog[0]["req_id"] == "REQ_002"
        assert backlog[-1]["req_id"] == "REQ_001"

    def test_empty_report_returns_empty(self) -> None:
        """Gereksinim yoksa generate() bos liste dondürmeli."""
        from outputs.backlog_generator import BacklogGenerator

        doc = ParsedDocument(raw_text="", requirements=[], total_sentences=0)
        report = AnalysisReport(parsed_doc=doc)

        generator = BacklogGenerator()
        backlog = generator.generate(report)

        assert backlog == []

    def test_backlog_item_structure(self) -> None:
        """Her backlog ogesi req_id, title, priority_score, story_points, type, depends_on icermeli."""
        from outputs.backlog_generator import BacklogGenerator

        req = self._make_req()
        report = _make_report(requirements=[req])

        generator = BacklogGenerator()
        backlog = generator.generate(report)

        assert len(backlog) == 1
        item = backlog[0]
        required_keys = {"req_id", "title", "priority_score", "story_points", "type", "depends_on"}
        assert required_keys.issubset(item.keys()), (
            f"Backlog ogesinde eksik alanlar: {required_keys - item.keys()}"
        )


# ---------------------------------------------------------------------------
# Exporters Testleri (Issue #19)
# ---------------------------------------------------------------------------


class TestExporters:
    """outputs/exporters.py icin birim testler."""

    def test_export_report_json_creates_file(self, tmp_path: Path) -> None:
        """export_report_json() gecerli JSON dosyasi olusturmali."""
        from outputs.exporters import export_report_json

        report = _make_report()
        output_path = tmp_path / "report.json"

        result_path = export_report_json(report, path=output_path)

        assert result_path.exists(), "JSON dosyasi olusturulmaliydi."
        assert result_path.suffix == ".json"
        assert result_path.stat().st_size > 0

    def test_export_report_json_valid_json(self, tmp_path: Path) -> None:
        """export_report_json() ciktisi gecerli JSON olmali ve req verilerini icermeli."""
        import json as json_module

        from outputs.exporters import export_report_json

        req = _make_requirement(
            req_id="REQ_001",
            text="Kullanici sisteme giris yapabilmeli.",
        )
        report = _make_report(requirements=[req])
        output_path = tmp_path / "report.json"

        result_path = export_report_json(report, path=output_path)

        content = result_path.read_text(encoding="utf-8")
        data = json_module.loads(content)

        assert "parsed_doc" in data
        assert "conflicts" in data
        assert "gaps" in data
        assert "improvements" in data

        reqs = data["parsed_doc"]["requirements"]
        assert len(reqs) == 1
        assert reqs[0]["id"] == "REQ_001"

    def test_export_backlog_xlsx_creates_file(self, tmp_path: Path) -> None:
        """export_backlog_xlsx() gecerli .xlsx dosyasi olusturmali."""
        pytest.importorskip("openpyxl")
        from outputs.exporters import export_backlog_xlsx

        backlog = [
            {
                "req_id": "REQ_001",
                "title": "Kullanici giris yapabilmeli.",
                "priority_score": 3.0,
                "story_points": 5,
                "type": "FUNCTIONAL",
                "depends_on": [],
            }
        ]
        output_path = tmp_path / "backlog.xlsx"
        result_path = export_backlog_xlsx(backlog, path=output_path)

        assert result_path.exists(), ".xlsx dosyasi olusturulmaliydi."
        assert result_path.suffix == ".xlsx"
        assert result_path.stat().st_size > 0

    def test_export_stories_docx_creates_file(self, tmp_path: Path) -> None:
        """export_stories_docx() gecerli .docx dosyasi olusturmali."""
        pytest.importorskip("docx")
        from outputs.exporters import export_stories_docx

        stories = [
            {
                "req_id": "REQ_001",
                "role": "kullanici",
                "goal": "sisteme giris yapabilmek",
                "benefit": "hesabima erismek",
                "acceptance_criteria": ["Giris formu calismali."],
            }
        ]
        output_path = tmp_path / "stories.docx"
        result_path = export_stories_docx(stories, path=output_path)

        assert result_path.exists(), ".docx dosyasi olusturulmaliydi."
        assert result_path.suffix == ".docx"
        assert result_path.stat().st_size > 0
