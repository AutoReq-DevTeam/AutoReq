"""
ui/components.py — Shared UI Components
"""

import html
import streamlit as st
from ui.i18n import t


# ── Step indicator + page header ─────────────────────────────────────────────

def page_header(title: str, subtitle: str = "", step: int = 1) -> None:
    steps = [t("step_input"), t("step_analysis"), t("step_results"), t("step_export")]

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
            f'{html.escape(subtitle)}</p>',
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
    st.markdown(
        f"""
<div class="ar-empty-state">
    <div class="ar-empty-state-icon">{html.escape(icon)}</div>
    <div class="ar-empty-state-title">{html.escape(heading)}</div>
    <div class="ar-empty-state-body">{html.escape(body)}</div>
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
    badge_lbl = t("badge_functional") if is_func else t("badge_nfr")
    card_mod = "" if is_func else " ar-req-card--nfr"

    escaped_id = html.escape(req_id)
    escaped_text = html.escape(text)

    st.markdown(
        f"""
<div class="ar-req-card{card_mod}">
    <div style="display:flex;align-items:center;flex-wrap:wrap;gap:0.25rem;margin-bottom:0.1rem;">
        <span class="{badge_cls}">{badge_lbl}</span>
        <span class="ar-req-id">{escaped_id}</span>
    </div>
    <div class="ar-req-text">{escaped_text}</div>
</div>
""",
        unsafe_allow_html=True,
    )


# ── Conflict card ─────────────────────────────────────────────────────────────

def conflict_card(conflict: dict, req_lookup: dict | None = None) -> None:
    severity = str(conflict.get("severity", "medium")).upper()
    req_ids = conflict.get("req_ids", [])
    reason = conflict.get("reason", t("conflict_reason_not_found"))
    conflict_type = conflict.get("conflict_type", "")

    sev_map = {
        "HIGH":   ("ar-badge ar-badge--high",   t("severity_high"),   ""),
        "MEDIUM": ("ar-badge ar-badge--medium",  t("severity_medium"), " ar-conflict-card--medium"),
        "LOW":    ("ar-badge ar-badge--low",     t("severity_low"),    " ar-conflict-card--low"),
    }
    badge_cls, badge_lbl, card_mod = sev_map.get(severity, sev_map["MEDIUM"])

    escaped_type = html.escape(conflict_type)
    escaped_reason = html.escape(reason)

    req_links_html = " ".join(
        f'<a class="ar-req-link" href="#{html.escape(rid)}">{html.escape(rid)}</a>' for rid in req_ids
    ) if req_ids else '<span style="font-size:0.78rem;color:var(--text-tertiary);font-family:\'Inter\',sans-serif;">—</span>'

    st.markdown(
        f"""
<div class="ar-conflict-card{card_mod}">
    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem;">
        <span class="{badge_cls}">{badge_lbl}</span>
        <span class="ar-conflict-title">{escaped_type}</span>
    </div>
    <div style="margin-bottom:0.25rem;">{req_links_html}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.expander(t("conflict_detail_expander")):
        if req_lookup and req_ids:
            panes_html = '<div class="ar-conflict-detail">'
            for rid in req_ids:
                req_text = req_lookup.get(rid, t("req_text_not_found"))
                escaped_rid = html.escape(rid)
                escaped_req_text = html.escape(req_text)
                panes_html += (
                    f'<div class="ar-conflict-detail-pane">'
                    f'<div class="ar-conflict-detail-id">{escaped_rid}</div>'
                    f'<div class="ar-conflict-detail-text">{escaped_req_text}</div>'
                    f'</div>'
                )
            panes_html += "</div>"
            st.markdown(panes_html, unsafe_allow_html=True)

        st.markdown(
            f"""
<div class="ar-conflict-reason">
    <div class="ar-conflict-reason-label">{t("conflict_reason_label")}</div>
    <div class="ar-conflict-reason-text">{escaped_reason}</div>
</div>
""",
            unsafe_allow_html=True,
        )


# ── Gap card ──────────────────────────────────────────────────────────────────

def gap_card(gap: dict) -> None:
    import hashlib

    scenario = gap.get("scenario", "unknown")
    missing_area = gap.get("missing_area", t("gap_missing_area_not_found"))
    suggestion = gap.get("suggestion", t("gap_suggestion_not_found"))
    severity = str(gap.get("severity", "medium")).upper()

    sev_map = {
        "HIGH":   ("ar-badge ar-badge--high",   t("severity_high"),   ""),
        "MEDIUM": ("ar-badge ar-badge--medium",  t("severity_medium"), ""),
        "LOW":    ("ar-badge ar-badge--low",     t("severity_low"),    " ar-gap-card--low"),
    }
    badge_cls, badge_lbl, card_mod = sev_map.get(severity, sev_map["MEDIUM"])

    escaped_scenario = html.escape(scenario)
    escaped_missing_area = html.escape(missing_area)

    _raw_key = f"gap_{scenario}_{missing_area}_{suggestion}"
    _stable_key = "gap_" + hashlib.md5(_raw_key.encode("utf-8")).hexdigest()[:12]

    st.markdown(
        f"""
<div class="ar-gap-card{card_mod}">
    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.4rem;">
        <span class="{badge_cls}">{badge_lbl}</span>
        <span class="ar-gap-title">{escaped_scenario}</span>
    </div>
    <div class="ar-gap-area">{escaped_missing_area}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.checkbox(
        f"{t('suggestion_prefix')}{suggestion}",
        value=False,
        key=_stable_key,
    )


# ── Improvement diff card ─────────────────────────────────────────────────────

def improvement_diff_card(improvement: dict) -> None:
    original = improvement.get("original", t("original_not_found"))
    improved = improvement.get("improved", t("improved_not_found"))
    reason = improvement.get("reason", "")

    escaped_original = html.escape(original)
    escaped_improved = html.escape(improved)
    escaped_reason = html.escape(reason)

    st.markdown(
        f"""
<div class="ar-diff-wrap">
    <div class="ar-diff-header">
        <div class="ar-diff-col">
            <span class="ar-diff-label">{t("diff_before_label")}</span>
        </div>
        <div class="ar-diff-col">
            <span class="ar-diff-label">{t("diff_after_label")}</span>
        </div>
    </div>
    <div class="ar-diff-body">
        <div class="ar-diff-before">{escaped_original}</div>
        <div class="ar-diff-after">{escaped_improved}</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if reason:
        with st.expander(t("improvement_reason_expander")):
            st.markdown(
                f'<p style="font-family:\'Inter\',sans-serif;font-size:0.875rem;'
                f'color:var(--text-secondary);line-height:1.7;margin:0;">{escaped_reason}</p>',
                unsafe_allow_html=True,
            )


# ── Legacy helpers kept for compatibility ────────────────────────────────────

def priority_badge(priority: str) -> None:
    st.markdown(
        f'<span class="ar-badge ar-badge--low">{html.escape(priority)}</span>',
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
