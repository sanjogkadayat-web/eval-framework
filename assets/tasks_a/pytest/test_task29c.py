import pandas as pd
import pytest
from pathlib import Path
import importlib, sys
import numpy as np

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).parent.parent / "assets" / "tasks_a" / "answers_python"))
task29c = importlib.import_module("task29c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task29c.py | Tests: task29c.py (PY-029)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).parent.parent / "assets" / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def transactions_path(tmp_path: Path, variant: str):
    """
    Fixture to create dummy transactions CSV files for different variants
    to test config-driven filtering based on txn_amount and channel.
    """
    base_data = {
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 16)],
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 16)],
        "txn_date": [f"2023-01-{i:02d}" for i in range(1, 16)],
        "txn_amount": [
            100.0, 600.0, 450.0, 700.0, 200.0, 800.0, 300.0, 900.0, 400.0, 1000.0, # Various amounts
            50.0, # Below threshold
            550.0, # Above threshold
            499.0, # Just below threshold
            500.0, # On threshold
            650.0  # Above threshold
        ],
        "txn_type": ["PURCHASE"] * 15,
        "merchant_category": ["RETAIL"] * 15,
        "channel": [
            "ONLINE", "BRANCH", "MOBILE", "ATM", "BRANCH",
            "ONLINE", "KIOSK", "MOBILE", "ONLINE", "ATM", # Various channels
            "ONLINE", "BRANCH", "MOBILE", "ATM", "ONLINE"
        ],
        "is_flagged": [False] * 15,
    }
    df = pd.DataFrame(base_data)

    if variant == "null_heavy":
        df.loc[df["txn_id"] == "SYNTHETIC_TXN_000002", "txn_amount"] = None  # 600.0 -> None
        df.loc[df["txn_id"] == "SYNTHETIC_TXN_000003", "channel"] = None      # MOBILE -> None
        df.loc[df["txn_id"] == "SYNTHETIC_TXN_000010", "txn_amount"] = "invalid" # 1000.0 -> invalid string

    elif variant == "duplicate_heavy":
        # Add duplicates of transactions that should and should not pass filters
        dup_passing_txn = df[df["txn_id"] == "SYNTHETIC_TXN_000008"].copy() # 900.0, MOBILE (should pass)
        dup_failing_txn = df[df["txn_id"] == "SYNTHETIC_TXN_000005"].copy() # 200.0, BRANCH (should fail)
        df = pd.concat([df, dup_passing_txn, dup_failing_txn], ignore_index=True)

    elif variant == "medium":
        df = pd.concat([df] * 10, ignore_index=True)
    elif variant == "large":
        df = pd.concat([df] * 100, ignore_index=True)

    transactions_path = tmp_path / f"synthetic_{variant}_transactions.csv"
    accounts_path = tmp_path / f"synthetic_{variant}_accounts.csv" # Dummy
    balances_path = tmp_path / f"synthetic_{variant}_daily_balances.csv"   # Dummy

    with open(transactions_path, 'w') as f: f.write("H1,H2,H3,H4,H5,H6,H7,H8\n") # Placeholder for synthetic header
    df.to_csv(transactions_path, mode='a', index=False, header=False)

    # Create dummy empty files for accounts and balances as they are required by the run signature
    pd.DataFrame(columns=[]).to_csv(accounts_path, index=False)
    pd.DataFrame(columns=[]).to_csv(balances_path, index=False)

    return accounts_path, transactions_path, balances_path


