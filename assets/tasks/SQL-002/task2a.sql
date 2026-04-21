-- SYNTHETIC DATA — no real financial data
-- Task: SQL-002 | Tier: Easy
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT 
    txn_type,
    SUM(txn_amount) AS total_txn_amount
FROM synthetic_clean_transactions
WHERE txn_amount IS NOT NULL
GROUP BY txn_type
ORDER BY txn_type;
