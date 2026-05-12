import streamlit as st
from pathlib import Path
from ui.file_loader import extract_text_from_upload
from ui.components import page_header, empty_state
from ui.i18n import t

_DATA_ROOT = Path(__file__).parent.parent.parent / "data"
_SAMPLES_DIR = _DATA_ROOT / "samples"
_DEMO_DIR = _DATA_ROOT / "demo_scenarios"

_SAMPLE_LABELS: dict[str, str] = {
    "ornek_eticaret.txt": "E-Ticaret",
    "ornek_bankacilik.txt": "Bankacılık",
    "ornek_egitim.txt": "Eğitim Platformu",
    "ornek_gereksinim.txt": "Genel Örnek",
}

_DEMO_LABELS: dict[str, str] = {
    "01_e_ticaret_celisma.txt": "Demo: E-Ticaret (Çelişki)",
    "02_bankacilik_eksik.txt": "Demo: Bankacılık (Eksik Gereksinim)",
    "03_egitim_mughrak.txt": "Demo: Eğitim (Muğlak NFR)",
    "04_kurumsal_portal_multi_actor.txt": "Demo: Kurumsal Portal (Çok Aktör)",
    "05_mobil_app_nfr_agirlikli.txt": "Demo: Mobil App (NFR Ağırlıklı)",
}

_TR_REQ_MARKERS: frozenset = frozenset({
    "meli", "malı", "bilmeli", "gerekli", "gereksinim",
    "zorunlu", "yapılmalı", "edilmeli", "sağlamalı",
    "erişebilmeli", "görebilmeli", "yönetebilmeli",
    "kullanabilmeli", "gönderebilmeli", "silinebilmeli",
    "oluşturabilmeli", "güncelleyebilmeli", "görüntüleyebilmeli",
})
_EN_REQ_MARKERS: frozenset = frozenset({
    "must", "shall", "should", "required", "requirement",
    "the system", "user shall", "will be able",
})
_ALL_REQ_MARKERS = _TR_REQ_MARKERS | _EN_REQ_MARKERS


def _is_requirements_text(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) < 20:
        return False
    if len(stripped.split()) < 4:
        return False
    lower = stripped.lower()
    return any(marker in lower for marker in _ALL_REQ_MARKERS)


def _set_input(text: str) -> None:
    st.session_state.user_input = text
    st.session_state._input_widget = text


demo_mode = st.session_state.get("demo_mode", False)

page_header(
    title=t("input_title"),
    subtitle=t("input_subtitle"),
    step=1,
)

if demo_mode:
    st.info(t("demo_active_info"))

# Sample loader — only in demo mode
if demo_mode:
    options: dict[str, Path] = {}
    if _SAMPLES_DIR.exists():
        for f in sorted(_SAMPLES_DIR.glob("*.txt")):
            label = _SAMPLE_LABELS.get(f.name, f.stem)
            options[label] = f

    if _DEMO_DIR.exists():
        for f in sorted(_DEMO_DIR.glob("*.txt")):
            label = _DEMO_LABELS.get(f.name, f"Demo: {f.stem}")
            options[label] = f

    if options:
        placeholder = t("sample_select_placeholder")
        label_list = [placeholder] + list(options.keys())
        selected_label = st.selectbox(
            t("sample_load_label"),
            label_list,
            index=0,
            key="sample_selector",
            help="data/samples/ ve data/demo_scenarios/ dosyalarını listeler.",
        )

        if selected_label != placeholder:
            sample_path = options[selected_label]
            try:
                content = sample_path.read_text(encoding="utf-8")
                if st.button(t("sample_load_btn").format(label=selected_label), key="load_sample_btn"):
                    _set_input(content)
                    st.toast(t("sample_loaded_toast").format(label=selected_label))
                    st.rerun()
            except OSError:
                st.warning(t("sample_read_error").format(name=sample_path.name))

if st.button(t("next_analysis_btn"), type="primary", use_container_width=True):
    raw = st.session_state.user_input.strip()
    if not raw:
        st.error(t("empty_text_error"))
    elif not _is_requirements_text(raw):
        st.error(t("invalid_req_error"))
    else:
        st.switch_page("ui/pages/02_analysis.py")

uploaded_file = st.file_uploader(
    t("file_upload_label"),
    type=["txt", "docx", "pdf"],
)

if uploaded_file is not None:
    try:
        extracted_text = extract_text_from_upload(uploaded_file)
        _set_input(extracted_text)
        st.toast(t("file_loaded_toast"))
    except ValueError as e:
        st.error(str(e))


def _sync_input():
    st.session_state.user_input = st.session_state._input_widget


text_val = st.text_area(
    label=t("text_area_label"),
    placeholder=t("text_area_placeholder"),
    height=220,
    key="_input_widget",
    value=st.session_state.get("user_input", ""),
    on_change=_sync_input,
)

if text_val != st.session_state.get("user_input", ""):
    st.session_state.user_input = text_val

if not st.session_state.get("user_input", "").strip():
    empty_state(
        icon="📋",
        heading=t("empty_state_no_text_heading"),
        body=t("empty_state_no_text_body"),
    )
