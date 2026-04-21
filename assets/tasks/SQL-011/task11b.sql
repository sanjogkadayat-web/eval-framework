-- SYNTHETIC DATA — no real financial data
-- Task: SQL-011 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH txn_by_region AS (
  SELECT
    a.region,
    SUM(t.txn_amount) AS total_txn_amount
  FROM synthetic_<variant>_accounts AS a
  INNER JOIN synthetic_<variant>_transactions AS t
    ON t.account_id = a.account_id
  GROUP BY
    a.region
),
balance_by_region AS (
  SELECT
    a.region,
    AVG(b.closing_balance) AS avg_closing_balance
  FROM synthetic_<variant>_accounts AS a
  INNER JOIN synthetic_<variant>_daily_balances AS b
    ON b.account_id = a.account_id
  GROUP BY
    a.region
)
SELECT
  COALESCE(t.region, b.region) AS region,
  t.total_txn_amount,
  b.avg_closing_balance
FROM txn_by_region AS t
FULL OUTER JOIN balance_by_region AS b
  ON b.region = t.region
ORDER BY
  region;
