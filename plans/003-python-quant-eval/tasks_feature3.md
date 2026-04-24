---
description: "Task list for Feature 3 — Python Quantitative Evaluation"
---

# Tasks: Feature 3 — Python Quantitative Evaluation

**Input**: Design documents from `specs/003-python-quant-eval/`
**Prerequisites**: `feature3_plan.md` (required), `spec.md` (required for user stories), `constitution.md` (required for all guardrails), Feature 1 complete and passing (required — `references/` documents, `references/file-schema.md`, synthetic datasets, `assets/task_bank.csv`, `assets/eval_results.csv`, and `merge_results.py` are all produced by F1 and must exist before Feature 3 begins)

**Tests**: Harness self-tests are included per the Feature 3 plan. Task-level pytest files are NOT included — Python correctness is determined by reading the pre-recorded `pytest_pass` field in `assets/eval_results.csv`, not by executing model-generated code.

**Organization**: Feature 3 has one primary user story (US3 — Python Quantitative Evaluation, Priority P2). It mirrors the F1 architecture in `python-skill/` and is independently testable without requiring F2 or F4. `python-skill/` and `sql-skill/` are fully independent directory trees — no scripts or assets are shared between them. **`references/file-schema.md`, `assets/task_bank.csv`, and `assets/eval_results.csv` are shared zip-root assets**, owned by F1 and consumed by F3 — they must not be duplicated or rewritten.

**Architecture**: Amendments A1, A2, and A3 are all ratified. This task list implements the **A3 two-table architecture**: prompt text and per-model filenames are in `assets/task_bank.csv` (populated for Python rows in T043); Python metrics are rows in the shared `assets/eval_results.csv` where `filename` ends in `.py`. The `merge_results.py` script (owned by F1) produces `eval_results.csv` from three per-author files during dataset preparation.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US3)
- Task IDs continue from Feature 2 (T041+) to support cross-feature traceability
- Paths follow the single-project CLI skill structure defined in the Feature 3 plan

---

## Phase 1: Setup

**Purpose**: Establish the `python-skill/` scaffold. Shared zip root assets (`references/`, `references/file-schema.md`, `assets/task_bank.csv`, `assets/eval_results.csv`, `assets/datasets/`) were created in Feature 1 and must not be duplicated — Feature 3 adds only what is new to the Python skill tree.

- [ ] T041 Create `python-skill/` scaffold: `SKILL.md` (stub — YAML frontmatter `name` and `description` fields only, no task list inline), `scripts/` (empty), `assets/personas/` (empty — for Feature 4), `assets/tasks/` (empty). **Do not create `assets/answers/` or `assets/variant_results/`** — those are pre-A3 directories and do not exist under the unified architecture.

- [ ] T042 [P] Verify `references/file-schema.md` (from Feature 1 T004) already contains the **Python-complete unified schema**: the Python-only fields (`peak_memory_bytes`, `pytest_filename`, `pytest_pass`) and the per-language null rules for `eval_results.csv` must already be declared. F1's T004 authored the schema in its final form covering both languages — no F3 update to the schema is required. If the file is incomplete (Python fields missing or null rules absent), this is a F1 defect and must be fixed in F1 before F3 proceeds. Confirm `sql-skill/scripts/schema_validator.py` (F1) still passes against the shared schema.

**Checkpoint**: `python-skill/` tree is in place. `references/file-schema.md` is confirmed complete. No new top-level directories are needed — Feature 3 consumes the shared `assets/task_bank.csv` and `assets/eval_results.csv`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: `task_bank.csv` Python rows must be fully populated, Python rows in `eval_results.csv` must be produced (via the merge script or fixture data), and per-task Python code files must exist before any scoring script is written. `schema_validator.py` for the Python skill must be implemented before the scoring pipeline runs.

**⚠️ CRITICAL**: No scoring script (`scorer.py`, `schema_validator.py`) may be written until T043–T046 are complete.

