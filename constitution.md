# AI Powered SQL & Python Evaluation Framework Constitution

===========================

## Core Principles

---

### Principle 1 — Purpose & Scope

This project delivers a reproducible, client-operable Claude Agent Skill that evaluates AI-generated SQL and Python code across a fixed task bank, producing a comparative scorecard for three AI models. It serves Analytics Engineers, Data Engineers, and Evaluation Leads at a Banking Institution who need an objective, evidence-based basis for AI model selection in analytics engineering workflows. The outcome that matters most is a self-contained zipped skill folder that the client can invoke in Claude and immediately receive a complete, reproducible scorecard — accompanied by a README/quickstart guide requiring no prior training to use.

The task bank contains 200 tasks (100 SQL + 100 Python). The contracted client deliverable covers 40 tasks (20 SQL + 20 Python), identified by `contracted = true` in `assets/task_bank.csv`. The remaining 160 tasks are a value-add delivered beyond the contract. The `--contracted-only` CLI flag produces the client-facing scorecard covering only the contracted 40 tasks. The full 200-task scorecard is available via the default invocation and is delivered as a bonus deliverable.

### Principle 2 — AI as Dual-Role Actor

This project occupies a unique position: Claude simultaneously acts as the evaluation harness and is one of the models under evaluation. This dual role is managed through three non-negotiable rules. First, all scoring and ranking logic is enforced by deterministic scripts — Claude's own judgment is never the arbiter of evaluation results. Second, all model-generated code is anonymized before it enters the scoring pipeline, ensuring Claude-as-harness cannot favor or disadvantage any model. Third, the harness never executes model-generated code at runtime — it operates exclusively as a comparison and aggregation engine over pre-recorded evaluation data. Humans remain responsible for interpreting and acting on all scorecard outputs.

### Principle 3 — Machine-Readable Skill, Plain-Language Deliverables

`SKILL.md` must follow structured, machine-readable markdown per the Claude Agent Skills standard: YAML frontmatter with `name` and `description` fields, concise instructions, and progressive disclosure to sub-files. `SKILL.md` references `assets/task_bank.csv` by path in one line — it must not embed the task list inline. All client-facing deliverables — the scorecard report, README, and quickstart guide — must be written in plain language readable by non-developer stakeholders at the Banking Institution. Acronyms and technical terms are explained on first use in all deliverable documents.

### Principle 4 — Guardrails Over Features

Evaluation integrity rules — model anonymization, deterministic scoring, synthetic-only data, flat-file-only storage, and pre-recorded evaluation data — are non-negotiable constraints, not implementation preferences. If a proposed feature or shortcut conflicts with any guardrail, the guardrail wins. The three items currently marked `[TBD]` — maintainability rubric, scoring weights, and runtime variance window — are explicitly deferred to post-V1, not omitted. No work may proceed on these items until they are formally added to the Constitution via the approved change process.

### Principle 5 — Iterative Refinement via Observed Behavior

This Constitution is a living, versioned document. It is updated through the PR + PM approval process, not through unilateral fixes. Recurring gaps in Claude-as-harness behavior — unexpected evaluation paths, missed scoring rules, inconsistent output formats — must trigger `SKILL.md` updates and, where applicable, Constitution amendments. They are never addressed through one-off prompt adjustments. The weekly review cadence exists to surface and act on these patterns systematically.

### Principle 6 — Pre-Recorded Evaluation Data

All model-generated code, execution results, performance metrics, and formatting scores are captured outside the harness — during a manual dataset preparation phase — and bundled as pre-recorded flat-file assets in the skill folder. The harness reads, compares, and aggregates this pre-recorded data; it does not generate, execute, or measure it. This separation exists because: (a) Claude-as-harness cannot call external model APIs in V1 (no API keys, no external services); (b) executing untrusted model-generated code inside the harness would introduce safety and environment variability risks; (c) pre-recording all deterministic inputs guarantees fully reproducible scoring across independent invocations. The only content generated at harness runtime is the AI Critic persona reviews, which are qualitative and carry no numeric weight.

---

## Tech Stack & Platform Rules

