-- SYNTHETIC DATA — no real financial data
-- Task: SQL-0013 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
SELECT
  a.region,
  SUM(CASE WHEN t.is_flagged = TRUE THEN 1 ELSE 0 END) AS flagged_transaction_count,
  SUM(CASE WHEN t.is_flagged = FALSE THEN 1 ELSE 0 END) AS unflagged_transaction_count
FROM synthetic_<variant>_accounts AS a
INNER JOIN synthetic_<variant>_transactions AS t
  ON a.account_id = t.account_id
GROUP BY
  a.region
ORDER BY
  a.region;