import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-010 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Flags transactions whose channel is not in the allowed set {ATM, BRANCH, MOBILE, ONLINE}.
    """
    transactions_df = pd.read_csv(transactions_path, skiprows=1)

    allowed_channels = {"ATM", "BRANCH", "MOBILE", "ONLINE"}
    transactions_df["is_invalid_channel"] = ~transactions_df["channel"].isin(allowed_channels)

    return transactions_df