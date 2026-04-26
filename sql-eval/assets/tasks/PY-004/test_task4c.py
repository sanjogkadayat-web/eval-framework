import pandas as pd
import pytest
from pathlib import Path
import importlib, sys

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).resolve().parent))
task4c = importlib.import_module("task4c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task4c.py | Tests: task4c.py (PY-004)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).resolve().parents[2] / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def transactions_path(tmp_path: Path, variant: str):
    """
    Fixture to create dummy transactions CSV files for different variants.
    """
    data = {
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 6)],
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 6)],
        "txn_date": ["2023-01-05", "2023-02-20", "2023-03-25", "2023-04-15", "2023-05-10"],
        "txn_amount": [100.50, 200.75, 50.25, 150.00, 300.10],
        "txn_type": ["PURCHASE", "REFUND", "TRANSFER", "FEE", "PURCHASE"],
        "merchant_category": ["RETAIL", "GROCERY", "TRAVEL", "DINING", "UTILITIES"],
        "channel": ["ONLINE", "BRANCH", "ATM", "MOBILE", "ONLINE"],
        "is_flagged": [False, False, True, False, True],
    }
    df = pd.DataFrame(data)
    
    initial_row_count = len(df)

    # Introduce specific characteristics for variants
    if variant == "null_heavy":
        df.loc[0, "txn_amount"] = None
        df.loc[2, "merchant_category"] = None
    elif variant == "duplicate_heavy":
        df = pd.concat([df, df.iloc[[0, 1]]], ignore_index=True) # Add 2 duplicate rows
    elif variant == "medium":
        df = pd.concat([df] * 10, ignore_index=True)
    elif variant == "large":
        df = pd.concat([df] * 100, ignore_index=True)

    transactions_path = tmp_path / f"synthetic_{variant}_transactions.csv"
    
    # Write synthetic header row first
    with open(transactions_path, 'w') as f:
        f.write("H1,H2,H3,H4,H5,H6,H7,H8\n") # Placeholder for synthetic header (skipped by task4c.py)
    
    df.to_csv(transactions_path, mode='a', index=False, header=False)
    
    return transactions_path, initial_row_count


@pytest.mark.parametrize(
    "variant",
    ["clean", "null_heavy", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task4c_run_function(transactions_path: tuple[Path, int], variant: str):
    """
    Tests the run function from task4c.py for various dataset variants.
    It checks if duplicate rows are correctly removed and asserts row counts.
    """
    path, initial_row_count = transactions_path
    
    # Dummy paths for accounts and balances as they are not used in task4c.run
    accounts_path = Path("dummy_accounts.csv")
    balances_path = Path("dummy_balances.csv")

    result_df = task4c.run(accounts_path, path, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty, "Resulting DataFrame should not be empty (unless input was empty)"

    # Assert expected columns are present
    expected_columns = [
        "txn_id", "account_id", "txn_date", "txn_amount", "txn_type",
        "merchant_category", "channel", "is_flagged"
    ]
    assert list(result_df.columns) == expected_columns

    # Variant-aware assertions
    if variant == "duplicate_heavy":
        # For duplicate_heavy, row count should decrease after deduplication
        assert len(result_df) < initial_row_count
        assert len(result_df) == len(result_df.drop_duplicates()), "DataFrame still contains duplicates after processing"
    else:
        # For other variants, there should be no exact duplicates to remove
        assert len(result_df) == initial_row_count
        assert len(result_df) == len(result_df.drop_duplicates()), "DataFrame should not have introduced new duplicates"

