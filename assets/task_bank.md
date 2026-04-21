# SQL and Python Task Banks for the 3-Table / 5-Variant Synthetic Dataset

These task banks are grounded in the uploaded dataset structure:

- **accounts**: `account_id`, `customer_segment`, `account_open_date`, `account_status`, `region`
- **transactions**: `txn_id`, `account_id`, `txn_date`, `txn_amount`, `txn_type`, `merchant_category`, `channel`, `is_flagged`
- **daily_balances**: `account_id`, `balance_date`, `closing_balance`, `txn_count_day`

Dataset variants:

1. `synthetic_clean_*`
2. `synthetic_medium_*`
3. `synthetic_large_*`
4. `synthetic_null_heavy_*`
5. `synthetic_duplicate_heavy_*`

All tasks are dataset-aware and reusable across all five variants.


## SQL — 30 Tasks

| Task ID | Tier | Task |
|---|---|---|
| SQL-001 | Easy | Return all ACTIVE accounts from the accounts table, showing account_id, customer_segment, and region. |
| SQL-002 | Easy | Compute total txn_amount by txn_type. |
| SQL-003 | Easy | Show average txn_amount by channel, rounded to 2 decimals. |
| SQL-004 | Easy | Find the minimum and maximum closing_balance for each account_id. |
| SQL-005 | Easy | Inner join accounts and transactions to show each txn_id with account_status. |
| SQL-006 | Easy | Left join accounts to transactions and return accounts that have no transactions. |
| SQL-007 | Easy | Bucket txn_amount into 'small', 'medium', and 'large' using CASE WHEN. |
| SQL-008 | Easy | Extract year and month from txn_date and count transactions by year-month. |
| SQL-009 | Easy | Use COALESCE to replace NULL region values with 'UNKNOWN'. |
| SQL-010 | Easy | Use EXISTS to return accounts that have at least one flagged transaction. |
| SQL-011 | Medium | Join accounts, transactions, and daily_balances to compute total txn_amount and average closing_balance by region. |
| SQL-012 | Medium | After joining accounts and transactions, classify each transaction as 'active-high-risk', 'active-normal', or 'inactive' using CASE. |
| SQL-013 | Medium | Produce one row per region with conditional counts of flagged vs unflagged transactions. |
| SQL-014 | Medium | Use a CTE to isolate only ACTIVE accounts, then join that CTE to transactions. |
| SQL-015 | Medium | Chain two CTEs: first total txn_amount per account, second rank accounts within each region. |
| SQL-016 | Medium | Use a CTE with ROW_NUMBER to keep the latest duplicate transaction per txn_id in the duplicate-heavy variant. |
| SQL-017 | Medium | Use a CTE plus ROW_NUMBER to return the top 3 highest-value transactions per account. |
| SQL-018 | Medium | Create a running total of txn_amount per account ordered by txn_date. |
| SQL-019 | Medium | Compute a 7-day moving average of closing_balance per account. |
| SQL-020 | Medium | Use LAG to calculate day-over-day change in closing_balance for each account. |
| SQL-021 | Medium | Return the first and last closing_balance observed for each account using window functions. |
| SQL-022 | Medium | Build a three-CTE scorecard with account count, flagged txn count, and average balance by region. |
| SQL-023 | Hard | Remove exact duplicate rows from duplicate-heavy transactions while keeping the earliest txn_id occurrence. |
| SQL-024 | Hard | Deduplicate accounts by precedence rule: ACTIVE outranks SUSPENDED, which outranks CLOSED, regardless of open date. |
| SQL-025 | Hard | Find transactions whose account_id does not exist in accounts and report them as referential-integrity issues. |
| SQL-026 | Hard | Flag transaction outliers using z-scores computed from txn_amount within each merchant_category. |
| SQL-027 | Hard | Flag balance outliers per customer_segment using the IQR method. |
| SQL-028 | Hard | Build a simple funnel from account_opened → first_transaction → first_flagged_transaction and measure drop-off. |
| SQL-029 | Hard | Perform cohort analysis by grouping accounts by account_open_date month and measuring later-month transaction activity. |
| SQL-030 | Hard | Write a multi-step SQL ETL pipeline that ingests raw accounts, validates required fields, deduplicates, and outputs a conformed table. |


## Python — 30 Tasks

| Task ID | Tier | Task |
|---|---|---|
| PY-001 | Easy | Load one of the accounts CSV files, skip the synthetic header row, and assert the expected five column names. |
| PY-002 | Easy | Validate that account_open_date, txn_date, and balance_date can be parsed as dates and that numeric columns have numeric dtype. |
| PY-003 | Easy | Count nulls per column in the null-heavy variant and raise an error if any column exceeds a configured threshold. |
| PY-004 | Easy | Drop exact duplicate rows from duplicate-heavy transactions and print how many were removed. |
| PY-005 | Easy | Filter the transactions table to keep only flagged transactions above a chosen amount and log the number dropped. |
| PY-006 | Easy | Clean string columns by stripping whitespace and normalizing region and customer_segment to uppercase. |
| PY-007 | Easy | Group transactions by txn_type and compute total txn_amount and row count. |
| PY-008 | Easy | Build a pivot table of total txn_amount by region and channel. |
| PY-009 | Easy | Fill null txn_amount values with the median txn_amount of the file. |
| PY-010 | Easy | Flag transactions whose channel is not in the allowed set {ATM, BRANCH, MOBILE, ONLINE}. |
| PY-011 | Medium | Write a functional ETL pipeline that loads accounts, validates schema, filters active rows, and saves output. |
| PY-012 | Medium | Create a running total of txn_amount within each account ordered by txn_date. |
| PY-013 | Medium | Compute a rolling average of closing_balance over the last 7 observations per account. |
| PY-014 | Medium | Compute a rolling 7-day sum of txn_amount for each account using a time-based window. |
| PY-015 | Medium | Add a previous_txn_amount feature within each account using shift. |
| PY-016 | Medium | Extract day_of_week, month, quarter, and is_weekend features from txn_date. |
| PY-017 | Medium | Build a three-DataFrame merge pipeline across accounts, transactions, and daily_balances and assert row counts at each step. |
| PY-018 | Medium | Flag rows where txn_date is earlier than account_open_date after joining accounts and transactions. |
| PY-019 | Medium | Deduplicate accounts by keeping the best row per account_id using a precedence rule over account_status. |
| PY-020 | Medium | Flag txn_amount outliers using the IQR rule. |
| PY-021 | Medium | Assign each account to a cohort based on account_open_date month. |
| PY-022 | Medium | Generate an audit log DataFrame capturing each transformation step and row counts before/after. |
| PY-023 | Hard | Build an end-to-end pipeline that ingests raw files, validates schema, deduplicates, engineers features, and writes outputs with logging. |
| PY-024 | Hard | Implement SCD Type 2 history tracking for account_status changes across account snapshots. |
| PY-025 | Hard | Flag rolling z-score anomalies in txn_amount within each account using a moving window. |
| PY-026 | Hard | Compute funnel drop-off from account creation to first transaction to first flagged transaction. |
| PY-027 | Hard | Calculate RFM scores (recency, frequency, monetary) for each account. |
| PY-028 | Hard | Flag likely churned accounts with no transactions in the last N days relative to the dataset max date. |
| PY-029 | Hard | Run a config-driven pipeline where thresholds and input paths come from YAML. |
| PY-030 | Hard | Write parameterized pytest cases covering null-heavy, duplicate-heavy, and clean variants for one transformation function. |
