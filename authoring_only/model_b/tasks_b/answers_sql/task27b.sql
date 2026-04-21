-- SYNTHETIC DATA — no real financial data
-- Task: SQL-027 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH segment_quartiles AS (
  SELECT
    a.customer_segment,
    QUANTILE_CONT(b.closing_balance, 0.25) AS q1,
    QUANTILE_CONT(b.closing_balance, 0.75) AS q3
  FROM synthetic_<variant>_accounts AS a
  INNER JOIN synthetic_<variant>_daily_balances AS b
    ON b.account_id = a.account_id
  WHERE a.customer_segment IS NOT NULL
    AND b.closing_balance IS NOT NULL
  GROUP BY
    a.customer_segment
),
bounds AS (
  SELECT
    b.account_id,
    b.balance_date,
    a.customer_segment,
    b.closing_balance,
    q.q1,
    q.q3,
    (q.q3 - q.q1) AS iqr,
    (q.q1 - 1.5 * (q.q3 - q.q1)) AS lower_bound,
    (q.q3 + 1.5 * (q.q3 - q.q1)) AS upper_bound
  FROM synthetic_<variant>_daily_balances AS b
  INNER JOIN synthetic_<variant>_accounts AS a
    ON a.account_id = b.account_id
  LEFT JOIN segment_quartiles AS q
    ON q.customer_segment = a.customer_segment
)
SELECT
  account_id,
  balance_date,
  customer_segment,
  closing_balance,
  lower_bound,
  upper_bound,
  CASE
    WHEN closing_balance IS NULL OR iqr IS NULL THEN FALSE
    WHEN closing_balance < lower_bound OR closing_balance > upper_bound THEN TRUE
    ELSE FALSE
  END AS is_outlier
FROM bounds
ORDER BY
  customer_segment,
  account_id,
  balance_date;
