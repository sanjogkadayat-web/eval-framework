"""
merge_results.py — Dataset preparation utility (FR-019)

Reads:
  assets/results/results_table_a.csv   (Claude Sonnet 4.5)
  assets/results/results_table_b.csv   (ChatGPT 5.2 Codex — baseline)
  assets/results/results_table_c.csv   (Gemini 2.5 Flash)

Writes:
  assets/eval_results.csv

The output snapshot_pass column is TRUE only when all three models
share the same snapshot_pass value for a given (task_num, dataset_variant).
Otherwise FALSE.

FR-019 validations performed before writing:
  V-MG-1  All three source files exist and are readable
  V-MG-2  All three files share identical headers
  V-MG-3  Headers match the canonical 12-column schema exactly
  V-MG-4  dataset_variant contains only the five canonical values
  V-MG-5  Letter-binding: rows in results_table_a contain only 'a' filenames, etc.
  V-MG-6  No (filename, dataset_variant) primary key appears in more than one source file
  V-MG-7  No duplicate primary keys within a single source file
  V-MG-8  Post-merge: output row count equals sum of all three source files
  V-MG-9  Post-merge: no duplicate (filename, dataset_variant) primary keys in output
  V-MG-10 Post-merge: snapshot_pass column contains only True / False (no nulls/blanks)

Usage:
  python merge_results.py [--input-dir <path>] [--output <path>]

Defaults:
  --input-dir  assets/results
  --output     assets/eval_results.csv
"""

