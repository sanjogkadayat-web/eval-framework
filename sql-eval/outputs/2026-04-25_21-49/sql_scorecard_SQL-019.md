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
- **Claude Sonnet 4.5:** Correctly implements 7-day moving average using ROWS BETWEEN 6 PRECEDING AND CURRENT ROW with proper PARTITION BY account_id and ORDER BY balance_date. Includes explicit NULL filtering to prevent invalid values from affecting window calculations.
- **ChatGPT 5.2 Codex:** Correctly applies window function with appropriate frame specification (6 preceding rows plus current) and proper partitioning by account_id. Uses parameterized variant placeholder for dataset flexibility.
- **Gemini 2.5 Flash:** Implements correct window frame semantics with AVG() OVER and proper ordering within partitions. Maintains template-based approach for variant substitution and produces clean, logical column output structure.

**Failures**
- **Claude Sonnet 4.5:** Schema fragility — hardcodes 'synthetic_clean_daily_balances' instead of using the <variant> placeholder, preventing correct execution against null_heavy, duplicate_heavy, medium, and large datasets.
- **ChatGPT 5.2 Codex:** Null handling — missing WHERE clause to filter NULL values in account_id or closing_balance, causing the null_heavy variant to fail consensus (18.75/25 reliability score). Formatting inconsistency with mixed indentation patterns.
- **Gemini 2.5 Flash:** None identified.

**Mitigation Strategies**
- **Claude Sonnet 4.5:** Replace hardcoded table name with 'synthetic_<variant>_daily_balances' to enable parameterized variant switching while retaining the defensive NULL filtering.
- **ChatGPT 5.2 Codex:** Add WHERE clause: WHERE account_id IS NOT NULL AND closing_balance IS NOT NULL before ORDER BY to exclude rows that would skew window calculations. Standardize indentation to 2 or 4 spaces consistently.
- **Gemini 2.5 Flash:** N/A

**Observations**
- **Claude Sonnet 4.5:** Clean, readable structure with consistent 4-space indentation and well-aligned clauses. Defensive WHERE clause demonstrates production-grade awareness of data quality issues, though at the cost of parameterization flexibility.
- **ChatGPT 5.2 Codex:** Compact layout with minimal vertical spacing. The OVER clause formatting is adequate but mixes 2-space indentation in the window spec with inconsistent alignment elsewhere, reducing maintainability.
- **Gemini 2.5 Flash:** Excellent vertical formatting with each major clause on its own line, enhancing scanability. Multi-line ORDER BY within the OVER clause improves clarity for complex window definitions, though verbose for this simple case.

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
