# SYNTHETIC DATA — no real financial data
# Task: PY-026 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Compute funnel drop-off from account creation to first transaction to first flagged transaction."""
    accounts = pd.read_csv(accounts_path, comment='#')
    transactions = pd.read_csv(transactions_path, comment='#')
    
    # Convert dates
    transactions['txn_date'] = pd.to_datetime(transactions['txn_date'])
    transactions['is_flagged_bool'] = transactions['is_flagged'].astype(str).str.lower() == 'true'
    
    # Stage 1: Account creation
    total_accounts = len(accounts['account_id'].unique())
    
    # Stage 2: First transaction
    accounts_with_txn = transactions['account_id'].nunique()
    
    # Stage 3: First flagged transaction
    accounts_with_flagged = transactions[transactions['is_flagged_bool'] == True]['account_id'].nunique()
    
    # Build funnel
    funnel = pd.DataFrame({
        'stage': ['account_created', 'first_transaction', 'first_flagged_transaction'],
        'account_count': [total_accounts, accounts_with_txn, accounts_with_flagged],
        'drop_off_count': [0, total_accounts - accounts_with_txn, accounts_with_txn - accounts_with_flagged],
        'drop_off_pct': [
            0.0,
            100.0 * (total_accounts - accounts_with_txn) / total_accounts if total_accounts > 0 else 0,
            100.0 * (accounts_with_txn - accounts_with_flagged) / accounts_with_txn if accounts_with_txn > 0 else 0
        ]
    })
    
    return funnel
