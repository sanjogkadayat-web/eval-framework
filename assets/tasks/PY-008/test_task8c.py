import pandas as pd
import pytest
from pathlib import Path
import importlib, sys

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).resolve().parent))
task8c = importlib.import_module("task8c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task8c.py | Tests: task8c.py (PY-008)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).resolve().parents[2] / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def setup_data(tmp_path: Path, variant: str):
    """
    Fixture to create dummy accounts and transactions CSV files for different variants.
    """
    # Base accounts data
    accounts_data = {
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 6)],
        "customer_segment": ["RETAIL", "SMALL_BIZ", "WEALTH", "STUDENT", "RETAIL"],
        "account_open_date": ["2023-01-01", "2023-02-15", "2023-03-20", "2023-04-10", "2023-05-05"],
        "account_status": ["ACTIVE"] * 5,
        "region": ["NORTH", "SOUTH", "EAST", "WEST", "NORTH"],
    }
    accounts_df = pd.DataFrame(accounts_data)

    # Base transactions data
    transactions_data = {
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 11)],
        "account_id": [
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0002", 
            "SYNTHETIC_ACCT_0003", "SYNTHETIC_ACCT_0004", "SYNTHETIC_ACCT_0001", 
            "SYNTHETIC_ACCT_0002", "SYNTHETIC_ACCT_0003", "SYNTHETIC_ACCT_0005", 
            "SYNTHETIC_ACCT_0005"
        ],
        "txn_date": [f"2023-01-{i+1:02d}" for i in range(10)],
        "txn_amount": [100.0, 50.0, 200.0, 75.0, 300.0, 120.0, 180.0, 90.0, 250.0, 110.0],
        "txn_type": ["PURCHASE"] * 10,
        "merchant_category": ["RETAIL"] * 10,
        "channel": ["ONLINE", "BRANCH", "ONLINE", "ATM", "MOBILE", "ONLINE", "BRANCH", "ATM", "MOBILE", "ONLINE"],
        "is_flagged": [False] * 10,
    }
    transactions_df = pd.DataFrame(transactions_data)

    if variant == "null_heavy":
        accounts_df.loc[0, "region"] = None # Null region
        transactions_df.loc[1, "channel"] = None # Null channel
        transactions_df.loc[3, "txn_amount"] = None # Null txn_amount
    elif variant == "duplicate_heavy":
        # Add a duplicate transaction that affects total_txn_amount
        dup_txn = pd.DataFrame({
            "txn_id": ["SYNTHETIC_TXN_000001"], "account_id": ["SYNTHETIC_ACCT_0001"],
            "txn_date": ["2023-01-01"], "txn_amount": [100.0], "txn_type": ["PURCHASE"],
            "merchant_category": ["RETAIL"], "channel": ["ONLINE"], "is_flagged": [False]
        })
        transactions_df = pd.concat([transactions_df, dup_txn], ignore_index=True)
    elif variant == "medium":
        accounts_df = pd.concat([accounts_df] * 10, ignore_index=True)
        transactions_df = pd.concat([transactions_df] * 10, ignore_index=True)
    elif variant == "large":
        accounts_df = pd.concat([accounts_df] * 50, ignore_index=True)
        transactions_df = pd.concat([transactions_df] * 50, ignore_index=True)

    accounts_path = tmp_path / f"synthetic_{variant}_accounts.csv"
    transactions_path = tmp_path / f"synthetic_{variant}_transactions.csv"
    balances_path = tmp_path / f"synthetic_{variant}_daily_balances.csv" # Not used, but required by run signature

    with open(accounts_path, 'w') as f: f.write("H1,H2,H3,H4,H5\n")
    accounts_df.to_csv(accounts_path, mode='a', index=False, header=False)
    
    with open(transactions_path, 'w') as f: f.write("H1,H2,H3,H4,H5,H6,H7,H8\n")
    transactions_df.to_csv(transactions_path, mode='a', index=False, header=False)

    # Create a dummy balances file as it's required by the run signature but not used in this task
    pd.DataFrame(columns=["account_id", "balance_date", "closing_balance", "txn_count_day"]).to_csv(balances_path, index=False, header=True)

    return accounts_path, transactions_path, balances_path


