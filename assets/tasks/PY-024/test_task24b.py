import importlib
import pathlib
import sys

import pandas as pd
import pytest

# SYNTHETIC DATA — no real financial data
# Pytest: test_task24b.py | Tests: task24b.py (PY-024)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

TASK_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TASK_DIR))
task = importlib.import_module("task24b")

DATASET_DIR = pathlib.Path(__file__).resolve().parents[2] / "datasets"


@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task24b_scd2(variant: str) -> None:
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"

    out = task.run(accounts_path, transactions_path, balances_path)
    assert isinstance(out, pd.DataFrame)
    expected_cols = {
        "account_id",
        "customer_segment",
        "account_status",
        "region",
        "effective_start_date",
        "effective_end_date",
    }
    assert expected_cols.issubset(set(out.columns))
    assert out["effective_start_date"].notna().all()
    assert out["effective_end_date"].notna().all()
