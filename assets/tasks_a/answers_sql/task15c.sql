-- SYNTHETIC DATA — no real financial data
-- Task: SQL-015 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH account_totals AS (
    SELECT 
        t.account_id,
        a.region,
        SUM(t.txn_amount) AS total_txn_amount
    FROM synthetic_clean_transactions t
    INNER JOIN synthetic_clean_accounts a ON t.account_id = a.account_id
    WHERE t.txn_amount IS NOT NULL
    GROUP BY t.account_id, a.region
),
ranked_accounts AS (
    SELECT 
        account_id,
        region,
        total_txn_amount,
        RANK() OVER (PARTITION BY region ORDER BY total_txn_amount DESC) AS region_rank
    FROM account_totals
)
SELECT 
    account_id,
    region,
    total_txn_amount,
    region_rank
FROM ranked_accounts
ORDER BY region, region_rank;
