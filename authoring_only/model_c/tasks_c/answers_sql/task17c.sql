-- SYNTHETIC DATA — no real financial data
-- Task: SQL-0017 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
WITH ranked_transactions AS (
  SELECT
    txn_id,
    account_id,
    txn_date,
    txn_amount,
    ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY txn_amount DESC, txn_id) AS rn
  FROM synthetic_<variant>_transactions
)
SELECT
  txn_id,
  account_id,
  txn_date,
  txn_amount
FROM ranked_transactions
WHERE
  rn <= 3
ORDER BY
  account_id,
  txn_amount DESC,
  txn_id;