import pytest
from modules.gap_analyzer import GapAnalyzer

def test_gap_analyzer_not_implemented():
    analyzer = GapAnalyzer()

    with pytest.raises(NotImplementedError):
        analyzer.analyze(None)