- [ ] T043 Populate `assets/task_bank.csv` Python rows — all 100 Python task rows (`PY-001`–`PY-100`) must have correct values per the schema in `references/file-schema.md` §1: `task_id`, `contracted` (`true` for `PY-001`–`PY-020`, `false` for `PY-021`–`PY-100`), `category` (`easy`/`medium`/`hard`), `prompt` (standardized prompt text stored inline, CSV-quoted), `model_a_filename` (`task{N}a.py`), `model_b_filename` (`task{N}b.py`), `model_c_filename` (`task{N}c.py`). If rows were stubbed as placeholders in Feature 1 T009, populate them fully here. Verify `schema_validator.py` (F1, via its `V-TB-*` checks) still passes after this update.

- [ ] T044 [P] Extend per-author fixture files `results_a.csv`, `results_b.csv`, `results_c.csv` (created as SQL-only fixtures in F1 T016) — add Python rows for `PY-001`–`PY-005` across all five variants in each file (15 new Python rows per file). Schema per `references/file-schema.md` §2: populate `filename` (`task{N}a.py`, `task{N}b.py`, `task{N}c.py`), `dataset_variant`, `token_usage_input`, `token_usage_output`, `runtime_ms`, `peak_memory_bytes`, `formatting_violations`, `pytest_filename` (`test_task{N}{letter}.py`), `pytest_pass`. Leave SQL-only fields (`checksum`, `row_count`, `snapshot_pass`) empty for Python rows. These fixture files live outside the released zip — they are used by the merge script (F1 T017) to produce a fixture `eval_results.csv` with both SQL and Python rows for integration testing.

- [ ] T045 [P] Re-run `merge_results.py` (from F1 T017) against the extended per-author fixture files to produce an updated fixture `assets/eval_results.csv` containing both SQL (SQL-001–SQL-005) and Python (PY-001–PY-005) rows across all five variants. Verify the merged file passes all `V-MG-*` and `V-ER-*` checks. **For production, the three team members will generate full 1,000-row per-author files on their separate machines and the merge produces the complete 3,000-row `eval_results.csv`.**

- [ ] T046 [P] Create per-task asset stubs for a representative contracted subset (PY-001–PY-005) in `assets/tasks/[task_id]/`: `task{N}a.py`, `task{N}b.py`, `task{N}c.py` (three model code files — synthetic placeholders for fixture testing), `reference_solution.py` (human-authored baseline — documentation artifact only, not executed by harness), `test_solution.py` (pytest file — documentation and reproducibility artifact only, not executed by harness at runtime). **No per-task `prompt.md` file** — prompt text is stored inline in `task_bank.csv`.

**Checkpoint**: `task_bank.csv` Python rows are fully populated (200 total rows, 40 contracted). Per-author fixture files contain Python rows for PY-001–PY-005 alongside the existing SQL fixture rows. Fixture `eval_results.csv` is produced by the merge script and passes all validation. Per-task code file stubs exist for PY-001–PY-005. No scoring script is written yet.

---

## Phase 3: User Story 3 — Python Quantitative Evaluation (Priority: P2) 🎯

**Goal**: A Data Engineer selects a Python Task ID and the harness reads pre-recorded metric rows from `eval_results.csv` for all three models, scores correctness via `pytest_pass` and performance via `runtime_ms` / `peak_memory_bytes` / `token_usage_*`, applies the clean-pass gate for variant inclusion, and persists all artifacts keyed by `task_id/model/category`.

**Independent Test**: Select a Python task (e.g., PY-001), confirm `eval_task.py` reads `task_bank.csv` to resolve `task_id` → three model filenames (`task1a.py`, `task1b.py`, `task1c.py`), filters `eval_results.csv` by `(filename, dataset_variant)` pairs matching those filenames, reads correctness (`pytest_pass`) and performance metrics (`runtime_ms`, `peak_memory_bytes`, `token_usage_input`, `token_usage_output`), surfaces variant rows for 100%-clean-pass models, and writes `result.json` to `outputs/PY-001/[model]/[category]/`. Verify `--contracted-only` evaluates only contracted tasks (PY-001–PY-020) and skips PY-021–PY-100 without error.

### Harness Self-Tests for User Story 3 ⚠️

> **Write these tests FIRST. Ensure they FAIL before writing the implementation.**

