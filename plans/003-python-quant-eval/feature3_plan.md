# Implementation Plan: Feature 3 — Python Quantitative Evaluation

**Branch**: `003-python-quant-eval` | **Date**: 2026-04-08 | **Last Updated**: 2026-04-24 | **Status**: ✅ Complete (V1)

> **Amendment A4 — April 2026 (ratified):** Task count revised to 30 Python tasks. No `--contracted-only` flag — all 30 tasks are the client deliverable. Model letters corrected: `a` = Claude Sonnet 4.5, `b` = ChatGPT 5.2 Codex (baseline), `c` = Gemini 2.5 Flash. Correctness gate is `pytest_pass_pct = 100` on clean variant. Performance scoring revised to 10-band percentile across 3 sub-scores (runtime, memory, tokens). `formatting_pass_pct` replaces `formatting_violations`. `run_eval.py` is the sole entry point — no `eval-task` CLI, no `schema_validator.py`, no `references/` folder. Per-author files renamed to `results_table_a/b/c.csv`.

> **Amendment A3 — April 2026 (ratified):** Two-table design adopted. `assets/task_bank.csv` + `assets/eval_results.csv`. Python-only fields: `peak_memory_bytes`, `pytest_filename`, `pytest_pass_pct`.

---

## Summary

Feature 3 implements the Python quantitative evaluation pipeline within the `python-skill/` Agent Skill. It gives Analytics Engineers and Data Engineers at the Banking Institution an objective, numeric basis for comparing AI model performance on Python ETL and analytics tasks.

All evaluation data is pre-recorded during the dataset preparation phase and bundled as flat-file assets. Model Python code files are stored under `assets/tasks/[task_id]/` — three per task (`task{N}a.py`, `task{N}b.py`, `task{N}c.py`). All tasks are resolved through `assets/task_bank.csv`. Pre-recorded metrics in `assets/eval_results.csv` — Python rows populate `pytest_pass_pct`, `peak_memory_bytes`, `runtime_ms`, `formatting_pass_pct`, `token_usage_input`, and `token_usage_output`; SQL-only fields (`checksum`, `row_count`, `snapshot_pass`) are null for Python rows.

**No model-generated code is executed at runtime.** The harness reads each model's metric rows for a given Task ID — five rows per filename across five variants — and scores across four dimensions:

- **Correctness** — `pytest_pass_pct = 100` on the clean variant. Pass = 25 pts. Fail = 0. Clean gate must pass before reliability is scored.
- **Formatting** — Mean `formatting_pass_pct` across all 5 variants / 100 × 25.
- **Performance** — 10-band percentile scoring on runtime, memory, and tokens averaged. No baseline dependency.
- **Reliability** — `pytest_pass_pct = 100` pass rate across 4 non-clean variants × 25. Only scored if correctness passes.

All artifacts are persisted under `outputs/[timestamp]/`. Model identifiers are encoded as filename letters (`a`/`b`/`c`) throughout. Real model names used only in scorecard output via `MODEL_NAMES` lookup.

---

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: `csv`, `json`, `statistics`, `pathlib`, `re`, `datetime`, `collections` — stdlib only. pytest, tracemalloc, and flake8 are dataset preparation tools only — not invoked at runtime.
**Storage**: Flat files only — `.json` and `.md` for scorecard output, `.csv` for `task_bank.csv` and `eval_results.csv`. No database.
**Entry Point**: `python python-skill/scripts/run_eval.py` (all tasks) or `python python-skill/scripts/run_eval.py --task-id PY-001` (single task)
**Target Platform**: Local development, Linux/macOS/Windows — no cloud, no Docker
**Constraints**:
- No code execution at runtime — harness is a comparison and aggregation engine only
- No database of any kind
- No `--contracted-only` flag — all 30 Python tasks are the deliverable
- Flat-file storage only
- No GPU dependencies

**Scale/Scope**: 30 Python tasks × 3 models × 5 variants = **450 Python rows in `eval_results.csv`**

---

## Constitution Check (V1)

