# Feature Specification: SQL + Python AI Evaluation Framework

**Feature Branch**: `001-sql-python-ai-eval`
**Created**: 2026-03-19
**Updated**: 2026-04-24
**Status**: V1 Complete
**Version**: 1.0

> **Amendment A4 — April 2026 (ratified):** V1 scope revised to 60 tasks (30 SQL + 30 Python). No `--contracted-only` flag — all 60 tasks are the client deliverable. Model letters corrected: `a` = Claude Sonnet 4.5, `b` = ChatGPT 5.2 Codex (baseline), `c` = Gemini 2.5 Flash. Correctness gate revised to row count majority consensus (SQL) and `pytest_pass_pct = 100` (Python). Performance scoring revised to 10-band percentile. `formatting_pass_pct` replaces `formatting_violations`. `run_eval.py` is the sole entry point per skill. Raw Metrics section added to scorecard output.

> **Amendment A3 — April 2026 (ratified):** Two-table design adopted: `assets/task_bank.csv` + `assets/eval_results.csv`. Filename-based identity convention established. Per-author authoring convention (`results_table_a/b/c.csv`) merged by `merge_results.py`.

> **Amendment A2 — April 2026 (ratified):** `generation_time_ms` removed from all schemas.

> **Amendment A1 — April 2026 (ratified):** Task count and contracted scope rules introduced. Superseded in part by A4.

---

## Overview

The SQL + Python AI Evaluation Framework is a single zipped deliverable containing two Claude Agent Skills — one for SQL evaluation and one for Python evaluation — that assess AI-generated code across a task bank of 60 analytics engineering tasks (30 SQL + 30 Python). All 60 tasks constitute the client deliverable.

Each skill applies a four-dimension rubric: correctness (pre-recorded automated test results), formatting (pre-recorded style linting scores), performance (pre-recorded runtime, memory, and token metrics), and a language-specific AI Critic persona review (generated at harness runtime as bulleted qualitative comments). All dataset variants are bundled as synthetic flat files. Every model receives exactly one standardized prompt per task — no revisions. The deliverable produces a single unified machine-readable JSON and a human-readable markdown scorecard per run.

All model code generation, code execution, test execution, performance measurement, and formatting validation occur during a manual dataset preparation phase outside the harness. The harness reads, compares, and aggregates this pre-recorded data — it never generates, executes, or measures model code at runtime. The only content produced at harness runtime is the AI Critic persona reviews.

Pre-recorded evaluation data is organized as a two-table design: `assets/task_bank.csv` (master index, 60 rows) and `assets/eval_results.csv` (unified results, up to 900 rows — 60 tasks × 3 models × 5 variants). Model identity and language are encoded in code filenames using the pattern `task{N}{model}.{ext}` — e.g., `task1a.py` = task 1, Claude Sonnet 4.5 (letter `a`), Python.

The three models under evaluation are Claude Sonnet 4.5 (filename letter `a`, evaluated), ChatGPT 5.2 Codex (letter `b`, baseline), and Gemini 2.5 Flash (letter `c`, evaluated). All scoring and ranking logic is enforced by deterministic scripts — Claude's judgment is never the arbiter of evaluation results.

---

## User Scenarios & Testing

### User Story 1 — SQL Quantitative Evaluation (Priority: P1)

An Analytics Engineer describes a SQL analytics task in plain English. Claude matches the description against `assets/task_bank.csv`, resolves the task ID, and runs `sql-skill/scripts/run_eval.py --task-id [SQL-XXX]`. The harness reads pre-recorded metrics for all three models from `assets/eval_results.csv` and scores each model across correctness, formatting, performance, and reliability.

**Acceptance Scenarios:**

1. **Given** a natural language prompt matching a SQL task, **When** Claude resolves the task ID and runs the scoring script, **Then** a scorecard is produced covering all three models with correctness, formatting, performance, and reliability scores plus delta vs baseline.
2. **Given** a model passes correctness on the clean variant (row count matches majority consensus), **When** the harness reads the four non-clean variant rows, **Then** reliability ticks (✓/✗) are produced for null_heavy, duplicate_heavy, medium, and large variants.
3. **Given** a model fails correctness on the clean variant, **When** reliability is evaluated, **Then** reliability score is 0 and ticks show ✗ for all variants — correctness gate enforced.

