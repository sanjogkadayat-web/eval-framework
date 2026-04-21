-- SYNTHETIC DATA — no real financial data
-- Task: SQL-006 | Tier: Easy
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT 
    a.account_id,
    a.customer_segment,
    a.region,
    a.account_status
FROM synthetic_clean_accounts a
LEFT JOIN synthetic_clean_transactions t ON a.account_id = t.account_id
WHERE t.txn_id IS NULL
ORDER BY a.account_id;
