import streamlit as st
from ui.results import render_results
from ui.components import page_header, empty_state

page_header(
    title="Analiz Sonuçları",
    subtitle="",
    step=3,
)

if st.session_state.get("analysis_report") is None:
    empty_state(
        icon="🔍",
        heading="Henüz bir analiz yapılmadı",
        body="Sonuçları görmek için önce Analiz sayfasından bir analiz başlatın.",
        cta_label="Analiz Sayfasına Git",
        cta_page="ui/pages/02_analysis.py",
    )
else:
    # Inject JS to click the right tab when navigated here from sidebar metrics
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
    // tab index 1 = Çelişkiler & Eksiklikler
    setTimeout(function() { clickTab(1); }, 400);
})();
</script>
""",
            height=0,
        )

    render_results(st.session_state.analysis_report)
