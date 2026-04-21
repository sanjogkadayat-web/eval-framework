import pandas as pd
import pytest
from pathlib import Path
import importlib, sys
import numpy as np

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).resolve().parent))
task14c = importlib.import_module("task14c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task14c.py | Tests: task14c.py (PY-014)
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
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", 
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", 
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", 
            "SYNTHETIC_ACCT_0001"
        ],
        "txn_date": [
            "2024-12-01", "2024-12-02", "2024-12-03", "2024-12-04", "2024-12-05",
            "2024-12-08", "2024-12-09", "2024-12-10", "2024-12-11", "2024-12-12"
        ],
        "txn_amount": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0],
        "txn_type": ["PURCHASE"] * 10,
        "merchant_category": ["RETAIL"] * 10,
        "channel": ["ONLINE"] * 10,
        "is_flagged": [False] * 10,
    }
    df = pd.DataFrame(base_data)

    # Add a second account for testing rolling sum across multiple accounts
    base_data_acct2 = {
        "txn_id": [f"SYNTHETIC_TXN_0000{i+10:02d}" for i in range(1, 6)],
        "account_id": ["SYNTHETIC_ACCT_0002"] * 5,
        "txn_date": [
            "2024-12-01", "2024-12-03", "2024-12-04", "2024-12-06", "2024-12-07"
        ],
        "txn_amount": [5.0, 15.0, 25.0, 35.0, 45.0],
        "txn_type": ["PURCHASE"] * 5,
        "merchant_category": ["RETAIL"] * 5,
        "channel": ["ONLINE"] * 5,
        "is_flagged": [False] * 5,
    }
    df_acct2 = pd.DataFrame(base_data_acct2)

    df = pd.concat([df, df_acct2], ignore_index=True)

    if variant == "null_heavy":
        df.loc[df["txn_id"] == "SYNTHETIC_TXN_000003", "txn_amount"] = None # ACCT_0001, 2024-12-03
        df.loc[df["txn_id"] == "SYNTHETIC_TXN_000013", "txn_amount"] = None # ACCT_0002, 2024-12-03
    elif variant == "duplicate_heavy":
        # Add a duplicate transaction within the same 7-day window
        dup_txn = pd.DataFrame({
            "txn_id": ["SYNTHETIC_TXN_000001"], "account_id": ["SYNTHETIC_ACCT_0001"],
            "txn_date": ["2024-12-01"], "txn_amount": [10.0], "txn_type": ["PURCHASE"],
            "merchant_category": ["RETAIL"], "channel": ["ONLINE"], "is_flagged": [False]
        })
        df = pd.concat([df, dup_txn], ignore_index=True)

        # Another duplicate with a different txn_id but same date and amount
        dup_txn_2 = pd.DataFrame({
            "txn_id": ["SYNTHETIC_TXN_999999"], "account_id": ["SYNTHETIC_ACCT_0001"],
            "txn_date": ["2024-12-01"], "txn_amount": [10.0], "txn_type": ["PURCHASE"],
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
def test_task14c_run_function(transactions_path: tuple[Path, Path, Path], variant: str):
    """
    Tests the run function from task14c.py to compute a rolling 7-day sum of 'txn_amount'
    for each account using a time-based window for various dataset variants.
    """
    accounts_path, transactions_path_arg, balances_path = transactions_path

    result_df = task14c.run(accounts_path, transactions_path_arg, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty, "Resulting DataFrame should not be empty"

    # Assert expected columns are present
    expected_columns = [
        "txn_id", "account_id", "txn_date", "txn_amount", "txn_type",
        "merchant_category", "channel", "is_flagged", "rolling_7day_sum_txn_amount"
    ]
    assert sorted(list(result_df.columns)) == sorted(expected_columns)

    # Assert 'rolling_7day_sum_txn_amount' column is numeric
    assert pd.api.types.is_numeric_dtype(result_df["rolling_7day_sum_txn_amount"])

    # For each account, verify the rolling sum calculation manually
    for account_id, group in result_df.groupby("account_id"):
        if pd.isna(account_id):
            assert group["rolling_7day_sum_txn_amount"].isnull().all()
            continue

        # Sort the group by txn_date and txn_id (as in task14c.py) for deterministic order
        sorted_group = group.sort_values(by=["txn_date", "txn_id"]).copy()
        sorted_group["txn_date"] = pd.to_datetime(sorted_group["txn_date"])
        
        # Manually calculate expected rolling sum for comparison
        # Set txn_date as index for rolling window operations to match logic in task14c.py
        expected_rolling_sum = sorted_group.set_index("txn_date") \
                                         .groupby("account_id")["txn_amount"] \
                                         .rolling("7D", closed="left") \
                                         .sum().reset_index(level=0, drop=True)
        
        # Merge back to original sorted group to compare with the result_df
        comparison_df = pd.merge(
            sorted_group[["txn_id", "txn_date", "txn_amount", "rolling_7day_sum_txn_amount"]],
            expected_rolling_sum.rename("expected_rolling_sum"),
            left_index=True,
            right_index=True,
            how='left'
        )

        # Only compare non-null values of the rolling sum
        non_null_comparison = comparison_df.dropna(subset=["rolling_7day_sum_txn_amount", "expected_rolling_sum"])
        pd.testing.assert_series_equal(
            non_null_comparison["rolling_7day_sum_txn_amount"].reset_index(drop=True),
            non_null_comparison["expected_rolling_sum"].reset_index(drop=True),
            check_dtype=False,
            check_exact=False, # Floating point comparison
        )

    # Specific checks for clean variant
    if variant == "clean":
        acct1_df = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0001"].sort_values(by=["txn_date", "txn_id"])
        # Expected values for ACCT_0001, 7-day rolling sum, closed="left"
        # 2024-12-01: 0.0 (no txns before)
        # 2024-12-02: 10.0 (from 2024-12-01)
        # 2024-12-03: 30.0 (from 2024-12-01, 2024-12-02)
        # 2024-12-04: 60.0 (from 2024-12-01, 2024-12-02, 2024-12-03)
        # 2024-12-05: 100.0 (from 2024-12-01 to 2024-12-04)
        # 2024-12-08: 150.0 (from 2024-12-02 to 2024-12-05)
        # 2024-12-09: 150.0 (from 2024-12-03 to 2024-12-08, excluding 03 itself. 30.0+40.0+50.0+60.0=180.0. Why 150.0 in the example? Closed='left' means it takes values strictly BEFORE current day)
        # Let's re-evaluate rolling sum with closed='left' for ACCT_0001:
        # Dates: 01, 02, 03, 04, 05, 08, 09, 10, 11, 12
        # Amounts: 10, 20, 30, 40, 50, 60, 70, 80, 90, 100
        #
        # 12-01 (value 10): 7D window before 12-01 is empty. Sum = 0.0
        # 12-02 (value 20): 7D window before 12-02 (2024-11-25 to 2024-12-01). Contains 12-01 (10). Sum = 10.0
        # 12-03 (value 30): 7D window before 12-03 (2024-11-26 to 2024-12-02). Contains 12-01 (10), 12-02 (20). Sum = 30.0
        # 12-04 (value 40): 7D window before 12-04 (2024-11-27 to 2024-12-03). Contains 12-01 (10), 12-02 (20), 12-03 (30). Sum = 60.0
        # 12-05 (value 50): 7D window before 12-05 (2024-11-28 to 2024-12-04). Contains 12-01 (10), 12-02 (20), 12-03 (30), 12-04 (40). Sum = 100.0
        # 12-08 (value 60): 7D window before 12-08 (2024-12-01 to 2024-12-07). Contains 12-01 to 12-05 (10+20+30+40+50). Sum = 150.0
        # 12-09 (value 70): 7D window before 12-09 (2024-12-02 to 2024-12-08). Contains 12-02 to 12-05 (20+30+40+50), 12-08 (60). Sum = 200.0
        # 12-10 (value 80): 7D window before 12-10 (2024-12-03 to 2024-12-09). Contains 12-03 to 12-05 (30+40+50), 12-08 (60), 12-09 (70). Sum = 250.0
        # 12-11 (value 90): 7D window before 12-11 (2024-12-04 to 2024-12-10). Contains 12-04, 12-05 (40+50), 12-08 (60), 12-09 (70), 12-10 (80). Sum = 300.0
        # 12-12 (value 100): 7D window before 12-12 (2024-12-05 to 2024-12-11). Contains 12-05 (50), 12-08 (60), 12-09 (70), 12-10 (80), 12-11 (90). Sum = 350.0

        expected_rolling_sums = [0.0, 10.0, 30.0, 60.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0]
        pd.testing.assert_series_equal(
            acct1_df["rolling_7day_sum_txn_amount"].reset_index(drop=True),
            pd.Series(expected_rolling_sums, dtype='float64'), # Ensure dtype matches
            check_dtype=False, check_exact=False
        )

    # For null_heavy variant, check that nulls in txn_amount are handled (skipped in sum)
    elif variant == "null_heavy":
        acct1_df_null_heavy = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0001"].sort_values(by=["txn_date", "txn_id"])
        # Dates: 01, 02, 03 (None), 04, 05, 08, 09, 10, 11, 12
        # Amounts: 10, 20, None, 40, 50, 60, 70, 80, 90, 100
        # 12-01: 0.0
        # 12-02: 10.0
        # 12-03: 30.0 (10+20)
        # 12-04: 60.0 (10+20+None+40 -> 10+20+40=70.0. Wait, `rolling().sum()` skips NaNs. So (10+20+40) = 70.0. Previous: 10+20+None+40. If txn_amount is None it will be skipped from sum. So 10+20=30.0)
        # Re-calculating for null_heavy ACCT_0001
        # Dates: 01, 02, 03, 04, 05, 08, 09, 10, 11, 12
        # Amounts: 10, 20, NaN, 40, 50, 60, 70, 80, 90, 100
        #
        # 12-01 (10): 0.0
        # 12-02 (20): 10.0
        # 12-03 (NaN): 30.0 (10+20)
        # 12-04 (40): 30.0 (10+20+NaN)
        # 12-05 (50): 70.0 (10+20+NaN+40)
        # 12-08 (60): 110.0 (20+NaN+40+50)
        # 12-09 (70): 150.0 (NaN+40+50+60)
        # 12-10 (80): 220.0 (40+50+60+70)
        # 12-11 (90): 260.0 (50+60+70+80)
        # 12-12 (100): 300.0 (60+70+80+90)

        expected_rolling_sums_null_heavy = [0.0, 10.0, 30.0, 30.0, 70.0, 110.0, 150.0, 220.0, 260.0, 300.0]
        pd.testing.assert_series_equal(
            acct1_df_null_heavy["rolling_7day_sum_txn_amount"].reset_index(drop=True),
            pd.Series(expected_rolling_sums_null_heavy, dtype='float64'),
            check_dtype=False, check_exact=False
        )

    # For duplicate_heavy, check that duplicate transactions within the window are summed correctly
    elif variant == "duplicate_heavy":
        acct1_df_dup_heavy = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0001"].sort_values(by=["txn_date", "txn_id"])
        # Dates: 01 (TXN_000001), 01 (TXN_999999), 01 (TXN_000001_dup), 02, 03, 04, 05, 08, 09, 10, 11, 12
        # Amounts: 10, 10, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100
        # Sorted:
        # 12-01, TXN_000001 -> 10
        # 12-01, TXN_999999 -> 10
        # 12-02, TXN_000002 -> 20
        # 12-03, TXN_000003 -> 30
        # 12-04, TXN_000004 -> 40
        # 12-05, TXN_000005 -> 50
        # 12-08, TXN_000006 -> 60
        # 12-09, TXN_000007 -> 70
        # 12-10, TXN_000008 -> 80
        # 12-11, TXN_000009 -> 90
        # 12-12, TXN_000010 -> 100
        # (The fixture logic for duplicate_heavy does not add a `TXN_000001_dup` with a distinct `txn_id`, it just adds `TXN_000001` again, and `TXN_999999`)
        # Let's assume the fixture logic effectively leads to 3 entries for 12-01, each 10.0
        # Original has 10 rows. Add `dup_txn` (1 row, date 12-01, amount 10) and `dup_txn_2` (1 row, date 12-01, amount 10)
        # So on 12-01, there are 3 transactions (10.0, 10.0, 10.0)
        #
        # Recalculating for duplicate_heavy ACCT_0001
        # Dates (sorted, unique): 01, 02, 03, 04, 05, 08, 09, 10, 11, 12
        # Txns per date & amount:
        # 12-01: (10, 10, 10) -> sum=30
        # 12-02: (20) -> sum=20
        # 12-03: (30) -> sum=30
        # 12-04: (40) -> sum=40
        # 12-05: (50) -> sum=50
        # 12-08: (60) -> sum=60
        # 12-09: (70) -> sum=70
        # 12-10: (80) -> sum=80
        # 12-11: (90) -> sum=90
        # 12-12: (100) -> sum=100

        # Rolling sums (closed="left")
        # 12-01 (val=10): sum(empty) = 0.0 (3 rows with txn_id TXN_000001, TXN_999999, TXN_000001, but all have amount 10)
        # The key is that `groupby("account_id")["txn_amount"].rolling("7D", closed="left").sum()` will apply to individual rows.
        # So each of the 3 rows on 12-01 will get a rolling sum of 0.0.
        # The row (TXN_000002, 12-02, 20) will get rolling sum of (10+10+10) = 30.0
        # The row (TXN_000003, 12-03, 30) will get rolling sum of (10+10+10+20) = 50.0
        # This indicates my manual calculation for clean variant was also likely flawed if I was considering sums of multiple txns on the same day.
        # No, the clean variant was fine as each date was unique.
        # The issue is how `rolling` interacts with duplicate indices (if `txn_date` were the index). But here, `txn_date` is a column.
        # Let's re-simulate the output correctly given `closed="left"`
        
        # Expected values for ACCT_0001, 7-day rolling sum, closed="left"
        # Row 1 (12-01, 10): 0.0
        # Row 2 (12-01, 10): 0.0
        # Row 3 (12-02, 20): 10.0 + 10.0 = 20.0 (previous 2 txns on 12-01)
        # Row 4 (12-03, 30): 10.0 + 10.0 + 20.0 = 40.0 (previous txns on 12-01, 12-02)
        # Row 5 (12-04, 40): 10.0 + 10.0 + 20.0 + 30.0 = 70.0
        # Row 6 (12-05, 50): 10.0 + 10.0 + 20.0 + 30.0 + 40.0 = 110.0
        # Row 7 (12-08, 60): 20.0 + 30.0 + 40.0 + 50.0 + 60.0 = 200.0 (from 12-02 to 12-05 + 12-08. No, 12-02 to 12-07)
        # Correct logic for rolling sum (7D, closed="left") for ACCT_0001, sorted by txn_date, txn_id:
        # Data:
        # txn_date   txn_amount txn_id
        # 2024-12-01  10.0   SYNTHETIC_TXN_000001 (original)
        # 2024-12-01  10.0   SYNTHETIC_TXN_999999 (dup_txn_2)
        # 2024-12-02  20.0   SYNTHETIC_TXN_000002
        # 2024-12-03  30.0   SYNTHETIC_TXN_000003
        # 2024-12-04  40.0   SYNTHETIC_TXN_000004
        # 2024-12-05  50.0   SYNTHETIC_TXN_000005
        # 2024-12-08  60.0   SYNTHETIC_TXN_000006
        # 2024-12-09  70.0   SYNTHETIC_TXN_000007
        # 2024-12-10  80.0   SYNTHETIC_TXN_000008
        # 2024-12-11  90.0   SYNTHETIC_TXN_000009
        # 2024-12-12 100.0   SYNTHETIC_TXN_000010

        # Manual calc of rolling sum:
        # Row index 0 (12-01, TXN_000001, 10.0): prev 7D = empty. Sum = 0.0
        # Row index 1 (12-01, TXN_999999, 10.0): prev 7D = empty. Sum = 0.0
        # Row index 2 (12-02, TXN_000002, 20.0): prev 7D (2024-11-25 to 2024-12-01). Sum = 10.0 (TXN_000001) + 10.0 (TXN_999999) = 20.0
        # Row index 3 (12-03, TXN_000003, 30.0): prev 7D (2024-11-26 to 2024-12-02). Sum = 10.0 + 10.0 + 20.0 = 40.0
        # Row index 4 (12-04, TXN_000004, 40.0): prev 7D (2024-11-27 to 2024-12-03). Sum = 10.0 + 10.0 + 20.0 + 30.0 = 70.0
        # Row index 5 (12-05, TXN_000005, 50.0): prev 7D (2024-11-28 to 2024-12-04). Sum = 10.0 + 10.0 + 20.0 + 30.0 + 40.0 = 110.0
        # Row index 6 (12-08, TXN_000006, 60.0): prev 7D (2024-12-01 to 2024-12-07). Sum = (10+10+20+30+40+50) = 160.0
        # Row index 7 (12-09, TXN_000007, 70.0): prev 7D (2024-12-02 to 2024-12-08). Sum = (20+30+40+50+60) = 200.0
        # Row index 8 (12-10, TXN_000008, 80.0): prev 7D (2024-12-03 to 2024-12-09). Sum = (30+40+50+60+70) = 250.0
        # Row index 9 (12-11, TXN_000009, 90.0): prev 7D (2024-12-04 to 2024-12-10). Sum = (40+50+60+70+80) = 300.0
        # Row index 10 (12-12, TXN_000010, 100.0): prev 7D (2024-12-05 to 2024-12-11). Sum = (50+60+70+80+90) = 350.0

        expected_rolling_sums_dup_heavy = [
            0.0, 0.0, 20.0, 40.0, 70.0, 110.0, 160.0, 200.0, 250.0, 300.0, 350.0
        ]
        pd.testing.assert_series_equal(
            acct1_df_dup_heavy["rolling_7day_sum_txn_amount"].reset_index(drop=True),
            pd.Series(expected_rolling_sums_dup_heavy, dtype='float64'),
            check_dtype=False, check_exact=False
        )

    # For medium and large, ensure non-empty output and rolling total column exists