---

### Approved Languages & Frameworks

**Primary Language**: Python 3.11+
**Evaluated Language**: SQL — SQL is the subject of evaluation tasks, not a runtime database language in V1
**Test Framework**: pytest — used during dataset preparation to validate model-generated Python code; not invoked by the harness at runtime
**Performance Measurement**: tracemalloc (Python peak memory) and `time` (wall-clock runtime) — used during dataset preparation to capture performance metrics; not invoked by the harness at runtime
**Formatting Validation**: flake8 (Python PEP8 violations) and sqlfluff (SQL style violations) — used during dataset preparation to capture formatting scores; not invoked by the harness at runtime
**Web/API Framework**: None — this skillset is not a web service. FastAPI, Flask, and all similar frameworks are explicitly prohibited in V1. An API framework for external data pulls (e.g., Kaggle CSVs) is deferred to post-V1.

### Skill Folder Structure

The deliverable follows the Claude Agent Skills standard:

```
eval-framework.zip
├── README.md
├── requirements.txt                  # All Python dependencies declared explicitly
├── run_scorecard.py                  # Scorecard CLI entry point
├── scorecard/                        # Scorecard package — spans both skills
├── references/                       # Shared: methodology, rubrics, file schema,
│                                     # deterministic rules — loaded on-demand only
├── assets/                           # Shared assets across both skills
│   ├── task_bank.csv                 # Master index — 200 tasks, contracted flag,
│   │                                 # prompt text inline, per-model code filenames.
│   │                                 # Scripts resolve all file paths through this index.
│   ├── eval_results.csv              # Unified pre-recorded metrics — 3,000 rows
│   │                                 # (200 tasks × 3 models × 5 variants).
│   │                                 # Primary key: (filename, dataset_variant).
│   │                                 # Single source of truth for all numeric scoring.
│   ├── tasks/                        # Per-task assets: prompt text in task_bank.csv;
│   │   └── [task_id]/                # code files (e.g. task1a.py, task1a.sql),
│   │                                 # reference_solution, reference_results (SQL),
│   │                                 # test_solution (Python)
│   └── datasets/                     # Five synthetic dataset variants
├── sql-skill/
│   ├── SKILL.md                      # YAML frontmatter + concise instructions.
│   │                                 # References assets/task_bank.csv by path only.
│   ├── scripts/                      # Python comparison/aggregation scripts
│   └── assets/personas/              # SQL Critic persona template
└── python-skill/
    ├── SKILL.md                      # YAML frontmatter + concise instructions.
    │                                 # References assets/task_bank.csv by path only.
    ├── scripts/
    └── assets/personas/              # Python Critic persona template
```

**SKILL.md rules**:

- Must begin with YAML frontmatter containing `name` and `description` fields
- `description` is the primary signal Claude uses to load the skill — it must be specific and action-oriented
- Do not use the `when_to_use` field — it is undocumented and unreliable; use `description` instead
- Body must be concise; verbose reference content belongs in `references/`
- Must reference `assets/task_bank.csv` by path — must not embed the task list inline

### Canonical File Format Standards

All scripts and outputs must conform to the following file format rules without exception. The canonical folder naming convention and file schema must be defined in a single `references/` document before any scripts are written.


| Content Type                                                                                                | Format   | Extension |
| ----------------------------------------------------------------------------------------------------------- | -------- | --------- |
| Machine-readable outputs, metrics, scorecard data, artifacts                                                | JSON     | `.json`   |
| Datasets, task bank, synthetic data, dataset variants, unified evaluation results, pre-recorded metric data | CSV      | `.csv`    |
| Human-readable content, reports, README, rubrics, methodology                                               | Markdown | `.md`     |


Artifacts are keyed by `task_id/model/category` in the folder structure.

### Pre-Recorded Evaluation Data Standards

All evaluation data is captured during the dataset preparation phase and bundled as flat-file assets. The architecture is a **two-table design** — one master index and one unified results table — indexed by filename-based identity. The following rules govern this data:

**Task Bank Index** — `assets/task_bank.csv`. Master index for all 200 tasks. 200 rows. One row per task.

