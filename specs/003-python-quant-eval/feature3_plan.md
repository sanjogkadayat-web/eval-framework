# Implementation Plan: Feature 3 — Python Quantitative Evaluation

**Branch**: `003-python-quant-eval` | **Date**: 2026-04-08 | **Last Updated**: 2026-04-18 | **Spec**: `specs/003-python-quant-eval/spec.md`
**Input**: Feature specification from `/specs/003-python-quant-eval/spec.md`

> **Amendment A3 — April 2026 (ratified 2026-04-18):** The three-file `assets/answers/` architecture for Python and the three-file `assets/variant_results/` architecture are both replaced by a two-table design: `assets/task_bank.csv` (master index, 200 rows with prompts inline and per-model filename references) and `assets/eval_results.csv` (unified metrics, up to 3,000 rows total). Model identity and language are encoded in code filenames (`task1a.py`, `task1b.py`, …). Python-only metric fields in `eval_results.csv` are `peak_memory_bytes`, `pytest_filename`, `pytest_pass` (all null for SQL rows). Per-author files (`results_a.csv`, `results_b.csv`, `results_c.csv`) are merged into `eval_results.csv` via FR-019 before release. See Constitution Amendment A3 for full rationale.

> **Amendment A1 — April 2026 (ratified 2026-04-09):** Task count raised from 20–40 to 100 Python tasks. Client contract unchanged at 20 Python tasks. `--contracted-only` CLI flag added. A1's consolidated answer-file and variant-results-file architecture has been superseded by A3's unified `eval_results.csv`; task-count and contracted-flag aspects of A1 remain in effect.

---

## Summary

Feature 3 implements the Python quantitative evaluation pipeline within the `python-skill/` Agent Skill. It gives Analytics Engineers and Data Engineers at the Banking Institution an objective, numeric basis for comparing AI model performance on Python ETL tasks — separating correctness from speed and resource cost.

All evaluation data is pre-recorded during the dataset preparation phase and bundled as flat-file assets. Model Python code files are stored under `assets/tasks/[task_id]/` — three per task, one per model (`task{N}a.py`, `task{N}b.py`, `task{N}c.py`). All tasks are resolved through the master index at `assets/task_bank.csv`, which also stores the standardized prompt text inline. Pre-recorded numeric metrics for every model × task × variant are stored as rows in the unified `assets/eval_results.csv` table — Python rows populate the `pytest_filename` and `pytest_pass` correctness fields, the `runtime_ms` and `peak_memory_bytes` performance fields, the `formatting_violations` formatting field, and the `token_usage_input` / `token_usage_output` generation fields; the SQL-only fields (`checksum`, `row_count`, `snapshot_pass`) are null for Python rows.

**No model-generated code is executed at runtime** — the harness reads, compares, and aggregates pre-recorded data only. The harness reads each model's metric rows for a given Task ID — five rows per filename across the five variants — and reports across two numeric dimensions:

- **Correctness** — pre-recorded pytest pass/fail from the `pytest_pass` field in `eval_results.csv`. A 100% pytest pass on the clean variant (in the pre-recorded data) is the gate condition for including the remaining four variant rows in the scorecard.
- **Performance** — wall-clock `runtime_ms` and `peak_memory_bytes` read from `eval_results.csv` per variant; `token_usage_input` and `token_usage_output` also read from `eval_results.csv` (same value across all five variant rows for a given filename). All metrics are pre-recorded during dataset preparation.

All artifacts (code files, scored output, per-dimension metrics) are persisted as flat files keyed by `task_id/model/category`. Model identifiers are never exposed to scoring logic — they are encoded as filename letters (`a`/`b`/`c`) and re-associated only after all numeric scores are recorded.

The flake8 violation count is pre-recorded in `eval_results.csv` as `formatting_violations` and written to `result.json` as part of the quantitative pipeline. The Python Critic persona review is handled separately in Feature 4.

The `--contracted-only` flag limits evaluation to the 20 contracted Python tasks (PY-001–PY-020, identified by `contracted = true` in `task_bank.csv`). When omitted, all 100 Python tasks are evaluated. The client-facing scorecard is always run with `--contracted-only`. The full 100-task scorecard is delivered as a value-add beyond the contract.

