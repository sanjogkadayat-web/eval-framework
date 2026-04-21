import pandas as pd
import pytest
from pathlib import Path
import importlib, sys
import numpy as np

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).parent.parent / "assets" / "tasks_a" / "answers_python"))
task19c = importlib.import_module("task19c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task19c.py | Tests: task19c.py (PY-019)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).parent.parent / "assets" / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def accounts_path(tmp_path: Path, variant: str):
    """
    Fixture to create dummy accounts CSV files for different variants
    with varied account statuses and potential duplicates.
    """
    base_data = {
        "account_id": [
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0002",
            "SYNTHETIC_ACCT_0002", "SYNTHETIC_ACCT_0003", "SYNTHETIC_ACCT_0003",
            "SYNTHETIC_ACCT_0004", "SYNTHETIC_ACCT_0005"
        ],
        "customer_segment": [
            "RETAIL", "RETAIL", "SMALL_BIZ", "SMALL_BIZ",
            "WEALTH", "WEALTH", "STUDENT", "STUDENT"
        ],
        "account_open_date": [
            "2023-01-01", "2023-01-15", # ACCT_0001
            "2023-02-01", "2023-02-10", # ACCT_0002
            "2023-03-01", "2023-03-10", # ACCT_0003
            "2023-04-01", # ACCT_0004
            "2023-05-01"  # ACCT_0005
        ],
        "account_status": [
            "CLOSED", "ACTIVE", # ACCT_0001: Active (2023-01-15) should win
            "SUSPENDED", "ACTIVE", # ACCT_0002: Active (2023-02-10) should win
            "CLOSED", "SUSPENDED", # ACCT_0003: Suspended (2023-03-10) should win
            "ACTIVE", # ACCT_0004: Only one
            "CLOSED"  # ACCT_0005: Only one
        ],
        "region": [
            "NORTH", "NORTH", "SOUTH", "SOUTH",
            "EAST", "EAST", "WEST", "WEST"
        ],
    }
    df = pd.DataFrame(base_data)

    if variant == "null_heavy":
        df.loc[df["account_id"] == "SYNTHETIC_ACCT_0001", "account_status"].iloc[1] = None # ACCT_0001, Active -> None
        df.loc[df["account_id"] == "SYNTHETIC_ACCT_0003", "account_status"].iloc[1] = None # ACCT_0003, Suspended -> None
    elif variant == "duplicate_heavy":
        # Add more duplicates, specifically with tied status_rank but different open_date
        # ACCT_0001: Add another ACTIVE, older open date (should still pick the one specified in base_data, as per tie-breaking rule)
        dup_active_older = pd.DataFrame({
            "account_id": ["SYNTHETIC_ACCT_0001"],
            "customer_segment": ["WEALTH"],
            "account_open_date": ["2023-01-05"], # Older than 2023-01-15
            "account_status": ["ACTIVE"],
            "region": ["NORTH"],
        })
        df = pd.concat([df, dup_active_older], ignore_index=True)

        # ACCT_0003: Add another SUSPENDED, older open date (should pick the one specified in base_data)
        dup_suspended_older = pd.DataFrame({
            "account_id": ["SYNTHETIC_ACCT_0003"],
            "customer_segment": ["WEALTH"],
            "account_open_date": ["2023-03-05"], # Older than 2023-03-10
            "account_status": ["SUSPENDED"],
            "region": ["EAST"],
        })
        df = pd.concat([df, dup_suspended_older], ignore_index=True)

    elif variant == "medium":
        df = pd.concat([df] * 10, ignore_index=True)
    elif variant == "large":
        df = pd.concat([df] * 100, ignore_index=True)

    accounts_path = tmp_path / f"synthetic_{variant}_accounts.csv"
    transactions_path = tmp_path / f"synthetic_{variant}_transactions.csv" # Dummy
    balances_path = tmp_path / f"synthetic_{variant}_daily_balances.csv"   # Dummy

    with open(accounts_path, 'w') as f: f.write("H1,H2,H3,H4,H5\n")
    df.to_csv(accounts_path, mode='a', index=False, header=False)

    # Create dummy empty files for transactions and balances as they are required by the run signature
    pd.DataFrame(columns=[]).to_csv(transactions_path, index=False)
    pd.DataFrame(columns=[]).to_csv(balances_path, index=False)

    return accounts_path, transactions_path, balances_path


@pytest.mark.parametrize(
    "variant",
    ["clean", "null_heavy", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task19c_run_function(accounts_path: tuple[Path, Path, Path], variant: str):
    """
    Tests the run function from task19c.py to deduplicate accounts based on
    account_status precedence (ACTIVE > SUSPENDED > CLOSED) for various dataset variants.
    """
    accounts_path_arg, transactions_path, balances_path = accounts_path

    result_df = task19c.run(accounts_path_arg, transactions_path, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty, "Resulting DataFrame should not be empty"

    # Assert expected columns are present (temporary 'status_rank' should be dropped)
    expected_columns = [
        "account_id", "customer_segment", "account_open_date", "account_status", "region"
    ]
    assert sorted(list(result_df.columns)) == sorted(expected_columns)
    assert "status_rank" not in result_df.columns

    # Assert that 'account_id' is unique after deduplication
    assert result_df["account_id"].is_unique

    # For clean variant, verify the specific deduplication logic
    if variant == "clean":
        # ACCT_0001: CLOSED (2023-01-01), ACTIVE (2023-01-15) -> Expect ACTIVE (2023-01-15)
        # ACCT_0002: SUSPENDED (2023-02-01), ACTIVE (2023-02-10) -> Expect ACTIVE (2023-02-10)
        # ACCT_0003: CLOSED (2023-03-01), SUSPENDED (2023-03-10) -> Expect SUSPENDED (2023-03-10)
        # ACCT_0004: ACTIVE (2023-04-01) -> Expect ACTIVE (2023-04-01)
        # ACCT_0005: CLOSED (2023-05-01) -> Expect CLOSED (2023-05-01)

        expected_data = {
            "account_id": [
                "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0002", "SYNTHETIC_ACCT_0003",
                "SYNTHETIC_ACCT_0004", "SYNTHETIC_ACCT_0005"
            ],
            "customer_segment": [
                "RETAIL", "SMALL_BIZ", "WEALTH",
                "STUDENT", "STUDENT"
            ],
            "account_open_date": [
                pd.Timestamp("2023-01-15"), # ACCT_0001
                pd.Timestamp("2023-02-10"), # ACCT_0002
                pd.Timestamp("2023-03-10"), # ACCT_0003
                pd.Timestamp("2023-04-01"), # ACCT_0004
                pd.Timestamp("2023-05-01")  # ACCT_0005
            ],
            "account_status": [
                "ACTIVE", "ACTIVE", "SUSPENDED",
                "ACTIVE", "CLOSED"
            ],
            "region": [
                "NORTH", "SOUTH", "EAST",
                "WEST", "WEST"
            ],
        }
        expected_df = pd.DataFrame(expected_data).sort_values(by="account_id").reset_index(drop=True)
        result_df_sorted = result_df.sort_values(by="account_id").reset_index(drop=True)

        pd.testing.assert_frame_equal(result_df_sorted, expected_df, check_dtype=False)

    # For null_heavy variant, check how null statuses are handled (should be lowest rank)
    elif variant == "null_heavy":
        # ACCT_0001: CLOSED (01-01), None (01-15) -> Expect CLOSED (01-01) if None is treated as lowest rank
        # ACCT_0003: CLOSED (03-01), None (03-10) -> Expect CLOSED (03-01) if None is treated as lowest rank
        # In task19c.py, if status is None, .map(status_precedence) will result in NaN, which for sorting purposes is usually treated as last.
        # So a non-null status should win over a null status.

        # ACCT_0001: CLOSED (rank 3), ACTIVE (rank 1) -> ACTIVE (2023-01-15)
        # Modified: CLOSED (rank 3), None (rank NaN) -> CLOSED (2023-01-01) because NaN is larger than 3
        acct1_result = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0001"]
        assert acct1_result["account_status"].iloc[0] == "CLOSED"
        assert acct1_result["account_open_date"].iloc[0] == pd.Timestamp("2023-01-01")

        # ACCT_0003: CLOSED (rank 3), SUSPENDED (rank 2) -> SUSPENDED (2023-03-10)
        # Modified: CLOSED (rank 3), None (rank NaN) -> CLOSED (2023-03-01)
        acct3_result = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0003"]
        assert acct3_result["account_status"].iloc[0] == "CLOSED"
        assert acct3_result["account_open_date"].iloc[0] == pd.Timestamp("2023-03-01")

    # For duplicate_heavy, ensure correct tie-breaking
    elif variant == "duplicate_heavy":
        # ACCT_0001:
        # Original: CLOSED (2023-01-01), ACTIVE (2023-01-15)
        # Added dup: ACTIVE (2023-01-05)
        # Sorted by [account_id, status_rank, account_open_date]:
        # ACTIVE (2023-01-05, customer_segment WEALTH) - rank 1
        # ACTIVE (2023-01-15, customer_segment RETAIL) - rank 1
        # CLOSED (2023-01-01, customer_segment RETAIL) - rank 3
        # Expect: ACTIVE (2023-01-05) because it's first by default in case of tie. No, account_open_date is second tie-breaker.
        # With `sort_values(by=["account_id", "status_rank", "account_open_date", "customer_segment"], keep="first")`
        # ACCT_0001, ACTIVE, 2023-01-05, WEALTH should win.
        acct1_result = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0001"]
        assert acct1_result["account_status"].iloc[0] == "ACTIVE"
        assert acct1_result["account_open_date"].iloc[0] == pd.Timestamp("2023-01-05")
        assert acct1_result["customer_segment"].iloc[0] == "WEALTH"

        # ACCT_0003:
        # Original: CLOSED (2023-03-01), SUSPENDED (2023-03-10)
        # Added dup: SUSPENDED (2023-03-05)
        # Sorted by [account_id, status_rank, account_open_date, customer_segment]:
        # SUSPENDED (2023-03-05, WEALTH) - rank 2
        # SUSPENDED (2023-03-10, WEALTH) - rank 2
        # CLOSED (2023-03-01, WEALTH) - rank 3
        # Expect: SUSPENDED (2023-03-05) because of earlier open date.
        acct3_result = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0003"]
        assert acct3_result["account_status"].iloc[0] == "SUSPENDED"
        assert acct3_result["account_open_date"].iloc[0] == pd.Timestamp("2023-03-05")
        assert acct3_result["customer_segment"].iloc[0] == "WEALTH"

    # For medium and large variants, ensure it completes without error
    # and the number of rows equals the number of unique account_ids
    elif variant == "medium":
        original_df = pd.read_csv(accounts_path_arg, skiprows=1)
        assert len(result_df) == original_df["account_id"].nunique()
    elif variant == "large":
        original_df = pd.read_csv(accounts_path_arg, skiprows=1)
        assert len(result_df) == original_df["account_id"].nunique()
