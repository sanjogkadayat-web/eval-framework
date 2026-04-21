-- SYNTHETIC DATA — no real financial data
-- Task: SQL-008 | Tier: Easy
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT 
    EXTRACT(YEAR FROM txn_date) AS txn_year,
    EXTRACT(MONTH FROM txn_date) AS txn_month,
    COUNT(*) AS txn_count
FROM synthetic_clean_transactions
WHERE txn_date IS NOT NULL
GROUP BY txn_year, txn_month
ORDER BY txn_year, txn_month;
