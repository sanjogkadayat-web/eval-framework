-- SYNTHETIC DATA — no real financial data
-- Task: SQL-0015 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
WITH account_total_transactions AS (
  SELECT
    account_id,
    SUM(txn_amount) AS total_txn_amount
  FROM synthetic_<variant>_transactions
  GROUP BY
    account_id
),
ranked_accounts AS (
  SELECT
    a.account_id,
    a.region,
    att.total_txn_amount,
    RANK() OVER (PARTITION BY a.region ORDER BY att.total_txn_amount DESC) AS rank_within_region
  FROM synthetic_<variant>_accounts AS a
  INNER JOIN account_total_transactions AS att
    ON a.account_id = att.account_id
)
SELECT
  account_id,
  region,
  total_txn_amount,
  rank_within_region
FROM ranked_accounts
ORDER BY
  region,
  rank_within_region;