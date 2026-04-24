# Implementation Plan: Feature 1 — SQL Quantitative Evaluation

**Branch**: `001-sql-quant-eval` | **Date**: 2026-04-08 | **Last Updated**: 2026-04-24 | **Status**: ✅ Complete (V1)

> **Amendment A4 — April 2026 (ratified):** Task count revised to 30 SQL tasks. No `--contracted-only` flag — all 30 tasks are the client deliverable. Model letters corrected: `a` = Claude Sonnet 4.5, `b` = ChatGPT 5.2 Codex (baseline), `c` = Gemini 2.5 Flash. Correctness gate revised to row count majority consensus (not `snapshot_pass`). Performance scoring revised to 10-band percentile (no baseline dependency). `formatting_pass_pct` replaces `formatting_violations`. `run_eval.py` is the sole entry point — no `eval-task` CLI, no `schema_validator.py`, no `references/` folder. Per-author files renamed to `results_table_a/b/c.csv`.

> **Amendment A3 — April 2026 (ratified):** Two-table design adopted. `assets/task_bank.csv` + `assets/eval_results.csv`. Filename-based identity convention established.

---

## Summary

Feature 1 implements the SQL quantitative evaluation pipeline within the `sql-skill/` Agent Skill. It gives Analytics Engineers and Evaluation Leads at the Banking Institution an objective, numeric basis for comparing AI model performance on SQL analytics tasks.

Model SQL code files are stored under `assets/tasks/[task_id]/` — three per task, one per model (`task{N}a.sql`, `task{N}b.sql`, `task{N}c.sql`). All tasks are resolved through the master index at `assets/task_bank.csv`. Pre-recorded numeric metrics for every model × task × variant are stored as rows in `assets/eval_results.csv` — SQL rows populate `row_count`, `checksum`, `snapshot_pass`, `runtime_ms`, `formatting_pass_pct`, `token_usage_input`, and `token_usage_output`; Python-only fields (`peak_memory_bytes`, `pytest_filename`, `pytest_pass_pct`) are null for SQL rows.

**No code is executed at runtime.** The harness reads each model's metric rows for a given Task ID — five rows per filename across five variants — and scores across four dimensions:

- **Correctness** — Row count majority consensus across all 3 models on the clean variant. Pass = 25 pts. Fail = 0. Clean gate must pass before reliability is scored.
- **Formatting** — Mean `formatting_pass_pct` across all 5 variants / 100 × 25.
- **Performance** — 10-band percentile scoring on runtime and tokens. No baseline dependency. Top 10% = 25, bottom 10% = 2.5.
- **Reliability** — Row count consensus pass rate across 4 non-clean variants × 25. Only scored if correctness passes.

All artifacts are persisted under `outputs/[timestamp]/`. Model identifiers are encoded as filename letters (`a`/`b`/`c`) throughout. Real model names are used only in scorecard output via the `MODEL_NAMES` lookup in `run_eval.py`.

---

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: `csv`, `json`, `statistics`, `pathlib`, `re`, `datetime`, `collections` — stdlib only
**Storage**: Flat files only — `.json` and `.md` for scorecard output, `.csv` for `task_bank.csv` and `eval_results.csv`. No database.
**Entry Point**: `python sql-skill/scripts/run_eval.py` (all tasks) or `python sql-skill/scripts/run_eval.py --task-id SQL-001` (single task)
**Target Platform**: Local development, Linux/macOS/Windows — no cloud, no Docker
**Constraints**:
- No code execution at runtime — harness is a comparison and aggregation engine only
- No database of any kind
- No `--contracted-only` flag — all 30 SQL tasks are the deliverable
- Flat-file storage only
- No GPU dependencies

**Scale/Scope**: 30 SQL tasks × 3 models × 5 variants = **450 SQL rows in `eval_results.csv`**

---

## Constitution Check (V1)

