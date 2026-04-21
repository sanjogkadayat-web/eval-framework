import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-024 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    accounts_df = pd.read_csv(accounts_path, skiprows=1)
    accounts_df["account_open_date"] = pd.to_datetime(accounts_df["account_open_date"], errors="coerce")

    precedence = {"ACTIVE": 1, "SUSPENDED": 2, "CLOSED": 3}
    accounts_df["status_rank"] = accounts_df["account_status"].map(precedence).fillna(99).astype(int)

    accounts_df = accounts_df.sort_values(
        by=["account_id", "account_open_date", "status_rank", "customer_segment", "region"],
        kind="stable",
    ).reset_index(drop=True)

    accounts_df["prev_account_status"] = accounts_df.groupby("account_id")["account_status"].shift(1)
    accounts_df["is_new_status"] = (accounts_df["account_status"] != accounts_df["prev_account_status"]) | (
        accounts_df["prev_account_status"].isna()
    )

    scd2_df = (
        accounts_df[accounts_df["is_new_status"]]
        .drop(columns=["prev_account_status", "is_new_status", "status_rank"])
        .copy()
    )

    scd2_df["effective_start_date"] = scd2_df["account_open_date"]
    scd2_df["next_start_date"] = scd2_df.groupby("account_id")["effective_start_date"].shift(-1)
    scd2_df["effective_end_date"] = scd2_df["next_start_date"] - pd.Timedelta(days=1)
    far_future = pd.Timestamp("2262-04-11")
    scd2_df["effective_end_date"] = scd2_df["effective_end_date"].fillna(far_future)

    return scd2_df[
        ["account_id", "customer_segment", "account_status", "region", "effective_start_date", "effective_end_date"]
    ]