- Schema: `task_id, contracted, category, prompt, model_a_filename, model_b_filename, model_c_filename`
- `task_id`: Primary key. `SQL-001` through `SQL-100`, `PY-001` through `PY-100`.
- `contracted`: Boolean. `true` for SQL-001–SQL-020 and PY-001–PY-020. Drives `--contracted-only` filtering.
- `category`: Difficulty enum — `easy`, `medium`, `hard`.
- `prompt`: Full standardized prompt text stored inline — identical across all three models.
- `model_a_filename`, `model_b_filename`, `model_c_filename`: Filenames of the three models' generated code files under `assets/tasks/[task_id]/`. E.g., `task1a.sql`, `task1b.sql`, `task1c.sql`.
- Language is encoded in the filename extension (`.py` → Python, `.sql` → SQL). No separate `language` column is required.
- Scripts resolve all file paths through this index — paths must not be hardcoded in scripts.

**Unified Evaluation Results** — `assets/eval_results.csv`. All pre-recorded evaluation metrics. Up to 3,000 rows (200 tasks × 3 models × 5 variants). One row per filename × dataset variant.

- Schema: `filename, dataset_variant, token_usage_input, token_usage_output, runtime_ms, peak_memory_bytes, formatting_violations, pytest_filename, pytest_pass, checksum, row_count, snapshot_pass`
- `filename`: Primary key component. E.g., `task1a.sql`, `task1a.py`. Encodes task number, model letter (a/b/c), and language (extension).
- `dataset_variant`: Primary key component. Enum — `clean`, `null_heavy`, `duplicate_heavy`, `medium`, `large`.
- `token_usage_input`, `token_usage_output`: Integer. Same value across all five variant rows for a given filename.
- `runtime_ms`: Integer. Wall-clock runtime in milliseconds against this variant's dataset. Varies per variant.
- `peak_memory_bytes`: Integer. Peak Python heap memory via tracemalloc. **Python files only — null for `.sql` filenames.**
- `formatting_violations`: Integer. flake8 violations (Python) or sqlfluff violations (SQL). Same value across all five variant rows for a given filename. `0` = clean.
- `pytest_filename`: String. Test file name used — e.g., `test_task1a.py`. **Python files only — null for `.sql` filenames.**
- `pytest_pass`: Boolean. `true` if all tests passed for this variant, `false` otherwise. Syntax errors and runtime exceptions recorded as `false`. **Python files only — null for `.sql` filenames.**
- `checksum`: String. SHA-256 hash of result set for this variant. **SQL files only — null for `.py` filenames.**
- `row_count`: Integer. Row count of result set for this variant. **SQL files only — null for `.py` filenames.**
- `snapshot_pass`: Boolean. `true` if result set matches reference snapshot for this variant. **SQL files only — null for `.py` filenames.**
- `generation_time_ms` is not captured in V1 and must not appear in this schema or any output artifact.

**Filename-Based Identity Convention**

- Pattern: `task{N}{model}.{ext}` where `N` is 1–100, `model` is `a` (Claude Sonnet 4.5), `b` (Gemini 2.5 Flash), or `c` (ChatGPT 5.2 Codex baseline), and `ext` is `py` or `sql`.
- Examples: `task1a.py`, `task1b.sql`, `task42c.py`, `task100a.sql`.
- The harness derives language from the extension and model identity from the letter before the extension. No `language` or `model_token` column is stored in `eval_results.csv` — they are derived from `filename` at load time.
- Real model names are mapped via `model_token_lookup.csv` held **outside the zip** and re-associated only at scorecard generation time.
- SQL tasks and Python tasks both use numbers 1–100. Filenames remain unambiguous because language is encoded by the extension and code files live under per-task directories (`assets/tasks/[task_id]/`).

**Authoring Workflow (Parallel Team Convention)**

Three team members generate the pre-recorded data independently — one per model — on separate machines. Each produces a per-author file:

