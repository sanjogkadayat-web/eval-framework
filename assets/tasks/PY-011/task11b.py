import pandas as pd
from pathlib import Path
import logging

# SYNTHETIC DATA — no real financial data
# Task: PY-011 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

logger = logging.getLogger(__name__)


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame | None:
    accounts_df = pd.read_csv(accounts_path, skiprows=1)

    expected_cols = [
        "account_id",
        "customer_segment",
        "account_open_date",
        "account_status",
        "region",
    ]
    missing = [c for c in expected_cols if c not in accounts_df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    accounts_df["account_open_date"] = pd.to_datetime(accounts_df["account_open_date"], errors="raise")

    active_df = accounts_df[accounts_df["account_status"] == "ACTIVE"].copy()

    output_path = Path(accounts_path).parent / "processed_active_accounts.csv"
    active_df.to_csv(output_path, index=False)
    logger.info("Saved processed active accounts to %s", output_path.name)

    return None
