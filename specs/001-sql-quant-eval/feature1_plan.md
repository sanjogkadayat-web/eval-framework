# Implementation Plan: Feature 1 — SQL Quantitative Evaluation

**Branch**: `001-sql-quant-eval` | **Date**: 2026-04-08 | **Last Updated**: 2026-04-18 | **Spec**: `specs/001-sql-quant-eval/spec.md`
**Input**: Feature specification from `/specs/001-sql-quant-eval/spec.md`

> **Amendment A3 — April 2026 (ratified 2026-04-18):** The three-file `assets/answers/` architecture for SQL and the per-task `answer_results/` folders are replaced by a two-table design: `assets/task_bank.csv` (master index, 200 rows with prompts inline and per-model filename references) and `assets/eval_results.csv` (unified metrics, up to 3,000 rows total). Model identity and language are encoded in code filenames (`task1a.sql`, `task1b.sql`, …). SQL-only metric fields in `eval_results.csv` are `checksum`, `row_count`, `snapshot_pass` (all null for Python rows); SQL-only fixtures under `assets/tasks/[task_id]/reference_results/` remain unchanged as the reference side of the comparison. A new merge step (FR-019) concatenates per-author files `results_a.csv`, `results_b.csv`, `results_c.csv` into `eval_results.csv` before release. See Constitution Amendment A3 for full rationale.

> **Amendment A1 — April 2026 (ratified 2026-04-09):** Task count raised from 20–40 to 100 SQL tasks. Client contract unchanged at 20 SQL tasks. `--contracted-only` CLI flag added. A1's consolidated answer-file architecture has been superseded by A3's unified `eval_results.csv`; task-count and contracted-flag aspects of A1 remain in effect.

---

## Summary

Feature 1 implements the SQL quantitative evaluation pipeline within the `sql-skill/` Agent Skill. It gives Analytics Engineers and Evaluation Leads at the Banking Institution an objective, numeric basis for comparing AI model performance on SQL analytics tasks.

Model SQL code files are stored under `assets/tasks/[task_id]/` — three per task, one per model (`task{N}a.sql`, `task{N}b.sql`, `task{N}c.sql`). All tasks are resolved through the master index at `assets/task_bank.csv`, which also stores the standardized prompt text inline. Pre-recorded numeric metrics for every model × task × variant are stored as rows in the unified `assets/eval_results.csv` table — SQL rows populate the `checksum`, `row_count`, `snapshot_pass` correctness fields and the `runtime_ms`, `formatting_violations`, `token_usage_input`, and `token_usage_output` performance/formatting fields; the Python-only fields (`peak_memory_bytes`, `pytest_filename`, `pytest_pass`) are null for SQL rows.

**No code is executed at runtime** — all deterministic outputs are populated during the dataset preparation phase before the harness runs. The harness reads each model's metric rows for a given Task ID — five rows per filename across the five variants — and evaluates across two numeric dimensions:

- **Correctness** — the SQL row for each (filename, variant) combination holds a `checksum` (SHA-256 of the result set), a `row_count`, and a `snapshot_pass` boolean. Correctness scoring interprets these against reference values stored at `assets/tasks/[task_id]/reference_results/[variant].csv`. Deterministic `ORDER BY` on stable keys or set-based equivalence with numeric epsilon for float comparisons is enforced per `references/deterministic-rules.md`. A 100% correctness pass on the clean variant is the gate condition for including the remaining four variant rows in the scorecard.
- **Performance** — `runtime_ms`, `token_usage_input`, and `token_usage_output` are read directly from `eval_results.csv`. No live measurement occurs during harness execution.

Every model answer that achieves 100% correctness on the clean dataset has its remaining four variant rows surfaced in the scorecard. If a variant's column names, data types, or structure differ from the clean baseline, `schema_checker.py` at harness runtime records `variant_mismatch = true` in `result.json` and excludes that variant from correctness scoring — it is not counted as a code failure. All artifacts (code files, scored output, per-dimension metrics) are persisted as flat files keyed by `task_id/model/category`. Model identifiers are never exposed to scoring logic — they are encoded as filename letters (`a`/`b`/`c`) and re-associated only after all numeric scores are recorded.

