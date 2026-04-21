import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-006 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Cleans string columns in the accounts table by stripping whitespace and normalizing
    'region' and 'customer_segment' to uppercase.
    """
    accounts_df = pd.read_csv(accounts_path, skiprows=1)

    # Strip whitespace from all string columns
    for col in accounts_df.select_dtypes(include=['object']).columns:
        accounts_df[col] = accounts_df[col].str.strip()

    # Normalize 'region' and 'customer_segment' to uppercase
    if 'region' in accounts_df.columns:
        accounts_df['region'] = accounts_df['region'].str.upper()
    if 'customer_segment' in accounts_df.columns:
        accounts_df['customer_segment'] = accounts_df['customer_segment'].str.upper()

    return accounts_df