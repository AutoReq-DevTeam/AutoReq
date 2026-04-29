# CONTEXT.md — AutoReq Source of Truth

> **Last Updated:** 2026-04-19  
> **Purpose:** Canonical reference for AI agents and contributors. Describes architecture, conventions, data flow, and environment setup.
>
> 📌 **Looking for a much deeper, agent-friendly walkthrough?** See [`AGENT_GUIDE.md`](./AGENT_GUIDE.md) (Turkish, comprehensive). This file (CONTEXT.md) is the short English overview.

---

## 1. Tech Stack & Versions

| Layer | Technology | Version Constraint | Purpose |
|---|---|---|---|
| **Language** | Python | ≥ 3.8 | Core runtime |
| **NLP** | Stanza | ≥ 1.8.0 | Tokenization, POS tagging, lemmatization, NER (Turkish model) |
| **NLP** | NLTK | ≥ 3.8.1 | Turkish stopword list |
| **ML** | scikit-learn | ≥ 1.4.0 | Reserved for future ML classifier (currently heuristic) |
| **Data** | NumPy / Pandas | ≥ 1.26/ ≥ 2.2 | Numerical & tabular utilities |
| **LLM** | Google Generative AI (Gemini) | Runtime (lazy) | Conflict detection, gap analysis, improvement suggestions |
| **LLM Framework** | LangChain + langchain-openai | ≥ 0.1.0 | Declared dep; not actively imported (future provider swap) |
| **Web UI** | Streamlit | ≥ 1.32.0 | Interactive single-page dashboard |
| **PDF** | fpdf2 / ReportLab | ≥ 2.7.9 / ≥ 4.1.0 | SRS document generation |
| **Export** | python-docx / openpyxl | ≥ 1.1.0 / ≥ 3.1.2 | Word and Excel export (future) |
| **Validation** | Pydantic | ≥ 2.6.0 | Data validation (future use) |
| **Logging** | Loguru | ≥ 0.7.2 | Structured logging with module binding |
| **Config** | python-dotenv | ≥ 1.0.0 | `.env` loading for API keys |
| **Testing** | pytest + pytest-cov | ≥ 8.0 / ≥ 4.1 | Unit testing and coverage |
| **VCS** | Git + GitHub | — | Scrum-based workflow |

---

## 2. Core Architecture

### 2.1 High-Level Overview

```
AutoReq is a hybrid NLP + LLM tool that transforms raw customer text
into structured software requirements documents (SRS, User Stories,
BDD scenarios). The primary language of analysis is Turkish.
```

### 2.2 Directory Layout

```
AutoReq/
├── app.py                  # Entry point — Streamlit orchestrator
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
│
├── core/                   # Layer 1: NLP preprocessing engine
│   ├── models.py           #   Shared dataclasses (Requirement, ParsedDocument, AnalysisReport)
│   ├── preprocessor.py     #   Stanza pipeline: tokenize → POS → lemma → filter stopwords
│   ├── classifier.py       #   FR / NFR heuristic classifier (keyword matching)
│   └── ner.py              #   Entity recognizer (actors & objects via lemma lookup)
│
├── modules/                # Layer 2: Intelligent analysis (LLM-powered)
│   ├── llm_client.py       #   Centralized Gemini API client (LLMClient class)
│   ├── conflict_detector.py#   Pairwise conflict analysis via LLM
│   ├── conflict_prompts.py #   System + user prompt templates for conflict detection
│   ├── gap_analyzer.py     #   Missing-requirement detector (stub — NotImplementedError)
│   ├── gap_prompts.py      #   System + user prompt templates for gap analysis
│   ├── improver.py         #   Vague-requirement improver (stub — NotImplementedError)
│   ├── analysis_report_parsing.py  # LLM JSON → AnalysisReport dict normalizer
│   ├── llm_response_utils.py      # extract_json_object() utility
│   └── logging_utils.py           # get_module_logger(), log_with_context()
│
├── outputs/                # Layer 3: Document & export generators
│   ├── srs_generator.py    #   ISO 29148 SRS PDF (fpdf2, Turkish font support)
│   ├── story_generator.py  #   User Story generator (stub)
│   ├── backlog_generator.py#   Product Backlog generator (stub)
│   ├── bdd_generator.py    #   Gherkin BDD scenario generator (stub)
│   ├── logo_generator.py   #   PNG logo creator (Pillow)
│   └── generated/          #   Output artifacts (.gitignore'd)
│
├── ui/                     # Layer 4: Streamlit UI components
│   ├── dashboard.py        #   Main input screen (text area + demo button + analyze button)
│   ├── results.py          #   Tabbed results panel (requirements, conflicts, gaps, downloads)
│   └── components.py       #   Reusable widgets (req_card, priority_badge, download_button)
│
├── tests/                  # pytest suite
│   ├── conftest.py         #   Adds project root to sys.path
│   ├── test_core.py        #   Core module tests (mostly stubs/TODO)
│   ├── test_modules.py     #   Module tests
│   └── test_outputs.py     #   Output tests
│
├── data/                   # ⚠ Currently empty placeholder folders
│   ├── samples/            #   (planned) sample input texts — folder exists, no files yet
│   └── templates/          #   (planned) JSON requirement templates — folder exists, no files yet
│
└── docs/                   # Project documentation
    ├── AGENT_GUIDE.md      #   ⭐ Agent-friendly comprehensive tutorial (Turkish)
    ├── TEAM.md             #   RACI matrix, member roles, sprint calendar (Turkish)
    ├── FEATURES.md         #   Feature list & status
    ├── CONTEXT.md          #   This file — architecture overview
    ├── ROADMAP_AND_ISSUES.md  # Sprint backlog & issue tracker (Turkish)
    ├── CHECKPOINTS/        #   Marp slide decks (Turkish)
    └── Makale/             #   Academic paper drafts (Turkish)
```

