-- SYNTHETIC DATA — no real financial data
-- Task: SQL-028 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH per_account AS (
  SELECT
    a.account_id,
    MIN(t.txn_date) AS first_transaction_date,
    MIN(CASE WHEN COALESCE(t.is_flagged, FALSE) = TRUE THEN t.txn_date ELSE NULL END) AS first_flagged_transaction_date
  FROM synthetic_<variant>_accounts AS a
  LEFT JOIN synthetic_<variant>_transactions AS t
    ON t.account_id = a.account_id
  GROUP BY
    a.account_id
),
funnel AS (
  SELECT
    COUNT(*) AS accounts_opened,
    SUM(CASE WHEN first_transaction_date IS NOT NULL THEN 1 ELSE 0 END) AS accounts_with_first_transaction,
    SUM(CASE WHEN first_flagged_transaction_date IS NOT NULL THEN 1 ELSE 0 END) AS accounts_with_first_flagged_transaction
  FROM per_account
)
SELECT
  accounts_opened,
  accounts_with_first_transaction,
  accounts_with_first_flagged_transaction,
  ROUND(
    1.0 - (accounts_with_first_transaction::DOUBLE / NULLIF(accounts_opened, 0)),
    4
  ) AS dropoff_opened_to_first_txn,
  ROUND(
    1.0 - (accounts_with_first_flagged_transaction::DOUBLE / NULLIF(accounts_with_first_transaction, 0)),
    4
  ) AS dropoff_first_txn_to_first_flagged_txn
FROM funnel;
