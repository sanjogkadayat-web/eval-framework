-- SYNTHETIC DATA — no real financial data
-- Task: SQL-025 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT 
    t.txn_id,
    t.account_id,
    t.txn_date,
    t.txn_amount,
    'missing_account_id' AS integrity_issue
FROM synthetic_clean_transactions t
LEFT JOIN synthetic_clean_accounts a ON t.account_id = a.account_id
WHERE a.account_id IS NULL AND t.account_id IS NOT NULL
ORDER BY t.txn_id;
