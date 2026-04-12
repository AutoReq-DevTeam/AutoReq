# 📋 AutoReq — Feature Specification & Tracking

> **Document Type:** Definitive Feature List  
> **Last Updated:** 2026-04-12  
> **Status Legend:** `[x]` Implemented | `[ ]` Planned | `⚠️` Partial

---

## 1. Project Vision

**AutoReq is a hybrid NLP + LLM-powered tool that automatically transforms raw, unstructured customer text (in Turkish) into structured, industry-standard software requirements documents — eliminating hours of manual elicitation and reducing costly misunderstandings.**

**The ultimate goal is to provide a one-click pipeline where a business analyst pastes a customer conversation and receives a complete SRS document, user stories, BDD scenarios, and a conflict report — all within seconds.**

---

## 2. Core Features (MVP)

These are the **must-have** features required for the initial release. The system must be able to accept raw Turkish text and produce classified, entity-tagged requirements displayed in an interactive dashboard.

### 2.1 Text Preprocessing Engine

- [x] **Sentence Tokenization** — Split raw input into individual requirement sentences using Stanza's Turkish model
- [x] **Stopword Removal** — Filter out Turkish stopwords (e.g., "bir", "ve", "için") using NLTK's Turkish corpus
- [x] **Lemmatization** — Reduce words to their root forms (e.g., "kullanıcıların" → "kullanıcı") via Stanza POS+lemma pipeline
- [x] **Text Normalization** — Lowercase conversion and punctuation cleanup before analysis
- [x] **Requirement ID Assignment** — Auto-generate sequential IDs (`REQ_001`, `REQ_002`, ...) for each extracted sentence

### 2.2 Requirement Classification

- [x] **Functional vs. Non-Functional Classification** — Categorize each requirement as `FUNCTIONAL` or `NON_FUNCTIONAL` using heuristic keyword matching
- [x] **NFR Keyword Dictionary** — Maintain a curated Turkish keyword list (e.g., "güvenli", "performans", "hızlı", "şifre", "ssl", "saniye") for non-functional detection
- [x] **Default-to-Functional Fallback** — Requirements that match no NFR keyword are classified as `FUNCTIONAL` to avoid false negatives

### 2.3 Named Entity Recognition (NER)

- [x] **Actor Detection** — Identify system actors (e.g., "Kullanıcı", "Sistem", "Yönetici", "Admin") using lemma-based lookup against a predefined actor dictionary
- [x] **Object Detection** — Extract domain objects (e.g., "şifre", "form", "e-posta", "sepet", "hesap") from requirement sentences
- [x] **Stanza NER Integration** — Use Stanza's Turkish NER pipeline for primary entity extraction
- [x] **Graceful Fallback** — If Stanza model fails to load, fall back to simple substring matching to ensure the system never crashes

### 2.4 Data Transfer Models

- [x] **Requirement Dataclass** — Structured DTO containing `id`, `text`, `req_type`, `actors`, `objects`, `priority`, `tokens`, `lemmas`, `pos_tags`
- [x] **ParsedDocument Dataclass** — Container holding `raw_text`, `requirements[]`, `language`, `total_sentences`
- [x] **AnalysisReport Dataclass** — Final output DTO with `parsed_doc`, `conflicts[]`, `gaps[]`, `improvements[]`

### 2.5 Interactive Dashboard (UI)

- [x] **Streamlit Single-Page App** — Clean web dashboard accessible at `localhost:8501`
- [x] **Text Input Area** — `st.text_area` for pasting raw customer text
- [x] **Demo Mode Button** — Pre-loaded sample Turkish requirement text for instant demonstration
- [x] **Analyze Button** — Triggers the full NLP pipeline with a single click
- [x] **Progress Indicators** — Spinner animation and toast notifications during analysis
- [x] **Tabbed Results Panel** — Results organized into tabs: Requirements, Conflicts, Gaps, Downloads
- [x] **Requirement Cards** — Custom `req_card()` UI component displaying classification, actors, and objects per requirement
- [x] **PDF Download Button** — `st.download_button` to export SRS document directly from the browser

