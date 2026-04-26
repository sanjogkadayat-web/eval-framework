-- SYNTHETIC DATA — no real financial data
-- Task: SQL-005 | Tier: Easy
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT
  t.txn_id,
  a.account_status
FROM synthetic_<variant>_transactions AS t
INNER JOIN synthetic_<variant>_accounts AS a
  ON a.account_id = t.account_id
ORDER BY t.txn_id;
