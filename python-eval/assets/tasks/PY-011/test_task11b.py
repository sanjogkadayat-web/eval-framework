import importlib
import pathlib
import shutil
import sys

import pandas as pd
import pytest

# SYNTHETIC DATA — no real financial data
# Pytest: test_task11b.py | Tests: task11b.py (PY-011)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

TASK_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TASK_DIR))
task = importlib.import_module("task11b")

DATASET_DIR = pathlib.Path(__file__).resolve().parents[2] / "datasets"


@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task11b_run_writes_output(variant: str, tmp_path: pathlib.Path) -> None:
    src_accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    accounts_path = tmp_path / src_accounts_path.name
    shutil.copyfile(src_accounts_path, accounts_path)

    transactions_path = tmp_path / f"synthetic_{variant}_transactions.csv"
    balances_path = tmp_path / f"synthetic_{variant}_daily_balances.csv"
    transactions_path.write_text("")
    balances_path.write_text("")

    result = task.run(accounts_path, transactions_path, balances_path)
    assert result is None

    out_path = tmp_path / "processed_active_accounts.csv"
    assert out_path.exists()

    out_df = pd.read_csv(out_path)
    assert "account_status" in out_df.columns
    if not out_df.empty:
        assert (out_df["account_status"] == "ACTIVE").all()