- [ ] T047 [P] [US3] Write unit test `tests/unit/test_anonymizer.py` (Python skill) — verify `python-skill/scripts/anonymizer.py` parses the canonical filename regex `^task(?P<task_num>\d+)(?P<model_letter>[abc])\.(?P<ext>py|sql)$` and returns `task_num`, `model_letter`, `ext`, derived `task_id` (e.g., `PY-001`), and derived `model_token` (e.g., `model_a`). Verify no real model name is constructed anywhere. Test with filenames for all three letters (`task1a.py`, `task1b.py`, `task1c.py`); verify the anonymizer rejects filenames that do not match the regex. Note: this is a new file under `python-skill/` — logically mirrors the F1 anonymizer but is an independent script under `python-skill/`.

- [ ] T048 [P] [US3] Write unit test `tests/unit/test_scorer.py` (Python skill) — verify `python-skill/scripts/scorer.py` correctly reads the pre-recorded `pytest_pass` field from `eval_results.csv` for each `(filename, dataset_variant)` pair; verify the 100% clean pass gate logic (variant rows other than `clean` are excluded from the scorecard if `pytest_pass = false` on the `clean` variant); verify `correctness_score` is derived from `pytest_pass` (1.0 if true, 0.0 if false); verify per-variant correctness is correctly surfaced; verify deterministic output for identical inputs; test edge cases: missing variant row for a filename (validation failure upstream — should not reach scorer), `pytest_pass = false` on clean (gate triggers, non-clean variants excluded), `pytest_pass = true` on clean with a mix of true/false on non-clean variants (all variants surfaced with their respective flags).

- [ ] T049 [P] [US3] Write unit test `tests/unit/test_schema_validator.py` (Python skill) — verify `python-skill/scripts/schema_validator.py` validates `assets/task_bank.csv` and `assets/eval_results.csv` against the `V-TB-*` and `V-ER-*` checks declared in `references/file-schema.md`. Particular attention to Python-specific cases: `pytest_pass` / `pytest_filename` / `peak_memory_bytes` must be populated for `.py` rows and null for `.sql` rows (V-ER-7); SQL-only fields (`checksum`, `row_count`, `snapshot_pass`) must be null for `.py` rows (V-ER-8); `pytest_filename` format `^test_task\d+[abc]\.py$` with matching numeric prefix and letter (V-ER-13); per-filename invariant of `pytest_filename` across variant rows (V-ER-12). Verify it passes on conformant fixture files.

- [ ] T050 [P] [US3] Write unit test `tests/unit/test_artifact_store.py` (Python skill) — verify `python-skill/scripts/artifact_store.py` writes `result.json` to the correct path (`outputs/[task_id]/[model]/[category]/result.json`); verify all required Python-record fields per `file-schema.md` §4 are present: `task_id`, `model_token`, `filename`, `dataset_variant`, `category`, `contracted`, `correctness_score`, `pytest_pass`, `runtime_ms`, `peak_memory_bytes`, `token_usage_input`, `token_usage_output`, `formatting_violations`, `variant_mismatch`, `critic_review_path`; verify SQL-only fields (`checksum_match`, `row_count_match`, `snapshot_pass`) are `null` for Python records; verify `generation_time_ms`, `flake8_violation_count`, `sqlfluff_violation_count`, `correctness_pass`, `correctness_detail` are **absent**; verify idempotent overwrite behavior; verify `critic_review_path` is null (Feature 4 populates it).

- [ ] T051 [US3] Write integration test `tests/integration/test_eval_task_pipeline.py` (Python skill) — using the fixture `task_bank.csv` and fixture `eval_results.csv` produced in T045, verify the full `eval-task --engine python --task-id PY-001` pipeline produces a correctly structured `result.json` with all Python-record fields populated per `file-schema.md` §4; verify excluded fields are absent; verify `--contracted-only` skips non-contracted tasks without error; verify variant scoring runs only for models with 100% clean pass (depends on T047–T050 test stubs existing).

### Implementation for User Story 3

