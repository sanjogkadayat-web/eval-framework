-- SYNTHETIC DATA — no real financial data
-- Task: SQL-007 | Tier: Easy
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT 
    txn_id,
    txn_amount,
    CASE 
        WHEN txn_amount < 100 THEN 'small'
        WHEN txn_amount >= 100 AND txn_amount < 1000 THEN 'medium'
        WHEN txn_amount >= 1000 THEN 'large'
        ELSE 'unknown'
    END AS txn_amount_bucket
FROM synthetic_clean_transactions
WHERE txn_amount IS NOT NULL
ORDER BY txn_id;
