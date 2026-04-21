import importlib
import pathlib
import sys

import pandas as pd
import pytest

# SYNTHETIC DATA — no real financial data
# Pytest: test_task12b.py | Tests: task12b.py (PY-012)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

TASK_DIR = pathlib.Path(__file__).resolve().parents[1] / "answers_python"
sys.path.insert(0, str(TASK_DIR))
task = importlib.import_module("task12b")

DATASET_DIR = pathlib.Path(__file__).resolve().parents[2] / "datasets"


@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task12b_running_total(variant: str) -> None:
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"

    out = task.run(accounts_path, transactions_path, balances_path)
    assert isinstance(out, pd.DataFrame)
    assert "running_total_txn_amount" in out.columns

    chk = out.dropna(subset=["account_id"]).copy()
    if not chk.empty:
        sums = pd.to_numeric(chk["txn_amount"], errors="coerce").fillna(0.0).groupby(chk["account_id"]).sum()
        lasts = chk.sort_values(["account_id", "txn_date", "txn_id"], kind="stable").groupby("account_id")[
            "running_total_txn_amount"
        ].last()
        pd.testing.assert_series_equal(lasts.sort_index(), sums.sort_index(), check_names=False)
