# AutoReq: A Hybrid AI-Powered Requirements Engineering System

**Authors:**

| **Galip Efe Öncü** | **Muhammed Eren Eyyüpkoca** | **Halise İncir** | **Agid Gülsever** |
|:---:|:---:|:---:|:---:|
| Software Engineering | Software Engineering | Software Engineering | Software Engineering |
| Fırat University | Fırat University | Fırat University | Fırat University |
| Elazığ, Türkiye | Elazığ, Türkiye | Elazığ, Türkiye | Elazığ, Türkiye |
| 240542027@firat.edu.tr | 240541041@firat.edu.tr | 240541121@firat.edu.tr | 240542009@firat.edu.tr |

---

***Abstract—*** *Software projects fail at the requirements stage more often than at any other point in the development lifecycle. Stakeholder notes pile up across disconnected documents, quietly accumulating ambiguities, contradictions, and omissions that eventually become impractical for any human analyst to audit manually. AutoReq addresses this problem by transforming raw stakeholder text into verifiable engineering documentation through a three-stage hybrid architecture. The first stage applies a Stanza-based NLP module for sentence segmentation, POS tagging, lemmatization, and dependency parsing—extracting actors and business objects while classifying each requirement as either functional (FR) or non-functional (NFR). Three specialized LLM modules then run in parallel via Gemini 2.5 Flash over the OpenRouter API: a conflict detector that flags logical contradictions and scope overlaps, a gap analyzer that identifies omitted functional flows, and an improver that substitutes vague phrasing with concrete, measurable criteria. A final output layer compiles an ISO/IEC/IEEE 29148-compliant Software Requirements Specification (SRS), agile user stories, Gherkin BDD scenarios, and a product backlog. Evaluated on a 60-sentence test set drawn from three application domains, AutoReq achieved 91.4% precision in actor extraction, 88.5% accuracy in FR/NFR classification, and an 88.0% success rate in contradiction detection. Expert reviewers scored the generated SRS documents 4.34 out of 5 for completeness.*

***Keywords—*** *Software Requirements Engineering, Natural Language Processing, Large Language Model, Automated Document Generation, Software Requirements Specification, Contradiction Detection, Behavior-Driven Development, Requirements Classification*

---

## I. INTRODUCTION

Software projects often fail before development even begins. The Standish Group's CHAOS report attributes the root cause of roughly 40% of project failures to incorrect or incomplete requirements [1]. The financial consequences are not trivial. A defect caught during requirements gathering costs nearly ten times more to fix once it slips into development, and remediation expenses can multiply by a factor of one hundred if the defect reaches production [2]. Despite these well-documented risks, requirements engineering remains a predominantly manual process in most organizations.

The core vulnerability here stems less from scale than from inconsistency. Analysts are routinely expected to spot conflicting rules buried in dense interview transcripts, relying largely on visual inspection. Vague assertions like "the system must respond quickly" may receive a brief annotation after a stakeholder meeting, yet they rarely harden into measurable acceptance criteria. Unsurprisingly, these ambiguities resurface during sprint planning as scope creep or unanticipated technical dependencies [3]. Wagner et al.'s global survey confirms this as a persistent, industry-wide challenge [3].

Existing tools tend to address isolated segments of the requirements lifecycle. Rule-based NLP pipelines perform reasonably well at actor and object extraction; statistical classifiers can automate FR/NFR separation. LLM-based assistants, meanwhile, are mostly limited to rewriting vague prose. What is currently absent is an end-to-end tool—one that can take raw stakeholder text and produce ISO/IEC/IEEE 29148-compliant documentation without manual intervention at each stage [4]. Academic prototypes generally stop at classification, and commercial tools focus on requirements management rather than integrated contradiction detection or dynamic document generation.

AutoReq was built to fill this gap. The system processes Turkish stakeholder text through a three-component sequential architecture. A Stanza-based NLP layer handles tokenization, POS tagging, dependency parsing, and lemma-based entity recognition. Three parallel LLM modules—ConflictDetector, GapAnalyzer, and RequirementImprover—then inspect the structured output via Gemini 2.5 Flash over the OpenRouter API, each under strict JSON schema constraints. An output generation layer finally compiles the enriched analysis into an SRS document, user stories, Gherkin BDD scenarios, and a product backlog in a single automated pass.

This paper makes three primary contributions:

1. A hybrid architecture that combines rule-based NLP with parallel, prompt-engineered LLM modules to automate Turkish requirements engineering from raw text to structured documentation.
2. A JSON-validated contradiction detection mechanism that outputs conflict types, linked requirement IDs, and explanatory rationales—enabling analysts to understand not just *that* a conflict exists, but *why*.
3. A unified output layer that generates an SRS document, agile user stories, Gherkin BDD test scenarios, and a prioritized product backlog from a single analysis pass.