@pytest.mark.parametrize(
    "variant",
    ["clean", "null_heavy", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task29c_run_function(transactions_path: tuple[Path, Path, Path], variant: str):
    """
    Tests the run function from task29c.py to perform config-driven filtering of transactions
    based on amount and channel for various dataset variants.
    """
    accounts_path, transactions_path_arg, balances_path = transactions_path

    result_df = task29c.run(accounts_path, transactions_path_arg, balances_path)

    assert isinstance(result_df, pd.DataFrame)

    # Assert expected columns are present
    expected_columns = [
        "txn_id", "account_id", "txn_date", "txn_amount", "txn_type",
        "merchant_category", "channel", "is_flagged"
    ]
    assert sorted(list(result_df.columns)) == sorted(expected_columns)

    # Define the expected filters from task29c.py's hardcoded config
    min_amount_threshold = 500
    allowed_channels = {"ONLINE", "MOBILE", "ATM"}

    # For clean variant, verify specific filtering results
    if variant == "clean":
        # Original data:
        # Amounts: 100, 600, 450, 700, 200, 800, 300, 900, 400, 1000, 50, 550, 499, 500, 650
        # Channels: ONLINE, BRANCH, MOBILE, ATM, BRANCH, ONLINE, KIOSK, MOBILE, ONLINE, ATM, ONLINE, BRANCH, MOBILE, ATM, ONLINE

        # Filter by amount (>= 500):
        # 600, 700, 800, 900, 1000, 550, 500, 650 -> 8 transactions
        # Channels for these: BRANCH, ATM, ONLINE, MOBILE, ATM, BRANCH, ATM, ONLINE

        # Filter by channel (ONLINE, MOBILE, ATM):
        # 600 (BRANCH) -> excluded
        # 700 (ATM) -> included
        # 800 (ONLINE) -> included
        # 900 (MOBILE) -> included
        # 1000 (ATM) -> included
        # 550 (BRANCH) -> excluded
        # 500 (ATM) -> included
        # 650 (ONLINE) -> included
        # Total expected rows: 6

        expected_txn_ids = [
            "SYNTHETIC_TXN_000004", # 700, ATM
            "SYNTHETIC_TXN_000006", # 800, ONLINE
            "SYNTHETIC_TXN_000008", # 900, MOBILE
            "SYNTHETIC_TXN_000010", # 1000, ATM
            "SYNTHETIC_TXN_000014", # 500, ATM
            "SYNTHETIC_TXN_000015"  # 650, ONLINE
        ]
        assert len(result_df) == len(expected_txn_ids)
        assert sorted(result_df["txn_id"].tolist()) == sorted(expected_txn_ids)
        assert (result_df["txn_amount"] >= min_amount_threshold).all()
        assert result_df["channel"].isin(allowed_channels).all()

    # For null_heavy variant, check how nulls/invalid values are handled in filtering
    elif variant == "null_heavy":
        # Original data was modified:
        # TXN_000002: txn_amount=600 -> None. Should be excluded by amount filter.
        # TXN_000003: channel=MOBILE -> None. Should be excluded by channel filter.
        # TXN_000010: txn_amount=1000 -> "invalid". Should be coerced to NaN and then excluded by amount filter.

        # Expected behavior:
        # - Rows with null/NaN txn_amount will not satisfy `>= min_amount_threshold`.
        # - Rows with null channel will not satisfy `isin(allowed_channels)`.

        # All transactions with amount >= 500 (before null/invalid):
        # 600, 700, 800, 900, 1000, 550, 500, 650 (8 txns)

        # Applying null/invalid changes:
        # TXN_000002 (600, BRANCH) -> None, BRANCH (excluded by amount)
        # TXN_000003 (450, MOBILE) -> 450, None (excluded by channel)
        # TXN_000010 (1000, ATM) -> NaN, ATM (excluded by amount)

        # So, from original passing 8 txns, TXN_000002 and TXN_000010 will be removed due to amount issues.
        # TXN_000003 was originally failing by amount, so its channel null doesn't matter for final count.
        # The remaining txns with amount >= 500 and valid non-null channel from {ONLINE, MOBILE, ATM} are:
        # TXN_000004 (700, ATM)
        # TXN_000006 (800, ONLINE)
        # TXN_000008 (900, MOBILE)
        # TXN_000014 (500, ATM)
        # TXN_000015 (650, ONLINE)
        # Total expected rows: 5

        expected_txn_ids_null_heavy = [
            "SYNTHETIC_TXN_000004", "SYNTHETIC_TXN_000006", "SYNTHETIC_TXN_000008",
            "SYNTHETIC_TXN_000014", "SYNTHETIC_TXN_000015"
        ]
        assert len(result_df) == len(expected_txn_ids_null_heavy)
        assert sorted(result_df["txn_id"].tolist()) == sorted(expected_txn_ids_null_heavy)
        assert (result_df["txn_amount"] >= min_amount_threshold).all()
        assert result_df["channel"].isin(allowed_channels).all()
        assert result_df["txn_amount"].isnull().sum() == 0
        assert result_df["channel"].isnull().sum() == 0

    # For duplicate_heavy variant, check that filtering is correct and duplicates are preserved if they pass filters
    elif variant == "duplicate_heavy":
        # Original passing txns from clean variant: 6
        # Added dup_passing_txn: SYNTHETIC_TXN_000008 (900.0, MOBILE) -> adds one more passing transaction
        # Added dup_failing_txn: SYNTHETIC_TXN_000005 (200.0, BRANCH) -> still fails filters, not in result.
        # So, total expected passing txns: 6 (original) + 1 (dup_passing_txn) = 7

        # Ensure the duplicated passing transaction is present twice
        assert len(result_df) == 7
        assert result_df["txn_id"].value_counts()["SYNTHETIC_TXN_000008"] == 2
        assert (result_df["txn_amount"] >= min_amount_threshold).all()
        assert result_df["channel"].isin(allowed_channels).all()

    # For medium and large variants, ensure it completes without error
    # and the new columns exist with appropriate dtype. Rely on the series assertions above for correctness.
    elif variant == "medium":
        # Expected row count: 6 (from clean variant) * 10 = 60
        assert len(result_df) == 6 * 10
        assert (result_df["txn_amount"] >= min_amount_threshold).all()
        assert result_df["channel"].isin(allowed_channels).all()
    elif variant == "large":
        # Expected row count: 6 (from clean variant) * 100 = 600
        assert len(result_df) == 6 * 100
        assert (result_df["txn_amount"] >= min_amount_threshold).all()
        assert result_df["channel"].isin(allowed_channels).all()
