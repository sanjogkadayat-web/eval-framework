# SYNTHETIC DATA — no real financial data
# Task: PY-010 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Flag transactions whose channel is not in the allowed set."""
    df = pd.read_csv(transactions_path, comment='#')
    
    allowed_channels = {'ATM', 'BRANCH', 'MOBILE', 'ONLINE'}
    
    df['invalid_channel'] = ~df['channel'].isin(allowed_channels)
    
    return df
