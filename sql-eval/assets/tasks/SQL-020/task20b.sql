-- SYNTHETIC DATA — no real financial data
-- Task: SQL-020 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT
  account_id,
  balance_date,
  closing_balance,
  LAG(closing_balance) OVER (
    PARTITION BY account_id
    ORDER BY balance_date
  ) AS prev_closing_balance,
  closing_balance
    - LAG(closing_balance) OVER (
      PARTITION BY account_id
      ORDER BY balance_date
    ) AS day_over_day_change
FROM synthetic_<variant>_daily_balances
ORDER BY
  account_id,
  balance_date;
