"""
ui/components.py — Ortak Arayüz Bileşenleri
"""

import streamlit as st


# ── Step indicator + page header ─────────────────────────────────────────────

def page_header(title: str, subtitle: str = "", step: int = 1) -> None:
    """Render the step indicator, page title, and optional subtitle."""
    steps = ["Girdi", "Analiz", "Sonuçlar", "Dışa Aktarım"]

    parts = []
    for i, label in enumerate(steps):
        pos = i + 1
        if pos < step:
            cls = "ar-step--complete"
            dot = "✓"
        elif pos == step:
            cls = "ar-step--active"
            dot = ""
        else:
            cls = "ar-step--future"
            dot = ""

        parts.append(
            f'<div class="ar-step {cls}">'
            f'<div class="ar-step-dot">{dot}</div>'
            f'<span class="ar-step-label">{label}</span>'
            f'</div>'
        )
        if i < len(steps) - 1:
            line_cls = "ar-step-line" if pos < step else "ar-step-line ar-step-line--future"
            parts.append(f'<div class="{line_cls}"></div>')

    stepper_html = '<div class="ar-stepper">' + "".join(parts) + "</div>"
    st.markdown(stepper_html, unsafe_allow_html=True)
    st.title(title)

    if subtitle:
        st.markdown(
            f'<p style="font-family:\'Inter\',sans-serif;font-size:0.875rem;'
            f'color:var(--text-tertiary);margin-top:-0.75rem;margin-bottom:1.5rem;">'
            f'{subtitle}</p>',
            unsafe_allow_html=True,
        )


# ── Empty state ───────────────────────────────────────────────────────────────

def empty_state(
    icon: str,
    heading: str,
    body: str,
    cta_label: str = "",
    cta_page: str = "",
) -> None:
    """Render a centered empty-state placeholder with an optional CTA button."""
    st.markdown(
        f"""
<div class="ar-empty-state">
    <div class="ar-empty-state-icon">{icon}</div>
    <div class="ar-empty-state-title">{heading}</div>
    <div class="ar-empty-state-body">{body}</div>
</div>
""",
        unsafe_allow_html=True,
    )
    if cta_label and cta_page:
        col = st.columns([1, 2, 1])[1]
        with col:
            if st.button(cta_label, use_container_width=True):
                st.switch_page(cta_page)


# ── Requirement card ──────────────────────────────────────────────────────────

def req_card(req_id: str, text: str, req_type: str) -> None:
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


# ── Conflict card ─────────────────────────────────────────────────────────────

def conflict_card(conflict: dict, req_lookup: dict | None = None) -> None:
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
    ) if req_ids else '<span style="font-size:0.78rem;color:var(--text-tertiary);font-family:\'Inter\',sans-serif;">—</span>'

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

    with st.expander("Çelişki detayını görüntüle"):
        # Side-by-side view when requirement texts are available
        if req_lookup and req_ids:
            panes_html = '<div class="ar-conflict-detail">'
            for rid in req_ids:
                req_text = req_lookup.get(rid, "Gereksinim metni bulunamadı.")
                panes_html += (
                    f'<div class="ar-conflict-detail-pane">'
                    f'<div class="ar-conflict-detail-id">{rid}</div>'
                    f'<div class="ar-conflict-detail-text">{req_text}</div>'
                    f'</div>'
                )
            panes_html += "</div>"
            st.markdown(panes_html, unsafe_allow_html=True)

        st.markdown(
            f"""
<div class="ar-conflict-reason">
    <div class="ar-conflict-reason-label">Çelişki Açıklaması</div>
    <div class="ar-conflict-reason-text">{reason}</div>
</div>
""",
            unsafe_allow_html=True,
        )


# ── Gap card ──────────────────────────────────────────────────────────────────

def gap_card(gap: dict) -> None:
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


# ── Improvement diff card ─────────────────────────────────────────────────────

def improvement_diff_card(improvement: dict) -> None:
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
                f'color:var(--text-secondary);line-height:1.7;margin:0;">{reason}</p>',
                unsafe_allow_html=True,
            )


# ── Legacy helpers kept for compatibility ────────────────────────────────────

def priority_badge(priority: str) -> None:
    st.markdown(
        f'<span class="ar-badge ar-badge--low">{priority}</span>',
        unsafe_allow_html=True,
    )


def download_button(label: str, data: bytes, filename: str, mime: str) -> None:
    st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime,
        use_container_width=True,
    )
