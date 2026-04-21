import sys

from evaluate_scripts_b import main


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

import sys

from evaluate_scripts_b import main


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

"""
Generate `results_table_b.csv` for model "b" answers.

This script is a dataset-prep utility: it executes the stored SQL and Python task
files against each dataset variant and records runtime, formatting, pytest, and
SQL result checksums.

Output schema (CSV):
filename | dataset_variant | token_usage_input | token_usage_output | runtime_ms |
peak_memory_bytes | formatting_pass_pct | pytest_filename | pytest_pass_pct |
checksum | row_count | snapshot_pass
"""

import csv
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
import tracemalloc
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import duckdb
import tiktoken

from bootstrap_assets_b import bootstrap, bootstrap_datasets_variant_folders


VARIANTS = ["clean", "null_heavy", "duplicate_heavy", "medium", "large"]


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    n: int
    engine: str  # "sql" | "python"

    @property
    def filename(self) -> str:
        ext = "sql" if self.engine == "sql" else "py"
        return f"task{self.n}b.{ext}"


def _repo_root() -> Path:
    return Path(__file__).resolve().parent


def _assets_dir(root: Path) -> Path:
    return root / "assets"


def _datasets_dir(root: Path) -> Path:
    return _assets_dir(root) / "datasets"


def _tasks_dir(root: Path) -> Path:
    return _assets_dir(root) / "tasks"


def _task_specs() -> list[TaskSpec]:
    out: list[TaskSpec] = []
    for n in range(1, 31):
        out.append(TaskSpec(task_id=f"SQL-{n:03d}", n=n, engine="sql"))
    for n in range(1, 31):
        out.append(TaskSpec(task_id=f"PY-{n:03d}", n=n, engine="python"))
    return out


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _count_lines(path: Path) -> int:
    # Ensure non-zero denominator for formatting_pass_pct.
    return max(1, len(_read_text(path).splitlines()))


def _token_counts(prompt_text: str, response_text: str) -> tuple[int, int]:
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(prompt_text)), len(enc.encode(response_text))


def _run_sqlfluff_violations(sql_path: Path) -> int:
    cmd = ["sqlfluff", "lint", str(sql_path), "--dialect", "ansi", "--format", "json"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    # sqlfluff returns non-zero when violations exist; we still parse JSON.
    try:
        payload = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError:
        # If sqlfluff failed hard, treat as total failure.
        return _count_lines(sql_path)
    violations = 0
    for file_entry in payload if isinstance(payload, list) else []:
        v = file_entry.get("violations", [])
        if isinstance(v, list):
            violations += len(v)
    return int(violations)


def _run_flake8_violations(py_path: Path) -> int:
    cmd = ["flake8", str(py_path), "--count"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    # flake8 prints the count as the last line.
    lines = [ln.strip() for ln in (proc.stdout or "").splitlines() if ln.strip()]
    if not lines:
        return 0
    try:
        return int(lines[-1])
    except ValueError:
        # If flake8 output format changed, fall back to "any output line = a violation".
        return len(lines)


def _formatting_pass_pct(file_path: Path, violations: int) -> float:
    checked = _count_lines(file_path)
    pct = ((checked - violations) / checked) * 100.0
    pct = max(0.0, min(100.0, pct))
    return round(pct, 2)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _dataset_paths_flat(datasets_dir: Path, variant: str) -> tuple[Path, Path, Path]:
    accounts = datasets_dir / f"synthetic_{variant}_accounts.csv"
    txns = datasets_dir / f"synthetic_{variant}_transactions.csv"
    balances = datasets_dir / f"synthetic_{variant}_daily_balances.csv"
    return accounts, txns, balances


def _duckdb_load_variant_tables(con: duckdb.DuckDBPyConnection, datasets_dir: Path, variant: str) -> None:
    accounts_path, txns_path, balances_path = _dataset_paths_flat(datasets_dir, variant)
    tables = {
        f"synthetic_{variant}_accounts": accounts_path,
        f"synthetic_{variant}_transactions": txns_path,
        f"synthetic_{variant}_daily_balances": balances_path,
    }
    for table, path in tables.items():
        if not path.exists():
            raise FileNotFoundError(str(path))
        con.execute(
            f"""
            CREATE OR REPLACE TABLE {table} AS
            SELECT * FROM read_csv_auto('{path.as_posix()}', header=true, comment='#', strict_mode=false);
            """
        )


def _canonicalize_df_to_csv_bytes(df: Any) -> bytes:
    """
    Convert a DuckDB/Pandas DataFrame to a deterministic CSV byte representation
    for hashing/comparison. We avoid index, and sort by all columns to reduce
    ordering variance in tasks that omit ORDER BY.
    """

    # DuckDB fetch_df() yields a pandas DataFrame.
    try:
        import pandas as pd  # local import (already in requirements)
    except Exception as e:  # pragma: no cover
        raise RuntimeError("pandas is required for result canonicalization") from e

    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)

    if not df.empty:
        cols = list(df.columns)
        df = df.sort_values(by=cols, kind="stable").reset_index(drop=True)

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False, encoding="utf-8") as tmp:
        tmp_path = Path(tmp.name)
    try:
        df.to_csv(tmp_path, index=False, lineterminator="\n")
        return tmp_path.read_bytes()
    finally:
        tmp_path.unlink(missing_ok=True)


