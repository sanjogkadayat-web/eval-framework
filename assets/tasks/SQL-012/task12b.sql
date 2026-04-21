-- SYNTHETIC DATA — no real financial data
-- Task: SQL-012 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT
  t.txn_id,
  t.account_id,
  a.account_status,
  t.is_flagged,
  CASE
    WHEN a.account_status = 'ACTIVE' AND COALESCE(t.is_flagged, FALSE) = TRUE THEN 'active-high-risk'
    WHEN a.account_status = 'ACTIVE' THEN 'active-normal'
    ELSE 'inactive'
  END AS txn_classification
FROM synthetic_<variant>_transactions AS t
LEFT JOIN synthetic_<variant>_accounts AS a
  ON a.account_id = t.account_id
ORDER BY
  t.txn_id;
