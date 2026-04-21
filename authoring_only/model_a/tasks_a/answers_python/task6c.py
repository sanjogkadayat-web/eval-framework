# SYNTHETIC DATA — no real financial data
# Task: PY-006 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Clean string columns by stripping whitespace and normalizing to uppercase."""
    df = pd.read_csv(accounts_path)
    
    # Strip whitespace from all string columns
    string_columns = df.select_dtypes(include=['object']).columns
    for col in string_columns:
        df[col] = df[col].astype(str).str.strip()
    
    # Normalize region and customer_segment to uppercase
    if 'region' in df.columns:
        df['region'] = df['region'].str.upper()
    if 'customer_segment' in df.columns:
        df['customer_segment'] = df['customer_segment'].str.upper()
    
    return df
