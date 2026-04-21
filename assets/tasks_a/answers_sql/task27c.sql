-- SYNTHETIC DATA — no real financial data
-- Task: SQL-0027 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
WITH SegmentQuartiles AS (
  SELECT
    a.customer_segment,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY db.closing_balance) OVER (PARTITION BY a.customer_segment) AS Q1,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY db.closing_balance) OVER (PARTITION BY a.customer_segment) AS Q3
  FROM synthetic_<variant>_daily_balances AS db
  JOIN synthetic_<variant>_accounts AS a
    ON db.account_id = a.account_id
  WHERE
    db.closing_balance IS NOT NULL
),
SegmentIQR AS (
  SELECT DISTINCT
    customer_segment,
    Q1,
    Q3,
    (Q3 - Q1) AS IQR
  FROM SegmentQuartiles
)
SELECT
  db.account_id,
  a.customer_segment,
  db.balance_date,
  db.closing_balance,
  CASE
    WHEN db.closing_balance < (si.Q1 - 1.5 * si.IQR) THEN TRUE
    WHEN db.closing_balance > (si.Q3 + 1.5 * si.IQR) THEN TRUE
    ELSE FALSE
  END AS is_balance_outlier
FROM synthetic_<variant>_daily_balances AS db
JOIN synthetic_<variant>_accounts AS a
  ON db.account_id = a.account_id
JOIN SegmentIQR AS si
  ON a.customer_segment = si.customer_segment
ORDER BY
  db.account_id,
  db.balance_date;