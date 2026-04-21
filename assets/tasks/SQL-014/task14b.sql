-- SYNTHETIC DATA — no real financial data
-- Task: SQL-014 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH active_accounts AS (
  SELECT
    account_id,
    customer_segment,
    region
  FROM synthetic_<variant>_accounts
  WHERE account_status = 'ACTIVE'
)
SELECT
  t.txn_id,
  t.account_id,
  a.customer_segment,
  a.region,
  t.txn_date,
  t.txn_amount,
  t.txn_type
FROM active_accounts AS a
INNER JOIN synthetic_<variant>_transactions AS t
  ON t.account_id = a.account_id
ORDER BY
  t.txn_id;
