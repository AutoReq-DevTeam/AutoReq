<div align="center">

# 🚀 AutoReq

### Automated Software Requirements Analyzer

*Transform raw customer text into structured engineering documents — powered by NLP and LLM intelligence.*

---

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Stanza](https://img.shields.io/badge/Stanza-NLP-09A3D5?style=for-the-badge)](https://stanfordnlp.github.io/stanza/)
[![Gemini](https://img.shields.io/badge/Gemini-LLM-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg?style=for-the-badge)](./LICENSE)
[![Tests](https://img.shields.io/badge/Tests-190%20passing-brightgreen?style=for-the-badge)]()

</div>

---

## 📖 Table of Contents

- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Performance Metrics](#-performance-metrics)
- [Tech Stack](#-tech-stack)
- [Installation](#%EF%B8%8F-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Outputs](#-outputs)
- [Testing](#-testing)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 📌 About the Project

**Requirements engineering** is one of the most challenging and time-consuming phases in software development. Ambiguous customer language, missed edge cases, and contradictory statements can derail entire projects before a single line of code is written. Industry research consistently attributes ~40% of project failures to poor requirements documentation.

**AutoReq** solves this by combining **classical NLP** (Stanza) for fast structural analysis with **Large Language Models** (Gemini 2.5 Flash via OpenRouter) for deep semantic reasoning — creating a hybrid AI pipeline that converts unstructured Turkish customer text into professionally structured, industry-standard documentation.

> *"Better software starts with better requirements."*

### 🔑 Why AutoReq?

- 🕐 **Save hours** of manual requirements elicitation and documentation
- 🎯 **Catch conflicts** between requirements with 96.1% F1 score
- 📄 **Generate ISO 29148-compliant** SRS documents automatically
- 🧪 **Produce test artifacts** — BDD scenarios, user stories, and sprint backlogs
- 🌐 **Turkish language native** — built specifically for agglutinative Turkish morphology
- 🔒 **KVKK compliant** — personal data masking before LLM processing

---

## ✨ Key Features

### 🛠 Core NLP Engine (Layer 1)
- **Text Preprocessing** — Sentence-level tokenization, stopword removal, and lemmatization using Stanza Turkish pipeline
- **KVKK Data Masking** — Auto-masks Turkish ID numbers (`[TC_KIMLIK_NO]`) and personal names (`[KISI_ADI]`) before LLM processing, with sentence-start analysis and exclusion lists to prevent false positives
- **Hybrid FR/NFR Classification** — 3-layer approach: (1) Turkish verb suffix detection (regex), (2) NFR keyword matching (55+ terms), (3) LLM few-shot fallback for ambiguous cases → **94.7% accuracy**
- **Actor & Object Extraction** — Multi-layer NER: lemma table (80+ actor lemmas), dependency parsing (`nsubj`/`nsubj:pass`), SOV syntactic patterns, and multi-word actor detection (18 bigram labels) → **86.5% F1 score**
- **Priority Detection** — Rule-based priority scoring with negation detection and compound pattern exclusion

### 🧠 Intelligent Analysis (Layer 2 — LLM-Powered)
- **Conflict Detection** — Pairwise analysis identifying contradictions across 6 categories (logic, business rule, performance, security, usability, other) with natural language explanations → **96.1% F1 score**
- **Gap Analysis** — Domain-aware detection of missing requirements using configurable checklists (e.g., login flow exists but password reset is missing), with confidence scoring and deduplication
- **Requirement Improvement** — Transforms vague statements like *"should be fast"* into measurable, testable criteria with 35+ Turkish/English vague keyword detection and batch LLM processing

### 📂 Document Generation (Layer 3)
- **SRS Generator** — Produces dynamic, data-driven ISO/IEC/IEEE 29148 compliant SRS documents (PDF) with 11 sections populated from actual analysis data, including functional/NFR tables, actors, data objects, and detected conflicts
- **User Stories** — Generates Agile stories in *"Bir [rol] olarak, [fayda] amacıyla [hedef] istiyorum"* format with acceptance criteria, exported as DOCX
- **BDD Scenarios** — Creates Gherkin-format *Given-When-Then* test scenarios (happy path + negative) under a unified `Feature:` block, exported as `.feature` files
- **Product Backlog** — Prioritized sprint backlog with Fibonacci story points, conflict-weighted scoring, and XLSX export with styled headers

### 🖥 Interactive Dashboard (Layer 4)
- **Streamlit-based UI** — 4-page navigation: Input → Analysis → Results → Export
- **Light/Dark Mode** — Full CSS theming with localStorage persistence
- **i18n Support** — Turkish and English interface localization
- **Demo Mode** — 6 pre-loaded domain scenarios (e-commerce, banking, education, healthcare, corporate, mobile)
- **Real-time Metrics** — Sidebar showing API status, token usage, cost tracking, and requirement/conflict/gap counts
- **Rich Components** — Requirement cards, conflict cards, gap cards, diff views, badges, and step indicators

---

## 🏗 Architecture

AutoReq follows a **3-layer pipeline architecture** with parallel execution:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        app.py (Orchestrator)                            │
│                     Streamlit 4-Page Dashboard                          │
├──────────────────┬──────────────────┬───────────────────────────────────┤
│     Layer 1      │     Layer 2      │           Layer 3                 │
│     core/        │     modules/     │           outputs/                │
│                  │                  │                                   │
│ TextPreprocessor │ ConflictDetector │ SRS Generator (PDF)               │
│ Classifier (3L)  │ GapAnalyzer      │ Story Generator (DOCX)            │
│ EntityRecognizer │ Req. Improver    │ BDD Generator (.feature)          │
│ PriorityDetector │ LLM Client       │ Backlog Generator (XLSX)          │
│ KVKK Masking     │ Prompt Cache     │ Exporters (JSON/XLSX/DOCX)        │
│ Models (Pydantic)│                  │                                   │
└──────────────────┴──────────────────┴───────────────────────────────────┘
```

### Data Flow

```
                    ┌─── TextPreprocessor (Stanza) ──→ Sentence Segmentation
                    │                                        │
Raw Text ───────────┤                                   ┌────┴────┐
                    │                              Classifier   NER
                    │                              (3-layer)  (3-layer)
                    │                                   └────┬────┘
                    │                                        ▼
                    │                                 ParsedDocument
                    │                                        │
                    │              ┌─────────────────────────┼───────────────┐
                    │              │ RequirementImprover     │               │
                    │              │ (sequential, first)     │               │
                    │              └────────────┬────────────┘               │
                    │                           ▼                            │
                    │              ┌────────────┴────────────┐              │
                    │              │   ThreadPoolExecutor     │              │
                    │              │  ┌──────────────────┐   │              │
                    │              │  │ ConflictDetector  │   │              │
                    │              │  │ GapAnalyzer       │   │              │
                    │              │  └──────────────────┘   │              │
                    │              └────────────┬────────────┘              │
                    │                           ▼                            │
                    │                     AnalysisReport                     │
                    │                           │                            │
                    │              ┌────────────┴────────────┐              │
                    │              │   ThreadPoolExecutor     │              │
                    │              │  (5 parallel workers)    │              │
                    │              │  ┌──────────────────┐   │              │
                    │              │  │ SRS PDF           │   │              │
                    │              │  │ Backlog XLSX      │   │              │
                    │              │  │ User Stories DOCX │   │              │
                    │              │  │ BDD .feature      │   │              │
                    │              │  │ JSON Report       │   │              │
                    │              │  └──────────────────┘   │              │
                    │              └──────────────────────────┘              │
                    └───────────────────────────────────────────────────────┘
```

### Design Patterns

| Pattern | Purpose |
|---|---|
| **Pipeline / Chain** | Sequential text processing across NLP stages |
| **Singleton (Memoized)** | Heavy NLP models loaded once via `@st.cache_resource` |
| **DTO (Pydantic v2)** | `Requirement → ParsedDocument → AnalysisReport` data flow with validation |
| **Strategy** | Interchangeable prompt templates for each LLM task |
| **Facade** | `LLMClient` hides OpenRouter/Gemini/DeepSeek API specifics |
| **Graceful Degradation** | Pipeline continues with NLP-only results if LLM unavailable |
| **Dependency Injection** | LLM client injected into all analyzers for testability |
| **Parallel Execution** | `ThreadPoolExecutor` for concurrent analysis and output generation |

---

## 📊 Performance Metrics

Evaluated on 3 independent datasets:

| Metric | Dev Corpus (244 sentences, 8 domains) | Held-out Corpus (113 sentences, 2 new domains) | Conflict Dataset (153 sentences, 50 conflict pairs) |
|---|---|---|---|
| **FR/NFR Classification** | 94.7% accuracy | 87.6% accuracy | — |
| **Actor Extraction — Precision** | 92.4% | 61.9% | — |
| **Actor Extraction — Recall** | 81.2% | 41.9% | — |
| **Actor Extraction — F1** | 86.5% | 50.0% | — |
| **Conflict Detection — Precision** | — | — | 94.2% |
| **Conflict Detection — Recall** | — | — | 98.0% |
| **Conflict Detection — F1** | — | — | 96.1% |

> **Note:** Held-out corpus covers healthcare and automotive (autonomous driving) domains never seen during development. The drop in actor extraction F1 (50.0%) reflects limitations of rule-based NER with unseen technical terminology — future work targets transformer-based NER integration.

---

## 🔧 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.8+ | Core runtime |
| **NLP Engine** | Stanza 1.11 | Tokenization, POS tagging, lemmatization, dependency parsing |
| **LLM** | Gemini 2.5 Flash (via OpenRouter) | Conflict detection, gap analysis, improvement, story/BDD generation |
| **LLM Fallback** | Google Gemini API → DeepSeek API | Triple-fallback chain for reliability |
| **Web UI** | Streamlit 1.57 | 4-page interactive dashboard with i18n |
| **PDF Export** | fpdf2 2.8 | ISO 29148 SRS document generation with Turkish font support |
| **XLSX Export** | openpyxl 3.1 | Styled Product Backlog spreadsheets |
| **DOCX Export** | python-docx 1.2 | User Stories with formatted acceptance criteria |
| **Data Models** | Pydantic v2 | Type-safe schema validation with `validate_assignment` |
| **Logging** | Loguru | Structured logging with module binding |
| **Testing** | pytest 9.0 + syrupy | Unit, integration, regression, and snapshot testing |
| **VCS** | Git + GitHub | Scrum-based agile workflow |

---

## ⚙️ Installation

### Prerequisites

- **Python** 3.8 or higher
- **pip** package manager
- **Git**

### Step-by-Step Setup

```bash
# 1️⃣ Clone the repository
git clone https://github.com/AutoReq-DevTeam/AutoReq.git
cd AutoReq

# 2️⃣ Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Download the Stanza Turkish NLP model (~150 MB)
python -c "import stanza; stanza.download('tr')"

# 5️⃣ Configure environment variables
cp .env.example .env          # Linux / macOS
copy .env.example .env        # Windows
```

### Environment Variables

Create a `.env` file from the provided template and configure:

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENROUTER_API_KEY` | ✅ Yes (for LLM features) | — | Your OpenRouter API key ([get one here](https://openrouter.ai/keys)) |
| `GEMINI_API_KEY` | ❌ No (fallback) | — | Google AI Studio API key (used as fallback if OpenRouter fails) |
| `DEEPSEEK_API_KEY` | ❌ No (fallback) | — | DeepSeek API key (used as secondary fallback) |

> **💡 Note:** The core NLP pipeline (preprocessing, classification, NER, priority detection) works **without** any API key. Only LLM-powered features (conflict detection, gap analysis, requirement improvement, story/BDD generation) require `OPENROUTER_API_KEY`.

---

## 🚀 Usage

### Launch the Application

```bash
streamlit run app.py
```

The Streamlit dashboard will open automatically at **`http://localhost:8501`**.

### Quick Start

1. **Input** — Paste your raw requirements text or select a demo scenario (6 domains available)
2. **Analyze** — Click the "Analyze" button; the pipeline processes text through all 3 layers
3. **Review** — Explore results across tabbed panels:
   - 📋 **Requirements** — Classified list with FR/NFR labels, actors, objects, and priorities
   - ⚠️ **Conflicts** — Detected contradictions with severity and natural language explanations
   - 🔍 **Gaps** — Missing requirements with suggestions and confidence scores
   - ✨ **Improvements** — Side-by-side diff view of vague → measurable transformations
4. **Export** — Download generated artifacts:
   - 📄 SRS Document (PDF)
   - 📝 User Stories (DOCX)
   - 🧪 BDD Scenarios (.feature)
   - 📊 Product Backlog (XLSX)
   - 📦 Full Analysis Report (JSON)

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=core --cov=modules --cov=outputs

# Run only unit tests
pytest tests/test_core.py tests/test_modules.py tests/test_outputs.py -v

# Run integration tests
pytest tests/integration/ -v

# Run regression / snapshot tests
pytest tests/regression/ -v
```

---

## 📁 Project Structure

```
AutoReq/
├── app.py                          # 🎯 Entry point — Streamlit orchestrator (1,495 lines)
├── requirements.txt                # 📦 Python dependencies (pinned)
├── .env.example                    # 🔐 Environment variable template
│
├── core/                           # 🧩 Layer 1: NLP Preprocessing Engine
│   ├── models.py                   #   Pydantic v2 dataclasses (Requirement, ParsedDocument, AnalysisReport)
│   ├── pipeline.py                 #   ✅ Full orchestration — parallel analysis + 5-worker output generation
│   ├── preprocessor.py             #   ✅ Stanza pipeline + KVKK masking (TC ID, personal names)
│   ├── classifier.py               #   ✅ 3-layer hybrid: verb suffix → NFR keywords → LLM fallback
│   ├── ner.py                      #   ✅ Multi-layer actor/object extraction (684 lines)
│   ├── nlp_engine.py               #   NLP engine initialization
│   └── priority_detector.py        #   ✅ Rule-based priority with negation detection
│
├── modules/                        # 🧠 Layer 2: Intelligent Analysis (LLM)
│   ├── llm_client.py               #   ✅ Triple-fallback: OpenRouter → Gemini → DeepSeek (333 lines)
│   ├── llm_cache.py                #   ✅ Prompt caching with configurable TTL
│   ├── conflict_detector.py        #   ✅ 6-category pairwise conflict analysis
│   ├── conflict_prompts.py         #   Prompt templates for conflict detection
│   ├── gap_analyzer.py             #   ✅ Domain-aware gap detection with confidence scoring
│   ├── gap_prompts.py              #   Prompt templates + DOMAIN_REFERENCES checklists
│   ├── improver.py                 #   ✅ Batch vague→measurable transformation (parallel chunks)
│   ├── improver_prompts.py         #   Prompt templates for improvement
│   ├── story_prompts.py            #   Prompt templates for user story generation
│   ├── bdd_prompts.py              #   Prompt templates for BDD scenario generation
│   ├── analysis_report_parsing.py  #   LLM JSON → AnalysisReport normalizer
│   ├── llm_response_utils.py       #   extract_json_object(), confidence sorting, ID validation
│   └── logging_utils.py            #   Loguru-based module logger utilities
│
├── outputs/                        # 📄 Layer 3: Document Generators
│   ├── srs_generator.py            #   ✅ Dynamic ISO 29148 SRS PDF (11 data-driven sections, 655 lines)
│   ├── story_generator.py          #   ✅ LLM-powered User Story generator + DOCX export (362 lines)
│   ├── bdd_generator.py            #   ✅ LLM-powered Gherkin BDD generator + .feature export (386 lines)
│   ├── backlog_generator.py        #   ✅ Rule-based prioritized backlog with Fibonacci scoring (201 lines)
│   ├── exporters.py                #   ✅ Multi-format export: XLSX, DOCX, JSON (290 lines)
│   ├── logo_generator.py           #   Pillow-based logo PNG creator (CLI)
│   ├── logo.png                    #   Generated logo (used in SRS PDF header)
│   ├── fonts/                      #   Bundled DejaVuSans fonts for Turkish character support
│   └── generated/                  #   Runtime output artifacts (gitignored)
│
├── ui/                             # 🖥 Layer 4: Streamlit UI Components
│   ├── i18n.py                     #   ✅ Full Turkish/English internationalization (16.7KB)
│   ├── components.py               #   ✅ Reusable widgets: req_card, conflict_card, badges, diff views
│   ├── dashboard.py                #   Dashboard layout
│   ├── results.py                  #   Tabbed results panel
│   ├── file_loader.py              #   File upload handling
│   ├── state.py                    #   Session state initialization
│   └── pages/                      #   4-page navigation
│       ├── 01_input.py             #     Text input + demo scenario selection
│       ├── 02_analysis.py          #     Analysis progress + pipeline execution
│       ├── 03_results.py           #     Tabbed results (requirements, conflicts, gaps, improvements)
│       └── 04_export.py            #     Download panel for all artifact formats
│
├── tests/                          # 🧪 Comprehensive Test Suite (190 tests)
│   ├── conftest.py                 #   Fixtures, sys.path setup, LLM mock helpers
│   ├── test_core.py                #   Preprocessor, classifier, NER, models, priority tests
│   ├── test_classifier_60.py       #   Detailed FR/NFR classification tests
│   ├── test_ner_60.py              #   Actor/object extraction tests
│   ├── test_priority_60.py         #   Priority detection tests
│   ├── test_modules.py             #   Module-level integration tests
│   ├── test_conflict_detector_60.py#   Conflict detector with LLM mocking
│   ├── test_gap_analyzer_60.py     #   Gap analyzer with LLM mocking
│   ├── test_improver_60.py         #   Improver with LLM mocking
│   ├── test_llm_response_utils_60.py#  JSON extraction, filtering utilities
│   ├── test_outputs.py             #   SRS, story, BDD, backlog, exporter tests
│   ├── test_run_eval.py            #   Evaluation runner tests
│   ├── integration/                #   End-to-end pipeline tests
│   │   └── test_e2e.py             #     6 E2E tests covering full pipeline
│   ├── regression/                 #   Golden contract + prompt snapshot tests
│   │   ├── test_golden_contract.py #     Contract tests against known outputs
│   │   ├── test_llm_mock_fixtures.py#    LLM mock fixture validation
│   │   └── test_prompt_snapshots.py#     Syrupy prompt snapshot tests
│   └── golden/                     #   Golden test data files
│
├── data/                           # 📊 Datasets & Demo Content
│   ├── demo_scenarios/             #   6 domain-specific demo texts
│   │   ├── 01_e_ticaret_celisma.txt
│   │   ├── 02_bankacilik_eksik.txt
│   │   ├── 03_egitim_mughrak.txt
│   │   ├── 04_kurumsal_portal_multi_actor.txt
│   │   ├── 05_mobil_app_nfr_agirlikli.txt
│   │   └── 06_saglik_heldout.txt
│   ├── evaluation/                 #   Evaluation corpora
│   │   ├── dev_corpus.json         #     244 sentences across 8 domains (48KB)
│   │   ├── heldout_corpus.json     #     113 sentences — healthcare + automotive (21KB)
│   │   └── conflict_pairs.json     #     50 intentional conflict pairs + controls (21KB)
│   ├── samples/                    #   Sample input texts
│   └── templates/                  #   JSON requirement templates
│
└── docs/                           # 📚 Documentation
    ├── AGENT_GUIDE.md              #   ⭐ Comprehensive project tutorial (41KB)
    ├── CONTEXT.md                  #   Source-of-truth architecture reference
    ├── FEATURES.md                 #   Feature list & implementation status
    ├── SRS.md                      #   Software Requirements Specification
    ├── AGENTS.md                   #   AI agent integration guide
    ├── Makale/                     #   Academic article drafts
    ├── AutoReq-Pres.pdf            #   Project presentation (1MB)
    └── *.png                       #   UI screenshots (input, analysis, results, export)
```

> 📌 **For AI assistants and new contributors:** start with [`docs/AGENT_GUIDE.md`](./docs/AGENT_GUIDE.md) — it lets you fully understand the project without reading any source file.

---

## 📂 Outputs

Once analysis is complete, AutoReq generates the following artifacts (all produced in parallel):

| Output | Format | Source | Description |
|---|---|---|---|
| 📄 **SRS Document** | PDF | Dynamic (AnalysisReport) | ISO/IEC/IEEE 29148 compliant, 11 data-driven sections |
| 📝 **User Stories** | DOCX | LLM (Gemini) | Agile stories with acceptance criteria |
| 🧪 **BDD Scenarios** | .feature (Gherkin) | LLM (Gemini) | Happy path + negative scenarios per requirement |
| 📊 **Product Backlog** | XLSX | Rule-based scoring | Fibonacci story points, conflict-weighted prioritization |
| 📦 **Analysis Report** | JSON | Full pipeline | Complete AnalysisReport with all data (Pydantic serialized) |

---

## 🧪 Testing

AutoReq has a comprehensive test suite with **190 tests** (including 106 snapshot tests):

```
tests/
├── Unit Tests          — Core NLP modules (preprocessor, classifier, NER, priority)
├── Module Tests        — LLM-dependent modules with mocked clients
├── Output Tests        — All 4 generators + 3 exporters
├── Integration Tests   — 6 end-to-end pipeline tests
├── Regression Tests    — Golden contracts + prompt snapshot tests (syrupy)
└── Evaluation Runner   — Corpus-based metric evaluation
```

```bash
# Full test suite (~500 seconds)
pytest tests/ -v

# Quick smoke test
pytest tests/test_core.py -v
```

---

## 🗺 Roadmap

```
Phase 1 — Core Analysis Engine                                 ✅ Complete
├── ✅ Text preprocessing pipeline (Stanza + KVKK masking)
├── ✅ 3-layer hybrid FR/NFR classifier (94.7% accuracy)
├── ✅ Multi-layer actor & object extraction (86.5% F1)
└── ✅ Rule-based priority detection with negation handling

Phase 2 — Intelligent LLM Modules                              ✅ Complete
├── ✅ Conflict detector — 6-category pairwise analysis (96.1% F1)
├── ✅ Gap analyzer — domain-aware with confidence scoring
├── ✅ Requirement improver — batch vague→measurable transformation
└── ✅ Triple-fallback LLM client (OpenRouter → Gemini → DeepSeek)

Phase 3 — Output Generation                                    ✅ Complete
├── ✅ Dynamic ISO 29148 SRS PDF (11 sections, Turkish fonts)
├── ✅ User Story generator + DOCX export
├── ✅ BDD Gherkin scenario generator + .feature export
├── ✅ Product Backlog generator + XLSX export
└── ✅ Multi-format exporters (JSON, XLSX, DOCX)

Phase 4 — UI & Developer Experience                            ✅ Complete
├── ✅ 4-page Streamlit dashboard with light/dark mode
├── ✅ Turkish/English i18n
├── ✅ 6 demo scenarios across different domains
├── ✅ 190-test suite (unit, integration, regression, snapshot)
└── ✅ Evaluation corpora (dev, held-out, conflict)

Phase 5 — Future Enhancements                                  📋 Planned
├── 🔲 Transformer-based NER (BERT/LLM) for unseen domains
├── 🔲 English & German language support
├── 🔲 Jira / Azure DevOps API integration
└── 🔲 User experience studies with professional business analysts
```

---

## 🤝 Contributing

Contributions are welcome! Follow our Scrum-based development workflow:

### Getting Started

1. **Fork** the repository
2. **Create** a feature branch from `develop`
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Commit** your changes using [conventional commits](https://www.conventionalcommits.org/)
   ```bash
   git commit -m "feat: add new analysis module"
   ```
4. **Push** your branch
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Open** a Pull Request against `develop`

### Commit Prefixes

| Prefix | Usage |
|---|---|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation changes |
| `test:` | Adding or updating tests |
| `prompt:` | LLM prompt modifications |

### Code Standards

- ✅ Every public function/class must have a **docstring**
- ✅ **Type hints** are required on all function signatures
- ✅ Use `field(default_factory=list)` for mutable defaults in dataclasses
- ✅ No `print()` in production code — use **Loguru** for logging
- ✅ PRs require at least **1 reviewer** approval

> 👥 For team structure and role assignments, see [TEAM.md](./docs/TEAM.md).

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0** — see the [LICENSE](./LICENSE) file for details.

---

<div align="center">

Built with ❤️ by the **AutoReq-DevTeam**

*Better software starts with better requirements.*

</div>