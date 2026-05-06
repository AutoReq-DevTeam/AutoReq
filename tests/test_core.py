"""
tests/test_core.py — Core Modül Testleri
Sahibi: Üye 4 (Test koordinasyonu) + Üye 1 (içerik)

Çalıştırma: pytest tests/ -v
"""

import pytest
from pydantic import ValidationError

from core.classifier import RequirementClassifier
from core.models import AnalysisReport, ParsedDocument, Requirement
from core.ner import EntityRecognizer
from core.priority_detector import PriorityDetector

# TODO: Üye 4 — Üye 1 ile koordineli olarak test senaryolarını doldur


class TestTextPreprocessor:
    def test_tokenization(self):
        from core.preprocessor import TextPreprocessor
        from core.models import ParsedDocument
        preprocessor = TextPreprocessor()
        doc = preprocessor.process("Bu bir test cümlesidir. Başka bir cümledir.")
        assert isinstance(doc, ParsedDocument)
        assert doc.total_sentences == 2
        assert len(doc.requirements) == 2

    def test_empty_input(self):
        from core.preprocessor import TextPreprocessor
        from core.models import ParsedDocument
        preprocessor = TextPreprocessor()
        doc = preprocessor.process("")
        assert isinstance(doc, ParsedDocument)
        assert doc.total_sentences == 0
        assert len(doc.requirements) == 0

    def test_whitespace_only_input(self):
        """Yalnızca boşluk içeren metin boş ParsedDocument döndürmeli."""
        from core.preprocessor import TextPreprocessor
        preprocessor = TextPreprocessor()
        doc = preprocessor.process("   \t\n  ")
        assert len(doc.requirements) == 0

    def test_non_string_input_returns_empty_doc(self):
        """Tip hatası (None, int, vb.) geldiğinde çökmemeli, boş doc dönmeli."""
        from core.preprocessor import TextPreprocessor
        preprocessor = TextPreprocessor()
        doc = preprocessor.process(None)  # type: ignore[arg-type]
        assert len(doc.requirements) == 0


class TestRequirementClassifier:
    def test_functional_classification(self):
        classifier = RequirementClassifier()
        req = Requirement(id="1", text="Kullanıcı sisteme giriş yapabilmeli.")
        result = classifier.classify(req)
        assert result.req_type == "FUNCTIONAL"

    def test_non_functional_classification(self):
        classifier = RequirementClassifier()
        req = Requirement(id="2", text="Sistem hızlı olmalı.")
        result = classifier.classify(req)
        assert result.req_type == "NON_FUNCTIONAL"

    def test_empty_text_does_not_crash(self):
        """Boş metin geldiğinde classify() çökmemeli ve req_type'u değiştirmemeli."""
        classifier = RequirementClassifier()
        req = Requirement(id="3", text="", req_type="UNKNOWN")
        result = classifier.classify(req)
        # Boş metin için mevcut değer korunmalı
        assert result.req_type == "UNKNOWN"


class TestEntityRecognizer:
    def test_actor_detection(self):
        ner = EntityRecognizer()
        req = Requirement(id="1", text="Kullanıcı sisteme şifresi ile girebilir.")
        result = ner.recognize(req)
        assert "kullanıcı" in [actor.lower() for actor in result.actors]


def test_basic():
    assert True
    from core.classifier import RequirementClassifier


def test_classifier_classifies_requirement():
    classifier = RequirementClassifier()

    req = Requirement(id="REQ_T01", text="Sistem verileri hızlı işlemeli.")
    result = classifier.classify(req)
    assert result.req_type == "NON_FUNCTIONAL"

    req2 = Requirement(id="REQ_T02", text="Admin rapor oluşturabilmeli.")
    result2 = classifier.classify(req2)
    assert result2.req_type == "FUNCTIONAL"


def test_ner_recognizes_entities():
    ner = EntityRecognizer()

    req = Requirement(id="REQ_T03", text="Kullanıcı profilini güncelleyebilir.")
    result = ner.recognize(req)
    assert isinstance(result.actors, list)
    assert isinstance(result.objects, list)
    assert "kullanıcı" in result.actors


