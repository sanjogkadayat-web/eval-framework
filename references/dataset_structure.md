# AI Evaluation Framework — Dataset Structure

> All datasets are synthetic. No real financial data, account numbers, routing numbers, transaction IDs, or customer identifiers appear anywhere in this document or in any bundled asset. The client is referred to as "Banking Institution" throughout.

---

## Contents

1. [Synthetic Tables — Schema Reference](#1-synthetic-tables--schema-reference)
2. [Table Relationships and Join Cardinality](#2-table-relationships-and-join-cardinality)
3. [Dataset Variants — Configurations and Row Counts](#3-dataset-variants--configurations-and-row-counts)
4. [Column-Level Data Type Constraints and Value Ranges](#4-column-level-data-type-constraints-and-value-ranges)
5. [Two-Table Answer Architecture](#5-two-table-answer-architecture)

---

## 1  Synthetic Tables — Schema Reference

Three core synthetic CSV files serve all 60 tasks across both SQL and Python evaluation. All files are prefixed `synthetic_` and carry a `SYNTHETIC` label in their file header. None contain real financial data.

---

### 1.1  synthetic_transactions.csv

**Role**: Core fact table. Used by most SQL and Python tasks as the primary dataset.

| Column              | Data Type | Nullable          | Key           | Description |
| ------------------- | --------- | ----------------- | ------------- | ----------- |
| `txn_id`            | STRING    | No                | PK            | Synthetic transaction identifier. Format: `SYNTHETIC_TXN_{zero-padded 6-digit integer}`. Unique per row across all variants. |
| `account_id`        | STRING    | Varies by variant | FK → accounts | Synthetic account identifier. Format: `SYNTHETIC_ACCT_{4-digit integer}`. `null_heavy` variant: ~25% nulls injected. Foreign key to `synthetic_accounts.account_id`. |
| `txn_date`          | DATE      | No                | —             | ISO 8601 format (`YYYY-MM-DD`). 24-month window ending on synthetic reference date 2024-12-31. |
| `txn_amount`        | FLOAT     | Varies by variant | —             | Transaction amount. Positive values only: `0.01` to `9999.99` in `clean`, `null_heavy`, `duplicate_heavy`, and `medium`. `large` variant: long-tail distribution up to `99999.99`. `null_heavy` variant: ~20% nulls injected. Two decimal places. |
| `txn_type`          | STRING    | No                | —             | Enum: `PURCHASE`, `REFUND`, `TRANSFER`, `FEE`. Uniform distribution across all four values. |
| `merchant_category` | STRING    | Varies by variant | —             | Enum: `RETAIL`, `GROCERY`, `TRAVEL`, `DINING`, `UTILITIES`, `HEALTHCARE`. `null_heavy` variant: ~15% nulls injected. |
| `channel`           | STRING    | No                | —             | Enum: `ONLINE`, `BRANCH`, `ATM`, `MOBILE`. Uniform distribution across all four values. |
| `is_flagged`        | BOOLEAN   | No                | —             | `true` or `false`. ~5% `true` in all variants. Used in anomaly detection tasks. |

---

### 1.2  synthetic_accounts.csv

**Role**: Dimension table. Used in JOIN tasks, GROUP BY tasks, and multi-table aggregation tasks.

| Column              | Data Type | Nullable | Key | Description |
| ------------------- | --------- | -------- | --- | ----------- |
| `account_id`        | STRING    | No       | PK  | Synthetic account identifier. Format: `SYNTHETIC_ACCT_{4-digit integer}`. Matches the FK in `synthetic_transactions.account_id`. Unique per row. |
| `customer_segment`  | STRING    | No       | —   | Enum: `RETAIL`, `SMALL_BIZ`, `WEALTH`, `STUDENT`. Uniform distribution. Used in GROUP BY and JOIN + aggregation tasks. |
| `account_open_date` | DATE      | No       | —   | ISO 8601 format (`YYYY-MM-DD`). Range: 5 years before synthetic reference date (2020-01-01 to 2024-12-31). |
| `account_status`    | STRING    | No       | —   | Enum: `ACTIVE`, `CLOSED`, `SUSPENDED`. Approximately 85% `ACTIVE`, 10% `CLOSED`, 5% `SUSPENDED`. |
| `region`            | STRING    | No       | —   | Enum: `NORTH`, `SOUTH`, `EAST`, `WEST`. Uniform distribution. Used in multi-level grouping and aggregation tasks. |

---

### 1.3  synthetic_daily_balances.csv

**Role**: Time-series table. Used in window function tasks, rolling average tasks, and running total tasks.

| Column            | Data Type | Nullable          | Key                                | Description |
| ----------------- | --------- | ----------------- | ---------------------------------- | ----------- |
| `account_id`      | STRING    | Varies by variant | Composite PK (with `balance_date`) | Synthetic account identifier. Matches `synthetic_accounts.account_id`. `null_heavy` variant: ~10% nulls injected. |
| `balance_date`    | DATE      | No                | Composite PK (with `account_id`)   | ISO 8601 format (`YYYY-MM-DD`). 90-day window ending 2024-12-31. One row per account per day — no gaps in `clean`, `medium`, `large`. |
| `closing_balance` | FLOAT     | Varies by variant | —                                  | Two decimal places. `clean` variant: `0.00`–`50,000.00` (no overdrafts). `medium` and `large`: down to `-500.00` (overdrafts included). `null_heavy`: ~20% nulls injected. |
| `txn_count_day`   | INTEGER   | No                | —                                  | Count of transactions on that day for the account. `0` = valid (no transactions). Range: `0`–`20`. |

---

## 2  Table Relationships and Join Cardinality

| Relationship | Join Key | Cardinality | Notes |
|---|---|---|---|
| `transactions` → `accounts` | `account_id` | Many-to-one | ~5 transactions per account in `clean`. FK nulls in `null_heavy` create unmatched rows on INNER JOIN — intentional. |
| `daily_balances` → `accounts` | `account_id` | Many-to-one | 90 balance rows per account in `clean`. FK nulls in `null_heavy` break composite key uniqueness — intentional. |
| `transactions` → `daily_balances` | `account_id` + `txn_date` = `balance_date` | Many-to-one | Non-standard join. Used in time-series enrichment tasks. |

**Accounts per variant**:

| Variant | Unique accounts (transactions) | Unique accounts (daily_balances) | Avg transactions per account |
|---|---|---|---|
| `clean` | ~100 | ~100 | ~5 avg |
| `null_heavy` | ~75 (25% null account_id) | ~90 (10% null) | ~5 avg (non-null only) |
| `duplicate_heavy` | ~100 | ~100 | ~6 avg (inflated by duplicates) |
| `medium` | ~500 | ~500 | ~10 avg |
| `large` | ~2,000 | ~2,000 | ~25 avg (range 1–100) |

---

## 3  Dataset Variants — Configurations and Row Counts

Every task is evaluated against all five variants. The `clean` variant is the gate condition: a model answer must achieve 100% correctness on `clean` before its variant results are included in the scorecard.

---

### 3.1  clean

| Property                | Value |
| ----------------------- | ----- |
| **Purpose**             | Gate condition. Baseline correctness. Must pass 100% to unlock variant scoring. |
| **transactions rows**   | ~500 |
| **accounts rows**       | ~100 |
| **daily_balances rows** | ~9,000 (100 accounts × 90 days) |
| **Nulls**               | None injected. All columns fully populated. |
| **Duplicates**          | None. Every primary key is unique. |
| **Value distribution**  | Uniform distribution across all enum values. No outliers. `txn_amount` range `0.01`–`9999.99`. `closing_balance` range `0.00`–`50000.00` (no overdrafts). |

---

### 3.2  null_heavy

| Property                 | Value |
| ------------------------ | ----- |
| **Purpose**              | Test null propagation in JOINs, null-safe aggregation, and imputation logic. |
| **transactions rows**    | ~500 |
| **accounts rows**        | ~100 |
| **daily_balances rows**  | ~9,000 |
| **Nulls injected**       | `transactions.account_id`: ~25%. `transactions.txn_amount`: ~20%. `transactions.merchant_category`: ~15%. `daily_balances.account_id`: ~10%. `daily_balances.closing_balance`: ~20%. |
| **What it stresses**     | Null propagation through joins. Null-safe aggregation. Conditional imputation in Python. Division-by-zero guards. |

---

### 3.3  duplicate_heavy

| Property                | Value |
| ----------------------- | ----- |
| **Purpose**             | Test deduplication correctness. Detect inflated aggregates caused by duplicate rows. |
| **transactions rows**   | ~600 (inflated from ~500 by ~15–20% duplicate injection) |
| **accounts rows**       | ~100 |
| **daily_balances rows** | ~9,000 (no duplicates in balances table) |
| **Nulls**               | None injected. |
| **Duplicates injected** | ~15–20% of `transactions` rows are exact or near-exact duplicates on `txn_id`. Some near-duplicates: same `txn_id`, same `account_id`, same `txn_amount`, different `txn_date` by ±1 day. |
| **What it stresses**    | Deduplication correctness. Inflated SUM and COUNT if duplicates not removed. Composite-key deduplication for near-duplicates. |

---

### 3.4  medium

| Property                | Value |
| ----------------------- | ----- |
| **Purpose**             | Test runtime and memory scaling under realistic load. |
| **transactions rows**   | ~5,000 |
| **accounts rows**       | ~500 |
| **daily_balances rows** | ~45,000 (500 accounts × 90 days) |
| **Nulls**               | None injected. Clean schema. |
| **Duplicates**          | None. |
| **What it stresses**    | Runtime scaling from ~500 to ~5,000 rows. Memory efficiency in Python. |

---

### 3.5  large

| Property                | Value |
| ----------------------- | ----- |
| **Purpose**             | Performance ceiling. Peak memory (Python). Query optimizer behavior (SQL). |
| **transactions rows**   | ~50,000 |
| **accounts rows**       | ~2,000 |
| **daily_balances rows** | ~180,000 (2,000 accounts × 90 days) |
| **Nulls**               | None injected. Clean schema. |
| **Duplicates**          | None. |
| **What it stresses**    | Peak memory in Python (tracemalloc ceiling). Query execution time in SQL. O(n²) pattern detection. |

---

### 3.6  Variant Summary

| Variant           | transactions | accounts | daily_balances | Nulls                       | Duplicates               | Purpose             |
| ----------------- | ------------ | -------- | -------------- | --------------------------- | ------------------------ | ------------------- |
| `clean`           | ~500         | ~100     | ~9,000         | None                        | None                     | Gate condition      |
| `null_heavy`      | ~500         | ~100     | ~9,000         | Yes — 10–25% on key columns | None                     | Null handling       |
| `duplicate_heavy` | ~600         | ~100     | ~9,000         | None                        | Yes — 15–20% on `txn_id` | Dedup correctness   |
| `medium`          | ~5,000       | ~500     | ~45,000        | None                        | None                     | Scaling             |
| `large`           | ~50,000      | ~2,000   | ~180,000       | None                        | None                     | Performance ceiling |

---

## 4  Column-Level Data Type Constraints and Value Ranges

### 4.1  synthetic_transactions.csv — Column Constraints

| Column              | Storage Type | Format / Enum                                   | Min Value              | Max Value                                                                           | Null Rule                    | Notes |
| ------------------- | ------------ | ----------------------------------------------- | ---------------------- | ----------------------------------------------------------------------------------- | ---------------------------- | ----- |
| `txn_id`            | STRING       | `SYNTHETIC_TXN_` + 6-digit zero-padded integer  | `SYNTHETIC_TXN_000001` | `SYNTHETIC_TXN_999999`                                                              | Never null                   | Unique per row in `clean`, `medium`, `large`. Non-unique in `duplicate_heavy` (intentional). |
| `account_id`        | STRING       | `SYNTHETIC_ACCT_` + 4-digit integer             | `SYNTHETIC_ACCT_0001`  | `SYNTHETIC_ACCT_9999`                                                               | Nullable — `null_heavy` only | FK to `synthetic_accounts.account_id`. Must exist in accounts table when not null. |
| `txn_date`          | DATE         | ISO 8601 `YYYY-MM-DD`                           | `2023-01-01`           | `2024-12-31`                                                                        | Never null                   | 24-month window ending on synthetic reference date. |
| `txn_amount`        | FLOAT        | Two decimal places                              | `0.01`                 | `9999.99` (`clean`/`null_heavy`/`duplicate_heavy`/`medium`) or `99999.99` (`large`) | Nullable — `null_heavy` only | Always positive. No zero values. Long-tail only in `large`. |
| `txn_type`          | STRING       | Enum                                            | —                      | —                                                                                   | Never null                   | Allowed values: `PURCHASE`, `REFUND`, `TRANSFER`, `FEE`. |
| `merchant_category` | STRING       | Enum                                            | —                      | —                                                                                   | Nullable — `null_heavy` only | Allowed values: `RETAIL`, `GROCERY`, `TRAVEL`, `DINING`, `UTILITIES`, `HEALTHCARE`. |
| `channel`           | STRING       | Enum                                            | —                      | —                                                                                   | Never null                   | Allowed values: `ONLINE`, `BRANCH`, `ATM`, `MOBILE`. |
| `is_flagged`        | BOOLEAN      | `true` / `false`                                | —                      | —                                                                                   | Never null                   | ~5% `true` in all variants. Stored as lowercase string in CSV. |

### 4.2  synthetic_accounts.csv — Column Constraints

| Column              | Storage Type | Format / Enum                        | Min Value             | Max Value             | Null Rule  | Notes |
| ------------------- | ------------ | ------------------------------------ | --------------------- | --------------------- | ---------- | ----- |
| `account_id`        | STRING       | `SYNTHETIC_ACCT_` + 4-digit integer  | `SYNTHETIC_ACCT_0001` | `SYNTHETIC_ACCT_9999` | Never null | PK. Always unique. |
| `customer_segment`  | STRING       | Enum                                 | —                     | —                     | Never null | Allowed values: `RETAIL`, `SMALL_BIZ`, `WEALTH`, `STUDENT`. Uniform distribution. |
| `account_open_date` | DATE         | ISO 8601 `YYYY-MM-DD`                | `2020-01-01`          | `2024-12-31`          | Never null | 5-year window. Always ≤ synthetic reference date. |
| `account_status`    | STRING       | Enum                                 | —                     | —                     | Never null | Allowed values: `ACTIVE`, `CLOSED`, `SUSPENDED`. Distribution: ~85% / ~10% / ~5%. |
| `region`            | STRING       | Enum                                 | —                     | —                     | Never null | Allowed values: `NORTH`, `SOUTH`, `EAST`, `WEST`. Uniform distribution. |

### 4.3  synthetic_daily_balances.csv — Column Constraints

| Column            | Storage Type | Format / Enum                        | Min Value             | Max Value             | Null Rule                    | Notes |
| ----------------- | ------------ | ------------------------------------ | --------------------- | --------------------- | ---------------------------- | ----- |
| `account_id`      | STRING       | `SYNTHETIC_ACCT_` + 4-digit integer  | `SYNTHETIC_ACCT_0001` | `SYNTHETIC_ACCT_9999` | Nullable — `null_heavy` only | Part of composite PK with `balance_date`. |
| `balance_date`    | DATE         | ISO 8601 `YYYY-MM-DD`                | `2024-10-03`          | `2024-12-31`          | Never null                   | 90-day window. Part of composite PK. |
| `closing_balance` | FLOAT        | Two decimal places                   | `-500.00`             | `50000.00`            | Nullable — `null_heavy` only | Negative values represent overdrafts. `clean` variant: minimum `0.00`. |
| `txn_count_day`   | INTEGER      | Whole number                         | `0`                   | `20`                  | Never null                   | 0 = no transactions that day (valid). Non-negative integer. |

### 4.4  Fixed Synthetic Reference Date

All date ranges are anchored to the **synthetic reference date: 2024-12-31**.

| Date Window          | Column              | Range                               |
| -------------------- | ------------------- | ----------------------------------- |
| Transaction history  | `txn_date`          | 2023-01-01 → 2024-12-31 (24 months) |
| Account history      | `account_open_date` | 2020-01-01 → 2024-12-31 (5 years)   |
| Daily balance window | `balance_date`      | 2024-10-03 → 2024-12-31 (90 days)   |

> **Why a fixed reference date?** Anchoring all dates to a fixed point ensures that tasks referencing "last 90 days", "prior 24 months", or "account age in years" produce deterministic results regardless of when the evaluation is run. The reference date must be declared in `references/deterministic-rules.md`.

### 4.5  Random Seed Policy

All synthetic data is generated using a fixed, declared random seed. The seed value must be documented in `references/deterministic-rules.md` before any data generation or evaluation run. Scripts must read the seed from that file — never hardcode it.

---

## 5  Two-Table Answer Architecture

All model-generated code is stored as individual files on disk, referenced by filename from two flat tables.

---

### 5.1  Filename Convention

Model-generated code files follow this naming pattern:

```
task{N}{model}.{ext}
```

| Component | Rule | Examples |
|---|---|---|
| `task` | Literal prefix | `task` |
| `{N}` | Task number, 1–30, no zero-padding | `1`, `15`, `30` |
| `{model}` | Single letter: `a` = model_a, `b` = model_b, `c` = model_c | `a`, `b`, `c` |
| `{ext}` | File extension encodes language | `.py` = Python, `.sql` = SQL |

**Examples**:

| Filename | Task | Model | Language |
|---|---|---|---|
| `task1a.sql` | SQL-001 | model_a | SQL |
| `task1b.sql` | SQL-001 | model_b | SQL |
| `task1c.sql` | SQL-001 | model_c | SQL |
| `task1a.py`  | PY-001  | model_a | Python |
| `task1b.py`  | PY-001  | model_b | Python |
| `task30c.sql` | SQL-030 | model_c | SQL |
| `task30c.py`  | PY-030  | model_c | Python |

> **Parsing rule**: The harness derives language from the file extension (`.py` → Python, `.sql` → SQL) and model identity from the letter before the extension. Real model names are mapped via `model_token_lookup.csv` held outside the zip and re-associated only at scorecard generation time.

All code files are stored at `assets/tasks/{task_id}/` alongside the prompt and reference solution.

---

### 5.2  Table 1 — task_bank.csv (60 rows)

**Location**: `assets/task_bank.csv`
**Purpose**: Master index for all 60 tasks. All scripts resolve file paths through this table — paths must never be hardcoded. One row per task.

| Field | Type | Nullable | Description / Example |
|---|---|---|---|
| `task_id` | STRING | No | `SQL-001` through `SQL-030`, `PY-001` through `PY-030`. Primary key. |
| `contracted` | BOOLEAN | No | `true` for all 60 tasks (this is the full contracted scope). Controls `--contracted-only` scorecard filter. |
| `category` | ENUM | No | `easy`, `medium`, or `hard`. |
| `prompt` | STRING | No | Full prompt text sent identically to all 3 models. Stored inline — no separate file reference. |
| `model_a_filename` | STRING | No | `task1a.sql` or `task1a.py`. Filename of Model A's generated code file. |
| `model_b_filename` | STRING | No | `task1b.sql` or `task1b.py`. Filename of Model B's generated code file. |
| `model_c_filename` | STRING | No | `task1c.sql` or `task1c.py`. Filename of Model C's generated code file. |

**Example rows**:

```
task_id,  contracted, category, prompt,                                                                          model_a_filename, model_b_filename, model_c_filename
SQL-001,  true,       easy,     "Return all ACTIVE accounts, showing account_id, customer_segment, and region.", task1a.sql,       task1b.sql,       task1c.sql
SQL-011,  true,       medium,   "Use a CTE to isolate only ACTIVE accounts, then join that CTE to transactions.", task11a.sql,      task11b.sql,      task11c.sql
PY-001,   true,       easy,     "Load one of the accounts CSV files and assert the expected five column names.",  task1a.py,        task1b.py,        task1c.py
PY-011,   true,       medium,   "Write a functional ETL pipeline that loads accounts, validates schema...",       task11a.py,       task11b.py,       task11c.py
```

> **Numbering note**: SQL tasks and Python tasks both use numbers 1–30. Filenames remain unambiguous because language is encoded by the extension (`.sql` vs `.py`) and tasks are stored under per-task directories (`assets/tasks/{task_id}/`).

---

### 5.3  Table 2 — eval_results.csv (900 rows)

**Location**: `assets/eval_results.csv`
**Purpose**: All pre-recorded evaluation metrics for every model × task × variant combination. One row per filename × dataset variant. 900 rows total (60 tasks × 3 models × 5 variants).

| Field | Type | Nullable | Source | Notes |
|---|---|---|---|---|
| `filename` | STRING | No | Phase 1 | Primary key component. E.g. `task1a.sql`, `task1a.py`. Encodes task number, model, and language. |
| `dataset_variant` | ENUM | No | Variant set | `clean`, `null_heavy`, `duplicate_heavy`, `medium`, `large`. Primary key component (with `filename`). |
| `token_usage_input` | INTEGER | No | Cursor plugin (Phase 1) | Input tokens consumed for code generation. Same value across all 5 variant rows for a given filename. |
| `token_usage_output` | INTEGER | No | Cursor plugin (Phase 1) | Output tokens generated. Same value across all 5 variant rows for a given filename. |
| `runtime_ms` | INTEGER | No | Phase 2 execution | Query/script execution time against this variant's dataset. Varies per variant. |
| `peak_memory_bytes` | INTEGER | Python only | tracemalloc (Phase 2B) | Peak Python heap memory. Python files only. Null for `.sql` files. |
| `formatting_violations` | INTEGER | No | flake8 / sqlfluff (Phase 3) | PEP8 violations (Python) or sqlfluff violations (SQL). Same value across all 5 variant rows for a given filename. `0` = clean. |
| `pytest_filename` | STRING | Python only | Phase 2B | Test file used, e.g. `test_task1a.py`. Null for `.sql` files. |
| `pytest_pass` | BOOLEAN | Python only | pytest (Phase 2B) | `true` or `false`. Syntax errors and runtime exceptions recorded as `false`. Null for `.sql` files. |
| `checksum` | STRING | SQL only | SHA-256 (Phase 2A) | SHA-256 hash of result set for this variant. Null for `.py` files. |
| `row_count` | INTEGER | SQL only | SQL engine (Phase 2A) | Row count of result set for this variant. Null for `.py` files. |
| `snapshot_pass` | BOOLEAN | SQL only | Snapshot comparison (Phase 2A) | `true` if result set matches reference snapshot for this variant. Null for `.py` files. |

**Example rows**:

```
filename,      dataset_variant,   token_usage_input, token_usage_output, runtime_ms, peak_memory_bytes, formatting_violations, pytest_filename,    pytest_pass, checksum,    row_count, snapshot_pass
task1a.sql,    clean,             512,               128,                45,         ,                  2,                     ,                   ,            abc123...,   500,       true
task1a.sql,    null_heavy,        512,               128,                48,         ,                  2,                     ,                   ,            def456...,   380,       true
task1a.py,     clean,             490,               210,                88,         4200000,           0,                     test_task1a.py,     true,        ,            ,
task1a.py,     null_heavy,        490,               210,                91,         4350000,           0,                     test_task1a.py,     false,       ,            ,
```

---
