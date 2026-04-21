-- SYNTHETIC DATA — no real financial data
-- Task: SQL-0030 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
WITH raw_accounts AS (
  SELECT
    account_id,
    customer_segment,
    account_open_date,
    account_status,
    region
  FROM synthetic_<variant>_accounts
),
validated_accounts AS (
  SELECT
    account_id,
    customer_segment,
    account_open_date,
    account_status,
    region
  FROM raw_accounts
  WHERE
    account_id IS NOT NULL AND customer_segment IS NOT NULL AND account_open_date IS NOT NULL AND account_status IS NOT NULL AND region IS NOT NULL
),
deduplicated_accounts AS (
  SELECT
    account_id,
    customer_segment,
    account_open_date,
    account_status,
    region
  FROM (
    SELECT
      *,
      ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY account_open_date) AS rn
    FROM validated_accounts
  )
  WHERE
    rn = 1
)
SELECT
  account_id,
  customer_segment,
  account_open_date,
  account_status,
  region
FROM deduplicated_accounts
ORDER BY
  account_id;