| # | Rule | Source | Status | Notes |
|:--|:-----|:-------|:-------|:------|
| 1 | Python 3.10+ only | Tech Stack | ✅ Pass | All dependencies are stdlib |
| 2 | No web/API framework | Explicit Prohibitions | ✅ Pass | No FastAPI/Flask |
| 3 | Flat files only — no database | Explicit Prohibitions | ✅ Pass | `.json`, `.csv`, `.md` only |
| 4 | No Docker / cloud / containerization | Explicit Prohibitions | ✅ Pass | Local execution only |
| 5 | Model anonymization enforced | Principle 2 / Security | ✅ Pass | Filename letter convention (`a`/`b`/`c`) throughout. Real names in `MODEL_NAMES` dict only. |
| 6 | No code execution at runtime | Principle 6 | ✅ Pass | Harness reads pre-recorded metrics only |
| 7 | All numeric scoring deterministic | Principle 2 | ✅ Pass | Script-enforced. Same inputs always produce same scores. |
| 8 | Synthetic data only | Security / FR-015 | ✅ Pass | Datasets labeled `synthetic_` in filename and header |
| 9 | No PII, no real financial identifiers | Security | ✅ Pass | All datasets are synthetic |
| 10 | No GPU dependencies | Explicit Prohibitions | ✅ Pass | stdlib only |
| 11 | Client referred to as "Banking Institution" only | Security | ✅ Pass | No client name in any script or output |
| 12 | Per-author files excluded from release zip | FR-016 | ✅ Pass | `results_table_a/b/c.csv` excluded; only merged `eval_results.csv` ships |
| 13 | Correctness gate enforced before reliability | Scoring System | ✅ Pass | Row count consensus on clean variant required; reliability scores 0 if gate fails |
| 14 | No `--contracted-only` flag | Amendment A4 | ✅ Pass | All 30 SQL tasks are the client deliverable |
| 15 | Timestamped output folders — no overwriting | FR-010 | ✅ Pass | Each run creates `outputs/[YYYY-MM-DD_HH-MM]/` |

**All 15 items pass.**

---

## Project Structure

```
sql-skill/
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
│       ├── task{N}a.sql         # Claude Sonnet 4.5's generated SQL
│       ├── task{N}b.sql         # ChatGPT 5.2 Codex's generated SQL (baseline)
│       ├── task{N}c.sql         # Gemini 2.5 Flash's generated SQL
│       └── reference_solution.sql
└── datasets/
    ├── synthetic_clean_*.csv
    ├── synthetic_null_heavy_*.csv
    ├── synthetic_duplicate_heavy_*.csv
    ├── synthetic_medium_*.csv
    └── synthetic_large_*.csv

outputs/
└── [YYYY-MM-DD_HH-MM]/
    ├── sql_scorecard_all.md
    ├── sql_scorecard_all.json
    ├── sql_scorecard_[task_id].md     ← single task run
    └── sql_scorecard_[task_id].json

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
| Correctness gate | Row count majority consensus across all 3 models on clean variant | `snapshot_pass` was comparing against model `c` only — unreliable. Consensus is model-agnostic. |
| Performance scoring | 10-band percentile, no baseline dependency | Baseline-relative scoring caused division by zero and penalised models doing legitimate work |
| No `--contracted-only` flag | All 30 tasks are the deliverable | Scope settled at 60 tasks total with no contracted subset in V1 |
| `formatting_pass_pct` | Percentage-based metric across 5 variants | Enables consistent 0–25 scaling; more informative than raw violation count |
| Timestamped output folders | `outputs/[YYYY-MM-DD_HH-MM]/` | No overwriting between runs; full history preserved |

---

## Complexity Tracking

| Item | Resolution |
|:-----|:-----------|
| 30 SQL tasks vs. original 100 | Scope revised to 60 total (30 SQL + 30 Python) under Amendment A4. All 30 are the client deliverable. |
| Two-table architecture with per-author convention | Three team members author data independently on separate machines. `merge_results.py` consolidates before release. Single-pass read model for downstream consumers. |
