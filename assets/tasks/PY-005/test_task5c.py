import pandas as pd
import pytest
from pathlib import Path
import importlib, sys

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).resolve().parent))
task5c = importlib.import_module("task5c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task5c.py | Tests: task5c.py (PY-005)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).resolve().parents[2] / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def transactions_path(tmp_path: Path, variant: str):
    """
    Fixture to create dummy transactions CSV files for different variants
    with varied flagged status and transaction amounts.
    """
    data = {
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 11)],
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 11)],
        "txn_date": [f"2023-01-{i:02d}" for i in range(1, 11)],
        "txn_amount": [100.0, 600.0, 50.0, 700.0, 200.0, 800.0, 300.0, 900.0, 400.0, 1000.0],
        "txn_type": ["PURCHASE"] * 10,
        "merchant_category": ["RETAIL"] * 10,
        "channel": ["ONLINE"] * 10,
        "is_flagged": [False, True, False, True, False, True, False, True, False, True],
    }
    df = pd.DataFrame(data)

    if variant == "null_heavy":
        df.loc[[1, 3], "txn_amount"] = None  # Flagged transactions with null amount
        df.loc[0, "merchant_category"] = None # A non-relevant null
    elif variant == "duplicate_heavy":
        # Add duplicates, some flagged, some below threshold
        dup_data = {
            "txn_id": ["SYNTHETIC_TXN_000001", "SYNTHETIC_TXN_000002"],
            "account_id": ["SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0002"],
            "txn_date": ["2023-01-01", "2023-02-01"],
            "txn_amount": [100.0, 600.0],
            "txn_type": ["PURCHASE", "REFUND"],
            "merchant_category": ["RETAIL", "GROCERY"],
            "channel": ["ONLINE", "BRANCH"],
            "is_flagged": [False, True],
        }
        df = pd.concat([df, pd.DataFrame(dup_data)], ignore_index=True)
    elif variant == "medium":
        df = pd.concat([df] * 10, ignore_index=True)
    elif variant == "large":
        df = pd.concat([df] * 100, ignore_index=True)

    transactions_path = tmp_path / f"synthetic_{variant}_transactions.csv"
    with open(transactions_path, 'w') as f: f.write("H1,H2,H3,H4,H5,H6,H7,H8\n")
    df.to_csv(transactions_path, mode='a', index=False, header=False)
    
    return transactions_path


@pytest.mark.parametrize(
    "variant",
    ["clean", "null_heavy", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task5c_run_function(transactions_path: Path, variant: str):
    """
    Tests the run function from task5c.py to filter for flagged transactions
    above a chosen amount for various dataset variants.
    """
    # Dummy paths for accounts and balances as they are not used in task5c.run
    accounts_path = Path("dummy_accounts.csv")
    balances_path = Path("dummy_balances.csv")

    result_df = task5c.run(accounts_path, transactions_path, balances_path)

    assert isinstance(result_df, pd.DataFrame)

    # All remaining transactions should be flagged
    if not result_df.empty:
        assert result_df["is_flagged"].all() == True
        # All remaining transactions should have txn_amount > 500
        assert (result_df["txn_amount"] > 500).all() == True
    
    # For null_heavy variant, check if rows with null txn_amount (that would otherwise pass) are excluded
    # The run function drops them implicitly because None > 500 is False
    if variant == "null_heavy":
        original_df = pd.read_csv(transactions_path, skiprows=1)
        original_flagged_above_500 = original_df[
            (original_df["is_flagged"] == True) & (original_df["txn_amount"] > 500)
        ]
        # Account for NaNs in txn_amount, as they won't satisfy > 500
        expected_len_after_null_handling = len(original_flagged_above_500.dropna(subset=["txn_amount"]))
        assert len(result_df) == expected_len_after_null_handling
    else:
        # Basic check for non-empty result for non-empty inputs, adjusted for expected filtering
        # In the dummy data, there are 4 flagged transactions > 500 (600, 700, 800, 900, 1000)
        # So, for clean/duplicate_heavy/medium/large, should expect at least 4 rows * scale_factor
        if variant == "clean":
            assert len(result_df) == 4
        elif variant == "duplicate_heavy":
            # Original 4 + 1 from dup_data (600.0, True) = 5 unique ones before duplcation
            # After actual duplication in fixture, and then filtering by task5c, will be more.
            # The specific `dup_data` means we have: 600.0, True, 700.0, True, 800.0, True, 900.0, True, 1000.0, True
            # And from `dup_data`: 600.0, True. Total 5 distinct entries that would pass the filter.
            # If the original df had 10 rows and 5 passed, and 2 duplicates added, one of which passed, then:
            # The fixture adds 2 extra rows: SYNTHETIC_TXN_000001 (100.0, False), SYNTHETIC_TXN_000002 (600.0, True)
            # So initial 10 rows + 2 duplicates = 12 rows.
            # The filter condition: (is_flagged == True) & (txn_amount > 500)
            # Original: (600,T), (700,T), (800,T), (900,T), (1000,T) -> 5 rows
            # Added dup: (600,T) -> 1 row.
            # Total rows in result should be 6.
            assert len(result_df) == 6
        elif variant == "medium":
            assert len(result_df) == 4 * 10
        elif variant == "large":
            assert len(result_df) == 4 * 100
