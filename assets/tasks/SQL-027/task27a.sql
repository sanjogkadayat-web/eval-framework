-- SYNTHETIC DATA — no real financial data
-- Task: SQL-027 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH segment_stats AS (
    SELECT 
        a.customer_segment,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY b.closing_balance) AS q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY b.closing_balance) AS q3
    FROM synthetic_clean_accounts a
    INNER JOIN synthetic_clean_daily_balances b ON a.account_id = b.account_id
    WHERE b.closing_balance IS NOT NULL
    GROUP BY a.customer_segment
),
segment_iqr AS (
    SELECT 
        customer_segment,
        q1,
        q3,
        q3 - q1 AS iqr,
        q1 - 1.5 * (q3 - q1) AS lower_bound,
        q3 + 1.5 * (q3 - q1) AS upper_bound
    FROM segment_stats
)
SELECT 
    b.account_id,
    b.balance_date,
    b.closing_balance,
    a.customer_segment,
    si.lower_bound,
    si.upper_bound,
    CASE 
        WHEN b.closing_balance < si.lower_bound OR b.closing_balance > si.upper_bound THEN true
        ELSE false
    END AS is_outlier
FROM synthetic_clean_daily_balances b
INNER JOIN synthetic_clean_accounts a ON b.account_id = a.account_id
INNER JOIN segment_iqr si ON a.customer_segment = si.customer_segment
WHERE b.closing_balance IS NOT NULL
ORDER BY b.account_id, b.balance_date;
