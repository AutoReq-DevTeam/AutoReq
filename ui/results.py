"""
ui/results.py — Analiz Sonuç Paneli
"""

import streamlit as st

from ui.components import (
    conflict_card,
    gap_card,
    improvement_diff_card,
    req_card,
)


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

    tab1, tab2, tab3 = st.tabs(
        ["Gereksinimler", "Çelişkiler & Eksiklikler", "İyileştirme Önerileri"]
    )

    with tab1:
        col1, col2 = st.columns([3, 1])
        with col1:
            _section("Ayrıştırılan Gereksinimler")
        with col2:
            filter_type = st.selectbox(
                "Filtrele",
                ["Tümü", "Fonksiyonel", "Fonksiyonel Olmayan"],
                label_visibility="collapsed",
            )

        if requirements:
            for i, req in enumerate(requirements, start=1):
                req_text = getattr(req, "text", str(req))
                req_type = getattr(req, "req_type", "UNKNOWN")
                req_id = getattr(req, "id", f"REQ-{i}")

                if filter_type == "Fonksiyonel" and req_type != "FUNCTIONAL":
                    continue
                if filter_type == "Fonksiyonel Olmayan" and req_type != "NON_FUNCTIONAL":
                    continue

                st.markdown(f"<a id='{req_id}'></a>", unsafe_allow_html=True)
                req_card(req_id=req_id, text=req_text, req_type=req_type)
        else:
            st.warning("Henüz ayrıştırılmış gereksinim bulunamadı.")

    with tab2:
        # Özet metrikler
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(
                f"""
<div style="background:#111111;border:1px solid #1e1e1e;border-radius:6px;
            padding:1rem 1.25rem;margin-bottom:1rem;">
    <div style="font-family:'Inter',sans-serif;font-size:0.7rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em;color:#555555;
                margin-bottom:0.4rem;">Toplam Çelişki</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:700;
                color:#ff5252;line-height:1;">{len(conflicts)}</div>
</div>""",
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                f"""
<div style="background:#111111;border:1px solid #1e1e1e;border-radius:6px;
            padding:1rem 1.25rem;margin-bottom:1rem;">
    <div style="font-family:'Inter',sans-serif;font-size:0.7rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em;color:#555555;
                margin-bottom:0.4rem;">Toplam Eksiklik</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:700;
                color:#f5a623;line-height:1;">{len(gaps)}</div>
</div>""",
                unsafe_allow_html=True,
            )

        _section("Çelişkiler")
        if conflicts:
            for conflict in conflicts:
                if isinstance(conflict, dict):
                    conflict_card(conflict)
                else:
                    st.write(conflict)
        else:
            st.info("Çelişki bulunamadı.")

        _section("Eksiklikler", margin_top="1.25rem")
        if gaps:
            grouped_gaps: dict = {}
            for gap in gaps:
                scenario = gap.get("scenario", "unknown") if isinstance(gap, dict) else "unknown"
                grouped_gaps.setdefault(scenario, []).append(gap)

            for scenario, scenario_gaps in grouped_gaps.items():
                st.markdown(
                    f'<p style="font-family:\'Inter\',sans-serif;font-size:0.8rem;'
                    f'font-weight:500;color:#888888;margin:0.75rem 0 0.4rem;">{scenario}</p>',
                    unsafe_allow_html=True,
                )
                for gap in scenario_gaps:
                    if isinstance(gap, dict):
                        gap_card(gap)
                    else:
                        st.write(gap)
        else:
            st.info("Eksiklik bulunamadı.")

    with tab3:
        _section("İyileştirme Önerileri")
        if improvements:
            for improvement in improvements:
                if isinstance(improvement, dict):
                    improvement_diff_card(improvement)
                else:
                    st.write(improvement)
        else:
            st.info("Henüz iyileştirme önerisi bulunmuyor.")
