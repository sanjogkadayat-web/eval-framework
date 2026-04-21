"""
Bootstrap script for "b" task assets.

Creates the required layout:
  assets/tasks/{task_id}/task{N}b.sql
  assets/tasks/{task_id}/task{N}b.py
  assets/tasks/{task_id}/test_task{N}b.py

Also writes assets/tasks/{task_id}/prompt.txt from assets/task_prompts_b.yaml.

This is intentionally additive: it does not delete the existing assets/tasks_b tree.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml


VARIANTS = ["clean", "null_heavy", "duplicate_heavy", "medium", "large"]


def _task_id_sql(n: int) -> str:
    return f"SQL-{n:03d}"


def _task_id_py(n: int) -> str:
    return f"PY-{n:03d}"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def bootstrap(repo_root: Path) -> None:
    assets_dir = repo_root / "assets"
    prompts_path = assets_dir / "task_prompts_b.yaml"
    prompts = yaml.safe_load(_read_text(prompts_path))
    sql_prompts: dict[str, str] = prompts.get("sql", {})
    py_prompts: dict[str, str] = prompts.get("python", {})

    tasks_root = assets_dir / "tasks"

    # Source trees currently present in repo
    src_sql = assets_dir / "tasks_b" / "answers_sql"
    src_py = assets_dir / "tasks_b" / "answers_python"
    src_pytest = assets_dir / "tasks_b" / "pytest"

    for n in range(1, 31):
        # SQL
        task_id = _task_id_sql(n)
        dest_dir = tasks_root / task_id
        dest_sql = dest_dir / f"task{n}b.sql"
        prompt = sql_prompts.get(task_id, "")
        _write_text(dest_dir / "prompt.txt", prompt + ("\n" if prompt and not prompt.endswith("\n") else ""))
        _copy_file(src_sql / f"task{n}b.sql", dest_sql)

        # Python
        task_id = _task_id_py(n)
        dest_dir = tasks_root / task_id
        dest_py = dest_dir / f"task{n}b.py"
        dest_test = dest_dir / f"test_task{n}b.py"
        prompt = py_prompts.get(task_id, "")
        _write_text(dest_dir / "prompt.txt", prompt + ("\n" if prompt and not prompt.endswith("\n") else ""))

        _copy_file(src_py / f"task{n}b.py", dest_py)

        # Rewrite the test to import from the same directory (new layout).
        # We keep the test logic identical otherwise.
        test_src = src_pytest / f"test_task{n}b.py"
        test_text = _read_text(test_src)
        # Minimal deterministic rewrite:
        # - TASK_DIR becomes the current directory
        # - DATASET_DIR remains assets/datasets (flat variant filenames) to match existing datasets
        test_text = test_text.replace(
            'TASK_DIR = pathlib.Path(__file__).resolve().parents[1] / "answers_python"\n'
            "sys.path.insert(0, str(TASK_DIR))\n",
            "TASK_DIR = pathlib.Path(__file__).resolve().parent\nsys.path.insert(0, str(TASK_DIR))\n",
        )
        test_text = test_text.replace(
            'DATASET_DIR = pathlib.Path(__file__).resolve().parents[2] / "datasets"\n',
            'DATASET_DIR = pathlib.Path(__file__).resolve().parents[2] / "datasets"\n',
        )
        _write_text(dest_test, test_text)


def bootstrap_datasets_variant_folders(repo_root: Path) -> None:
    """
    Optional: create assets/datasets/{variant}/synthetic_{table}.csv
    from the existing flat files assets/datasets/synthetic_{variant}_{table}.csv
    """

    assets_dir = repo_root / "assets"
    datasets_dir = assets_dir / "datasets"

    for variant in VARIANTS:
        for table in ["accounts", "transactions", "daily_balances"]:
            src = datasets_dir / f"synthetic_{variant}_{table}.csv"
            if not src.exists():
                continue
            dst = datasets_dir / variant / f"synthetic_{table}.csv"
            _copy_file(src, dst)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    bootstrap(root)
    bootstrap_datasets_variant_folders(root)