The sqlfluff violation count is pre-recorded in `eval_results.csv` as `formatting_violations` and written to `result.json` as part of the quantitative pipeline. The SQL Critic persona review is handled separately in Feature 2.

The `--contracted-only` flag limits evaluation to the 20 contracted SQL tasks (SQL-001–SQL-020, identified by `contracted = true` in `task_bank.csv`). When omitted, all 100 SQL tasks are evaluated. The client-facing scorecard is always run with `--contracted-only`. The full 100-task scorecard is delivered as a value-add beyond the contract.

---

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: `hashlib` (stdlib — SHA-256 checksum of serialized result set rows for aggregate parity validation); `csv` / `json` (flat-file I/O — stdlib)
**Storage**: Flat files only — `.json` for metrics and artifacts, `.csv` for `task_bank.csv`, `eval_results.csv`, reference result sets, and datasets, `.md` for human-readable output. No database.
**Testing**: pytest — harness self-tests only. No task-level pytest files for SQL: correctness is determined by interpreting pre-recorded `checksum` / `row_count` / `snapshot_pass` fields against reference result sets. Harness self-tests cover the scorer, anonymizer, schema checker, schema validator, merge script, and artifact store.
**Target Platform**: Local development, Linux/macOS — no cloud, no Docker, no containerization
**Project Type**: CLI skill — invoked via `eval-task --engine sql [--task-id SQL-001] [--contracted-only]` within the `sql-skill/` Agent Skill
**Performance Goals**: Query runtime, token usage, and formatting violations are pre-stored in `eval_results.csv` and surfaced as-is for cross-model comparison against the ChatGPT 5.2 Codex baseline (filename letter `c`). No live measurement occurs during harness execution.
**Constraints**:

- No code execution at runtime — harness is a comparison and aggregation engine only (Principle 6)
- No database of any kind
- Model anonymization enforced at the asset layer via filename letter convention (`a`/`b`/`c`); no real model names appear anywhere in the pre-recorded data
- Flat-file storage only
- No GPU dependencies
- SQL Critic persona review is out of scope for this feature — handled in Feature 2

**Scale/Scope**:

- Full build ceiling: 100 SQL tasks × 3 models × 5 variants = **1,500 SQL rows in `eval_results.csv`**
- Client-contracted ceiling (`--contracted-only`): 20 SQL tasks × 3 models × 5 variants = **300 SQL rows**
- Realistic scored counts are lower in both cases: the four non-clean variant rows are only surfaced in the scorecard for model answers that achieve 100% correctness on the clean dataset.

---

## Constitution Check

*GATE: All items must pass (or have an approved amendment in progress) before implementation begins. Re-check after technical design is finalized.*


