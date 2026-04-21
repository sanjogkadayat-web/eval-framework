-- SYNTHETIC DATA — no real financial data
-- Task: SQL-005 | Tier: Easy
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT 
    t.txn_id,
    t.account_id,
    a.account_status
FROM synthetic_clean_transactions t
INNER JOIN synthetic_clean_accounts a ON t.account_id = a.account_id
ORDER BY t.txn_id;
