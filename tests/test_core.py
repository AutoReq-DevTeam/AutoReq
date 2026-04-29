"""
tests/test_core.py — Core Modül Testleri
Sahibi: Üye 4 (Test koordinasyonu) + Üye 1 (içerik)

Çalıştırma: pytest tests/ -v
"""

import pytest

from core.classifier import RequirementClassifier
from core.ner import EntityRecognizer

# TODO: Üye 1 ile koordineli olarak test senaryolarını doldur


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


class DummyRequirement:
    def __init__(self, text):
        self.text = text
        self.req_type = None
        self.actors = []
        self.objects = []


def test_basic():
    assert True


def test_classifier_marks_functional_requirement():
    classifier = RequirementClassifier()
    req = DummyRequirement("Admin rapor oluşturur.")

    result = classifier.classify(req)

    assert result is not None
    assert result.req_type == "FUNCTIONAL"


def test_classifier_marks_non_functional_requirement():
    classifier = RequirementClassifier()
    req = DummyRequirement("Sistem hızlı çalışmalı ve yüksek performans sağlamalıdır.")

    result = classifier.classify(req)

    assert result is not None
    assert result.req_type == "NON_FUNCTIONAL"


def test_ner_returns_actor_list():
    ner = EntityRecognizer()
    req = DummyRequirement("Kullanıcı şifresini sıfırlayabilmelidir.")

    result = ner.recognize(req)

    assert result is not None
    assert isinstance(result.actors, list)
    assert "kullanıcı" in result.actors