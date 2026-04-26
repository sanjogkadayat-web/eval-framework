-- SYNTHETIC DATA — no real financial data
-- Task: SQL-0012 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
SELECT
  t.txn_id,
  t.account_id,
  a.account_status,
  t.is_flagged,
  CASE
    WHEN a.account_status = 'ACTIVE' AND t.is_flagged = TRUE THEN 'active-high-risk'
    WHEN a.account_status = 'ACTIVE' AND t.is_flagged = FALSE THEN 'active-normal'
    WHEN a.account_status IN ('CLOSED', 'SUSPENDED') THEN 'inactive'
    ELSE 'unknown'
  END AS transaction_classification
FROM synthetic_<variant>_transactions AS t
INNER JOIN synthetic_<variant>_accounts AS a
  ON t.account_id = a.account_id
ORDER BY
  t.txn_id;