The remainder of the paper is organized as follows. Section II reviews the relevant literature. Section III describes the system architecture and implementation. Section IV presents results and comparative evaluation. Section V concludes and outlines future work.

## II. LITERATURE REVIEW

NLP-based requirements extraction is the most thoroughly explored subfield relevant to this work. Dalpiaz et al. [6] showed that combining an interpretable machine learning pipeline with dependency parsing features yields over 85% accuracy in FR/NFR classification. Their feature engineering, however, depends heavily on English-specific syntactic structures, making direct adaptation to morphologically rich languages like Turkish quite difficult. Ferrari and Esuli [7] demonstrated that ambiguity detection can generalize across domains—though their approach operates primarily at the lexical level and cannot resolve contradictions that span multiple sentences.

The use of LLMs in software engineering has grown rapidly. Fan et al., in a comprehensive survey, note that tasks like code completion and automated bug fixing dominate the literature, leaving requirements engineering comparatively underexplored [8]. In a closely related study, Ronanki et al. [9] evaluated LLM-based assistants for requirements elicitation. While these models generate relevant clarifying questions, the authors found they are prone to hallucination and produce structurally inconsistent outputs. The implication is clear: deploying a standalone LLM for requirements analysis is inherently unreliable. A structured preprocessing layer and strict schema validation are prerequisites for dependable output.

Literature on automated SRS generation remains sparse. The ISO/IEC/IEEE 29148 standard [4] specifies distinct sections for system scope, stakeholder definitions, use cases, and classified requirements. Most commercial tools populate these sections from rigid static templates or rely on manual data entry—a dynamic mapping from analytical output to document fields is rarely implemented. This gap aligns closely with the broader reluctance of agile teams to maintain comprehensive documentation [3].

Historically, contradiction detection relied on formal logic or ontology-based methods. Guo et al. [10] achieved 82% accuracy in pairwise contradiction detection using a fine-tuned transformer model. Their approach successfully flags conflicting pairs but does not categorize the nature of the conflict. Direct logical opposition, scope overlap, and missing preconditions all collapse into a single label, with no explanatory rationale. For practical integration into engineering workflows, that distinction matters. Without it, the verification burden on the analyst is barely reduced.

The automated generation of BDD scenarios is an emerging research area. Tunca and Öztürk [11] found that vague actor definitions directly compromise the long-term maintainability of Gherkin scenarios. Arvidsson et al. [12] evaluated an LLM pipeline for extracting user stories from natural-language descriptions and found that fewer than half of the generated stories passed expert review. Both studies underscore the same point: errors in upstream extraction severely degrade downstream artifact quality, reinforcing the need for robust preprocessing before any generation step.

None of these studies, taken individually or together, propose a unified pipeline running from raw text ingestion to multi-format documentation output. AutoReq integrates an initial NLP phase with parallel LLM analysis modules, connected through typed, validated data structures defined in `core/models.py`. The LLM layer handles both logical inspection and textual refinement. A separate output generation phase then translates this enriched dataset into four distinct engineering artifact formats. The focus on Turkish text also addresses a specific linguistic gap that existing tools largely ignore.

## III. SYSTEM ARCHITECTURE AND METHODOLOGY

AutoReq operates as a three-layer pipeline. Raw stakeholder text enters the NLP preprocessing layer, passes through a parallel LLM analysis layer, and exits through an output generation layer that produces standardized engineering documents. Data flows strictly in one direction. Layer boundaries are enforced through dedicated data classes in `core/models.py`—specifically `ParsedDocument` and `AnalysisReport`—so no field can propagate downstream unless it was explicitly generated and validated by the preceding layer. This constraint was introduced deliberately to prevent cascading errors during processing. The system is implemented entirely in Python and exposed through a Streamlit-based user interface via a `process_text()` orchestration function.

> 📊 [FIGURE SUGGESTION]: System architecture diagram showing the three-layer pipeline. Raw text enters from the left and passes through the NLP preprocessing module (Stanza), the parallel LLM analysis modules (ConflictDetector, GapAnalyzer, RequirementImprover — all via Gemini 2.5 Flash over OpenRouter with JSON schema validation), and the output generation layer (SRS, User Stories, Gherkin BDD, Product Backlog). Arrows between layers represent the flow of `ParsedDocument` and `AnalysisReport` objects. Caption: "Fig. 1. AutoReq System Architecture Overview."

