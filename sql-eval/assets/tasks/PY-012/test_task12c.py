import pandas as pd
import pytest
from pathlib import Path
import importlib, sys

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).resolve().parent))
task12c = importlib.import_module("task12c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task12c.py | Tests: task12c.py (PY-012)
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
    base_data = {
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 11)],
        "account_id": [
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0002", 
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0003", "SYNTHETIC_ACCT_0002", 
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0003", "SYNTHETIC_ACCT_0004", 
            "SYNTHETIC_ACCT_0004"
        ],
        "txn_date": [
            "2023-01-05", "2023-01-06", "2023-01-05", "2023-01-07", "2023-01-05",
            "2023-01-06", "2023-01-08", "2023-01-06", "2023-01-05", "2023-01-06"
        ],
        "txn_amount": [100.0, 50.0, 200.0, 75.0, 300.0, 120.0, 180.0, 90.0, 250.0, 110.0],
        "txn_type": ["PURCHASE"] * 10,
        "merchant_category": ["RETAIL"] * 10,
        "channel": ["ONLINE"] * 10,
        "is_flagged": [False] * 10,
    }
    df = pd.DataFrame(base_data)

    if variant == "null_heavy":
        df.loc[0, "txn_amount"] = None  # Null in txn_amount for ACCT_0001
        df.loc[2, "account_id"] = None   # Null account_id for ACCT_0002 related transaction
    elif variant == "duplicate_heavy":
        # Add a duplicate transaction for ACCT_0001 with same date but different txn_id
        dup_txn = pd.DataFrame({
            "txn_id": ["SYNTHETIC_TXN_000011"], "account_id": ["SYNTHETIC_ACCT_0001"],
            "txn_date": ["2023-01-06"], "txn_amount": [60.0], "txn_type": ["PURCHASE"],
            "merchant_category": ["RETAIL"], "channel": ["ONLINE"], "is_flagged": [False]
        })
        df = pd.concat([df, dup_txn], ignore_index=True)
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
def test_task12c_run_function(transactions_path: Path, variant: str):
    """
    Tests the run function from task12c.py to create a running total of 'txn_amount'
    within each account ordered by 'txn_date' for various dataset variants.
    """
    # Dummy paths for accounts and balances as they are not used in task12c.run
    accounts_path = Path("dummy_accounts.csv")
    balances_path = Path("dummy_balances.csv")

    result_df = task12c.run(accounts_path, transactions_path, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    # For null_heavy with account_id = None, those rows will be dropped in cumsum, leading to fewer rows if account_id is critical.
    # The task asks for running total *within each account*. So if account_id is null, it might be excluded or lead to NaNs.
    if variant == "null_heavy":
        original_df = pd.read_csv(transactions_path, skiprows=1)
        # Rows with null account_id or null txn_amount should not get a running total
        expected_len = len(original_df.dropna(subset=["account_id", "txn_amount"]))
        # The `cumsum` will produce NaN for nulls, but if `account_id` is null, it also groups as null, not dropping it. 
        # So we expect same number of rows, but running_total_txn_amount will be NaN for those.
        assert len(result_df) == len(original_df) # No rows dropped, just NaNs in new column
    else:
        assert not result_df.empty, "Resulting DataFrame should not be empty"
        original_df_for_len = pd.read_csv(transactions_path, skiprows=1)
        assert len(result_df) == len(original_df_for_len)

    # Assert 'running_total_txn_amount' column is present and numeric
    assert "running_total_txn_amount" in result_df.columns
    assert pd.api.types.is_numeric_dtype(result_df["running_total_txn_amount"])

    # Assertions for specific running total logic
    # For each account, check the running total manually
    for account_id, group in result_df.groupby("account_id"):
        if pd.isna(account_id): # Handle the case where account_id itself is null
            assert group["running_total_txn_amount"].isnull().all()
            continue

        # Sort the group by txn_date and txn_id as done in the run function for deterministic order
        sorted_group = group.sort_values(by=["txn_date", "txn_id"]).copy()
        
        # Drop rows where txn_amount is NaN for cumsum calculation comparison
        sorted_group_for_sum = sorted_group.dropna(subset=["txn_amount"])

        expected_running_total = sorted_group_for_sum["txn_amount"].cumsum()
        
        # Merge back to original sorted group to compare with the result_df
        comparison_df = pd.merge(
            sorted_group[["txn_id", "txn_date", "txn_amount", "running_total_txn_amount"]],
            expected_running_total.rename("expected_running_total"),
            left_index=True,
            right_index=True,
            how='left'
        )

        # Only compare non-null running totals
        # This handles cases where txn_amount might be null, leading to NaN in cumsum
        non_null_comparison = comparison_df.dropna(subset=["running_total_txn_amount", "expected_running_total"])
        pd.testing.assert_series_equal(
            non_null_comparison["running_total_txn_amount"].reset_index(drop=True),
            non_null_comparison["expected_running_total"].reset_index(drop=True),
            check_dtype=False, # Pandas can infer different float types
            check_exact=False, # Floating point comparison
        )

    # Check that for duplicate_heavy variant, the running totals reflect the added transaction
    if variant == "duplicate_heavy":
        acct_0001_df = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0001"].sort_values(by=["txn_date", "txn_id"])
        # Expected sequence of txn_amounts for ACCT_0001 in order:
        # 2023-01-05: 100.0 (SYNTHETIC_TXN_000001)
        # 2023-01-06: 50.0 (SYNTHETIC_TXN_000002)
        # 2023-01-06: 60.0 (SYNTHETIC_TXN_000011) - added duplicate
        # 2023-01-07: 75.0 (SYNTHETIC_TXN_000004)
        # 2023-01-08: 180.0 (SYNTHETIC_TXN_000007)

        expected_running_totals = [100.0, 150.0, 210.0, 285.0, 465.0] # Assuming original data matches this sorted order
        # Need to recalculate based on the fixture's base_data if it changes.
        # Original ACCT_0001 transactions: [100.0 (01-05), 50.0 (01-06), 75.0 (01-07), 180.0 (01-08)]
        # Added dup: 60.0 (01-06, txn_id 000011)
        # Sorted by date then txn_id:
        # 01-05: TXN_000001 -> 100.0
        # 01-06: TXN_000002 -> 50.0
        # 01-06: TXN_000011 -> 60.0
        # 01-07: TXN_000004 -> 75.0
        # 01-08: TXN_000007 -> 180.0

        # Cumulative sums: 100.0, 150.0, 210.0, 285.0, 465.0

        pd.testing.assert_series_equal(
            acct_0001_df["running_total_txn_amount"].reset_index(drop=True),
            pd.Series([100.0, 150.0, 210.0, 285.0, 465.0]),
            check_dtype=False, check_exact=False
        )

    # For medium and large, ensure non-empty output and running total column exists
    # More detailed numerical checks are computationally expensive and might not be feasible for all scaled variants
