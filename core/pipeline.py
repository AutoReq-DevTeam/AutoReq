"""
core/pipeline.py — Analiz Orkestrasyonu
"""

import os
import streamlit as st
from loguru import logger
import concurrent.futures

from core.models import AnalysisReport
from core.preprocessor import TextPreprocessor
from core.classifier import RequirementClassifier
from core.ner import EntityRecognizer
from core.priority_detector import PriorityDetector
from modules.conflict_detector import ConflictDetector
from modules.gap_analyzer import GapAnalyzer
from modules.improver import RequirementImprover
from modules.llm_client import LLMClientError, flush_usage_to_session, set_thread_session_id

from outputs.srs_generator import generate_srs
from outputs.story_generator import StoryGenerator
from outputs.bdd_generator import BDDGenerator
from outputs.backlog_generator import BacklogGenerator
from outputs.exporters import export_backlog_xlsx, export_stories_docx, export_report_json

_log = logger.bind(module="pipeline")

@st.cache_resource(show_spinner="Yapay Zeka Modelleri Belleğe Yükleniyor... (İlk açılışta biraz sürebilir)")
def load_nlp_pipeline():
    return {
        "preprocessor": TextPreprocessor(),
        "classifier": RequirementClassifier(),
        "ner": EntityRecognizer(),
        "priority_detector": PriorityDetector(),
    }

nlp_engines = load_nlp_pipeline()

def _is_llm_available() -> bool:
    return bool(os.getenv("OPENROUTER_API_KEY"))

