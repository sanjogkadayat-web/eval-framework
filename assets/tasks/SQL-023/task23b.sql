-- SYNTHETIC DATA — no real financial data
-- Task: SQL-023 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH deduped AS (
  SELECT
    t.*,
    ROW_NUMBER() OVER (
      PARTITION BY
        t.txn_id,
        t.account_id,
        t.txn_date,
        t.txn_amount,
        t.txn_type,
        t.merchant_category,
        t.channel,
        t.is_flagged
      ORDER BY t.txn_id
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
FROM deduped
WHERE rn = 1
ORDER BY
  txn_id;
