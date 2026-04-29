import streamlit as st
from ui.results import render_results

st.title("Sonuçlar")

if st.session_state.get("analysis_report") is None:
    st.warning("Henüz bir analiz yapılmadı. Lütfen Analiz sayfasına gidin.")
    if st.button("Analiz Sayfasına Git"):
        st.switch_page("ui/pages/02_analysis.py")
else:
    # We call the existing render_results function which renders the tabs
    render_results(st.session_state.analysis_report)
