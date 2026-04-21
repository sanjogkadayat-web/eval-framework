-- SYNTHETIC DATA — no real financial data
-- Task: SQL-021 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH w AS (
  SELECT
    account_id,
    balance_date,
    closing_balance,
    FIRST_VALUE(closing_balance) OVER (
      PARTITION BY account_id
      ORDER BY balance_date
      ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS first_closing_balance,
    LAST_VALUE(closing_balance) OVER (
      PARTITION BY account_id
      ORDER BY balance_date
      ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS last_closing_balance,
    ROW_NUMBER() OVER (
      PARTITION BY account_id
      ORDER BY balance_date
    ) AS rn
  FROM synthetic_<variant>_daily_balances
)
SELECT
  account_id,
  first_closing_balance,
  last_closing_balance
FROM w
WHERE rn = 1
ORDER BY
  account_id;
