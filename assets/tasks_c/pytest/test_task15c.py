import pandas as pd
import pytest
from pathlib import Path
import importlib, sys
import numpy as np

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).parent.parent / "assets" / "tasks_a" / "answers_python"))
task15c = importlib.import_module("task15c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task15c.py | Tests: task15c.py (PY-015)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).parent.parent / "assets" / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def transactions_path(tmp_path: Path, variant: str):
    """
    Fixture to create dummy transactions CSV files for different variants.
    """
    base_data = {
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 11)],
        "account_id": [
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", 
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0002", "SYNTHETIC_ACCT_0002", 
            "SYNTHETIC_ACCT_0002", "SYNTHETIC_ACCT_0003", "SYNTHETIC_ACCT_0003", 
            "SYNTHETIC_ACCT_0003"
        ],
        "txn_date": [
            "2023-01-05", "2023-01-06", "2023-01-07", "2023-01-08", # ACCT_0001
            "2023-01-05", "2023-01-06", "2023-01-07", # ACCT_0002
            "2023-01-05", "2023-01-06", "2023-01-07"  # ACCT_0003
        ],
        "txn_amount": [
            100.0, 50.0, 200.0, 75.0, # ACCT_0001
            300.0, 120.0, 180.0, # ACCT_0002
            90.0, 250.0, 110.0 # ACCT_0003
        ],
        "txn_type": ["PURCHASE"] * 10,
        "merchant_category": ["RETAIL"] * 10,
        "channel": ["ONLINE"] * 10,
        "is_flagged": [False] * 10,
    }
    df = pd.DataFrame(base_data)

    if variant == "null_heavy":
        df.loc[df["txn_id"] == "SYNTHETIC_TXN_000002", "txn_amount"] = None  # ACCT_0001, 2nd txn_amount null
        df.loc[df["txn_id"] == "SYNTHETIC_TXN_000006", "txn_amount"] = None  # ACCT_0002, 2nd txn_amount null
    elif variant == "duplicate_heavy":
        # Add a duplicate transaction for ACCT_0001 on the same date with different txn_id
        dup_txn_1 = pd.DataFrame({
            "txn_id": ["SYNTHETIC_TXN_000001_DUP"], "account_id": ["SYNTHETIC_ACCT_0001"],
            "txn_date": ["2023-01-05"], "txn_amount": [10.0], "txn_type": ["PURCHASE"],
            "merchant_category": ["RETAIL"], "channel": ["ONLINE"], "is_flagged": [False]
        })
        df = pd.concat([df, dup_txn_1], ignore_index=True)
        # Add another duplicate for ACCT_0002 to ensure consistent sorting handles it
        dup_txn_2 = pd.DataFrame({
            "txn_id": ["SYNTHETIC_TXN_000005_DUP"], "account_id": ["SYNTHETIC_ACCT_0002"],
            "txn_date": ["2023-01-05"], "txn_amount": [30.0], "txn_type": ["PURCHASE"],
            "merchant_category": ["RETAIL"], "channel": ["ONLINE"], "is_flagged": [False]
        })
        df = pd.concat([df, dup_txn_2], ignore_index=True)
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
def test_task15c_run_function(transactions_path: tuple[Path, Path, Path], variant: str):
    """
    Tests the run function from task15c.py to add a 'previous_txn_amount' feature
    within each account using the shift method for various dataset variants.
    """
    accounts_path, transactions_path_arg, balances_path = transactions_path

    result_df = task15c.run(accounts_path, transactions_path_arg, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty, "Resulting DataFrame should not be empty"

    # Assert expected columns are present
    expected_columns = [
        "txn_id", "account_id", "txn_date", "txn_amount", "txn_type",
        "merchant_category", "channel", "is_flagged", "previous_txn_amount"
    ]
    assert sorted(list(result_df.columns)) == sorted(expected_columns)

    # Assert 'previous_txn_amount' column is numeric
    assert pd.api.types.is_numeric_dtype(result_df["previous_txn_amount"])

    # For each account, verify the shifted value
    for account_id, group in result_df.groupby("account_id"):
        if pd.isna(account_id):
            assert group["previous_txn_amount"].isnull().all()
            continue

        # Sort the group by txn_date and txn_id (as in task15c.py) for deterministic order
        sorted_group = group.sort_values(by=["txn_date", "txn_id"]).copy()

        # Manually calculate expected previous_txn_amount for comparison
        expected_previous_txn = sorted_group["txn_amount"].shift(1)

        pd.testing.assert_series_equal(
            sorted_group["previous_txn_amount"].reset_index(drop=True),
            expected_previous_txn.reset_index(drop=True),
            check_dtype=False,
            check_exact=False, # Floating point comparison
        )

    # Specific checks for clean variant for ACCT_0001
    if variant == "clean":
        acct1_df = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0001"].sort_values(by=["txn_date", "txn_id"])
        # Expected previous_txn_amount for ACCT_0001:
        # Original: 100.0, 50.0, 200.0, 75.0
        # Shifted: NaN, 100.0, 50.0, 200.0
        expected_prev_amounts = [np.nan, 100.0, 50.0, 200.0]
        pd.testing.assert_series_equal(
            acct1_df["previous_txn_amount"].reset_index(drop=True),
            pd.Series(expected_prev_amounts, dtype='float64'),
            check_dtype=False, check_exact=False
        )
    elif variant == "null_heavy":
        acct1_df_null_heavy = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0001"].sort_values(by=["txn_date", "txn_id"])
        # Original: 100.0, None, 200.0, 75.0
        # Shifted: NaN, 100.0, None, 200.0
        expected_prev_amounts_null_heavy = [np.nan, 100.0, np.nan, 200.0]
        pd.testing.assert_series_equal(
            acct1_df_null_heavy["previous_txn_amount"].reset_index(drop=True),
            pd.Series(expected_prev_amounts_null_heavy, dtype='float64'),
            check_dtype=False, check_exact=False
        )
    elif variant == "duplicate_heavy":
        acct1_df_dup_heavy = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0001"].sort_values(by=["txn_date", "txn_id"])
        # Original data for ACCT_0001 sorted by txn_date, txn_id:
        # 2023-01-05: 100.0 (SYNTHETIC_TXN_000001)
        # 2023-01-05: 10.0 (SYNTHETIC_TXN_000001_DUP)
        # 2023-01-06: 50.0 (SYNTHETIC_TXN_000002)
        # 2023-01-07: 200.0 (SYNTHETIC_TXN_000003)
        # 2023-01-08: 75.0 (SYNTHETIC_TXN_000004)

        # Expected shifted amounts:
        # NaN
        # 100.0
        # 10.0
        # 50.0
        # 200.0
        expected_prev_amounts_dup_heavy = [np.nan, 100.0, 10.0, 50.0, 200.0]
        pd.testing.assert_series_equal(
            acct1_df_dup_heavy["previous_txn_amount"].reset_index(drop=True),
            pd.Series(expected_prev_amounts_dup_heavy, dtype='float64'),
            check_dtype=False, check_exact=False
        )

    # For medium and large, ensure non-empty output and previous_txn_amount column exists
