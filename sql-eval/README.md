# SQL Evaluation Skill

Benchmarks AI-generated SQL code from Claude Sonnet 4.5, ChatGPT 5.2 Codex, and Gemini 2.5 Flash across 30 realistic analytics engineering tasks and returns a decision-ready scorecard.

## Overview

This skill evaluates model-generated SQL across filters, joins, CTEs, window functions, deduplication, and incremental load patterns. It scores correctness via row count consensus, formatting via sqlfluff, performance via runtime and token usage, and reliability across five dataset variants. A SQL Critic persona automatically reviews anonymized model code and produces structured qualitative commentary. All scoring is deterministic — the same prompt always produces the same numeric scores.

## Prerequisites

- Python 3.10+
- Claude.ai account (Pro, Max, Team, or Enterprise)
- **Code Execution and File Creation** enabled in Settings > Capabilities

## Installation

1. Go to **Settings > Capabilities** and ensure **Code Execution and File Creation** is turned on.
2. Go to **Settings > Customize > Skills**.
3. Click **"+"** then **"+ Create skill"**.
4. Upload **sql-eval.zip**.
   > The ZIP must contain the `sql-eval/` folder at root — not loose files.
5. Open a new chat — the skill activates automatically.

## Usage

### Evaluate a single task

Ask Claude a plain English question describing the analytics task:

```
Evaluate how well each model computes a 7-day moving average of closing balance per account
```

Or provide a task ID directly:

```
Run the SQL evaluation for SQL-019
```

### Evaluate all tasks

```
Run the full SQL evaluation and produce a scorecard
```

Scorecard outputs are written to a timestamped folder under `outputs/`. Each run creates a new folder — previous runs are never overwritten.

## Output

```
outputs/[YYYY-MM-DD_HH-MM]/
├── sql_scorecard_all.md
├── sql_scorecard_all.json
├── sql_scorecard_SQL-019.md      ← single task run
└── sql_scorecard_SQL-019.json
```

Every scorecard contains six sections: Summary Table, Delta vs Baseline, Quantitative Assessment, Critic Review, Metric Key, and Raw Metrics.

## Scoring

Four dimensions, 25 points each. Maximum score: 100.

| Dimension | Points | What It Measures |
|:----------|:------:|:-----------------|
| Correctness | 25 | Row count majority consensus on clean variant. |
| Formatting | 25 | sqlfluff violations (ANSI dialect). |
| Performance | 25 | 10-band percentile scoring on runtime and tokens. |
| Reliability | 25 | Pass rate across null-heavy, duplicate-heavy, medium, and large variants. Only scored if correctness passes. |

## Companion Skill

This framework includes a separate **Python Evaluation Skill** (`python-eval.zip`) that benchmarks the same three models across 30 Python analytics tasks. Install it the same way — upload `python-eval.zip` as a second skill.
