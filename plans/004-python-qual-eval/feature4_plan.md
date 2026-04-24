# Implementation Plan: Feature 4 — Python Critic Review

**Branch**: `004-python-qual-eval` | **Date**: 2026-04-08 | **Last Updated**: 2026-04-24 | **Status**: ✅ Complete (V1)

> **Amendment A4 — April 2026 (ratified):** No standalone `eval_qualitative` CLI — Critic Review is integrated directly into `run_eval.py` as placeholder generation. The AI fills in `<!-- CRITIC:... -->` placeholders at runtime using the persona file. No `critic_runner.py`, no `anonymizer.py`, no `artifact_store.py` — all scorecard writing is handled by `run_eval.py`. Scale revised to 30 Python tasks × 3 models = 90 Critic reviews max.

> **Amendment A3 — April 2026 (ratified):** Two-table design adopted. Critic input is the anonymized `.py` code file at `assets/tasks/[task_id]/task{N}{a|b|c}.py`. Formatting score read from `formatting_pass_pct` in `eval_results.csv`.

---

## Summary

Feature 4 implements the Python Critic persona review within the `python-skill/` Agent Skill. It is integrated into `run_eval.py` — Critic Review placeholders are written automatically at the end of every scorecard generation run.

After the quantitative scoring sections are written, `run_eval.py` appends a **Critic Review** section to the scorecard markdown. For each task, four sections are written — Strengths, Failures, Mitigation Strategies, Observations — with one placeholder bullet per model per section:

```
<!-- CRITIC:[task_id]:[letter]:[Section] -->
```

The AI running the skill (Claude, Cursor, or Copilot) fills in every placeholder by:

1. Reading the persona at `python-skill/assets/personas/python_critic_persona.md`
2. Loading the three anonymized Python files from `assets/tasks/[task_id]/`
3. Writing one concise bullet per model (1–3 sentences) for each section

The Critic focuses on code quality aspects specific to Python analytics work: null handling, pandas idioms, schema validation, test coverage, deduplication logic, and maintainability. The Critic produces no numeric scores. No model identifier appears in the code files passed to the Critic — only the anonymized filename letter (`a`/`b`/`c`). Real model names appear only in the final formatted output using the `MODEL_NAMES` lookup.

The `formatting_pass_pct` score is pre-recorded in `eval_results.csv` and scored in the Quantitative Assessment section by `run_eval.py`. Feature 4 does not invoke flake8 — it focuses exclusively on qualitative Critic commentary.

---

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: stdlib only — no new dependencies beyond Feature 3
**Storage**: Critic placeholders written inline to the scorecard `.md` file. No separate Critic output file.
**Entry Point**: Integrated into `python-skill/scripts/run_eval.py` — no standalone CLI
**Target Platform**: Local development — no cloud, no Docker
**Constraints**:
- No numeric scoring by Critic
- No model identifiers in code files passed to Critic
- Critic output structure enforced via persona template
- No code execution at runtime
- No GPU dependencies

**Scale/Scope**: 30 Python tasks × 3 models = **90 Critic review bullets per section** (max, single-task run = 3 bullets per section)

---

## Constitution Check (V1)

| # | Rule | Source | Status | Notes |
|:--|:-----|:-------|:-------|:------|
| 1 | Python 3.10+ only | Tech Stack | ✅ Pass | No new dependencies |
| 2 | No web/API framework | Explicit Prohibitions | ✅ Pass | No external HTTP calls |
| 3 | Flat files only — no database | Explicit Prohibitions | ✅ Pass | Placeholders written to `.md` scorecard |
| 4 | No Docker / cloud / containerization | Explicit Prohibitions | ✅ Pass | Local execution only |
| 5 | Model anonymization before Critic | Principle 2 / Security | ✅ Pass | Critic receives anonymized `.py` files only. Real names never exposed in code content. |
| 6 | Critic produces no numeric score | Principle 2 / FR-009 | ✅ Pass | Enforced via persona template. Four sections are qualitative only. |
| 7 | No model identifiers in Critic input | Principle 2 / Security | ✅ Pass | Files identified by filename letter only. `python_critic_persona.md` contains no model identifiers. |
| 8 | No code execution at runtime | Principle 6 | ✅ Pass | No flake8 invocation. `formatting_pass_pct` is pre-recorded. |
| 9 | All numeric scoring deterministic | Principle 2 | ✅ Pass | Critic produces no numeric score. Formatting scores are pre-recorded. |
| 10 | Synthetic data only | Security / FR-015 | ✅ Pass | Datasets inherited from Feature 3 |
| 11 | No PII, no real financial identifiers | Security | ✅ Pass | No new datasets |
| 12 | No GPU dependencies | Explicit Prohibitions | ✅ Pass | stdlib only |
| 13 | Client referred to as "Banking Institution" only | Security | ✅ Pass | No client name in any output |
| 14 | Works with any AI platform | Skill Design | ✅ Pass | Placeholder pattern works with Claude, Cursor, and GitHub Copilot |
| 15 | Critic Review integrated into run_eval.py | Amendment A4 | ✅ Pass | No standalone CLI. No separate critic_runner.py. |

**All 15 items pass.**

---

## Project Structure

```
python-skill/
├── SKILL.md
├── scripts/
│   └── run_eval.py              # Writes Critic placeholders after Quantitative
│                                # Assessment section. Reads task prompt from
│                                # task_bank.csv. Writes one placeholder per
│                                # model per section per task.
└── assets/
    ├── tasks/
    │   └── [task_id]/
    │       ├── task{N}a.py      # Anonymized Python — Claude Sonnet 4.5
    │       ├── task{N}b.py      # Anonymized Python — ChatGPT 5.2 Codex
    │       └── task{N}c.py      # Anonymized Python — Gemini 2.5 Flash
    └── personas/
        └── python_critic_persona.md  # Manually authored. No model identifiers.
                                      # Enforces 4-section output structure.
                                      # Focuses on: null handling, pandas idioms,
                                      # schema validation, test coverage,
                                      # deduplication logic, maintainability.

outputs/
└── [YYYY-MM-DD_HH-MM]/
    ├── python_scorecard_[tag].md    # Contains Critic Review section with
    │                                # <!-- CRITIC:... --> placeholders
    └── python_scorecard_[tag].json
```

### Critic Placeholder Format

```
## Critic Review

### [Task prompt text]

**Strengths**
- **Claude Sonnet 4.5:** <!-- CRITIC:PY-011:a:Strengths -->
- **ChatGPT 5.2 Codex:** <!-- CRITIC:PY-011:b:Strengths -->
- **Gemini 2.5 Flash:** <!-- CRITIC:PY-011:c:Strengths -->

**Failures**
- **Claude Sonnet 4.5:** <!-- CRITIC:PY-011:a:Failures -->
...
```

---

## Key Design Decisions

| Decision | What Was Chosen | Why |
|:---------|:----------------|:----|
| Critic integrated into `run_eval.py` | Placeholder pattern written inline | No need for separate `critic_runner.py` or `eval_qualitative` CLI in V1 |
| Placeholder-based Critic | `<!-- CRITIC:... -->` HTML comments | AI fills in at runtime — works with any platform (Claude, Cursor, Copilot) |
| Python-specific persona | Separate from SQL Critic | Python reviews focus on pandas idioms, tracemalloc, pytest patterns — different from SQL style concerns |
| Grouped by section | All three models under each section heading | Cleaner client view vs 12 separate blocks per task |
| Task prompt as heading | Prompt text used as section heading | More readable than task IDs in client-facing output |
