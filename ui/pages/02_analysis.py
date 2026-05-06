import streamlit as st
from core.pipeline import process_text
from ui.state import update_counts
from ui.components import page_header, empty_state

page_header(
    title="Analiz",
    subtitle="Girilen metin yapay zeka ile analiz edilerek gereksinimler, çelişkiler ve eksiklikler tespit edilir.",
    step=2,
)

if "user_input" not in st.session_state or not st.session_state.user_input.strip():
    empty_state(
        icon="📝",
        heading="Henüz metin girmediniz",
        body="Analiz başlatmak için önce Girdi sayfasından gereksinim metni eklemeniz gerekiyor.",
        cta_label="Girdi Sayfasına Git",
        cta_page="ui/pages/01_input.py",
    )
else:
    raw_text = st.session_state.user_input

    # Estimate requirement count before running
    _lines = [ln.strip() for ln in raw_text.split("\n") if len(ln.strip()) > 15]
    est_count = max(1, len(_lines))

    st.markdown(
        f'<p style="font-family:\'Inter\',sans-serif;font-size:0.875rem;'
        f'color:var(--text-tertiary);margin-bottom:0.75rem;">'
        f'Tahmini <strong style="color:var(--text-secondary);">{est_count}</strong> gereksinim satırı tespit edildi.</p>',
        unsafe_allow_html=True,
    )

    st.info("Aşağıdaki metin analiz edilecektir:")
    st.text_area("Girdi Metni", value=raw_text, height=150, disabled=True)

    if st.button("Analizi Başlat", type="primary", use_container_width=True):
        st.toast("Analiz başladı...")

        progress_bar = st.progress(0, text="Hazırlanıyor...")

        status = st.status("Analiz başlatılıyor...", expanded=True)

        progress_bar.progress(15, text="Metin ön işleniyor...")
        st.session_state.analysis_report = process_text(raw_text, status_ui=status)
        progress_bar.progress(100, text="Tamamlandı.")

        update_counts()
        status.update(label="Analiz tamamlandı.", state="complete", expanded=False)

        req_c = st.session_state.get("req_count", 0)
        conflict_c = st.session_state.get("conflict_count", 0)
        gap_c = st.session_state.get("gap_count", 0)
        cost = st.session_state.get("total_cost_usd", 0.0)

        st.toast(
            f"✓ Analiz tamamlandı — {req_c} gereksinim, {conflict_c} çelişki, {gap_c} eksiklik"
        )

        st.markdown(
            f"""
<div style="display:flex;gap:1rem;margin:1rem 0;flex-wrap:wrap;">
  <div style="background:var(--bg-card);border:1px solid var(--border-subtle);border-left:3px solid var(--accent-primary);
              border-radius:6px;padding:0.75rem 1.25rem;flex:1;min-width:120px;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;font-weight:700;
                color:var(--accent-primary);line-height:1;">{req_c}</div>
    <div style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em;color:var(--text-tertiary);
                margin-top:0.25rem;">Gereksinim</div>
  </div>
  <div style="background:var(--bg-card);border:1px solid var(--border-subtle);border-left:3px solid var(--color-danger);
              border-radius:6px;padding:0.75rem 1.25rem;flex:1;min-width:120px;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;font-weight:700;
                color:var(--color-danger);line-height:1;">{conflict_c}</div>
    <div style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em;color:var(--text-tertiary);
                margin-top:0.25rem;">Çelişki</div>
  </div>
  <div style="background:var(--bg-card);border:1px solid var(--border-subtle);border-left:3px solid var(--color-warning);
              border-radius:6px;padding:0.75rem 1.25rem;flex:1;min-width:120px;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;font-weight:700;
                color:var(--color-warning);line-height:1;">{gap_c}</div>
    <div style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em;color:var(--text-tertiary);
                margin-top:0.25rem;">Eksiklik</div>
  </div>
  <div style="background:var(--bg-card);border:1px solid var(--border-subtle);border-left:3px solid var(--color-info);
              border-radius:6px;padding:0.75rem 1.25rem;flex:1;min-width:120px;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;font-weight:700;
                color:var(--color-info);line-height:1;">${cost:.4f}</div>
    <div style="font-family:'Inter',sans-serif;font-size:0.68rem;font-weight:600;
                text-transform:uppercase;letter-spacing:0.1em;color:var(--text-tertiary);
                margin-top:0.25rem;">Maliyet</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        if st.session_state.get("pipeline_warnings"):
            st.error("Analiz tamamlandı fakat bazı AI işlemleri sırasında hatalar oluştu. Sonuç sayfasına otomatik yönlendirme iptal edildi. Lütfen yukarıdaki hataları inceleyin.")
            # Clear warnings so they don't block next time
            st.session_state["pipeline_warnings"] = []
        else:
            st.success("Analiz başarıyla tamamlandı. Sonuçlara yönlendiriliyorsunuz...")
            st.switch_page("ui/pages/03_results.py")
