import streamlit as st
from pathlib import Path
from ui.components import download_button

st.markdown('<div class="ar-title-bar"></div>', unsafe_allow_html=True)
st.title("Dışa Aktarım")
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;font-size:0.875rem;color:#666666;'
    'margin-top:-0.75rem;margin-bottom:1.5rem;">Oluşturulan çıktıları indirin.</p>',
    unsafe_allow_html=True,
)

generated_dir = Path("outputs") / "generated"

col1, col2 = st.columns(2)

with col1:
    # SRS PDF
    pdf_files = list(generated_dir.glob("*.pdf"))
    if pdf_files:
        pdf_path = sorted(pdf_files)[-1]
        with open(pdf_path, "rb") as f:
            download_button(
                label=f"SRS PDF ({pdf_path.name})",
                data=f.read(),
                filename=pdf_path.name,
                mime="application/pdf",
            )
    else:
        st.warning("SRS PDF çıktısı bulunamadı.")

    # User Stories DOCX
    docx_path = generated_dir / "user_stories.docx"
    if docx_path.exists():
        with open(docx_path, "rb") as f:
            download_button(
                label="User Stories (Word)",
                data=f.read(),
                filename="user_stories.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
    else:
        st.warning("User Stories Word çıktısı bulunamadı.")

with col2:
    # Backlog XLSX
    xlsx_path = generated_dir / "backlog.xlsx"
    if xlsx_path.exists():
        with open(xlsx_path, "rb") as f:
            download_button(
                label="Product Backlog (Excel)",
                data=f.read(),
                filename="backlog.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
    else:
        st.warning("Backlog Excel çıktısı bulunamadı.")

    # Report JSON
    json_path = generated_dir / "analysis_report.json"
    if json_path.exists():
        with open(json_path, "rb") as f:
            download_button(
                label="Tam Analiz Raporu (JSON)",
                data=f.read(),
                filename="analysis_report.json",
                mime="application/json",
            )
    else:
        st.warning("JSON rapor çıktısı bulunamadı.")
