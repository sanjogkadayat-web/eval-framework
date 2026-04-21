-- SYNTHETIC DATA — no real financial data
-- Task: SQL-004 | Tier: Easy
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
SELECT
  account_id,
  MIN(closing_balance) AS min_closing_balance,
  MAX(closing_balance) AS max_closing_balance
FROM synthetic_<variant>_daily_balances
GROUP BY
  account_id
ORDER BY
  account_id;