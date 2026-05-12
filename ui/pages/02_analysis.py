import streamlit as st
from core.pipeline import process_text
from ui.state import update_counts
from ui.components import page_header, empty_state
from ui.i18n import t

page_header(
    title=t("analysis_title"),
    subtitle=t("analysis_subtitle"),
    step=2,
)

if "user_input" not in st.session_state or not st.session_state.user_input.strip():
    empty_state(
        icon="📝",
        heading=t("analysis_empty_heading"),
        body=t("analysis_empty_body"),
        cta_label=t("analysis_go_input"),
        cta_page="ui/pages/01_input.py",
    )
else:
    raw_text = st.session_state.user_input

    _lines = [ln.strip() for ln in raw_text.split("\n") if len(ln.strip()) > 15]
    est_count = max(1, len(_lines))

    st.markdown(
        f'<p style="font-family:\'Inter\',sans-serif;font-size:0.875rem;'
        f'color:var(--text-tertiary);margin-bottom:0.75rem;">'
        f'{t("analysis_est_lines", count=est_count)}</p>',
        unsafe_allow_html=True,
    )

    st.info(t("analysis_preview_info"))
    st.text_area(t("analysis_input_label"), value=raw_text, height=150, disabled=True)

    if st.button(t("analysis_start_btn"), type="primary", use_container_width=True):
        st.toast(t("analysis_started_toast"))

        progress_bar = st.progress(0, text=t("analysis_preparing"))

        status = st.status(t("analysis_status_starting"), expanded=True)

        progress_bar.progress(15, text=t("analysis_preprocessing"))
        st.session_state.analysis_report = process_text(raw_text, status_ui=status)
        progress_bar.progress(100, text=t("analysis_done"))

        update_counts()
        status.update(label=t("analysis_status_done"), state="complete", expanded=False)

        req_c = st.session_state.get("req_count", 0)
        conflict_c = st.session_state.get("conflict_count", 0)
        gap_c = st.session_state.get("gap_count", 0)
        cost = st.session_state.get("total_cost_usd", 0.0)

        st.toast(t("analysis_toast_done", req_c=req_c, conflict_c=conflict_c, gap_c=gap_c))

        st.markdown(
            f"""
<div style="display:flex;gap:1rem;margin:1rem 0;flex-wrap:wrap;">
  <div style="background:var(--bg-card);border:1px solid var(--border-subtle);border-left:3px solid var(--accent-primary);
              border-radius:6px;padding:0.75rem 1.25rem;flex:1;min-width:120px;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;font-weight:700;
                color:var(--accent-primary);line-height:1;">{req_c}</div>
    <div style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em;color:var(--text-tertiary);
                margin-top:0.25rem;">{t("req_label")}</div>
  </div>
  <div style="background:var(--bg-card);border:1px solid var(--border-subtle);border-left:3px solid var(--color-danger);
              border-radius:6px;padding:0.75rem 1.25rem;flex:1;min-width:120px;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;font-weight:700;
                color:var(--color-danger);line-height:1;">{conflict_c}</div>
    <div style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em;color:var(--text-tertiary);
                margin-top:0.25rem;">{t("conflict_label")}</div>
  </div>
  <div style="background:var(--bg-card);border:1px solid var(--border-subtle);border-left:3px solid var(--color-warning);
              border-radius:6px;padding:0.75rem 1.25rem;flex:1;min-width:120px;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;font-weight:700;
                color:var(--color-warning);line-height:1;">{gap_c}</div>
    <div style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em;color:var(--text-tertiary);
                margin-top:0.25rem;">{t("gap_label")}</div>
  </div>
  <div style="background:var(--bg-card);border:1px solid var(--border-subtle);border-left:3px solid var(--color-info);
              border-radius:6px;padding:0.75rem 1.25rem;flex:1;min-width:120px;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;font-weight:700;
                color:var(--color-info);line-height:1;">${cost:.4f}</div>
    <div style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em;color:var(--text-tertiary);
                margin-top:0.25rem;">{t("cost_label")}</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        if st.session_state.get("pipeline_warnings"):
            st.error(t("analysis_error"))
            st.session_state["pipeline_warnings"] = []
        else:
            st.success(t("analysis_success"))
            st.switch_page("ui/pages/03_results.py")