### 2.3 Design Patterns

| Pattern | Where | Purpose |
|---|---|---|
| **Pipeline / Chain** | `app.py → process_text()` | Sequential processing: preprocessor → classifier → NER |
| **Singleton (Memoized)** | `@st.cache_resource` on `load_nlp_pipeline()` | Heavy NLP models loaded once into RAM across Streamlit reruns |
| **DTO (Data Transfer Object)** | `core/models.py` dataclasses | `Requirement → ParsedDocument → AnalysisReport` flow between layers |
| **Strategy (Prompt Templates)** | `conflict_prompts.py`, `gap_prompts.py` | Persona + task + output schema composed into system prompts |
| **Facade** | `LLMClient` | Single interface hiding Gemini-specific API details |
| **Graceful Degradation** | `ner.py` fallback | If Stanza fails to load, falls back to simple string matching |
| **Dependency Injection** | `ConflictDetector(llm_client=...)` | LLM client injected for testability |
| **Lazy Import** | `llm_client.py` → `google.generativeai` | SDK imported at init time, not module load time |

### 2.4 Implementation Status

| Component | Status |
|---|---|
| `TextPreprocessor` | ✅ Implemented |
| `RequirementClassifier` | ✅ Implemented (heuristic / keyword) |
| `EntityRecognizer` | ✅ Implemented (Stanza + fallback) |
| `LLMClient` (Gemini) | ✅ Implemented |
| `ConflictDetector` | ✅ Implemented (LLM-powered) |
| `analysis_report_parsing` | ✅ Implemented |
| `GapAnalyzer` | ❌ Stub (`NotImplementedError`) |
| `RequirementImprover` | ❌ Stub (`NotImplementedError`) |
| `SRSGenerator` | ⚠️ Partial (template PDF, no dynamic data) |
| `StoryGenerator` | ❌ Stub |
| `BacklogGenerator` | ❌ Stub |
| `BDDGenerator` | ❌ Stub |

---

## 3. Coding Standards

### 3.1 Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Files / modules | `snake_case.py` | `conflict_detector.py` |
| Classes | `PascalCase` | `RequirementClassifier` |
| Functions / methods | `snake_case` | `process_text()` |
| Constants | `UPPER_SNAKE_CASE` | `CORE_CONFLICT_ANALYZER_PERSONA` |
| Dataclass fields | `snake_case` | `req_type`, `source_index` |
| Private methods | `_leading_underscore` | `_chat_gemini()`, `_run_pairwise_llm_analysis()` |
| Requirement IDs | `REQ_NNN` (zero-padded) | `REQ_001`, `REQ_012` |

### 3.2 Docstrings & Type Hints

- **Every** public class/function must have a **docstring** (Turkish or English).
- Type hints are **required** on all function signatures (return type + parameters).
- Dataclasses use `field(default_factory=list)` for mutable defaults — **never** bare `[]`.

### 3.3 Error Handling

