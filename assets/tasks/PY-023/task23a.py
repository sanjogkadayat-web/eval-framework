# SYNTHETIC DATA — no real financial data
# Task: PY-023 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
import numpy as np
from pathlib import Path


def run(accounts_path, transactions_path, balances_path, output_dir=None):
    """Build an end-to-end pipeline that ingests raw files, validates schema, deduplicates, engineers features, and writes outputs with logging."""
    log = []
    
    # Step 1: Ingest raw files
    accounts = pd.read_csv(accounts_path, comment='#')
    transactions = pd.read_csv(transactions_path, comment='#')
    log.append(f"Loaded accounts: {len(accounts)} rows, transactions: {len(transactions)} rows")
    
    # Step 2: Validate schema
    expected_account_cols = ['account_id', 'customer_segment', 'account_open_date', 'account_status', 'region']
    assert list(accounts.columns) == expected_account_cols, "Accounts schema validation failed"
    log.append("Schema validation passed")
    
    # Step 3: Deduplicate
    accounts_before = len(accounts)
    accounts = accounts.drop_duplicates(subset=['account_id'], keep='first')
    log.append(f"Deduplicated accounts: {accounts_before} -> {len(accounts)}")
    
    transactions_before = len(transactions)
    transactions = transactions.drop_duplicates()
    log.append(f"Deduplicated transactions: {transactions_before} -> {len(transactions)}")
    
    # Step 4: Engineer features
    transactions['txn_date'] = pd.to_datetime(transactions['txn_date'])
    transactions['month'] = transactions['txn_date'].dt.month
    transactions['is_weekend'] = transactions['txn_date'].dt.dayofweek.isin([5, 6])
    transactions['is_flagged_bool'] = transactions['is_flagged'].astype(str).str.lower() == 'true'
    log.append("Feature engineering completed")
    
    # Step 5: Write outputs
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        accounts.to_csv(output_path / 'accounts_clean.csv', index=False)
        transactions.to_csv(output_path / 'transactions_clean.csv', index=False)
        
        with open(output_path / 'pipeline_log.txt', 'w') as f:
            f.write('\n'.join(log))
        
        log.append(f"Outputs written to {output_dir}")
        return None
    
    print('\n'.join(log))
    return transactions
