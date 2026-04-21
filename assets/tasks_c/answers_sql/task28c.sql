-- SYNTHETIC DATA — no real financial data
-- Task: SQL-0028 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
WITH account_opened AS (
  SELECT
    account_id,
    account_open_date
  FROM synthetic_<variant>_accounts
),
first_transaction AS (
  SELECT
    account_id,
    MIN(txn_date) AS first_txn_date
  FROM synthetic_<variant>_transactions
  GROUP BY
    account_id
),
first_flagged_transaction AS (
  SELECT
    account_id,
    MIN(txn_date) AS first_flagged_txn_date
  FROM synthetic_<variant>_transactions
  WHERE
    is_flagged = TRUE
  GROUP BY
    account_id
)
SELECT
  ao.account_id,
  ao.account_open_date,
  ft.first_txn_date,
  fft.first_flagged_txn_date,
  CASE
    WHEN ft.first_txn_date IS NOT NULL THEN (
      JULIANDAY(ft.first_txn_date) - JULIANDAY(ao.account_open_date)
    )
    ELSE NULL
  END AS days_to_first_txn,
  CASE
    WHEN fft.first_flagged_txn_date IS NOT NULL THEN (
      JULIANDAY(fft.first_flagged_txn_date) - JULIANDAY(ft.first_txn_date)
    )
    ELSE NULL
  END AS days_to_first_flagged_txn
FROM account_opened AS ao
LEFT JOIN first_transaction AS ft
  ON ao.account_id = ft.account_id
LEFT JOIN first_flagged_transaction AS fft
  ON ao.account_id = fft.account_id
ORDER BY
  ao.account_id;