| #   | Rule                                                                   | Source                              | Status                    | Notes                                                                                                                                                                                                                                                                            |
| --- | ---------------------------------------------------------------------- | ----------------------------------- | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Python 3.11+ only                                                      | Tech Stack                          | ✅ Pass                    | All dependencies are stdlib — no unapproved packages                                                                                                                                                                                                                             |
| 2   | No web/API framework                                                   | Explicit Prohibitions               | ✅ Pass                    | No API calls in Feature 1; no FastAPI/Flask                                                                                                                                                                                                                                      |
| 3   | Flat files only — no database                                          | Explicit Prohibitions               | ✅ Pass                    | `.json`, `.csv`, `.md` only                                                                                                                                                                                                                                                      |
| 4   | No Docker / cloud / containerization                                   | Explicit Prohibitions               | ✅ Pass                    | Local execution only                                                                                                                                                                                                                                                             |
| 5   | Model anonymization before scoring                                     | Principle 2 / Security              | ✅ Pass                    | Model identity encoded as filename letter (`a`/`b`/`c`) at the asset layer. Real model names never appear in `eval_results.csv`, code filenames, or directory paths. `model_token` in `outputs/` paths is derived from the filename letter at load time. |
| 6   | All scoring logic deterministic                                        | Principle 2                         | ✅ Pass                    | Row count, checksum, and snapshot comparisons are fully script-enforced. Epsilon tolerance for float comparisons enforced per IEEE 754 and declared in `references/deterministic-rules.md`. No LLM judgment in any numeric result                                                |
| 7   | Synthetic data only, labeled in filename and header                    | Security / FR-016                   | ✅ Pass                    | All datasets bundled as labeled synthetic `.csv`                                                                                                                                                                                                                                 |
| 8   | No PII, no real financial identifiers                                  | Security                            | ✅ Pass                    | Synthetic data rules enforced at asset creation                                                                                                                                                                                                                                  |
| 9   | Artifact key format `task_id/model/category`                           | FR-011 (amended)                    | ✅ Pass                    | PM-ratified amendment confirmed to cover both SQL and Python artifact keys. Consistent with Feature 3                                                                                                                                                                            |
| 10  | No GPU dependencies                                                    | Explicit Prohibitions               | ✅ Pass                    | All dependencies are stdlib; no GPU-only packages                                                                                                                                                                                                                                |
| 11  | No `when_to_use` field in `SKILL.md`                                   | Tech Stack                          | ✅ Pass                    | Not applicable to scripts — Prompt Engineer to enforce during `SKILL.md` authoring                                                                                                                                                                                               |
| 12  | Critic persona not invoked in this feature                             | Principle 2 / FR-008                | ✅ Pass                    | SQL Critic scoped to Feature 2; absent from Feature 1 pipeline                                                                                                                                                                                                                   |
| 13  | No code execution at runtime                                           | Principle 6 / Explicit Prohibitions | ✅ Pass                    | All deterministic outputs pre-stored in `eval_results.csv`; harness is a comparison engine only                                                                                                                                                                                  |
| 14  | Pre-recorded data validated before scoring                             | FR-017                              | ✅ Pass                    | `schema_validator.py` validates `eval_results.csv` against `references/file-schema.md` — header exactness, variant enum, primary-key uniqueness, task-bank coverage, per-language null rules — before any scoring step                                                           |
| 15  | Task count ceiling (A1)                                                | Amendment A1                        | ✅ Pass                    | Task count raised from 20–40 to 100 SQL tasks. Client contract unchanged at 20 SQL tasks. `contracted` flag in `task_bank.csv` controls client-facing scorecard scope. A1 ratified.                                                                                              |
| 16  | Two-table unified architecture (A3)                                    | Amendment A3                        | ✅ Pass                    | `assets/answers/` and `answer_results/` folders replaced by `assets/task_bank.csv` + `assets/eval_results.csv`. Prompt text inline in `task_bank.csv`. Reference result sets remain at `assets/tasks/[task_id]/reference_results/`. A3 ratified.                                  |
| 17  | `contracted` flag in `task_bank.csv`                                   | Amendment A1                        | ✅ Pass                    | Boolean field on `task_bank.csv`. `true` for SQL-001–SQL-020. Single source of truth for `--contracted-only` scorecard filtering. Validated via `schema_validator.py`.                                                                                                           |
| 18  | Merge step (FR-019) for per-author files                               | Amendment A3                        | ✅ Pass                    | `results_a.csv`, `results_b.csv`, `results_c.csv` merged into `eval_results.csv` during dataset preparation via `merge_results.py`. Merge validates header consistency, variant enum, primary-key uniqueness, and row totals. Per-author files must not appear in the released zip. |


**All 18 items pass. Constitution Check gate is clear for A3-aligned implementation.**

---

## Project Structure

### Documentation (this feature)