---

### User Story 2 — SQL Qualitative Evaluation (Priority: P1)

An Analytics Engineer completes a SQL evaluation run and automatically receives a structured AI Critic review. The Critic reads the anonymized SQL code files and produces commentary across four sections — Strengths, Failures, Mitigation Strategies, Observations — with one bullet per model.

**Acceptance Scenarios:**

1. **Given** a completed SQL scorecard with `<!-- CRITIC:... -->` placeholders, **When** Claude reads the SQL Critic persona and the anonymized code files, **Then** every placeholder is filled with a 1–3 sentence bullet covering the relevant section.
2. **Given** the code files are identified by anonymized filename only (`task{N}{letter}.sql`), **When** the Critic produces its review, **Then** no real model name (Claude Sonnet 4.5, ChatGPT 5.2 Codex, Gemini 2.5 Flash) appears in the Critic's reasoning — only in the final formatted output using the `MODEL_NAMES` lookup.
3. **Given** the Critic review is complete, **Then** the scorecard contains all four sections for all three models with no numeric scores in the Critic output.

---

### User Story 3 — Python Quantitative Evaluation (Priority: P2)

A Data Engineer describes a Python analytics task in plain English. Claude matches the description against `assets/task_bank.csv`, resolves the task ID, and runs `python-skill/scripts/run_eval.py --task-id [PY-XXX]`. The harness reads pre-recorded metrics for all three models and scores correctness (`pytest_pass_pct = 100` on clean), formatting (flake8), performance (runtime, memory, tokens), and reliability across four stress variants.

**Acceptance Scenarios:**

1. **Given** a natural language prompt matching a Python task, **When** Claude resolves the task ID and runs the scoring script, **Then** a scorecard is produced with correctness (pytest), formatting (flake8), performance (runtime + memory + tokens), and reliability scores for all three models.
2. **Given** a model passes correctness on the clean variant (`pytest_pass_pct = 100`), **When** the four non-clean variants are evaluated, **Then** reliability ticks are produced per variant.
3. **Given** a model fails correctness on the clean variant, **Then** reliability score is 0 — correctness gate enforced.

---

### User Story 4 — Python Qualitative Evaluation (Priority: P2)

A Data Engineer completes a Python evaluation run and automatically receives a structured AI Critic review using the Python Critic persona. Commentary covers code quality, null handling, pandas idioms, test coverage, and maintainability across four sections.

**Acceptance Scenarios:**

1. **Given** a completed Python scorecard with `<!-- CRITIC:... -->` placeholders, **When** Claude reads the Python Critic persona and the anonymized `.py` code files, **Then** every placeholder is filled with a concise bullet per model per section.
2. **Given** the code files are identified by anonymized filename only, **When** the Critic produces its review, **Then** no real model name appears in the Critic's code analysis — only in the final formatted output.
3. **Given** the Critic review is complete, **Then** all four sections are populated for all three models with no numeric scores.

---

### User Story 5 — Comparative Scorecard (Priority: P3)

An Evaluation Lead runs the full evaluation across all 30 SQL or all 30 Python tasks and generates a comparative scorecard with summary tables, delta analysis, per-task breakdown, Critic review, and raw quantitative metrics.

**Acceptance Scenarios:**

1. **Given** a full evaluation run across all tasks, **When** scores are aggregated, **Then** the scorecard includes: mean scores per model, delta table vs ChatGPT baseline, per-task Quantitative Assessment with reliability ticks, full Critic Review, Metric Key, and Raw Metrics table.
2. **Given** the same inputs are provided across independent runs, **Then** all numeric scores are identical — fully deterministic.
3. **Given** a single-task run, **Then** the scorecard covers that task only and is saved to a new timestamped folder without overwriting any prior run.

---

## Edge Cases

