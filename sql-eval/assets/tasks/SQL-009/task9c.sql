-- SYNTHETIC DATA — no real financial data
-- Task: SQL-009 | Tier: Easy
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
SELECT
  account_id,
  customer_segment,
  COALESCE(region, 'UNKNOWN') AS region
FROM synthetic_<variant>_accounts
ORDER BY
  account_id;