| Scenario | Pattern |
|---|---|
| Unimplemented feature | Raise `NotImplementedError` with descriptive message |
| LLM failures | Custom `LLMClientError(RuntimeError)` — caught and re-raised with context |
| Missing API key | `LLMClientError` at `__init__` time with setup instructions |
| Missing NLP model | `logger.warning()` + set `self.nlp = None`; fallback on method call |
| JSON parse failure | `ValueError` from `extract_json_object()` → wrapped in `LLMClientError` |
| Empty input | Return empty DTO (e.g., `ParsedDocument(raw_text=...)`) — never crash |

### 3.4 Logging

- **Library:** Loguru (not stdlib `logging`, except NER module which uses `logging.getLogger`)
- **Pattern:** `get_module_logger("module_name")` returns a bound logger via `logger.bind(module=...)`
- **Levels:** `debug` for LLM call details, `info` for analysis results, `error`/`exception` for failures
- **No print()** in production paths (only in model download feedback)

### 3.5 Git Conventions

```
Branch:   main → develop → feature/uye[n]-description
Commits:  feat: | fix: | docs: | test: | prompt:
PR:       Minimum 1 reviewer required
```

### 3.6 Folder Ownership

| Directory | Owner |
|---|---|
| `core/` + `app.py` | Üye 1 (Galip Efe Öncü) — NLP & Preprocessing |
| `modules/` | Üye 2 (Eren Eyyüpkoca) — Intelligent Analysis |
| `outputs/` | Üye 3 (Halise İncir) — Document Generation |
| `ui/` + `tests/` | Üye 4 (Agid Gülsever) — UI & Testing |
| `core/models.py` | Shared — changes require PR review by all |

---

## 4. Critical Logic — Data Flow

### 4.1 Main Pipeline (`app.py → process_text()`)

```
┌─────────────┐     ┌────────────────┐     ┌──────────────┐     ┌───────────────┐
│  Raw Text   │────▶│ TextPreprocessor│────▶│  Classifier  │────▶│ EntityRecognizer│
│ (user input)│     │  .process()    │     │  .classify() │     │  .recognize()  │
└─────────────┘     └────────────────┘     └──────────────┘     └───────────────┘
                           │                      │                      │
                    ParsedDocument          Requirement.req_type    Requirement.actors
                    [Requirement×N]         set to FR / NFR        & .objects populated
                           │
                           ▼
                    ┌──────────────┐
                    │AnalysisReport│  ← conflicts=[], gaps=[], improvements=[]
                    └──────────────┘     (populated by Layer 2 when integrated)
                           │
                           ▼
                    ┌──────────────┐
                    │ render_results│  ← Streamlit tabbed UI
                    └──────────────┘
```

### 4.2 Data Models (core/models.py)

```python
Requirement:
  id: str              # "REQ_001"
  text: str            # Original sentence
  req_type: str        # "FUNCTIONAL" | "NON_FUNCTIONAL" | "UNKNOWN"
  actors: List[str]    # ["kullanıcı", "sistem"]
  objects: List[str]   # ["şifre", "form"]
  priority: Optional   # "HIGH" | "MEDIUM" | "LOW"
  tokens: List[str]    # Filtered words (no stopwords/punctuation)
  lemmas: List[str]    # Word roots
  pos_tags: List[str]  # UPOS tags

ParsedDocument:
  raw_text: str
  requirements: List[Requirement]
  language: str = "tr"
  total_sentences: int

AnalysisReport:
  parsed_doc: ParsedDocument
  conflicts: List[dict]      # {req_ids, conflict_type, reason, ...}
  gaps: List[dict]           # {missing_area, suggestion, severity, ...}
  improvements: List[dict]   # {original, improved, reason}
```

### 4.3 LLM Integration Flow (Conflict Detection)

```
ConflictDetector.analyze(doc)
  │
  ├─ _format_requirements_block(doc)      → "[REQ_001] (FUNCTIONAL) ..."
  ├─ build_pairwise_conflict_user_prompt() → structured user message
  ├─ build_conflict_detection_system_prompt() → persona + task + JSON schema
  │
  ├─ LLMClient.chat(system_prompt, user_prompt)
  │     └─ _chat_gemini() → Gemini 3.0 Flash API call
  │           └─ Returns LLMResponse(content=..., raw=...)
  │
  ├─ extract_json_object(response.content) → parsed dict
  ├─ conflicts_payload_to_report_dicts()   → normalized list[dict]
  │
  └─ Returns PairwiseConflictAnalysis(conflicts, meta, raw_llm)
```

### 4.4 Classifier Logic (Heuristic)

