import streamlit as st


def init_state():
    """Uygulama için gerekli session state alanlarını başlatır."""

    defaults = {
        "user_input": "",
        "analysis_report": None,
        "req_count": 0,
        "conflict_count": 0,
        "gap_count": 0,
        "total_tokens_used": 0,
        "total_cost_usd": 0.0,
        "demo_mode": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def update_counts():
    """Analiz sonucuna göre sayaçları günceller."""

    report = st.session_state.get("analysis_report")

    if report is None:
        st.session_state.req_count = 0
        st.session_state.conflict_count = 0
        st.session_state.gap_count = 0
        return

    st.session_state.req_count = len(report.parsed_doc.requirements)
    st.session_state.conflict_count = len(report.conflicts)
    st.session_state.gap_count = len(report.gaps)