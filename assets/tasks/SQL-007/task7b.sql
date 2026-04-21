-- SYNTHETIC DATA — no real financial data
-- Task: SQL-007 | Tier: Easy
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT
  txn_id,
  account_id,
  txn_amount,
  CASE
    WHEN txn_amount IS NULL THEN NULL
    WHEN txn_amount < 100 THEN 'small'
    WHEN txn_amount < 1000 THEN 'medium'
    ELSE 'large'
  END AS amount_bucket
FROM synthetic_<variant>_transactions
ORDER BY txn_id;
