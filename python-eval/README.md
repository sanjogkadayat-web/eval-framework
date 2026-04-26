# Python Evaluation Skill

Benchmarks AI-generated Python code from Claude Sonnet 4.5, ChatGPT 5.2 Codex, and Gemini 2.5 Flash across 30 realistic analytics engineering tasks and returns a decision-ready scorecard.

## Overview

This skill evaluates model-generated Python pipelines across ingestion, validation, transformation, feature engineering, and aggregation tasks. It scores correctness via pytest, formatting via flake8, performance via runtime and memory, and reliability across five dataset variants. A Python Critic persona automatically reviews anonymized model code and produces structured qualitative commentary. All scoring is deterministic — the same prompt always produces the same numeric scores.

## Prerequisites

- Python 3.10+
- Claude.ai account (Pro, Max, Team, or Enterprise)
- **Code Execution and File Creation** enabled in Settings > Capabilities

## Installation

1. Go to **Settings > Capabilities** and ensure **Code Execution and File Creation** is turned on.
2. Go to **Settings > Customize > Skills**.
3. Click **"+"** then **"+ Create skill"**.
4. Upload **python-eval.zip**.
   > The ZIP must contain the `python-eval/` folder at root — not loose files.
5. Open a new chat — the skill activates automatically.

## Usage

### Evaluate a single task

Ask Claude a plain English question describing the analytics task:

```
Evaluate how well each model builds a functional ETL pipeline that loads accounts, validates schema, filters active rows, and saves output
```

Or provide a task ID directly:

```
Run the Python evaluation for PY-011
```

### Evaluate all tasks

```
Run the full Python evaluation and produce a scorecard
```

Scorecard outputs are written to a timestamped folder under `outputs/`. Each run creates a new folder — previous runs are never overwritten.

## Output

```
outputs/[YYYY-MM-DD_HH-MM]/
├── python_scorecard_all.md
├── python_scorecard_all.json
├── python_scorecard_PY-011.md      ← single task run
└── python_scorecard_PY-011.json
```

Every scorecard contains six sections: Summary Table, Delta vs Baseline, Quantitative Assessment, Critic Review, Metric Key, and Raw Metrics.

## Scoring

Four dimensions, 25 points each. Maximum score: 100.

| Dimension | Points | What It Measures |
|:----------|:------:|:-----------------|
| Correctness | 25 | All pytest tests pass on clean variant. |
| Formatting | 25 | flake8 / PEP 8 violations. |
| Performance | 25 | 10-band percentile scoring on runtime, memory, and tokens. |
| Reliability | 25 | Pass rate across null-heavy, duplicate-heavy, medium, and large variants. Only scored if correctness passes. |

## Companion Skill

This framework includes a separate **SQL Evaluation Skill** (`sql-eval.zip`) that benchmarks the same three models across 30 SQL analytics tasks. Install it the same way — upload `sql-eval.zip` as a second skill.
