-- SYNTHETIC DATA — no real financial data
-- Task: SQL-014 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH active_accounts AS (
    SELECT 
        account_id,
        customer_segment,
        region,
        account_open_date
    FROM synthetic_clean_accounts
    WHERE account_status = 'ACTIVE'
)
SELECT 
    t.txn_id,
    t.account_id,
    t.txn_date,
    t.txn_amount,
    t.txn_type,
    a.customer_segment,
    a.region
FROM synthetic_clean_transactions t
INNER JOIN active_accounts a ON t.account_id = a.account_id
ORDER BY t.txn_id;
