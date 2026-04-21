-- SYNTHETIC DATA — no real financial data
-- Task: SQL-0025 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
SELECT
  t.txn_id,
  t.account_id,
  t.txn_date,
  t.txn_amount,
  'Referential integrity issue: account_id not found' AS issue
FROM synthetic_<variant>_transactions AS t
LEFT JOIN synthetic_<variant>_accounts AS a
  ON t.account_id = a.account_id
WHERE
  a.account_id IS NULL
ORDER BY
  t.txn_id;