-- SYNTHETIC DATA — no real financial data
-- Task: SQL-016 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH ranked AS (
  SELECT
    t.*,
    ROW_NUMBER() OVER (
      PARTITION BY t.txn_id
      ORDER BY t.txn_date DESC NULLS LAST, t.account_id DESC NULLS LAST, t.txn_amount DESC NULLS LAST
    ) AS rn
  FROM synthetic_<variant>_transactions AS t
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
FROM ranked
WHERE rn = 1
ORDER BY
  txn_id;
