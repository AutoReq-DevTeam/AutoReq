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
    type_label = "[F]" if req_type == "FUNCTIONAL" else "[NFR]"

    with st.container():
        col1, col2 = st.columns([1, 8])

        with col1:
            st.markdown(f"<h3 style='color:#D4AF37;'>{type_label}</h3>", unsafe_allow_html=True)

        with col2:
            st.markdown(f"**{req_id}**")
            st.markdown(f"**Tür:** `{req_type}`")
            st.write(text)

        st.divider()


def conflict_card(conflict: dict):
    """Tek bir çelişkiyi severity rozeti, req_ids ve açıklama ile gösterir."""
    severity = str(conflict.get("severity", "medium")).upper()
    severity_label = severity

    req_ids = conflict.get("req_ids", [])
    reason = conflict.get("reason", "Çelişki açıklaması bulunamadı.")
    conflict_type = conflict.get("conflict_type", "Genel Çelişki")

    with st.container():
        st.markdown(f"### {conflict_type}")
        st.markdown(f"**Severity:** `{severity_label}`")

        if req_ids:
            st.markdown("**İlgili Gereksinimler:**")
            req_links = [
                f"<a href='#{req_id}'>{req_id}</a>"
                for req_id in req_ids
            ]
            st.markdown(" | ".join(req_links), unsafe_allow_html=True)
        else:
            st.caption("İlgili gereksinim ID bilgisi bulunamadı.")

        with st.expander("Çelişki nedenini göster"):
            st.write(reason)

        st.divider()


def gap_card(gap: dict):
    """Tek bir eksikliği scenario, missing_area, suggestion ve severity ile gösterir."""
    scenario = gap.get("scenario", "unknown")
    missing_area = gap.get("missing_area", "Eksik alan belirtilmemiş.")
    suggestion = gap.get("suggestion", "Öneri bulunamadı.")
    severity = str(gap.get("severity", "medium")).upper()
    severity_label = severity

    with st.container():
        st.markdown(f"### {scenario}")
        st.markdown(f"**Eksik Alan:** {missing_area}")
        st.markdown(f"**Severity:** `{severity_label}`")
        st.checkbox(
            f"Öneri: {suggestion}",
            value=False,
            key=f"gap_{scenario}_{missing_area}_{suggestion}",
        )
        st.divider()


def improvement_diff_card(improvement: dict):
    """İyileştirme önerisini original/improved karşılaştırması olarak gösterir."""
    original = improvement.get("original", "Önceki ifade bulunamadı.")
    improved = improvement.get("improved", "İyileştirilmiş ifade bulunamadı.")
    reason = improvement.get("reason", "")

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Önce")
            st.warning(original)

        with col2:
            st.markdown("#### Sonra")
            st.success(improved)

        if reason:
            with st.expander("İyileştirme gerekçesi"):
                st.write(reason)

        st.divider()


def priority_badge(priority: str):
    """Öncelik etiketi (HIGH / MEDIUM / LOW) gösterir."""
    st.markdown(f"`{priority}`")


def download_button(label: str, data: bytes, filename: str, mime: str):
    """Standart indirme butonu wrapper'ı."""
    st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime,
        use_container_width=True,
    )