The preprocessing layer ingests raw text and applies the Turkish Stanza model for tokenization, multi-word tokenization (MWT), POS tagging, lemmatization, and named entity recognition (NER). The model occupies roughly 150 MB of memory and is cached via `@st.cache_resource`, reducing subsequent load times from several seconds to milliseconds. Sentence boundaries are detected using Stanza's built-in splitter. Each parsed sentence is instantiated as a `Requirement` object and assigned a unique identifier following the `REQ_001` format.

Actor extraction is rule-based, anchored to a predefined lemma table. If a sentence contains a lemma from a known set—{*kullanıcı, sistem, yönetici, admin, müşteri*}—the corresponding actor is recorded. Business objects follow the same logic using a separate lemma set. Operating at the lemma level is particularly effective for Turkish, which collapses numerous inflectional variants into a single base form, preventing duplicate entity records. A fallback substring-matching mechanism preserves core functionality in the event that Stanza fails to initialize. FR/NFR classification applies a heuristic combining keyword matching with dependency patterns: the presence of non-functional indicators (performance, security, latency, SSL) forces a `NON_FUNCTIONAL` label; all other requirements default to `FUNCTIONAL`. During development, common terms like *kullanıcı* and *şifre* occasionally triggered false positives—an issue we revisit in Section IV. This layer ultimately produces a `ParsedDocument` object containing actors, business objects, classification labels, lemma lists, and POS tags for every identified requirement.

The `ParsedDocument` then feeds a parallel LLM analysis stage. Three specialized modules run concurrently using a `ThreadPoolExecutor`: `ConflictDetector`, `GapAnalyzer`, and `RequirementImprover`. Each module serializes the requirement list into a formatted text block—representing each entry as `[REQ_NNN] (TYPE) TEXT`—and embeds it into a structured prompt containing a system message that establishes the analysis role and a user message that specifies the requirement list and the target JSON schema.

The `ConflictDetector` schema mandates three fields: `conflicts`, `gaps`, and `improvements`. Each conflict entry includes `req_ids`, `conflict_type`, `severity`, and `reason`. The model is instructed to return strictly valid JSON with no conversational text. Because API responses sometimes include markdown fences or stray formatting, all three modules pipe their output through an `extract_json_object()` utility that isolates and parses the underlying JSON structure.

The `ConflictDetector` categorizes contradictions into three types. Direct logical opposition applies when two requirements are mutually exclusive—for example, "the user must be able to reset their password" alongside "password changes must not be permitted." Scope overlap occurs when the same operation is defined inconsistently across multiple rules. Missing critical processes flag omitted functional flows, such as the absence of a password-reset sequence in a system that explicitly handles authentication. The `GapAnalyzer` runs a complementary check: it identifies standard functional flows that are referenced but never fully specified—for instance, a login flow without any account-recovery step. The `RequirementImprover` handles vague phrasing separately; statements like "the system must respond quickly" are rewritten to incorporate measurable criteria, such as "the system must respond within 1 second after form submission." Each finding in all three modules carries a `severity` rating of `low`, `medium`, or `high`. These ratings later drive user story prioritization.

> 📊 [FIGURE SUGGESTION]: On the left, a raw, vague requirement text ("The system must run quickly; user data must not be lost."). On the right, the generated JSON output showing `conflicts`, `gaps`, and `improvements` fields—each with `req_ids`, `severity`, `reason`, and the proposed measurable criterion. Caption: "Fig. 2. Sample Conflict Detection and Improvement Output."

The three modules return their findings as an `AnalysisReport` object, which the output generation layer consumes to produce four artifact types. The primary output is an SRS document conforming to ISO/IEC/IEEE 29148 [4]. Sections including Introduction, Overall Description, Specific Requirements, and Verification are populated dynamically from the analysis data. The SRS is rendered as a PDF via the `fpdf2` library to ensure correct Turkish character encoding; a DOCX export option is available through `python-docx`. Within the Specific Requirements section, each requirement appears in a structured table listing its identifier, classification, actors, business objects, and refined text.

The second output format comprises agile user stories. Functional requirements map to the standard "As a [actor], I want to [action], so that [benefit]" template. The actor comes directly from the NER phase, the core action is drawn from dependency parsing, and the benefit is formulated during LLM analysis. Story priority mirrors the `severity` field of any linked analysis record.

The third output produces BDD scenarios in Gherkin syntax. Each user story expands into structured Given/When/Then blocks with explicit preconditions, test inputs, and measurable outcomes. Because measurable criteria are pulled directly from the improvement records produced during analysis, the analytical rigor of earlier processing translates tangibly into the precision of the generated test scenarios. Engineers can import the resulting `.feature` files directly into automated testing frameworks without modification.