| # | Rule | Source | Status | Notes |
|:--|:-----|:-------|:-------|:------|
| 1 | Python 3.10+ only | Tech Stack | ✅ Pass | All dependencies are stdlib |
| 2 | No web/API framework | Explicit Prohibitions | ✅ Pass | No FastAPI/Flask |
| 3 | Flat files only — no database | Explicit Prohibitions | ✅ Pass | `.json`, `.csv`, `.md` only |
| 4 | No Docker / cloud / containerization | Explicit Prohibitions | ✅ Pass | Local execution only |
| 5 | Model anonymization enforced | Principle 2 / Security | ✅ Pass | Filename letter convention (`a`/`b`/`c`) throughout |
| 6 | No code execution at runtime | Principle 6 | ✅ Pass | pytest, tracemalloc, flake8 are dataset preparation tools only |
| 7 | All numeric scoring deterministic | Principle 2 | ✅ Pass | Script-enforced. Same inputs always produce same scores. |
| 8 | Synthetic data only | Security / FR-015 | ✅ Pass | Datasets labeled `synthetic_` in filename and header |
| 9 | No PII, no real financial identifiers | Security | ✅ Pass | All datasets are synthetic |
| 10 | No GPU dependencies | Explicit Prohibitions | ✅ Pass | stdlib only |
| 11 | Client referred to as "Banking Institution" only | Security | ✅ Pass | No client name in any script or output |
| 12 | Per-author files excluded from release zip | FR-016 | ✅ Pass | `results_table_a/b/c.csv` excluded; only merged `eval_results.csv` ships |
| 13 | Correctness gate enforced before reliability | Scoring System | ✅ Pass | `pytest_pass_pct = 100` on clean required; reliability scores 0 if gate fails |
| 14 | No `--contracted-only` flag | Amendment A4 | ✅ Pass | All 30 Python tasks are the client deliverable |
| 15 | Timestamped output folders — no overwriting | FR-010 | ✅ Pass | Each run creates `outputs/[YYYY-MM-DD_HH-MM]/` |

**All 15 items pass.**

---

## Project Structure

```
python-skill/
├── SKILL.md
└── scripts/
    └── run_eval.py              # Sole entry point. Reads task_bank.csv,
                                 # filters eval_results.csv, scores all
                                 # 4 dimensions, writes scorecard .md + .json,
                                 # writes Critic placeholders.

assets/
├── task_bank.csv                # 60 rows — master index for all tasks
├── eval_results.csv             # 900 rows — unified pre-recorded metrics
├── tasks/
│   └── [task_id]/
│       ├── task{N}a.py          # Claude Sonnet 4.5's generated Python
│       ├── task{N}b.py          # ChatGPT 5.2 Codex's generated Python (baseline)
│       ├── task{N}c.py          # Gemini 2.5 Flash's generated Python
│       ├── reference_solution.py
│       └── test_solution.py     # Documentation artifact — not executed by harness
└── datasets/
    ├── synthetic_clean_*.csv
    ├── synthetic_null_heavy_*.csv
    ├── synthetic_duplicate_heavy_*.csv
    ├── synthetic_medium_*.csv
    └── synthetic_large_*.csv

outputs/
└── [YYYY-MM-DD_HH-MM]/
    ├── python_scorecard_all.md
    ├── python_scorecard_all.json
    ├── python_scorecard_[task_id].md     ← single task run
    └── python_scorecard_[task_id].json

merge_results.py                 # Repo root — merges results_table_a/b/c.csv
                                 # into assets/eval_results.csv

# Authoring-only — NOT in release zip:
#   authoring_only/results_table_a.csv
#   authoring_only/results_table_b.csv
#   authoring_only/results_table_c.csv
```

---

## Key Design Decisions

| Decision | What Was Chosen | Why |
|:---------|:----------------|:----|
| Correctness gate | `pytest_pass_pct = 100` on clean variant | Direct test result — unambiguous pass/fail |
| Performance sub-scores | 3 averaged: runtime + memory + tokens | Memory is Python-specific signal not available for SQL; averaging gives balanced view |
| 10-band percentile scoring | Fixed thresholds from dataset distribution | No baseline dependency; no division by zero; Gemini scoring 0 on correctness doesn't distort performance bands |
| `formatting_pass_pct` | Percentage-based metric across 5 variants | Consistent 0–25 scaling; more informative than raw violation count |
| `test_solution.py` as documentation only | Not executed at runtime | Harness reads pre-recorded `pytest_pass_pct` — no live test execution needed |

---

## Complexity Tracking

| Item | Resolution |
|:-----|:-----------|
| 30 Python tasks vs. original 100 | Scope revised to 60 total (30 SQL + 30 Python) under Amendment A4. All 30 are the client deliverable. |
| Gemini scores 0 on most Python correctness | Genuine model finding — not a framework bug. Documented in DEBT.md. Reliability correctly scores 0 as consequence of correctness gate. |
| Two-table architecture with per-author convention | Three team members author data independently. `merge_results.py` consolidates before release. Shared `eval_results.csv` serves both SQL and Python skills. |
