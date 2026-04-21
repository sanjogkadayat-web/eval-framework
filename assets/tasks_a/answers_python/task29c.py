import pandas as pd
from pathlib import Path
import yaml
import logging

# SYNTHETIC DATA — no real financial data
# Task: PY-029 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

logger = logging.getLogger(__name__)

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Runs a config-driven pipeline where thresholds and input paths come from a YAML configuration.
    This example filters transactions based on amount and channel, as defined in the config.
    """

    # Default YAML configuration (can be loaded from a file in a real scenario)
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
    pipeline_config = config.get("pipeline_config", {})
    transactions_filter_config = pipeline_config.get("transactions_filter", {})

    min_amount_threshold = transactions_filter_config.get("min_amount_threshold", 0)
    allowed_channels = transactions_filter_config.get("allowed_channels", [])

    logger.info(f"Config loaded: min_amount_threshold={min_amount_threshold}, allowed_channels={allowed_channels}")

    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    initial_rows = len(transactions_df)
    logger.info(f"Loaded {initial_rows} transactions.")

    # Filter by amount threshold
    filtered_by_amount_df = transactions_df[transactions_df["txn_amount"] >= min_amount_threshold].copy()
    logger.info(f"Filtered by amount: {len(filtered_by_amount_df)} rows remaining (dropped {initial_rows - len(filtered_by_amount_df)}).")

    # Filter by allowed channels
    filtered_df = filtered_by_amount_df[filtered_by_amount_df["channel"].isin(allowed_channels)].copy()
    logger.info(f"Filtered by channel: {len(filtered_df)} rows remaining (dropped {len(filtered_by_amount_df) - len(filtered_df)}).")

    return filtered_df