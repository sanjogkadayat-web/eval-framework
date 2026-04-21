-- SYNTHETIC DATA — no real financial data
-- Task: SQL-030 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH raw_accounts AS (
  SELECT
    *
  FROM synthetic_<variant>_accounts
),
validated AS (
  SELECT
    account_id,
    customer_segment,
    account_open_date::DATE AS account_open_date,
    account_status,
    region
  FROM raw_accounts
  WHERE account_id IS NOT NULL
    AND account_open_date IS NOT NULL
    AND account_status IN ('ACTIVE', 'SUSPENDED', 'CLOSED')
    AND customer_segment IN ('RETAIL', 'SMALL_BIZ', 'WEALTH', 'STUDENT')
),
deduped AS (
  SELECT
    v.*,
    ROW_NUMBER() OVER (
      PARTITION BY v.account_id
      ORDER BY
        CASE v.account_status
          WHEN 'ACTIVE' THEN 1
          WHEN 'SUSPENDED' THEN 2
          WHEN 'CLOSED' THEN 3
          ELSE 4
        END,
        v.account_open_date DESC NULLS LAST,
        v.customer_segment,
        v.region
    ) AS rn
  FROM validated AS v
),
conformed AS (
  SELECT
    account_id,
    customer_segment,
    account_open_date,
    account_status,
    COALESCE(region, 'UNKNOWN') AS region
  FROM deduped
  WHERE rn = 1
)
SELECT
  account_id,
  customer_segment,
  account_open_date,
  account_status,
  region
FROM conformed
ORDER BY
  account_id;
