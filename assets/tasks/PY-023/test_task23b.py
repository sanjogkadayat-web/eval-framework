import importlib
import pathlib
import shutil
import sys

import pytest

# SYNTHETIC DATA — no real financial data
# Pytest: test_task23b.py | Tests: task23b.py (PY-023)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

TASK_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TASK_DIR))
task = importlib.import_module("task23b")

DATASET_DIR = pathlib.Path(__file__).resolve().parents[2] / "datasets"


@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task23b_end_to_end_pipeline_writes_outputs(
    variant: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    src_accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    src_transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    src_balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"

    accounts_path = tmp_path / src_accounts_path.name
    transactions_path = tmp_path / src_transactions_path.name
    balances_path = tmp_path / src_balances_path.name

    shutil.copyfile(src_accounts_path, accounts_path)
    shutil.copyfile(src_transactions_path, transactions_path)
    shutil.copyfile(src_balances_path, balances_path)

    monkeypatch.chdir(tmp_path)
    result = task.run(accounts_path, transactions_path, balances_path)
    assert result is None

    out_dir = tmp_path / "processed_data"
    assert out_dir.exists()
    assert (out_dir / "conformed_accounts.csv").exists()
    assert (out_dir / "conformed_transactions.csv").exists()
    assert (out_dir / "conformed_daily_balances.csv").exists()
