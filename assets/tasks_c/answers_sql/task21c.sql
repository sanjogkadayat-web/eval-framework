-- SYNTHETIC DATA — no real financial data
-- Task: SQL-0021 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
SELECT DISTINCT
  account_id,
  FIRST_VALUE(closing_balance) OVER (PARTITION BY account_id ORDER BY balance_date) AS first_closing_balance,
  LAST_VALUE(closing_balance) OVER (PARTITION BY account_id ORDER BY balance_date) AS last_closing_balance
FROM synthetic_<variant>_daily_balances
ORDER BY
  account_id;