```text
specs/001-sql-quant-eval/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

Single-project CLI skill — Option 1 applies.

```text
sql-skill/
├── SKILL.md                              # YAML frontmatter. References assets/task_bank.csv
│                                         # by path in one line. Body stays concise — task
│                                         # list is never embedded inline.
├── scripts/
│   ├── eval_task.py                      # CLI entry point:
│   │                                     # eval-task --engine sql
│   │                                     # [--task-id SQL-001] [--contracted-only]
│   │                                     # Reads task_bank.csv to resolve task_id → model
│   │                                     # filenames. Loads eval_results.csv filtered by
│   │                                     # (filename, dataset_variant) matching the task.
│   ├── anonymizer.py                     # Derives model_token from filename letter (a/b/c)
│   │                                     # before scoring pipeline. No real model names
│   │                                     # ever pass through scoring logic.
│   ├── schema_validator.py               # Validates eval_results.csv against
│   │                                     # references/file-schema.md before scoring begins
│   │                                     # (FR-017). Checks: header exactness, variant enum,
│   │                                     # primary-key uniqueness, task-bank coverage,
│   │                                     # per-language null rules.
│   ├── scorer.py                         # Interprets pre-recorded correctness fields
│   │                                     # (checksum, row_count, snapshot_pass) against
│   │                                     # reference result sets; applies clean-pass gate
│   ├── variant_scorer.py                 # Surfaces the four non-clean variant rows for
│   │                                     # 100%-passing model answers; reads schema_checker
│   │                                     # result to tag variants as mismatched.
│   ├── merge_results.py                  # NEW — dataset preparation utility. Concatenates
│   │                                     # results_a.csv, results_b.csv, results_c.csv into
│   │                                     # assets/eval_results.csv. Validates header
│   │                                     # consistency, variant enum, primary-key
│   │                                     # uniqueness, and row totals (FR-019). Not
│   │                                     # invoked by the harness at runtime.
│   ├── artifact_store.py                 # Persists all outputs to outputs/ keyed
│   │                                     # by task_id/model/category
│   └── schema_checker.py                 # Detects column/type mismatches between
│                                         # variant result sets and clean baseline
│                                         # schema at harness runtime; writes result
│                                         # to "variant_mismatch" field in result.json.
│                                         # (variant_mismatch is NOT stored in
│                                         # eval_results.csv — it is derived at runtime.)
└── assets/
    ├── task_bank.csv                     # Master index — 200 rows (100 SQL + 100 Python).
    │                                     # Fields: task_id, contracted, category, prompt,
    │                                     # model_a_filename, model_b_filename,
    │                                     # model_c_filename. Prompt text inline —
    │                                     # no separate prompt.md file per task.
    │                                     # All scripts resolve file paths through this index.
    ├── eval_results.csv                  # Unified pre-recorded metrics — up to 3,000 rows.
    │                                     # Schema: filename, dataset_variant,
    │                                     # token_usage_input, token_usage_output,
    │                                     # runtime_ms, peak_memory_bytes (Python only),
    │                                     # formatting_violations, pytest_filename
    │                                     # (Python only), pytest_pass (Python only),
    │                                     # checksum (SQL only), row_count (SQL only),
    │                                     # snapshot_pass (SQL only).
    │                                     # Primary key: (filename, dataset_variant).
    │                                     # Produced by merge_results.py during dataset prep.
    ├── tasks/
    │   └── [task_id]/
    │       ├── task{N}a.sql              # Claude Sonnet 4.5's generated SQL
    │       ├── task{N}b.sql              # Gemini 2.5 Flash's generated SQL
    │       ├── task{N}c.sql              # ChatGPT 5.2 Codex's generated SQL (baseline)
    │       ├── reference_solution.sql    # Baseline reference SQL
    │       └── reference_results/
    │           ├── clean.csv
    │           ├── null_heavy.csv
    │           ├── duplicate_heavy.csv
    │           ├── medium.csv
    │           └── large.csv
    └── datasets/
        ├── synthetic_clean_*.csv         # transactions, accounts, daily_balances
        ├── synthetic_null_heavy_*.csv
        ├── synthetic_duplicate_heavy_*.csv
        ├── synthetic_medium_*.csv
        └── synthetic_large_*.csv