class TestModels:
    """core/models.py Pydantic v2 BaseModel'lerinin yapısal ve doğrulama testleri.

    Issue #17 kapsamında Pydantic v2 migrasyonu tamamlanmıştır (Scrum Master onaylı,
    2026-04-24). Yapısal testler varsayılan değer ve mutable default izolasyonunu;
    ValidationError testleri Literal alan kısıtlarını (req_type, priority) ve
    validate_assignment davranışını doğrular.
    """

    def test_requirement_default_req_type(self) -> None:
        """Requirement oluşturulurken req_type varsayılanı 'UNKNOWN' olmalı."""
        req = Requirement(id="REQ_001", text="Test gereksinimi.")
        assert req.req_type == "UNKNOWN"

    def test_requirement_mutable_default_isolation(self) -> None:
        """İki ayrı Requirement nesnesi actors listesini paylaşmamalı (mutable default tuzağı)."""
        req1 = Requirement(id="REQ_001", text="Birinci.")
        req2 = Requirement(id="REQ_002", text="İkinci.")
        req1.actors.append("kullanıcı")
        assert "kullanıcı" not in req2.actors, (
            "Mutable default tuzağı: req1.actors ile req2.actors aynı liste referansını paylaşıyor."
        )

    def test_requirement_priority_default_is_none(self) -> None:
        """Requirement.priority varsayılan değeri None olmalı."""
        req = Requirement(id="REQ_001", text="Önceliksiz gereksinim.")
        assert req.priority is None

    def test_parsed_document_default_empty_requirements(self) -> None:
        """ParsedDocument.requirements varsayılan olarak boş liste ile başlamalı."""
        doc = ParsedDocument(raw_text="Ham metin.")
        assert doc.requirements == []
        assert doc.language == "tr"
        assert doc.total_sentences == 0

    def test_analysis_report_default_empty_lists(self) -> None:
        """AnalysisReport.conflicts, gaps ve improvements varsayılan olarak boş liste olmalı."""
        doc = ParsedDocument(raw_text="Test metni.")
        report = AnalysisReport(parsed_doc=doc)
        assert report.conflicts == []
        assert report.gaps == []
        assert report.improvements == []

    def test_analysis_report_mutable_default_isolation(self) -> None:
        """İki ayrı AnalysisReport nesnesi conflicts listesini paylaşmamalı."""
        doc1 = ParsedDocument(raw_text="Birinci metin.")
        doc2 = ParsedDocument(raw_text="İkinci metin.")
        report1 = AnalysisReport(parsed_doc=doc1)
        report2 = AnalysisReport(parsed_doc=doc2)
        report1.conflicts.append({"req_ids": ["REQ_001"], "conflict_type": "logic", "reason": "test"})
        assert report2.conflicts == [], (
            "Mutable default tuzağı: report1.conflicts ile report2.conflicts aynı listeyi paylaşıyor."
        )

    def test_requirement_invalid_req_type_raises(self) -> None:
        """Geçersiz req_type değeri ValidationError fırlatmalı (Pydantic v2 AC #4)."""
        with pytest.raises(ValidationError):
            Requirement(id="REQ_001", text="Test.", req_type="INVALID")

    def test_requirement_invalid_priority_raises(self) -> None:
        """Geçersiz priority değeri ValidationError fırlatmalı."""
        with pytest.raises(ValidationError):
            Requirement(id="REQ_001", text="Test.", priority="CRITICAL")

    def test_requirement_invalid_assignment_raises(self) -> None:
        """validate_assignment=True: geçerli nesneye geçersiz atama da ValidationError fırlatmalı."""
        req = Requirement(id="REQ_001", text="Test.")
        with pytest.raises(ValidationError):
            req.req_type = "GECERSIZ"

    def test_requirement_valid_values_accepted(self) -> None:
        """Geçerli Literal değerleri hatasız kabul edilmeli."""
        for rt in ("FUNCTIONAL", "NON_FUNCTIONAL", "UNKNOWN"):
            req = Requirement(id="REQ_001", text="Test.", req_type=rt)
            assert req.req_type == rt
        for prio in ("HIGH", "MEDIUM", "LOW"):
            req = Requirement(id="REQ_001", text="Test.", priority=prio)
            assert req.priority == prio


