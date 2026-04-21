-- SYNTHETIC DATA — no real financial data
-- Task: SQL-028 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH accounts_opened AS (
    SELECT COUNT(*) AS accounts_opened
    FROM synthetic_clean_accounts
),
first_transactions AS (
    SELECT 
        t.account_id,
        MIN(t.txn_date) AS first_txn_date
    FROM synthetic_clean_transactions t
    GROUP BY t.account_id
),
accounts_with_first_txn AS (
    SELECT COUNT(DISTINCT account_id) AS accounts_with_txn
    FROM first_transactions
),
first_flagged_transactions AS (
    SELECT 
        t.account_id,
        MIN(t.txn_date) AS first_flagged_date
    FROM synthetic_clean_transactions t
    WHERE t.is_flagged = true
    GROUP BY t.account_id
),
accounts_with_flagged AS (
    SELECT COUNT(DISTINCT account_id) AS accounts_with_flagged
    FROM first_flagged_transactions
)
SELECT 
    'account_opened' AS funnel_stage,
    ao.accounts_opened AS account_count,
    ao.accounts_opened AS cumulative_count,
    0.0 AS drop_off_pct
FROM accounts_opened ao
UNION ALL
SELECT 
    'first_transaction' AS funnel_stage,
    awt.accounts_with_txn AS account_count,
    awt.accounts_with_txn AS cumulative_count,
    ROUND(100.0 * (ao.accounts_opened - awt.accounts_with_txn) / ao.accounts_opened, 2) AS drop_off_pct
FROM accounts_with_first_txn awt, accounts_opened ao
UNION ALL
SELECT 
    'first_flagged_transaction' AS funnel_stage,
    awf.accounts_with_flagged AS account_count,
    awf.accounts_with_flagged AS cumulative_count,
    ROUND(100.0 * (awt.accounts_with_txn - awf.accounts_with_flagged) / awt.accounts_with_txn, 2) AS drop_off_pct
FROM accounts_with_flagged awf, accounts_with_first_txn awt
ORDER BY 
    CASE funnel_stage
        WHEN 'account_opened' THEN 1
        WHEN 'first_transaction' THEN 2
        WHEN 'first_flagged_transaction' THEN 3
    END;
