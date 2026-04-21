import pandas as pd
import pytest
from pathlib import Path
import importlib, sys
import numpy as np
from datetime import timedelta

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).parent.parent / "assets" / "tasks_a" / "answers_python"))
task27c = importlib.import_module("task27c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task27c.py | Tests: task27c.py (PY-027)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).parent.parent / "assets" / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def setup_data(tmp_path: Path, variant: str):
    """
    Fixture to create dummy accounts and transactions CSV files for different variants
    to test RFM (Recency, Frequency, Monetary) scoring.
    """
    # Base Accounts Data
    base_accounts_data = {
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 6)],
        "customer_segment": ["RETAIL"] * 5,
        "account_open_date": [
            "2023-01-01", "2023-01-10", "2023-02-01", "2023-03-01", "2023-04-01"
        ],
        "account_status": ["ACTIVE"] * 5,
        "region": ["NORTH"] * 5,
    }
    accounts_df = pd.DataFrame(base_accounts_data)

    # Base Transactions Data
    base_transactions_data = {
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 11)],
        "account_id": [
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", # 3 txns for ACCT_0001
            "SYNTHETIC_ACCT_0002", "SYNTHETIC_ACCT_0002", # 2 txns for ACCT_0002
            "SYNTHETIC_ACCT_0003", # 1 txn for ACCT_0003
            "SYNTHETIC_ACCT_0001", # Another for ACCT_0001
            "SYNTHETIC_ACCT_0004", # 1 txn for ACCT_0004
            "SYNTHETIC_ACCT_0002", # Another for ACCT_0002
            "SYNTHETIC_ACCT_0005"  # 1 txn for ACCT_0005 (no transactions)
        ],
        "txn_date": [
            "2024-11-01", "2024-11-05", "2024-11-10", # ACCT_0001
            "2024-10-01", "2024-10-15", # ACCT_0002
            "2024-09-01", # ACCT_0003
            "2024-11-15", # ACCT_0001 (latest for ACCT_0001)
            "2024-08-01", # ACCT_0004
            "2024-10-20", # ACCT_0002 (latest for ACCT_0002)
            "2024-07-01" # ACCT_0005 (not used in base_transactions_data - this should be a transaction for ACCT_0005)
        ],
        "txn_amount": [
            100.0, 50.0, 200.0, # ACCT_0001
            75.0, 150.0, # ACCT_0002
            300.0, # ACCT_0003
            120.0, # ACCT_0001
            180.0, # ACCT_0004
            90.0, # ACCT_0002
            250.0  # ACCT_0005 (This is a txn for ACCT_0005)
        ],
        "txn_type": ["PURCHASE"] * 11,
        "merchant_category": ["RETAIL"] * 11,
        "channel": ["ONLINE"] * 11,
        "is_flagged": [False] * 11,
    }
    transactions_df = pd.DataFrame(base_transactions_data)

    if variant == "null_heavy":
        # Accounts: ACCT_0001 gets null account_open_date
        accounts_df.loc[0, "account_open_date"] = None
        # Transactions: ACCT_0001's latest txn_date becomes null
        transactions_df.loc[6, "txn_date"] = None # This is ACCT_0001, date 2024-11-15
        transactions_df.loc[0, "txn_amount"] = None # ACCT_0001 txn_amount null
        # ACCT_0005 has no transactions, so fillna should apply.
        # Add a transaction with null account_id to be ignored by RFM calc
        transactions_df = pd.concat([transactions_df, pd.DataFrame({
            "txn_id": ["SYNTHETIC_TXN_NULLACCT"], "account_id": [None],
            "txn_date": ["2024-11-01"], "txn_amount": [500.0], "txn_type": ["PURCHASE"],
            "merchant_category": ["RETAIL"], "channel": ["ONLINE"], "is_flagged": [False]
        })], ignore_index=True)

    elif variant == "duplicate_heavy":
        # Add duplicate transactions for ACCT_0001 to increase frequency and monetary
        dup_txn_1 = transactions_df[transactions_df["txn_id"] == "SYNTHETIC_TXN_000001"].copy()
        dup_txn_2 = transactions_df[transactions_df["txn_id"] == "SYNTHETIC_TXN_000007"].copy()
        transactions_df = pd.concat([transactions_df, dup_txn_1, dup_txn_2], ignore_index=True)

        # Add a duplicate account
        accounts_df = pd.concat([accounts_df, accounts_df.iloc[[0]]], ignore_index=True)

    elif variant == "medium":
        accounts_df = pd.concat([accounts_df] * 10, ignore_index=True)
        transactions_df = pd.concat([transactions_df] * 10, ignore_index=True)
    elif variant == "large":
        accounts_df = pd.concat([accounts_df] * 100, ignore_index=True)
        transactions_df = pd.concat([transactions_df] * 100, ignore_index=True)

    accounts_path = tmp_path / f"synthetic_{variant}_accounts.csv"
    transactions_path = tmp_path / f"synthetic_{variant}_transactions.csv"
    balances_path = tmp_path / f"synthetic_{variant}_daily_balances.csv" # Dummy

    with open(accounts_path, 'w') as f: f.write("H1,H2,H3,H4,H5\n")
    accounts_df.to_csv(accounts_path, mode='a', index=False, header=False)
    
    with open(transactions_path, 'w') as f: f.write("H1,H2,H3,H4,H5,H6,H7,H8\n")
    transactions_df.to_csv(transactions_path, mode='a', index=False, header=False)

    # Create dummy empty files for balances as they are required by the run signature
    pd.DataFrame(columns=[]).to_csv(balances_path, index=False)

    return accounts_path, transactions_path, balances_path


