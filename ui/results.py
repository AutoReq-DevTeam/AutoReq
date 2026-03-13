"""
ui/results.py — Analiz Sonuç Paneli
Sorumlu: Agid Gülsever

Açıklama:
Tamamlanan analiz sonuçlarını görselleştirir. Gereksinim listesi, çelişki raporları 
ve indirilebilir dökümanları sekmeli bir yapıda kullanıcıya sunar.
"""

import streamlit as st


def render_results(report):
    """
    Analiz raporunu sekmeli panelde görüntüler.

    Parametreler:
        report: AnalysisReport nesnesi (Üye 2'den gelir).
    """
    st.header("📊 Analiz Sonuçları")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📋 Gereksinimler",
            "⚠️ Çelişkiler & Eksiklikler",
            "💡 İyileştirme Önerileri",
            "📥 İndirilebilir Çıktılar",
        ]
    )

    with tab1:
        # TODO: Üye 4 — report.parsed_doc.requirements listesini tablo olarak göster
        st.info("Gereksinim tablosu buraya gelecek.")

    with tab2:
        # TODO: Üye 4 — report.conflicts ve report.gaps'i listele
        st.info("Çelişki ve eksiklik listesi buraya gelecek.")

    with tab3:
        # TODO: Üye 4 — report.improvements listesini göster
        st.info("İyileştirme önerileri buraya gelecek.")

    with tab4:
        # TODO: Üye 4 — SRS PDF, User Stories, Backlog, BDD indirme butonları
        st.info("İndirme butonları buraya gelecek.")
