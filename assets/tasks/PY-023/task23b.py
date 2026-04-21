import logging
from pathlib import Path

import numpy as np
import pandas as pd

# SYNTHETIC DATA — no real financial data
# Task: PY-023 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

logger = logging.getLogger(__name__)


def _require_columns(df: pd.DataFrame, required: list[str], table_name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{table_name}: missing required columns: {missing}")


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    accounts_df = pd.read_csv(accounts_path, skiprows=1)
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    balances_df = pd.read_csv(balances_path, skiprows=1)

    _require_columns(
        accounts_df,
        ["account_id", "customer_segment", "account_open_date", "account_status", "region"],
        "accounts",
    )
    _require_columns(
        transactions_df,
        ["txn_id", "account_id", "txn_date", "txn_amount", "txn_type", "merchant_category", "channel", "is_flagged"],
        "transactions",
    )
    _require_columns(
        balances_df,
        ["account_id", "balance_date", "closing_balance", "txn_count_day"],
        "daily_balances",
    )

    accounts_df["account_open_date"] = pd.to_datetime(accounts_df["account_open_date"], errors="coerce")
    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"], errors="coerce")
    transactions_df["txn_amount"] = pd.to_numeric(transactions_df["txn_amount"], errors="coerce")
    balances_df["balance_date"] = pd.to_datetime(balances_df["balance_date"], errors="coerce")
    balances_df["closing_balance"] = pd.to_numeric(balances_df["closing_balance"], errors="coerce")
    balances_df["txn_count_day"] = pd.to_numeric(balances_df["txn_count_day"], errors="coerce")

    precedence = {"ACTIVE": 1, "SUSPENDED": 2, "CLOSED": 3}
    accounts_df["status_rank"] = accounts_df["account_status"].map(precedence).fillna(99).astype(int)
    accounts_df = (
        accounts_df.sort_values(
            by=["account_id", "status_rank", "account_open_date", "customer_segment", "region"],
            ascending=[True, True, False, True, True],
            kind="stable",
        )
        .drop_duplicates(subset=["account_id"], keep="first")
        .drop(columns=["status_rank"])
        .reset_index(drop=True)
    )

    transactions_df = transactions_df.drop_duplicates(keep="first").copy()
    balances_df = balances_df.drop_duplicates(keep="first").copy()

    transactions_df = transactions_df.sort_values(
        by=["account_id", "txn_date", "txn_id"], kind="stable"
    ).copy()
    transactions_df["day_of_week"] = transactions_df["txn_date"].dt.day_name()
    transactions_df["month"] = transactions_df["txn_date"].dt.month
    transactions_df["quarter"] = transactions_df["txn_date"].dt.quarter
    transactions_df["is_weekend"] = transactions_df["txn_date"].dt.dayofweek >= 5

    balances_df = balances_df.sort_values(by=["account_id", "balance_date"], kind="stable").copy()
    balances_df["rolling_avg_7_obs"] = (
        balances_df.groupby("account_id")["closing_balance"]
        .rolling(window=7, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    output_dir = Path("./processed_data")
    output_dir.mkdir(exist_ok=True)

    accounts_df.to_csv(output_dir / "conformed_accounts.csv", index=False)
    transactions_df.to_csv(output_dir / "conformed_transactions.csv", index=False)
    balances_df.to_csv(output_dir / "conformed_daily_balances.csv", index=False)

    logger.info("Wrote conformed outputs to %s", output_dir.resolve())
    return None
