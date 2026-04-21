-- SYNTHETIC DATA — no real financial data
-- Task: SQL-022 | Tier: Medium
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH accounts_by_region AS (
  SELECT
    region,
    COUNT(*) AS account_count
  FROM synthetic_<variant>_accounts
  GROUP BY
    region
),
flagged_txns_by_region AS (
  SELECT
    a.region,
    SUM(CASE WHEN COALESCE(t.is_flagged, FALSE) = TRUE THEN 1 ELSE 0 END) AS flagged_txn_count
  FROM synthetic_<variant>_accounts AS a
  INNER JOIN synthetic_<variant>_transactions AS t
    ON t.account_id = a.account_id
  GROUP BY
    a.region
),
avg_balance_by_region AS (
  SELECT
    a.region,
    AVG(b.closing_balance) AS avg_closing_balance
  FROM synthetic_<variant>_accounts AS a
  INNER JOIN synthetic_<variant>_daily_balances AS b
    ON b.account_id = a.account_id
  GROUP BY
    a.region
)
SELECT
  COALESCE(ac.region, ft.region, ab.region) AS region,
  ac.account_count,
  ft.flagged_txn_count,
  ab.avg_closing_balance
FROM accounts_by_region AS ac
FULL OUTER JOIN flagged_txns_by_region AS ft
  ON ft.region = ac.region
FULL OUTER JOIN avg_balance_by_region AS ab
  ON ab.region = COALESCE(ac.region, ft.region)
ORDER BY
  region;
