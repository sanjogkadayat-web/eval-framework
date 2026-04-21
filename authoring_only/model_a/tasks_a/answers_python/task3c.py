# SYNTHETIC DATA — no real financial data
# Task: PY-003 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path, threshold=0.30):
    """Count nulls per column and raise error if any column exceeds threshold."""
    df = pd.read_csv(transactions_path)
    
    null_counts = df.isnull().sum()
    null_percentages = (null_counts / len(df)) * 100
    
    null_summary = pd.DataFrame({
        'column': null_counts.index,
        'null_count': null_counts.values,
        'null_percentage': null_percentages.values
    })
    
    # Check if any column exceeds threshold
    exceeds_threshold = null_summary[null_summary['null_percentage'] > (threshold * 100)]
    
    if not exceeds_threshold.empty:
        raise ValueError(
            f"Columns exceed null threshold of {threshold*100}%:\n{exceeds_threshold.to_string()}"
        )
    
    return null_summary
