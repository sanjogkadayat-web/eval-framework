import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-002 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame | None:
    """
    Validates that date columns can be parsed as dates and that numeric columns have numeric dtype.
    Raises an error if any validation fails.
    """
    try:
        accounts_df = pd.read_csv(accounts_path, skiprows=1)
        transactions_df = pd.read_csv(transactions_path, skiprows=1)
        balances_df = pd.read_csv(balances_path, skiprows=1)
    except Exception as e:
        raise ValueError(f"Error loading CSV files: {e}")

    # Validate accounts_df
    try:
        accounts_df["account_open_date"] = pd.to_datetime(accounts_df["account_open_date"])
    except Exception as e:
        raise ValueError(f"Error parsing account_open_date in accounts table: {e}")

    # Validate transactions_df
    try:
        transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"])
        transactions_df["txn_amount"] = pd.to_numeric(transactions_df["txn_amount"])
    except Exception as e:
        raise ValueError(f"Error parsing date or numeric columns in transactions table: {e}")

    # Validate daily_balances_df
    try:
        balances_df["balance_date"] = pd.to_datetime(balances_df["balance_date"])
        balances_df["closing_balance"] = pd.to_numeric(balances_df["closing_balance"])
        balances_df["txn_count_day"] = pd.to_numeric(balances_df["txn_count_day"])
    except Exception as e:
        raise ValueError(f"Error parsing date or numeric columns in daily_balances table: {e}")

    print("All date and numeric columns validated successfully.")
    return None