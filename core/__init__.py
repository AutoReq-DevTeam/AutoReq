# core/__init__.py
# Sahibi: Üye 1 (NLP Core & Preprocessing)

from .preprocessor import TextPreprocessor
from .classifier import RequirementClassifier
from .ner import EntityRecognizer
from .models import ParsedDocument
from .nlp_engine import get_shared_stanza_pipeline

__all__ = [
    "TextPreprocessor",
    "RequirementClassifier",
    "EntityRecognizer",
    "ParsedDocument",
    "get_shared_stanza_pipeline",
]
