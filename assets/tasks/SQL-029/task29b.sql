-- SYNTHETIC DATA — no real financial data
-- Task: SQL-029 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH cohorts AS (
  SELECT
    account_id,
    DATE_TRUNC('month', account_open_date)::DATE AS cohort_month
  FROM synthetic_<variant>_accounts
  WHERE account_open_date IS NOT NULL
),
cohort_txns AS (
  SELECT
    c.cohort_month,
    DATE_TRUNC('month', t.txn_date)::DATE AS activity_month,
    DATE_DIFF('month', c.cohort_month, DATE_TRUNC('month', t.txn_date)::DATE) AS months_since_cohort,
    t.account_id
  FROM cohorts AS c
  INNER JOIN synthetic_<variant>_transactions AS t
    ON t.account_id = c.account_id
  WHERE t.txn_date IS NOT NULL
    AND DATE_TRUNC('month', t.txn_date)::DATE >= c.cohort_month
)
SELECT
  cohort_month,
  months_since_cohort,
  COUNT(DISTINCT account_id) AS active_accounts,
  COUNT(*) AS txn_count
FROM cohort_txns
GROUP BY
  cohort_month,
  months_since_cohort
ORDER BY
  cohort_month,
  months_since_cohort;
