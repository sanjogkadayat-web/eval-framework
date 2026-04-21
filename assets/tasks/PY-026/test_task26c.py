import pandas as pd
import pytest
from pathlib import Path
import importlib, sys
import numpy as np

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).resolve().parent))
task26c = importlib.import_module("task26c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task26c.py | Tests: task26c.py (PY-026)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).resolve().parents[2] / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def setup_data(tmp_path: Path, variant: str):
    """
    Fixture to create dummy accounts and transactions CSV files for different variants
    to test funnel drop-off calculation.
    """
    # Base Accounts Data
    base_accounts_data = {
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 6)],
        "customer_segment": ["RETAIL"] * 5,
        "account_open_date": [f"2023-01-0{i}" for i in range(1, 6)],
        "account_status": ["ACTIVE"] * 5,
        "region": ["NORTH"] * 5,
    }
    accounts_df = pd.DataFrame(base_accounts_data)

    # Base Transactions Data
    base_transactions_data = {
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 11)],
        "account_id": [
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", # ACCT_0001: 2 txns, 1 flagged
            "SYNTHETIC_ACCT_0002", "SYNTHETIC_ACCT_0002", # ACCT_0002: 2 txns, 1 flagged
            "SYNTHETIC_ACCT_0003", # ACCT_0003: 1 txn, not flagged
            "SYNTHETIC_ACCT_0001", # ACCT_0001: another txn
            "SYNTHETIC_ACCT_0004", # ACCT_0004: 1 txn, not flagged
            "SYNTHETIC_ACCT_0002", # ACCT_0002: another txn
            "SYNTHETIC_ACCT_0001", # ACCT_0001: another txn
            "SYNTHETIC_ACCT_0005"  # ACCT_0005: 1 txn, not flagged
        ],
        "txn_date": [
            "2023-01-05", "2023-01-06", # ACCT_0001
            "2023-02-05", "2023-02-06", # ACCT_0002
            "2023-03-05", # ACCT_0003
            "2023-01-07", # ACCT_0001
            "2023-04-05", # ACCT_0004
            "2023-02-07", # ACCT_0002
            "2023-01-08", # ACCT_0001
            "2023-05-05"  # ACCT_0005
        ],
        "txn_amount": [100.0] * 10,
        "txn_type": ["PURCHASE"] * 10,
        "merchant_category": ["RETAIL"] * 10,
        "channel": ["ONLINE"] * 10,
        "is_flagged": [
            False, True,  # ACCT_0001
            False, True,  # ACCT_0002
            False,        # ACCT_0003
            False,        # ACCT_0001
            False,        # ACCT_0004
            False,        # ACCT_0002
            False,        # ACCT_0001
            False         # ACCT_0005
        ],
    }
    transactions_df = pd.DataFrame(base_transactions_data)

    if variant == "null_heavy":
        # Accounts: ACCT_0001 gets null account_open_date
        accounts_df.loc[0, "account_open_date"] = None
        # Transactions: ACCT_0001's first flagged txn_date becomes null
        transactions_df.loc[1, "txn_date"] = None
        # ACCT_0003's only transaction account_id becomes null
        transactions_df.loc[4, "account_id"] = None
        # ACCT_0004's only transaction is_flagged becomes null
        transactions_df.loc[6, "is_flagged"] = None

    elif variant == "duplicate_heavy":
        # Add exact duplicates for accounts and transactions
        accounts_df = pd.concat([accounts_df, accounts_df.iloc[[0]]], ignore_index=True)
        transactions_df = pd.concat([transactions_df, transactions_df.iloc[[0]]], ignore_index=True)
    elif variant == "medium":
        accounts_df = pd.concat([accounts_df] * 10, ignore_index=True)
        transactions_df = pd.concat([transactions_df] * 10, ignore_index=True)
    elif variant == "large":
        accounts_df = pd.concat([accounts_df] * 100, ignore_index=True)
        transactions_df = pd.concat([transactions_df] * 100, ignore_index=True)

    accounts_path = tmp_path / f"synthetic_{variant}_accounts.csv"
    transactions_path = tmp_path / f"synthetic_{variant}_transactions.csv"
    balances_path = tmp_path / f"synthetic_{variant}_daily_balances.csv" # Dummy

    with open(accounts_path, 'w') as f: f.write("H1,H2,H3,H4,H5\n")
    accounts_df.to_csv(accounts_path, mode='a', index=False, header=False)
    
    with open(transactions_path, 'w') as f: f.write("H1,H2,H3,H4,H5,H6,H7,H8\n")
    transactions_df.to_csv(transactions_path, mode='a', index=False, header=False)

    # Create dummy empty files for balances as they are required by the run signature
    pd.DataFrame(columns=[]).to_csv(balances_path, index=False)

    return accounts_path, transactions_path, balances_path


