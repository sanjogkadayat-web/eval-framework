# Implementation Plan: Feature 5 — Comparative Scorecard

**Branch**: `005-comparative-scorecard` | **Date**: 2026-04-08 | **Last Updated**: 2026-04-24 | **Status**: ✅ Complete (V1)

> **Amendment A4 — April 2026 (ratified):** No standalone `scorecard` CLI, no `collector.py`, no `aggregator.py`, no `run_scorecard.py`. Scorecard generation is fully integrated into each skill's `run_eval.py`. Both SQL and Python produce independent scorecards. No `--contracted-only` flag — all 60 tasks are the deliverable. Full scale revised to 900 rows (60 tasks × 3 models × 5 variants). Raw Metrics added as 6th scorecard section. Scorecard output is timestamped per run — no overwriting.

> **Amendment A3 — April 2026 (ratified):** Two-table design. `formatting_pass_pct` replaces `formatting_violations`. No `generation_time_ms`.

> **Amendment A2 — April 2026 (ratified):** `generation_time_ms` removed from all schemas.

---

## Summary

Feature 5 implements the comparative scorecard — the aggregated output that surfaces all quantitative scores, delta analysis, Critic Review, and raw metrics across all three models for any configured set of tasks.

In V1, scorecard generation is fully integrated into each skill's `run_eval.py`. There is no separate `scorecard` CLI or `collector.py`. Each `run_eval.py` reads `eval_results.csv` directly and produces a complete scorecard in a single pass.

Two scorecards are produced independently:

- **`sql_scorecard_[tag].md` + `.json`** — produced by `sql-skill/scripts/run_eval.py`
- **`python_scorecard_[tag].md` + `.json`** — produced by `python-skill/scripts/run_eval.py`

Each scorecard contains **six sections in order**:

1. **Summary Table** — mean scores across all tasks per model (omitted for single-task runs)
2. **Delta Table** — model `a` and `c` vs ChatGPT 5.2 Codex baseline (omitted for single-task runs)
3. **Quantitative Assessment** — per-task score breakdown with reliability ticks ✓/✗ per variant
4. **Critic Review** — `<!-- CRITIC:... -->` placeholders, filled by AI at runtime
5. **Metric Key** — scoring formula reference
6. **Raw Metrics** — actual runtime (ms), token usage (input + output), and peak memory (bytes, Python only) per model per task

All aggregation is deterministic and script-enforced. No LLM judgment is used in any numeric dimension. Real model names are used throughout the scorecard output via the `MODEL_NAMES` lookup — re-association happens at scorecard generation time after all scoring is complete.

---

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: `csv`, `json`, `statistics`, `pathlib`, `re`, `datetime`, `collections` — stdlib only
**Storage**: Reads `assets/task_bank.csv` and `assets/eval_results.csv`. Writes `.md` and `.json` to `outputs/[YYYY-MM-DD_HH-MM]/`. No database.
**Entry Point**: Integrated into each skill's `run_eval.py`. No standalone CLI.
**Target Platform**: Local development — no cloud, no Docker
**Constraints**:
- No LLM invocation of any kind in scoring logic
- No API calls
- No database
- No GPU dependencies
- All aggregation and delta logic deterministic and script-enforced
- No `--contracted-only` flag

**Scale/Scope**:
- Full run: 30 tasks × 3 models = **90 scored records per skill**
- Single-task run: 3 models = **3 scored records**
- Each run outputs 1 `.md` + 1 `.json`

---

## Constitution Check (V1)

