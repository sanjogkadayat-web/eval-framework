# Python Evaluation Scorecard

Task: Compute a rolling average of closing_balance over the last 7 observations per account. | 3 models | Baseline reference: ChatGPT 5.2 Codex


## Quantitative Assessment

---

### Compute a rolling average of closing_balance over the last 7 observations per account. (Medium)

| Model | Correctness /25 | Formatting /25 | Performance /25 ↑ | Reliability /25 | Total /100 | Δ Total |
|---|---|---|---|---|---|---|
| Claude Sonnet 4.5 | 25.0 | 6.82 | 21.67 | 25.0 `✓ ✓ ✓ ✓` | 78.48 | -1.0 |
| ChatGPT 5.2 Codex *(baseline)* | 25.0 | 21.16 | 8.33 | 25.0 `✓ ✓ ✓ ✓` | 79.49 | — |
| Gemini 2.5 Flash | 0.0 | 17.0 | 10.0 | 0.0 | 27.0 | -52.49 |

---

## Critic Review

### Compute a rolling average of closing_balance over the last 7 observations per account.

**Strengths**
- **Claude Sonnet 4.5:** Uses `pd.read_csv(..., comment='#')` to skip the synthetic header comment declaratively, sorts by `(account_id, balance_date)` before rolling, and applies `groupby().transform(lambda x: x.rolling(window=7, min_periods=1).mean())` — which returns an index-aligned Series so the assignment to `rolling_avg_7` is safe on the sorted frame. Passes all four stress variants, confirming the logic holds under null and duplicate-heavy conditions.
- **ChatGPT 5.2 Codex:** Robust schema handling — `pd.to_datetime(..., errors="coerce")` and `pd.to_numeric(..., errors="coerce")` defend against malformed strings in the null_heavy variant. The `sort_values(..., kind="stable")` preserves insertion order among ties (useful for the duplicate-heavy variant), and the `groupby().rolling().reset_index(level=0, drop=True)` pattern is the idiomatic way to realign the multi-indexed rolling output back to the original frame. Passes all 5 variants.
- **Gemini 2.5 Flash:** Clean docstring and comments clearly label each step; sort, groupby, and rolling are all structurally in the right place; uses `skiprows=1` to strip the synthetic header row.

**Failures**
- **Claude Sonnet 4.5:** Unsafe pandas pattern — no `errors="coerce"` on `pd.to_datetime`, so any malformed `balance_date` string will raise rather than produce NaT; null handling is partial. Deduplication gap — duplicates in the duplicate_heavy variant are silently folded into the rolling window, inflating the denominator on repeated dates even though tests still pass row-count checks.
- **ChatGPT 5.2 Codex:** Deduplication gap — duplicate `(account_id, balance_date)` rows are kept in the rolling window, so the 7-observation average can be skewed by repeat rows in the duplicate_heavy variant. Missing edge case — uses "last 7 observations" semantics rather than a true 7-calendar-day time window, which diverges when dates are sparse.
- **Gemini 2.5 Flash:** Logic error / correctness failure — fails the clean-variant pytest gate, which cascades into a zero reliability score under the scoring rules. Unsafe pandas pattern — calls `pd.to_datetime` and `pd.to_numeric` without `errors="coerce"`, so any unparseable value raises instead of being coerced to NaT/NaN, making the function brittle on null_heavy. Test coverage gap — no defensive handling of duplicate rows for the duplicate_heavy variant.

**Mitigation Strategies**
- **Claude Sonnet 4.5:** Add `errors="coerce"` to `pd.to_datetime` and an explicit `pd.to_numeric(df['closing_balance'], errors='coerce')`; drop exact duplicates on `(account_id, balance_date)` before rolling (e.g. `df = df.drop_duplicates(subset=['account_id', 'balance_date'], keep='last')`).
- **ChatGPT 5.2 Codex:** Insert a `drop_duplicates(subset=['account_id', 'balance_date'], keep='last')` ahead of the rolling call to neutralise duplicate-heavy data; if true calendar-day semantics are required, switch to `.rolling('7D', on='balance_date')` after setting a datetime index per group.
- **Gemini 2.5 Flash:** Add `errors="coerce"` to both `pd.to_datetime` and `pd.to_numeric` to harden the clean-variant test (the current strict parsing is the most likely root cause of the correctness failure), then mirror Claude's dedup fix; re-run the test suite to confirm parity before shipping.

**Observations**
- **Claude Sonnet 4.5:** The `transform(lambda ...)` pattern is clean and produces an index-aligned Series so the assignment is unambiguous, but the lambda closure is a known pandas performance anti-pattern on large frames — the preferred `groupby(...).rolling(...)` + `reset_index` idiom avoids a Python-level callback per group. Low flake8 compliance (trailing whitespace / blank-line inconsistencies in the body) drags formatting down despite the logic being sound.
- **ChatGPT 5.2 Codex:** Idiomatic, defensive, and readable — type annotations on the signature, explicit coercion, stable sort, and the canonical `reset_index(level=0, drop=True)` realignment. This is the most production-ready of the three; the main maintainability improvement would be an inline comment explaining why `reset_index` is needed.
- **Gemini 2.5 Flash:** Overall structure mirrors a standard rolling pipeline, but one very long single-line rolling expression hurts readability and the absence of `errors="coerce"` signals a fragility the author did not consider. Docstring is good, but the code needs defensive I/O to survive the stress variants.

---

## Metric Key

- **Correctness /25** — `pytest_pass_pct = 100` on clean variant → 25 pts, else 0.
- **Formatting /25** — Mean `formatting_pass_pct` across 5 variants via flake8 (PEP 8), scaled 0–25.
- **Performance /25 ↑** — Mean of 3 sub-scores (runtime, memory, tokens), each banded into 10 percentile brackets: top 10% = 25, bottom 10% = 2.5. Higher is better. No baseline dependency.
- **Reliability /25** — Pass rate across 4 stress variants (null_heavy, duplicate_heavy, medium, large) × 25. Only scored if clean correctness passes. Ticks show null_heavy / duplicate_heavy / medium / large.
- **Δ Total** — vs ChatGPT 5.2 Codex. Positive = better, negative = worse.
