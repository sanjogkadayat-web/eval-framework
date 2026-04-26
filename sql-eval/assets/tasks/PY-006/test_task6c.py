import pandas as pd
import pytest
from pathlib import Path
import importlib, sys

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).resolve().parent))
task6c = importlib.import_module("task6c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task6c.py | Tests: task6c.py (PY-006)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).resolve().parents[2] / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def accounts_path(tmp_path: Path, variant: str):
    """
    Fixture to create dummy accounts CSV files for different variants
    with varied string formatting (whitespace, mixed case, nulls).
    """
    data = {
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 6)],
        "customer_segment": [" retail ", "Small_Biz", "WEALTH ", "  student", "RETAIL"],
        "account_open_date": ["2023-01-01", "2023-02-15", "2023-03-20", "2023-04-10", "2023-05-05"],
        "account_status": [" ACTIVE ", "ACTIVE", "CLOSED", "SUSPENDED ", "ACTIVE"],
        "region": [" NORTH ", "south", "EAST", " west ", "NORTH"],
    }
    df = pd.DataFrame(data)

    # Introduce specific characteristics for variants
    if variant == "null_heavy":
        df.loc[0, "region"] = None
        df.loc[2, "customer_segment"] = None
    elif variant == "duplicate_heavy":
        df = pd.concat([df, df.iloc[[0, 1]]], ignore_index=True) # Add 2 duplicate rows
    elif variant == "medium":
        df = pd.concat([df] * 10, ignore_index=True)
    elif variant == "large":
        df = pd.concat([df] * 100, ignore_index=True)

    accounts_path = tmp_path / f"synthetic_{variant}_accounts.csv"
    
    # Write synthetic header row first
    with open(accounts_path, 'w') as f:
        f.write("H1,H2,H3,H4,H5\n") # Placeholder for synthetic header (skipped by task6c.py)
    
    df.to_csv(accounts_path, mode='a', index=False, header=False)
    
    return accounts_path


@pytest.mark.parametrize(
    "variant",
    ["clean", "null_heavy", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task6c_run_function(accounts_path: Path, variant: str):
    """
    Tests the run function from task6c.py to clean string columns
    for various dataset variants.
    """
    # Dummy paths for transactions and balances as they are not used in task6c.run
    transactions_path = Path("dummy_transactions.csv")
    balances_path = Path("dummy_balances.csv")

    result_df = task6c.run(accounts_path, transactions_path, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty, "Resulting DataFrame should not be empty (unless input was empty)"

    # Assert expected columns are present
    expected_columns = [
        "account_id",
        "customer_segment",
        "account_open_date",
        "account_status",
        "region",
    ]
    assert list(result_df.columns) == expected_columns

    # Assert that 'region' and 'customer_segment' are uppercase and stripped of whitespace
    for col in ["customer_segment", "region"]:
        # Filter out NaN values before applying string checks
        cleaned_col = result_df[col].dropna()
        if not cleaned_col.empty:
            assert cleaned_col.apply(lambda x: x == str(x).strip().upper()).all(), \
                f"Column '{col}' contains values that are not uppercase or not stripped"

    # Additionally, check a non-transformed string column like 'account_status' to ensure whitespace stripping
    cleaned_account_status = result_df["account_status"].dropna()
    if not cleaned_account_status.empty:
        assert cleaned_account_status.apply(lambda x: x == str(x).strip()).all(), \
            f"Column 'account_status' contains values that are not stripped"
