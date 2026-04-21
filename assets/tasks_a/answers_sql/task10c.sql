-- SYNTHETIC DATA — no real financial data
-- Task: SQL-010 | Tier: Easy
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT 
    a.account_id,
    a.customer_segment,
    a.region,
    a.account_status
FROM synthetic_clean_accounts a
WHERE EXISTS (
    SELECT 1
    FROM synthetic_clean_transactions t
    WHERE t.account_id = a.account_id
    AND t.is_flagged = true
)
ORDER BY a.account_id;
