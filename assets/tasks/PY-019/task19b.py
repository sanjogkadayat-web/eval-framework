import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-019 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    accounts_df = pd.read_csv(accounts_path, skiprows=1)
    accounts_df["account_open_date"] = pd.to_datetime(accounts_df["account_open_date"], errors="coerce")

    precedence = {"ACTIVE": 1, "SUSPENDED": 2, "CLOSED": 3}
    accounts_df["status_rank"] = accounts_df["account_status"].map(precedence).fillna(99).astype(int)

    deduped = (
        accounts_df.sort_values(
            by=["account_id", "status_rank", "account_open_date", "customer_segment", "region"],
            ascending=[True, True, False, True, True],
            kind="stable",
        )
        .drop_duplicates(subset=["account_id"], keep="first")
        .drop(columns=["status_rank"])
        .reset_index(drop=True)
    )

    return deduped
