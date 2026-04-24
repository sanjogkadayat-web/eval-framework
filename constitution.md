# AI Powered SQL & Python Evaluation Framework Constitution

===========================

## Core Principles

---

### Principle 1 — Purpose & Scope

This project delivers a reproducible, client-operable Claude Agent Skill that evaluates AI-generated SQL and Python code across a fixed task bank, producing a comparative scorecard for three AI models. It serves Analytics Engineers, Data Engineers, and Evaluation Leads at a Banking Institution who need an objective, evidence-based basis for AI model selection in analytics engineering workflows.

The outcome that matters most is a self-contained zipped skill folder that the client can upload to Claude via Settings > Customize > Skills and immediately receive a complete, reproducible scorecard — accompanied by a README requiring no prior training to use.

The task bank contains 60 tasks (30 SQL + 30 Python). All 60 tasks are delivered as the full client deliverable. There is no contracted subset flag in V1.

### Principle 2 — AI as Dual-Role Actor

This project occupies a unique position: Claude simultaneously acts as the evaluation harness and is one of the models under evaluation. This dual role is managed through three non-negotiable rules. First, all scoring and ranking logic is enforced by deterministic scripts — Claude's own judgment is never the arbiter of evaluation results. Second, all model-generated code is anonymized before it enters the scoring pipeline, ensuring Claude-as-harness cannot favor or disadvantage any model. Third, the harness never executes model-generated code at runtime — it operates exclusively as a comparison and aggregation engine over pre-recorded evaluation data. Humans remain responsible for interpreting and acting on all scorecard outputs.

### Principle 3 — Machine-Readable Skill, Plain-Language Deliverables

`SKILL.md` must follow structured, machine-readable markdown per the Claude Agent Skills standard: YAML frontmatter with `name` and `description` fields, concise instructions, and progressive disclosure to sub-files. `SKILL.md` references `assets/task_bank.csv` by path in one line — it must not embed the task list inline. All client-facing deliverables — the scorecard report and README — must be written in plain language readable by non-developer stakeholders at the Banking Institution.

### Principle 4 — Guardrails Over Features

Evaluation integrity rules — model anonymization, deterministic scoring, synthetic-only data, flat-file-only storage, and pre-recorded evaluation data — are non-negotiable constraints, not implementation preferences. If a proposed feature or shortcut conflicts with any guardrail, the guardrail wins.

### Principle 5 — Iterative Refinement via Observed Behavior

This Constitution is a living, versioned document. It is updated through the PM approval process. Recurring gaps in Claude-as-harness behavior — unexpected evaluation paths, missed scoring rules, inconsistent output formats — must trigger `SKILL.md` updates and, where applicable, Constitution amendments. They are never addressed through one-off prompt adjustments.

### Principle 6 — Pre-Recorded Evaluation Data

All model-generated code, execution results, performance metrics, and formatting scores are captured outside the harness — during a manual dataset preparation phase — and bundled as pre-recorded flat-file assets in the skill folder. The harness reads, compares, and aggregates this pre-recorded data; it does not generate, execute, or measure it. This separation exists because: (a) executing untrusted model-generated code inside the harness would introduce safety and environment variability risks; (b) pre-recording all deterministic inputs guarantees fully reproducible scoring across independent invocations. The only content generated at harness runtime is the AI Critic persona reviews, which are qualitative and carry no numeric weight.

---

## Tech Stack & Platform Rules

---

### Approved Languages & Frameworks

**Primary Language**: Python 3.10+
**Evaluated Languages**: SQL and Python — the subjects of evaluation tasks, not runtime languages executed by the harness
**Test Framework**: pytest — used during dataset preparation to validate model-generated Python code; not invoked by the harness at runtime
**Performance Measurement**: tracemalloc (Python peak memory) and `time` (wall-clock runtime) — used during dataset preparation; not invoked by the harness at runtime
**Formatting Validation**: flake8 (Python PEP8 violations) and sqlfluff (SQL style violations) — used during dataset preparation; not invoked by the harness at runtime
**Web/API Framework**: None — explicitly prohibited in V1

### Models Under Evaluation (V1)

| Letter | Model | Role |
|--------|-------|------|
| `a` | Claude Sonnet 4.5 | Evaluated |
| `b` | ChatGPT 5.2 Codex | Baseline |
| `c` | Gemini 2.5 Flash | Evaluated |

All deltas are computed vs model `b` (ChatGPT 5.2 Codex). Positive delta = better than baseline. Negative delta = worse.

### Skill Folder Structure (V1 Release)