```
For each Requirement:
  1. Lowercase the text
  2. Check if ANY keyword from nfr_keywords list appears in text
     Keywords: güvenli, şifre, performans, hızlı, saniye, gecikme, ssl, ...
  3. Match found → "NON_FUNCTIONAL"
     No match   → "FUNCTIONAL"
```

### 4.5 NER Logic (Lemma-Based)

```
For each Requirement:
  1. Run Stanza pipeline (tokenize → mwt → pos → lemma → ner)
  2. For each word, get lemma (lowercase)
  3. Check lemma against:
     - actor_lemmas: {kullanıcı, sistem, yönetici, admin, müşteri, ...}
     - object_lemmas: {şifre, form, e-posta, sepet, hesap, ...}
  4. Collect into sets (deduplication)
  5. Fallback: if Stanza unavailable → plain substring matching
```

---

## 5. Environment Setup

### 5.1 Prerequisites

- Python ≥ 3.8
- pip
- (Optional) Windows for SRS PDF Arial font support

### 5.2 Installation

```bash
# 1. Clone
git clone https://github.com/AutoReq-DevTeam/AutoReq.git
cd AutoReq

# 2. Virtual environment
python -m venv venv
venv\Scripts\activate         # Windows
# source venv/bin/activate    # Linux/macOS

# 3. Install dependencies (includes google-generativeai for the Gemini LLM layer)
pip install -r requirements.txt

# 4. Download Stanza Turkish model (~150 MB)
python -c "import stanza; stanza.download('tr')"
```

### 5.3 Environment Variables

Create `.env` from `.env.example`:

```bash
cp .env.example .env
```

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | **Yes** (for LLM features) | — | Google AI Studio API key |
| `GEMINI_MODEL_NAME` | No | `gemini-3.0-flash` | Model to use (`gemini-3.0-flash`, `gemini-3.0-pro`) |

> ⚠️ Core NLP pipeline (preprocessor, classifier, NER) works **without** an API key.  
> LLM features (conflict detection, gap analysis) require `GEMINI_API_KEY`.

### 5.4 Running

```bash
# Launch Streamlit UI
streamlit run app.py
# Opens at http://localhost:8501
```

### 5.5 Testing

```bash
pytest tests/ -v
pytest tests/ -v --cov=core --cov=modules --cov=outputs
```

### 5.6 Key File Paths

| Path | Purpose |
|---|---|
| `outputs/generated/` | Runtime-generated PDFs (gitignored, currently empty) |
| `outputs/srs_taslak.pdf` | Pre-generated static SRS template (committed) |
| `outputs/logo.png` | Logo image for PDF header (committed) |
| `data/samples/` | (planned) sample input texts — folder exists but is empty |
| `data/templates/` | (planned) requirement JSON schema — folder exists but is empty |

---

## 6. Agent Notes

### Critical Constraints

1. **Turkish language context**: All NLP processing, prompts, and UI labels are in Turkish. Stanza Turkish model (`stanza.download('tr')`) is mandatory.
2. **Mutable default trap**: Always use `field(default_factory=list)` in dataclasses, never bare `[]`.
3. **Shared models contract**: `core/models.py` is the interface boundary. Changes to `Requirement`, `ParsedDocument`, or `AnalysisReport` affect all 4 team members.
4. **LLM output parsing**: LLM responses may contain markdown fences or extra text. `extract_json_object()` handles this by finding the first `{...}` block.
5. **Stanza loads twice**: `TextPreprocessor` and `EntityRecognizer` each instantiate their own `stanza.Pipeline` — both cached via `@st.cache_resource` in `app.py`.
6. **Tests are mostly stubs**: The test suite has many `TODO` / `pass` placeholders. The two `test_*_raises_not_implemented` tests in `test_core.py` are now **outdated** (the underlying functions have been implemented) and will fail on `main` — see ROADMAP Issue #8.
7. **SRS generator is Windows-coupled**: Font paths hardcoded to `C:\Windows\Fonts\arial.ttf`. Falls back to Helvetica on non-Windows. Also writes to `outputs/srs_taslak.pdf` while UI scans `outputs/generated/*.pdf` — these don't currently match.
8. **`ConflictDetector` not wired into `app.py`**: `process_text()` returns `conflicts=[]` even though `ConflictDetector.analyze()` is fully implemented. Integration is pending.
9. **Classifier false positives**: NFR keyword list contains `"kullanıcı"` and `"şifre"`, so most functional sentences mentioning users/passwords are mis-classified as NON_FUNCTIONAL. Will be replaced by an ML model later.
10. **License**: GNU GPL v3.
