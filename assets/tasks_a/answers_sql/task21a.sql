-- SYNTHETIC DATA — no real financial data
-- Task: SQL-021 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT 
    account_id,
    FIRST_VALUE(closing_balance) OVER (
        PARTITION BY account_id 
        ORDER BY balance_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS first_closing_balance,
    LAST_VALUE(closing_balance) OVER (
        PARTITION BY account_id 
        ORDER BY balance_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS last_closing_balance
FROM synthetic_clean_daily_balances
WHERE account_id IS NOT NULL AND closing_balance IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY balance_date) = 1
ORDER BY account_id;
