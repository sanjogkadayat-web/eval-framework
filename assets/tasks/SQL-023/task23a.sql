-- SYNTHETIC DATA — no real financial data
-- Task: SQL-023 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH ranked_duplicates AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (
            PARTITION BY txn_id, account_id, txn_date, txn_amount, txn_type, merchant_category, channel, is_flagged
            ORDER BY txn_id
        ) AS rn
    FROM synthetic_duplicate_heavy_transactions
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
FROM ranked_duplicates
WHERE rn = 1
ORDER BY txn_id;
