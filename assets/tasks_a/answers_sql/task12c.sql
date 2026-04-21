-- SYNTHETIC DATA — no real financial data
-- Task: SQL-012 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT 
    t.txn_id,
    t.account_id,
    t.txn_amount,
    a.account_status,
    t.is_flagged,
    CASE 
        WHEN a.account_status = 'ACTIVE' AND t.is_flagged = true THEN 'active-high-risk'
        WHEN a.account_status = 'ACTIVE' AND t.is_flagged = false THEN 'active-normal'
        ELSE 'inactive'
    END AS txn_classification
FROM synthetic_clean_transactions t
INNER JOIN synthetic_clean_accounts a ON t.account_id = a.account_id
ORDER BY t.txn_id;