- `results_a.csv` — 1,000 rows (100 SQL + 100 Python tasks × 5 variants), all rows where `filename` ends in `a.{py|sql}`
- `results_b.csv` — 1,000 rows, all rows where `filename` ends in `b.{py|sql}`
- `results_c.csv` — 1,000 rows, all rows where `filename` ends in `c.{py|sql}`

Each per-author file uses the identical `eval_results.csv` schema above. These files are **an authoring convention only** — they are not deliverables and must not be bundled in the zip. Before release, they are merged into `assets/eval_results.csv` by a merge script that:

1. Validates that all three files share identical headers matching the canonical schema
2. Validates that the `dataset_variant` column contains only the five canonical values
3. Validates that no `(filename, dataset_variant)` pair appears in more than one source file
4. Concatenates rows into a single `eval_results.csv`
5. Validates that the merged file has exactly `3 × (rows_expected_per_author)` rows and no duplicate primary keys

Merge failures halt the release. The merge script and its self-test are owned by Feature 1.

**Integrity Rules**

- All pre-recorded data must be generated using the tools declared in the Tech Stack (pytest, tracemalloc, flake8, sqlfluff) during the dataset preparation phase
- Pre-recorded metrics must match the exact schema defined in `references/file-schema.md`
- `model_token` identifiers (used in `outputs/` directory paths and downstream `result.json` artifacts) must be consistent with the filename suffix convention (`a` → `model_a`, `b` → `model_b`, `c` → `model_c`). Real model names are mapped in a separate lookup file held outside the zip and re-associated only at scorecard generation time.
- The `contracted` field in `task_bank.csv` is the sole source of truth for contracted-scope filtering. `schema_validator.py` must validate that every `task_id` referenced by a `filename` in `eval_results.csv` resolves to a row in `task_bank.csv` before scoring begins. Any discrepancy is a validation failure that halts the pipeline.

### Deterministic Comparison Rules

All evaluation scoring and ranking is enforced by deterministic scripts. The following generally accepted principles apply and must be documented in `references/` before the first evaluation run. Specific values (epsilon, seeds) are declared in `references/` and must not be hardcoded in scripts.

- **Floating point comparisons**: Use epsilon tolerance per IEEE 754 standard
- **Random sampling**: Use fixed, explicitly declared random seeds
- **SQL result comparison**: Use `ORDER BY` on stable keys or set-based equivalence
- **Scoring aggregation**: Script-enforced — no LLM judgment in ranking logic

### Models Under Evaluation (V1)


| Role      | Model             | Filename Letter |
| --------- | ----------------- | --------------- |
| Evaluated | Claude Sonnet 4.5 | `a`             |
| Evaluated | Gemini 2.5 Flash  | `b`             |
| Baseline  | ChatGPT 5.2 Codex | `c`             |


### API Keys

API key handling is not in scope for V1. No API key rules, storage, or credential management apply to this version. API key management will be explicitly defined in a future Constitution amendment when external service integration is introduced. Model code generation is performed outside the harness during dataset preparation using Cursor and model-specific plugins — these tools are not part of the harness or the deliverable.

### Infrastructure & Deployment

**V1 Environment**: Local development only

- No cloud infrastructure (AWS, Azure, GCP)
- No Docker, Kubernetes, or containerization of any kind
- No managed cloud services or remote servers
- No database — flat files only (see Canonical File Format Standards above)
- No execution of model-generated code by the harness at runtime

**Delivery**: Zipped skill folder uploaded to Claude.ai or via the Anthropic API

**Post-V1 (Deferred)**:

- PostgreSQL as preferred persistent document store
- API framework for external data pulls

### Performance & Cost Considerations

- Prefer CPU-friendly models; avoid GPU-only solutions
- `SKILL.md` must be kept concise — verbose content delegated to `references/` to minimize context window consumption
- Progressive disclosure enforced: metadata → `SKILL.md` → sub-files, only as needed
- `assets/task_bank.csv` is the index layer — scripts load it to resolve paths; its content is never embedded in `SKILL.md`

### Explicit Prohibitions (V1)

