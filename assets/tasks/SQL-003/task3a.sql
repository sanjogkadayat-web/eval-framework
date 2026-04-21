-- SYNTHETIC DATA — no real financial data
-- Task: SQL-003 | Tier: Easy
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT 
    channel,
    ROUND(AVG(txn_amount), 2) AS avg_txn_amount
FROM synthetic_clean_transactions
WHERE txn_amount IS NOT NULL
GROUP BY channel
ORDER BY channel;
