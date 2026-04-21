-- SYNTHETIC DATA — no real financial data
-- Task: SQL-011 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
SELECT
  a.region,
  SUM(t.txn_amount) AS total_txn_amount,
  AVG(db.closing_balance) AS average_closing_balance
FROM synthetic_<variant>_accounts AS a
LEFT JOIN synthetic_<variant>_transactions AS t
  ON a.account_id = t.account_id
LEFT JOIN synthetic_<variant>_daily_balances AS db
  ON a.account_id = db.account_id
GROUP BY
  a.region
ORDER BY
  a.region;