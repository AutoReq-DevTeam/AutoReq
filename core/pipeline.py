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
from modules.llm_client import LLMClientError

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
    return bool(os.getenv("GEMINI_API_KEY"))

def process_text(raw_text: str, status_ui=None) -> AnalysisReport:
    if status_ui: status_ui.update(label="Stanza ile ön işleme yapılıyor...")
    parsed_doc = nlp_engines["preprocessor"].process(raw_text)

    for req in parsed_doc.requirements:
        req = nlp_engines["classifier"].classify(req)
        req = nlp_engines["ner"].recognize(req)
        req = nlp_engines["priority_detector"].detect(req)

    conflicts = []
    if _is_llm_available():
        try:
            _log.info("LLM ile çelişki analizi başlatılıyor...")
            if status_ui: status_ui.update(label="LLM ile çelişki analizi yapılıyor...")
            conflicts = ConflictDetector().analyze(parsed_doc)
            _log.info("Çelişki analizi tamamlandı | conflicts={}", len(conflicts))
        except (LLMClientError, ValueError) as exc:
            _log.warning("Çelişki analizi başarısız — boş liste ile devam ediliyor | hata={}", exc)
            conflicts = []
    else:
        _log.info("GEMINI_API_KEY tanımlı değil — çelişki analizi atlanıyor.")

    gaps = []
    if _is_llm_available():
        try:
            _log.info("LLM ile eksiklik analizi başlatılıyor...")
            if status_ui: status_ui.update(label="LLM ile eksiklik analizi yapılıyor...")
            gaps = GapAnalyzer().analyze(parsed_doc)
            _log.info("Eksiklik analizi tamamlandı | gaps={}", len(gaps))
        except (LLMClientError, ValueError) as exc:
            _log.warning("Eksiklik analizi başarısız — boş liste ile devam ediliyor | hata={}", exc)
            gaps = []
    else:
        _log.info("GEMINI_API_KEY tanımlı değil — eksiklik analizi atlanıyor.")

    improvements = []
    if _is_llm_available():
        try:
            _log.info("LLM ile gereksinim iyileştirme başlatılıyor...")
            if status_ui: status_ui.update(label="LLM ile gereksinimler iyileştiriliyor...")
            improver = RequirementImprover()
            for req in parsed_doc.requirements:
                result = improver.improve(req)
                if result.get("improved") != result.get("original"):
                    improvements.append(result)
            _log.info("Gereksinim iyileştirme tamamlandı | improvements={}", len(improvements))
        except (LLMClientError, ValueError) as exc:
            _log.warning("Gereksinim iyileştirme başarısız — boş liste ile devam ediliyor | hata={}", exc)
            improvements = []
    else:
        _log.info("GEMINI_API_KEY tanımlı değil — gereksinim iyileştirme atlanıyor.")

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
                    scenarios = BDDGenerator().generate(report)
                    BDDGenerator().write_feature_file(scenarios)
            except Exception as e: _log.error("BDD üretimi hatası: {}", e)

        def gen_json():
            try: export_report_json(report)
            except Exception as e: _log.error("JSON export hatası: {}", e)

        futures = [
            executor.submit(gen_srs),
            executor.submit(gen_backlog),
            executor.submit(gen_stories),
            executor.submit(gen_bdd),
            executor.submit(gen_json)
        ]
        concurrent.futures.wait(futures)

    _log.info("Paralel çıktı üretimi tamamlandı.")
    return report
