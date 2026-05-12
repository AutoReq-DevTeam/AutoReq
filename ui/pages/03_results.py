import streamlit as st
from ui.results import render_results
from ui.components import page_header, empty_state
from ui.i18n import t

page_header(
    title=t("results_title"),
    subtitle="",
    step=3,
)

if st.session_state.get("analysis_report") is None:
    empty_state(
        icon="🔍",
        heading=t("results_empty_heading"),
        body=t("results_empty_body"),
        cta_label=t("results_go_analysis"),
        cta_page="ui/pages/02_analysis.py",
    )
else:
    scroll_to = st.session_state.pop("result_scroll_to", None)
    if scroll_to in ("conflicts", "gaps"):
        st.components.v1.html(
            """
<script>
(function() {
    function clickTab(idx) {
        var tabs = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
        if (tabs.length > idx) {
            tabs[idx].click();
        }
    }
    setTimeout(function() { clickTab(1); }, 400);
})();
</script>
""",
            height=0,
        )

    render_results(st.session_state.analysis_report)
