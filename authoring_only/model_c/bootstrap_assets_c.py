"""
Bootstrap script for "c" task assets.

Creates the required layout:
  assets/tasks/{task_id}/task{N}c.sql
  assets/tasks/{task_id}/task{N}c.py
  assets/tasks/{task_id}/test_task{N}c.py

Also writes assets/tasks/{task_id}/prompt.txt from assets/task_prompts_c.yaml.

This is intentionally additive: it does not delete the existing assets/tasks_c tree.
"""

from __future__ import annotations

import re
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


def _copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists():
        print(f"[bootstrap_assets_c] skip missing source: {src}")
        return False
    _copy_file(src, dst)
    return True


def bootstrap(repo_root: Path) -> None:
    assets_dir = repo_root / "assets"
    prompts_path = assets_dir / "task_prompts_c.yaml"
    prompts = yaml.safe_load(_read_text(prompts_path))
    sql_prompts: dict[str, str] = prompts.get("sql", {})
    py_prompts: dict[str, str] = prompts.get("python", {})

    tasks_root = assets_dir / "tasks"

    # Source trees currently present in repo
    src_sql = assets_dir / "tasks_c" / "answers_sql"
    src_py = assets_dir / "tasks_c" / "answers_python"
    src_pytest = assets_dir / "tasks_c" / "pytest"

    for n in range(1, 31):
        # SQL
        task_id = _task_id_sql(n)
        dest_dir = tasks_root / task_id
        dest_sql = dest_dir / f"task{n}c.sql"
        prompt = sql_prompts.get(task_id, "")
        _write_text(dest_dir / "prompt.txt", prompt + ("\n" if prompt and not prompt.endswith("\n") else ""))
        _copy_if_exists(src_sql / f"task{n}c.sql", dest_sql)

        # Python
        task_id = _task_id_py(n)
        dest_dir = tasks_root / task_id
        dest_py = dest_dir / f"task{n}c.py"
        dest_test = dest_dir / f"test_task{n}c.py"
        prompt = py_prompts.get(task_id, "")
        _write_text(dest_dir / "prompt.txt", prompt + ("\n" if prompt and not prompt.endswith("\n") else ""))

        _copy_if_exists(src_py / f"task{n}c.py", dest_py)

        # Rewrite the test to import from the same directory (new layout).
        # We keep the test logic identical otherwise.
        test_src = src_pytest / f"test_task{n}c.py"
        if test_src.exists():
            test_text = _rewrite_test_text(_read_text(test_src))
            _write_text(dest_test, test_text)
        else:
            print(f"[bootstrap_assets_c] skip missing source: {test_src}")


# Model C tests use patterns like:
#   sys.path.insert(0, str(Path(__file__).parent.parent / "assets" / "tasks_a" / "answers_python"))
#   DATASET_DIR = Path(__file__).parent.parent / "assets" / "datasets"
# After the restructure the task module sits in the same directory as the test,
# and datasets are three levels up at assets/datasets.
_SYS_PATH_REPLACEMENT = (
    "sys.path.insert(0, str(Path(__file__).resolve().parent))"
)
_DATASET_DIR_REPLACEMENT = (
    'DATASET_DIR = Path(__file__).resolve().parents[2] / "datasets"'
)

_SYS_PATH_LINE_RE = re.compile(
    r'^[ \t]*sys\.path\.insert\(0,[ \t]*str\(.*?/[ \t]*"answers_python"[ \t]*\)\)[ \t]*$',
    re.MULTILINE,
)
_DATASET_DIR_LINE_RE = re.compile(
    r'^[ \t]*DATASET_DIR[ \t]*=[ \t]*.*?/[ \t]*"datasets"[ \t]*$',
    re.MULTILINE,
)


def _rewrite_test_text(text: str) -> str:
    text = _SYS_PATH_LINE_RE.sub(_SYS_PATH_REPLACEMENT, text)
    text = _DATASET_DIR_LINE_RE.sub(_DATASET_DIR_REPLACEMENT, text)
    return text


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