@pytest.mark.parametrize(
    "variant",
    ["clean", "null_heavy", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task26c_run_function(setup_data: tuple[Path, Path, Path], variant: str):
    """
    Tests the run function from task26c.py to compute funnel drop-off from
    account creation to first transaction to first flagged transaction for various dataset variants.
    """
    accounts_path, transactions_path, balances_path = setup_data

    result_df = task26c.run(accounts_path, transactions_path, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty, "Resulting DataFrame should not be empty"

    # Assert expected columns are present
    expected_columns = ["step", "count", "drop_off_rate"]
    assert sorted(list(result_df.columns)) == sorted(expected_columns)

    # Assert steps are in the correct order
    assert list(result_df["step"]) == ["Account Created", "First Transaction", "First Flagged Transaction"]

    # Assert for clean variant
    if variant == "clean":
        # Accounts: 5 unique (0001, 0002, 0003, 0004, 0005)
        # First Transaction: All 5 accounts have at least one transaction
        # First Flagged Transaction: ACCT_0001 (txn_id 2), ACCT_0002 (txn_id 4)
        # So 2 accounts have flagged transactions
        expected_counts = [5, 5, 2]
        expected_drop_off_rates = [0.0, 0.0, (5 - 2) / 5]

        pd.testing.assert_series_equal(
            result_df["count"].reset_index(drop=True),
            pd.Series(expected_counts, dtype=np.int64),
            check_exact=True
        )
        pd.testing.assert_series_equal(
            result_df["drop_off_rate"].reset_index(drop=True),
            pd.Series(expected_drop_off_rates, dtype=np.float64),
            check_exact=False # Floating point comparison
        )
    
    # Assert for null_heavy variant
    elif variant == "null_heavy":
        # Accounts: 5 unique. ACCT_0001 (null open date), ACCT_0003 (no txns due to null account_id), ACCT_0004 (no flagged txns due to null is_flagged)
        # account_created_count: 5 (all original accounts)
        # First Transaction:
        # ACCT_0001: txns 01-05 (valid), 01-06 (null txn_date, dropped), 01-07 (valid), 01-08 (valid). First valid is 01-05.
        # ACCT_0002: txns 02-05 (valid), 02-06 (valid), 02-07 (valid). First valid is 02-05.
        # ACCT_0003: txn 03-05 (account_id is null, so won't join to accounts). No first txn for ACCT_0003.
        # ACCT_0004: txn 04-05 (valid). First valid is 04-05.
        # ACCT_0005: txn 05-05 (valid). First valid is 05-05.
        # Accounts with first txn: ACCT_0001, ACCT_0002, ACCT_0004, ACCT_0005. So 4 accounts.
        # first_txn_count = 4

        # First Flagged Transaction:
        # ACCT_0001: original (is_flagged: False, True, False, False). First flagged is 01-07.
        # ACCT_0002: original (is_flagged: False, True, False). First flagged is 02-06.
        # ACCT_0004: original (is_flagged: False -> None). No flagged for ACCT_0004.
        # Accounts with first flagged txn: ACCT_0001, ACCT_0002. So 2 accounts.
        # first_flagged_txn_count = 2

        expected_counts = [5, 4, 2]
        expected_drop_off_rates = [0.0, (5 - 4) / 5, (4 - 2) / 4]

        pd.testing.assert_series_equal(
            result_df["count"].reset_index(drop=True),
            pd.Series(expected_counts, dtype=np.int64),
            check_exact=True
        )
        pd.testing.assert_series_equal(
            result_df["drop_off_rate"].reset_index(drop=True),
            pd.Series(expected_drop_off_rates, dtype=np.float64),
            check_exact=False
        )

    # Assert for duplicate_heavy variant
    elif variant == "duplicate_heavy":
        # Accounts: 5 original + 1 dup = 6 rows. Unique accounts: 5.
        # account_created_count = 5

        # Transactions: 10 original + 1 dup = 11 rows. Unique transactions (based on all columns): 10.
        # First transaction: Still all 5 accounts have first transactions.
        # first_txn_count = 5

        # First Flagged Transaction: Still ACCT_0001 and ACCT_0002. The duplicate of ACCT_0001, TXN_000001 is not flagged.
        # first_flagged_txn_count = 2

        expected_counts = [5, 5, 2]
        expected_drop_off_rates = [0.0, 0.0, (5 - 2) / 5]

        pd.testing.assert_series_equal(
            result_df["count"].reset_index(drop=True),
            pd.Series(expected_counts, dtype=np.int64),
            check_exact=True
        )
        pd.testing.assert_series_equal(
            result_df["drop_off_rate"].reset_index(drop=True),
            pd.Series(expected_drop_off_rates, dtype=np.float64),
            check_exact=False
        )

    # For medium and large variants, check the structure and plausibility of counts
    elif variant == "medium":
        assert len(result_df) == 3
        assert result_df["count"].iloc[0] == 5 * 10 # 50 accounts created
        assert result_df["count"].iloc[1] == 5 * 10 # 50 first transactions
        assert result_df["count"].iloc[2] == 2 * 10 # 20 first flagged transactions
        assert result_df["drop_off_rate"].iloc[1] == 0.0
        assert result_df["drop_off_rate"].iloc[2] == (50 - 20) / 50
    elif variant == "large":
        assert len(result_df) == 3
        assert result_df["count"].iloc[0] == 5 * 100 # 500 accounts created
        assert result_df["count"].iloc[1] == 5 * 100 # 500 first transactions
        assert result_df["count"].iloc[2] == 2 * 100 # 200 first flagged transactions
        assert result_df["drop_off_rate"].iloc[1] == 0.0
        assert result_df["drop_off_rate"].iloc[2] == (500 - 200) / 500
