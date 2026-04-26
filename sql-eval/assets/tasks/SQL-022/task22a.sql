-- SYNTHETIC DATA — no real financial data
-- Task: SQL-022 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH account_counts AS (
    SELECT 
        region,
        COUNT(DISTINCT account_id) AS account_count
    FROM synthetic_clean_accounts
    GROUP BY region
),
flagged_counts AS (
    SELECT 
        a.region,
        COUNT(CASE WHEN t.is_flagged = true THEN 1 END) AS flagged_txn_count
    FROM synthetic_clean_accounts a
    INNER JOIN synthetic_clean_transactions t ON a.account_id = t.account_id
    GROUP BY a.region
),
balance_averages AS (
    SELECT 
        a.region,
        AVG(b.closing_balance) AS avg_closing_balance
    FROM synthetic_clean_accounts a
    INNER JOIN synthetic_clean_daily_balances b ON a.account_id = b.account_id
    WHERE b.closing_balance IS NOT NULL
    GROUP BY a.region
)
SELECT 
    ac.region,
    ac.account_count,
    fc.flagged_txn_count,
    ba.avg_closing_balance
FROM account_counts ac
LEFT JOIN flagged_counts fc ON ac.region = fc.region
LEFT JOIN balance_averages ba ON ac.region = ba.region
ORDER BY ac.region;
