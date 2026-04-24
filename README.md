# AI Model Evaluation Framework

A Claude-native skill that benchmarks AI coding assistants across SQL and Python analytics tasks and returns a decision-ready scorecard.

## Overview

This framework evaluates Claude Sonnet 4.5, ChatGPT 5.2 Codex, and Gemini 2.5 Flash across 60 realistic analytics engineering tasks — 30 SQL and 30 Python. It scores each model across four dimensions (correctness, formatting, performance, and reliability) and produces a structured qualitative Critic review, giving analytics teams an objective, reproducible benchmark before committing to an AI coding assistant for production workflows.

The framework is packaged as two Claude Agent Skills and activates automatically from a plain English prompt — no configuration, no manual steps.

## Features

- **SQL Skill:** Evaluates model-generated SQL across filters, joins, CTEs, window functions, deduplication, and incremental load patterns. Scores correctness via row count consensus, formatting via sqlfluff, performance via runtime and token usage, and reliability across five dataset variants.
- **Python Skill:** Evaluates model-generated Python pipelines across ingestion, validation, transformation, feature engineering, and aggregation tasks. Scores correctness via pytest, formatting via flake8, performance via runtime and memory, and reliability across five dataset variants.
- **AI Critic Review:** A SQL Critic and Python Critic persona automatically review anonymized model code after every evaluation run, producing structured qualitative commentary across four sections: Strengths, Failures, Mitigation Strategies, and Observations.
- **Comparative Scorecard:** A single unified output covering all three models with numeric scores, delta vs the ChatGPT baseline, per-task breakdown, Critic review, and raw quantitative metrics — saved as both markdown and JSON per run.
- **Fully Deterministic:** All numeric scoring is derived from pre-recorded metrics. The same prompt always produces the same scores.

## Prerequisites

- Python 3.10+
- Claude.ai account (Pro, Max, Team, or Enterprise)
- **Code Execution and File Creation** enabled in Settings > Capabilities

## Installation

### Option 1 — Upload to Claude (Recommended)

1. Go to **Settings > Capabilities** and ensure **Code Execution and File Creation** is turned on.
2. Go to **Settings > Customize > Skills**.
3. Click **"+"** then **"+ Create skill"**.
4. Upload **eval_framework.zip**.
   > The ZIP must contain the `eval_framework/` folder at root — not loose files.
5. Toggle both the SQL Skill and Python Skill on.
6. Open a new chat — the skills activate automatically.

### Option 2 — Clone the Repository

For contributors or teams running the framework locally in Cursor or Copilot:

```bash
# Clone the repository
git clone https://github.com/sanjogkadayat-web/eval-framework
cd eval-framework

# Install dependencies
pip install -r requirements.txt
```

To update to the latest version:

```bash
git pull origin main
pip install -r requirements.txt
```

Then re-package and re-upload the zip to Claude if needed.

## Usage

### Evaluate a single task

Ask Claude a plain English question describing the analytics task:

```
Evaluate how well each model computes a 7-day moving average of closing balance per account
```

```
Evaluate how well each model builds a functional ETL pipeline that loads accounts, validates schema, filters active rows, and saves output
```

### Evaluate all tasks

```
Run the full SQL evaluation and produce a scorecard
```

```
Run the full Python evaluation and produce a scorecard
```

Scorecard outputs are written to a timestamped folder under `outputs/`. Each run creates a new folder — previous runs are never overwritten.

## Output

```
outputs/[YYYY-MM-DD_HH-MM]/
├── sql_scorecard_all.md
├── sql_scorecard_all.json
├── sql_scorecard_SQL-019.md      ← single task run
├── sql_scorecard_SQL-019.json
├── python_scorecard_all.md
├── python_scorecard_all.json
├── python_scorecard_PY-011.md
└── python_scorecard_PY-011.json
```

Every scorecard contains six sections: Summary Table, Delta vs Baseline, Quantitative Assessment, Critic Review, Metric Key, and Raw Metrics.

## Project Structure

```
eval_framework/
├── README.md
├── requirements.txt
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
└── outputs/
```

## Scoring

Four dimensions, 25 points each. Maximum score: 100.

| Dimension | Points | What It Measures |
|:----------|:------:|:-----------------|
| Correctness | 25 | SQL: row count majority consensus on clean variant. Python: all pytest tests pass on clean variant. |
| Formatting | 25 | SQL: sqlfluff violations. Python: flake8 / PEP 8 violations. |
| Performance | 25 | 10-band percentile scoring on runtime and tokens (SQL) or runtime, memory, and tokens (Python). |
| Reliability | 25 | Pass rate across null-heavy, duplicate-heavy, medium, and large variants. Only scored if correctness passes. |

Delta (Δ) values compare Claude Sonnet 4.5 and Gemini 2.5 Flash against the ChatGPT 5.2 Codex baseline. Positive = better. Negative = worse.

## Known Limitations

- Live dataset evaluation is not supported in V1 — all metrics are pre-recorded
- Gemini scores 0 on most Python correctness tasks (genuine model finding, not a bug)
- ChatGPT fails null-heavy reliability on 18/30 SQL tasks (genuine finding)
- Critic Review text may vary slightly between runs; numeric scores are fully deterministic

## Team

Built by Sanjog, Albina, and Jack — Team JAS, April 2026.
