---
name: sql-eval
description: >
  Evaluates AI-generated SQL code and produces a comparative scorecard for
  Claude Sonnet 4.5, ChatGPT 5.2 Codex, and Gemini 2.5 Flash across four
  dimensions: correctness, formatting, performance, and reliability (25 pts
  each, 100 total). When a user describes a SQL task in natural language,
  match their description against the prompt column in assets/task_bank.csv
  to find the closest task, then run scripts/run_eval.py with that
  task ID. If the user provides a task ID directly (e.g. SQL-001), use it
  as-is. After scoring, complete the Critic Review using the persona at
  assets/personas/sql_critic_persona.md. Scores are based on
  pre-recorded evaluation data against synthetic banking datasets (accounts,
  transactions, daily_balances) — live dataset evaluation is not supported.
  Use this skill whenever a user asks to evaluate, score, benchmark, or
  compare SQL query quality across the three models.
---

# SQL Evaluation Skill

Evaluates model-generated SQL code for a Banking Institution analytics
engineering benchmark. Operates exclusively over pre-recorded data —
no SQL engine is invoked at runtime.

## Step 1 — Run the Quantitative Scoring Script

Run this from the skill root to generate all numeric scores:

```bash
# Score all tasks
python scripts/run_eval.py

# Score a single task
python scripts/run_eval.py --task-id SQL-001
```

This reads `assets/task_bank.csv` and `assets/eval_results.csv` and writes:

| Output | Description |
|---|---|
| `outputs/[timestamp]/sql_scorecard_[task_id or all].json` | Machine-readable — aggregates + one record per task × model |
| `outputs/[timestamp]/sql_scorecard_[task_id or all].md` | Human-readable — summary table, delta table, Quantitative Assessment scores, Critic placeholders, Raw Metrics |

## Step 2 — Complete the Critic Review

After the script runs, the scorecard markdown contains a **Critic Review**
section with one structured block per task, headed by the task prompt. Each block has four sections
(Strengths, Failures, Mitigation Strategies, Observations), each with one
bullet per model.

**Fill in every `<!-- CRITIC:... -->` placeholder immediately** by:

1. Reading the persona at `assets/personas/sql_critic_persona.md`
2. Looking up the task ID in `assets/task_bank.csv` by matching the prompt heading, then loading the three SQL files from `assets/tasks/[task_id]/`
3. Writing one concise bullet per model (1–3 sentences) for each section

### Critic Review format (per task)

**Strengths**
- **Claude Sonnet 4.5:** what this model's SQL handles correctly
- **ChatGPT 5.2 Codex:** what this model's SQL handles correctly
- **Gemini 2.5 Flash:** what this model's SQL handles correctly

**Failures**
- **Claude Sonnet 4.5:** concrete problems (null handling / deduplication gap / logic error / schema fragility / performance issue / missing edge case). "None identified." if clean.
- **ChatGPT 5.2 Codex:** same
- **Gemini 2.5 Flash:** same

**Mitigation Strategies**
- **Claude Sonnet 4.5:** one fix per failure. "N/A" if no failures.
- **ChatGPT 5.2 Codex:** same
- **Gemini 2.5 Flash:** same

**Observations**
- **Claude Sonnet 4.5:** style, readability, maintainability notes
- **ChatGPT 5.2 Codex:** same
- **Gemini 2.5 Flash:** same

### Rules
- No numeric scores
- No extra sections or changed headings
- Review each model independently — no cross-model comparisons within a bullet
- Do not reproduce the SQL code

## Scoring Reference

All numeric scores are derived deterministically from `eval_results.csv`.
No AI judgment is used in any numeric dimension.

### Correctness (25 pts)
Row count majority consensus across all 3 models on the clean variant.
A model passes (25 pts) when its row count matches the majority. Fails = 0.

### Formatting (25 pts)
Mean `formatting_pass_pct` across all 5 variants, pre-recorded via
sqlfluff (ANSI dialect), scaled 0–25.

### Performance (25 pts) ↑ higher is better
Two sub-scores averaged: runtime and tokens. Each scored using 10-band
percentile brackets derived from the full dataset distribution.
Top 10% of observed values = 25. Bottom 10% = 2.5. No baseline dependency.

### Reliability (25 pts)
Row count consensus pass rate across 4 non-clean variants
(null_heavy, duplicate_heavy, medium, large) × 25.
Only scored for tasks that pass the clean correctness gate.

### Delta (Δ)
All deltas are vs ChatGPT 5.2 Codex. Positive = better. Negative = worse.

## Inputs

| File | Path |
|---|---|
| Task bank | `assets/task_bank.csv` |
| Evaluation results | `assets/eval_results.csv` |
| Task code files | `assets/tasks/[task_id]/task{N}[a\|b\|c].sql` |
| SQL Critic persona | `assets/personas/sql_critic_persona.md` |

## Guardrails

- No SQL engine is invoked at runtime — all metrics are pre-recorded
- sqlfluff is a dataset preparation tool only — not invoked at runtime
- Model identity is anonymised throughout: filename letters a/b/c only
- All datasets are synthetic — labeled `synthetic_` in filename and header
- Flat files only — no database, no external API calls
