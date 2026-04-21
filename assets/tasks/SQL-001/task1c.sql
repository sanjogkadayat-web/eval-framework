-- SYNTHETIC DATA — no real financial data
-- Task: SQL-001 | Tier: Easy
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
SELECT
  account_id,
  customer_segment,
  region
FROM synthetic_<variant>_accounts
WHERE
  account_status = 'ACTIVE'
ORDER BY
  account_id;