import pandas as pd
import pytest
from pathlib import Path
import importlib, sys
import numpy as np

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).parent.parent / "assets" / "tasks_a" / "answers_python"))
task13c = importlib.import_module("task13c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task13c.py | Tests: task13c.py (PY-013)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).parent.parent / "assets" / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def balances_path(tmp_path: Path, variant: str):
    """
    Fixture to create dummy daily_balances CSV files for different variants.
    """
    base_dates_acct1 = [f"2024-12-{i:02d}" for i in range(1, 11)] # 10 days
    base_dates_acct2 = [f"2024-12-{i:02d}" for i in range(1, 6)]  # 5 days

    base_data = {
        "account_id": ["SYNTHETIC_ACCT_0001"] * len(base_dates_acct1) + ["SYNTHETIC_ACCT_0002"] * len(base_dates_acct2),
        "balance_date": base_dates_acct1 + base_dates_acct2,
        "closing_balance": [100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0, 180.0, 190.0] + \
                           [50.0, 60.0, 70.0, 80.0, 90.0],
        "txn_count_day": [1, 2, 1, 3, 2, 1, 2, 1, 3, 2] + \
                         [1, 1, 2, 1, 2],
    }
    df = pd.DataFrame(base_data)

    if variant == "null_heavy":
        # Introduce nulls in closing_balance for rolling average test
        df.loc[df["account_id"] == "SYNTHETIC_ACCT_0001", "closing_balance"].iloc[1] = None # Acct1, Day 2
        df.loc[df["account_id"] == "SYNTHETIC_ACCT_0001", "closing_balance"].iloc[5] = None # Acct1, Day 6
        df.loc[df["account_id"] == "SYNTHETIC_ACCT_0002", "closing_balance"].iloc[2] = None # Acct2, Day 3
    elif variant == "duplicate_heavy":
        # Add duplicate rows for an account-date pair to see how rolling handles it
        dup_row_acct1 = df[(df["account_id"] == "SYNTHETIC_ACCT_0001") & (df["balance_date"] == "2024-12-05")].copy()
        dup_row_acct1["txn_count_day"] = 99 # Make one value different to distinguish
        df = pd.concat([df, dup_row_acct1], ignore_index=True)
        # Add another duplicate row, exact copy
        dup_row_acct2 = df[(df["account_id"] == "SYNTHETIC_ACCT_0002") & (df["balance_date"] == "2024-12-02")].copy()
        df = pd.concat([df, dup_row_acct2], ignore_index=True)

    elif variant == "medium":
        df = pd.concat([df] * 10, ignore_index=True)
    elif variant == "large":
        df = pd.concat([df] * 100, ignore_index=True)

    balances_path = tmp_path / f"synthetic_{variant}_daily_balances.csv"
    transactions_path = tmp_path / f"synthetic_{variant}_transactions.csv" # Dummy
    accounts_path = tmp_path / f"synthetic_{variant}_accounts.csv"   # Dummy

    with open(balances_path, 'w') as f: f.write("H1,H2,H3,H4\n") # Placeholder for synthetic header
    df.to_csv(balances_path, mode='a', index=False, header=False)

    # Create dummy empty files for accounts and transactions as they are required by the run signature
    pd.DataFrame(columns=[]).to_csv(accounts_path, index=False)
    pd.DataFrame(columns=[]).to_csv(transactions_path, index=False)

    return accounts_path, transactions_path, balances_path


@pytest.mark.parametrize(
    "variant",
    ["clean", "null_heavy", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task13c_run_function(balances_path: tuple[Path, Path, Path], variant: str):
    """
    Tests the run function from task13c.py to compute a rolling average of 'closing_balance'
    over the last 7 observations per account for various dataset variants.
    """
    accounts_path, transactions_path, balances_path_arg = balances_path

    result_df = task13c.run(accounts_path, transactions_path, balances_path_arg)

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty, "Resulting DataFrame should not be empty"

    # Assert expected columns are present
    expected_columns = ["account_id", "balance_date", "closing_balance", "txn_count_day", "rolling_avg_7_obs"]
    assert sorted(list(result_df.columns)) == sorted(expected_columns)

    # Assert 'rolling_avg_7_obs' column is numeric
    assert pd.api.types.is_numeric_dtype(result_df["rolling_avg_7_obs"])

    # For each account, verify the rolling average calculation
    for account_id, group in result_df.groupby("account_id"):
        sorted_group = group.sort_values(by="balance_date").copy()
        
        # Manually calculate expected rolling average for comparison
        # min_periods=1 means it will calculate even if fewer than 7 non-NaN values
        expected_rolling_avg = sorted_group["closing_balance"].rolling(window=7, min_periods=1).mean()
        
        # Compare only non-null values of the rolling average
        pd.testing.assert_series_equal(
            sorted_group["rolling_avg_7_obs"].dropna().reset_index(drop=True),
            expected_rolling_avg.dropna().reset_index(drop=True),
            check_dtype=False,
            check_exact=False, # Floating point comparison
        )
