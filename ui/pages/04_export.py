import streamlit as st
from pathlib import Path
from datetime import datetime
from ui.components import download_button, page_header, empty_state
from ui.i18n import t

page_header(
    title=t("export_title"),
    subtitle=t("export_subtitle"),
    step=4,
)

generated_dir = Path("outputs") / "generated"

report = st.session_state.get("analysis_report")
has_results = report is not None

if has_results:
    req_c = st.session_state.get("req_count", 0)
    conflict_c = st.session_state.get("conflict_count", 0)
    gap_c = st.session_state.get("gap_count", 0)
    improve_c = len(getattr(report, "improvements", []))

    st.markdown(
        f"""
<div style="display:flex;gap:0.75rem;margin-bottom:1.75rem;flex-wrap:wrap;">
  <div style="background:var(--bg-card);border:1px solid var(--border-subtle);border-radius:6px;
              padding:0.75rem 1.25rem;flex:1;min-width:100px;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;font-weight:700;
                color:var(--accent-primary);">{req_c}</div>
    <div style="font-family:'Inter',sans-serif;font-size:0.65rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em;color:var(--text-tertiary);
                margin-top:0.2rem;">{t("req_label")}</div>
  </div>
  <div style="background:var(--bg-card);border:1px solid var(--border-subtle);border-radius:6px;
              padding:0.75rem 1.25rem;flex:1;min-width:100px;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;font-weight:700;
                color:var(--color-danger);">{conflict_c}</div>
    <div style="font-family:'Inter',sans-serif;font-size:0.65rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em;color:var(--text-tertiary);
                margin-top:0.2rem;">{t("conflict_label")}</div>
  </div>
  <div style="background:var(--bg-card);border:1px solid var(--border-subtle);border-radius:6px;
              padding:0.75rem 1.25rem;flex:1;min-width:100px;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;font-weight:700;
                color:var(--color-warning);">{gap_c}</div>
    <div style="font-family:'Inter',sans-serif;font-size:0.65rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em;color:var(--text-tertiary);
                margin-top:0.2rem;">{t("gap_label")}</div>
  </div>
  <div style="background:var(--bg-card);border:1px solid var(--border-subtle);border-radius:6px;
              padding:0.75rem 1.25rem;flex:1;min-width:100px;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;font-weight:700;
                color:var(--color-info);">{improve_c}</div>
    <div style="font-family:'Inter',sans-serif;font-size:0.65rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em;color:var(--text-tertiary);
                margin-top:0.2rem;">{t("improvements_section")}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def _file_meta(path: Path) -> dict:
    stat = path.stat()
    size_kb = stat.st_size / 1024
    size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
    mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y %H:%M")
    return {"size": size_str, "date": mtime}


def _export_card(
    label: str,
    icon: str,
    path: Path | None,
    filename: str,
    mime: str,
    missing_msg: str,
    data: bytes | None = None,
) -> None:
    # If in-memory data is provided, use it
    if data is not None:
        size_kb = len(data) / 1024
        size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
        mtime = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        st.markdown(
            f"""
<div class="ar-export-card">
    <div class="ar-export-card-label">{icon} {label}</div>
""",
            unsafe_allow_html=True,
        )
        download_button(
            label=t("export_download_btn", filename=filename),
            data=data,
            filename=filename,
            mime=mime,
        )
        st.markdown(
            f"""
    <div class="ar-export-meta">
        <div class="ar-export-meta-item">
            <span class="ar-export-meta-key">{t("export_size")}</span>
            <span class="ar-export-meta-val">{size_str}</span>
        </div>
        <div class="ar-export-meta-item">
            <span class="ar-export-meta-key">{t("export_created")}</span>
            <span class="ar-export-meta-val">{mtime}</span>
        </div>
        <div class="ar-export-meta-item">
            <span class="ar-export-meta-key">{t("export_file")}</span>
            <span class="ar-export-meta-val">{filename} (In-Memory)</span>
        </div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
    # Otherwise, fall back to disk path check
    elif path and path.exists():
        meta = _file_meta(path)
        with open(path, "rb") as f:
            file_data = f.read()

        st.markdown(
            f"""
<div class="ar-export-card">
    <div class="ar-export-card-label">{icon} {label}</div>
""",
            unsafe_allow_html=True,
        )
        download_button(
            label=t("export_download_btn", filename=filename),
            data=file_data,
            filename=filename,
            mime=mime,
        )
        st.markdown(
            f"""
    <div class="ar-export-meta">
        <div class="ar-export-meta-item">
            <span class="ar-export-meta-key">{t("export_size")}</span>
            <span class="ar-export-meta-val">{meta['size']}</span>
        </div>
        <div class="ar-export-meta-item">
            <span class="ar-export-meta-key">{t("export_created")}</span>
            <span class="ar-export-meta-val">{meta['date']}</span>
        </div>
        <div class="ar-export-meta-item">
            <span class="ar-export-meta-key">{t("export_file")}</span>
            <span class="ar-export-meta-val">{path.name}</span>
        </div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="ar-export-card">'
            f'<div class="ar-export-card-label">{icon} {label}</div>',
            unsafe_allow_html=True,
        )
        st.warning(missing_msg)
        st.markdown("</div>", unsafe_allow_html=True)


if not has_results:
    empty_state(
        icon="📦",
        heading=t("export_empty_heading"),
        body=t("export_empty_body"),
        cta_label=t("export_go_analysis"),
        cta_page="ui/pages/02_analysis.py",
    )
else:
    st.markdown(
        f'<p class="ar-section-label">{t("export_section_label")}</p>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        pdf_files = list(generated_dir.glob("*.pdf")) if generated_dir.exists() else []
        pdf_path = sorted(pdf_files)[-1] if pdf_files else None
        _export_card(
            label=t("export_srs_label"),
            icon="📄",
            path=pdf_path,
            filename=pdf_path.name if pdf_path else "srs.pdf",
            mime="application/pdf",
            missing_msg=t("export_srs_missing"),
            data=st.session_state.get("srs_pdf"),
        )

        docx_path = generated_dir / "user_stories.docx"
        _export_card(
            label=t("export_stories_label"),
            icon="📝",
            path=docx_path if docx_path.exists() else None,
            filename="user_stories.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            missing_msg=t("export_stories_missing"),
            data=st.session_state.get("user_stories_docx"),
        )

    with col2:
        xlsx_path = generated_dir / "backlog.xlsx"
        _export_card(
            label=t("export_backlog_label"),
            icon="📊",
            path=xlsx_path if xlsx_path.exists() else None,
            filename="backlog.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            missing_msg=t("export_backlog_missing"),
            data=st.session_state.get("backlog_xlsx"),
        )

        json_path = generated_dir / "analysis_report.json"
        _export_card(
            label=t("export_json_label"),
            icon="🗂",
            path=json_path if json_path.exists() else None,
            filename="analysis_report.json",
            mime="application/json",
            missing_msg=t("export_json_missing"),
            data=st.session_state.get("analysis_report_json"),
        )
