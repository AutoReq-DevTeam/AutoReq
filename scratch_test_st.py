import sys
from unittest.mock import MagicMock

mock_st = MagicMock()
mock_st.session_state = {}
def mock_cache_resource(*args, **kwargs):
    def decorator(func):
        return func
    return decorator
mock_st.cache_resource = mock_cache_resource
sys.modules['streamlit'] = mock_st

import streamlit as st
print("st.session_state:", st.session_state)

from core.pipeline import nlp_engines
print("NLP Engines loaded:", nlp_engines.keys())