- No FastAPI, Flask, or any web/API framework
- No external services beyond PM-approved integrations
- No `when_to_use` YAML field in `SKILL.md`
- No Docker, Kubernetes, or containerization
- No cloud infrastructure (AWS, Azure, GCP)
- No database of any kind
- No API key handling or credential management
- No GPU-only dependencies
- No execution of model-generated code by the harness at runtime
- No live invocation of pytest, tracemalloc, flake8, or sqlfluff by the harness — these are dataset preparation tools only
- No hardcoded file paths in scripts — all paths resolved via `assets/task_bank.csv`
- No real model names in code filenames, `eval_results.csv` rows, directory paths, or any file inside the skill folder — filename-letter convention (`a`/`b`/`c`) or `model_token` identifiers only
- No per-author `results_a.csv` / `results_b.csv` / `results_c.csv` in the released zip — these are an authoring convention only; only the merged `eval_results.csv` is shipped

---

## Security, Privacy & Data Boundaries

---

### Client Identity

The client is referred to exclusively as "Banking Institution" in all internal project documents, including this Constitution, all specs, all plans, and all skill assets. The client's actual name must not appear anywhere in the skill folder, version control history, or any internal artifact.

### Synthetic Data Rules

- All datasets bundled in the skill folder are synthetic only — no real financial data is permitted at any stage
- Every synthetic dataset must be explicitly labeled as synthetic in both its filename and its file header
- Synthetic data must not replicate real financial record formats closely enough to be mistaken for actual data — no real-looking account numbers, routing numbers, transaction IDs, or customer identifiers
- No real data provided by the Banking Institution may be introduced into the skill folder or evaluation workflow at any point in V1

### Model Anonymization & Evaluation Integrity

- All model-generated code must be anonymized before it enters the evaluation scoring pipeline
- Code filenames use the filename-letter convention (`a`/`b`/`c`) only — never real model names. This is the anonymized identifier in all pre-recorded data.
- `model_token` — derived from the filename letter at load time (`a` → `model_a`, `b` → `model_b`, `c` → `model_c`) — is the anonymized identifier used in `outputs/` directory paths and downstream `result.json` artifacts
- Model identifiers (Claude Sonnet 4.5, Gemini 2.5 Flash, ChatGPT 5.2 Codex) must be stripped from all outputs before the harness evaluates them
- Evaluation logs must not contain model identifiers until after all scoring is complete
- The model name ↔ filename-letter mapping is maintained in a separate lookup file held outside the skill folder's scoring pipeline
- This rule exists to prevent Claude-as-harness from introducing bias toward or against any model under evaluation

### PII & Sensitive Data

- No personally identifiable information (PII) of any kind in any bundled dataset or asset
- No real institution names, employee names, account holders, or customer records in any file
- No sensitive financial identifiers — account numbers, routing numbers, card numbers — in any synthetic dataset

### External Services & Data Sharing

- No external services are permitted in V1 beyond what is required to run the skill locally
- Any new external service integration in future versions requires written PM approval before use
- No Banking Institution data — synthetic or otherwise — may be transmitted to any external service at any point in V1

### Escalation Rule

Any ambiguity about whether a dataset, file, or integration crosses a data or privacy boundary must be escalated to the PM before proceeding. When in doubt, do not include — escalate first.

---

## Out of Scope

---

### Functional Exclusions

The following features will NOT be built in V1:

- Real-time or streaming evaluation — the harness runs as a single synchronous skill invocation only
- User-level personalization or adaptive prompting — all models receive identical standardized prompts; no task-specific prompt engineering
- UI, dashboard, or visualization layer — output is a flat file scorecard and Markdown report only
- Human-in-the-loop review workflow — evaluation is fully automated within the skill
- Model fine-tuning, retraining, or prompt optimization as an output of evaluation
- External data ingestion — all datasets are bundled synthetic assets; no Kaggle pulls, no API data sources in V1
- Live code execution by the harness — all model-generated code is executed during dataset preparation, not at harness runtime
- Live invocation of testing or linting tools by the harness — pytest, tracemalloc, flake8, and sqlfluff are dataset preparation tools

### Technical Exclusions

The following architectures, tools, and patterns will NOT be adopted in V1:

