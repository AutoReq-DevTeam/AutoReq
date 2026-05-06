import streamlit as st
from pathlib import Path
from ui.file_loader import extract_text_from_upload

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
    """Metnin bir yazılım gereksinim belgesi olup olmadığını buluşsal olarak kontrol eder."""
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

st.markdown('<div class="ar-title-bar"></div>', unsafe_allow_html=True)
st.title("Gereksinim Girişi")
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;font-size:0.875rem;color:#666666;'
    'margin-top:-0.75rem;margin-bottom:1.5rem;">Analiz edilecek gereksinim metnini '
    'girin veya hazır bir örnek yükleyin.</p>',
    unsafe_allow_html=True,
)
if demo_mode:
    st.info("Demo Modu aktif — demo senaryoları listeye eklendi.")

# Örnek Veri Yükle — yalnızca Demo Modu açıkken gösterilir
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
        label_list = ["— Örnek veri seç —"] + list(options.keys())
        selected_label = st.selectbox(
            "Örnek Veri Yükle",
            label_list,
            index=0,
            key="sample_selector",
            help="data/samples/ ve data/demo_scenarios/ dosyalarını listeler.",
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

if st.button("İleri: Analiz", type="primary", use_container_width=True):
    raw = st.session_state.user_input.strip()
    if not raw:
        st.error("Lütfen metin gir!")
    elif not _is_requirements_text(raw):
        st.error(
            "Girilen metin bir yazılım gereksinim belgesi gibi görünmüyor. "
            "Lütfen 'Kullanıcı sisteme giriş yapabilmeli.' gibi gereksinim cümleleri içeren bir metin girin."
        )
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
