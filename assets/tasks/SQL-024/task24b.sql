-- SYNTHETIC DATA — no real financial data
-- Task: SQL-024 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH ranked AS (
  SELECT
    a.*,
    ROW_NUMBER() OVER (
      PARTITION BY a.account_id
      ORDER BY
        CASE a.account_status
          WHEN 'ACTIVE' THEN 1
          WHEN 'SUSPENDED' THEN 2
          WHEN 'CLOSED' THEN 3
          ELSE 4
        END,
        a.account_open_date DESC NULLS LAST,
        a.customer_segment,
        a.region
    ) AS rn
  FROM synthetic_<variant>_accounts AS a
)
SELECT
  account_id,
  customer_segment,
  account_open_date,
  account_status,
  region
FROM ranked
WHERE rn = 1
ORDER BY
  account_id;
