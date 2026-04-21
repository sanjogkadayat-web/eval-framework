-- SYNTHETIC DATA — no real financial data
-- Task: SQL-026 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH stats AS (
  SELECT
    merchant_category,
    AVG(txn_amount) AS mean_txn_amount,
    STDDEV_POP(txn_amount) AS std_txn_amount
  FROM synthetic_<variant>_transactions
  WHERE txn_amount IS NOT NULL
  GROUP BY
    merchant_category
),
scored AS (
  SELECT
    t.txn_id,
    t.merchant_category,
    t.txn_amount,
    (t.txn_amount - s.mean_txn_amount) / NULLIF(s.std_txn_amount, 0) AS z_score
  FROM synthetic_<variant>_transactions AS t
  LEFT JOIN stats AS s
    ON s.merchant_category = t.merchant_category
)
SELECT
  txn_id,
  merchant_category,
  txn_amount,
  z_score,
  CASE
    WHEN z_score IS NULL THEN FALSE
    WHEN ABS(z_score) > 3 THEN TRUE
    ELSE FALSE
  END AS is_outlier
FROM scored
ORDER BY
  txn_id;