- Web or API framework (FastAPI, Flask, or similar)
- Database of any kind — flat files only
- Docker, Kubernetes, or any containerization
- Cloud infrastructure (AWS, Azure, GCP) or managed cloud services
- Microservices or multi-tenant architecture
- GPU-dependent solutions
- API key management or credential handling
- Runtime code execution of model-generated output by the harness

### Explicitly Deferred to Post-V1


| Item                                                      | Status   |
| --------------------------------------------------------- | -------- |
| PostgreSQL as persistent document store                   | Deferred |
| API framework for external data pulls (e.g., Kaggle CSVs) | Deferred |
| API key management and credential handling rules          | Deferred |
| Maintainability rubric and scoring weights                | TBD      |
| Runtime variance window definition                        | TBD      |
| Scoring thresholds and pass/fail weights                  | TBD      |


> **Note on Scorecard Thresholds**: Scoring weights and acceptance thresholds are currently TBD and are deferred to post-V1. However, these thresholds must be formally agreed upon with the Banking Institution client before final delivery. This is not solely an internal team decision.

### Definition of Done (V1)

V1 is complete when all of the following are true:

- Zipped skill folder is complete, self-contained, and uploadable to Claude.ai
- README and quickstart guide are included in the deliverable
- Client invokes skill in Claude with `--contracted-only` and receives a complete comparative scorecard covering the 40 contracted tasks
- All evaluation logic is deterministic and script-enforced
- No manual steps are required beyond skill invocation
- Scorecard is reproducible across independent invocations with identical inputs
- `assets/task_bank.csv` and `assets/eval_results.csv` are bundled and validated against `references/file-schema.md`
- Full 200-task scorecard is producible without `--contracted-only` flag as the value-add deliverable

---

## Governance

---

### Roles & Ownership


| Role                 | Responsibility                                                                                                                                                                                                      |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **PM**               | Owns this Constitution; final decision-maker; tiebreaker on all disputes; approves all changes                                                                                                                      |
| **System Architect** | Skill Owner for: folder structure, `scripts/`, `assets/` (including `task_bank.csv`, `eval_results.csv`, and the per-author `results_*.csv` merge workflow), `requirements.txt`, file schema, technical architecture, pre-recorded data schema |
| **Prompt Engineer**  | Skill Owner for: `SKILL.md` instructions, prompt templates, LLM behavior rules, progressive disclosure structure, Critic persona templates                                                                          |
| **All Members**      | Responsible for flagging Constitution violations when observed                                                                                                                                                      |


### Change Process

This Constitution is the authoritative source of truth. No unilateral deviations are permitted under any circumstances, including urgent or time-sensitive situations. All proposed changes and observed violations follow this exact sequence:

1. Team member identifies a proposed change or Constitution violation
2. Proposer prepares a written rationale
3. Written rationale submitted to PM for review
4. PM approval obtained before any change is adopted
5. PR raised only after PM approval is confirmed
6. PR merged — Constitution updated and version number incremented

### Review Cadence

- Constitution reviewed weekly by all three team members
- Recurring patterns in Claude-as-harness behavior not addressed by current Constitution language must be raised at the next weekly review
- Recurring issues trigger `SKILL.md` updates and/or Constitution amendments — never one-off fixes

### Enforcement

- All specs, plans, scripts, prompt templates, and skill assets must comply with this Constitution at all times
- If a conflict arises between any deliverable and this Constitution, the Constitution wins
- The team must either update the Constitution via the approved change process OR adjust the deliverable to comply — no middle ground
- AI-generated suggestions — including from Claude-as-harness — that conflict with this Constitution are rejected by default

### Versioning

- Constitution version number is incremented with each approved amendment
- All prior versions are preserved in version control history
- Version, ratification date, and last amended date are maintained in the footer below

---

## Amendment Log

---

### Amendment A1 — April 2026

**Status**: ✅ Ratified by PM — 2026-04-09. Subsequently superseded in part by Amendment A3 (see below). All affected feature plans and spec updated accordingly.

**Changes introduced by Amendment A1**:

