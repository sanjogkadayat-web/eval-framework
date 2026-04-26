# SYNTHETIC DATA — no real financial data
# Task: PY-029 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
import yaml
from pathlib import Path


DEFAULT_CONFIG = """
pipeline_config:
  transactions_filter:
    min_amount_threshold: 500
    allowed_channels:
      - ONLINE
      - MOBILE
      - ATM
"""


def run(accounts_path, transactions_path, balances_path, config_path=None):
    """Run a config-driven pipeline where thresholds and input paths come from YAML."""
    if config_path is not None:
        config = yaml.safe_load(Path(config_path).read_text())
    else:
        config = yaml.safe_load(DEFAULT_CONFIG)

    pipeline_cfg = (config or {}).get('pipeline_config', {})
    tx_filter_cfg = pipeline_cfg.get('transactions_filter', {})

    min_amount = float(tx_filter_cfg.get('min_amount_threshold', 0))
    allowed_channels = list(tx_filter_cfg.get('allowed_channels', []))

    transactions = pd.read_csv(transactions_path, comment='#')
    transactions['txn_amount'] = pd.to_numeric(transactions['txn_amount'], errors='coerce')

    filtered = transactions[transactions['txn_amount'] >= min_amount].copy()
    if allowed_channels:
        filtered = filtered[filtered['channel'].isin(allowed_channels)].copy()

    return filtered
