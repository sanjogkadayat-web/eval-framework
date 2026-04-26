-- SYNTHETIC DATA — no real financial data
-- Task: SQL-013 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT 
    a.region,
    COUNT(CASE WHEN t.is_flagged = true THEN 1 END) AS flagged_txn_count,
    COUNT(CASE WHEN t.is_flagged = false THEN 1 END) AS unflagged_txn_count
FROM synthetic_clean_accounts a
INNER JOIN synthetic_clean_transactions t ON a.account_id = t.account_id
GROUP BY a.region
ORDER BY a.region;
