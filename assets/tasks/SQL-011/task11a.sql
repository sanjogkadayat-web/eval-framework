-- SYNTHETIC DATA — no real financial data
-- Task: SQL-011 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT 
    a.region,
    SUM(t.txn_amount) AS total_txn_amount,
    AVG(b.closing_balance) AS avg_closing_balance
FROM synthetic_clean_accounts a
INNER JOIN synthetic_clean_transactions t ON a.account_id = t.account_id
INNER JOIN synthetic_clean_daily_balances b ON a.account_id = b.account_id
WHERE t.txn_amount IS NOT NULL AND b.closing_balance IS NOT NULL
GROUP BY a.region
ORDER BY a.region;
