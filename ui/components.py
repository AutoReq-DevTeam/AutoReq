"""
ui/components.py — Ortak Arayüz Bileşenleri
"""

import streamlit as st


def req_card(req_id: str, text: str, req_type: str):
    is_func = req_type == "FUNCTIONAL"
    badge_cls = "ar-badge ar-badge--func" if is_func else "ar-badge ar-badge--nfr"
    badge_lbl = "Fonksiyonel" if is_func else "Fonksiyonel Olmayan"
    card_mod = "" if is_func else " ar-req-card--nfr"

    st.markdown(
        f"""
<div class="ar-req-card{card_mod}">
    <div style="display:flex;align-items:center;flex-wrap:wrap;gap:0.25rem;margin-bottom:0.1rem;">
        <span class="{badge_cls}">{badge_lbl}</span>
        <span class="ar-req-id">{req_id}</span>
    </div>
    <div class="ar-req-text">{text}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def conflict_card(conflict: dict):
    severity = str(conflict.get("severity", "medium")).upper()
    req_ids = conflict.get("req_ids", [])
    reason = conflict.get("reason", "Çelişki açıklaması bulunamadı.")
    conflict_type = conflict.get("conflict_type", "Genel Çelişki")

    sev_map = {
        "HIGH":   ("ar-badge ar-badge--high",   "Yüksek",   ""),
        "MEDIUM": ("ar-badge ar-badge--medium",  "Orta",     " ar-conflict-card--medium"),
        "LOW":    ("ar-badge ar-badge--low",     "Düşük",    " ar-conflict-card--low"),
    }
    badge_cls, badge_lbl, card_mod = sev_map.get(severity, sev_map["MEDIUM"])

    req_links_html = " ".join(
        f'<a class="ar-req-link" href="#{rid}">{rid}</a>' for rid in req_ids
    ) if req_ids else '<span style="font-size:0.78rem;color:#444;font-family:\'Inter\',sans-serif;">—</span>'

    st.markdown(
        f"""
<div class="ar-conflict-card{card_mod}">
    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem;">
        <span class="{badge_cls}">{badge_lbl}</span>
        <span class="ar-conflict-title">{conflict_type}</span>
    </div>
    <div style="margin-bottom:0.25rem;">{req_links_html}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.expander("Çelişki nedenini görüntüle"):
        st.markdown(
            f'<p style="font-family:\'Inter\',sans-serif;font-size:0.875rem;'
            f'color:#c0c0c0;line-height:1.7;margin:0;">{reason}</p>',
            unsafe_allow_html=True,
        )


def gap_card(gap: dict):
    import hashlib

    scenario = gap.get("scenario", "unknown")
    missing_area = gap.get("missing_area", "Eksik alan belirtilmemiş.")
    suggestion = gap.get("suggestion", "Öneri bulunamadı.")
    severity = str(gap.get("severity", "medium")).upper()

    sev_map = {
        "HIGH":   ("ar-badge ar-badge--high",   "Yüksek",   ""),
        "MEDIUM": ("ar-badge ar-badge--medium",  "Orta",     ""),
        "LOW":    ("ar-badge ar-badge--low",     "Düşük",    " ar-gap-card--low"),
    }
    badge_cls, badge_lbl, card_mod = sev_map.get(severity, sev_map["MEDIUM"])

    _raw_key = f"gap_{scenario}_{missing_area}_{suggestion}"
    _stable_key = "gap_" + hashlib.md5(_raw_key.encode("utf-8")).hexdigest()[:12]

    st.markdown(
        f"""
<div class="ar-gap-card{card_mod}">
    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.4rem;">
        <span class="{badge_cls}">{badge_lbl}</span>
        <span class="ar-gap-title">{scenario}</span>
    </div>
    <div class="ar-gap-area">{missing_area}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.checkbox(
        f"Öneri: {suggestion}",
        value=False,
        key=_stable_key,
    )


def improvement_diff_card(improvement: dict):
    original = improvement.get("original", "Önceki ifade bulunamadı.")
    improved = improvement.get("improved", "İyileştirilmiş ifade bulunamadı.")
    reason = improvement.get("reason", "")

    st.markdown(
        f"""
<div class="ar-diff-wrap">
    <div class="ar-diff-header">
        <div class="ar-diff-col">
            <span class="ar-diff-label">Önceki</span>
        </div>
        <div class="ar-diff-col">
            <span class="ar-diff-label">İyileştirilmiş</span>
        </div>
    </div>
    <div class="ar-diff-body">
        <div class="ar-diff-before">{original}</div>
        <div class="ar-diff-after">{improved}</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if reason:
        with st.expander("İyileştirme gerekçesini görüntüle"):
            st.markdown(
                f'<p style="font-family:\'Inter\',sans-serif;font-size:0.875rem;'
                f'color:#c0c0c0;line-height:1.7;margin:0;">{reason}</p>',
                unsafe_allow_html=True,
            )


def priority_badge(priority: str):
    st.markdown(
        f'<span class="ar-badge ar-badge--low">{priority}</span>',
        unsafe_allow_html=True,
    )


def download_button(label: str, data: bytes, filename: str, mime: str):
    st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime,
        use_container_width=True,
    )
