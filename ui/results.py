"""
ui/results.py — Analiz Sonuç Paneli
Sorumlu: Agid Gülsever

Açıklama:
Tamamlanan analiz sonuçlarını görselleştirir. Gereksinim listesi, çelişki raporları
ve teknik çıktıları sekmeli bir yapıda kullanıcıya sunar.
"""

from pathlib import Path

import streamlit as st

from ui.components import download_button, req_card


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

    st.header("📊 Analiz Sonuçları")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📋 Gereksinimler",
            "⚠️ Çelişkiler & Eksiklikler",
            "✨ İyileştirme Önerileri",
            "📥 İndirilebilir Çıktılar",
        ]
    )

    with tab1:
        st.subheader("Ayrıştırılan Gereksinimler")

        if requirements:
            for i, req in enumerate(requirements, start=1):
                req_text = getattr(req, "text", str(req))
                req_type = getattr(req, "req_type", "UNKNOWN")
                req_id = getattr(req, "id", f"REQ-{i}")

                req_card(req_id=req_id, text=req_text, req_type=req_type)
        else:
            st.warning("Henüz ayrıştırılmış gereksinim bulunamadı.")

    with tab2:
        st.subheader("Çelişkiler")

        if report.conflicts:
            for i, conflict in enumerate(report.conflicts, start=1):
                st.markdown(f"### Çelişki {i}")

                if isinstance(conflict, dict):
                    for key, value in conflict.items():
                        st.write(f"**{key}:** {value}")
                else:
                    st.write(conflict)
        else:
            st.info("Çelişki bulunamadı.")

        st.subheader("Eksiklikler")

        if report.gaps:
            for i, gap in enumerate(report.gaps, start=1):
                st.markdown(f"### Eksiklik {i}")

                if isinstance(gap, dict):
                    for key, value in gap.items():
                        st.write(f"**{key}:** {value}")
                else:
                    st.write(gap)
        else:
            st.info("Eksiklik bulunamadı.")

    with tab3:
        st.subheader("İyileştirme Önerileri")

        if report.improvements:
            for i, improvement in enumerate(report.improvements, start=1):
                st.markdown(f"### Öneri {i}")

                if isinstance(improvement, dict):
                    for key, value in improvement.items():
                        st.write(f"**{key}:** {value}")
                else:
                    st.write(improvement)
        else:
            st.info("Henüz iyileştirme önerisi bulunmuyor.")

    with tab4:
        st.subheader("İndirilebilir Çıktılar")

        generated_dir = Path("outputs") / "generated"
        pdf_files = list(generated_dir.glob("*.pdf"))

        if pdf_files:
            pdf_path = pdf_files[0]

            with open(pdf_path, "rb") as pdf_file:
                download_button(
                    label=f"📄 {pdf_path.name} dosyasını indir",
                    data=pdf_file.read(),
                    filename=pdf_path.name,
                    mime="application/pdf",
                )
        else:
            st.warning("outputs/generated klasöründe henüz PDF çıktısı bulunamadı.")