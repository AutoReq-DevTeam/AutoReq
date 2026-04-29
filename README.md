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
[![Status](https://img.shields.io/badge/Status-In%20Development-orange?style=for-the-badge)]()

</div>

---

## 📖 Table of Contents

- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Installation](#%EF%B8%8F-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Outputs](#-outputs)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 📌 About the Project

**Requirements engineering** is one of the most challenging and time-consuming phases in software development. Ambiguous customer language, missed edge cases, and contradictory statements can derail entire projects before a single line of code is written.

**AutoReq** solves this by combining **classical NLP** (Stanza/NLTK) for fast structural analysis with **Large Language Models** (Google Gemini) for deep semantic reasoning — creating a hybrid AI pipeline that converts unstructured customer text into professionally structured, industry-standard documentation.

> *"Better software starts with better requirements."*

### 🔑 Why AutoReq?

- 🕐 **Save hours** of manual requirements elicitation and documentation
- 🎯 **Catch conflicts** and missing requirements before they become costly bugs
- 📄 **Generate ISO-compliant** SRS documents automatically
- 🌐 **Turkish language native** — built specifically for Turkish NLP processing

---

## ✨ Key Features

### 🛠 Core NLP Engine
- **Text Preprocessing** — Sentence-level tokenization, stopword removal, and lemmatization using Stanza
- **Requirement Classification** — Automatic categorization into **Functional (FR)** and **Non-Functional (NFR)** requirements via heuristic keyword matching
- **Named Entity Recognition (NER)** — Detect actors (*User, System, Admin*) and objects (*password, form, database*) using lemma-based lookup with Stanza fallback

### 🧠 Intelligent Analysis (LLM-Powered)
- **Conflict Detection** — Pairwise analysis of requirements to identify logical contradictions via Google Gemini
- **Gap Analysis** — Identify missing requirements by comparing against standard templates *(in progress)*
- **Improvement Suggestions** — Transform vague statements like *"should be fast"* into measurable, testable criteria *(in progress)*

### 📂 Document Generation
- **SRS Generator** — Produce ISO/IEC/IEEE 29148 compliant Software Requirements Specification in PDF format
- **User Stories** — Generate Agile stories in *"As a [role], I want [goal], so that [benefit]"* format *(in progress)*
- **BDD Scenarios** — Create Gherkin-format *Given-When-Then* test scenarios *(in progress)*
- **Product Backlog** — Prioritized sprint backlog generation *(in progress)*

### 🖥 Interactive Dashboard
- **Streamlit-based UI** — Clean, single-page web dashboard with real-time analysis feedback
- **Demo Mode** — Pre-loaded sample text for instant demonstration
- **Tabbed Results** — Requirements, conflicts, gaps, and download panels organized in tabs

---

## 🏗 Architecture

AutoReq follows a **layered pipeline architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────────┐
│                       app.py (Orchestrator)                         │
│                       Streamlit Entry Point                         │
├─────────────┬───────────────┬───────────────┬───────────────────────┤
│   Layer 1   │    Layer 2    │    Layer 3    │       Layer 4         │
│   core/     │   modules/    │   outputs/    │       ui/             │
│             │               │               │                       │
│ Preprocessor│ LLM Client    │ SRS Generator │ Dashboard             │
│ Classifier  │ Conflict Det. │ Story Gen.    │ Results Panel         │
│ NER         │ Gap Analyzer  │ BDD Gen.      │ Reusable Components   │
│ Models      │ Improver      │ Backlog Gen.  │                       │
└─────────────┴───────────────┴───────────────┴───────────────────────┘
```

### Data Flow

```
Raw Text ─→ TextPreprocessor ─→ Classifier ─→ EntityRecognizer ─→ AnalysisReport
              (Stanza)          (Heuristic)     (Stanza NER)          │
                                                                      ▼
                                                                 Streamlit UI
                                                               (Tabbed Results)
```

### Design Patterns Used

| Pattern | Purpose |
|---|---|
| **Pipeline / Chain** | Sequential text processing across NLP stages |
| **Singleton (Memoized)** | Heavy NLP models loaded once via `@st.cache_resource` |
| **DTO (Dataclass)** | `Requirement → ParsedDocument → AnalysisReport` data flow |
| **Strategy** | Interchangeable prompt templates for LLM tasks |
| **Facade** | `LLMClient` hides Gemini API specifics |
| **Graceful Degradation** | Fallback to string matching if Stanza model unavailable |
| **Dependency Injection** | LLM client injected into analyzers for testability |

---

## 🔧 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.8+ | Core runtime |
| **NLP Engine** | Stanza / NLTK | Tokenization, POS tagging, lemmatization, NER |
| **LLM** | Google Gemini (via `google-generativeai`) | Conflict detection, gap analysis, document generation |
| **Web UI** | Streamlit | Interactive single-page dashboard |
| **PDF Export** | fpdf2 / ReportLab | ISO 29148 SRS document generation |
| **Data Validation** | Pydantic | Schema validation (future) |
| **Logging** | Loguru | Structured logging with module binding |
| **Testing** | pytest + pytest-cov | Unit testing and coverage reporting |
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

# 3️⃣ Install dependencies (includes google-generativeai for the Gemini LLM layer)
pip install -r requirements.txt

# 4️⃣ Download the Stanza Turkish NLP model (~150 MB)
python -c "import stanza; stanza.download('tr')"

# 5️⃣ Configure environment variables
cp .env.example .env          # Linux / macOS
copy .env.example .env        # Windows
```

> 💡 The core NLP layer (preprocessor / classifier / NER) runs without an API key. Only the LLM-powered modules (conflict detection, gap analysis) require `GEMINI_API_KEY` and the `google-generativeai` SDK.

### Environment Variables

Create a `.env` file from the provided template and configure:

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | ✅ Yes (for LLM features) | — | Your Google AI Studio API key ([get one here](https://aistudio.google.com/apikey)) |
| `GEMINI_MODEL_NAME` | ❌ No | `gemini-3.0-flash` | Gemini model variant to use |

> **💡 Note:** The core NLP pipeline (preprocessing, classification, NER) works **without** an API key. Only LLM-powered features (conflict detection, gap analysis) require `GEMINI_API_KEY`.

---

## 🚀 Usage

### Launch the Application

```bash
streamlit run app.py
```

The Streamlit dashboard will open automatically at **`http://localhost:8501`**.

### Quick Start

1. **Paste** your raw requirements text into the text area (or click the demo button for a sample)
2. **Click** the "Analyze" button
3. **Review** the results across the tabbed panels:
   - 📋 **Requirements** — Classified list with FR/NFR labels, actors, and objects
   - ⚠️ **Conflicts** — Detected contradictions between requirements
   - 🔍 **Gaps** — Missing requirements and suggestions
   - 📥 **Downloads** — Export your SRS document as PDF

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=core --cov=modules --cov=outputs
```

---

## 📁 Project Structure

```
AutoReq/
├── app.py                     # 🎯 Entry point — Streamlit orchestrator
├── requirements.txt           # 📦 Python dependencies
├── .env.example               # 🔐 Environment variable template
│
├── core/                      # 🧩 Layer 1: NLP Preprocessing Engine
│   ├── models.py              #   Shared dataclasses (Requirement, ParsedDocument, AnalysisReport)
│   ├── preprocessor.py        #   Stanza pipeline: tokenize → POS → lemma → filter
│   ├── classifier.py          #   FR / NFR heuristic classifier
│   └── ner.py                 #   Entity recognizer (actors & objects)
│
├── modules/                   # 🧠 Layer 2: Intelligent Analysis (LLM)
│   ├── llm_client.py              #   Centralized Gemini API client
│   ├── conflict_detector.py       #   ✅ Pairwise conflict analysis (LLM)
│   ├── conflict_prompts.py        #   Prompt templates for conflict detection
│   ├── gap_analyzer.py            #   ❌ Stub — NotImplementedError
│   ├── gap_prompts.py             #   Prompt templates for gap analysis (ready)
│   ├── improver.py                #   ❌ Stub — NotImplementedError
│   ├── analysis_report_parsing.py #   LLM JSON → AnalysisReport normalizer
│   ├── llm_response_utils.py      #   extract_json_object() utility
│   └── logging_utils.py           #   Loguru-based module logger utilities
│
├── outputs/                   # 📄 Layer 3: Document Generators
│   ├── srs_generator.py       #   ⚠️  Static ISO 29148 SRS PDF (no dynamic data yet)
│   ├── story_generator.py     #   ❌ Stub — User Story generator
│   ├── backlog_generator.py   #   ❌ Stub — Product Backlog generator
│   ├── bdd_generator.py       #   ❌ Stub — Gherkin BDD scenario generator
│   ├── logo_generator.py      #   Pillow-based logo PNG creator (CLI)
│   ├── logo.png               #   Generated logo (used in SRS PDF header)
│   ├── srs_taslak.pdf         #   Pre-generated static SRS template
│   └── generated/             #   Runtime output artifacts (gitignored, currently empty)
│
├── ui/                        # 🖥 Layer 4: Streamlit UI Components
│   ├── dashboard.py           #   Main input screen
│   ├── results.py             #   Tabbed results panel
│   └── components.py          #   Reusable widgets (req_card, badges, buttons)
│
├── tests/                     # 🧪 Test Suite (mostly stubs — see ROADMAP)
│   ├── conftest.py            #   sys.path setup
│   ├── test_core.py           #   Core module tests
│   ├── test_modules.py        #   Module tests
│   └── test_outputs.py        #   Output tests
│
├── data/                      # ⚠️  Currently empty placeholders
│   ├── samples/               #   (planned) sample input texts
│   └── templates/             #   (planned) JSON requirement templates
│
└── docs/                      # 📚 Documentation
    ├── AGENT_GUIDE.md         #   ⭐ Comprehensive agent-friendly project tutorial (Turkish)
    ├── TEAM.md                #   Team roles & RACI matrix (Turkish)
    ├── FEATURES.md            #   Feature list & status
    ├── CONTEXT.md             #   Source-of-truth architecture reference
    ├── ROADMAP_AND_ISSUES.md  #   Sprint backlog & issue tracker (Turkish)
    └── CHECKPOINTS/           #   Marp slide decks (Turkish)
```

> 📌 **For AI assistants and new contributors:** start with [`docs/AGENT_GUIDE.md`](./docs/AGENT_GUIDE.md) — it lets you fully understand the project without reading any source file.

---

## 📂 Outputs

Once analysis is complete, AutoReq can generate the following artifacts:

| Output | Format | Description |
|---|---|---|
| 📄 **SRS Document** | PDF | ISO/IEC/IEEE 29148 compliant Software Requirements Specification |
| 📝 **User Stories** | Text / Export | Agile stories in *"As a user, I want..."* format |
| 📋 **Product Backlog** | List / Export | Prioritized sprint work items |
| 🧪 **BDD Scenarios** | Gherkin | *Given-When-Then* formatted test scenarios |

---

## 🗺 Roadmap

```
Phase 1 — MVP (Core Analysis Engine)                          ✅ Complete
├── ✅ Text preprocessing pipeline (Stanza)
├── ✅ Functional / Non-Functional classifier
└── ✅ NER-based actor and object detection

Phase 2 — Intelligent Modules                                 🔧 In Progress
├── ✅ Conflict & contradiction detector (LLM) — implemented but NOT yet wired into app.py
├── 🔲 Gap analysis & suggestion engine        — prompts ready, analyzer is a stub
└── 🔲 Vague-expression improver               — stub

Phase 3 — Output & Integration                                📋 Planned
├── ⚠️ Automated SRS PDF generation (static template only — no dynamic data binding yet)
├── 🔲 User Story & Backlog export
├── 🔲 BDD scenario generator
└── 🔲 Jira / Trello integration (optional)
```

> 📎 For detailed sprint backlog and weekly task breakdown, see [ROADMAP_AND_ISSUES.md](./docs/ROADMAP_AND_ISSUES.md).

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