class TestPriorityDetector:
    """PriorityDetector için 3 temel senaryo testi.

    Gerçek Requirement Pydantic nesneleri kullanılır — detect() dönüş tipi de
    doğrulanır.
    """

    def test_high_priority_detection(self):
        """'güvenlik' veya 'kritik' içeren gereksinim HIGH öncelik almalı."""
        detector = PriorityDetector()

        req = Requirement(id="REQ_001", text="Sistem güvenlik açıklarına karşı korunmalıdır.")
        result = detector.detect(req)
        assert isinstance(result, Requirement)
        assert result.priority == "HIGH"

        req2 = Requirement(id="REQ_002", text="Kritik veriler şifreli saklanmalıdır.")
        result2 = detector.detect(req2)
        assert result2.priority == "HIGH"

    def test_low_priority_detection(self):
        """'tercihen' veya 'opsiyonel' içeren gereksinim LOW öncelik almalı."""
        detector = PriorityDetector()

        req = Requirement(id="REQ_003", text="Karanlık mod tercihen desteklenmelidir.")
        result = detector.detect(req)
        assert isinstance(result, Requirement)
        assert result.priority == "LOW"

        req2 = Requirement(id="REQ_004", text="İleride çoklu dil desteği eklenebilir.")
        result2 = detector.detect(req2)
        assert result2.priority == "LOW"

    def test_medium_priority_default(self):
        """HIGH veya LOW anahtar kelimesi içermeyen gereksinim MEDIUM almalı."""
        detector = PriorityDetector()

        req = Requirement(id="REQ_005", text="Kullanıcı sisteme kayıt olabilmelidir.")
        result = detector.detect(req)
        assert isinstance(result, Requirement)
        assert result.priority == "MEDIUM"

    def test_detect_returns_requirement_instance(self):
        """detect() her zaman Requirement tipinde bir nesne döndürmeli."""
        detector = PriorityDetector()
        req = Requirement(id="REQ_006", text="Sistem çalışmalıdır.")
        result = detector.detect(req)
        assert isinstance(result, Requirement), "detect() Requirement tipinde nesne döndürmeli."
        assert result.priority in ("HIGH", "MEDIUM", "LOW")


