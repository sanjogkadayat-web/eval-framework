import importlib
import pathlib
import sys

import pandas as pd
import pytest

# SYNTHETIC DATA — no real financial data
# Pytest: test_task1b.py | Tests: task1b.py (PY-001)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

TASK_DIR = pathlib.Path(__file__).resolve().parents[1] / "answers_python"
sys.path.insert(0, str(TASK_DIR))
task = importlib.import_module("task1b")

DATASET_DIR = pathlib.Path(__file__).resolve().parents[2] / "datasets"


@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task1b_run(variant: str) -> None:
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"

    df = task.run(accounts_path, transactions_path, balances_path)
    assert isinstance(df, pd.DataFrame)

    expected_columns = [
        "account_id",
        "customer_segment",
        "account_open_date",
        "account_status",
        "region",
    ]
    assert list(df.columns) == expected_columns
    assert len(df) > 0
