import logging
from pathlib import Path

import pandas as pd
import yaml

# SYNTHETIC DATA — no real financial data
# Task: PY-029 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

logger = logging.getLogger(__name__)


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    config_str = """
    pipeline_config:
      transactions_filter:
        min_amount_threshold: 500
        allowed_channels:
          - ONLINE
          - MOBILE
          - ATM
    """

    config = yaml.safe_load(config_str)
    tx_cfg = (config or {}).get("pipeline_config", {}).get("transactions_filter", {})

    min_amount = float(tx_cfg.get("min_amount_threshold", 0))
    allowed_channels = set(tx_cfg.get("allowed_channels", []))
    logger.info("Config loaded: min_amount_threshold=%s allowed_channels=%s", min_amount, sorted(allowed_channels))

    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    transactions_df["txn_amount"] = pd.to_numeric(transactions_df["txn_amount"], errors="coerce")

    filtered = transactions_df[transactions_df["txn_amount"].ge(min_amount)].copy()
    if allowed_channels:
        filtered = filtered[filtered["channel"].isin(allowed_channels)].copy()

    return filtered
