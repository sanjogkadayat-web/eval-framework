# Python Evaluation Scorecard

Task: Write a functional ETL pipeline that loads accounts, validates schema, filters active rows, and saves output. | 3 models | Baseline reference: ChatGPT 5.2 Codex


## Quantitative Assessment

---

### Write a functional ETL pipeline that loads accounts, validates schema, filters active rows, and saves output. (Medium)

| Model | Correctness /25 | Formatting /25 | Performance /25 ↑ | Reliability /25 | Total /100 | Δ Total |
|---|---|---|---|---|---|---|
| Claude Sonnet 4.5 | 25.0 | 9.62 | 20.0 | 25.0 `✓ ✓ ✓ ✓` | 79.62 | -6.58 |
| ChatGPT 5.2 Codex *(baseline)* | 25.0 | 22.86 | 13.33 | 25.0 `✓ ✓ ✓ ✓` | 86.19 | — |
| Gemini 2.5 Flash | 0.0 | 17.86 | 16.67 | 0.0 | 34.52 | -51.67 |

---

## Critic Review

### Write a functional ETL pipeline that loads accounts, validates schema, filters active rows, and saves output.

**Strengths**
- **Claude Sonnet 4.5:** Clean, minimal ETL pipeline with proper schema validation using assertion, correct pandas filtering with `.copy()` to avoid SettingWithCopyWarning, and flexible output path handling with directory creation.
- **ChatGPT 5.2 Codex:** Robust schema validation with explicit missing column check, proper date parsing with `pd.to_datetime()` for type safety, and uses list comprehension for validation logic making it concise and Pythonic.
- **Gemini 2.5 Flash:** Comprehensive ETL structure with try-except blocks around file operations, detailed logging at each pipeline stage, and explicit dtype validation against expected schema dictionary providing strong type enforcement.

**Failures**
- **Claude Sonnet 4.5:** Schema fragility — uses `comment='#'` to handle synthetic header but assertion compares exact list equality which is brittle to column ordering changes.
- **ChatGPT 5.2 Codex:** Missing edge case — hardcodes output path instead of accepting it as a parameter, breaking the expected function signature and failing tests that pass an `output_path` argument.
- **Gemini 2.5 Flash:** Logic error — attempts to convert `account_open_date` to datetime64 using `.astype()` on a string column without parsing, causing dtype conversion failure and zero correctness score.

**Mitigation Strategies**
- **Claude Sonnet 4.5:** Replace list equality check with set comparison: `assert set(df.columns) == set(expected_columns)` to allow flexible column ordering while maintaining validation.
- **ChatGPT 5.2 Codex:** Add `output_path=None` parameter to function signature and conditionally save only when provided, matching the expected test interface.
- **Gemini 2.5 Flash:** Replace `.astype("datetime64[ns]")` with `pd.to_datetime(accounts_df[col])` to properly parse date strings before dtype conversion.

**Observations**
- **Claude Sonnet 4.5:** Lightweight implementation prioritizing simplicity over verbosity, but lacks logging or error handling for production observability. The `.copy()` usage shows pandas best practice awareness.
- **ChatGPT 5.2 Codex:** Balanced approach with type hints, explicit validation, and logging setup, though logger is declared but minimally used. The `skiprows=1` correctly handles synthetic header row.
- **Gemini 2.5 Flash:** Over-engineered for the task scope with excessive try-except blocks and f-string logging that may impact performance. The schema validation logic is more complex than necessary but demonstrates defensive programming style.

---

## Metric Key

- **Correctness /25** — `pytest_pass_pct = 100` on clean variant → 25 pts, else 0.
- **Formatting /25** — Mean `formatting_pass_pct` across 5 variants via flake8 (PEP 8), scaled 0–25.
- **Performance /25 ↑** — Mean of 3 sub-scores (runtime, memory, tokens), each banded into 10 percentile brackets: top 10% = 25, bottom 10% = 2.5. Higher is better. No baseline dependency.
- **Reliability /25** — Pass rate across 4 stress variants (null_heavy, duplicate_heavy, medium, large) × 25. Only scored if clean correctness passes. Ticks show null_heavy / duplicate_heavy / medium / large.
- **Δ Total** — vs ChatGPT 5.2 Codex. Positive = better, negative = worse.

---

## Raw Metrics

| Model | Task | Runtime (ms) | Peak Memory (bytes) | Input Tokens | Output Tokens |
|:------|:-----|-------------:|--------------------:|-------------:|--------------:|
| Claude Sonnet 4.5 | PY-011 | 0 | 6097 | 22 | 232 |
| ChatGPT 5.2 Codex | PY-011 | 7 | 393300 | 17 | 263 |
| Gemini 2.5 Flash | PY-011 | 5 | 450279 | 1 | 229 |