def calculate_expected_rfm(accounts_df_original: pd.DataFrame, transactions_df_original: pd.DataFrame, reference_date: pd.Timestamp) -> pd.DataFrame:
    """
    Helper function to calculate expected RFM scores manually for comparison.
    """
    accounts_df = accounts_df_original.copy()
    transactions_df = transactions_df_original.copy()

    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"])
    transactions_df["txn_amount"] = pd.to_numeric(transactions_df["txn_amount"], errors='coerce')

    # Drop transactions with null account_id or txn_amount before RFM calculation
    transactions_df.dropna(subset=["account_id", "txn_amount"], inplace=True)

    latest_txn_date = transactions_df.groupby("account_id")["txn_date"].max().reset_index()
    latest_txn_date["recency"] = (reference_date - latest_txn_date["txn_date"]).dt.days

    rf_df = transactions_df.groupby("account_id").agg(
        frequency=("txn_id", "count"),
        monetary=("txn_amount", "sum")
    ).reset_index()

    # Merge RFM components
    rfm_df = pd.merge(accounts_df[["account_id", "customer_segment", "region"]], latest_txn_date[["account_id", "recency"]], on="account_id", how="left")
    rfm_df = pd.merge(rfm_df, rf_df, on="account_id", how="left")

    # Fillna logic for accounts with no transactions, matching task27c.py
    max_open_date_days_diff = (reference_date - accounts_df["account_open_date"].dropna()).dt.days.max()
    rfm_df["recency"] = rfm_df["recency"].fillna(max_open_date_days_diff if not accounts_df["account_open_date"].dropna().empty else 0)
    rfm_df["frequency"] = rfm_df["frequency"].fillna(0)
    rfm_df["monetary"] = rfm_df["monetary"].fillna(0)

    return rfm_df


