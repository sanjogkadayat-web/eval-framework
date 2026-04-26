-- SYNTHETIC DATA — no real financial data
-- Task: SQL-0022 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB
WITH account_counts AS (
  SELECT
    region,
    COUNT(account_id) AS total_account_count
  FROM synthetic_<variant>_accounts
  GROUP BY
    region
),
flagged_txn_counts AS (
  SELECT
    a.region,
    COUNT(t.txn_id) AS total_flagged_txn_count
  FROM synthetic_<variant>_accounts AS a
  INNER JOIN synthetic_<variant>_transactions AS t
    ON a.account_id = t.account_id
  WHERE
    t.is_flagged = TRUE
  GROUP BY
    a.region
),
average_balances AS (
  SELECT
    a.region,
    AVG(db.closing_balance) AS average_closing_balance
  FROM synthetic_<variant>_accounts AS a
  INNER JOIN synthetic_<variant>_daily_balances AS db
    ON a.account_id = db.account_id
  GROUP BY
    a.region
)
SELECT
  ac.region,
  ac.total_account_count,
  ftc.total_flagged_txn_count,
  ab.average_closing_balance
FROM account_counts AS ac
LEFT JOIN flagged_txn_counts AS ftc
  ON ac.region = ftc.region
LEFT JOIN average_balances AS ab
  ON ac.region = ab.region
ORDER BY
  ac.region;