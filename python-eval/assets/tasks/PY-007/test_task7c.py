import pandas as pd
import pytest
from pathlib import Path
import importlib, sys

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).resolve().parent))
task7c = importlib.import_module("task7c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task7c.py | Tests: task7c.py (PY-007)
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
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 6)],
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 6)],
        "txn_date": ["2023-01-05", "2023-02-20", "2023-03-25", "2023-04-15", "2023-05-10"],
        "txn_amount": [100.0, 200.0, 50.0, 150.0, 300.0],
        "txn_type": ["PURCHASE", "REFUND", "PURCHASE", "FEE", "PURCHASE"],
        "merchant_category": ["RETAIL"] * 5,
        "channel": ["ONLINE"] * 5,
        "is_flagged": [False, False, True, False, True],
    }
    df = pd.DataFrame(base_data)

    if variant == "null_heavy":
        df.loc[0, "txn_amount"] = None  # Null in txn_amount
        df.loc[2, "txn_type"] = None     # Null in grouping column
    elif variant == "duplicate_heavy":
        # Add duplicates for existing txn_type to increase count and sum
        duplicate_rows = pd.DataFrame({
            "txn_id": ["SYNTHETIC_TXN_000006", "SYNTHETIC_TXN_000007"],
            "account_id": ["SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0002"],
            "txn_date": ["2023-01-05", "2023-02-20"],
            "txn_amount": [100.0, 200.0],
            "txn_type": ["PURCHASE", "REFUND"],
            "merchant_category": ["RETAIL", "GROCERY"],
            "channel": ["ONLINE", "BRANCH"],
            "is_flagged": [False, False],
        })
        df = pd.concat([df, duplicate_rows], ignore_index=True)
    elif variant == "medium":
        df = pd.concat([df] * 10, ignore_index=True)
    elif variant == "large":
        df = pd.concat([df] * 100, ignore_index=True)

    transactions_path = tmp_path / f"synthetic_{variant}_transactions.csv"
    with open(transactions_path, 'w') as f: f.write("H1,H2,H3,H4,H5,H6,H7,H8\n")
    df.to_csv(transactions_path, mode='a', index=False, header=False)
    
    return transactions_path


@pytest.mark.parametrize(
    "variant",
    ["clean", "null_heavy", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task7c_run_function(transactions_path: Path, variant: str):
    """
    Tests the run function from task7c.py to group transactions by txn_type
    and compute total txn_amount and row count for various dataset variants.
    """
    # Dummy paths for accounts and balances as they are not used in task7c.run
    accounts_path = Path("dummy_accounts.csv")
    balances_path = Path("dummy_balances.csv")

    result_df = task7c.run(accounts_path, transactions_path, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty, "Resulting DataFrame should not be empty (unless input was empty)"

    # Assert expected columns are present
    expected_columns = ["txn_type", "total_txn_amount", "transaction_count"]
    assert sorted(list(result_df.columns)) == sorted(expected_columns)

    # Assertions for clean variant
    if variant == "clean":
        expected_data_clean = {
            "txn_type": ["FEE", "PURCHASE", "REFUND"],
            "total_txn_amount": [150.0, 450.0, 200.0], # 150, 100+50+300, 200
            "transaction_count": [1, 3, 1]
        }
        expected_df_clean = pd.DataFrame(expected_data_clean).sort_values(by="txn_type").reset_index(drop=True)
        result_df_sorted = result_df.sort_values(by="txn_type").reset_index(drop=True)
        pd.testing.assert_frame_equal(result_df_sorted, expected_df_clean, check_dtype=False)

    # Assertions for null_heavy variant
    elif variant == "null_heavy":
        # Original: [100.0, 200.0, 50.0, 150.0, 300.0]
        # Nulls: df.loc[0, "txn_amount"] = None (100.0 -> None)
        #        df.loc[2, "txn_type"] = None (PURCHASE(50.0) -> None)
        # Expected groups:
        # PURCHASE (orig idx 1, 4): txn_amount: 200.0, 300.0 => total_txn_amount: 500.0, transaction_count: 2 (txn_id counts non-null grouping key)
        # REFUND (orig idx 2): txn_amount: 200.0 => total_txn_amount: 200.0, transaction_count: 1
        # FEE (orig idx 3): txn_amount: 150.0 => total_txn_amount: 150.0, transaction_count: 1
        # None (orig idx 0, 2): txn_amount: None, 50.0 (one txn_amount is null, one txn_type is null)
        # When txn_type is null, it forms its own group. txn_amount=None will be skipped by sum(). count() will count non-null txn_ids.
        # So, the original txn_id=0, txn_amount=None, txn_type=PURCHASE will be grouped under None. Its txn_amount is None.
        # The original txn_id=2, txn_amount=50.0, txn_type=PURCHASE will be grouped under None. Its txn_amount is 50.0.
        # Group None: total_txn_amount: 50.0, transaction_count: 2
        expected_data_null_heavy = {
            "txn_type": ["FEE", "PURCHASE", "REFUND", None],
            "total_txn_amount": [150.0, 500.0, 200.0, 50.0], # 150, 200+300, 200, 50
            "transaction_count": [1, 2, 1, 2]
        }
        expected_df_null_heavy = pd.DataFrame(expected_data_null_heavy).sort_values(by="txn_type", na_position='last').reset_index(drop=True)
        result_df_sorted = result_df.sort_values(by="txn_type", na_position='last').reset_index(drop=True)
        pd.testing.assert_frame_equal(result_df_sorted, expected_df_null_heavy, check_dtype=False)

    # Assertions for duplicate_heavy variant
    elif variant == "duplicate_heavy":
        # base_data has 5 rows: PURCHASE (100, 50, 300), REFUND (200), FEE (150)
        # duplicate_rows has 2 rows: PURCHASE (100), REFUND (200)
        # Combined:
        # PURCHASE: [100.0, 50.0, 300.0, 100.0] -> sum=550.0, count=4
        # REFUND:   [200.0, 200.0] -> sum=400.0, count=2
        # FEE:      [150.0] -> sum=150.0, count=1
        expected_data_duplicate_heavy = {
            "txn_type": ["FEE", "PURCHASE", "REFUND"],
            "total_txn_amount": [150.0, 550.0, 400.0],
            "transaction_count": [1, 4, 2]
        }
        expected_df_duplicate_heavy = pd.DataFrame(expected_data_duplicate_heavy).sort_values(by="txn_type").reset_index(drop=True)
        result_df_sorted = result_df.sort_values(by="txn_type").reset_index(drop=True)
        pd.testing.assert_frame_equal(result_df_sorted, expected_df_duplicate_heavy, check_dtype=False)

    # Assertions for medium and large variants
    elif variant == "medium":
        # Expect counts and sums to be scaled by 10
        assert result_df["transaction_count"].sum() == 5 * 10
        assert result_df["total_txn_amount"].sum() == (100+200+50+150+300) * 10
    elif variant == "large":
        # Expect counts and sums to be scaled by 100
        assert result_df["transaction_count"].sum() == 5 * 100
        assert result_df["total_txn_amount"].sum() == (100+200+50+150+300) * 100