---

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: `csv` / `json` (flat-file I/O — stdlib). No third-party packages required for the harness. pytest, tracemalloc, and flake8 are used during dataset preparation only — not invoked by the harness at runtime.
**Storage**: Flat files only — `.json` for metrics and artifacts, `.csv` for `task_bank.csv`, `eval_results.csv`, and datasets, `.md` for human-readable output. No database.
**Testing**: pytest — harness self-tests only. Harness self-tests cover the scorer (which reads pre-recorded data, not invokes pytest), anonymizer, schema checker, schema validator, and artifact store. The merge script (`merge_results.py`) is owned by Feature 1; Feature 3 self-tests rely on fixture `eval_results.csv` files and do not re-test the merge logic.
**Target Platform**: Local development, Linux/macOS — no cloud, no Docker, no containerization
**Project Type**: CLI skill — invoked via `eval-task --engine python [--task-id PY-001] [--contracted-only]` within the `python-skill/` Agent Skill
**Performance Goals**: Wall-clock runtime and peak memory are read from pre-recorded rows in `eval_results.csv`. Token usage is also read from `eval_results.csv` (same value across all five variant rows for a given filename). All metrics surfaced as-is for cross-model comparison against the ChatGPT 5.2 Codex baseline (filename letter `c`). No live measurement occurs during harness execution.
**Constraints**:

- No code execution at runtime — harness is a comparison and aggregation engine only (Principle 6)
- No API calls in this feature
- No database
- No GPU dependencies
- Model anonymization enforced at the asset layer via filename letter convention (`a`/`b`/`c`); no real model names appear anywhere in the pre-recorded data
- Flat-file storage only

**Scale/Scope**:

- Full build ceiling: 100 Python tasks × 3 models × 5 variants = **1,500 Python rows in `eval_results.csv`**
- Client-contracted ceiling (`--contracted-only`): 20 Python tasks × 3 models × 5 variants = **300 Python rows**
- Realistic scorecard coverage is lower in both cases: the four non-clean variant rows are only surfaced in the scorecard for model answers that achieve 100% pytest pass on the clean dataset.

---

## Constitution Check

*GATE: All items must pass (or have an approved amendment in progress) before implementation begins. Re-check after technical design is finalized.*


| #   | Rule                                                                     | Source                              | Status                    | Notes                                                                                                                                                                                                                                                                                              |
| --- | ------------------------------------------------------------------------ | ----------------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Python 3.11+ only                                                        | Tech Stack                          | ✅ Pass                    | All harness dependencies are stdlib — no unapproved packages                                                                                                                                                                                                                                       |
| 2   | No web/API framework                                                     | Explicit Prohibitions               | ✅ Pass                    | No API calls in Feature 3; no FastAPI/Flask                                                                                                                                                                                                                                                        |
| 3   | Flat files only — no database                                            | Explicit Prohibitions               | ✅ Pass                    | `.json`, `.csv`, `.md` only                                                                                                                                                                                                                                                                        |
| 4   | No Docker / cloud / containerization                                     | Explicit Prohibitions               | ✅ Pass                    | Local execution only                                                                                                                                                                                                                                                                               |
| 5   | Model anonymization before scoring                                       | Principle 2 / Security              | ✅ Pass                    | Model identity encoded as filename letter (`a`/`b`/`c`) at the asset layer from ingestion onward. Real model names never appear in `eval_results.csv`, code filenames, or directory paths. `model_token` in `outputs/` paths is derived from the filename letter at load time. Consistent with Feature 1. |
| 6   | All scoring logic deterministic                                          | Principle 2                         | ✅ Pass                    | All results read from pre-recorded data; scoring is comparison of pre-recorded values against gates (e.g., 100% clean pass). No LLM judgment in any numeric result. **Known gap**: wall-clock runtime is non-deterministic by nature; variance window is deferred to post-V1 [TBD] per Constitution |
| 7   | Synthetic data only, labeled in filename and header                      | Security / FR-016                   | ✅ Pass                    | All datasets bundled as labeled synthetic `.csv`                                                                                                                                                                                                                                                   |
| 8   | No PII, no real financial identifiers                                    | Security                            | ✅ Pass                    | Synthetic data rules enforced at asset creation                                                                                                                                                                                                                                                    |
| 9   | Artifact key format `task_id/model/category`                             | FR-011 (amended)                    | ✅ Pass                    | Constitution amendment ratified by PM. Artifact keys for Feature 3 use `task_id/model/category`. FR-011 updated in Constitution accordingly.                                                                                                                                                       |
| 10  | No GPU dependencies                                                      | Explicit Prohibitions               | ✅ Pass                    | No GPU-only packages in dependency list                                                                                                                                                                                                                                                            |
| 11  | No `when_to_use` field in `SKILL.md`                                     | Tech Stack                          | ✅ Pass                    | Not applicable to scripts — Prompt Engineer to enforce during `SKILL.md` authoring                                                                                                                                                                                                                 |
| 12  | Critic persona not invoked in this feature                               | Principle 2 / FR-008/009            | ✅ Pass                    | Critic scoped to Feature 4; absent from Feature 3 pipeline                                                                                                                                                                                                                                         |
| 13  | No code execution at runtime                                             | Principle 6 / Explicit Prohibitions | ✅ Pass                    | No pytest, tracemalloc, or flake8 invocation by harness. All results pre-recorded in `eval_results.csv`                                                                                                                                                                                            |
| 14  | Token usage captured per task per model                                  | FR-006 / FR-010                     | ✅ Pass                    | Pre-stored as `token_usage_input` and `token_usage_output` fields in `eval_results.csv` — same value across all five variant rows for a given filename. Same approach as Feature 1 for SQL                                                                                                         |
| 15  | One-shot accuracy reportable per model                                   | FR-010                              | ✅ Pass                    | Derived from pre-recorded `pytest_pass` on clean variant — one attempt per model per task, no revisions                                                                                                                                                                                            |
| 16  | Pre-recorded data validated before scoring                               | FR-017                              | ✅ Pass                    | `schema_validator.py` validates `eval_results.csv` against `references/file-schema.md` — header exactness, variant enum, primary-key uniqueness, task-bank coverage, per-language null rules — before any scoring step. Python rows must have `pytest_pass`, `pytest_filename`, `peak_memory_bytes` populated and SQL-only fields null. |
| 17  | Task count ceiling (A1)                                                  | Amendment A1                        | ✅ Pass                    | Task count raised from 20–40 to 100 Python tasks. Client contract unchanged at 20 Python tasks. `contracted` flag in `task_bank.csv` controls client-facing scorecard scope. A1 ratified.                                                                                                          |
| 18  | Two-table unified architecture (A3)                                      | Amendment A3                        | ✅ Pass                    | `assets/answers/` and `assets/variant_results/` replaced by `assets/task_bank.csv` + `assets/eval_results.csv`. A3 ratified.                                                                                                                                                                       |
| 19  | `contracted` flag in `task_bank.csv`                                     | Amendment A1                        | ✅ Pass                    | Boolean field on `task_bank.csv`. `true` for PY-001–PY-020. Single source of truth for `--contracted-only` scorecard filtering.                                                                                                                                                                    |


