"""
tests/test_modules.py — Akıllı Modül Testleri
Sahibi: Üye 4 (Test koordinasyonu) + Üye 2 (içerik)
"""

import pytest
from modules.gap_analyzer import GapAnalyzer


def test_gap_analyzer_not_implemented():
    analyzer = GapAnalyzer()

    with pytest.raises(NotImplementedError):
        analyzer.analyze(None)


class TestConflictDetector:
    def test_detects_contradiction(self):
        # TODO: Üye 4 — Zıt ifadeler içeren bir belgede çelişki tespit edilmeli
        pass


class TestGapAnalyzer:
    def test_detects_missing_password_reset(self):
        # TODO: Üye 4 — Login gereksinimi varsa Password Reset eksikliği önerilmeli
        pass


class TestRequirementImprover:
    def test_improves_vague_requirement(self):
        # TODO: Üye 4 — "Hızlı olmalı" ifadesi ölçülebilir öneriye dönüşmeli
        pass