| # | Rule | Source | Status | Notes |
|:--|:-----|:-------|:-------|:------|
| 1 | Python 3.10+ only | Tech Stack | ✅ Pass | All dependencies are stdlib |
| 2 | No web/API framework | Explicit Prohibitions | ✅ Pass | No FastAPI/Flask; no external calls |
| 3 | Flat files only — no database | Explicit Prohibitions | ✅ Pass | Reads `.csv`; writes `.md` and `.json` |
| 4 | No Docker / cloud / containerization | Explicit Prohibitions | ✅ Pass | Local execution only |
| 5 | Model identifiers re-associated only after all scoring complete | Principle 2 / Security | ✅ Pass | `MODEL_NAMES` lookup applied during scorecard write — after all numeric scores computed |
| 6 | All scoring/ranking logic deterministic | Principle 2 | ✅ Pass | No LLM judgment in any numeric dimension |
| 7 | Synthetic data only | Security / FR-015 | ✅ Pass | No new datasets |
| 8 | No PII, no real financial identifiers | Security | ✅ Pass | Scorecard contains aggregated metrics only |
| 9 | No GPU dependencies | Explicit Prohibitions | ✅ Pass | stdlib only |
| 10 | No `--contracted-only` flag | Amendment A4 | ✅ Pass | All 60 tasks are the deliverable |
| 11 | Timestamped output folders — no overwriting | FR-010 | ✅ Pass | Each run creates `outputs/[YYYY-MM-DD_HH-MM]/` |
| 12 | Raw Metrics section included | Amendment A4 | ✅ Pass | 6th section in every scorecard |
| 13 | JSON output produced alongside markdown | FR-010 | ✅ Pass | `.json` and `.md` written per run |
| 14 | Client referred to as "Banking Institution" only | Security | ✅ Pass | No client name in any output |
| 15 | Critic placeholders present in scorecard | FR-008/009 | ✅ Pass | `<!-- CRITIC:... -->` written for every task × model × section |

**All 15 items pass.**

---

## Project Structure

```
sql-skill/scripts/run_eval.py        # Produces sql_scorecard_[tag].md + .json
python-skill/scripts/run_eval.py     # Produces python_scorecard_[tag].md + .json

assets/
├── task_bank.csv                    # Read by both run_eval.py scripts
└── eval_results.csv                 # Single source of truth for all metrics

outputs/
└── [YYYY-MM-DD_HH-MM]/
    ├── sql_scorecard_all.md
    ├── sql_scorecard_all.json
    ├── sql_scorecard_[task_id].md
    ├── sql_scorecard_[task_id].json
    ├── python_scorecard_all.md
    ├── python_scorecard_all.json
    ├── python_scorecard_[task_id].md
    └── python_scorecard_[task_id].json
```

### Scorecard Section Order

```markdown
# SQL Evaluation Scorecard

[scope] | 3 models | Baseline reference: ChatGPT 5.2 Codex

## Summary — Mean Scores          ← omitted for single-task runs
## Delta vs Baseline              ← omitted for single-task runs
## Quantitative Assessment        ← per-task tables with ✓/✗ reliability ticks
## Critic Review                  ← <!-- CRITIC:... --> placeholders
---
## Metric Key                     ← scoring formula reference
---
## Raw Metrics                    ← runtime, tokens, memory per model per task
```

---

## Key Design Decisions

| Decision | What Was Chosen | Why |
|:---------|:----------------|:----|
| Scorecard integrated into `run_eval.py` | No separate `scorecard` CLI | V1 scope doesn't require cross-skill aggregation — SQL and Python are evaluated independently |
| Two independent scorecards | SQL and Python produce separate outputs | Cleaner separation; client can evaluate SQL and Python independently |
| Raw Metrics as 6th section | Added at client request | Surfaces actual token usage, runtime, and memory directly — supports deeper analysis |
| JSON output alongside markdown | Both `.md` and `.json` per run | `.md` for human reading; `.json` for programmatic access or custom reporting |
| Timestamped folders | `outputs/[YYYY-MM-DD_HH-MM]/` | Full run history preserved; no overwriting |
| Delta vs ChatGPT baseline | Model `b` as reference point | ChatGPT 5.2 Codex is the most widely adopted baseline in the client's context |

---

## Complexity Tracking

| Item | Resolution |
|:-----|:-----------|
| No cross-skill aggregation in V1 | SQL and Python produce independent scorecards. A unified cross-skill scorecard is a Phase 2 feature if needed. |
| Raw Metrics sourced from `performance_detail` | `run_eval.py` already computes `performance_detail` dict during scoring — Raw Metrics table reads from this dict plus the `clean` variant row in `eval_results.csv`. No second pass needed. |
| Critic placeholders vs. live Critic invocation | Placeholders are the V1 approach — works with any AI platform without API coupling. Live invocation is a potential Phase 2 enhancement. |
