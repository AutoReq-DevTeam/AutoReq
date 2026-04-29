import streamlit as st
from pathlib import Path
from ui.file_loader import extract_text_from_upload

_SAMPLES_DIR = Path(__file__).parent.parent.parent / "data" / "samples"

_SAMPLE_LABELS: dict[str, str] = {
    "ornek_eticaret.txt": "E-Ticaret",
    "ornek_bankacilik.txt": "Bankacılık",
    "ornek_egitim.txt": "Eğitim Platformu",
    "ornek_gereksinim.txt": "Genel Örnek",
}

def _set_input(text):
    st.session_state.user_input = text
    st.session_state._input_widget = text

st.title("Girdi")
st.subheader("Gereksinim Metnini Yükleyin")

# Sample Loader
sample_files = sorted(_SAMPLES_DIR.glob("*.txt")) if _SAMPLES_DIR.exists() else []
if sample_files:
    options = {_SAMPLE_LABELS.get(f.name, f"{f.stem}"): f for f in sample_files}
    label_list = ["— Örnek veri seç —"] + list(options.keys())
    
    selected_label = st.selectbox(
        "Örnek Veri Yükle",
        label_list,
        index=0,
        key="sample_selector",
        help="data/samples/ klasöründen hazır gereksinim metinlerini yükleyin.",
    )
    
    if selected_label != "— Örnek veri seç —":
        sample_path = options[selected_label]
        try:
            content = sample_path.read_text(encoding="utf-8")
            if st.button(f"'{selected_label}' dosyasını yükle", key="load_sample_btn"):
                _set_input(content)
                st.toast(f"{selected_label} yüklendi.")
                st.rerun()
        except OSError:
            st.warning(f"'{sample_path.name}' dosyası okunamadı.")

col1, col2 = st.columns(2)

with col1:
    if st.button("Demo Verisi", use_container_width=True):
        _set_input(
            "Kullanıcı sisteme kayıt olabilmeli.\n"
            "Şifresini sıfırlayabilmeli.\n"
            "Admin kullanıcıları yönetebilmeli."
        )
        st.toast("Demo metni yüklendi.")
        st.rerun()

with col2:
    if st.button("İleri: Analiz", type="primary", use_container_width=True):
        if not st.session_state.user_input.strip():
            st.error("Lütfen metin gir!")
        else:
            st.switch_page("ui/pages/02_analysis.py")

uploaded_file = st.file_uploader(
    "Dosya yükle (.txt, .docx, .pdf)",
    type=["txt", "docx", "pdf"],
)

if uploaded_file is not None:
    try:
        extracted_text = extract_text_from_upload(uploaded_file)
        _set_input(extracted_text)
        st.toast("Dosya yüklendi ve metin çıkarıldı.")
    except ValueError as e:
        st.error(str(e))

def _sync_input():
    st.session_state.user_input = st.session_state._input_widget

text_val = st.text_area(
    label="Gereksinim metnini gir:",
    placeholder="Örnek: Kullanıcı sisteme giriş yapabilmeli. Şifresini unuttuğunda sıfırlayabilmeli.",
    height=220,
    key="_input_widget",
    value=st.session_state.get("user_input", ""),
    on_change=_sync_input
)

if text_val != st.session_state.get("user_input", ""):
    st.session_state.user_input = text_val
