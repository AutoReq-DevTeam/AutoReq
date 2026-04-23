"""
tests/test_core.py — Core Modül Testleri
Sahibi: Üye 4 (Test koordinasyonu) + Üye 1 (içerik)

Çalıştırma: pytest tests/ -v
"""

import pytest

from core.classifier import RequirementClassifier
from core.ner import EntityRecognizer

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