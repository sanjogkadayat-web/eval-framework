# SYNTHETIC DATA — no real financial data
# Task: PY-022 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Generate an audit log DataFrame capturing each transformation step and row counts before/after."""
    audit_log = []
    
    # Step 1: Load accounts
    accounts = pd.read_csv(accounts_path, comment='#')
    audit_log.append({
        'step': 'load_accounts',
        'action': 'load',
        'rows_before': 0,
        'rows_after': len(accounts)
    })
    
    # Step 2: Filter active accounts
    active_accounts = accounts[accounts['account_status'] == 'ACTIVE']
    audit_log.append({
        'step': 'filter_active',
        'action': 'filter',
        'rows_before': len(accounts),
        'rows_after': len(active_accounts)
    })
    
    # Step 3: Load transactions
    transactions = pd.read_csv(transactions_path, comment='#')
    audit_log.append({
        'step': 'load_transactions',
        'action': 'load',
        'rows_before': 0,
        'rows_after': len(transactions)
    })
    
    # Step 4: Merge accounts and transactions
    merged = transactions.merge(active_accounts, on='account_id', how='inner')
    audit_log.append({
        'step': 'merge_accounts_transactions',
        'action': 'merge',
        'rows_before': len(transactions),
        'rows_after': len(merged)
    })
    
    audit_df = pd.DataFrame(audit_log)
    
    return audit_df