1. **Task count ceiling** — Raised from "20–40 analytics tasks" to 200 total (100 SQL + 100 Python). Client contract remains at 40 tasks (20 SQL + 20 Python). The contracted subset is identified by `contracted = true` in `task_bank.csv`. `--contracted-only` CLI flag produces the client deliverable. **Status: still in effect.** Affects: Principle 1, FR-001, Feature 1 Scale/Scope, Feature 3 Scale/Scope, Feature 5 Scale/Scope.
2. **Answer file architecture** — Per-task `answers.csv` pattern replaced by six consolidated files in `assets/answers/` (one per model per language, 100 rows each). **Status: SUPERSEDED by Amendment A3.** The six-file architecture has been consolidated further into a single unified `eval_results.csv` plus a three-file per-author authoring convention.
3. **Variant results file architecture** — Per-task `variant_results.csv` pattern replaced by three consolidated files in `assets/variant_results/` (one per Python model, up to 500 rows each). **Status: SUPERSEDED by Amendment A3.** Variant execution metrics are now fields in the unified `eval_results.csv`.
4. **Task bank index** — `assets/task_bank.csv` introduced as master index for all 200 tasks. All scripts must resolve file paths through this index — hardcoded paths are prohibited. `SKILL.md` references it by path only. **Status: still in effect, schema revised under A3.** Affects: Principle 3, Skill Folder Structure, Explicit Prohibitions, FR-018.
5. **`contracted` flag** — Boolean field added to `task_bank.csv`. **Status: still in effect, single source of truth.** `true` for SQL-001–SQL-020 and PY-001–PY-020. Affects: Pre-Recorded Evaluation Data Standards, FR-017, FR-018, SC-012, SC-013.
6. **`--contracted-only` CLI flag** — Added to `eval-task` and `scorecard` commands. **Status: still in effect.** Affects: FR-013, Feature 5 Technical Context and Project Structure.
7. **Scorecard ceilings** — Full ceiling raised from 600 to 3,000 scored comparisons (200 tasks × 3 models × 5 variants). Client contracted ceiling: 300 (40 tasks × 3 models × 5 variants). **Status: still in effect.** Affects: Feature 1, 3, 5 Scale/Scope sections.

**Rationale**: The scale increase to 200 tasks provides a statistically stronger evaluation evidence base at no additional architectural cost. The `contracted` flag and `--contracted-only` flag ensure the client deliverable remains exactly as contracted while the value-add build is additive and non-disruptive. No scoring logic, rubric, or evaluation integrity rules change under this amendment.

---

### Amendment A2 — April 2026

**Status**: ✅ Ratified by PM — 2026-04-13.

**Changes introduced by Amendment A2**:

1. **`generation_time_ms` removed from all schemas** — `generation_time_ms` is not captured in V1 and is removed from all pre-recorded data schemas and all `result.json` output artifacts. It must not appear in any harness script, fixture file, or scorecard output. Affects: Pre-Recorded Evaluation Data Standards, Feature 1 Project Structure, Feature 3 Project Structure, Feature 5 Unified JSON and Markdown Scorecard sections.

**Rationale**: Generation time requires calling the model API during dataset preparation with instrumentation that was not implemented in the initial dataset preparation workflow. Removing it simplifies the data collection phase with no impact on the core evaluation rubric — correctness, formatting, and runtime/memory performance remain fully captured.

---

### Amendment A3 — April 2026

**Status**: ✅ Ratified by PM — 2026-04-18.

**Changes introduced by Amendment A3**:

1. **Two-table answer architecture (supersedes A1 items 2 and 3)** — The six-file `assets/answers/` architecture and the three-file `assets/variant_results/` architecture introduced in A1 are both replaced by a **two-table design**:
   - `assets/task_bank.csv` — master index. 200 rows. One row per task. Schema: `task_id, contracted, category, prompt, model_a_filename, model_b_filename, model_c_filename`.
   - `assets/eval_results.csv` — unified pre-recorded metrics. Up to 3,000 rows (200 tasks × 3 models × 5 variants). Schema: `filename, dataset_variant, token_usage_input, token_usage_output, runtime_ms, peak_memory_bytes, formatting_violations, pytest_filename, pytest_pass, checksum, row_count, snapshot_pass`.