- **Correctness gate**: SQL reliability is only scored if the model's row count matches majority consensus on the clean variant. Python reliability is only scored if `pytest_pass_pct = 100` on the clean variant.
- **SQL majority consensus**: If all three models return different row counts on the clean variant, no model passes correctness — all score 0 for correctness and reliability.
- **Missing pre-recorded data**: If `eval_results.csv` is missing rows for a `(filename, dataset_variant)` pair, the affected model scores 0 for the dimensions dependent on that variant.
- **Gemini Python correctness**: Gemini 2.5 Flash scores 0 on most Python correctness tasks — genuine model finding, not a framework bug. Reliability is scored 0 as a consequence of the correctness gate.
- **ChatGPT null-heavy reliability**: ChatGPT 5.2 Codex returns more rows than consensus on the null_heavy variant for 18/30 SQL tasks — genuine finding, documented in DEBT.md.
- **Critic non-determinism**: Numeric scores are fully deterministic. Critic Review text may vary slightly between runs due to LLM non-determinism — this is expected and documented.
- **Per-author merge failure**: If `results_table_a/b/c.csv` fail the merge validation in `merge_results.py`, the release halts. `eval_results.csv` must not be produced from a failed merge.

---

## Requirements

### Functional Requirements

| FR | Description | Owner |
|:---|:------------|:------|
| **FR-001** | System MUST maintain a task bank of 60 analytics tasks (30 SQL + 30 Python) indexed in `assets/task_bank.csv`. All 60 tasks are the client deliverable — no contracted subset flag in V1. | Script |
| **FR-002** | System MUST read pre-recorded model metrics for Claude Sonnet 4.5 (`a`), ChatGPT 5.2 Codex (`b`, baseline), and Gemini 2.5 Flash (`c`) from `assets/eval_results.csv`. Model identity is encoded in the `filename` field using the pattern `task{N}{model}.{ext}`. | Script |
| **FR-003** | System MUST enforce a one-shot evaluation policy — each model has exactly one pre-recorded code file per task; no revisions permitted. | Script |
| **FR-004** | System MUST score SQL correctness by row count majority consensus across all 3 models on the clean variant. Python correctness by `pytest_pass_pct = 100` on clean variant. Both gates must pass before reliability is scored. | Script |
| **FR-005** | System MUST report formatting scores derived from `formatting_pass_pct` in `eval_results.csv` — mean across all 5 variants, scaled 0–25. Pre-recorded via sqlfluff (SQL) or flake8 (Python). | Script |
| **FR-006** | System MUST report performance scores using 10-band percentile scoring against fixed thresholds. SQL: 2 sub-scores averaged (runtime, tokens). Python: 3 sub-scores averaged (runtime, memory, tokens). No baseline dependency. | Script |
| **FR-007** | System MUST score reliability across 4 non-clean variants (null_heavy, duplicate_heavy, medium, large) only for models that pass the clean correctness gate. Reliability ticks (✓/✗) reported per variant. | Script |
| **FR-008** | System MUST invoke the SQL Critic persona automatically after every SQL eval run. Critic MUST return structured commentary with 4 sections (Strengths, Failures, Mitigation Strategies, Observations), one bullet per model, no numeric scores. | LLM |
| **FR-009** | System MUST invoke the Python Critic persona automatically after every Python eval run. Same 4-section format as FR-008. | LLM |
| **FR-010** | System MUST write scorecard output to a new timestamped folder under `outputs/[YYYY-MM-DD_HH-MM]/`. No overwriting of prior runs. Both `.md` and `.json` produced per run. | Script |
| **FR-011** | Scorecard MUST contain 6 sections in order: Summary Table, Delta Table, Quantitative Assessment, Critic Review, Metric Key, Raw Metrics. | Script |
| **FR-012** | System MUST resolve all task-to-file path mappings via `assets/task_bank.csv`. Scripts MUST NOT hardcode file paths. | Script |
| **FR-013** | System MUST provide `run_eval.py` in each skill's `scripts/` folder, supporting `--task-id` for single-task runs and no flag for all-task runs. | Script |
| **FR-014** | System MUST provide `merge_results.py` at repo root to merge `results_table_a/b/c.csv` into `assets/eval_results.csv`. Merge MUST validate header consistency, variant enum, primary key uniqueness, and row counts. | Script |
| **FR-015** | All bundled datasets MUST be synthetic only — labeled as synthetic in filename and file header. No real account numbers, routing numbers, or customer identifiers. | Script |
| **FR-016** | Per-author `results_table_*.csv` files MUST NOT appear in the release zip. Only the merged `eval_results.csv` is shipped. | Script |