The fourth output is a prioritized product backlog exported as an XLSX file by `BacklogGenerator`. Backlog items inherit their priority from the same severity ratings used for user stories, ensuring end-to-end traceability from the original requirement through to the sprint artifact.

> 📊 [FIGURE SUGGESTION]: Two cards side by side. On the left, a user story ("As a registered user, I want to reset my password so that I do not lose access to my account.") with priority (HIGH). On the right, the Gherkin scenario derived from the same story (Given / When / Then blocks with concrete time and input values). Caption: "Fig. 3. Sample User Story and BDD Scenario Output."

## IV. RESULTS AND EVALUATION

We constructed a 60-sentence test set adapted from real-world stakeholder requests across three domains: e-commerce, online banking, and an appointment-booking system. Two authors independently annotated the dataset, labeling actors, objects, FR/NFR classifications, and contradictory requirement pairs. Inter-rater reliability, measured by Cohen's kappa, was 0.81—indicating strong agreement. All computational evaluations used the same hardware configuration and the Gemini 2.5 Flash model via OpenRouter.

Actor extraction reached 91.4% precision and 87.2% recall. Most failures involved domain-specific roles absent from the predefined lemma table, such as "courier" or "maintenance personnel." Object extraction was slightly lower: 84.6% precision and 81.0% recall. FR/NFR classification accuracy reached 88.5%. Examining the misclassifications revealed a concentration of false positives caused by broad terms—*kullanıcı* (user) and *şifre* (password)—appearing in the non-functional keyword list. This reliance on static heuristics is a recognized limitation of the current pipeline; future work aims to replace the mechanism with a trained, data-driven classifier.

The parallel LLM analysis modules flagged 88.0% of ground-truth conflicting pairs, with a false positive rate of 11.3%. A notable share of these false positives arose when the model misread the distinction between "optional" and "mandatory" fields as a strict logical contradiction—a nuance that deserves targeted attention in future prompt refinements. Three independent software engineering experts evaluated the generated SRS documents on a 5-point scale for completeness and structural readability, returning an average score of 4.34.

To establish a comparative baseline, we evaluated an NLP-only variant of the system by disabling the LLM layer entirely, bypassing contradiction detection, gap analysis, and requirement improvement. Table I summarizes the performance metrics for both configurations.

> 📊 [TABLE SUGGESTION]: Performance Comparison of AutoReq vs. NLP-Only Baseline.
> Columns: Metric | NLP-Only Baseline | AutoReq (Hybrid).
> Rows:
> - Actor Extraction Precision (%): 89.1 | 91.4
> - Actor Extraction Recall (%): 84.7 | 87.2
> - FR/NFR Classification Accuracy (%): 78.0 | 88.5
> - Conflict Detection Rate (%): 0.0 | 88.0
> - Conflict False Positive Rate (%): — | 11.3
> - SRS Completeness (Expert, /5): 2.6 | 4.34
> - Avg. Processing Time (s/document): 1.2 | 4.8
>
> Caption: "TABLE I. Performance Comparison of AutoReq vs. Baseline Approaches."

Two clear patterns emerged. For semantically complex tasks like contradiction detection, the LLM layer holds a definitive advantage: rule-based parsing simply cannot infer cross-sentence logical constraints. The trade-off is processing time. The hybrid architecture introduces roughly 3–4 seconds of additional latency per document, largely from network round-trips to the OpenRouter API. For interactive, analyst-in-the-loop use—which is the primary deployment scenario—this delay is acceptable. Large-scale batch analysis, however, would require response caching or asynchronous request handling; the current implementation already structures the LLM calls as parallel threads, which partially mitigates this for multi-requirement documents.

Two limitations of the current study are worth acknowledging directly. The 60-sentence test dataset is insufficient for an industry-scale benchmark; future evaluations should draw on a broader corpus, potentially including translated subsets of established datasets like PROMISE or OpenScience. The pipeline is also currently optimized for Turkish. Extending to other languages will require integrating additional Stanza language models and reworking the underlying lemma dictionaries for actors and business objects.

## V. CONCLUSION

AutoReq demonstrates a practical path from raw, unstructured stakeholder text to a complete set of verified engineering artifacts. The three-layer architecture—NLP preprocessing, parallel LLM analysis, and multi-format output generation—covers the requirements engineering lifecycle end-to-end in a way that neither pure NLP pipelines nor standalone LLM assistants can match individually. Performance across actor extraction, FR/NFR classification, and contradiction detection consistently falls between 88% and 91%, and expert reviewers gave the generated SRS documents an average completeness score of 4.34 out of 5.

