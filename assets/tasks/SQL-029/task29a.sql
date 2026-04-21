-- SYNTHETIC DATA — no real financial data
-- Task: SQL-029 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH account_cohorts AS (
    SELECT 
        account_id,
        DATE_TRUNC('month', account_open_date) AS cohort_month
    FROM synthetic_clean_accounts
),
transaction_months AS (
    SELECT 
        account_id,
        DATE_TRUNC('month', txn_date) AS txn_month,
        COUNT(*) AS txn_count,
        SUM(txn_amount) AS txn_amount
    FROM synthetic_clean_transactions
    WHERE txn_amount IS NOT NULL
    GROUP BY account_id, DATE_TRUNC('month', txn_date)
)
SELECT 
    ac.cohort_month,
    tm.txn_month,
    DATEDIFF('month', ac.cohort_month, tm.txn_month) AS months_since_open,
    COUNT(DISTINCT tm.account_id) AS active_accounts,
    SUM(tm.txn_count) AS total_txn_count,
    SUM(tm.txn_amount) AS total_txn_amount
FROM account_cohorts ac
LEFT JOIN transaction_months tm ON ac.account_id = tm.account_id
WHERE tm.txn_month IS NOT NULL
GROUP BY ac.cohort_month, tm.txn_month
ORDER BY ac.cohort_month, tm.txn_month;
