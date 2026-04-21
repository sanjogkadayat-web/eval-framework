-- SYNTHETIC DATA — no real financial data
-- Task: SQL-013 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

SELECT
  COALESCE(a.region, 'UNKNOWN') AS region,
  SUM(CASE WHEN COALESCE(t.is_flagged, FALSE) = TRUE THEN 1 ELSE 0 END) AS flagged_txn_count,
  SUM(CASE WHEN COALESCE(t.is_flagged, FALSE) = FALSE THEN 1 ELSE 0 END) AS unflagged_txn_count
FROM synthetic_<variant>_transactions AS t
LEFT JOIN synthetic_<variant>_accounts AS a
  ON a.account_id = t.account_id
GROUP BY
  COALESCE(a.region, 'UNKNOWN')
ORDER BY
  region;
