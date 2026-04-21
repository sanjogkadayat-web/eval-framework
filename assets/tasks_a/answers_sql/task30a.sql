-- SYNTHETIC DATA — no real financial data
-- Task: SQL-030 | Tier: Hard
-- Tables: synthetic_<variant>_accounts, synthetic_<variant>_transactions, synthetic_<variant>_daily_balances
-- Compatible with: DuckDB

WITH raw_accounts AS (
    SELECT 
        account_id,
        customer_segment,
        account_open_date,
        account_status,
        region
    FROM synthetic_clean_accounts
),
validated_accounts AS (
    SELECT 
        account_id,
        customer_segment,
        account_open_date,
        account_status,
        region,
        CASE 
            WHEN account_id IS NULL THEN 'missing_account_id'
            WHEN customer_segment IS NULL THEN 'missing_customer_segment'
            WHEN account_open_date IS NULL THEN 'missing_account_open_date'
            WHEN account_status IS NULL THEN 'missing_account_status'
            ELSE 'valid'
        END AS validation_status
    FROM raw_accounts
),
deduplicated_accounts AS (
    SELECT 
        account_id,
        customer_segment,
        account_open_date,
        account_status,
        region,
        validation_status,
        ROW_NUMBER() OVER (
            PARTITION BY account_id 
            ORDER BY 
                CASE 
                    WHEN account_status = 'ACTIVE' THEN 1
                    WHEN account_status = 'SUSPENDED' THEN 2
                    WHEN account_status = 'CLOSED' THEN 3
                    ELSE 4
                END,
                account_open_date
        ) AS rn
    FROM validated_accounts
    WHERE validation_status = 'valid'
),
conformed_accounts AS (
    SELECT 
        account_id,
        UPPER(TRIM(customer_segment)) AS customer_segment,
        account_open_date,
        UPPER(TRIM(account_status)) AS account_status,
        COALESCE(UPPER(TRIM(region)), 'UNKNOWN') AS region,
        CURRENT_TIMESTAMP AS etl_timestamp
    FROM deduplicated_accounts
    WHERE rn = 1
)
SELECT 
    account_id,
    customer_segment,
    account_open_date,
    account_status,
    region,
    etl_timestamp
FROM conformed_accounts
ORDER BY account_id;
