import pandas as pd
import pytest
from pathlib import Path
import importlib, sys
import numpy as np

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).parent.parent / "assets" / "tasks_a" / "answers_python"))
task25c = importlib.import_module("task25c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task25c.py | Tests: task25c.py (PY-025)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).parent.parent / "assets" / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def transactions_path(tmp_path: Path, variant: str):
    """
    Fixture to create dummy transactions CSV files for different variants
    with varied transaction amounts for rolling z-score anomaly detection.
    """
    base_data = {
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 15)],
        "account_id": [
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001",
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001",
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", # 8 transactions for ACCT_0001
            "SYNTHETIC_ACCT_0002", "SYNTHETIC_ACCT_0002", "SYNTHETIC_ACCT_0002",
            "SYNTHETIC_ACCT_0003", "SYNTHETIC_ACCT_0003", "SYNTHETIC_ACCT_0003",
        ],
        "txn_date": [
            "2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05", "2023-01-06", "2023-01-07", "2023-01-08", # ACCT_0001
            "2023-02-01", "2023-02-02", "2023-02-03", # ACCT_0002
            "2023-03-01", "2023-03-02", "2023-03-03", # ACCT_0003
        ],
        "txn_amount": [
            100.0, 105.0, 110.0, 115.0, 120.0, 125.0, 130.0, 500.0, # ACCT_0001 (500 is an outlier)
            200.0, 205.0, 50.0, # ACCT_0002 (50 is an outlier)
            300.0, 310.0, 320.0 # ACCT_0003
        ],
        "txn_type": ["PURCHASE"] * 14,
        "merchant_category": ["RETAIL"] * 14,
        "channel": ["ONLINE"] * 14,
        "is_flagged": [False] * 14,
    }
    df = pd.DataFrame(base_data)

    if variant == "null_heavy":
        df.loc[df["txn_id"] == "SYNTHETIC_TXN_000002", "txn_amount"] = None  # ACCT_0001, normal value becomes null
        df.loc[df["txn_id"] == "SYNTHETIC_TXN_000008", "txn_amount"] = None  # ACCT_0001, outlier value becomes null
        df.loc[df["txn_id"] == "SYNTHETIC_TXN_000011", "txn_amount"] = "abc" # ACCT_0002, outlier value becomes non-numeric
    elif variant == "duplicate_heavy":
        # Add a duplicate transaction that is an outlier
        dup_outlier = df[df["txn_id"] == "SYNTHETIC_TXN_000008"].copy()
        df = pd.concat([df, dup_outlier], ignore_index=True)

        # Add a duplicate normal transaction
        dup_normal = df[df["txn_id"] == "SYNTHETIC_TXN_000001"].copy()
        df = pd.concat([df, dup_normal], ignore_index=True)
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


def calculate_expected_z_scores(df: pd.DataFrame, window_size: int = 7) -> pd.Series:
    """
    Manually calculates rolling z-scores for a DataFrame to compare against task25c.py output.
    Handles min_periods and division by zero for rolling_std.
    """
    df = df.sort_values(by=["account_id", "txn_date", "txn_id"]).copy()
    df["txn_date"] = pd.to_datetime(df["txn_date"])
    
    # Drop rows with NaN txn_amount for calculation
    df_for_calc = df.dropna(subset=["txn_amount"])

    rolling_mean = df_for_calc.groupby("account_id")["txn_amount"].rolling(
        window=window_size, min_periods=1
    ).mean().reset_index(level=0, drop=True)
    
    rolling_std = df_for_calc.groupby("account_id")["txn_amount"].rolling(
        window=window_size, min_periods=1
    ).std().reset_index(level=0, drop=True)

    # Reindex rolling_mean and rolling_std to match the original index of df_for_calc
    # This is important because the rolling operations return series with the original index.
    rolling_mean = rolling_mean.reindex(df_for_calc.index)
    rolling_std = rolling_std.reindex(df_for_calc.index)

    z_score = np.where(
        rolling_std == 0,
        0,  # If std is 0, z-score is 0
        (df_for_calc["txn_amount"] - rolling_mean) / rolling_std
    )
    return pd.Series(z_score, index=df_for_calc.index)


