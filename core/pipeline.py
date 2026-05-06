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
from modules.llm_client import LLMClientError, flush_usage_to_session

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
    return bool(os.getenv("GEMINI_API_KEY") or os.getenv("DEEPSEEK_API_KEY"))

def process_text(raw_text: str, status_ui=None) -> AnalysisReport:
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
    if _is_llm_available():
        _log.info("LLM ile çelişki ve eksiklik analizi paralel başlatılıyor...")
        if status_ui: status_ui.update(label="LLM ile çelişki ve eksiklik analizi yapılıyor...")

        def _run_conflicts():
            return ConflictDetector().analyze(parsed_doc)

        def _run_gaps():
            return GapAnalyzer().analyze(parsed_doc)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            fut_conflicts = ex.submit(_run_conflicts)
            fut_gaps = ex.submit(_run_gaps)

            try:
                conflicts = fut_conflicts.result()
                _log.info("Çelişki analizi tamamlandı | conflicts={}", len(conflicts))
            except (LLMClientError, ValueError) as exc:
                _log.warning("Çelişki analizi başarısız — boş liste ile devam ediliyor | hata={}", exc)
                st.warning(f"⚠️ Çelişki analizi tamamlanamadı: {exc}")
                conflicts = []

            try:
                gaps = fut_gaps.result()
                _log.info("Eksiklik analizi tamamlandı | gaps={}", len(gaps))
            except (LLMClientError, ValueError) as exc:
                _log.warning("Eksiklik analizi başarısız — boş liste ile devam ediliyor | hata={}", exc)
                st.warning(f"⚠️ Eksiklik analizi tamamlanamadı: {exc}")
                gaps = []
    else:
        _log.info("API key tanımlı değil — çelişki ve eksiklik analizi atlanıyor.")

    flush_usage_to_session()

    report = AnalysisReport(
        parsed_doc=parsed_doc.model_dump(),
        conflicts=conflicts,
        gaps=gaps,
        improvements=[],
    )

    _log.info("Paralel çıktı üretimi başlatılıyor...")
    if status_ui: status_ui.update(label="Paralel belge üretimi yapılıyor...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        def gen_srs():
            try: generate_srs(report)
            except Exception as e: _log.error("SRS üretimi hatası: {}", e)

        def gen_backlog():
            try:
                backlog = BacklogGenerator().generate(report)
                export_backlog_xlsx(backlog)
            except Exception as e: _log.error("Backlog üretimi hatası: {}", e)

        def gen_stories():
            try:
                if _is_llm_available():
                    stories = StoryGenerator().generate(report)
                    export_stories_docx(stories)
            except Exception as e: _log.error("Story üretimi hatası: {}", e)

        def gen_bdd():
            try:
                if _is_llm_available():
                    bdd = BDDGenerator()
                    scenarios = bdd.generate(report)
                    bdd.write_feature_file(scenarios)
            except Exception as e: _log.error("BDD üretimi hatası: {}", e)

        def gen_json():
            try: export_report_json(report)
            except Exception as e: _log.error("JSON export hatası: {}", e)

        def gen_improvements():
            if not _is_llm_available():
                return
            try:
                _log.info("LLM ile gereksinim iyileştirme toplu başlatılıyor...")
                improver = RequirementImprover()
                results = improver.improve_batch(parsed_doc.requirements)
                report.improvements = [r for r in results if r.get("improved") != r.get("original")]
                _log.info("Gereksinim iyileştirme tamamlandı | improvements={}", len(report.improvements))
            except (LLMClientError, ValueError) as exc:
                _log.warning("Gereksinim iyileştirme başarısız | hata={}", exc)

        futures = [
            executor.submit(gen_srs),
            executor.submit(gen_backlog),
            executor.submit(gen_stories),
            executor.submit(gen_bdd),
            executor.submit(gen_json),
            executor.submit(gen_improvements),
        ]
        concurrent.futures.wait(futures)

    flush_usage_to_session()
    _log.info("Paralel çıktı üretimi tamamlandı.")
    return report
