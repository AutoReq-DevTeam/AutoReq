"""
ui/results.py — Sonuçları Gösterme Ekranı
Sahibi: Üye 4 (Arayüz ve Entegrasyon)

Senin Görevin:
Analiz bitti! Şimdi Üye 2'nin ve Üye 3'ün o karanlıkta ürettiği tüm raporları müşteriye çok şık bir şekilde sunma vakti.
Burada sekmeler (tablar) kullan.
1. Sekmede temizlenmiş metni tablo yap.
2. Sekmede Üye 2'nin bulduğu hataları kırmızı ünlemlerle (⚠️) göster.
3. Sekmede büyük "PDF İndir", "Excel İndir" butonları koy.

Çıktı: "Müşterinin okumaktan keyif alacağı, sekmeli ve butonlu harika bir sonuç sayfası."
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