**All 19 items pass. Constitution Check gate is clear for A3-aligned implementation.**

---

## Project Structure

### Documentation (this feature)

```text
specs/003-python-quant-eval/
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
python-skill/
├── SKILL.md                                    # YAML frontmatter. References assets/task_bank.csv
│                                               # by path in one line. Body stays concise — task
│                                               # list is never embedded inline.
├── scripts/
│   ├── eval_task.py                            # CLI entry point:
│   │                                           # eval-task --engine python
│   │                                           # [--task-id PY-001] [--contracted-only]
│   │                                           # Reads task_bank.csv to resolve task_id → model
│   │                                           # filenames. Loads eval_results.csv filtered by
│   │                                           # (filename, dataset_variant) matching the task.
│   ├── anonymizer.py                           # Derives model_token from filename letter
│   │                                           # (a/b/c) before scoring pipeline. No real
│   │                                           # model names ever pass through scoring logic.
│   ├── schema_validator.py                     # Validates eval_results.csv against
│   │                                           # references/file-schema.md before scoring
│   │                                           # begins (FR-017). Checks: header exactness,
│   │                                           # variant enum, primary-key uniqueness,
│   │                                           # task-bank coverage, per-language null rules.
│   ├── scorer.py                               # Reads pre-recorded pytest_pass from
│   │                                           # eval_results.csv; applies gate logic
│   │                                           # (100% clean pass required for variant
│   │                                           # inclusion); writes scored output
│   ├── artifact_store.py                       # Persists all outputs to outputs/ keyed
│   │                                           # by task_id/model/category
│   └── schema_checker.py                       # Detects variant column/type mismatches
│                                               # at harness runtime; writes result to
│                                               # "variant_mismatch" field in result.json.
│                                               # (variant_mismatch is NOT stored in
│                                               # eval_results.csv — it is derived at runtime.)
└── assets/
    ├── task_bank.csv                           # Master index — 200 rows (100 SQL + 100 Python).
    │                                           # Shared with sql-skill. Fields: task_id,
    │                                           # contracted, category, prompt,
    │                                           # model_a_filename, model_b_filename,
    │                                           # model_c_filename. Prompt text inline —
    │                                           # no separate prompt.md file per task.
    │                                           # Scripts resolve all file paths through this index.
    ├── eval_results.csv                        # Unified pre-recorded metrics — up to 3,000 rows.
    │                                           # Shared with sql-skill. Schema: filename,
    │                                           # dataset_variant, token_usage_input,
    │                                           # token_usage_output, runtime_ms,
    │                                           # peak_memory_bytes (Python only),
    │                                           # formatting_violations, pytest_filename
    │                                           # (Python only), pytest_pass (Python only),
    │                                           # checksum (SQL only), row_count (SQL only),
    │                                           # snapshot_pass (SQL only).
    │                                           # Primary key: (filename, dataset_variant).
    │                                           # Produced by merge_results.py (owned by F1)
    │                                           # during dataset prep.
    ├── tasks/
    │   └── [task_id]/
    │       ├── task{N}a.py                     # Claude Sonnet 4.5's generated Python
    │       ├── task{N}b.py                     # Gemini 2.5 Flash's generated Python
    │       ├── task{N}c.py                     # ChatGPT 5.2 Codex's generated Python
    │       ├── reference_solution.py           # Baseline reference — documentation and
    │       │                                   # reproducibility artifact; not executed by harness
    │       └── test_solution.py                # pytest file — documentation and reproducibility
    │                                           # artifact; not executed by harness at runtime
    └── datasets/
        ├── synthetic_clean_*.csv
        ├── synthetic_null_heavy_*.csv
        ├── synthetic_duplicate_heavy_*.csv
        ├── synthetic_medium_*.csv
        └── synthetic_large_*.csv

outputs/                                        # Runtime output — not bundled in zip
    └── [task_id]/
        └── [model]/
            └── [category]/
                └── result.json                 # Per-run artifact: correctness scores
                                                # (from pytest_pass), performance metrics
                                                # (runtime_ms, peak_memory_bytes,
                                                # token_usage_input, token_usage_output),
                                                # per-variant results,
                                                # variant_mismatch flag (derived at runtime),
                                                # formatting_violations,
                                                # contracted flag (from task_bank.csv)

references/                                     # Shared layer (zip root)
├── methodology.md
├── rubric.md
├── file-schema.md                              # Unified eval_results.csv schema +
│                                               # task_bank.csv schema + result.json schema.
│                                               # Single source of truth for schema_validator.py.
└── deterministic-rules.md

requirements.txt                                # Shared — all Python dependencies

tests/                                          # Harness self-tests
├── unit/
│   ├── test_anonymizer.py
│   ├── test_scorer.py
│   ├── test_schema_validator.py
│   └── test_artifact_store.py
└── integration/
    └── test_eval_task_pipeline.py

# Authoring-only — NOT bundled in release zip:
#   results_a.csv, results_b.csv, results_c.csv
#   (merged into assets/eval_results.csv by merge_results.py — owned by Feature 1)
```

