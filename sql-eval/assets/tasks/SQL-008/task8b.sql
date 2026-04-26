-- SYNTHETIC DATA — no real financial data
-- Task: SQL-008 | Tier: Easy
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH month_counts AS (
  SELECT
    DATE_TRUNC('month', txn_date)::DATE AS year_month,
    COUNT(*) AS txn_count
  FROM synthetic_<variant>_transactions
  GROUP BY 1
)
SELECT
  year_month,
  txn_count
FROM month_counts
ORDER BY year_month;