```
eval_framework/
├── README.md
├── HANDOFF.md
├── DEBT.md
├── requirements.txt
├── merge_results.py
├── assets/
│   ├── task_bank.csv
│   ├── eval_results.csv
│   ├── tasks/[task_id]/
│   └── datasets/
├── sql-skill/
│   ├── SKILL.md
│   ├── scripts/run_eval.py
│   └── assets/personas/sql_critic_persona.md
├── python-skill/
│   ├── SKILL.md
│   ├── scripts/run_eval.py
│   └── assets/personas/python_critic_persona.md
└── outputs/   ← empty, populated at runtime
```

**Excluded from release zip**: `authoring_only/`, `results_table_a/b/c.csv`, `specs/`, `constitution.md`, `references/`, `spec.md`

### Canonical File Format Standards

| Content Type | Format | Extension |
|:-------------|:-------|:----------|
| Machine-readable scorecard data | JSON | `.json` |
| Datasets, task bank, evaluation results | CSV | `.csv` |
| Human-readable reports, scorecards, README | Markdown | `.md` |

### Pre-Recorded Evaluation Data Standards

All evaluation data is captured during the dataset preparation phase and bundled as flat files. The architecture is a **two-table design**.

**Task Bank Index** — `assets/task_bank.csv`

- 60 rows. One row per task.
- Schema: `task_id, prompt, model_a_file_name, model_b_file_name, model_c_file_name, category`
- `task_id`: Primary key. `SQL-001` through `SQL-030`, `PY-001` through `PY-030`.
- `category`: Difficulty — `easy`, `medium`, `hard`.
- `prompt`: Full standardized prompt text stored inline.
- `model_a_file_name`, `model_b_file_name`, `model_c_file_name`: Filenames of each model's code file under `assets/tasks/[task_id]/`.

**Unified Evaluation Results** — `assets/eval_results.csv`

- Up to 900 rows (60 tasks × 3 models × 5 variants). One row per filename × dataset variant.
- Schema: `filename, dataset_variant, token_usage_input, token_usage_output, runtime_ms, peak_memory_bytes, formatting_pass_pct, pytest_filename, pytest_pass_pct, checksum, row_count, snapshot_pass`
- `filename`: Primary key component. E.g., `task1a.sql`, `task1a.py`.
- `dataset_variant`: Primary key component. Enum — `clean`, `null_heavy`, `duplicate_heavy`, `medium`, `large`.
- `peak_memory_bytes`: Python files only — null for `.sql` filenames.
- `pytest_filename`, `pytest_pass_pct`: Python files only — null for `.sql` filenames.
- `checksum`, `row_count`, `snapshot_pass`: SQL files only — null for `.py` filenames.
- `formatting_pass_pct`: Percentage of formatting checks passed. Pre-recorded via flake8 (Python) or sqlfluff (SQL).

**Authoring Workflow**

Three team members generate the pre-recorded data independently — one per model. Each produces a per-author file:
- `results_table_a.csv` — rows for model `a` (Claude Sonnet 4.5)
- `results_table_b.csv` — rows for model `b` (ChatGPT 5.2 Codex)
- `results_table_c.csv` — rows for model `c` (Gemini 2.5 Flash)

These are merged into `assets/eval_results.csv` by `merge_results.py` before release. Per-author files are an authoring convention only — not bundled in the release zip.

---

## Scoring System (V1)

Four dimensions, 25 points each. Maximum score: 100.

### Correctness (25 pts)

- **SQL**: Row count majority consensus across all 3 models on the clean variant. Pass = 25, Fail = 0.
- **Python**: `pytest_pass_pct = 100` on clean variant. Pass = 25, Fail = 0.
- Clean gate must pass before reliability is scored.

### Formatting (25 pts)

Mean `formatting_pass_pct` across all 5 variants / 100 × 25. Pre-recorded via sqlfluff (SQL) or flake8 (Python).

### Performance (25 pts — higher is better)

10-band percentile scoring. No baseline dependency. Top 10% = 25 pts, each decile drops 2.5 pts, bottom 10% = 2.5 pts.

- **SQL**: 2 sub-scores averaged — `runtime_ms` + tokens
- **Python**: 3 sub-scores averaged — `runtime_ms` + `peak_memory_bytes` + tokens

**Fixed thresholds (derived from dataset distribution):**

| Metric | Thresholds |
|:-------|:-----------|
| SQL runtime (ms) | 1, 2, 2, 3, 4, 5, 7, 12, 26 |
| SQL tokens | 102, 118, 136, 151, 167, 184, 209, 271, 355 |
| Python runtime (ms) | 3, 4, 6, 7, 9, 11, 24, 44, 186 |
| Python memory (bytes) | 5871, 6097, 6830, 330108, 351566, 454303, 490933, 1456692, 12611584 |
| Python tokens | 164, 192, 210, 230, 248, 278, 327, 363, 431 |