**Structure Decision**: Single-project CLI skill. All Feature 3 scripts live under `python-skill/scripts/`. The pre-recorded metric architecture follows Amendment A3: a two-table design with `assets/task_bank.csv` as master index and `assets/eval_results.csv` as unified metrics, shared with `sql-skill/`. Model identity is encoded in code filenames (`a`/`b`/`c`) — no `model_token` or `language` column is stored in `eval_results.csv`; both are derived from the `filename` field at load time. Prompt text is stored inline in `task_bank.csv` — per-task `prompt.md` files are no longer created. `eval_task.py` reads `task_bank.csv` first on every invocation to resolve `task_id` to filenames, then filters `eval_results.csv` by `(filename, dataset_variant)`. No `runner.py` or `variant_runner.py` — the harness does not execute model-generated code at runtime per Principle 6. `scorer.py` reads pre-recorded `pytest_pass` values from `eval_results.csv` and applies gate logic (100% clean pass required for variant inclusion in the scorecard). `reference_solution.py` and `test_solution.py` are retained as documentation and reproducibility artifacts but are not executed by the harness. Dataset filenames are prefixed `synthetic_`. `schema_validator.py` validates `eval_results.csv` against `references/file-schema.md` before any scoring begins per FR-017; the prior `contracted` cross-check between answer files and `task_bank.csv` is obsolete (single source of truth in `task_bank.csv`) and replaced by a task-bank coverage check. The merge script (`merge_results.py`) is owned by Feature 1 and produces `eval_results.csv` from the three per-author files during dataset preparation — Feature 3 consumes the merged output. Scored output artifacts are written to `outputs/task_id/model/category/result.json` at runtime and are excluded from the zipped deliverable.

---

## Complexity Tracking


| Violation                                                           | Why Needed                                                                                                                                                                                                                                                                                                                     | Simpler Alternative Rejected Because                                                                                                          |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| 100 Python tasks vs. contracted 20                                  | Value-add scope agreed by team. Client contract unchanged at 20 Python tasks. `contracted` flag controls all client-facing output. The additional 80 tasks provide a statistically stronger evaluation at no additional architectural cost.                                                                                    | Delivering only 20 tasks produces a narrower evidence base that weakens the client's ability to make a well-founded model selection decision. |
| Two-table unified architecture with per-author authoring convention | The three-person team authors pre-recorded data independently on separate machines — one per model. A per-author file is the natural unit of work. Consolidating to a single `eval_results.csv` before release gives downstream consumers (SQL skill, Python skill, scorecard) a single-pass read model across both languages. | Maintaining separate Python answer and variant-results files would fragment the read model and require joins across files at harness runtime. |


