import importlib
import pathlib
import sys

import pandas as pd
import pytest

# SYNTHETIC DATA — no real financial data
# Pytest: test_task30b.py | Tests: task30b.py (PY-030)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

TASK_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TASK_DIR))
task = importlib.import_module("task30b")

DATASET_DIR = pathlib.Path(__file__).resolve().parents[2] / "datasets"


@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task30b_dummy_transform_and_run(variant: str) -> None:
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"

    df = pd.read_csv(accounts_path, skiprows=1)
    out_df = task.dummy_transform_function(df)
    assert isinstance(out_df, pd.DataFrame)
    pd.testing.assert_frame_equal(out_df, df)

    result = task.run(accounts_path, transactions_path, balances_path)
    assert result is None
