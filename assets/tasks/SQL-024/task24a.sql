-- SYNTHETIC DATA — no real financial data
-- Task: SQL-024 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH ranked_accounts AS (
    SELECT 
        account_id,
        customer_segment,
        account_open_date,
        account_status,
        region,
        CASE 
            WHEN account_status = 'ACTIVE' THEN 1
            WHEN account_status = 'SUSPENDED' THEN 2
            WHEN account_status = 'CLOSED' THEN 3
            ELSE 4
        END AS status_rank,
        ROW_NUMBER() OVER (
            PARTITION BY account_id 
            ORDER BY 
                CASE 
                    WHEN account_status = 'ACTIVE' THEN 1
                    WHEN account_status = 'SUSPENDED' THEN 2
                    WHEN account_status = 'CLOSED' THEN 3
                    ELSE 4
                END
        ) AS rn
    FROM synthetic_duplicate_heavy_accounts
)
SELECT 
    account_id,
    customer_segment,
    account_open_date,
    account_status,
    region
FROM ranked_accounts
WHERE rn = 1
ORDER BY account_id;
