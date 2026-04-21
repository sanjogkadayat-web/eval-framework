import pandas as pd
import pytest
from pathlib import Path
import importlib, sys
import numpy as np

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).parent.parent / "assets" / "tasks_a" / "answers_python"))
task16c = importlib.import_module("task16c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task16c.py | Tests: task16c.py (PY-016)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).parent.parent / "assets" / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def transactions_path(tmp_path: Path, variant: str):
    """
    Fixture to create dummy transactions CSV files for different variants
    with varied transaction dates.
    """
    base_data = {
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 11)],
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 11)],
        "txn_date": [
            "2024-01-01", # Monday
            "2024-01-05", # Friday
            "2024-01-06", # Saturday (weekend)
            "2024-01-07", # Sunday (weekend)
            "2024-02-10", # Saturday (weekend)
            "2024-03-15", # Friday
            "2024-04-20", # Saturday (weekend)
            "2024-05-25", # Saturday (weekend)
            "2024-06-03", # Monday
            "2024-07-15"  # Monday
        ],
        "txn_amount": [100.0] * 10,
        "txn_type": ["PURCHASE"] * 10,
        "merchant_category": ["RETAIL"] * 10,
        "channel": ["ONLINE"] * 10,
        "is_flagged": [False] * 10,
    }
    df = pd.DataFrame(base_data)

    if variant == "null_heavy":
        df.loc[2, "txn_date"] = None  # Null date for a weekend transaction
        df.loc[7, "txn_date"] = None  # Null date for another weekend transaction
    elif variant == "duplicate_heavy":
        # Add duplicates for existing transactions, including some with weekend dates
        dup_data = pd.DataFrame({
            "txn_id": ["SYNTHETIC_TXN_000001", "SYNTHETIC_TXN_000003", "SYNTHETIC_TXN_000011"],
            "account_id": ["SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0003", "SYNTHETIC_ACCT_0001"],
            "txn_date": ["2024-01-01", "2024-01-06", "2024-01-07"],
            "txn_amount": [100.0, 100.0, 100.0],
            "txn_type": ["PURCHASE", "PURCHASE", "PURCHASE"],
            "merchant_category": ["RETAIL", "RETAIL", "RETAIL"],
            "channel": ["ONLINE", "ONLINE", "ONLINE"],
            "is_flagged": [False, False, False],
        })
        df = pd.concat([df, dup_data], ignore_index=True)
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
def test_task16c_run_function(transactions_path: tuple[Path, Path, Path], variant: str):
    """
    Tests the run function from task16c.py to extract day_of_week, month, quarter,
    and is_weekend features from 'txn_date' for various dataset variants.
    """
    accounts_path, transactions_path_arg, balances_path = transactions_path

    result_df = task16c.run(accounts_path, transactions_path_arg, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty, "Resulting DataFrame should not be empty"

    # Assert expected columns are present
    expected_columns = [
        "txn_id", "account_id", "txn_date", "txn_amount", "txn_type",
        "merchant_category", "channel", "is_flagged",
        "day_of_week", "month", "quarter", "is_weekend"
    ]
    assert sorted(list(result_df.columns)) == sorted(expected_columns)

    # Assert dtypes of new columns
    assert result_df["day_of_week"].dtype == "object" # string
    assert pd.api.types.is_integer_dtype(result_df["month"])
    assert pd.api.types.is_integer_dtype(result_df["quarter"])
    assert pd.api.types.is_boolean_dtype(result_df["is_weekend"])

    # Specific checks for clean variant
    if variant == "clean":
        expected_dates = [
            pd.Timestamp("2024-01-01"), # Monday
            pd.Timestamp("2024-01-05"), # Friday
            pd.Timestamp("2024-01-06"), # Saturday
            pd.Timestamp("2024-01-07"), # Sunday
            pd.Timestamp("2024-02-10"), # Saturday
            pd.Timestamp("2024-03-15"), # Friday
            pd.Timestamp("2024-04-20"), # Saturday
            pd.Timestamp("2024-05-25"), # Saturday
            pd.Timestamp("2024-06-03"), # Monday
            pd.Timestamp("2024-07-15")  # Monday
        ]
        expected_day_of_week = [
            "Tuesday", "Saturday", "Sunday", "Monday", "Saturday",
            "Friday", "Saturday", "Saturday", "Monday", "Monday"
        ] # Corrected for 2024 dates
        # 2024-01-01: Monday, Jan (1), Q1, not weekend
        # 2024-01-05: Friday, Jan (1), Q1, not weekend
        # 2024-01-06: Saturday, Jan (1), Q1, weekend
        # 2024-01-07: Sunday, Jan (1), Q1, weekend
        # 2024-02-10: Saturday, Feb (2), Q1, weekend
        # 2024-03-15: Friday, Mar (3), Q1, not weekend
        # 2024-04-20: Saturday, Apr (4), Q2, weekend
        # 2024-05-25: Saturday, May (5), Q2, weekend
        # 2024-06-03: Monday, Jun (6), Q2, not weekend
        # 2024-07-15: Monday, Jul (7), Q3, not weekend

        expected_day_of_week = [
            "Monday", "Friday", "Saturday", "Sunday", "Saturday",
            "Friday", "Saturday", "Saturday", "Monday", "Monday"
        ]
        expected_month = [1, 1, 1, 1, 2, 3, 4, 5, 6, 7]
        expected_quarter = [1, 1, 1, 1, 1, 1, 2, 2, 2, 3]
        expected_is_weekend = [
            False, False, True, True, True,
            False, True, True, False, False
        ]

        for i, row in result_df.iterrows():
            assert row["day_of_week"] == expected_day_of_week[i]
            assert row["month"] == expected_month[i]
            assert row["quarter"] == expected_quarter[i]
            assert row["is_weekend"] == expected_is_weekend[i]

    # For null_heavy variant, check that null dates result in null features
    elif variant == "null_heavy":
        null_date_rows = result_df[result_df["txn_date"].isnull()]
        assert not null_date_rows.empty
        assert null_date_rows["day_of_week"].isnull().all()
        assert null_date_rows["month"].isnull().all()
        assert null_date_rows["quarter"].isnull().all()
        assert null_date_rows["is_weekend"].isnull().all()
    
    # For duplicate_heavy, ensure that duplicates have the same extracted features
    elif variant == "duplicate_heavy":
        # Check for consistency across duplicates based on txn_id and account_id
        duplicates_check_df = result_df[result_df.duplicated(subset=["txn_id", "account_id"], keep=False)]
        for _, group in duplicates_check_df.groupby(["txn_id", "account_id"]):
            assert group["day_of_week"].nunique() == 1
            assert group["month"].nunique() == 1
            assert group["quarter"].nunique() == 1
            assert group["is_weekend"].nunique() == 1

    # For medium and large variants, simply ensure it completes without error
    # and the new columns exist with appropriate dtypes.
