-- SYNTHETIC DATA — no real financial data
-- Task: SQL-019 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT
  account_id,
  balance_date,
  closing_balance,
  AVG(closing_balance) OVER (
    PARTITION BY account_id
    ORDER BY balance_date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS moving_avg_7day
FROM synthetic_<variant>_daily_balances
ORDER BY
  account_id,
  balance_date;