- [ ] T052 [US3] Implement `python-skill/scripts/anonymizer.py` — parses the canonical filename regex `^task(?P<task_num>\d+)(?P<model_letter>[abc])\.(?P<ext>py|sql)$` and returns a dict containing `task_num`, `model_letter`, `ext`, derived `task_id` (`PY-{task_num zero-padded to 3}` for `.py` filenames), and derived `model_token` (e.g., `model_a`). No real model names are constructed. Rejects filenames not matching the regex with a clear error. Logically mirrors `sql-skill/scripts/anonymizer.py` but is a fully independent script under `python-skill/`. Must pass T047 tests.

- [ ] T053 [US3] Implement `python-skill/scripts/schema_validator.py` — validates `assets/task_bank.csv` against the 11 `V-TB-*` checks and `assets/eval_results.csv` against the 13 `V-ER-*` checks declared in `references/file-schema.md`. On any failure, halts the pipeline with a clear error message citing the specific check ID, the file, the row (where applicable), and the offending field (per `file-schema.md` §5.3). Validates the same shared files as `sql-skill/scripts/schema_validator.py` — the two scripts are functionally equivalent but live in independent skill trees per Constitution. Must pass T049 tests.

- [ ] T054 [US3] Implement `python-skill/scripts/scorer.py` — filters `assets/eval_results.csv` by `(filename, dataset_variant)` for a given task and model; reads `pytest_pass` for the `clean` variant to determine the clean-pass gate; if `clean` passes, surfaces `pytest_pass` for the remaining four variant rows; reads `formatting_violations`, `runtime_ms`, `peak_memory_bytes`, `token_usage_input`, `token_usage_output` from the relevant rows. Computes `correctness_score` as `1.0` if `pytest_pass = true` else `0.0` per variant. **Does not invoke pytest, tracemalloc, or flake8 at runtime.** Does not read or write `generation_time_ms` — not captured in V1. Must pass T048 tests.

- [ ] T055 [US3] Implement `python-skill/scripts/schema_checker.py` — detects column name or data type drift between a variant's data schema and the clean baseline schema at harness runtime. Writes `variant_mismatch = true` to the run's `result.json` when drift is detected. **`variant_mismatch` is not a field in `eval_results.csv`** — it is derived at runtime and surfaced only in `result.json`. Mismatched variants are reported separately and excluded from correctness scoring.

- [ ] T056 [US3] Implement `python-skill/scripts/artifact_store.py` — persists all run outputs to `outputs/[task_id]/[model]/[category]/result.json`; fields per `file-schema.md` §4.1 for Python records: `task_id`, `model_token`, `filename`, `dataset_variant`, `category`, `contracted` (resolved from `task_bank.csv`), `correctness_score`, `pytest_pass`, `checksum_match` (null for Python), `row_count_match` (null for Python), `snapshot_pass` (null for Python), `runtime_ms`, `peak_memory_bytes`, `token_usage_input`, `token_usage_output`, `formatting_violations`, `variant_mismatch`, `critic_review_path` (null — populated by Feature 4). **Does not include `generation_time_ms`, `flake8_violation_count`, `sqlfluff_violation_count`, `correctness_pass`, or `correctness_detail`.** Must pass T050 tests.

- [ ] T057 [US3] Implement `python-skill/scripts/eval_task.py` — CLI entry point: `eval-task --engine python [--task-id PY-001] [--contracted-only]`. On invocation: (1) reads `assets/task_bank.csv` to resolve `task_id` → three model filenames (FR-018 — no hardcoded paths); (2) invokes `schema_validator.py` on `task_bank.csv` and `eval_results.csv` before scoring begins; (3) filters `eval_results.csv` by the three filenames; (4) invokes `anonymizer.py` on each filename to derive `model_token`; (5) invokes `scorer.py` for correctness on the clean variant and reads performance fields; (6) invokes `scorer.py` for remaining variants if clean correctness = 100%; (7) invokes `schema_checker.py` per variant; (8) invokes `artifact_store.py` to persist `result.json`. `--contracted-only` flag: skips tasks where `task_bank.csv.contracted = false` without error. Must pass T051 integration test.

