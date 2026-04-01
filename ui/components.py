"""
ui/components.py — Ortak Arayüz Bileşenleri
Sorumlu: Agid Gülsever

Açıklama:
Uygulama genelinde tekrar kullanılan görsel bileşenleri (kartlar, rozetler, butonlar) 
barındırır. Standart bir görsel dil oluşturmak için kullanılır.
"""

import streamlit as st


def req_card(req_id: str, text: str, req_type: str):
    """Tek bir gereksinimi kart formatında gösterir."""
    icon = "🟢" if req_type == "FUNCTIONAL" else "🔵"

    with st.container():
        col1, col2 = st.columns([1, 8])

        with col1:
            st.markdown(f"### {icon}")

        with col2:
            st.markdown(f"**{req_id}**")
            st.markdown(f"**Tür:** `{req_type}`")
            st.write(text)

        st.divider()


def priority_badge(priority: str):
    """Öncelik etiketi (HIGH / MEDIUM / LOW) gösterir."""
    colors = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
    icon = colors.get(priority, "⚪")
    st.markdown(f"{icon} `{priority}`")


def download_button(label: str, data: bytes, filename: str, mime: str):
    """Standart indirme butonu wrapper'ı."""
    st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime,
        use_container_width=True,
    )