outputs/                                  # Runtime output — not bundled in zip
    └── [task_id]/
        └── [model]/
            └── [category]/
                └── result.json           # Per-run artifact: correctness scores,
                                          # performance metrics, per-variant results,
                                          # variant_mismatch flag (derived at runtime),
                                          # formatting_violations,
                                          # contracted flag (from task_bank.csv)

references/                               # Shared layer (zip root)
├── methodology.md
├── rubric.md
├── file-schema.md                        # Unified eval_results.csv schema + task_bank.csv
│                                         # schema + result.json schema. Single source of
│                                         # truth for schema_validator.py.
└── deterministic-rules.md

requirements.txt                          # Shared — all Python dependencies

tests/                                    # Harness self-tests
├── unit/
│   ├── test_anonymizer.py
│   ├── test_scorer.py
│   ├── test_schema_validator.py
│   ├── test_merge_results.py             # NEW — covers FR-019 merge validation
│   └── test_artifact_store.py
└── integration/
    └── test_eval_task_pipeline.py

# Authoring-only — NOT bundled in release zip:
#   results_a.csv, results_b.csv, results_c.csv
#   (merged into assets/eval_results.csv by merge_results.py before release)
```

**Structure Decision**: Single-project CLI skill. All Feature 1 scripts live under `sql-skill/scripts/`. The pre-recorded metric architecture follows Amendment A3: a two-table design with `assets/task_bank.csv` as master index and `assets/eval_results.csv` as unified metrics. Model identity is encoded in code filenames (`a`/`b`/`c`) — no `model_token` or `language` column is stored in `eval_results.csv`; both are derived from the `filename` field at load time. Prompt text is stored inline in `task_bank.csv` — per-task `prompt.md` files are no longer created. Reference result sets remain co-located per `task_id` under `assets/tasks/[task_id]/reference_results/` — one `.csv` per variant, unchanged from prior architecture. `eval_task.py` reads `task_bank.csv` first on every invocation to resolve `task_id` to filenames, then filters `eval_results.csv` by `(filename, dataset_variant)`. `schema_validator.py` validates `eval_results.csv` against `references/file-schema.md` before any scoring begins per FR-017; the prior `contracted` cross-check between answer files and `task_bank.csv` is obsolete (single source of truth in `task_bank.csv`) and replaced by a task-bank coverage check (every filename-derivable `task_id` must exist in `task_bank.csv`). A new `merge_results.py` script (FR-019) is provided for dataset preparation to concatenate the three per-author files (`results_a.csv`, `results_b.csv`, `results_c.csv`) into `assets/eval_results.csv` before release — per-author files must not appear in the released zip. Dataset filenames are prefixed `synthetic_` to satisfy the Constitution's labeling requirement. Scored output artifacts are written to `outputs/task_id/model/category/result.json` at runtime and excluded from the zipped deliverable.

---

## Complexity Tracking


| Violation                                               | Why Needed                                                                                                                                                                                                                                                                   | Simpler Alternative Rejected Because                                                                                                                             |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 100 SQL tasks vs. contracted 20                         | Value-add scope agreed by team. Client contract unchanged at 20 SQL tasks. `contracted` flag controls all client-facing output. The additional 80 tasks provide a statistically stronger evaluation at no additional architectural cost.                                     | Delivering only 20 tasks produces a narrower evidence base that weakens the client's ability to make a well-founded model selection decision.                    |
| Two-table unified architecture with per-author authoring convention | The three-person team authors pre-recorded data independently on separate machines — one per model. A per-author file is the natural unit of work. Consolidating to a single `eval_results.csv` before release gives downstream consumers a single-pass read model. | A single monolithic file authored jointly would require shared environment access and real-time coordination. Separate per-model deliverables avoid merge conflicts and keep the authoring workflow fully parallel. |


