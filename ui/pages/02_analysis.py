import streamlit as st
from core.pipeline import process_text
from ui.state import update_counts

st.title("Analiz")

if "user_input" not in st.session_state or not st.session_state.user_input.strip():
    st.warning("Henüz metin girmediniz. Lütfen Girdi sayfasına dönün.")
    if st.button("Girdi Sayfasına Git"):
        st.switch_page("ui/pages/01_input.py")
else:
    st.info("Aşağıdaki metin analiz edilecektir:")
    st.text_area("Girdi Metni", value=st.session_state.user_input, height=150, disabled=True)

    if st.button("Analizi Başlat", type="primary", use_container_width=True):
        st.toast("Analiz başladı.")
        
        status = st.status("Analiz başlatılıyor...", expanded=True)
        st.session_state.analysis_report = process_text(st.session_state.user_input, status_ui=status)
        update_counts() # Sidebar metricleri icin count guncelle
        status.update(label="Analiz tamamlandı.", state="complete", expanded=False)
        
        st.success("Analiz başarıyla tamamlandı. Sonuçlara yönlendiriliyorsunuz...")
        st.switch_page("ui/pages/03_results.py")