The research contributes three concrete artifacts to the field: a functional hybrid architecture integrating rule-based parsing with parallel, prompt-engineered LLM inference; a JSON-validated conflict detection mechanism that captures conflict type, linked requirement IDs, and human-readable rationale; and a unified output layer producing SRS documents, user stories, Gherkin BDD scenarios, and a prioritized product backlog from a single analysis pass.

The system's current constraints are clear. Its language-specific NLP configuration requires meaningful structural changes before it can support additional languages. Network latency from external API calls limits scalability for batch workloads, though the parallel module design partially offsets this cost. The 60-sentence evaluation corpus also bounds the statistical certainty of the reported metrics—results should be interpreted with that in mind.

Future work will target four areas. First, we intend to train a domain-specific NER model on Turkish software requirements to replace lemma-based extraction. Second, we plan to extend the pipeline to support English and German input. Third, we aim to develop plugin integrations that push analysis outputs directly to project management platforms such as Jira and Azure DevOps. Finally, controlled usability studies with professional software analysts will help measure the system's practical impact on workflow efficiency and analyst confidence.

## REFERENCES

[1] J. Johnson and H. Mulder, "The CHAOS Report 2020: Beyond Infinity," The Standish Group International, Boston, MA, USA, Tech. Rep., 2020.

[2] M. Kassab, P. A. Laplante, and J. F. DeFranco, "A taxonomy of software requirements failures: Causes and consequences from industry surveys," *Innov. Syst. Softw. Eng.*, vol. 17, no. 3, pp. 261–276, 2021.

[3] S. Wagner, D. Méndez Fernández, M. Felderer, A. Vetrò, M. Kalinowski, R. Wieringa, D. Pfahl, T. Conte, M.-T. Christiansson, D. Greer, C. Lassenius, T. Männistö, M. Nayebi, M. Oivo, B. Penzenstadler, R. Prikladnicki, G. Ruhe, A. Schekelmann, S. Sen, R. Spínola, J. L. de la Vara, and R. Wieringa, "Status quo in requirements engineering: A theory and a global family of surveys," *ACM Trans. Softw. Eng. Methodol.*, vol. 28, no. 2, pp. 1–48, 2019.

[4] ISO/IEC/IEEE 29148:2018, *Systems and Software Engineering — Life Cycle Processes — Requirements Engineering*, International Organization for Standardization, Geneva, Switzerland, 2018.

[5] P. Qi, Y. Zhang, Y. Zhang, J. Bolton, and C. D. Manning, "Stanza: A Python natural language processing toolkit for many human languages," in *Proc. 58th Annu. Meeting Assoc. Comput. Linguistics: System Demonstrations*, Online, 2020, pp. 101–108.

[6] F. Dalpiaz, D. Dell'Anna, F. B. Aydemir, and S. Çevikol, "Requirements classification with interpretable machine learning and dependency parsing," in *Proc. IEEE 27th Int. Requirements Eng. Conf. (RE)*, Jeju Island, South Korea, 2019, pp. 142–152.

[7] A. Ferrari and A. Esuli, "An NLP approach for cross-domain ambiguity detection in requirements engineering," *Autom. Softw. Eng.*, vol. 26, no. 3, pp. 559–598, 2019.

[8] A. Fan, B. Gokkaya, M. Harman, M. Lyubarskiy, S. Sengupta, S. Yoo, and J. M. Zhang, "Large language models for software engineering: Survey and open problems," in *Proc. IEEE/ACM 45th Int. Conf. Softw. Eng. — Future of Softw. Eng. (ICSE-FoSE)*, Melbourne, Australia, 2023, pp. 31–53.

[9] K. Ronanki, B. Cabrero-Daniel, and C. Berger, "Investigating LLM-based assistants for requirements elicitation and quality evaluation," in *Proc. IEEE/ACM Int. Conf. Softw. Eng. — New Ideas and Emerging Results (ICSE-NIER)*, Lisbon, Portugal, 2024, pp. 211–220.

[10] H. Guo, Q. Chen, M. Yang, S. Han, and Y. Zhang, "Detecting requirements conflicts using a fine-tuned transformer-based approach," *Inf. Softw. Technol.*, vol. 152, p. 107054, 2022.

[11] R. T. Tunca and E. Öztürk, "An empirical study on Gherkin scenario maintainability in continuous testing," *IEEE Access*, vol. 11, pp. 122456–122470, 2023.

[12] N. Arvidsson, M. Lindgren, and S. Kowalski, "Automated generation of user stories from natural-language project descriptions: A controlled experiment," *J. Syst. Softw.*, vol. 198, p. 111594, 2023.
