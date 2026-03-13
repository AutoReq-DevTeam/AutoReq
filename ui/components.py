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
    # TODO: Üye 4 — Kart tasarımı (st.container + st.columns kombinasyonu)
    color = "🟢" if req_type == "FUNCTIONAL" else "🔵"
    st.markdown(f"**{color} [{req_id}]** {text}")


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
