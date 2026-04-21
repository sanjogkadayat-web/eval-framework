-- SYNTHETIC DATA — no real financial data
-- Task: SQL-016 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH ranked_transactions AS (
    SELECT 
        txn_id,
        account_id,
        txn_date,
        txn_amount,
        txn_type,
        merchant_category,
        channel,
        is_flagged,
        ROW_NUMBER() OVER (PARTITION BY txn_id ORDER BY txn_date DESC, account_id) AS rn
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
FROM ranked_transactions
WHERE rn = 1
ORDER BY txn_id;