---

## 3. Future Enhancements (Backlog)

Features planned for subsequent sprints and later versions. Ordered by priority.

### 3.1 Intelligent Analysis — LLM-Powered (High Priority)

- [x] **Conflict Detection Engine** — Pairwise analysis of all requirements using Google Gemini to identify logical contradictions (e.g., "System must be offline" vs. "System must sync in real-time")
- [x] **Conflict Prompt Templates** — Structured system + user prompts with persona ("Senior QA Engineer") and JSON output schema for reliable LLM responses
- [x] **LLM Client (Gemini)** — Centralized `LLMClient` class wrapping Google Generative AI SDK with lazy import, error handling, and `LLMClientError` exceptions
- [x] **LLM JSON Response Parsing** — `extract_json_object()` utility to reliably extract JSON from LLM responses that may contain markdown fences or extra text
- [ ] **Gap Analysis Engine** — Compare extracted requirements against standard templates (authentication, authorization, error handling, logging) and flag missing areas
- [ ] **Vague Expression Improver** — Transform ambiguous statements like "Sistem hızlı olmalı" into measurable criteria like "System shall respond within 2 seconds under 1000 concurrent users"
- [ ] **Robust LLM Error Recovery** — Catch `ValueError` from malformed LLM JSON responses and return empty `[]` instead of crashing the pipeline

### 3.2 Document Generation (Medium Priority)

- [x] **SRS PDF Template** — Static ISO/IEC/IEEE 29148 compliant PDF skeleton with 10 standard sections, Turkish font support (ş, ğ, ı, İ), corporate logo, and page numbering via `fpdf2`
- [ ] **Dynamic SRS Population** — Fill the SRS template with live `AnalysisReport` data (classified requirements, detected actors, conflict summary) instead of static placeholder text
- [ ] **User Story Generator** — Convert functional requirements into Agile stories in "As a [Actor], I want [Action], so that [Value]" format using LLM
- [ ] **BDD Scenario Generator** — Produce Gherkin-format test scenarios (`Given` / `When` / `Then`) for each functional requirement
- [ ] **Product Backlog Generator** — Generate a prioritized sprint backlog with effort estimates from the extracted requirements

### 3.3 UI & Experience Enhancements (Medium Priority)

- [ ] **Sidebar Project Status** — `st.sidebar` showing overall analysis progress, model status, and API key availability
- [ ] **Multi-Tab UI Architecture** — Separate input, analysis, and results into distinct Streamlit pages/tabs for clearer navigation
- [ ] **Conflict Visualization** — Display conflicting requirement pairs with highlighted differences and severity indicators
- [ ] **Gap Visualization** — Show missing requirement areas in a categorized checklist with suggested additions

### 3.4 Testing & Quality (Medium Priority)

- [ ] **Core Module Unit Tests** — Meaningful assertion-based tests for `classifier.py` (verify `FUNCTIONAL`/`NON_FUNCTIONAL` output) and `ner.py` (verify actor/object extraction)
- [ ] **LLM Module Tests** — Mock-based tests for `ConflictDetector` to verify prompt construction and response parsing without API calls
- [ ] **Output Module Tests** — Validate generated PDF structure, Turkish character encoding, and file integrity
- [ ] **Test Coverage ≥ 70%** — Achieve minimum 70% code coverage across `core/`, `modules/`, and `outputs/`

### 3.5 Integration & Advanced (Low Priority)

- [ ] **Multi-Language Support** — Extend NLP pipeline beyond Turkish to support English requirement texts
- [ ] **Jira / Trello Integration** — Export generated user stories and backlog items directly to project management tools via API
- [ ] **Batch File Upload** — Accept `.txt`, `.docx`, or `.pdf` file uploads instead of only text area input
- [ ] **Requirement Prioritization** — Assign `HIGH` / `MEDIUM` / `LOW` priority to each requirement based on keyword analysis and LLM assessment
- [ ] **Version History** — Track changes between multiple analysis runs on the same text
- [ ] **Pydantic Validation** — Enforce strict schema validation on all data models using Pydantic v2

