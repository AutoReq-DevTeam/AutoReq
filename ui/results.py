"""
ui/results.py — Analysis Results Panel
"""

import streamlit as st

from ui.components import (
    conflict_card,
    gap_card,
    improvement_diff_card,
    req_card,
    empty_state,
)
from ui.i18n import t


def _section(label: str, margin_top: str = "0.5rem"):
    st.markdown(
        f'<p class="ar-section-label" style="margin-top:{margin_top};">{label}</p>',
        unsafe_allow_html=True,
    )


def render_results(report):
    requirements = report.parsed_doc.requirements
    conflicts = getattr(report, "conflicts", [])
    gaps = getattr(report, "gaps", [])
    improvements = getattr(report, "improvements", [])

    req_lookup = {
        getattr(req, "id", f"REQ-{i}"): getattr(req, "text", str(req))
        for i, req in enumerate(requirements, start=1)
    }

    tab1, tab2, tab3 = st.tabs(
        [t("tab_requirements"), t("tab_conflicts_gaps"), t("tab_improvements")]
    )

    with tab1:
        col1, col2 = st.columns([3, 1])
        with col1:
            _section(t("req_section_label"))
        with col2:
            filter_type = st.selectbox(
                "Filter",
                [t("filter_all"), t("filter_functional"), t("filter_nfr")],
                label_visibility="collapsed",
            )

        if requirements:
            for i, req in enumerate(requirements, start=1):
                req_text = getattr(req, "text", str(req))
                req_type = getattr(req, "req_type", "UNKNOWN")
                req_id = getattr(req, "id", f"REQ-{i}")

                if filter_type == t("filter_functional") and req_type != "FUNCTIONAL":
                    continue
                if filter_type == t("filter_nfr") and req_type != "NON_FUNCTIONAL":
                    continue

                st.markdown(f"<a id='{req_id}'></a>", unsafe_allow_html=True)
                req_card(req_id=req_id, text=req_text, req_type=req_type)
        else:
            empty_state(
                icon="📋",
                heading=t("req_empty_heading"),
                body=t("req_empty_body"),
            )

    with tab2:
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(
                f"""
<div style="background:var(--bg-card);border:1px solid var(--border-subtle);
            border-left:3px solid var(--color-danger);border-radius:6px;
            padding:1rem 1.25rem;margin-bottom:1rem;
            box-shadow:0 0 24px var(--color-danger-bg);">
    <div style="font-family:'Inter',sans-serif;font-size:0.7rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em;color:var(--text-tertiary);
                margin-bottom:0.4rem;">{t("total_conflicts_label")}</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:700;
                color:var(--color-danger);line-height:1;">{len(conflicts)}</div>
</div>""",
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                f"""
<div style="background:var(--bg-card);border:1px solid var(--border-subtle);
            border-left:3px solid var(--color-warning);border-radius:6px;
            padding:1rem 1.25rem;margin-bottom:1rem;
            box-shadow:0 0 24px var(--color-warning-bg);">
    <div style="font-family:'Inter',sans-serif;font-size:0.7rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em;color:var(--text-tertiary);
                margin-bottom:0.4rem;">{t("total_gaps_label")}</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:700;
                color:var(--color-warning);line-height:1;">{len(gaps)}</div>
</div>""",
                unsafe_allow_html=True,
            )

        _section(t("conflicts_section"))
        if conflicts:
            for conflict in conflicts:
                if isinstance(conflict, dict):
                    conflict_card(conflict, req_lookup=req_lookup)
                else:
                    st.write(conflict)
        else:
            st.info(t("no_conflicts_info"))

        _section(t("gaps_section"), margin_top="1.25rem")
        if gaps:
            grouped_gaps: dict = {}
            for gap in gaps:
                scenario = gap.get("scenario", "unknown") if isinstance(gap, dict) else "unknown"
                grouped_gaps.setdefault(scenario, []).append(gap)

            for scenario, scenario_gaps in grouped_gaps.items():
                st.markdown(
                    f'<p style="font-family:\'Inter\',sans-serif;font-size:0.8rem;'
                    f'font-weight:500;color:var(--text-secondary);margin:0.75rem 0 0.4rem;">'
                    f'{scenario}</p>',
                    unsafe_allow_html=True,
                )
                for gap in scenario_gaps:
                    if isinstance(gap, dict):
                        gap_card(gap)
                    else:
                        st.write(gap)
        else:
            st.info(t("no_gaps_info"))

    with tab3:
        _section(t("improvements_section"))
        if improvements:
            for improvement in improvements:
                if isinstance(improvement, dict):
                    improvement_diff_card(improvement)
                else:
                    st.write(improvement)
        else:
            empty_state(
                icon="✨",
                heading=t("improvements_empty_heading"),
                body=t("improvements_empty_body"),
            )