@pytest.mark.parametrize(
    "variant",
    ["clean", "null_heavy", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task8c_run_function(setup_data: tuple[Path, Path, Path], variant: str):
    """
    Tests the run function from task8c.py to build a pivot table of total txn_amount
    by region and channel for various dataset variants.
    """
    accounts_path, transactions_path, balances_path = setup_data

    result_df = task8c.run(accounts_path, transactions_path, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty, "Resulting DataFrame should not be empty (unless filtered to empty)"

    # Assert expected index and columns of the pivot table
    expected_index = sorted(["NORTH", "SOUTH", "EAST", "WEST", None]) if variant == "null_heavy" else sorted(["NORTH", "SOUTH", "EAST", "WEST"])
    expected_columns = sorted(["ONLINE", "BRANCH", "ATM", "MOBILE", None]) if variant == "null_heavy" else sorted(["ONLINE", "BRANCH", "ATM", "MOBILE"])

    if not result_df.index.name == "region":
        # If reset_index was called, region would be a column, not index
        assert "region" in result_df.columns
        # For pivot table, index is 'region', columns are 'channel'
        assert sorted(result_df["region"].dropna().unique()) == sorted(["EAST", "NORTH", "SOUTH", "WEST"])
        assert sorted(result_df.columns.drop("region").tolist()) == sorted(["ATM", "BRANCH", "MOBILE", "ONLINE"])
    else:
        # Directly check index and columns if it's a pivot_table output
        assert result_df.index.name == "region"
        assert sorted(result_df.index.dropna().tolist()) == sorted(["EAST", "NORTH", "SOUTH", "WEST"])
        assert sorted(result_df.columns.dropna().tolist()) == sorted(["ATM", "BRANCH", "MOBILE", "ONLINE"])


    # Assertions for clean variant
    if variant == "clean":
        expected_data = {
            "ATM":    {"EAST": 0.0, "NORTH": 0.0, "SOUTH": 0.0, "WEST": 75.0},
            "BRANCH": {"EAST": 0.0, "NORTH": 50.0, "SOUTH": 180.0, "WEST": 0.0},
            "MOBILE": {"EAST": 0.0, "NORTH": 0.0, "SOUTH": 0.0, "WEST": 300.0},
            "ONLINE": {"EAST": 0.0, "NORTH": 220.0, "SOUTH": 0.0, "WEST": 0.0}
        }

        # Accounts df:
        # 0001: NORTH
        # 0002: SOUTH
        # 0003: EAST
        # 0004: WEST
        # 0005: NORTH
        
        # Transactions df:
        # 100.0, SYNTHETIC_ACCT_0001, ONLINE
        # 50.0,  SYNTHETIC_ACCT_0001, BRANCH
        # 200.0, SYNTHETIC_ACCT_0002, ONLINE
        # 75.0,  SYNTHETIC_ACCT_0003, ATM
        # 300.0, SYNTHETIC_ACCT_0004, MOBILE
        # 120.0, SYNTHETIC_ACCT_0001, ONLINE
        # 180.0, SYNTHETIC_ACCT_0002, BRANCH
        # 90.0,  SYNTHETIC_ACCT_0003, ATM
        # 250.0, SYNTHETIC_ACCT_0005, MOBILE -> This account_id is NORTH, not WEST, so the 300.0 for MOBILE should come from here.
        # 110.0, SYNTHETIC_ACCT_0005, ONLINE

        # Corrected expected_data based on account_id mapping to region
        expected_data_corrected = {
            "ATM":    {"EAST": 75.0 + 90.0, "NORTH": 0.0, "SOUTH": 0.0, "WEST": 0.0}, # from ACCT_0003 (EAST) 75.0, 90.0
            "BRANCH": {"EAST": 0.0, "NORTH": 50.0, "SOUTH": 180.0, "WEST": 0.0}, # from ACCT_0001 (NORTH) 50.0, ACCT_0002 (SOUTH) 180.0
            "MOBILE": {"EAST": 0.0, "NORTH": 250.0, "SOUTH": 0.0, "WEST": 300.0}, # from ACCT_0005 (NORTH) 250.0, ACCT_0004 (WEST) 300.0
            "ONLINE": {"EAST": 0.0, "NORTH": 100.0 + 120.0 + 110.0, "SOUTH": 200.0, "WEST": 0.0} # from ACCT_0001 (NORTH) 100.0, 120.0, ACCT_0002 (SOUTH) 200.0, ACCT_0005 (NORTH) 110.0
        }

        # Convert to DataFrame for comparison
        expected_pivot_df = pd.DataFrame(expected_data_corrected).reindex(index=sorted(expected_data_corrected.keys()), columns=sorted(expected_data_corrected["ONLINE"].keys()))
        expected_pivot_df.index.name = "region"
        expected_pivot_df.columns.name = "channel"
        
        # Reindex the result_df to match the expected_pivot_df index and columns for comparison
        result_reindexed = result_df.reindex(index=expected_pivot_df.index, columns=expected_pivot_df.columns, fill_value=0.0)

        pd.testing.assert_frame_equal(result_reindexed, expected_pivot_df, check_dtype=False, check_like=True)

    # Variant-aware assertions for null_heavy
    elif variant == "null_heavy":
        # Expect nulls in `region` and `channel` to appear as their own group/column in pivot table.
        # Null `txn_amount` should be ignored in sum.
        # ACCT_0001 (region=NORTH) has a transaction with channel=None
        # The transaction with txn_amount=None (for ACCT_0003, ATM) should not contribute to sum.

        # Recalculate based on specific null_heavy scenario
        # accounts_df.loc[0, "region"] = None # ACCT_0001 region is now None
        # transactions_df.loc[1, "channel"] = None # ACCT_0001 (txn_id 2, txn_amount 50.0) channel is None
        # transactions_df.loc[3, "txn_amount"] = None # ACCT_0003 (txn_id 4, txn_amount 75.0 -> None) txn_amount is None

        # Account 0001: (NORTH->None) - (100.0, ONLINE), (50.0, BRANCH->None), (120.0, ONLINE)
        # Account 0002: (SOUTH) - (200.0, ONLINE), (180.0, BRANCH)
        # Account 0003: (EAST) - (75.0->None, ATM), (90.0, ATM)
        # Account 0004: (WEST) - (300.0, MOBILE)
        # Account 0005: (NORTH) - (250.0, MOBILE), (110.0, ONLINE)

        expected_data_null_heavy = {
            "ATM":    {"EAST": 90.0, "NORTH": 0.0, "SOUTH": 0.0, "WEST": 0.0, None: 0.0}, # only 90.0 from ACCT_0003 (EAST) remains, 75.0 is null
            "BRANCH": {"EAST": 0.0, "NORTH": 0.0, "SOUTH": 180.0, "WEST": 0.0, None: 0.0}, # 50.0 from ACCT_0001 (None) is now in None channel group.
            "MOBILE": {"EAST": 0.0, "NORTH": 250.0, "SOUTH": 0.0, "WEST": 300.0, None: 0.0},
            "ONLINE": {"EAST": 0.0, "NORTH": 100.0 + 110.0, "SOUTH": 200.0, "WEST": 0.0, None: 0.0}, # 100.0, 110.0 from ACCT_0001,0005 (None, NORTH), 200.0 from ACCT_0002 (SOUTH)
            None:     {"EAST": 0.0, "NORTH": 0.0, "SOUTH": 0.0, "WEST": 0.0, None: 50.0} # ACCT_0001 (region None), channel None: 50.0
        }

        expected_pivot_df = pd.DataFrame(expected_data_null_heavy).reindex(index=sorted(expected_data_null_heavy.keys()), columns=sorted(expected_data_null_heavy["ATM"].keys()))
        expected_pivot_df.index.name = "region"
        expected_pivot_df.columns.name = "channel"
        
        # Reindex the result_df to match the expected_pivot_df index and columns for comparison
        result_reindexed = result_df.reindex(index=expected_pivot_df.index, columns=expected_pivot_df.columns, fill_value=0.0)
        pd.testing.assert_frame_equal(result_reindexed, expected_pivot_df, check_dtype=False, check_like=True)

    # For duplicate_heavy, check sums with duplicates considered
    elif variant == "duplicate_heavy":
        # Original total amounts:
        # ATM: 75.0 (A3) + 90.0 (A3) = 165.0
        # BRANCH: 50.0 (A1) + 180.0 (A2) = 230.0
        # MOBILE: 300.0 (A4) + 250.0 (A5) = 550.0
        # ONLINE: 100.0 (A1) + 200.0 (A2) + 120.0 (A1) + 110.0 (A5) = 530.0
        
        # Duplicate transaction: (100.0, SYNTHETIC_ACCT_0001, ONLINE)
        # This should increase NORTH-ONLINE by 100.0
        # So NORTH-ONLINE should be 530.0 (original) + 100.0 = 630.0
        expected_data_dup = {
            "ATM":    {"EAST": 165.0, "NORTH": 0.0, "SOUTH": 0.0, "WEST": 0.0},
            "BRANCH": {"EAST": 0.0, "NORTH": 50.0, "SOUTH": 180.0, "WEST": 0.0},
            "MOBILE": {"EAST": 0.0, "NORTH": 250.0, "SOUTH": 0.0, "WEST": 300.0},
            "ONLINE": {"EAST": 0.0, "NORTH": 100.0 + 120.0 + 110.0 + 100.0, "SOUTH": 200.0, "WEST": 0.0}
        }

        expected_pivot_df = pd.DataFrame(expected_data_dup).reindex(index=sorted(expected_data_dup.keys()), columns=sorted(expected_data_dup["ONLINE"].keys()))
        expected_pivot_df.index.name = "region"
        expected_pivot_df.columns.name = "channel"
        
        result_reindexed = result_df.reindex(index=expected_pivot_df.index, columns=expected_pivot_df.columns, fill_value=0.0)
        pd.testing.assert_frame_equal(result_reindexed, expected_pivot_df, check_dtype=False, check_like=True)

    # For medium and large variants, check that sums are scaled correctly
    elif variant == "medium":
        # Sum of all txn_amounts in base_data is 100+50+200+75+300+120+180+90+250+110 = 1475.0
        assert result_df.sum().sum() == pytest.approx(1475.0 * 10)
    elif variant == "large":
        assert result_df.sum().sum() == pytest.approx(1475.0 * 50)