### Reliability (25 pts)

Pass rate across 4 non-clean variants (null_heavy, duplicate_heavy, medium, large) × 25. Only scored if clean correctness passes.

- **SQL**: Row count matches consensus per variant.
- **Python**: `pytest_pass_pct = 100` per variant.

### Delta (Δ)

All deltas vs model `b` (ChatGPT 5.2 Codex). Positive = better than baseline. Negative = worse.

---

## Scorecard Output (V1)

Every run creates a new timestamped folder. No overwriting.

```
outputs/[YYYY-MM-DD_HH-MM]/
├── sql_scorecard_all.md
├── sql_scorecard_all.json
├── sql_scorecard_[task_id].md      ← single task run
├── sql_scorecard_[task_id].json
├── python_scorecard_all.md
├── python_scorecard_all.json
├── python_scorecard_[task_id].md
└── python_scorecard_[task_id].json
```

### Scorecard Sections (in order)

1. **Summary Table** — mean scores across all tasks per model
2. **Delta Table** — model `a` and model `c` vs baseline
3. **Quantitative Assessment** — per-task score tables with reliability ticks ✓/✗
4. **Critic Review** — grouped by section (Strengths / Failures / Mitigation Strategies / Observations), one bullet per model
5. **Metric Key** — scoring formula reference
6. **Raw Metrics** — actual runtime (ms), token usage, and peak memory (bytes) per model per task

---

## Critic Review (V1)

- Placeholders written by `run_eval.py`: `<!-- CRITIC:[task_id]:[letter]:[Section] -->`
- AI fills them in at runtime using the appropriate persona file
- Format: 4 sections, 3 bullets each (one per model), real model names used
- No numeric scores in Critic output
- No model identifier leakage in the code files passed to the Critic
- Works with any AI platform (Claude, Cursor, GitHub Copilot)

**Persona files:**
- `sql-skill/assets/personas/sql_critic_persona.md`
- `python-skill/assets/personas/python_critic_persona.md`

---

## Security, Privacy & Data Boundaries

### Client Identity

The client is referred to exclusively as "Banking Institution" in all internal project documents, including this Constitution, all specs, and all skill assets. The client's actual name must not appear anywhere in the skill folder or any internal artifact.

### Synthetic Data Rules

- All datasets bundled in the skill folder are synthetic only — no real financial data is permitted at any stage
- Every synthetic dataset must be explicitly labeled as synthetic in both its filename and its file header
- No real account numbers, routing numbers, transaction IDs, or customer identifiers

### Model Anonymization

- All model-generated code is anonymized before it enters the scoring pipeline
- Code filenames use the filename-letter convention (`a`/`b`/`c`) only — never real model names
- Real model names are used in scorecard output only — never in `eval_results.csv` or code file paths

### PII & Sensitive Data

- No personally identifiable information of any kind in any bundled dataset or asset
- No real institution names, employee names, or customer records in any file

---

## Out of Scope (V1)

### Functional Exclusions

- Real-time or streaming evaluation
- Live dataset evaluation — all metrics are pre-recorded; live execution is a V2 feature
- UI, dashboard, or visualization layer
- Human-in-the-loop review workflow
- Model fine-tuning or prompt optimization as an output of evaluation
- `--contracted-only` CLI flag — no contracted subset in V1; all 60 tasks are the deliverable
- 200-task scale — V1 delivers 60 tasks (30 SQL + 30 Python)

### Technical Exclusions

- Web or API framework (FastAPI, Flask, or similar)
- Database of any kind — flat files only
- Docker, Kubernetes, or any containerization
- Cloud infrastructure (AWS, Azure, GCP)
- GPU-dependent solutions
- API key management or credential handling
- Runtime code execution of model-generated output by the harness
- Live invocation of pytest, tracemalloc, flake8, or sqlfluff by the harness

### Explicitly Deferred to Post-V1

| Item | Target |
|:-----|:-------|
| Live dataset execution pipeline | Phase 2 |
| Expand to 200 tasks | Phase 2 |
| Scoring threshold agreement with Banking Institution | Phase 2 |
| Additional model support | Phase 3 |
| Custom task authoring interface | Phase 3 |
| Automated dataset refresh | Phase 3 |

---

## Definition of Done (V1)

V1 is complete when all of the following are true:

- Zipped skill folder is complete, self-contained, and uploadable to Claude.ai via Settings > Customize > Skills
- README, HANDOFF.md, and DEBT.md are included in the repo
- Both `run_eval.py` scripts produce correct scorecards for single-task and all-task runs
- All scoring is deterministic — same prompt always produces same numeric scores
- Happy Path verified: SQL-019 prompt returns a correct scorecard in Claude
- Critic Review placeholders are present in scorecard output and fillable by Claude
- `assets/task_bank.csv` and `assets/eval_results.csv` are validated and bundled
- No per-author `results_table_*.csv` files in the release zip
- `outputs/` folder is empty in the release zip — populated at runtime only

---

## Governance

### Roles & Ownership

| Role | Responsibility |
|:-----|:---------------|
| **PM** | Owns this Constitution; final decision-maker; approves all changes |
| **System Architect** | Owns folder structure, `scripts/`, `assets/`, `requirements.txt`, file schema, pre-recorded data |
| **Prompt Engineer** | Owns `SKILL.md` instructions, Critic persona templates, LLM behavior rules |
| **All Members** | Responsible for flagging Constitution violations when observed |

### Change Process

1. Team member identifies a proposed change or violation
2. Proposer prepares a written rationale
3. Written rationale submitted to PM for review
4. PM approval obtained before any change is adopted
5. Constitution updated and version number incremented

### Enforcement

- All specs, plans, scripts, and skill assets must comply with this Constitution at all times
- If a conflict arises between any deliverable and this Constitution, the Constitution wins
- AI-generated suggestions that conflict with this Constitution are rejected by default

---

## Amendment Log

### Amendment A1 — April 2026

**Status**: ✅ Ratified

Task count raised from 20–40 to 200 total. Client contract scoped at 40 tasks with `--contracted-only` flag. `assets/task_bank.csv` introduced as master index. **Superseded in part by A4.**

### Amendment A2 — April 2026

**Status**: ✅ Ratified

`generation_time_ms` removed from all schemas and output artifacts.

### Amendment A3 — April 2026

**Status**: ✅ Ratified

Two-table design adopted: `assets/task_bank.csv` + `assets/eval_results.csv`. Filename-based identity convention (`task{N}{model}.{ext}`) introduced. Per-author authoring convention (`results_a.csv`, `results_b.csv`, `results_c.csv`) established. Six-file architecture from A1 superseded.

### Amendment A4 — April 2026 (V1 Delivery Scope)

**Status**: ✅ Ratified

**Changes:**

1. **Task count revised to 60** — V1 delivers 30 SQL + 30 Python tasks. The 200-task ceiling from A1 is deferred to Phase 2. No `--contracted-only` flag — all 60 tasks are the client deliverable.

2. **Model letter assignment corrected** — `a` = Claude Sonnet 4.5 (evaluated), `b` = ChatGPT 5.2 Codex (baseline), `c` = Gemini 2.5 Flash (evaluated). All deltas are vs `b`.

3. **Correctness gate revised** — SQL correctness determined by row count majority consensus across all 3 models on clean variant. `snapshot_pass` field was unreliable (compared against model `c` only) and is not used as the correctness gate.

4. **Performance scoring revised** — Baseline-relative performance scoring replaced with 10-band percentile scoring fixed to dataset distribution. No baseline dependency. Thresholds hardcoded from current 60-task dataset distribution.

5. **`formatting_pass_pct` replaces `formatting_violations`** — Percentage-based formatting metric used instead of raw violation count. Enables consistent 0–25 scaling across both languages.

6. **`run_eval.py` as sole entry point** — No `run_scorecard.py`, no `eval-task` CLI, no `schema_validator.py`, no `references/` folder in V1. Each skill has one `run_eval.py` script invoked directly.

7. **Raw Metrics section added to scorecard** — Scorecard now contains 6 sections: Summary, Delta, Quantitative Assessment, Critic Review, Metric Key, Raw Metrics.

8. **Skill upload via Settings > Customize > Skills** — Delivery method is zip upload to Claude.ai skill settings, not project file upload.

9. **Per-author files renamed** — `results_a.csv` → `results_table_a.csv`, `results_b.csv` → `results_table_b.csv`, `results_c.csv` → `results_table_c.csv`. Merged by `merge_results.py` at zip root.

**Rationale**: V1 scope was refined during Weeks 5–7 based on actual build feasibility, dataset availability, and scoring system validation. The 60-task scope produces a statistically credible benchmark while remaining fully deliverable within the project timeline. The correctness and performance scoring revisions were made to fix genuine bugs discovered during dataset validation.

---

Version: 2.0 | Ratified: April 2026 | Last Amended: April 2026 (Amendment A4 — V1 delivery scope)
