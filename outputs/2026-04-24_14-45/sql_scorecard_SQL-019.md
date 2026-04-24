# SQL Evaluation Scorecard

Task: Compute a 7-day moving average of closing_balance per account. | 3 models | Baseline reference: ChatGPT 5.2 Codex


## Quantitative Assessment

---

### Compute a 7-day moving average of closing_balance per account. (Medium)

| Model | Correctness /25 | Formatting /25 | Performance /25 ↑ | Reliability /25 | Total /100 | Δ Total |
|---|---|---|---|---|---|---|
| Claude Sonnet 4.5 | 25.0 | 25.0 | 10.0 | 25.0 `✓ ✓ ✓ ✓` | 85.0 | +17.64 |
| ChatGPT 5.2 Codex *(baseline)* | 25.0 | 11.11 | 12.5 | 18.75 `✗ ✓ ✓ ✓` | 67.36 | — |
| Gemini 2.5 Flash | 25.0 | 20.59 | 10.0 | 25.0 `✓ ✓ ✓ ✓` | 80.59 | +13.23 |

---

## Critic Review

### Compute a 7-day moving average of closing_balance per account.

**Strengths**
- **Claude Sonnet 4.5:** Correctly implements the 7-day moving average using `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` with proper partitioning by account_id and ordering by balance_date. Includes defensive null filtering to prevent null values from skewing the window calculation.
- **ChatGPT 5.2 Codex:** Properly structured window function with accurate partitioning and ordering logic, using the standard `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` frame specification to capture exactly 7 rows per window.
- **Gemini 2.5 Flash:** Implements the window function with correct syntax including proper partitioning by account_id, ordering by balance_date, and appropriate ROWS BETWEEN frame specification for the 7-day window.

**Failures**
- **Claude Sonnet 4.5:** None identified.
- **ChatGPT 5.2 Codex:** Missing edge case — null handling is absent, allowing null values in account_id or closing_balance to pass through unfiltered, which could produce incomplete or incorrect moving averages when nulls are present in the window frame.
- **Gemini 2.5 Flash:** Schema fragility — syntax error on line 13 with `ORDER BY balance_date ROWS BETWEEN` missing newline, causing the ROWS clause to run into the ORDER BY incorrectly.

**Mitigation Strategies**
- **Claude Sonnet 4.5:** N/A
- **ChatGPT 5.2 Codex:** Add explicit WHERE clause to filter out rows where `account_id IS NOT NULL AND closing_balance IS NOT NULL` before computing the window function.
- **Gemini 2.5 Flash:** Add line break after `balance_date` on line 13 to separate the ORDER BY clause from the ROWS BETWEEN frame specification.

**Observations**
- **Claude Sonnet 4.5:** Clean, production-ready code with consistent indentation and defensive null handling. The explicit WHERE filter demonstrates awareness of data quality concerns typical in financial datasets.
- **ChatGPT 5.2 Codex:** Uses template placeholder `synthetic_<variant>_daily_balances` instead of hardcoded table name, showing intent for reusability across dataset variants. However, indentation is slightly inconsistent between the SELECT and FROM clauses.
- **Gemini 2.5 Flash:** Overly verbose formatting with unnecessary line breaks within the window function specification, reducing readability. The ORDER BY clause placement creates ambiguity about whether the sort applies to the window or the result set.

---

## Metric Key

- **Correctness /25** — Row count majority consensus on clean variant → 25 pts if matches, else 0.
- **Formatting /25** — Mean `formatting_pass_pct` across 5 variants via sqlfluff (ANSI), scaled 0–25.
- **Performance /25 ↑** — Mean of 2 sub-scores (runtime, tokens), each banded into 10 percentile brackets: top 10% = 25, bottom 10% = 2.5. Higher is better. No baseline dependency.
- **Reliability /25** — Pass rate across 4 stress variants (null_heavy, duplicate_heavy, medium, large) × 25. Only scored if clean correctness passes. Ticks show null_heavy / duplicate_heavy / medium / large.
- **Δ Total** — vs ChatGPT 5.2 Codex. Positive = better, negative = worse.

---

## Raw Metrics

| Model | Task | Runtime (ms) | Input Tokens | Output Tokens |
|:------|:-----|-------------:|-------------:|--------------:|
| Claude Sonnet 4.5 | SQL-019 | 18 | 16 | 138 |
| ChatGPT 5.2 Codex | SQL-019 | 8 | 10 | 130 |
| Gemini 2.5 Flash | SQL-019 | 127 | 1 | 138 |
