# Implementation Plan — AutoReq Prioritized Fixes & Article Translation

This implementation plan defines the step-by-step development process, organized by priorities (P0, P1, P2, Phase 4). 

---

## Approved Design Decisions

- **KVKK Masking Layer:** Approved. A local, regex-based anonymization/masking layer will be built into `core/preprocessor.py` to tag and replace T.C. Kimlik Numbers and human names before requirements text reaches the external LLMs.
- **In-Memory File Exports:** Approved. Document generation (PDF, DOCX, XLSX) will be refactored to generate files in-memory using `io.BytesIO`, solving multi-user write collisions and preventing local data leakage.

---

## Proposed Execution Phases

### Phase 1 — Blocker Fixes (P0)
*Goal: Resolve all critical vulnerabilities, crashes, and pipeline data-flow bugs.*

1. **Standalone Functional Verbs (NLP):**
   - Refactor `_FR_VERB_RE` in `core/classifier.py` from `\w+` to `\w*` to match standalone verbs like "yapmalı", "silmeli" and add `-melidir/-malıdır` variants.
2. **Turkish Lowercasing (NLP):**
   - Implement `turkish_lower()` mapping dotted/dotless I correctly. Apply it across `preprocessor.py`, `ner.py`, and `classifier.py` to avoid keyword mismatches.
3. **KVKK Compliance Masking (Security):**
   - Implement regex-based masking in `core/preprocessor.py` to anonymize T.C. Kimlik Numbers and personal identifiers before LLM calls.
4. **Improved Requirements Flow (DocGen):**
   - Modify `core/pipeline.py` to ensure BDD, Story, Backlog, and SRS generators construct outputs using the improved requirements list from `RequirementImprover` instead of raw unimproved ones.
5. **In-Memory Document Generation (UX/DocGen):**
   - Refactor all exporters in `outputs/exporters.py`, `srs_generator.py`, `bdd_generator.py`, `story_generator.py`, and `backlog_generator.py` to output files via `io.BytesIO`. Update Streamlit download buttons to read from memory.
6. **Thread-Safe UI Warnings (UX/Performance):**
   - Fix worker threads throwing exceptions by returning warnings/exceptions from futures to the main thread. Mutate `st.session_state["pipeline_warnings"]` only from the main Streamlit thread.
7. **JSON Exporter Race Condition (Performance):**
   - Defer `export_report_json` execution in `pipeline.py` until after the batch improvement task completes, ensuring improvements are populated in `analysis_report.json`.
8. **LLMClient Model Name Resolution (LLM):**
   - Strip OpenRouter prefixes (e.g. `google/`) when running natively on Gemini, and select appropriate defaults based on active API keys.
9. **Stored XSS Mitigation (Security):**
   - Call `html.escape()` on all dynamically rendered requirement variables in `ui/components.py` before passing to `st.markdown(..., unsafe_allow_html=True)`.
10. **Prompt Injection Shield (Security):**
    - Wrap requirement variables in distinct XML tags in LLM prompts to prevent input text from overriding instructions.

---

### Phase 2 — Critical Fixes (P1)
*Goal: Fix major usability limitations and package dependencies.*

11. **Stanza Neural NER Processor (Performance/NLP):**
    - Remove `'ner'` from Stanza pipeline processors in `core/nlp_engine.py` to save ~300MB of RAM and improve startup latency.
12. **Gaps references checklists (LLM):**
    - Inject the `DOMAIN_REFERENCES` checklist into the Gap Analyzer prompts dynamically in `modules/gap_analyzer.py`.
13. **Turkish SRS Fonts (DocGen):**
    - Implement `download_fonts.py` to fetch `DejaVuSans.ttf` and `DejaVuSans-Bold.ttf` on startup, resolving Turkish character crashes in headless Linux environments.
14. **Gherkin BDD Syntax (DocGen):**
    - Refactor `bdd_generator.py` to group scenarios under a single `Feature` block or export separate files, ensuring compatibility with standard Gherkin engines.
15. **Turkish User Story Templates (DocGen):**
    - Translate user story output templates in `outputs/exporters.py` to proper Turkish syntax.
16. **Score Point Mapping (DocGen):**
    - Lower the 8 SP score mapping threshold in `backlog_generator.py` to `>= 4.0` (or increase weight coefficients) so that it is mathematically reachable.
17. **Session-Isolated Counters (Performance):**
    - Replace global `_pending_tokens` and `_pending_cost` in `llm_client.py` with session-isolated or thread-local variables.
18. **Dependency CVE Upgrades (Security):**
    - Pin all requirements in `requirements.txt` with `==`. Upgrade `streamlit` to `==1.37.0` and `nltk` to `==3.9.1`. Remove duplicate package lines.
19. **Annotation Bias Mitigation (Metrics):**
    - Setup guidelines for calculating Inter-Rater Agreement (Cohen's Kappa) and correct metric discrepancies between text drafts and results.

---

### Phase 3 — Important Fixes (P2)
*Goal: Improve metrics accuracy and refine prompt structures.*

20. **NER Actor Extraction nsubj Filtering (Dataset):**
    - Refactor `core/ner.py` to match nouns from `actor_lemmas` only if they occupy the grammatical subject (`nsubj`) role or passive agent position in the dependency parse tree, reducing false positives on object references (e.g. "sayfa geçişleri").
21. **Conflict Ground Truth Cleaning (Dataset):**
    - Remove false conflict pairs (e.g., REQ_010 vs REQ_011) and SUT expected actors ("sistem", "uygulama") from the evaluation ground truth.

---

### Phase 4 — Turkish Article & Presentation Refactoring
*Goal: Generate a high-quality, humanized academic article and slide deck in Turkish, reflecting all new improvements and accurate evaluation metrics.*

22. **Turkish Research Article Draft (TheArticle_TR.txt):**
    - Translate the complete manuscript to academic Turkish (`docs/Makale/article_TR.txt`).
    - Integrate descriptions of the new components added (Turkish lowercasing, KVKK masking layer, in-memory BytesIO document generation, session isolation).
    - Update all evaluation metrics tables to match the corrected JSON reports (e.g., 92.1% classification accuracy instead of 93.7% error, new precision metrics after NER nsubj filtering).
    - Rewrite and paraphrase all flagged AI-style sections to lower the AI detection score below 10%, ensuring a natural, humanized academic voice.
23. **Turkish Presentation Slides (Sunum_TR.md):**
    - Translate and align the presentation slide deck (`docs/Makale/sunum_TR.md`), updating all metrics to exactly match the article and JSON evaluation files.

---

## Verification Plan

### Automated Tests
```bash
# 1. Run all unit and integration tests
venv/bin/python -m pytest

# 2. Run dev corpus evaluations
PYTHONPATH=. venv/bin/python scripts/eval_dev_corpus.py

# 3. Run held-out corpus evaluations
PYTHONPATH=. venv/bin/python scripts/eval_heldout_corpus.py
```

### Manual Verification
1. **Masking & Anonymization:** Input a text with T.C. Kimlik Numbers and name, check the masked output in the UI.
2. **In-Memory Download:** Perform an analysis and click to download the generated PDF/Word/Excel files. Confirm no new files are created on the server's disk.
3. **Turnitin Check:** (Post-Phase 4) Check rewritten Turkish article text using an AI detector to verify the humanized score is <10%.
