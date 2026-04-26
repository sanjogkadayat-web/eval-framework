-- SYNTHETIC DATA — no real financial data
-- Task: SQL-0023 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
WITH deduplicated_transactions AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY txn_id, account_id, txn_date, txn_amount, txn_type, merchant_category, channel, is_flagged ORDER BY txn_id) AS rn
  FROM synthetic_<variant>_transactions
)
SELECT
  txn_id,
  account_id,
  txn_date,
  txn_amount,
  txn_type,
  merchant_category,
  channel,
  is_flagged
FROM deduplicated_transactions
WHERE
  rn = 1
ORDER BY
  txn_id;