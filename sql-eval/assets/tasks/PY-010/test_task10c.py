import pandas as pd
import pytest
from pathlib import Path
import importlib, sys

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).resolve().parent))
task10c = importlib.import_module("task10c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task10c.py | Tests: task10c.py (PY-010)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).resolve().parents[2] / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def transactions_path(tmp_path: Path, variant: str):
    """
    Fixture to create dummy transactions CSV files for different variants
    with varied channel types and potential nulls.
    """
    base_data = {
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 11)],
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 11)],
        "txn_date": [f"2023-01-{i:02d}" for i in range(1, 11)],
        "txn_amount": [100.0, 200.0, 50.0, 150.0, 300.0, 120.0, 180.0, 90.0, 250.0, 110.0],
        "txn_type": ["PURCHASE"] * 10,
        "merchant_category": ["RETAIL"] * 10,
        "channel": [
            "ONLINE", "BRANCH", "KIOSK", "ATM", "MOBILE",
            "BRANCH", "ONLINE", "OTHER", "ATM", "BRANCH"
        ],
        "is_flagged": [False] * 10,
    }
    df = pd.DataFrame(base_data)

    if variant == "null_heavy":
        df.loc[2, "channel"] = None  # Null channel, should be flagged as invalid
        df.loc[7, "channel"] = None  # Another null channel
    elif variant == "duplicate_heavy":
        # Add duplicates, some with valid, some with invalid channels
        dup_data = pd.DataFrame({
            "txn_id": ["SYNTHETIC_TXN_000001", "SYNTHETIC_TXN_000003", "SYNTHETIC_TXN_000011"],
            "account_id": ["SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0003", "SYNTHETIC_ACCT_0001"],
            "txn_date": ["2023-01-01", "2023-01-03", "2023-01-11"],
            "txn_amount": [100.0, 50.0, 20.0],
            "txn_type": ["PURCHASE", "PURCHASE", "REFUND"],
            "merchant_category": ["RETAIL", "RETAIL", "RETAIL"],
            "channel": ["ONLINE", "KIOSK", "WEB"],
            "is_flagged": [False, False, False],
        })
        df = pd.concat([df, dup_data], ignore_index=True)
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
def test_task10c_run_function(transactions_path: Path, variant: str):
    """
    Tests the run function from task10c.py to flag transactions whose channel
    is not in the allowed set {ATM, BRANCH, MOBILE, ONLINE} for various dataset variants.
    """
    # Dummy paths for accounts and balances as they are not used in task10c.run
    accounts_path = Path("dummy_accounts.csv")
    balances_path = Path("dummy_balances.csv")

    result_df = task10c.run(accounts_path, transactions_path, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty, "Resulting DataFrame should not be empty (unless input was empty)"

    # Assert 'is_invalid_channel' column is present
    assert "is_invalid_channel" in result_df.columns
    assert result_df["is_invalid_channel"].dtype == "bool"

    # Define allowed channels as in task10c.py
    allowed_channels = {"ATM", "BRANCH", "MOBILE", "ONLINE"}

    # Assert correctness of the 'is_invalid_channel' flag
    for index, row in result_df.iterrows():
        channel = row["channel"]
        is_invalid_flag = row["is_invalid_channel"]

        if pd.isna(channel):
            # NaN channels should be considered invalid
            assert is_invalid_flag is True, f"Expected NaN channel to be flagged as invalid at index {index}"
        else:
            expected_flag = channel not in allowed_channels
            assert is_invalid_flag == expected_flag, \
                f"Mismatch at index {index}: channel={channel}, expected_flag={expected_flag}, actual_flag={is_invalid_flag}"

    # Specific checks for duplicate_heavy to ensure consistent flagging across duplicates
    if variant == "duplicate_heavy":
        # Original data has KIOSK (True), OTHER (True). Added WEB (True).
        # Duplicated ONLINE (False) and KIOSK (True)
        # Ensure flags are consistent for duplicate entries
        duplicates_check_df = result_df[result_df.duplicated(subset=["txn_id", "account_id"], keep=False)]
        for _, group in duplicates_check_df.groupby(["txn_id", "account_id"]):
            assert group["is_invalid_channel"].nunique() == 1, \
                f"Duplicate entries for txn_id/account_id have inconsistent is_invalid_channel flags"

    # For large variants, simply ensure it completes without error, relying on pandas efficiency
    # (memory assertion is handled by the framework runtime)