class TestPipeline:
    """Tests for core/pipeline.py — process_text() and helpers.

    nlp_engines is replaced with mocks so Stanza is never called from these tests.
    Output generators are also mocked to avoid filesystem writes.
    """

    @staticmethod
    def _make_mock_engines(req):
        from core.models import ParsedDocument
        from unittest.mock import MagicMock

        parsed_doc = ParsedDocument(
            raw_text="Test metni.",
            requirements=[req],
            total_sentences=1,
        )
        return {
            "preprocessor": MagicMock(**{"process.return_value": parsed_doc}),
            "classifier": MagicMock(**{"classify.return_value": req}),
            "ner": MagicMock(**{"recognize.return_value": req}),
            "priority_detector": MagicMock(**{"detect.return_value": req}),
        }, parsed_doc

    @staticmethod
    def _patch_outputs(monkeypatch, pipeline_module):
        from unittest.mock import MagicMock

        monkeypatch.setattr(pipeline_module, "generate_srs", MagicMock())
        monkeypatch.setattr(pipeline_module, "export_backlog_xlsx", MagicMock())
        monkeypatch.setattr(pipeline_module, "export_stories_docx", MagicMock())
        monkeypatch.setattr(pipeline_module, "export_report_json", MagicMock())
        monkeypatch.setattr(pipeline_module, "BacklogGenerator", MagicMock())
        monkeypatch.setattr(pipeline_module, "StoryGenerator", MagicMock())
        monkeypatch.setattr(pipeline_module, "BDDGenerator", MagicMock())

    def test_is_llm_available_with_key(self, monkeypatch):
        import core.pipeline as pm
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        assert pm._is_llm_available() is True

    def test_is_llm_available_without_key(self, monkeypatch):
        import core.pipeline as pm
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        assert pm._is_llm_available() is False

    def test_process_text_no_llm_returns_report(self, monkeypatch):
        """Without GEMINI_API_KEY, LLM branches are skipped; report fields are empty."""
        import core.pipeline as pm
        from core.models import AnalysisReport, Requirement

        req = Requirement(id="REQ_001", text="Test cümlesi.")
        mock_engines, _ = self._make_mock_engines(req)
        monkeypatch.setattr(pm, "nlp_engines", mock_engines)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        self._patch_outputs(monkeypatch, pm)

        report = pm.process_text("Test metni.")
        assert isinstance(report, AnalysisReport)
        assert report.conflicts == []
        assert report.gaps == []
        assert report.improvements == []

    def test_process_text_calls_nlp_engines(self, monkeypatch):
        """process_text() invokes classifier, ner, and priority_detector for every req."""
        import core.pipeline as pm
        from core.models import Requirement

        req = Requirement(id="REQ_001", text="Test cümlesi.")
        mock_engines, _ = self._make_mock_engines(req)
        monkeypatch.setattr(pm, "nlp_engines", mock_engines)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        self._patch_outputs(monkeypatch, pm)

        pm.process_text("Test metni.")
        mock_engines["classifier"].classify.assert_called_once_with(req)
        mock_engines["ner"].recognize.assert_called_once()
        mock_engines["priority_detector"].detect.assert_called_once()

    def test_process_text_with_status_ui(self, monkeypatch):
        """status_ui.update() is called at least once during processing."""
        import core.pipeline as pm
        from core.models import Requirement
        from unittest.mock import MagicMock

        req = Requirement(id="REQ_001", text="Test.")
        mock_engines, _ = self._make_mock_engines(req)
        monkeypatch.setattr(pm, "nlp_engines", mock_engines)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        self._patch_outputs(monkeypatch, pm)

        status_ui = MagicMock()
        pm.process_text("Test.", status_ui=status_ui)
        assert status_ui.update.called

    def test_process_text_llm_conflict_error_falls_back(self, monkeypatch):
        """LLMClientError in ConflictDetector → conflicts stays []."""
        import core.pipeline as pm
        from core.models import Requirement
        from modules.llm_client import LLMClientError
        from unittest.mock import MagicMock

        req = Requirement(id="REQ_001", text="Test cümlesi.")
        mock_engines, _ = self._make_mock_engines(req)
        monkeypatch.setattr(pm, "nlp_engines", mock_engines)
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

        mock_conflict = MagicMock()
        mock_conflict.return_value.analyze.side_effect = LLMClientError("429")
        monkeypatch.setattr(pm, "ConflictDetector", mock_conflict)

        mock_gap = MagicMock()
        mock_gap.return_value.analyze.return_value = []
        monkeypatch.setattr(pm, "GapAnalyzer", mock_gap)

        mock_improver = MagicMock()
        mock_improver.return_value.improve.return_value = {"original": "x", "improved": "x"}
        monkeypatch.setattr(pm, "RequirementImprover", mock_improver)

        self._patch_outputs(monkeypatch, pm)

        report = pm.process_text("Test metni.")
        assert report.conflicts == []

    def test_process_text_successful_llm(self, monkeypatch):
        """When LLM is available and all analyzers succeed, results are populated."""
        import core.pipeline as pm
        from core.models import Requirement
        from unittest.mock import MagicMock

        req = Requirement(id="REQ_001", text="Test cümlesi.")
        mock_engines, _ = self._make_mock_engines(req)
        monkeypatch.setattr(pm, "nlp_engines", mock_engines)
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

        conflict = {"req_ids": ["REQ_001"], "conflict_type": "CONTRADICTORY", "reason": "x"}
        gap = {"missing_area": "Auth", "suggestion": "Add 2FA", "severity": "HIGH"}
        improvement = {"original": "Test.", "improved": "Test gereksinimi netleştirildi."}

        mock_conflict = MagicMock()
        mock_conflict.return_value.analyze.return_value = [conflict]
        monkeypatch.setattr(pm, "ConflictDetector", mock_conflict)

        mock_gap = MagicMock()
        mock_gap.return_value.analyze.return_value = [gap]
        monkeypatch.setattr(pm, "GapAnalyzer", mock_gap)

        mock_improver = MagicMock()
        mock_improver.return_value.improve.return_value = improvement
        monkeypatch.setattr(pm, "RequirementImprover", mock_improver)

        self._patch_outputs(monkeypatch, pm)

        report = pm.process_text("Test metni.")
        assert len(report.conflicts) == 1
        assert len(report.gaps) == 1
        assert len(report.improvements) == 1