2. **Filename-based identity convention** — Model and language are encoded in the filename using the pattern `task{N}{model}.{ext}`. The filename letter (`a`/`b`/`c`) replaces the `model_token` column in pre-recorded data. `model_token` is still used in `outputs/` directory paths and downstream `result.json` artifacts — it is derived from the filename letter at load time. Real model names are mapped via `model_token_lookup.csv` held outside the zip.

3. **Per-author authoring convention** — Three team members generate the pre-recorded data independently on separate machines, each producing a per-author file (`results_a.csv`, `results_b.csv`, `results_c.csv`, 1,000 rows each). Before release, these are merged into `assets/eval_results.csv` by a merge script that validates header consistency, variant enum, primary key uniqueness, and row totals. Only the merged file is bundled in the zip — the per-author files are an authoring convention and must not appear in the release.

4. **Field renames and removals** — As a consequence of the consolidation, several field names are standardized across the whole project:
   - `flake8_violation_count` / `sqlfluff_violation_count` → `formatting_violations` (unified, applies to both languages)
   - `correctness_pass` (Python variant results) → `pytest_pass` (Python only, in `eval_results.csv`)
   - `correctness_detail` — removed. Per-test detail is not captured at the unified-results level; diagnostic artifacts remain under `assets/tasks/[task_id]/` if needed.
   - `variant_mismatch` — removed from pre-recorded data schema. Variant-mismatch detection at harness runtime remains a `schema_checker.py` responsibility and is surfaced in `result.json` only, not in `eval_results.csv`.
   - `row_counts` → `row_count` (SQL only, singular)
   - `snapshot_tests` → `snapshot_pass` (SQL only, boolean)

5. **Schema validation updated** — `schema_validator.py` validates `eval_results.csv` against the unified schema in `references/file-schema.md` before scoring begins. It cross-checks that every `task_id` derivable from a `filename` resolves to a row in `task_bank.csv`. The prior cross-check of the `contracted` field between answer files and `task_bank.csv` is obsolete (there is now a single source of truth in `task_bank.csv`), but the task-ID coverage check remains a FR-017 gate.

6. **Per-task asset layout revised** — `assets/tasks/[task_id]/` no longer contains a per-task `answers.csv` or `variant_results.csv`. It contains: the three models' code files (e.g., `task1a.py`, `task1b.py`, `task1c.py`), `reference_solution.{py|sql}`, reference result sets (SQL), and `test_solution.py` (Python, documentation artifact only). Prompts live inline in `task_bank.csv` — the per-task `prompt.md` file is also removed.

**Affects**: Skill Folder Structure, Pre-Recorded Evaluation Data Standards, Explicit Prohibitions (new rule on per-author files), FR-002, FR-004, FR-005, FR-006, FR-015, FR-017, FR-018, Feature 1 Project Structure and Structure Decision, Feature 2 per-task asset tree, Feature 3 Project Structure and Structure Decision, Feature 4 per-task asset tree, Feature 5 Summary and Data Context, all constitution-check alignment tables in feature plans.

**Rationale**: The six-file architecture introduced in A1 was intended to make pre-recorded data easier to validate and version-control relative to a per-task pattern. In practice, the three-person team authors the data independently on separate machines — one per model — making a per-author file layout the natural unit of work. The prior six-file split also required cross-file joins to reconstruct a full (task × model × variant) view, producing fragile validation logic. The two-table design preserves the strengths of the A1 consolidation (single schema per file, easy diffing, manageable file count) while matching the actual authoring workflow and producing a single unified file that every downstream consumer — `scorer.py`, `variant_scorer.py`, `collector.py` — can read with one pass. The filename-based identity convention removes a redundant `model_token` column and eliminates an entire class of possible consistency bugs between column values and directory names. No evaluation integrity rule, scoring rubric, or anonymization guarantee is weakened.

---

Version: 1.4 | Ratified: March 27, 2026 | Last Amended: April 18, 2026 (Amendment A3 — two-table unified architecture)