---

## 4. User Roles

| Role | Description | Primary Actions |
|---|---|---|
| **Business Analyst** | The primary end user. Gathers raw customer text from meetings, emails, or interviews. | Paste raw text → Run analysis → Review classified requirements → Export SRS document |
| **QA Engineer** | Responsible for verifying requirements quality and test coverage. | Review conflict reports → Identify contradictions → Use BDD scenarios for test planning |
| **Project Manager / Product Owner** | Oversees sprint planning and backlog grooming. | Export user stories → Generate product backlog → Prioritize requirements for sprint planning |
| **Software Architect** | Makes technical decisions based on non-functional requirements. | Filter NFR requirements → Review gap analysis → Validate system constraints (performance, security) |
| **Developer (Team Member)** | Builds features based on classified and approved requirements. | Access specific requirements by ID → Read acceptance criteria from generated stories → Reference SRS sections |
| **Stakeholder / Client** | Non-technical user who needs visibility into project requirements. | View dashboard results → Download PDF report → Verify that their input was correctly captured |

---

## 5. Success Criteria

Each feature is considered **successfully completed** when it meets **all** of the following conditions:

### 5.1 Functional Criteria

| Criterion | Measurement |
|---|---|
| **Correct Output** | The feature produces the expected output for the defined input. For classifiers: "Sistem hızlı olmalı" → `NON_FUNCTIONAL`. For NER: "Kullanıcı şifresini değiştirmeli" → actors: `["kullanıcı"]`, objects: `["şifre"]`. |
| **No Runtime Errors** | The feature runs without throwing unhandled exceptions. Stubs must raise `NotImplementedError`; completed features must handle all edge cases (empty input, missing API key, malformed LLM response). |
| **Pipeline Integration** | The feature is called from `app.py → process_text()` and its output is visible in the Streamlit dashboard. A feature that works in isolation but is not integrated is **not done**. |
| **Turkish Language Support** | All NLP features correctly handle Turkish-specific characters (ş, ğ, ı, İ, ö, ü, ç) and morphology. PDF exports render Turkish text without encoding errors. |

### 5.2 Quality Criteria

| Criterion | Measurement |
|---|---|
| **Unit Test Exists** | At least one `pytest` test with a meaningful assertion (not just `pass` or `TODO`) covers the feature's primary function. |
| **Test Passes** | `pytest tests/ -v` reports the feature's test(s) as `PASSED` on the `main` branch. |
| **Docstring & Type Hints** | Every public function/class added by the feature has a docstring and type-annotated parameters and return type. |
| **No `print()` Statements** | Production code uses `Loguru` logging — no `print()` in committed code. |

### 5.3 Performance Criteria

| Criterion | Measurement |
|---|---|
| **Pipeline Speed** | Full analysis of a single-page text (~100 sentences) completes in **< 15 seconds** (including LLM calls). |
| **Preprocessing Speed** | NLP-only processing (tokenize + classify + NER) of 100 words completes in **< 1 second**. |
| **Model Load Time** | Stanza pipeline loads once via `@st.cache_resource` — no re-loading on Streamlit re-runs. |

### 5.4 Definition of Done (DoD) Checklist

A feature moves from `[ ]` to `[x]` only when:

- [ ] Code is merged to `develop` branch via approved Pull Request (≥ 1 reviewer)
- [ ] All acceptance criteria from the corresponding Issue in `ROADMAP_AND_ISSUES.md` are met
- [ ] At least one passing unit test covers the feature
- [ ] No regressions — all existing tests still pass
- [ ] Feature is accessible through the Streamlit UI (or CLI, where applicable)

---

> 📎 **Related Documents:**  
> - [ROADMAP_AND_ISSUES.md](./ROADMAP_AND_ISSUES.md) — Sprint backlog and weekly task breakdown  
> - [TEAM.md](./TEAM.md) — Team roles, RACI matrix, and module ownership  
> - [README.md](../README.md) — Project overview and setup instructions