@pytest.mark.parametrize(
    "variant",
    ["clean", "null_heavy", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task25c_run_function(transactions_path: tuple[Path, Path, Path], variant: str):
    """
    Tests the run function from task25c.py to flag rolling z-score anomalies in
    'txn_amount' within each account using a moving window for various dataset variants.
    """
    accounts_path, transactions_path_arg, balances_path = transactions_path

    result_df = task25c.run(accounts_path, transactions_path_arg, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    
    # Load original for comparison (after dropping nulls in txn_amount)
    original_transactions_df = pd.read_csv(transactions_path_arg, skiprows=1)
    original_transactions_df["txn_amount"] = pd.to_numeric(original_transactions_df["txn_amount"], errors='coerce')
    original_transactions_df = original_transactions_df.dropna(subset=["txn_amount"])

    if original_transactions_df.empty:
        # If all txn_amounts were null/non-numeric and dropped, result_df should be empty or have no anomalies
        assert result_df.empty or (len(result_df) == len(original_transactions_df) and result_df["is_anomaly"].all() == False)
        return
    
    # Assert expected columns are present, including the new flag column and z-score
    expected_columns = [
        "txn_id", "account_id", "txn_date", "txn_amount", "txn_type",
        "merchant_category", "channel", "is_flagged", "rolling_z_score", "is_anomaly"
    ]
    assert all(col in result_df.columns for col in expected_columns)

    # Assert dtypes
    assert pd.api.types.is_float_dtype(result_df["rolling_z_score"])
    assert pd.api.types.is_boolean_dtype(result_df["is_anomaly"])

    # Calculate expected z-scores and anomalies for comparison
    expected_z_scores_series = calculate_expected_z_scores(original_transactions_df)
    z_score_threshold = 2 # Hardcoded in task25c.py
    expected_anomalies_series = expected_z_scores_series.abs() > z_score_threshold

    # Merge expected results with result_df for comparison
    # Sort both for deterministic comparison
    result_df_sorted = result_df.sort_values(by=["account_id", "txn_date", "txn_id"]).reset_index(drop=True)
    original_transactions_df_sorted = original_transactions_df.sort_values(by=["account_id", "txn_date", "txn_id"]).reset_index(drop=True)
    expected_z_scores_sorted = expected_z_scores_series.sort_index().reset_index(drop=True)
    expected_anomalies_sorted = expected_anomalies_series.sort_index().reset_index(drop=True)

    # Ensure lengths match after internal dropping of NaNs
    assert len(result_df_sorted) == len(original_transactions_df_sorted)

    pd.testing.assert_series_equal(
        result_df_sorted["rolling_z_score"],
        expected_z_scores_sorted,
        check_dtype=False, check_exact=False # Floating point comparison
    )
    pd.testing.assert_series_equal(
        result_df_sorted["is_anomaly"],
        expected_anomalies_sorted,
        check_dtype=True, check_exact=True
    )

    # Specific checks for clean variant
    if variant == "clean":
        # ACCT_0001: 500.0 should be an anomaly
        # ACCT_0002: 50.0 should be an anomaly
        # ACCT_0003: No anomalies expected

        acct1_anomalies = result_df_sorted[
            (result_df_sorted["account_id"] == "SYNTHETIC_ACCT_0001") & 
            (result_df_sorted["is_anomaly"] == True)
        ]
        assert len(acct1_anomalies) == 1
        assert acct1_anomalies["txn_amount"].iloc[0] == 500.0

        acct2_anomalies = result_df_sorted[
            (result_df_sorted["account_id"] == "SYNTHETIC_ACCT_0002") & 
            (result_df_sorted["is_anomaly"] == True)
        ]
        assert len(acct2_anomalies) == 1
        assert acct2_anomalies["txn_amount"].iloc[0] == 50.0

        acct3_anomalies = result_df_sorted[
            (result_df_sorted["account_id"] == "SYNTHETIC_ACCT_0003") & 
            (result_df_sorted["is_anomaly"] == True)
        ]
        assert len(acct3_anomalies) == 0

    # For null_heavy variant, ensure nulls/non-numeric values are dropped and not causing errors
    elif variant == "null_heavy":
        # Ensure rows with original null/non-numeric txn_amount are not in the result_df
        assert "SYNTHETIC_TXN_000002" not in result_df_sorted["txn_id"].values # Original null
        assert "SYNTHETIC_TXN_000008" not in result_df_sorted["txn_id"].values # Original null
        assert "SYNTHETIC_TXN_000011" not in result_df_sorted["txn_id"].values # Original non-numeric
        
        # Check if ACCT_0001 now has 6 valid transactions after dropping two (txn_id 2 and 8)
        acct1_valid_txns = original_transactions_df[
            (original_transactions_df["account_id"] == "SYNTHETIC_ACCT_0001") & 
            (original_transactions_df["txn_amount"].notnull())
        ]
        assert len(result_df_sorted[result_df_sorted["account_id"] == "SYNTHETIC_ACCT_0001"]) == len(acct1_valid_txns)
        
        # After dropping some values, the statistics will change, and new outliers might appear or old ones disappear.
        # This is implicitly tested by the general series assertion above.

    # For medium and large variants, simply ensure it completes without error
    # and the new columns exist with appropriate dtypes. Rely on the series assertions above for correctness.
