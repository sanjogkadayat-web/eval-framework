-- SYNTHETIC DATA — no real financial data
-- Task: SQL-0018 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
SELECT
  txn_id,
  account_id,
  txn_date,
  txn_amount,
  SUM(txn_amount) OVER (PARTITION BY account_id ORDER BY txn_date, txn_id) AS running_total_txn_amount
FROM synthetic_<variant>_transactions
ORDER BY
  account_id,
  txn_date,
  txn_id;