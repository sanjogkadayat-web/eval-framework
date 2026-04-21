import importlib
import pathlib
import sys

import pandas as pd
import pytest

# SYNTHETIC DATA — no real financial data
# Pytest: test_task5b.py | Tests: task5b.py (PY-005)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

TASK_DIR = pathlib.Path(__file__).resolve().parents[1] / "answers_python"
sys.path.insert(0, str(TASK_DIR))
task = importlib.import_module("task5b")

DATASET_DIR = pathlib.Path(__file__).resolve().parents[2] / "datasets"


@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task5b_run(variant: str) -> None:
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"

    out = task.run(accounts_path, transactions_path, balances_path)
    assert isinstance(out, pd.DataFrame)
    assert {"txn_id", "is_flagged", "txn_amount"}.issubset(set(out.columns))

    if not out.empty:
        out_amt = pd.to_numeric(out["txn_amount"], errors="coerce")
        assert (out["is_flagged"] == True).all()
        assert (out_amt > 500.0).all()
