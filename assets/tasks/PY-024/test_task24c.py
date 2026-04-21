import pandas as pd
import pytest
from pathlib import Path
import importlib, sys
import numpy as np

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).resolve().parent))
task24c = importlib.import_module("task24c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task24c.py | Tests: task24c.py (PY-024)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).resolve().parents[2] / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def accounts_path(tmp_path: Path, variant: str):
    """
    Fixture to create dummy accounts CSV files for different variants
    to test SCD Type 2 implementation.
    """
    base_data = {
        "account_id": [
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001",
            "SYNTHETIC_ACCT_0002", "SYNTHETIC_ACCT_0002",
            "SYNTHETIC_ACCT_0003"
        ],
        "customer_segment": [
            "RETAIL", "RETAIL", "WEALTH",
            "SMALL_BIZ", "SMALL_BIZ",
            "STUDENT"
        ],
        "account_open_date": [
            "2023-01-01", "2023-01-10", "2023-01-15", # ACCT_0001: Closed->Suspended->Active
            "2023-02-01", "2023-02-15", # ACCT_0002: Active->Closed
            "2023-03-01"  # ACCT_0003: Active
        ],
        "account_status": [
            "CLOSED", "SUSPENDED", "ACTIVE",
            "ACTIVE", "CLOSED",
            "ACTIVE"
        ],
        "region": [
            "NORTH", "NORTH", "NORTH",
            "SOUTH", "SOUTH",
            "EAST"
        ],
    }
    df = pd.DataFrame(base_data)

    if variant == "null_heavy":
        # Introduce nulls in key columns for SCD2 logic
        # ACCT_0001: 2nd status (Suspended) becomes Null -> should treat as a change
        df.loc[1, "account_status"] = None
        # ACCT_0002: 1st open date becomes Null -> should be handled in sorting / initial record logic
        df.loc[3, "account_open_date"] = None
        # ACCT_0003: Account status becomes Null
        df.loc[5, "account_status"] = None

    elif variant == "duplicate_heavy":
        # Add more duplicates, specifically with tied account_open_date and account_status
        # ACCT_0001: Add another ACTIVE on 2023-01-15 but different segment (should still pick first by status_rank)
        dup_active = pd.DataFrame({
            "account_id": ["SYNTHETIC_ACCT_0001"],
            "customer_segment": ["STUDENT"],
            "account_open_date": ["2023-01-15"],
            "account_status": ["ACTIVE"],
            "region": ["NORTH"],
        })
        df = pd.concat([df, dup_active], ignore_index=True)

        # ACCT_0002: Add another ACTIVE on 2023-02-01 but different region
        dup_active_acct2 = pd.DataFrame({
            "account_id": ["SYNTHETIC_ACCT_0002"],
            "customer_segment": ["SMALL_BIZ"],
            "account_open_date": ["2023-02-01"],
            "account_status": ["ACTIVE"],
            "region": ["WEST"],
        })
        df = pd.concat([df, dup_active_acct2], ignore_index=True)

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
def test_task24c_run_function(accounts_path: tuple[Path, Path, Path], variant: str):
    """
    Tests the run function from task24c.py for SCD Type 2 history tracking for
    account_status changes across account snapshots for various dataset variants.
    """
    accounts_path_arg, transactions_path, balances_path = accounts_path

    result_df = task24c.run(accounts_path_arg, transactions_path, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty, "Resulting DataFrame should not be empty"

    # Assert expected columns are present
    expected_columns = [
        "account_id", "customer_segment", "account_status", "region",
        "effective_start_date", "effective_end_date"
    ]
    assert sorted(list(result_df.columns)) == sorted(expected_columns)

    # Assert date columns are datetime
    assert pd.api.types.is_datetime64_any_dtype(result_df["effective_start_date"])
    assert pd.api.types.is_datetime64_any_dtype(result_df["effective_end_date"])

    # Assert for clean variant
    if variant == "clean":
        # ACCT_0001: CLOSED (2023-01-01) -> SUSPENDED (2023-01-10) -> ACTIVE (2023-01-15)
        # Expected records for ACCT_0001:
        # 1. CLOSED, start: 2023-01-01, end: 2023-01-09
        # 2. SUSPENDED, start: 2023-01-10, end: 2023-01-14
        # 3. ACTIVE, start: 2023-01-15, end: 9999-12-31
        acct1_df = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0001"].sort_values(by="effective_start_date")
        assert len(acct1_df) == 3
        assert acct1_df.iloc[0]["account_status"] == "CLOSED"
        assert acct1_df.iloc[0]["effective_start_date"] == pd.Timestamp("2023-01-01")
        assert acct1_df.iloc[0]["effective_end_date"] == pd.Timestamp("2023-01-09")

        assert acct1_df.iloc[1]["account_status"] == "SUSPENDED"
        assert acct1_df.iloc[1]["effective_start_date"] == pd.Timestamp("2023-01-10")
        assert acct1_df.iloc[1]["effective_end_date"] == pd.Timestamp("2023-01-14")

        assert acct1_df.iloc[2]["account_status"] == "ACTIVE"
        assert acct1_df.iloc[2]["effective_start_date"] == pd.Timestamp("2023-01-15")
        assert acct1_df.iloc[2]["effective_end_date"] == pd.Timestamp("9999-12-31")

        # ACCT_0002: ACTIVE (2023-02-01) -> CLOSED (2023-02-15)
        # Expected records for ACCT_0002:
        # 1. ACTIVE, start: 2023-02-01, end: 2023-02-14
        # 2. CLOSED, start: 2023-02-15, end: 9999-12-31
        acct2_df = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0002"].sort_values(by="effective_start_date")
        assert len(acct2_df) == 2
        assert acct2_df.iloc[0]["account_status"] == "ACTIVE"
        assert acct2_df.iloc[0]["effective_start_date"] == pd.Timestamp("2023-02-01")
        assert acct2_df.iloc[0]["effective_end_date"] == pd.Timestamp("2023-02-14")

        assert acct2_df.iloc[1]["account_status"] == "CLOSED"
        assert acct2_df.iloc[1]["effective_start_date"] == pd.Timestamp("2023-02-15")
        assert acct2_df.iloc[1]["effective_end_date"] == pd.Timestamp("9999-12-31")

        # ACCT_0003: ACTIVE (2023-03-01)
        # Expected record for ACCT_0003:
        # 1. ACTIVE, start: 2023-03-01, end: 9999-12-31
        acct3_df = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0003"]
        assert len(acct3_df) == 1
        assert acct3_df.iloc[0]["account_status"] == "ACTIVE"
        assert acct3_df.iloc[0]["effective_start_date"] == pd.Timestamp("2023-03-01")
        assert acct3_df.iloc[0]["effective_end_date"] == pd.Timestamp("9999-12-31")

    # Assert for null_heavy variant
    elif variant == "null_heavy":
        # account_open_date = None for ACCT_0002 (first record) -> should be NaT, effective_end_date also NaT or 9999-12-31
        # account_status = None for ACCT_0001 (second record) -> should trigger a change from CLOSED to None
        # account_status = None for ACCT_0003 (only record) -> should result in one record with status None

        # ACCT_0001: CLOSED (2023-01-01) -> None (2023-01-10) -> ACTIVE (2023-01-15)
        acct1_df = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0001"].sort_values(by="effective_start_date")
        assert len(acct1_df) == 3
        assert acct1_df.iloc[0]["account_status"] == "CLOSED"
        assert acct1_df.iloc[0]["effective_start_date"] == pd.Timestamp("2023-01-01")
        assert acct1_df.iloc[0]["effective_end_date"] == pd.Timestamp("2023-01-09")

        assert acct1_df.iloc[1]["account_status"] is None or pd.isna(acct1_df.iloc[1]["account_status"])
        assert acct1_df.iloc[1]["effective_start_date"] == pd.Timestamp("2023-01-10")
        assert acct1_df.iloc[1]["effective_end_date"] == pd.Timestamp("2023-01-14")

        assert acct1_df.iloc[2]["account_status"] == "ACTIVE"
        assert acct1_df.iloc[2]["effective_start_date"] == pd.Timestamp("2023-01-15")
        assert acct1_df.iloc[2]["effective_end_date"] == pd.Timestamp("9999-12-31")

        # ACCT_0002: None (account_open_date) -> CLOSED (2023-02-15)
        # If account_open_date is None, pd.to_datetime makes it NaT. NaT will be sorted first by default if not handled.
        # In task24c, `accounts_df.sort_values(by=["account_id", "account_open_date", "status_rank", "customer_segment", "region"])`
        # NaT is typically sorted first for datetime columns. So the first record will have NaT.
        acct2_df = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0002"].sort_values(by="effective_start_date")
        assert len(acct2_df) == 2
        assert pd.isna(acct2_df.iloc[0]["effective_start_date"]) # This first record starts with NaT
        assert acct2_df.iloc[0]["account_status"] == "ACTIVE" # This is the original status for that row
        assert acct2_df.iloc[0]["effective_end_date"] == pd.Timestamp("2023-02-14")
        assert acct2_df.iloc[1]["effective_start_date"] == pd.Timestamp("2023-02-15")
        assert acct2_df.iloc[1]["account_status"] == "CLOSED"
        assert acct2_df.iloc[1]["effective_end_date"] == pd.Timestamp("9999-12-31")

        # ACCT_0003: None (account_status) (2023-03-01)
        acct3_df = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0003"]
        assert len(acct3_df) == 1
        assert acct3_df.iloc[0]["account_status"] is None or pd.isna(acct3_df.iloc[0]["account_status"])
        assert acct3_df.iloc[0]["effective_start_date"] == pd.Timestamp("2023-03-01")
        assert acct3_df.iloc[0]["effective_end_date"] == pd.Timestamp("9999-12-31")

    # Assert for duplicate_heavy variant
    elif variant == "duplicate_heavy":
        # ACCT_0001: CLOSED (2023-01-01) -> SUSPENDED (2023-01-10) -> ACTIVE (2023-01-15)
        # Added dup: ACTIVE (2023-01-15, STUDENT segment)
        # Based on sorting (status_rank, open_date, customer_segment), the first ACTIVE (RETAIL) at 2023-01-15 wins tie-breaker if it comes first in original dataframe order.
        # However, the task description implies: `accounts_df.sort_values(by=["account_id", "account_open_date", "status_rank", "customer_segment", "region"])` will ensure deterministic result.
        # Original order of 2023-01-15, ACTIVE is (RETAIL, NORTH)
        # Duplicated is (STUDENT, NORTH)
        # So RETAIL should come before STUDENT, so original should win.

        acct1_df = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0001"].sort_values(by="effective_start_date")
        assert len(acct1_df) == 3
        assert acct1_df.iloc[0]["account_status"] == "CLOSED"
        assert acct1_df.iloc[0]["effective_start_date"] == pd.Timestamp("2023-01-01")
        assert acct1_df.iloc[0]["effective_end_date"] == pd.Timestamp("2023-01-09")

        assert acct1_df.iloc[1]["account_status"] == "SUSPENDED"
        assert acct1_df.iloc[1]["effective_start_date"] == pd.Timestamp("2023-01-10")
        assert acct1_df.iloc[1]["effective_end_date"] == pd.Timestamp("2023-01-14")

        assert acct1_df.iloc[2]["account_status"] == "ACTIVE"
        assert acct1_df.iloc[2]["effective_start_date"] == pd.Timestamp("2023-01-15")
        assert acct1_df.iloc[2]["customer_segment"] == "RETAIL" # Should pick original RETAIL over STUDENT
        assert acct1_df.iloc[2]["effective_end_date"] == pd.Timestamp("9999-12-31")

        # ACCT_0002: ACTIVE (2023-02-01) -> CLOSED (2023-02-15)
        # Added dup: ACTIVE (2023-02-01) with region WEST
        # Sorting order is account_id, open_date, status_rank, customer_segment, region
        # So (2023-02-01, ACTIVE, SMALL_BIZ, SOUTH) should win over (2023-02-01, ACTIVE, SMALL_BIZ, WEST) given SOUTH < WEST
        acct2_df = result_df[result_df["account_id"] == "SYNTHETIC_ACCT_0002"].sort_values(by="effective_start_date")
        assert len(acct2_df) == 2
        assert acct2_df.iloc[0]["account_status"] == "ACTIVE"
        assert acct2_df.iloc[0]["effective_start_date"] == pd.Timestamp("2023-02-01")
        assert acct2_df.iloc[0]["region"] == "SOUTH" # Original one wins
        assert acct2_df.iloc[0]["effective_end_date"] == pd.Timestamp("2023-02-14")

        assert acct2_df.iloc[1]["account_status"] == "CLOSED"
        assert acct2_df.iloc[1]["effective_start_date"] == pd.Timestamp("2023-02-15")
        assert acct2_df.iloc[1]["effective_end_date"] == pd.Timestamp("9999-12-31")

    # For medium and large variants, simply ensure it completes without error
    # and the number of records is plausible (e.g., at least as many as unique account_ids).
    elif variant == "medium":
        original_df_path = Path(accounts_path_arg)
        original_df = pd.read_csv(original_df_path, skiprows=1)
        # With scaling by 10, expect total number of records to be scaled.
        # Unique account_ids (3) * 10 = 30 initial records. SCD2 logic will then expand them.
        # In clean variant, ACCT_0001 (3), ACCT_0002 (2), ACCT_0003 (1) = 6 records.
        # So 6 * 10 = 60 records expected.
        assert len(result_df) == 6 * 10
        assert result_df["account_id"].nunique() == 3 # Still 3 unique accounts
    elif variant == "large":
        original_df_path = Path(accounts_path_arg)
        original_df = pd.read_csv(original_df_path, skiprows=1)
        # 6 * 100 = 600 records expected.
        assert len(result_df) == 6 * 100
        assert result_df["account_id"].nunique() == 3 # Still 3 unique accounts
