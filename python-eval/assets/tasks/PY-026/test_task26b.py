import importlib
import pathlib
import sys

import pandas as pd
import pytest

# SYNTHETIC DATA — no real financial data
# Pytest: test_task26b.py | Tests: task26b.py (PY-026)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

TASK_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TASK_DIR))
task = importlib.import_module("task26b")

DATASET_DIR = pathlib.Path(__file__).resolve().parents[2] / "datasets"


@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task26b_funnel(variant: str) -> None:
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"

    out = task.run(accounts_path, transactions_path, balances_path)
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 1
    for col in [
        "accounts_opened",
        "accounts_with_first_transaction",
        "accounts_with_first_flagged_transaction",
        "dropoff_opened_to_first_txn",
        "dropoff_first_txn_to_first_flagged_txn",
    ]:
        assert col in out.columns
    assert out["dropoff_opened_to_first_txn"].between(0.0, 1.0).all()
    assert out["dropoff_first_txn_to_first_flagged_txn"].between(0.0, 1.0).all()
