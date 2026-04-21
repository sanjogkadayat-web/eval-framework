import pandas as pd
import pytest
from pathlib import Path
import importlib, sys
import numpy as np

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).resolve().parent))
task20c = importlib.import_module("task20c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task20c.py | Tests: task20c.py (PY-020)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).resolve().parents[2] / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def transactions_path(tmp_path: Path, variant: str):
    """
    Fixture to create dummy transactions CSV files for different variants
    with varied transaction amounts for outlier detection.
    """
    base_data = {
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 16)],
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 16)],
        "txn_date": [f"2023-01-{i:02d}" for i in range(1, 16)],
        "txn_amount": [
            10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, # Normal range
            5.0, # Low outlier
            150.0, # High outlier
            1.0, # Very low outlier
            200.0, # Very high outlier
            65.0 # Another normal value
        ],
        "txn_type": ["PURCHASE"] * 15,
        "merchant_category": ["RETAIL"] * 15,
        "channel": ["ONLINE"] * 15,
        "is_flagged": [False] * 15,
    }
    df = pd.DataFrame(base_data)

    if variant == "null_heavy":
        df.loc[df["txn_id"] == "SYNTHETIC_TXN_000003", "txn_amount"] = None # Null in normal range
        df.loc[df["txn_id"] == "SYNTHETIC_TXN_000011", "txn_amount"] = None # Null for a potential outlier
        df.loc[df["txn_id"] == "SYNTHETIC_TXN_000013", "txn_amount"] = None # Null for another potential outlier
        # Add a row with non-numeric txn_amount to test errors='coerce'
        non_numeric_row = pd.DataFrame({
            "txn_id": ["SYNTHETIC_TXN_NONUMERIC"], "account_id": ["SYNTHETIC_ACCT_9999"],
            "txn_date": ["2023-01-16"], "txn_amount": ["abc"], "txn_type": ["PURCHASE"],
            "merchant_category": ["RETAIL"], "channel": ["ONLINE"], "is_flagged": [False]
        })
        df = pd.concat([df, non_numeric_row], ignore_index=True)

    elif variant == "duplicate_heavy":
        # Add duplicates of normal and outlier transactions
        dup_normal = df[df["txn_id"] == "SYNTHETIC_TXN_000005"].copy()
        dup_low_outlier = df[df["txn_id"] == "SYNTHETIC_TXN_000011"].copy()
        df = pd.concat([df, dup_normal, dup_low_outlier], ignore_index=True)
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
def test_task20c_run_function(transactions_path: tuple[Path, Path, Path], variant: str):
    """
    Tests the run function from task20c.py to flag 'txn_amount' outliers using the
    Interquartile Range (IQR) rule for various dataset variants.
    """
    accounts_path, transactions_path_arg, balances_path = transactions_path

    result_df = task20c.run(accounts_path, transactions_path_arg, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    
    # Assert expected columns are present, including the new flag column
    expected_columns = [
        "txn_id", "account_id", "txn_date", "txn_amount", "txn_type",
        "merchant_category", "channel", "is_flagged", "is_outlier"
    ]
    assert all(col in result_df.columns for col in expected_columns)

    # Assert 'is_outlier' column is boolean
    assert pd.api.types.is_boolean_dtype(result_df["is_outlier"])

    # Read original data (after initial loading and type conversion in the function)
    original_df = pd.read_csv(transactions_path_arg, skiprows=1)
    original_df["txn_amount"] = pd.to_numeric(original_df["txn_amount"], errors='coerce')
    original_df_numeric_only = original_df.dropna(subset=["txn_amount"])

    # Handle empty DataFrame case explicitly, matching task20c.py behavior
    if original_df_numeric_only.empty:
        assert result_df.empty or (len(result_df) == len(original_df) and result_df["is_outlier"].all() == False)
        return # Test passes for empty/all-null case
    
    # Manually calculate IQR and bounds for comparison
    Q1 = original_df_numeric_only["txn_amount"].quantile(0.25)
    Q3 = original_df_numeric_only["txn_amount"].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Expected outliers based on manual calculation
    expected_outliers_series = (
        (original_df_numeric_only["txn_amount"] < lower_bound) |
        (original_df_numeric_only["txn_amount"] > upper_bound)
    )

    # For direct comparison, ensure the result_df corresponds to the filtered original_df
    # and then compare the 'is_outlier' column
    result_df_sorted = result_df.sort_values(by=["txn_id"]).reset_index(drop=True)
    original_df_numeric_only_sorted = original_df_numeric_only.sort_values(by=["txn_id"]).reset_index(drop=True)

    # The length of result_df should be equal to the length of original_df_numeric_only
    assert len(result_df_sorted) == len(original_df_numeric_only_sorted)
    
    pd.testing.assert_series_equal(
        result_df_sorted["is_outlier"].reset_index(drop=True),
        expected_outliers_series.reset_index(drop=True),
        check_dtype=True, # Boolean dtype
        check_exact=True
    )

    # Additional check: For null_heavy, ensure rows with original non-numeric/null txn_amount are dropped
    if variant == "null_heavy":
        assert "SYNTHETIC_TXN_NONUMERIC" not in result_df["txn_id"].values
        assert "SYNTHETIC_TXN_000003" not in result_df["txn_id"].values
        assert "SYNTHETIC_TXN_000011" not in result_df["txn_id"].values
        assert "SYNTHETIC_TXN_000013" not in result_df["txn_id"].values

    # For medium and large variants, simply ensure it completes without error
    # and the new column exists with appropriate dtype.
