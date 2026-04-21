import pandas as pd
import pytest
from pathlib import Path
import importlib, sys

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).parent.parent / "assets" / "tasks_a" / "answers_python"))
task9c = importlib.import_module("task9c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task9c.py | Tests: task9c.py (PY-009)
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
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 11)],
        "txn_date": [f"2023-01-{i:02d}" for i in range(1, 11)],
        "txn_amount": [100.0, 200.0, None, 150.0, 300.0, None, 50.0, 250.0, 120.0, 180.0],
        "txn_type": ["PURCHASE"] * 10,
        "merchant_category": ["RETAIL"] * 10,
        "channel": ["ONLINE"] * 10,
        "is_flagged": [False] * 10,
    }
    df = pd.DataFrame(base_data)
    
    if variant == "clean":
        # For clean, replace None with a specific value to ensure no nulls initially
        df["txn_amount"] = df["txn_amount"].fillna(df["txn_amount"].median())
    elif variant == "null_heavy":
        # Keep nulls as they are for null_heavy variant to test fillna logic
        pass
    elif variant == "duplicate_heavy":
        # Add duplicates with nulls
        dup_data = {
            "txn_id": ["SYNTHETIC_TXN_000011"],
            "account_id": ["SYNTHETIC_ACCT_0001"],
            "txn_date": ["2023-01-11"],
            "txn_amount": [None],
            "txn_type": ["PURCHASE"],
            "merchant_category": ["RETAIL"],
            "channel": ["ONLINE"],
            "is_flagged": [False],
        }
        df = pd.concat([df, pd.DataFrame(dup_data)], ignore_index=True)
    elif variant == "medium":
        df = pd.concat([df] * 10, ignore_index=True)
    elif variant == "large":
        df = pd.concat([df] * 100, ignore_index=True)

    transactions_path = tmp_path / f"synthetic_{variant}_transactions.csv"
    
    with open(transactions_path, 'w') as f:
        f.write("H1,H2,H3,H4,H5,H6,H7,H8\n") # Placeholder for synthetic header
    
    df.to_csv(transactions_path, mode='a', index=False, header=False)
    
    return transactions_path


@pytest.mark.parametrize(
    "variant",
    ["clean", "null_heavy", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task9c_run_function(transactions_path: Path, variant: str):
    """
    Tests the run function from task9c.py to fill null 'txn_amount' values
    with the median 'txn_amount' for various dataset variants.
    """
    # Dummy paths for accounts and balances as they are not used in task9c.run
    accounts_path = Path("dummy_accounts.csv")
    balances_path = Path("dummy_balances.csv")

    result_df = task9c.run(accounts_path, transactions_path, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty, "Resulting DataFrame should not be empty (unless input was empty)"

    # Assert expected columns are present
    expected_columns = [
        "txn_id", "account_id", "txn_date", "txn_amount", "txn_type",
        "merchant_category", "channel", "is_flagged"
    ]
    assert list(result_df.columns) == expected_columns

    # Assert no nulls in 'txn_amount' column after processing
    assert result_df["txn_amount"].isnull().sum() == 0

    # Task-specific correctness assertion: Check if nulls were filled with the correct median
    original_df = pd.read_csv(transactions_path, skiprows=1)
    original_non_null_amounts = original_df["txn_amount"].dropna()

    if not original_non_null_amounts.empty:
        expected_median = original_non_null_amounts.median()
        # Find original null positions
        original_null_indices = original_df[original_df["txn_amount"].isnull()].index

        if not original_null_indices.empty:
            # Assert that values at original null positions are now the median
            # For large/medium variants, need to be careful with index alignment after concat
            if variant in ["clean", "null_heavy", "duplicate_heavy"]:
                for idx in original_null_indices:
                    assert result_df.loc[idx, "txn_amount"] == pytest.approx(expected_median)
            else:
                # For scaled variants, just check if all original null values are replaced by median
                # This is a less precise check but handles the scaling.
                assert (result_df.loc[original_null_indices, "txn_amount"] == pytest.approx(expected_median)).all()

    else:
        # If original_df had no non-null txn_amounts, then median would be NaN, and fillna might not work as expected
        # However, the synthetic data should always have some non-nulls for median calculation.
        # If all were null, pandas fillna with NaN median would still result in NaN. The task implies valid median calculation.
        pass
