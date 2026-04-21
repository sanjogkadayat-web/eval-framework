-- SYNTHETIC DATA — no real financial data
-- Task: SQL-026 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH category_stats AS (
    SELECT 
        merchant_category,
        AVG(txn_amount) AS mean_amount,
        STDDEV(txn_amount) AS stddev_amount
    FROM synthetic_clean_transactions
    WHERE txn_amount IS NOT NULL AND merchant_category IS NOT NULL
    GROUP BY merchant_category
    HAVING STDDEV(txn_amount) > 0
)
SELECT 
    t.txn_id,
    t.account_id,
    t.txn_date,
    t.txn_amount,
    t.merchant_category,
    (t.txn_amount - cs.mean_amount) / cs.stddev_amount AS z_score,
    CASE 
        WHEN ABS((t.txn_amount - cs.mean_amount) / cs.stddev_amount) > 3 THEN true
        ELSE false
    END AS is_outlier
FROM synthetic_clean_transactions t
INNER JOIN category_stats cs ON t.merchant_category = cs.merchant_category
WHERE t.txn_amount IS NOT NULL
ORDER BY t.txn_id;
