-- SYNTHETIC DATA — no real financial data
-- Task: SQL-0026 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
WITH category_stats AS (
  SELECT
    merchant_category,
    AVG(txn_amount) AS mean_txn_amount,
    STDDEV(txn_amount) AS stddev_txn_amount
  FROM synthetic_<variant>_transactions
  GROUP BY
    merchant_category
),
 outlier_detection AS (
  SELECT
    t.txn_id,
    t.account_id,
    t.txn_date,
    t.txn_amount,
    t.merchant_category,
    (t.txn_amount - cs.mean_txn_amount) / cs.stddev_txn_amount AS z_score,
    CASE
      WHEN ABS((t.txn_amount - cs.mean_txn_amount) / cs.stddev_txn_amount) > 3 THEN TRUE
      ELSE FALSE
    END AS is_outlier
  FROM synthetic_<variant>_transactions AS t
  INNER JOIN category_stats AS cs
    ON t.merchant_category = cs.merchant_category
  WHERE
    cs.stddev_txn_amount IS NOT NULL AND cs.stddev_txn_amount != 0
)
SELECT
  txn_id,
  account_id,
  txn_date,
  txn_amount,
  merchant_category,
  z_score,
  is_outlier
FROM outlier_detection
ORDER BY
  txn_id;