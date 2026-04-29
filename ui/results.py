"""
ui/results.py — Analiz Sonuç Paneli
Sorumlu: Agid Gülsever

Açıklama:
Tamamlanan analiz sonuçlarını görselleştirir. Gereksinim listesi, çelişki raporları
ve teknik çıktıları sekmeli bir yapıda kullanıcıya sunar.
"""

from pathlib import Path

import streamlit as st

from ui.components import (
    conflict_card,
    gap_card,
    improvement_diff_card,
    req_card,
)


def _safe_get(dictionary, key, default="-"):
    if isinstance(dictionary, dict):
        return dictionary.get(key, default)
    return default


def render_results(report):
    """
    Analiz raporunu sekmeli panelde görüntüler.

    Parametreler:
        report: AnalysisReport nesnesi
    """
    requirements = report.parsed_doc.requirements
    conflicts = getattr(report, "conflicts", [])
    gaps = getattr(report, "gaps", [])
    improvements = getattr(report, "improvements", [])

    st.header("Analiz Sonuçları")

    tab1, tab2, tab3 = st.tabs(
        [
            "Gereksinimler",
            "Çelişkiler & Eksiklikler",
            "İyileştirme Önerileri",
        ]
    )

    with tab1:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Ayrıştırılan Gereksinimler")
        with col2:
            filter_type = st.selectbox(
                "Filtrele", 
                ["Tümü", "Fonksiyonel", "Fonksiyonel Olmayan"],
                label_visibility="collapsed"
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
        metric_col1, metric_col2 = st.columns(2)

        with metric_col1:
            st.metric("Toplam Çelişki", len(conflicts))

        with metric_col2:
            st.metric("Toplam Eksiklik", len(gaps))

        st.subheader("Çelişkiler")

        if conflicts:
            for conflict in conflicts:
                if isinstance(conflict, dict):
                    conflict_card(conflict)
                else:
                    st.write(conflict)
        else:
            st.info("Çelişki bulunamadı.")

        st.subheader("Eksiklikler")

        if gaps:
            grouped_gaps = {}

            for gap in gaps:
                if isinstance(gap, dict):
                    scenario = gap.get("scenario", "unknown")
                    grouped_gaps.setdefault(scenario, []).append(gap)
                else:
                    grouped_gaps.setdefault("unknown", []).append(gap)

            for scenario, scenario_gaps in grouped_gaps.items():
                st.markdown(f"### {scenario}")

                for gap in scenario_gaps:
                    if isinstance(gap, dict):
                        gap_card(gap)
                    else:
                        st.write(gap)
        else:
            st.info("Eksiklik bulunamadı.")

    with tab3:
        st.subheader("İyileştirme Önerileri")

        if improvements:
            for improvement in improvements:
                if isinstance(improvement, dict):
                    improvement_diff_card(improvement)
                else:
                    st.write(improvement)
        else:
            st.info("Henüz iyileştirme önerisi bulunmuyor.")
