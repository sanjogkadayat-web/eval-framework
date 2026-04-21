-- SYNTHETIC DATA — no real financial data
-- Task: SQL-008 | Tier: Easy
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
SELECT
  STRFTIME(txn_date, '%Y-%m') AS transaction_year_month,
  COUNT(txn_id) AS transaction_count
FROM synthetic_<variant>_transactions
GROUP BY
  transaction_year_month
ORDER BY
  transaction_year_month;