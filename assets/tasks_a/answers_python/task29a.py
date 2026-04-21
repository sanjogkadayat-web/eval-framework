# SYNTHETIC DATA — no real financial data
# Task: PY-029 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
import yaml
from pathlib import Path


def run(accounts_path, transactions_path, balances_path, config_path=None):
    """Run a config-driven pipeline where thresholds and input paths come from YAML."""
    # Load config if provided, otherwise use defaults
    if config_path:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    else:
        config = {
            'min_txn_amount': 100.0,
            'null_threshold': 0.30,
            'days_threshold': 90
        }
    
    # Load data (use paths from config if provided, otherwise use function parameters)
    accounts = pd.read_csv(config.get('accounts_path', accounts_path))
    transactions = pd.read_csv(config.get('transactions_path', transactions_path))
    
    # Apply config-driven filters
    min_amount = config.get('min_txn_amount', 100.0)
    filtered_txns = transactions[transactions['txn_amount'] > min_amount].copy()
    
    # Check null threshold
    null_threshold = config.get('null_threshold', 0.30)
    null_pct = filtered_txns.isnull().sum() / len(filtered_txns)
    
    if (null_pct > null_threshold).any():
        print(f"Warning: Some columns exceed null threshold of {null_threshold}")
    
    # Create summary
    summary = pd.DataFrame({
        'config_key': list(config.keys()),
        'config_value': [str(v) for v in config.values()]
    })
    
    return filtered_txns