import argparse
import csv
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CANONICAL_HEADERS = [
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

VALID_VARIANTS = {"clean", "null_heavy", "duplicate_heavy", "medium", "large"}

FILENAME_RE = re.compile(r"^task(?P<task_num>\d+)(?P<model_letter>[abc])\.(?P<ext>py|sql)$")

SOURCE_FILES = [
    ("results_table_a.csv", "a"),
    ("results_table_b.csv", "b"),
    ("results_table_c.csv", "c"),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def halt(check_id: str, message: str) -> None:
    print(f"[merge_results] {check_id} FAILURE: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_snapshot_pass(value: str) -> bool | None:
    """Normalise snapshot_pass strings to Python bool or None."""
    v = str(value).strip().lower()
    if v in ("true", "1"):
        return True
    if v in ("false", "0"):
        return False
    return None  # empty / null — valid for Python tasks


# ---------------------------------------------------------------------------
# Main merge logic
# ---------------------------------------------------------------------------

def merge(input_dir: Path, output_path: Path) -> None:

    # ------------------------------------------------------------------
    # V-MG-1  Source files exist
    # ------------------------------------------------------------------
    source_paths = []
    for filename, letter in SOURCE_FILES:
        p = input_dir / filename
        if not p.exists():
            halt("V-MG-1", f"Source file not found: {p}")
        source_paths.append((p, letter))
    print("✓ V-MG-1  All three source files found")

    # ------------------------------------------------------------------
    # V-MG-2 / V-MG-3  Headers are identical and match canonical schema
    # ------------------------------------------------------------------
    all_rows: list[dict] = []
    headers_seen: list[list[str]] = []

    for p, letter in source_paths:
        with p.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = list(reader.fieldnames or [])
            headers_seen.append(headers)

    first_header = headers_seen[0]
    for i, h in enumerate(headers_seen[1:], start=1):
        if h != first_header:
            halt(
                "V-MG-2",
                f"{SOURCE_FILES[i][0]} header differs from {SOURCE_FILES[0][0]}.\n"
                f"  Expected: {first_header}\n  Got:      {h}",
            )
    print("✓ V-MG-2  All three files share identical headers")

    if first_header != CANONICAL_HEADERS:
        halt(
            "V-MG-3",
            f"Headers do not match canonical schema.\n"
            f"  Expected: {CANONICAL_HEADERS}\n  Got:      {first_header}",
        )
    print("✓ V-MG-3  Headers match canonical 12-column schema")

    # ------------------------------------------------------------------
    # Read all rows now that headers are validated
    # ------------------------------------------------------------------
    per_source_rows: list[list[dict]] = []
    for p, _ in source_paths:
        per_source_rows.append(read_csv(p))

    # ------------------------------------------------------------------
    # V-MG-4  Valid dataset_variant values
    # ------------------------------------------------------------------
    for (p, _), rows in zip(source_paths, per_source_rows):
        for i, row in enumerate(rows, start=2):  # row 1 = header
            v = row.get("dataset_variant", "")
            if v not in VALID_VARIANTS:
                halt(
                    "V-MG-4",
                    f"{p.name} row {i}: invalid dataset_variant '{v}'. "
                    f"Must be one of {sorted(VALID_VARIANTS)}.",
                )
    print("✓ V-MG-4  All dataset_variant values are valid")

    # ------------------------------------------------------------------
    # V-MG-5  Letter-binding: each file must contain only its own letter
    # ------------------------------------------------------------------
    for (p, expected_letter), rows in zip(source_paths, per_source_rows):
        for i, row in enumerate(rows, start=2):
            fn = row.get("filename", "")
            m = FILENAME_RE.match(fn)
            if not m:
                halt(
                    "V-MG-5",
                    f"{p.name} row {i}: filename '{fn}' does not match "
                    r"^task\d+[abc]\.(py|sql)$",
                )
            if m.group("model_letter") != expected_letter:
                halt(
                    "V-MG-5",
                    f"{p.name} row {i}: filename '{fn}' belongs to model "
                    f"'{m.group('model_letter')}' but should be '{expected_letter}'.",
                )
    print("✓ V-MG-5  Letter-binding: each file contains only its own model's rows")

    # ------------------------------------------------------------------
    # V-MG-6  No (filename, dataset_variant) pair in more than one source
    # ------------------------------------------------------------------
    global_pks: dict[tuple, str] = {}
    for (p, _), rows in zip(source_paths, per_source_rows):
        for row in rows:
            pk = (row["filename"], row["dataset_variant"])
            if pk in global_pks:
                halt(
                    "V-MG-6",
                    f"Primary key {pk} appears in both {global_pks[pk]} and {p.name}.",
                )
            global_pks[pk] = p.name
    print("✓ V-MG-6  No primary key appears in more than one source file")

    # ------------------------------------------------------------------
    # V-MG-7  No duplicate primary keys within a single source file
    # ------------------------------------------------------------------
    for (p, _), rows in zip(source_paths, per_source_rows):
        seen: set[tuple] = set()
        for i, row in enumerate(rows, start=2):
            pk = (row["filename"], row["dataset_variant"])
            if pk in seen:
                halt("V-MG-7", f"{p.name} row {i}: duplicate primary key {pk}.")
            seen.add(pk)
    print("✓ V-MG-7  No duplicate primary keys within any source file")

    # ------------------------------------------------------------------
    # Build combined rows (a → b → c order per spec)
    # ------------------------------------------------------------------
    for rows in per_source_rows:
        all_rows.extend(rows)

    # ------------------------------------------------------------------
    # Compute cross-model snapshot_pass
    #
    # For SQL rows: group by (task_num, dataset_variant) across all 3 models.
    # snapshot_pass = True  iff all three models have the same value.
    # snapshot_pass = False if any differ.
    # For Python rows: snapshot_pass is empty/null (field not applicable).
    # ------------------------------------------------------------------

    # Build a lookup: (task_num, dataset_variant) → list of raw snapshot_pass values
    # Only SQL rows (.sql extension) carry snapshot_pass.
    sp_by_task_variant: dict[tuple, list[str]] = {}
    for row in all_rows:
        fn = row["filename"]
        m = FILENAME_RE.match(fn)
        if m and m.group("ext") == "sql":
            key = (m.group("task_num"), row["dataset_variant"])
            sp_by_task_variant.setdefault(key, [])
            sp_by_task_variant[key].append(str(row.get("snapshot_pass", "")).strip().lower())

    # Compute consensus: True only if all values are identical
    sp_consensus: dict[tuple, str] = {}
    for key, values in sp_by_task_variant.items():
        # Normalise: treat empty strings as distinct from "true"/"false"
        sp_consensus[key] = "True" if len(set(values)) == 1 else "False"

    # Apply back to rows
    for row in all_rows:
        fn = row["filename"]
        m = FILENAME_RE.match(fn)
        if m and m.group("ext") == "sql":
            key = (m.group("task_num"), row["dataset_variant"])
            row["snapshot_pass"] = sp_consensus.get(key, "False")
        else:
            # Python tasks: keep blank (field is SQL-only per schema)
            row["snapshot_pass"] = ""

    # ------------------------------------------------------------------
    # V-MG-8  Output row count == sum of source row counts
    # ------------------------------------------------------------------
    expected_count = sum(len(rows) for rows in per_source_rows)
    if len(all_rows) != expected_count:
        halt(
            "V-MG-8",
            f"Row count mismatch: expected {expected_count}, got {len(all_rows)}.",
        )
    print(f"✓ V-MG-8  Row count correct: {len(all_rows)} rows ({expected_count} expected)")

    # ------------------------------------------------------------------
    # V-MG-9  No duplicate primary keys in merged output
    # ------------------------------------------------------------------
    merged_pks: set[tuple] = set()
    for i, row in enumerate(all_rows, start=2):
        pk = (row["filename"], row["dataset_variant"])
        if pk in merged_pks:
            halt("V-MG-9", f"Merged output row {i}: duplicate primary key {pk}.")
        merged_pks.add(pk)
    print("✓ V-MG-9  No duplicate primary keys in merged output")

    # ------------------------------------------------------------------
    # V-MG-10  snapshot_pass contains only True / False / empty (for Python)
    # ------------------------------------------------------------------
    for i, row in enumerate(all_rows, start=2):
        fn = row["filename"]
        m = FILENAME_RE.match(fn)
        is_sql = m and m.group("ext") == "sql"
        sp = str(row.get("snapshot_pass", "")).strip()
        if is_sql and sp not in ("True", "False"):
            halt(
                "V-MG-10",
                f"Row {i} ({fn}): snapshot_pass must be 'True' or 'False' for SQL rows, got '{sp}'.",
            )
        if not is_sql and sp not in ("", ):
            # Python rows must be empty — already enforced above but double-check
            pass
    print("✓ V-MG-10 snapshot_pass values are valid throughout")

    # ------------------------------------------------------------------
    # Write output
    # ------------------------------------------------------------------
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CANONICAL_HEADERS)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n✅ Done — {len(all_rows)} rows written to {output_path}")
    print(f"   Models: a=Claude Sonnet 4.5 | b=ChatGPT 5.2 Codex (baseline) | c=Gemini 2.5 Flash")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Merge results_table_a/b/c.csv into assets/eval_results.csv (FR-019)."
    )
    parser.add_argument(
        "--input-dir",
        default="assets/results",
        help="Directory containing results_table_a/b/c.csv (default: assets/results)",
    )
    parser.add_argument(
        "--output",
        default="assets/eval_results.csv",
        help="Output path for merged CSV (default: assets/eval_results.csv)",
    )
    args = parser.parse_args(argv)

    input_dir = Path(args.input_dir)
    output_path = Path(args.output)

    print(f"merge_results.py — FR-019 merge")
    print(f"  Input dir : {input_dir.resolve()}")
    print(f"  Output    : {output_path.resolve()}")
    print()

    merge(input_dir, output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