- [ ] T058 [US3] Populate `SKILL.md` for `python-skill/` — YAML frontmatter with `name: python-eval` and a specific, action-oriented `description` field (the primary signal Claude uses to load the skill); body references `assets/task_bank.csv` by path in one line only; no task list embedded inline; no `when_to_use` field; body must be concise (verbose content lives in `references/`).

**Checkpoint**: `eval-task --engine python --task-id PY-001` runs end-to-end against fixture data and produces a correctly structured `result.json`. All unit and integration tests pass. `--contracted-only` correctly filters to PY-001–PY-020. User Story 3 is fully functional and independently testable without F2 or F4.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Quickstart documentation, compliance verification, and regression check against Feature 1.

- [ ] T059 [P] Write `quickstart.md` for `python-skill/` — plain language (no jargon, acronyms explained on first use per constitution Principle 3); covers: prerequisites, how to invoke `eval-task --engine python`, how to use `--contracted-only`, how to read `result.json` output including `peak_memory_bytes`, `pytest_pass`, and `formatting_violations`, and what to do if `schema_validator.py` raises an error. Audience: Analytics Engineers and Data Engineers at the Banking Institution with no prior training.

- [ ] T060 Run the quickstart validation — follow `python-skill/quickstart.md` from scratch against the fixture data; verify all steps succeed without prior knowledge of the codebase; note any step that requires clarification and update `quickstart.md` accordingly.

- [ ] T061 [P] Verify constitution compliance for all Feature 3 files — confirm: no hardcoded file paths in scripts (all resolved via `task_bank.csv`); no real model names anywhere in code files, `eval_results.csv` rows, or directory paths (filename-letter convention `a`/`b`/`c` only); all datasets prefixed `synthetic_` with `SYNTHETIC` header label; no database or API framework code in `python-skill/`; client referred to as "Banking Institution" only; `python-skill/` and `sql-skill/` share no scripts or assets (they do share `references/`, `assets/task_bank.csv`, `assets/eval_results.csv`, and `assets/datasets/` — these are zip-root shared resources by design); per-author `results_*.csv` files are **not** present in the release output.

- [ ] T062 [P] Code review pass — confirm: `schema_validator.py` halts pipeline (not just logs a warning) on any `V-TB-*` or `V-ER-*` violation; `scorer.py` applies the 100% clean pass gate and never invokes pytest at runtime; `eval_task.py` reads all paths from `task_bank.csv` and never constructs paths by string concatenation; `result.json` contains the `contracted` flag on every record and does not contain `generation_time_ms`, `flake8_violation_count`, `correctness_pass`, or `correctness_detail`; no Feature 3 script invokes the merge script at harness runtime (merge is dataset preparation only, owned by F1).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Depends on Feature 1 complete — `references/` (including `file-schema.md`), `assets/task_bank.csv`, `assets/eval_results.csv`, and `assets/datasets/` must exist; `python-skill/` tree must not yet exist
- **Phase 2 (Foundational)**: Depends on Phase 1 — T042 (file-schema verification) must complete before T043 (task_bank Python rows) and T044 (fixture Python rows); T045 (merge) depends on T044
- **Phase 3 (User Story 3)**: Tests (T047–T051) can be written as soon as Phase 2 completes; implementation (T052–T058) follows tests
- **Phase 4 (Polish)**: Depends on Phase 3 checkpoint passing

### Within Phase 3

- T047–T051 (tests): Write first. Ensure FAIL before T052–T058 begin.
- T052 (`anonymizer.py`): Depends on T004 (filename regex defined in `file-schema.md`); no other internal dependencies
- T053 (`schema_validator.py`): Depends on T042 (schema confirmed) and T043 (`task_bank.csv` Python rows populated)
- T054 (`scorer.py`): Depends on T045 (fixture `eval_results.csv` with Python rows) and T048 (test exists and fails)
- T055 (`schema_checker.py`): No dependencies beyond Phase 2
- T056 (`artifact_store.py`): Depends on T004 (`result.json` schema defined)
- T057 (`eval_task.py`): Depends on T052–T056 all passing
- T058 (`SKILL.md`): No code dependencies; can be authored in parallel with Phase 3 implementation

### Relationship to Other Features

