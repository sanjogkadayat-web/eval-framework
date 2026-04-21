import importlib
import pathlib
import sys

import pandas as pd
import pytest

# SYNTHETIC DATA — no real financial data
# Pytest: test_task13b.py | Tests: task13b.py (PY-013)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

TASK_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TASK_DIR))
task = importlib.import_module("task13b")

DATASET_DIR = pathlib.Path(__file__).resolve().parents[2] / "datasets"


@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task13b_rolling_avg(variant: str) -> None:
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"

    out = task.run(accounts_path, transactions_path, balances_path)
    assert isinstance(out, pd.DataFrame)
    assert "rolling_avg_7_obs" in out.columns
    assert len(out) > 0
