import pandas as pd
from pathlib import Path
import logging

# SYNTHETIC DATA — no real financial data
# Task: PY-011 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

logger = logging.getLogger(__name__)

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame | None:
    """
    A functional ETL pipeline that loads accounts, validates schema, filters active rows,
    and saves the output to a new CSV file.
    """

    # 1. Load accounts data
    try:
        accounts_df = pd.read_csv(accounts_path, skiprows=1)
        logger.info(f"Loaded {len(accounts_df)} rows from {accounts_path.name}")
    except Exception as e:
        logger.error(f"Error loading accounts CSV: {e}")
        raise

    # 2. Define expected schema for validation
    expected_schema = {
        "account_id": pd.StringDtype(),
        "customer_segment": pd.StringDtype(),
        "account_open_date": "datetime64[ns]",
        "account_status": pd.StringDtype(),
        "region": pd.StringDtype(),
    }

    # 3. Validate schema and convert dtypes
    for col, dtype in expected_schema.items():
        if col not in accounts_df.columns:
            raise ValueError(f"Missing expected column: {col}")
        try:
            accounts_df[col] = accounts_df[col].astype(dtype)
        except Exception as e:
            logger.error(f"Error converting column '{col}' to {dtype}: {e}")
            raise
    logger.info("Schema validated and dtypes converted.")

    # 4. Filter for active accounts
    active_accounts_df = accounts_df[accounts_df["account_status"] == "ACTIVE"].copy()
    logger.info(f"Filtered to {len(active_accounts_df)} active accounts.")

    # 5. Save processed data
    output_path = accounts_path.parent / "processed_active_accounts.csv"
    try:
        active_accounts_df.to_csv(output_path, index=False)
        logger.info(f"Saved processed active accounts to {output_path.name}")
    except Exception as e:
        logger.error(f"Error saving processed accounts CSV: {e}")
        raise

    return None