def process_text(raw_text: str, status_ui=None) -> AnalysisReport:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    ctx = get_script_run_ctx()
    session_id = ctx.session_id if ctx else None

    if status_ui: status_ui.update(label="Stanza ile ön işleme yapılıyor...")
    parsed_doc = nlp_engines["preprocessor"].process(raw_text)

    for req in parsed_doc.requirements:
        req = nlp_engines["classifier"].classify(req)
        req = nlp_engines["ner"].recognize(req)
        req = nlp_engines["priority_detector"].detect(req)

    if not parsed_doc.requirements:
        raise ValueError(
            "Metinden hiçbir gereksinim çıkarılamadı. "
            "Lütfen yazılım gereksinim cümleleri içeren bir metin girin."
        )

    conflicts = []
    gaps = []
    improvements = []
    if _is_llm_available():
        # 1. Run improvements synchronously first so other analyzers and output generators use improved text
        try:
            _log.info("LLM ile gereksinim iyileştirme toplu başlatılıyor...")
            improver = RequirementImprover()
            results = improver.improve_batch(parsed_doc.requirements)
            for req, res in zip(parsed_doc.requirements, results):
                original = res.get("original", "").strip()
                improved = res.get("improved", "").strip()
                req.original_text = original
                if improved and improved != original:
                    req.text = improved
                    improvements.append(res)
            _log.info("Gereksinim iyileştirme tamamlandı | improvements={}", len(improvements))
        except (LLMClientError, ValueError) as exc:
            _log.warning("Gereksinim iyileştirme başarısız | hata={}", exc)
            if "pipeline_warnings" not in st.session_state:
                st.session_state["pipeline_warnings"] = []
            st.session_state["pipeline_warnings"].append(f"Gereksinim İyileştirme: {exc}")

        # 2. Run conflicts and gaps in parallel on the improved requirements
        _log.info("LLM ile çelişki ve eksiklik analizi paralel başlatılıyor...")
        if status_ui: status_ui.update(label="LLM ile çelişki ve eksiklik analizi yapılıyor...")

        def _run_conflicts():
            if session_id:
                set_thread_session_id(session_id)
            return ConflictDetector().analyze(parsed_doc)

        def _run_gaps():
            if session_id:
                set_thread_session_id(session_id)
            return GapAnalyzer().analyze(parsed_doc)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            fut_conflicts = ex.submit(_run_conflicts)
            fut_gaps = ex.submit(_run_gaps)

            if "pipeline_warnings" not in st.session_state:
                st.session_state["pipeline_warnings"] = []

            try:
                conflicts = fut_conflicts.result()
                _log.info("Çelişki analizi tamamlandı | conflicts={}", len(conflicts))
            except (LLMClientError, ValueError) as exc:
                _log.warning("Çelişki analizi başarısız — boş liste ile devam ediliyor | hata={}", exc)
                st.warning(f"⚠️ Çelişki analizi tamamlanamadı: {exc}")
                st.session_state["pipeline_warnings"].append(f"Çelişki Analizi: {exc}")
                conflicts = []

            try:
                gaps = fut_gaps.result()
                _log.info("Eksiklik analizi tamamlandı | gaps={}", len(gaps))
            except (LLMClientError, ValueError) as exc:
                _log.warning("Eksiklik analizi başarısız — boş liste ile devam ediliyor | hata={}", exc)
                st.warning(f"⚠️ Eksiklik analizi tamamlanamadı: {exc}")
                st.session_state["pipeline_warnings"].append(f"Eksiklik Analizi: {exc}")
                gaps = []
    else:
        _log.info("API key tanımlı değil — çelişki ve eksiklik analizi atlanıyor.")

    flush_usage_to_session()

    report = AnalysisReport(
        parsed_doc=parsed_doc.model_dump(),
        conflicts=conflicts,
        gaps=gaps,
        improvements=improvements,
    )

    _log.info("Paralel çıktı üretimi başlatılıyor...")
    if status_ui: status_ui.update(label="Paralel belge üretimi yapılıyor...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        def gen_srs():
            if session_id:
                set_thread_session_id(session_id)
            try:
                pdf_buf = generate_srs(report, in_memory=True)
                return pdf_buf.getvalue(), None
            except Exception as e1:
                try:
                    generate_srs(report)
                    return None, None
                except Exception as e2:
                    _log.error("SRS üretimi hatası: {}", e2)
                    return None, f"SRS Belgesi Üretimi: {e2}"

        def gen_backlog():
            if session_id:
                set_thread_session_id(session_id)
            try:
                backlog = BacklogGenerator().generate(report)
                xlsx_buf = export_backlog_xlsx(backlog, in_memory=True)
                return xlsx_buf.getvalue(), None
            except Exception as e1:
                try:
                    backlog = BacklogGenerator().generate(report)
                    export_backlog_xlsx(backlog)
                    return None, None
                except Exception as e2:
                    _log.error("Backlog üretimi hatası: {}", e2)
                    return None, f"Backlog Üretimi: {e2}"

        def gen_stories():
            if session_id:
                set_thread_session_id(session_id)
            try:
                if _is_llm_available():
                    stories = StoryGenerator().generate(report)
                    docx_buf = export_stories_docx(stories, in_memory=True)
                    return docx_buf.getvalue(), None
                return None, None
            except Exception as e1:
                try:
                    if _is_llm_available():
                        stories = StoryGenerator().generate(report)
                        export_stories_docx(stories)
                    return None, None
                except Exception as e2:
                    _log.error("Story üretimi hatası: {}", e2)
                    return None, f"Kullanıcı Hikayesi Üretimi: {e2}"

        def gen_bdd():
            if session_id:
                set_thread_session_id(session_id)
            try:
                if _is_llm_available():
                    bdd = BDDGenerator()
                    scenarios = bdd.generate(report)
                    bdd_buf = bdd.write_feature_file(scenarios, in_memory=True)
                    return bdd_buf.getvalue(), None
                return None, None
            except Exception as e1:
                try:
                    if _is_llm_available():
                        bdd = BDDGenerator()
                        scenarios = bdd.generate(report)
                        bdd.write_feature_file(scenarios)
                    return None, None
                except Exception as e2:
                    _log.error("BDD üretimi hatası: {}", e2)
                    return None, f"BDD Senaryosu Üretimi: {e2}"

        def gen_json():
            if session_id:
                set_thread_session_id(session_id)
            try:
                json_buf = export_report_json(report, in_memory=True)
                return json_buf.getvalue(), None
            except Exception as e1:
                try:
                    export_report_json(report)
                    return None, None
                except Exception as e2:
                    _log.error("JSON export hatası: {}", e2)
                    return None, f"JSON Rapor Üretimi: {e2}"

        futures = {
            executor.submit(gen_srs): "srs_pdf",
            executor.submit(gen_backlog): "backlog_xlsx",
            executor.submit(gen_stories): "user_stories_docx",
            executor.submit(gen_bdd): "scenarios_feature",
            executor.submit(gen_json): "analysis_report_json",
        }
        
        warnings_to_add = []
        for fut in concurrent.futures.as_completed(futures):
            key = futures[fut]
            try:
                val, warning = fut.result()
                if val is not None:
                    st.session_state[key] = val
                if warning is not None:
                    warnings_to_add.append(warning)
            except Exception as e:
                _log.error("İş parçacığı beklenmedik hata ({}): {}", key, e)
                warnings_to_add.append(f"{key} üretimi beklenmedik hata: {e}")

        if warnings_to_add:
            if "pipeline_warnings" not in st.session_state:
                st.session_state["pipeline_warnings"] = []
            st.session_state["pipeline_warnings"].extend(warnings_to_add)

    flush_usage_to_session()
    _log.info("Paralel çıktı üretimi tamamlandı.")
    return report
