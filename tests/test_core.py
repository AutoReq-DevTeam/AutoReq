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
        # TODO: Üye 4 — Tokenizasyon çıktısını doğrula
        pass

    def test_empty_input(self):
        # TODO: Üye 4 — Boş string girildiğinde hata fırlatılmamalı
        pass


class TestRequirementClassifier:
    def test_functional_classification(self):
        # TODO: Üye 4 — Fonksiyonel bir cümleyi doğru sınıflandırmalı
        pass

    def test_non_functional_classification(self):
        # TODO: Üye 4 — NFR cümlesini doğru sınıflandırmalı
        pass


class TestEntityRecognizer:
    def test_actor_detection(self):
        # TODO: Üye 4 — "Kullanıcı" aktörünü tespit etmeli
        pass


def test_basic():
    assert True
    from core.classifier import RequirementClassifier


def test_classifier_classifies_requirement():
    classifier = RequirementClassifier()

    class DummyRequirement:
        def __init__(self, text):
            self.text = text
            self.req_type = "UNKNOWN"

    req = DummyRequirement("Sistem verileri hızlı işlemeli.")
    result = classifier.classify(req)
    assert result.req_type == "NON_FUNCTIONAL"

    req2 = DummyRequirement("Admin rapor oluşturabilmeli.")
    result2 = classifier.classify(req2)
    assert result2.req_type == "FUNCTIONAL"


def test_ner_recognizes_entities():
    ner = EntityRecognizer()

    class DummyRequirement:
        def __init__(self, text):
            self.text = text
            self.actors = []
            self.objects = []

    req = DummyRequirement("Kullanıcı profilini güncelleyebilir.")
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
    """PriorityDetector için 3 temel senaryo testi."""

    def _make_req(self, text: str):
        """Test için minimal Requirement benzeri nesne üretir."""

        class _Req:
            def __init__(self, t: str) -> None:
                self.id = "REQ_001"
                self.text = t
                self.priority = None

        return _Req(text)

    def test_high_priority_detection(self):
        """'güvenlik' veya 'kritik' içeren gereksinim HIGH öncelik almalı."""
        detector = PriorityDetector()

        req = self._make_req("Sistem güvenlik açıklarına karşı korunmalıdır.")
        result = detector.detect(req)
        assert result.priority == "HIGH"

        req2 = self._make_req("Kritik veriler şifreli saklanmalıdır.")
        result2 = detector.detect(req2)
        assert result2.priority == "HIGH"

    def test_low_priority_detection(self):
        """'tercihen' veya 'opsiyonel' içeren gereksinim LOW öncelik almalı."""
        detector = PriorityDetector()

        req = self._make_req("Karanlık mod tercihen desteklenmelidir.")
        result = detector.detect(req)
        assert result.priority == "LOW"

        req2 = self._make_req("İleride çoklu dil desteği eklenebilir.")
        result2 = detector.detect(req2)
        assert result2.priority == "LOW"

    def test_medium_priority_default(self):
        """HIGH veya LOW anahtar kelimesi içermeyen gereksinim MEDIUM almalı."""
        detector = PriorityDetector()

        req = self._make_req("Kullanıcı sisteme kayıt olabilmelidir.")
        result = detector.detect(req)
        assert result.priority == "MEDIUM"