def _sql_runtime_and_artifacts(
    sql_path_b: Path,
    sql_path_reference: Path,
    datasets_dir: Path,
    variant: str,
) -> tuple[int, str | None, int | None, bool | None]:
    """
    Returns: (runtime_ms, checksum, row_count, snapshot_pass)
    """

    sql_text_b = _read_text(sql_path_b).replace("<variant>", variant)
    sql_text_ref = _read_text(sql_path_reference).replace("<variant>", variant)

    con = duckdb.connect(database=":memory:")
    try:
        _duckdb_load_variant_tables(con, datasets_dir, variant)

        start = time.perf_counter()
        df_b = con.execute(sql_text_b).fetch_df()
        runtime_ms = int((time.perf_counter() - start) * 1000)

        csv_bytes_b = _canonicalize_df_to_csv_bytes(df_b)
        checksum = hashlib.sha256(csv_bytes_b).hexdigest()
        row_count = int(getattr(df_b, "shape", (len(df_b),))[0])

        # Reference snapshots live next to the task file (created if missing).
        ref_dir = sql_path_b.parent / "reference_results"
        ref_csv_path = ref_dir / f"{variant}.csv"
        if ref_csv_path.exists():
            csv_bytes_ref = ref_csv_path.read_bytes()
            snapshot_pass = csv_bytes_b == csv_bytes_ref
        else:
            try:
                df_ref = con.execute(sql_text_ref).fetch_df()
                csv_bytes_ref = _canonicalize_df_to_csv_bytes(df_ref)
                ref_dir.mkdir(parents=True, exist_ok=True)
                ref_csv_path.write_bytes(csv_bytes_ref)
                snapshot_pass = csv_bytes_b == csv_bytes_ref
            except Exception:
                snapshot_pass = False

        return runtime_ms, checksum, row_count, snapshot_pass
    finally:
        con.close()


