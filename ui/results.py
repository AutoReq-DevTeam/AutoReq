"""
ui/results.py — Analiz Sonuç Paneli
Sorumlu: Agid Gülsever

Açıklama:
Tamamlanan analiz sonuçlarını görselleştirir. Gereksinim listesi, çelişki raporları
ve teknik çıktıları sekmeli bir yapıda kullanıcıya sunar.
"""

import streamlit as st


def render_results(report):
    """
    Analiz raporunu sekmeli panelde görüntüler.

    Parametreler:
        report: AnalysisReport nesnesi
    """
    requirements = report.parsed_doc.requirements

    st.header("📊 Analiz Sonuçları")

    tab1, tab2, tab3 = st.tabs(
        [
            "📄 Özet",
            "📋 Gereksinimler",
            "⚙️ Teknik",
        ]
    )

    with tab1:
        st.subheader("Analiz Özeti")
        st.metric("Toplam Gereksinim", len(requirements))

        if requirements:
            st.success("Metin başarıyla işlendi ve gereksinimler ayrıştırıldı.")
        else:
            st.warning("Analiz tamamlandı ancak gereksinim listesi boş döndü.")

    with tab2:
        st.subheader("Ayrıştırılan Gereksinimler")

        if requirements:
            for i, req in enumerate(requirements, start=1):
                st.markdown(f"### 📌 Gereksinim {i}")
                st.info(str(req))
        else:
            st.warning("Henüz ayrıştırılmış gereksinim bulunamadı.")

    with tab3:
        st.subheader("Teknik Detaylar")
        st.write("Çatışmalar:", report.conflicts)
        st.write("Eksikler:", report.gaps)
        st.write("İyileştirmeler:", report.improvements)