@pytest.mark.parametrize(
    "variant",
    ["clean", "null_heavy", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task27c_run_function(setup_data: tuple[Path, Path, Path], variant: str):
    """
    Tests the run function from task27c.py to calculate RFM scores for each account
    for various dataset variants.
    """
    accounts_path_arg, transactions_path_arg, balances_path = setup_data

    result_df = task27c.run(accounts_path_arg, transactions_path_arg, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty, "Resulting DataFrame should not be empty"

    # Assert expected columns are present
    expected_columns = [
        "account_id", "customer_segment", "region",
        "recency", "frequency", "monetary"
    ]
    assert sorted(list(result_df.columns)) == sorted(expected_columns)

    # Assert dtypes of RFM columns
    assert pd.api.types.is_integer_dtype(result_df["recency"])
    assert pd.api.types.is_integer_dtype(result_df["frequency"])
    assert pd.api.types.is_float_dtype(result_df["monetary"])

    # Load original data to calculate expected values for comparison
    original_accounts_df = pd.read_csv(accounts_path_arg, skiprows=1)
    original_transactions_df = pd.read_csv(transactions_path_arg, skiprows=1)

    # Determine reference_date as in task27c.py
    if not original_transactions_df.empty:
        original_transactions_df["txn_date"] = pd.to_datetime(original_transactions_df["txn_date"], errors='coerce')
        reference_date = original_transactions_df["txn_date"].max() + timedelta(days=1) if not original_transactions_df["txn_date"].dropna().empty else pd.to_datetime("2025-01-01")
    else:
        reference_date = pd.to_datetime("2025-01-01")
    
    expected_rfm_df = calculate_expected_rfm(original_accounts_df, original_transactions_df, reference_date)

    # Sort both for deterministic comparison
    result_df_sorted = result_df.sort_values(by="account_id").reset_index(drop=True)
    expected_rfm_df_sorted = expected_rfm_df.sort_values(by="account_id").reset_index(drop=True)

    pd.testing.assert_frame_equal(
        result_df_sorted,
        expected_rfm_df_sorted,
        check_dtype=False, # Pandas can infer slightly different numeric dtypes
        check_exact=False, # Floating point comparison for monetary
        atol=1e-2 # Absolute tolerance for monetary values
    )

    # Additional specific checks for particular variants if needed
    if variant == "null_heavy":
        # ACCT_0001 had null latest txn_date and null txn_amount.
        # After dropping nulls in the helper `calculate_expected_rfm`, ACCT_0001 will have fewer transactions or no transactions.
        # Let's manually trace ACCT_0001 RFM:
        # Original txns for ACCT_0001: (2024-11-01, 100), (2024-11-05, 50), (2024-11-10, 200), (2024-11-15, 120).
        # Null heavy changes: (2024-11-01, None), (2024-11-15, None)
        # Valid txns: (2024-11-05, 50), (2024-11-10, 200).
        # Latest txn_date for ACCT_0001 (from non-nulls): 2024-11-10.
        # Reference date from original transactions (max of non-null): 2024-11-10 + 1 day = 2024-11-11 (or 2024-10-20 if no valid txn_dates later).
        # The max non-null txn_date is 2024-10-20 (ACCT_0002). So reference_date = 2024-10-21.
        # Recency for ACCT_0001 (latest 2024-11-10): (2024-10-21 - 2024-11-10).dt.days -> negative. This implies issues with the global reference_date. 
        # The `reference_date` should be based on `transactions_df["txn_date"].max()` *after* `errors='coerce'` and *before* `dropna` on account_id, to represent the latest possible date.
        # Let's re-evaluate `reference_date` within the fixture/test scope if needed for consistency.
        # The `reference_date` in task27c.py is defined from the transactions_df *before* any dropping of nulls based on `account_id`.
        # After `pd.to_datetime(transactions_df["txn_date"])`, the max is still 2024-11-15 (even if later marked None for specific row).
        # For null_heavy, `transactions_df.loc[6, "txn_date"] = None` was ACCT_0001, date 2024-11-15. So the max non-null date would be 2024-11-10.
        # Thus `reference_date` will be 2024-11-11.
        # ACCT_0001: latest non-null txn_date is 2024-11-10. Recency = (2024-11-11 - 2024-11-10).dt.days = 1.
        # Frequency: (50, 200) -> 2 txns.
        # Monetary: 50 + 200 = 250.

        acct1_rfm = result_df_sorted[result_df_sorted["account_id"] == "SYNTHETIC_ACCT_0001"]
        assert acct1_rfm["recency"].iloc[0] == 1
        assert acct1_rfm["frequency"].iloc[0] == 2
        assert acct1_rfm["monetary"].iloc[0] == pytest.approx(250.0)

        # ACCT_0005 has no transactions, its recency should be filled with max days diff, and F/M are 0
        acct5_rfm = result_df_sorted[result_df_sorted["account_id"] == "SYNTHETIC_ACCT_0005"]
        assert acct5_rfm["frequency"].iloc[0] == 0
        assert acct5_rfm["monetary"].iloc[0] == pytest.approx(0.0)
        # Recency for ACCT_0005: (2024-11-11 - 2023-04-01).dt.days = 589
        assert acct5_rfm["recency"].iloc[0] == 589

