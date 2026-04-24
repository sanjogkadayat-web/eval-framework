---
name: python-eval
description: >
  Evaluates AI-generated Python code and produces a comparative scorecard for
  Claude Sonnet 4.5, ChatGPT 5.2 Codex, and Gemini 2.5 Flash across four
  dimensions: correctness, formatting, performance, and reliability (25 pts
  each, 100 total). When a user describes a Python task in natural language,
  match their description against the prompt column in assets/task_bank.csv
  to find the closest task, then run python-skill/scripts/run_eval.py with
  that task ID. If the user provides a task ID directly (e.g. PY-001), use
  it as-is. After scoring, complete the Critic Review using the persona at
  python-skill/assets/personas/python_critic_persona.md. Scores are based on
  pre-recorded evaluation data against synthetic banking datasets (accounts,
  transactions, daily_balances) — live dataset evaluation is not supported.
  Use this skill whenever a user asks to evaluate, score, benchmark, or
  compare Python code quality across the three models.
---

# Python Evaluation Skill

Evaluates model-generated Python code for a Banking Institution analytics
engineering benchmark. Operates exclusively over pre-recorded data —
no model-generated Python code is executed at runtime.

## Step 1 — Run the Quantitative Scoring Script

Run this from the repo root to generate all numeric scores:

```bash
# Score all tasks
python python-skill/scripts/run_eval.py

# Score a single task
python python-skill/scripts/run_eval.py --task-id PY-001
```

This reads `assets/task_bank.csv` and `assets/eval_results.csv` and writes:

| Output | Description |
|---|---|
| `outputs/[timestamp]/python_scorecard_[task_id or all].json` | Machine-readable — aggregates + one record per task × model |
| `outputs/[timestamp]/python_scorecard_[task_id or all].md` | Human-readable — summary table, delta table, Quantitative Assessment scores, Critic placeholders, Raw Metrics |

## Step 2 — Complete the Critic Review

After the script runs, the scorecard markdown contains a **Critic Review**
section with one structured block per task, headed by the task prompt. Each block has four sections
(Strengths, Failures, Mitigation Strategies, Observations), each with one
bullet per model.

**Fill in every `<!-- CRITIC:... -->` placeholder immediately** by:

1. Reading the persona at `python-skill/assets/personas/python_critic_persona.md`
2. Looking up the task ID in `assets/task_bank.csv` by matching the prompt heading, then loading the three Python files from `assets/tasks/[task_id]/`
3. Writing one concise bullet per model (1–3 sentences) for each section

### Critic Review format (per task)

**Strengths**
- **Claude Sonnet 4.5:** what this model's code handles correctly
- **ChatGPT 5.2 Codex:** what this model's code handles correctly
- **Gemini 2.5 Flash:** what this model's code handles correctly

**Failures**
- **Claude Sonnet 4.5:** concrete problems (null handling / deduplication gap / logic error / schema fragility / unsafe pandas pattern / missing edge case / test coverage gap). "None identified." if clean.
- **ChatGPT 5.2 Codex:** same
- **Gemini 2.5 Flash:** same

**Mitigation Strategies**
- **Claude Sonnet 4.5:** one fix per failure. "N/A" if no failures.
- **ChatGPT 5.2 Codex:** same
- **Gemini 2.5 Flash:** same

**Observations**
- **Claude Sonnet 4.5:** style, pandas idioms, readability, maintainability notes
- **ChatGPT 5.2 Codex:** same
- **Gemini 2.5 Flash:** same

### Rules
- No numeric scores
- No extra sections or changed headings
- Review each model independently — no cross-model comparisons within a bullet
- Do not reproduce the Python code

## Scoring Reference

All numeric scores are derived deterministically from `eval_results.csv`.
No AI judgment is used in any numeric dimension.

### Correctness (25 pts)
`pytest_pass_pct = 100` on the clean variant → 25 pts. Otherwise 0.
The clean-pass gate must be satisfied before reliability is scored.

### Formatting (25 pts)
Mean `formatting_pass_pct` across all 5 variants, pre-recorded via
flake8 (PEP 8), scaled 0–25.

### Performance (25 pts) ↑ higher is better
Three sub-scores averaged: runtime, peak memory, and tokens. Each scored
using 10-band percentile brackets derived from the full dataset distribution.
Top 10% of observed values = 25. Bottom 10% = 2.5. No baseline dependency.

### Reliability (25 pts)
`pytest_pass_pct = 100` pass rate across 4 non-clean variants
(null_heavy, duplicate_heavy, medium, large) × 25.
Only scored for tasks that pass the clean correctness gate.

### Delta (Δ)
All deltas are vs ChatGPT 5.2 Codex. Positive = better. Negative = worse.

## Inputs

| File | Path |
|---|---|
| Task bank | `assets/task_bank.csv` |
| Evaluation results | `assets/eval_results.csv` |
| Task code files | `assets/tasks/[task_id]/task{N}[a\|b\|c].py` |
| Python Critic persona | `python-skill/assets/personas/python_critic_persona.md` |

## Guardrails

- No model-generated Python code is executed at runtime — all metrics are pre-recorded
- flake8 and tracemalloc are dataset preparation tools only — not invoked at runtime
- Model identity is anonymised throughout: filename letters a/b/c only
- All datasets are synthetic — labeled `synthetic_` in filename and header
- Flat files only — no database, no external API calls
