import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load env
load_dotenv()

# Add repo to sys.path
sys.path.insert(0, "/home/knover/Documents/GitHub/AutoReq")

from core.preprocessor import TextPreprocessor
from core.classifier import RequirementClassifier
from core.ner import EntityRecognizer
from core.priority_detector import PriorityDetector
from core.models import Requirement, ParsedDocument, AnalysisReport

from modules.conflict_detector import ConflictDetector
from modules.gap_analyzer import GapAnalyzer
from modules.improver import RequirementImprover

from outputs.srs_generator import generate_srs
from outputs.story_generator import StoryGenerator
from outputs.bdd_generator import BDDGenerator
from outputs.backlog_generator import BacklogGenerator
from outputs.exporters import export_backlog_xlsx, export_stories_docx

def generate_all():
    artifact_dir = Path("/home/knover/.gemini/antigravity/brain/a10b89f1-3ed6-4ebb-9370-43c5ec74f343")
    input_path = "/home/knover/Documents/GitHub/AutoReq/data/demo_scenarios/01_e_ticaret_celisma.txt"
    
    with open(input_path, "r", encoding="utf-8") as f:
        raw_text = f.read().strip()
        
    print("Starting pipeline for demo artifacts...")
    
    # 1. Preprocess
    preprocessor = TextPreprocessor()
    parsed_doc = preprocessor.process(raw_text)
    
    # 2. NLP annotations
    classifier = RequirementClassifier()
    ner = EntityRecognizer()
    priority = PriorityDetector()
    
    for req in parsed_doc.requirements:
        classifier.classify(req)
        ner.recognize(req)
        priority.detect(req)
        
    # 3. LLM Analyzers
    print("Running LLM Analyzers (Improver, Conflict, Gap)...")
    improver = RequirementImprover()
    improvements = []
    try:
        results = improver.improve_batch(parsed_doc.requirements)
        for req, res in zip(parsed_doc.requirements, results):
            original = res.get("original", "").strip()
            improved = res.get("improved", "").strip()
            req.original_text = original
            if improved and improved != original:
                req.text = improved
                improvements.append(res)
    except Exception as e:
        print("Improver error:", e)
        
    conflicts = []
    try:
        conflicts = ConflictDetector().analyze(parsed_doc)
    except Exception as e:
        print("ConflictDetector error:", e)
        
    gaps = []
    try:
        gaps = GapAnalyzer().analyze(parsed_doc)
    except Exception as e:
        print("GapAnalyzer error:", e)
        
    report = AnalysisReport(
        parsed_doc=parsed_doc,
        conflicts=conflicts,
        gaps=gaps,
        improvements=improvements
    )
    
    print("Generating artifact documents...")
    # 4. Generate outputs
    
    # A. SRS PDF
    srs_path = artifact_dir / "demo_srs.pdf"
    generate_srs(report, output_path=srs_path, draft_watermark=True)
    print(f"SRS PDF saved to {srs_path}")
    
    # B. Backlog XLSX
    backlog = BacklogGenerator().generate(report)
    backlog_path = artifact_dir / "demo_backlog.xlsx"
    export_backlog_xlsx(backlog, path=backlog_path)
    print(f"Backlog XLSX saved to {backlog_path}")
    
    # C. User Stories DOCX
    stories = StoryGenerator().generate(report)
    stories_path = artifact_dir / "demo_user_stories.docx"
    export_stories_docx(stories, path=stories_path)
    print(f"User Stories DOCX saved to {stories_path}")
    
    # D. Gherkin BDD Feature
    bdd = BDDGenerator()
    scenarios = bdd.generate(report)
    bdd_path = artifact_dir / "demo_scenarios.feature"
    bdd.write_feature_file(scenarios, output_path=bdd_path)
    print(f"Gherkin scenarios saved to {bdd_path}")
    
    print("\nDemo artifacts generation completed successfully!")

if __name__ == "__main__":
    generate_all()