---

### Key Entities

- **Task** — A single analytics engineering problem with a unique ID (SQL-001–SQL-030, PY-001–PY-030), standardized prompt (stored inline in `task_bank.csv`), category (easy/medium/hard), and three model code files. Indexed in `assets/task_bank.csv`.
- **Model** — One of three AI coding assistants: Claude Sonnet 4.5 (`a`), ChatGPT 5.2 Codex (`b`, baseline), Gemini 2.5 Flash (`c`). Model identity encoded in code filename letter.
- **Task Bank Index** — `assets/task_bank.csv`. Master index of all 60 tasks. Scripts resolve all file paths through this index.
- **Unified Evaluation Results** — `assets/eval_results.csv`. Single source of truth for all pre-recorded numeric metrics. Up to 900 rows. Primary key: `(filename, dataset_variant)`.
- **Per-Author Results File** — `results_table_a/b/c.csv`. Authoring convention only — one file per team member per model. Merged before release, not bundled in zip.
- **Dataset Variant** — One of five fixed input configurations: `clean`, `null_heavy`, `duplicate_heavy`, `medium`, `large`.
- **Scorecard** — Aggregated output per run. Single-task or all-tasks mode. Saved as `.md` and `.json` in a timestamped `outputs/` subfolder.
- **Critic Persona** — Language-specific AI reviewer (SQL or Python). Invoked at harness runtime. Produces 4-section structured commentary on anonymized code. Only LLM-generated content in the harness.
- **Raw Metrics** — Actual runtime (ms), token usage (input + output), and peak memory (bytes, Python only) per model per task. Displayed in the final scorecard section sourced from `eval_results.csv`.

---

## Success Criteria

| SC | Outcome | Theme |
|:---|:--------|:------|
| **SC-001** | Single-task SQL prompt returns a complete scorecard for all 3 models within one Claude session | User Experience |
| **SC-002** | Single-task Python prompt returns a complete scorecard for all 3 models within one Claude session | User Experience |
| **SC-003** | All-tasks SQL run produces a scorecard covering all 30 SQL tasks | Coverage |
| **SC-004** | All-tasks Python run produces a scorecard covering all 30 Python tasks | Coverage |
| **SC-005** | Same prompt produces identical numeric scores across independent runs | Determinism |
| **SC-006** | SQL correctness correctly applies row count majority consensus on clean variant | Scoring Integrity |
| **SC-007** | Python correctness correctly applies `pytest_pass_pct = 100` gate on clean variant | Scoring Integrity |
| **SC-008** | Reliability scores 0 for any model that fails the clean correctness gate | Scoring Integrity |
| **SC-009** | Performance scores use 10-band percentile bands with no baseline dependency | Scoring Integrity |
| **SC-010** | Every scorecard run automatically produces Critic Review with all 4 sections populated for all 3 models | Output Quality |
| **SC-011** | No real model name appears in code filenames, `eval_results.csv`, or Critic review analysis | Anonymization |
| **SC-012** | Each run creates a new timestamped `outputs/` folder — no prior run is overwritten | Output Integrity |
| **SC-013** | Raw Metrics table in every scorecard shows actual runtime, tokens, and memory sourced from `eval_results.csv` | Output Quality |
| **SC-014** | `merge_results.py` produces a valid `eval_results.csv` or halts with a clear error — never produces a partial merge | Data Integrity |
| **SC-015** | A Banking Institution team member with no prior training can upload the zip, run the SQL-019 prompt, and receive a complete scorecard | Deliverability |

---

*End of spec.md*

**Document History:**

| Version | Date | Author | Changes |
|:--------|:-----|:-------|:--------|
| 0.1–0.5 | March–April 2026 | Team JAS | Initial drafts through Amendment A3 |
| 1.0 | April 2026 | Team JAS | V1 delivery scope — Amendment A4 applied |
