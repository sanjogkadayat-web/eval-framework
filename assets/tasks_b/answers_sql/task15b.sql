-- SYNTHETIC DATA — no real financial data
-- Task: SQL-015 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH account_totals AS (
  SELECT
    a.region,
    a.account_id,
    SUM(t.txn_amount) AS total_txn_amount
  FROM synthetic_<variant>_accounts AS a
  INNER JOIN synthetic_<variant>_transactions AS t
    ON t.account_id = a.account_id
  GROUP BY
    a.region,
    a.account_id
),
ranked AS (
  SELECT
    region,
    account_id,
    total_txn_amount,
    DENSE_RANK() OVER (
      PARTITION BY region
      ORDER BY total_txn_amount DESC NULLS LAST, account_id
    ) AS region_rank
  FROM account_totals
)
SELECT
  region,
  account_id,
  total_txn_amount,
  region_rank
FROM ranked
ORDER BY
  region,
  region_rank,
  account_id;
