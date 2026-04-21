import pandas as pd
from pathlib import Path
import logging
import numpy as np

# SYNTHETIC DATA — no real financial data
# Task: PY-023 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

logger = logging.getLogger(__name__)

def _load_and_validate_accounts(accounts_path: Path) -> pd.DataFrame:
    logger.info(f"Loading accounts data from {accounts_path.name}")
    accounts_df = pd.read_csv(accounts_path, skiprows=1)

    expected_columns = {
        "account_id": pd.StringDtype(),
        "customer_segment": pd.StringDtype(),
        "account_open_date": "datetime64[ns]",
        "account_status": pd.StringDtype(),
        "region": pd.StringDtype(),
    }

    for col, dtype in expected_columns.items():
        if col not in accounts_df.columns:
            raise ValueError(f"Accounts table: Missing expected column: {col}")
        try:
            if "datetime" in str(dtype):
                accounts_df[col] = pd.to_datetime(accounts_df[col])
            else:
                accounts_df[col] = accounts_df[col].astype(dtype)
        except Exception as e:
            raise ValueError(f"Accounts table: Error converting column '{col}' to {dtype}: {e}")
    logger.info("Accounts schema validated and dtypes converted.")
    return accounts_df

def _load_and_validate_transactions(transactions_path: Path) -> pd.DataFrame:
    logger.info(f"Loading transactions data from {transactions_path.name}")
    transactions_df = pd.read_csv(transactions_path, skiprows=1)

    expected_columns = {
        "txn_id": pd.StringDtype(),
        "account_id": pd.StringDtype(),
        "txn_date": "datetime64[ns]",
        "txn_amount": np.float64,
        "txn_type": pd.StringDtype(),
        "merchant_category": pd.StringDtype(),
        "channel": pd.StringDtype(),
        "is_flagged": pd.BooleanDtype(),
    }

    for col, dtype in expected_columns.items():
        if col not in transactions_df.columns:
            raise ValueError(f"Transactions table: Missing expected column: {col}")
        try:
            if "datetime" in str(dtype):
                transactions_df[col] = pd.to_datetime(transactions_df[col])
            elif "float" in str(dtype) or "int" in str(dtype): # Handle numeric types
                transactions_df[col] = pd.to_numeric(transactions_df[col], errors='coerce')
            else:
                transactions_df[col] = transactions_df[col].astype(dtype)
        except Exception as e:
            raise ValueError(f"Transactions table: Error converting column '{col}' to {dtype}: {e}")
    logger.info("Transactions schema validated and dtypes converted.")
    return transactions_df

def _load_and_validate_balances(balances_path: Path) -> pd.DataFrame:
    logger.info(f"Loading daily balances data from {balances_path.name}")
    balances_df = pd.read_csv(balances_path, skiprows=1)

    expected_columns = {
        "account_id": pd.StringDtype(),
        "balance_date": "datetime64[ns]",
        "closing_balance": np.float64,
        "txn_count_day": np.int64,
    }

    for col, dtype in expected_columns.items():
        if col not in balances_df.columns:
            raise ValueError(f"Daily Balances table: Missing expected column: {col}")
        try:
            if "datetime" in str(dtype):
                balances_df[col] = pd.to_datetime(balances_df[col])
            elif "float" in str(dtype) or "int" in str(dtype): # Handle numeric types
                balances_df[col] = pd.to_numeric(balances_df[col], errors='coerce')
            else:
                balances_df[col] = balances_df[col].astype(dtype)
        except Exception as e:
            raise ValueError(f"Daily Balances table: Error converting column '{col}' to {dtype}: {e}")
    logger.info("Daily Balances schema validated and dtypes converted.")
    return balances_df

def _deduplicate_accounts(accounts_df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Deduplicating accounts...")
    initial_rows = len(accounts_df)
    status_precedence = {"ACTIVE": 1, "SUSPENDED": 2, "CLOSED": 3}
    accounts_df["status_rank"] = accounts_df["account_status"].map(status_precedence)

    deduplicated_df = accounts_df.sort_values(
        by=["account_id", "status_rank"], ascending=[True, True]
    ).drop_duplicates(subset=["account_id"], keep="first")

    deduplicated_df = deduplicated_df.drop(columns=["status_rank"])
    logger.info(f"Removed {initial_rows - len(deduplicated_df)} duplicate account rows.")
    return deduplicated_df

def _deduplicate_transactions_and_balances(df: pd.DataFrame, df_name: str) -> pd.DataFrame:
    logger.info(f"Deduplicating {df_name}...")
    initial_rows = len(df)
    deduplicated_df = df.drop_duplicates(keep="first")
    logger.info(f"Removed {initial_rows - len(deduplicated_df)} exact duplicate rows from {df_name}.")
    return deduplicated_df

def _engineer_transaction_features(transactions_df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Engineering transaction features...")
    transactions_df["day_of_week"] = transactions_df["txn_date"].dt.day_name()
    transactions_df["month"] = transactions_df["txn_date"].dt.month
    transactions_df["quarter"] = transactions_df["txn_date"].dt.quarter
    transactions_df["is_weekend"] = transactions_df["txn_date"].dt.dayofweek >= 5
    return transactions_df

def _engineer_balance_features(balances_df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Engineering daily balance features...")
    balances_df = balances_df.sort_values(by=["account_id", "balance_date"]).copy()
    balances_df["rolling_avg_7_obs"] = balances_df.groupby("account_id")["closing_balance"].rolling(
        window=7, min_periods=1
    ).mean().reset_index(level=0, drop=True)
    return balances_df

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> None:
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # 1. Ingest raw files and validate schema
    accounts_df = _load_and_validate_accounts(accounts_path)
    transactions_df = _load_and_validate_transactions(transactions_path)
    balances_df = _load_and_validate_balances(balances_path)

    # 2. Deduplicate
    accounts_df = _deduplicate_accounts(accounts_df)
    transactions_df = _deduplicate_transactions_and_balances(transactions_df, "transactions")
    balances_df = _deduplicate_transactions_and_balances(balances_df, "daily_balances")

    # 3. Engineer features
    transactions_df = _engineer_transaction_features(transactions_df)
    balances_df = _engineer_balance_features(balances_df)

    # 4. Write outputs
    output_dir = Path("./processed_data")
    output_dir.mkdir(exist_ok=True)

    accounts_output_path = output_dir / "conformed_accounts.csv"
    transactions_output_path = output_dir / "conformed_transactions.csv"
    balances_output_path = output_dir / "conformed_daily_balances.csv"

    accounts_df.to_csv(accounts_output_path, index=False)
    logger.info(f"Saved conformed accounts to {accounts_output_path.name}")

    transactions_df.to_csv(transactions_output_path, index=False)
    logger.info(f"Saved conformed transactions to {transactions_output_path.name}")

    balances_df.to_csv(balances_output_path, index=False)
    logger.info(f"Saved conformed daily balances to {balances_output_path.name}")

    logger.info("ETL pipeline completed successfully.")