- Feature 3 is fully independent of Feature 2 (SQL Critic) — they operate on separate skill trees and can be developed in parallel
- Feature 3 is a prerequisite for Feature 4 (Python Critic) — Feature 4 extends `python-skill/` in place and requires `eval_task.py` and `artifact_store.py` from this feature
- Feature 3 output (`result.json` with `formatting_violations`, `pytest_pass`, and all performance metrics) is required input for Feature 5 (Comparative Scorecard)

### Parallel Opportunities

T041 and T042 (Phase 1) can run in parallel. T043, T044, and T046 (Phase 2) can run in parallel once Phase 1 is complete; T045 depends on T044. All test tasks (T047–T051) can run in parallel once Phase 2 completes. T052, T055, T056, and T058 can all be implemented in parallel.

---

## Parallel Example: Phase 2

```bash
# T043, T044, T046 can run simultaneously:
Task: "Populate assets/task_bank.csv Python rows"                                    # T043
Task: "Extend per-author fixture files with Python rows for PY-001–PY-005"           # T044
Task: "Create per-task code file stubs for PY-001–PY-005 in assets/tasks/"           # T046

# T045 runs after T044 is complete:
Task: "Re-run merge_results.py to produce fixture eval_results.csv with both languages"  # T045
```

---

## Implementation Strategy

### MVP First (User Story 3 Only)

1. Confirm Feature 1 checkpoint is passing (prerequisite)
2. Complete Phase 1: scaffold `python-skill/`; verify `references/file-schema.md` is complete
3. Complete Phase 2: populate `task_bank.csv` Python rows; extend per-author fixtures with Python rows; re-run the merge to produce a two-language fixture `eval_results.csv`; create per-task Python code file stubs
4. Write tests (T047–T051) — ensure they FAIL
5. Implement scripts in dependency order: `anonymizer.py` → `schema_validator.py` → `scorer.py` → `schema_checker.py` → `artifact_store.py` → `eval_task.py`
6. **STOP and VALIDATE**: Run integration test end-to-end; run quickstart from scratch
7. Complete Phase 4 polish

### Incremental Delivery

Feature 3 delivers the quantitative half of the Python four-dimension rubric. Once the Phase 3 checkpoint passes, Feature 4 (Python Critic) can begin extending `python-skill/` in place. Feature 3 can be developed in parallel with Feature 2 since they operate on independent skill trees.

---

## Notes

- [P] tasks = different files, no blocking dependencies between them
- [US3] label maps all tasks to User Story 3 — Python Quantitative Evaluation
- Task IDs begin at T041 to maintain cross-feature traceability (F1: T001–T029, F2: T030–T040)
- The harness never executes model-generated code — `scorer.py` reads the pre-recorded `pytest_pass` field from `eval_results.csv`; no pytest, tracemalloc, or flake8 is invoked at runtime
- `formatting_violations` is pre-recorded in `eval_results.csv` — no flake8 invocation by the harness
- `peak_memory_bytes` and `runtime_ms` are pre-recorded in `eval_results.csv` — no tracemalloc invocation by the harness
- `generation_time_ms`, `flake8_violation_count`, `sqlfluff_violation_count`, `correctness_pass`, `correctness_detail` are **excluded fields** per Amendments A2 and A3 — they must not appear in any schema, script, fixture, or artifact
- Model identity is encoded in code filenames (`a`/`b`/`c`); `model_token` is derived at load time — no real model names appear anywhere in the pre-recorded data
- Per-author `results_*.csv` files are an authoring convention only — they are merged by `merge_results.py` (F1 T017) into `assets/eval_results.csv` during dataset preparation and must **never** appear in the released zip
- `python-skill/` and `sql-skill/` are independent trees for scripts and personas, but they **share zip-root resources**: `references/`, `assets/task_bank.csv`, `assets/eval_results.csv`, `assets/datasets/`. This is by design per Constitution folder structure.
- `reference_solution.py` and `test_solution.py` are documentation artifacts only — they must not be executed by the harness at any point
- Commit after each task or logical group; do not batch multiple scripts into one commit
- Stop at the Phase 3 checkpoint to validate User Story 3 independently before beginning Feature 4
