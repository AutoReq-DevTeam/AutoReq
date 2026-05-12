"""
ui/i18n.py — Internationalization (EN/TR)
"""

import streamlit as st

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # Sidebar
        "api_active_openrouter": "Active — OpenRouter",
        "api_active_deepseek": "Active — DeepSeek",
        "api_active_gemini": "Active — Gemini",
        "api_undefined": "Not Configured",
        "system_status": "System Status",
        "api": "API",
        "cost": "Cost",
        "tokens": "Tokens",
        "analysis_summary": "Analysis Summary",
        "req_short": "Req.",
        "conflict_short": "Conflict",
        "gap_short": "Gap",
        "sb_req_help": "Go to requirements page",
        "sb_conflict_help": "Go to conflicts section",
        "sb_gap_help": "Go to gaps section",
        "demo_mode": "Demo Mode",
        "demo_mode_help": "Loads demo scenarios and enables presentation-friendly UI.",
        "demo_mode_active": "Demo Mode Active",
        "language_label": "Language",
        # Step labels
        "step_input": "Input",
        "step_analysis": "Analysis",
        "step_results": "Results",
        "step_export": "Export",
        # Page: Input
        "input_title": "Requirement Input",
        "input_subtitle": "Enter the requirement text to analyze or load a ready-made sample.",
        "demo_active_info": "Demo Mode active — demo scenarios added to the list.",
        "sample_select_placeholder": "— Select sample data —",
        "sample_load_label": "Load Sample Data",
        "sample_load_btn": "Load '{label}'",
        "sample_loaded_toast": "✓ {label} loaded.",
        "sample_read_error": "Could not read '{name}'.",
        "next_analysis_btn": "Next: Analysis →",
        "empty_text_error": "Please enter some text!",
        "invalid_req_error": (
            "The text does not look like a software requirements document. "
            "Please enter text containing requirement sentences such as "
            "'The user shall be able to log in.'"
        ),
        "file_upload_label": "Upload file (.txt, .docx, .pdf)",
        "file_loaded_toast": "✓ File uploaded and text extracted.",
        "text_area_label": "Enter requirement text:",
        "text_area_placeholder": (
            "Example: The user shall be able to log in. "
            "The user shall be able to reset their password."
        ),
        "empty_state_no_text_heading": "No text entered yet",
        "empty_state_no_text_body": (
            "Type your requirement text in the area above or upload a file. "
            "The system will analyze requirements and detect conflicts and gaps."
        ),
        # Page: Analysis
        "analysis_title": "Analysis",
        "analysis_subtitle": (
            "The entered text is analyzed by AI to detect requirements, conflicts, and gaps."
        ),
        "analysis_empty_heading": "No text entered yet",
        "analysis_empty_body": (
            "To start analysis, first add a requirement text from the Input page."
        ),
        "analysis_go_input": "Go to Input Page",
        "analysis_est_lines": (
            'Estimated <strong style="color:var(--text-secondary);">{count}</strong> '
            "requirement line(s) detected."
        ),
        "analysis_preview_info": "The following text will be analyzed:",
        "analysis_input_label": "Input Text",
        "analysis_start_btn": "Start Analysis",
        "analysis_started_toast": "Analysis started...",
        "analysis_preparing": "Preparing...",
        "analysis_status_starting": "Starting analysis...",
        "analysis_preprocessing": "Preprocessing text...",
        "analysis_done": "Completed.",
        "analysis_status_done": "Analysis complete.",
        "analysis_toast_done": (
            "✓ Analysis complete — {req_c} requirements, {conflict_c} conflicts, {gap_c} gaps"
        ),
        "req_label": "Requirements",
        "conflict_label": "Conflicts",
        "gap_label": "Gaps",
        "cost_label": "Cost",
        "analysis_error": (
            "Analysis completed but some AI operations encountered errors. "
            "Automatic redirect cancelled. Please review the errors above."
        ),
        "analysis_success": "Analysis completed successfully. Redirecting to results...",
        # Page: Results
        "results_title": "Analysis Results",
        "results_empty_heading": "No analysis performed yet",
        "results_empty_body": (
            "To see results, first start an analysis from the Analysis page."
        ),
        "results_go_analysis": "Go to Analysis Page",
        # Page: Export
        "export_title": "Export",
        "export_subtitle": "Download the generated outputs.",
        "export_section_label": "Export Files",
        "export_empty_heading": "No outputs generated yet",
        "export_empty_body": (
            "To create downloadable files, you need to run an analysis first."
        ),
        "export_go_analysis": "Go to Analysis Page",
        "export_srs_label": "SRS — Software Requirements Specification",
        "export_stories_label": "User Stories — Word",
        "export_backlog_label": "Product Backlog — Excel",
        "export_json_label": "Full Analysis Report — JSON",
        "export_download_btn": "Download — {filename}",
        "export_size": "Size",
        "export_created": "Created",
        "export_file": "File",
        "export_srs_missing": "SRS PDF output not found.",
        "export_stories_missing": "User Stories Word output not found.",
        "export_backlog_missing": "Backlog Excel output not found.",
        "export_json_missing": "JSON report output not found.",
        # Components
        "badge_functional": "Functional",
        "badge_nfr": "Non-Functional",
        "conflict_detail_expander": "View conflict details",
        "req_text_not_found": "Requirement text not found.",
        "conflict_reason_label": "Conflict Explanation",
        "conflict_reason_not_found": "Conflict explanation not found.",
        "diff_before_label": "Before",
        "diff_after_label": "Improved",
        "improvement_reason_expander": "View improvement rationale",
        "severity_high": "High",
        "severity_medium": "Medium",
        "severity_low": "Low",
        "gap_missing_area_not_found": "Missing area not specified.",
        "gap_suggestion_not_found": "No suggestion found.",
        "original_not_found": "Original statement not found.",
        "improved_not_found": "Improved statement not found.",
        "suggestion_prefix": "Suggestion: ",
        # Results page
        "tab_requirements": "Requirements",
        "tab_conflicts_gaps": "Conflicts & Gaps",
        "tab_improvements": "Improvement Suggestions",
        "req_section_label": "Parsed Requirements",
        "filter_all": "All",
        "filter_functional": "Functional",
        "filter_nfr": "Non-Functional",
        "req_empty_heading": "No requirements found",
        "req_empty_body": (
            "Could not extract requirements from the text. "
            "Please try a text with clearer requirement sentences."
        ),
        "total_conflicts_label": "Total Conflicts",
        "total_gaps_label": "Total Gaps",
        "conflicts_section": "Conflicts",
        "gaps_section": "Gaps",
        "no_conflicts_info": "No conflicts found.",
        "no_gaps_info": "No gaps found.",
        "improvements_section": "Improvement Suggestions",
        "improvements_empty_heading": "No improvement suggestions",
        "improvements_empty_body": (
            "All requirements appear clear and complete, "
            "or the LLM connection is not active."
        ),
    },
    "tr": {
        # Sidebar
        "api_active_openrouter": "Aktif — OpenRouter",
        "api_active_deepseek": "Aktif — DeepSeek",
        "api_active_gemini": "Aktif — Gemini",
        "api_undefined": "Tanımsız",
        "system_status": "Sistem Durumu",
        "api": "API",
        "cost": "Maliyet",
        "tokens": "Token",
        "analysis_summary": "Analiz Özeti",
        "req_short": "Gerek.",
        "conflict_short": "Çelişki",
        "gap_short": "Eksiklik",
        "sb_req_help": "Gereksinimler sayfasına git",
        "sb_conflict_help": "Çelişkiler bölümüne git",
        "sb_gap_help": "Eksiklikler bölümüne git",
        "demo_mode": "Demo Modu",
        "demo_mode_help": "Demo senaryolarını gösterir ve sunum dostu arayüzü etkinleştirir.",
        "demo_mode_active": "Demo Modu Aktif",
        "language_label": "Dil",
        # Step labels
        "step_input": "Girdi",
        "step_analysis": "Analiz",
        "step_results": "Sonuçlar",
        "step_export": "Dışa Aktarım",
        # Page: Input
        "input_title": "Gereksinim Girişi",
        "input_subtitle": "Analiz edilecek gereksinim metnini girin veya hazır bir örnek yükleyin.",
        "demo_active_info": "Demo Modu aktif — demo senaryoları listeye eklendi.",
        "sample_select_placeholder": "— Örnek veri seç —",
        "sample_load_label": "Örnek Veri Yükle",
        "sample_load_btn": "'{label}' dosyasını yükle",
        "sample_loaded_toast": "✓ {label} yüklendi.",
        "sample_read_error": "'{name}' dosyası okunamadı.",
        "next_analysis_btn": "İleri: Analiz →",
        "empty_text_error": "Lütfen metin gir!",
        "invalid_req_error": (
            "Girilen metin bir yazılım gereksinim belgesi gibi görünmüyor. "
            "Lütfen 'Kullanıcı sisteme giriş yapabilmeli.' gibi gereksinim "
            "cümleleri içeren bir metin girin."
        ),
        "file_upload_label": "Dosya yükle (.txt, .docx, .pdf)",
        "file_loaded_toast": "✓ Dosya yüklendi ve metin çıkarıldı.",
        "text_area_label": "Gereksinim metnini gir:",
        "text_area_placeholder": (
            "Örnek: Kullanıcı sisteme giriş yapabilmeli. "
            "Şifresini unuttuğunda sıfırlayabilmeli."
        ),
        "empty_state_no_text_heading": "Henüz metin girilmedi",
        "empty_state_no_text_body": (
            "Gereksinim metninizi yukarıdaki alana yazın veya bir dosya yükleyin. "
            "Sistem gereksinimleri analiz ederek çelişkileri ve eksiklikleri tespit eder."
        ),
        # Page: Analysis
        "analysis_title": "Analiz",
        "analysis_subtitle": (
            "Girilen metin yapay zeka ile analiz edilerek gereksinimler, "
            "çelişkiler ve eksiklikler tespit edilir."
        ),
        "analysis_empty_heading": "Henüz metin girmediniz",
        "analysis_empty_body": (
            "Analiz başlatmak için önce Girdi sayfasından gereksinim metni eklemeniz gerekiyor."
        ),
        "analysis_go_input": "Girdi Sayfasına Git",
        "analysis_est_lines": (
            'Tahmini <strong style="color:var(--text-secondary);">{count}</strong> '
            "gereksinim satırı tespit edildi."
        ),
        "analysis_preview_info": "Aşağıdaki metin analiz edilecektir:",
        "analysis_input_label": "Girdi Metni",
        "analysis_start_btn": "Analizi Başlat",
        "analysis_started_toast": "Analiz başladı...",
        "analysis_preparing": "Hazırlanıyor...",
        "analysis_status_starting": "Analiz başlatılıyor...",
        "analysis_preprocessing": "Metin ön işleniyor...",
        "analysis_done": "Tamamlandı.",
        "analysis_status_done": "Analiz tamamlandı.",
        "analysis_toast_done": (
            "✓ Analiz tamamlandı — {req_c} gereksinim, {conflict_c} çelişki, {gap_c} eksiklik"
        ),
        "req_label": "Gereksinim",
        "conflict_label": "Çelişki",
        "gap_label": "Eksiklik",
        "cost_label": "Maliyet",
        "analysis_error": (
            "Analiz tamamlandı fakat bazı AI işlemleri sırasında hatalar oluştu. "
            "Sonuç sayfasına otomatik yönlendirme iptal edildi. "
            "Lütfen yukarıdaki hataları inceleyin."
        ),
        "analysis_success": "Analiz başarıyla tamamlandı. Sonuçlara yönlendiriliyorsunuz...",
        # Page: Results
        "results_title": "Analiz Sonuçları",
        "results_empty_heading": "Henüz bir analiz yapılmadı",
        "results_empty_body": (
            "Sonuçları görmek için önce Analiz sayfasından bir analiz başlatın."
        ),
        "results_go_analysis": "Analiz Sayfasına Git",
        # Page: Export
        "export_title": "Dışa Aktarım",
        "export_subtitle": "Oluşturulan çıktıları indirin.",
        "export_section_label": "Dışa Aktarım Dosyaları",
        "export_empty_heading": "Henüz çıktı oluşturulmadı",
        "export_empty_body": (
            "İndirilebilir dosyalar oluşturmak için önce bir analiz çalıştırmanız gerekiyor."
        ),
        "export_go_analysis": "Analiz Sayfasına Git",
        "export_srs_label": "SRS — Yazılım Gereksinimleri Belgesi",
        "export_stories_label": "Kullanıcı Hikayeleri — Word",
        "export_backlog_label": "Ürün Geliş Günlüğü — Excel",
        "export_json_label": "Tam Analiz Raporu — JSON",
        "export_download_btn": "İndir — {filename}",
        "export_size": "Boyut",
        "export_created": "Oluşturulma",
        "export_file": "Dosya",
        "export_srs_missing": "SRS PDF çıktısı bulunamadı.",
        "export_stories_missing": "User Stories Word çıktısı bulunamadı.",
        "export_backlog_missing": "Backlog Excel çıktısı bulunamadı.",
        "export_json_missing": "JSON rapor çıktısı bulunamadı.",
        # Components
        "badge_functional": "Fonksiyonel",
        "badge_nfr": "Fonksiyonel Olmayan",
        "conflict_detail_expander": "Çelişki detayını görüntüle",
        "req_text_not_found": "Gereksinim metni bulunamadı.",
        "conflict_reason_label": "Çelişki Açıklaması",
        "conflict_reason_not_found": "Çelişki açıklaması bulunamadı.",
        "diff_before_label": "Önceki",
        "diff_after_label": "İyileştirilmiş",
        "improvement_reason_expander": "İyileştirme gerekçesini görüntüle",
        "severity_high": "Yüksek",
        "severity_medium": "Orta",
        "severity_low": "Düşük",
        "gap_missing_area_not_found": "Eksik alan belirtilmemiş.",
        "gap_suggestion_not_found": "Öneri bulunamadı.",
        "original_not_found": "Önceki ifade bulunamadı.",
        "improved_not_found": "İyileştirilmiş ifade bulunamadı.",
        "suggestion_prefix": "Öneri: ",
        # Results page
        "tab_requirements": "Gereksinimler",
        "tab_conflicts_gaps": "Çelişkiler & Eksiklikler",
        "tab_improvements": "İyileştirme Önerileri",
        "req_section_label": "Ayrıştırılan Gereksinimler",
        "filter_all": "Tümü",
        "filter_functional": "Fonksiyonel",
        "filter_nfr": "Fonksiyonel Olmayan",
        "req_empty_heading": "Gereksinim bulunamadı",
        "req_empty_body": (
            "Metinden gereksinim çıkarılamadı. "
            "Lütfen daha açık gereksinim cümleleri içeren bir metin deneyin."
        ),
        "total_conflicts_label": "Toplam Çelişki",
        "total_gaps_label": "Toplam Eksiklik",
        "conflicts_section": "Çelişkiler",
        "gaps_section": "Eksiklikler",
        "no_conflicts_info": "Çelişki bulunamadı.",
        "no_gaps_info": "Eksiklik bulunamadı.",
        "improvements_section": "İyileştirme Önerileri",
        "improvements_empty_heading": "İyileştirme önerisi yok",
        "improvements_empty_body": (
            "Tüm gereksinimler yeterince açık ve eksiksiz görünüyor, "
            "ya da LLM bağlantısı etkin değil."
        ),
    },
}

_LANG_OPTIONS = {"English": "en", "Türkçe": "tr"}
_LANG_DISPLAY = {v: k for k, v in _LANG_OPTIONS.items()}


def get_lang() -> str:
    return st.session_state.get("language", "en")


def t(key: str, **kwargs) -> str:
    lang = get_lang()
    texts = _TRANSLATIONS.get(lang, _TRANSLATIONS["en"])
    text = texts.get(key, _TRANSLATIONS["en"].get(key, key))
    return text.format(**kwargs) if kwargs else text


def lang_selector_sidebar() -> None:
    """Render a compact language selector at the bottom of the sidebar."""
    current = get_lang()
    options = list(_LANG_OPTIONS.keys())
    current_display = _LANG_DISPLAY.get(current, "English")
    selected = st.sidebar.selectbox(
        t("language_label"),
        options,
        index=options.index(current_display),
        key="language_selector",
        label_visibility="visible",
    )
    chosen_code = _LANG_OPTIONS[selected]
    if chosen_code != current:
        st.session_state["language"] = chosen_code
        st.rerun()
