-- SYNTHETIC DATA — no real financial data
-- Task: SQL-0029 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
WITH cohorts AS (
  SELECT
    account_id,
    STRFTIME(account_open_date, '%Y-%m') AS cohort_month
  FROM synthetic_<variant>_accounts
),
account_activity AS (
  SELECT
    account_id,
    STRFTIME(txn_date, '%Y-%m') AS activity_month
  FROM synthetic_<variant>_transactions
  GROUP BY
    account_id,
    activity_month
)
SELECT
  c.cohort_month,
  aa.activity_month,
  COUNT(DISTINCT c.account_id) AS accounts_in_cohort_month,
  COUNT(DISTINCT aa.account_id) AS accounts_with_activity
FROM cohorts AS c
INNER JOIN account_activity AS aa
  ON c.account_id = aa.account_id
WHERE
  aa.activity_month >= c.cohort_month
GROUP BY
  c.cohort_month,
  aa.activity_month
ORDER BY
  c.cohort_month,
  aa.activity_month;