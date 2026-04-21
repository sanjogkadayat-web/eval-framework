-- SYNTHETIC DATA — no real financial data
-- Task: SQL-018 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT 
    txn_id,
    account_id,
    txn_date,
    txn_amount,
    SUM(txn_amount) OVER (
        PARTITION BY account_id 
        ORDER BY txn_date, txn_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total
FROM synthetic_clean_transactions
WHERE txn_amount IS NOT NULL AND account_id IS NOT NULL
ORDER BY account_id, txn_date, txn_id;