def _import_task_module_from_path(py_path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(py_path.stem, py_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not import module from {py_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_PYTEST_NODE_RESULT_RE = re.compile(
    r"^(?P<nodeid>.+?)\s+(?P<result>PASSED|FAILED|SKIPPED|XFAIL|XPASS)\b", re.IGNORECASE
)


def _pytest_variant_pass_pcts(test_path: Path, variants: list[str]) -> dict[str, float]:
    """
    Run pytest once for a test file and compute per-variant pass percentage
    from the verbose per-node output lines.
    """

    wanted = set(variants)
    totals: dict[str, int] = {v: 0 for v in variants}
    passed: dict[str, int] = {v: 0 for v in variants}

    collect = subprocess.run(
        ["pytest", "--collect-only", "-q", str(test_path)],
        capture_output=True,
        text=True,
    )
    collected = [ln.strip() for ln in (collect.stdout or "").splitlines() if ln.strip()]
    wanted_nodeids: list[str] = []
    for nid in collected:
        mvar = re.search(r"\[(?P<variant>[^\]]+)\]\s*$", nid)
        if not mvar:
            continue
        if mvar.group("variant") in wanted:
            wanted_nodeids.append(nid)

    if not wanted_nodeids:
        return {v: 0.0 for v in variants}

    run = subprocess.run(
        ["pytest", "-vv", "--disable-warnings", *wanted_nodeids],
        capture_output=True,
        text=True,
    )
    out_lines = ((run.stdout or "") + "\n" + (run.stderr or "")).splitlines()
    for ln in out_lines:
        m = _PYTEST_NODE_RESULT_RE.match(ln.strip())
        if not m:
            continue
        nodeid = m.group("nodeid")
        result = m.group("result")
        # Extract [variant] suffix if present
        mvar = re.search(r"\[(?P<variant>[^\]]+)\]\s*$", nodeid)
        if not mvar:
            continue
        variant = mvar.group("variant")
        if variant not in wanted:
            continue
        totals[variant] += 1
        if result.upper() == "PASSED":
            passed[variant] += 1

    out: dict[str, float] = {}
    for v in variants:
        tot = totals.get(v, 0)
        pas = passed.get(v, 0)
        out[v] = round((pas / tot) * 100.0, 2) if tot else 0.0
    return out


def _python_runtime_and_peak_memory(
    py_path: Path, datasets_dir: Path, variant: str
) -> tuple[int, int | None]:
    import contextlib
    import io

    accounts_path, txns_path, balances_path = _dataset_paths_flat(datasets_dir, variant)
    mod = _import_task_module_from_path(py_path)
    if not hasattr(mod, "run"):
        raise AttributeError(f"{py_path.name} has no run(...)")

    tracemalloc.start()
    try:
        sink = io.StringIO()
        start = time.perf_counter()
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            _ = mod.run(accounts_path, txns_path, balances_path)
        runtime_ms = int((time.perf_counter() - start) * 1000)
        _, peak = tracemalloc.get_traced_memory()
        return runtime_ms, int(peak)
    finally:
        tracemalloc.stop()


def _ensure_bootstrapped(root: Path) -> None:
    # New structure required by the user instructions.
    bootstrap(root)
    # Also create variant folders with canonical filenames (optional).
    bootstrap_datasets_variant_folders(root)


def _path_task_dir(root: Path, task_id: str) -> Path:
    return _tasks_dir(root) / task_id


def _reference_sql_path(root: Path, n: int) -> Path:
    # Use model "c" SQL as reference snapshot generator.
    return _assets_dir(root) / "tasks_c" / "answers_sql" / f"task{n}c.sql"


def _write_results_csv(rows: Iterable[dict[str, Any]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "filename",
        "dataset_variant",
        "token_usage_input",
        "token_usage_output",
        "runtime_ms",
        "peak_memory_bytes",
        "formatting_pass_pct",
        "pytest_filename",
        "pytest_pass_pct",
        "checksum",
        "row_count",
        "snapshot_pass",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def main(argv: list[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Generate results_table_b.csv from model-b task files.")
    parser.add_argument(
        "--out",
        default="results_table_b.csv",
        help="Output CSV path (default: results_table_b.csv in repo root).",
    )
    parser.add_argument(
        "--variants",
        default=",".join(VARIANTS),
        help="Comma-separated variants (default: clean,null_heavy,duplicate_heavy,medium,large).",
    )
    args = parser.parse_args(argv)

    root = _repo_root()
    _ensure_bootstrapped(root)

    datasets_dir = _datasets_dir(root)
    variants = [v.strip() for v in args.variants.split(",") if v.strip()]

    rows: list[dict[str, Any]] = []

    for spec in _task_specs():
        task_dir = _path_task_dir(root, spec.task_id)
        code_path = task_dir / spec.filename
        prompt_text = _read_text(task_dir / "prompt.txt") if (task_dir / "prompt.txt").exists() else ""
        response_text = _read_text(code_path) if code_path.exists() else ""
        token_in, token_out = _token_counts(prompt_text, response_text)

        if spec.engine == "sql":
            violations = _run_sqlfluff_violations(code_path)
        else:
            violations = _run_flake8_violations(code_path)
        formatting_pass_pct = _formatting_pass_pct(code_path, violations)

        pytest_map: dict[str, float] | None = None
        test_path: Path | None = None
        if spec.engine == "python":
            test_path = task_dir / f"test_task{spec.n}b.py"
            pytest_map = _pytest_variant_pass_pcts(test_path, variants)

        for variant in variants:
            base: dict[str, Any] = {
                "filename": spec.filename,
                "dataset_variant": variant,
                "token_usage_input": token_in,
                "token_usage_output": token_out,
                "formatting_pass_pct": formatting_pass_pct,
            }

            if spec.engine == "sql":
                ref_sql = _reference_sql_path(root, spec.n)
                runtime_ms, checksum, row_count, snapshot_pass = _sql_runtime_and_artifacts(
                    sql_path_b=code_path,
                    sql_path_reference=ref_sql,
                    datasets_dir=datasets_dir,
                    variant=variant,
                )
                base.update(
                    {
                        "runtime_ms": runtime_ms,
                        "peak_memory_bytes": "",
                        "pytest_filename": "",
                        "pytest_pass_pct": "",
                        "checksum": checksum,
                        "row_count": row_count,
                        "snapshot_pass": str(bool(snapshot_pass)).lower() if snapshot_pass is not None else "",
                    }
                )
            else:
                runtime_ms, peak_bytes = _python_runtime_and_peak_memory(code_path, datasets_dir, variant)
                assert test_path is not None
                assert pytest_map is not None
                pytest_pass_pct = pytest_map.get(variant, 0.0)
                base.update(
                    {
                        "runtime_ms": runtime_ms,
                        "peak_memory_bytes": peak_bytes,
                        "pytest_filename": test_path.name,
                        "pytest_pass_pct": pytest_pass_pct,
                        "checksum": "",
                        "row_count": "",
                        "snapshot_pass": "",
                    }
                )

            rows.append(base)

    out_path = (root / args.out).resolve()
    _write_results_csv(rows, out_path)
    print(out_path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))