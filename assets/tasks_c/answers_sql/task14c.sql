-- SYNTHETIC DATA — no real financial data
-- Task: SQL-0014 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
WITH active_accounts AS (
  SELECT
    account_id
  FROM synthetic_<variant>_accounts
  WHERE
    account_status = 'ACTIVE'
)
SELECT
  t.*
FROM active_accounts AS a
INNER JOIN synthetic_<variant>_transactions AS t
  ON a.account_id = t.account_id
ORDER BY
  t.account_id,
  t.txn_id;