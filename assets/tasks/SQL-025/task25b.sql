-- SYNTHETIC DATA — no real financial data
-- Task: SQL-025 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH issues AS (
  SELECT
    t.txn_id,
    t.account_id,
    CASE
      WHEN t.account_id IS NULL THEN 'NULL_ACCOUNT_ID'
      WHEN a.account_id IS NULL THEN 'MISSING_ACCOUNT'
      ELSE NULL
    END AS issue_type
  FROM synthetic_<variant>_transactions AS t
  LEFT JOIN synthetic_<variant>_accounts AS a
    ON a.account_id = t.account_id
)
SELECT
  txn_id,
  account_id,
  issue_type
FROM issues
WHERE issue_type IS NOT NULL
ORDER BY
  txn_id;
