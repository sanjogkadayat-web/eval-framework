---
description: "Task list for Feature 1 — SQL Quantitative Evaluation"
---

# Tasks: Feature 1 — SQL Quantitative Evaluation

**Input**: Design documents from `specs/001-sql-quant-eval/`
**Prerequisites**: `feature1_plan.md` (required), `spec.md` (required for user stories), `constitution.md` (required for all guardrails)

**Tests**: Harness self-tests are included per the Feature 1 plan. Task-level pytest files are NOT included — SQL correctness is determined by interpreting the pre-recorded `checksum`, `row_count`, and `snapshot_pass` fields in `assets/eval_results.csv` against reference result sets, not by running model-generated code.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. Feature 1 has one primary user story (US1 — SQL Quantitative Evaluation, Priority P1) covering both acceptance scenarios. All setup and foundational work is prerequisite to that story.

**Architecture**: Amendments A1, A2, and A3 are all ratified. This task list implements the **A3 two-table architecture**: `assets/task_bank.csv` (master index with prompts inline and per-model filenames) and `assets/eval_results.csv` (unified metrics produced by merging three per-author files). See `references/file-schema.md` for the canonical schemas.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1)
- Paths follow the single-project CLI skill structure defined in the Feature 1 plan

---

## Phase 1: Setup

**Purpose**: Establish the zip root scaffold, shared references layer, and `requirements.txt` before any feature work begins.

- [ ] T001 Create top-level zip root scaffold: `eval-framework/` with empty `README.md`, `requirements.txt`, `references/`, `assets/`, `sql-skill/`, `python-skill/`, `scorecard/`, `outputs/` per constitution folder structure

- [ ] T002 [P] Create `requirements.txt` at zip root — declare all Python 3.11+ stdlib dependencies explicitly (`csv`, `json`, `hashlib`, `pathlib`, `re`, `statistics`); note that `pytest`, `flake8`, `sqlfluff`, and `tracemalloc`-instrumented scripts are dataset preparation tools only and must be listed separately with a comment making that clear

- [ ] T003 [P] Create `sql-skill/` scaffold: `SKILL.md` (stub — YAML frontmatter `name` and `description` fields only, no task list inline), `scripts/` (empty), `assets/personas/` (empty), `assets/tasks/` (empty), `assets/datasets/` (empty)

**Checkpoint**: Zip root scaffold exists. `sql-skill/` tree is in place. `requirements.txt` is committed.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: All `references/` documents and synthetic dataset fixtures must exist and be validated before any scoring script is written. The constitution is explicit: deterministic rules, epsilon values, and file schemas must be declared in `references/` before the first evaluation run.

**⚠️ CRITICAL**: No scoring script (`scorer.py`, `variant_scorer.py`, `schema_validator.py`) and no merge script (`merge_results.py`) may be written until this phase is complete.

- [ ] T004 Author `references/file-schema.md` — **single source of truth** for the canonical schemas. Must define:
      - **`task_bank.csv` schema**: 7 fields — `task_id`, `contracted`, `category`, `prompt`, `model_a_filename`, `model_b_filename`, `model_c_filename`. Primary key: `task_id`. Cross-field rules: three filenames share same numeric prefix and extension; extension matches language implied by `task_id`.
      - **`eval_results.csv` schema**: 12 fields — `filename`, `dataset_variant`, `token_usage_input`, `token_usage_output`, `runtime_ms`, `peak_memory_bytes` (Python only), `formatting_violations`, `pytest_filename` (Python only), `pytest_pass` (Python only), `checksum` (SQL only), `row_count` (SQL only), `snapshot_pass` (SQL only). Primary key: `(filename, dataset_variant)`.
      - **Per-author `results_a.csv` / `results_b.csv` / `results_c.csv`**: identical schema to `eval_results.csv`; 1,000 rows each; letter-binding rule (rows in `results_a.csv` must have `filename` matching `^task\d+a\.(py|sql)$`).
      - **`result.json` output artifact schema**: full field list with per-language null rules.
      - **Validation rule IDs** (`V-TB-*`, `V-ER-*`, `V-MG-*`) for `schema_validator.py` and `merge_results.py` to reference in error messages.
      - **Filename parsing regex**: `^task(?P<task_num>\d+)(?P<model_letter>[abc])\.(?P<ext>py|sql)$`.
      - **Dataset variant enum**: `clean`, `null_heavy`, `duplicate_heavy`, `medium`, `large` — exact lowercase values.
      - **Explicit field exclusions**: `generation_time_ms`, `model_token`, `language`, `correctness_pass`, `correctness_detail`, `variant_mismatch`, `flake8_violation_count`, `sqlfluff_violation_count` — must not appear in `eval_results.csv`.

- [ ] T005 [P] Author `references/deterministic-rules.md` — declare: epsilon tolerance for float comparisons (IEEE 754 standard), fixed random seeds (explicit values), SQL result comparison rules (`ORDER BY` on stable keys OR set-based equivalence with numeric epsilon), `sqlfluff` dialect configuration. No values may be hardcoded in scripts — all must reference this file.

- [ ] T006 [P] Author `references/methodology.md` — document: one-shot evaluation policy (one attempt per model, no revisions), pre-recorded evaluation data model (harness is comparison engine only — never executes code), model anonymization flow via the filename-letter convention (`a`/`b`/`c` at the asset layer; `model_token` derived at load time; real names in lookup outside zip only), dataset preparation phase vs. harness runtime distinction, per-author authoring convention (`results_*.csv` files merged into `eval_results.csv` before release — never shipped).

- [ ] T007 [P] Author `references/rubric.md` — document the four-dimension rubric: (1) Correctness — numeric, from pre-recorded `checksum` / `row_count` / `snapshot_pass` fields compared against reference result sets; (2) Formatting — numeric, from pre-recorded `formatting_violations` field; (3) Performance — numeric, from pre-recorded `runtime_ms`, `token_usage_input`, `token_usage_output`; (4) Critic Review — qualitative only, generated at harness runtime. Note that Critic is out of scope for Feature 1.

- [ ] T008 Create synthetic fixture datasets in `assets/datasets/` — CSV files per variant per table, each prefixed `synthetic_` and containing a `SYNTHETIC` label in the file header. Tables: `transactions`, `accounts`, `daily_balances`. Variants: `clean` (~500 rows, no nulls, no dupes), `null_heavy` (~500 rows, 20–30% nulls on join keys and numeric cols), `duplicate_heavy` (~600 rows, ~15–20% duplicate primary keys), `medium` (~5,000 rows, clean schema), `large` (~50,000 rows, high cardinality). All per the schema in `dataset_structure.md`. No real account numbers, routing numbers, or customer identifiers — synthetic IDs only (e.g., `SYNTHETIC_TXN_000001`, `SYNTHETIC_ACCT_0001`).

- [ ] T009 Create `assets/task_bank.csv` — master index, exactly 200 rows (100 SQL + 100 Python). Schema per `references/file-schema.md` (T004): `task_id`, `contracted`, `category`, `prompt`, `model_a_filename`, `model_b_filename`, `model_c_filename`. `contracted = true` for exactly `SQL-001`–`SQL-020` and `PY-001`–`PY-020` (40 rows total). `prompt` text stored inline (CSV-quoted). Filenames follow `task{N}{letter}.{ext}` convention. For Phase 1 / Feature 1 only, populate SQL rows fully; Python rows may be stubbed with placeholder filenames matching the `.py` extension pattern — Feature 3 populates them fully in T043.

**Checkpoint**: All four `references/` documents are authored and reviewed. `references/file-schema.md` defines the unified schemas with the complete set of validation rules. Synthetic datasets exist and are labeled. `task_bank.csv` is in place with all 200 rows. No scoring script is written yet.

---

## Phase 3: User Story 1 — SQL Quantitative Evaluation (Priority: P1) 🎯 MVP

**Goal**: An Analytics Engineer selects a SQL Task ID and the harness reads pre-recorded metric rows from `eval_results.csv` for all three models, scores correctness and performance, applies the clean-pass gate for variant inclusion, and persists all artifacts keyed by `task_id/model/category`.

**Independent Test**: Select a SQL task (e.g., SQL-001), confirm `eval_task.py` reads `task_bank.csv` to resolve `task_id` → three model filenames, filters `eval_results.csv` by `(filename, dataset_variant)` pairs matching those filenames, interprets correctness fields against reference result sets, reads performance fields directly, surfaces variant rows for 100%-clean-pass models, and writes `result.json` to `outputs/SQL-001/[model]/[category]/`. Verify `--contracted-only` evaluates only contracted tasks (SQL-001–SQL-020).

### Harness Self-Tests for User Story 1 ⚠️

> **Write these tests FIRST. Ensure they FAIL before writing the implementation.**

- [ ] T010 [P] [US1] Write unit test `tests/unit/test_anonymizer.py` — verify `anonymizer.py` derives `model_token` (`model_a`/`model_b`/`model_c`) from the filename letter at load time; verify no real model name appears in any output; test with filenames for all three letters (`task1a.sql`, `task1b.sql`, `task1c.sql`); verify the anonymizer rejects filenames that do not match the canonical regex `^task\d+[abc]\.(py|sql)$`.

- [ ] T011 [P] [US1] Write unit test `tests/unit/test_scorer.py` — verify `scorer.py` correctly interprets, per-variant: `row_count` match against reference row count (pass/fail), `checksum` match against reference checksum (exact equality, lowercase hex), `snapshot_pass` boolean. Verify `correctness_score` is computed from all three primitives. Verify deterministic output for identical inputs. Test edge cases: empty result set, mismatched column count, float rounding (epsilon from `references/deterministic-rules.md`).

- [ ] T012 [P] [US1] Write unit test `tests/unit/test_schema_validator.py` — verify `schema_validator.py` raises a clear validation error referencing the specific check ID (`V-TB-*`, `V-ER-*`) when: header mismatch, `task_id` format violation, contracted distribution wrong, filename cross-field inconsistency in `task_bank.csv`; duplicate `(filename, dataset_variant)` pair in `eval_results.csv`; orphan filename in `eval_results.csv` not in `task_bank.csv`; missing variant for a filename; SQL-only field populated on `.py` row (or vice versa); non-negative integer constraint violation; `checksum` not matching 64-char lowercase hex; per-filename invariant violation (e.g., `token_usage_input` differing across variant rows for same filename). Verify it passes on conformant fixture files.

- [ ] T012b [P] [US1] Write unit test `tests/unit/test_merge_results.py` — verify `merge_results.py` validates, per `references/file-schema.md` §6:
      - V-MG-1: rejects missing source files
      - V-MG-2: rejects header mismatch between files
      - V-MG-3: flags unexpected row counts (warn or fail per release policy)
      - V-MG-4: rejects rows in `results_a.csv` where `filename` letter is not `a` (same for `b`, `c`)
      - V-MG-5: rejects unknown `dataset_variant` values in any source file
      - V-MG-6: rejects duplicate `(filename, dataset_variant)` within one source file
      - V-MG-7: rejects cross-file primary-key collisions
      - V-MG-8: verifies merged row count equals sum of source rows
      - V-MG-9: verifies merged primary-key uniqueness
      - V-MG-10: merged file passes all `V-ER-*` checks
      Verify a successful merge produces the expected row count and preserves row order (`a` → `b` → `c`). Verify no per-author file is written to the release output path.

- [ ] T013 [P] [US1] Write unit test `tests/unit/test_artifact_store.py` — verify `artifact_store.py` writes `result.json` to the correct path (`outputs/[task_id]/[model]/[category]/result.json`); verify all required fields per `file-schema.md` §4 are present (`task_id`, `model_token`, `filename`, `dataset_variant`, `category`, `contracted`, `correctness_score`, `checksum_match`, `row_count_match`, `snapshot_pass`, `runtime_ms`, `token_usage_input`, `token_usage_output`, `formatting_violations`, `variant_mismatch`, `critic_review_path`); verify Python-only fields (`pytest_pass`, `peak_memory_bytes`) are `null` for SQL records; verify `generation_time_ms`, `flake8_violation_count`, `sqlfluff_violation_count`, `correctness_pass`, `correctness_detail` are **absent**; verify idempotent overwrite behavior.

- [ ] T014 [US1] Write integration test `tests/integration/test_eval_task_pipeline.py` — using hand-crafted fixture `task_bank.csv`, `eval_results.csv`, code files under `assets/tasks/`, and reference result sets, verify the full `eval-task --engine sql --task-id SQL-001` pipeline produces a correctly structured `result.json` with all fields populated per `file-schema.md` §4; verify `--contracted-only` skips non-contracted tasks without error (depends on T010–T013, T012b test stubs existing).

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create per-task asset stubs for a representative contracted subset (SQL-001–SQL-005) in `assets/tasks/[task_id]/`: `task{N}a.sql`, `task{N}b.sql`, `task{N}c.sql` (three model code files — synthetic placeholders for fixture testing), `reference_solution.sql` (human-authored baseline), `reference_results/` (five CSVs: `clean.csv`, `null_heavy.csv`, `duplicate_heavy.csv`, `medium.csv`, `large.csv` — pre-computed from the reference solution against the synthetic datasets in T008). **No per-task `prompt.md` file** — prompt text is stored inline in `task_bank.csv`.

- [ ] T016 [US1] Create per-author fixture files `results_a.csv`, `results_b.csv`, `results_c.csv` for Feature 1 development and testing. Each file contains rows for SQL-001–SQL-005 only (15 data rows per file: 5 tasks × 1 model × 5 variants) with realistic synthetic values for all fields per `file-schema.md` §2. SQL-only fields populated; Python-only fields left empty. Header row matches the canonical `eval_results.csv` header exactly. These fixture files live outside the released zip — they are used only by the merge script test (T012b) and the integration test (T014) during development. For production, the three team members will generate full 1,000-row per-author files on their separate machines.

- [ ] T017 [US1] Implement `sql-skill/scripts/merge_results.py` — dataset preparation utility implementing FR-019. Reads `results_a.csv`, `results_b.csv`, `results_c.csv` from a configurable input path; applies all ten `V-MG-*` validation checks per `file-schema.md` §6; concatenates rows in order (`a`, then `b`, then `c`) with a single canonical header; writes `assets/eval_results.csv`. On any validation failure, halts with a clear error message citing the failed check ID (e.g., `[merge_results] V-MG-7 failure: task3b.py/clean appears in both results_a.csv and results_b.csv`). Runs post-merge validation (V-MG-8 through V-MG-10) before writing the output. **Not invoked by the harness at runtime** — this is a dataset-preparation tool. Must pass T012b tests.

- [ ] T018 [US1] Implement `sql-skill/scripts/anonymizer.py` — parses the canonical filename regex `^task(?P<task_num>\d+)(?P<model_letter>[abc])\.(?P<ext>py|sql)$` and returns a dict containing `task_num`, `model_letter`, `ext`, derived `task_id` (e.g., `SQL-001`), and derived `model_token` (e.g., `model_a`). No real model names pass through. Rejects filenames not matching the regex with a clear error. Must pass T010 tests.

- [ ] T019 [US1] Implement `sql-skill/scripts/schema_validator.py` — validates `assets/task_bank.csv` against the 11 `V-TB-*` checks and `assets/eval_results.csv` against the 13 `V-ER-*` checks declared in `references/file-schema.md`. On any failure, halts the pipeline with a clear error message citing the specific check ID, the file, the row (where applicable), and the offending field (per `file-schema.md` §5.3). Does NOT invoke the merge script — that is a dataset preparation step, validated separately via T017 / T012b. Must pass T012 tests.

- [ ] T020 [US1] Implement `sql-skill/scripts/scorer.py` — filters `assets/eval_results.csv` by `(filename, dataset_variant)` for a given task and model; interprets the three correctness primitives (`checksum` against reference checksum, `row_count` against reference row count, `snapshot_pass` boolean) to compute `checksum_match`, `row_count_match`, `snapshot_pass`, and a composite `correctness_score`; reference checksums and row counts are read from `assets/tasks/[task_id]/reference_results/[variant].csv`; applies the clean-pass gate (variant rows other than `clean` are excluded from the scorecard if `clean` correctness is not 100%). Reads epsilon from `references/deterministic-rules.md` for any float comparisons — never hardcodes tolerances. Must pass T011 tests.

- [ ] T021 [US1] Implement `sql-skill/scripts/schema_checker.py` — detects column name or data type drift between a variant's reference result set and the clean baseline schema at harness runtime. Writes `variant_mismatch = true` to the run's `result.json` when drift is detected. **`variant_mismatch` is not a field in `eval_results.csv`** — it is derived at runtime and surfaced only in `result.json`. Mismatched variants are reported separately and excluded from correctness scoring.

- [ ] T022 [US1] Implement `sql-skill/scripts/variant_scorer.py` — for model answers that achieve 100% correctness on the `clean` variant: invokes `scorer.py` per variant for the remaining four variant rows; invokes `schema_checker.py` per variant; collects per-variant pass/fail and `variant_mismatch` flags. Does not process non-clean variants for answers that fail on `clean`.

- [ ] T023 [US1] Implement `sql-skill/scripts/artifact_store.py` — persists all run outputs to `outputs/[task_id]/[model]/[category]/result.json`; fields per `file-schema.md` §4.1: `task_id`, `model_token`, `filename`, `dataset_variant`, `category`, `contracted` (resolved from `task_bank.csv`), `correctness_score`, `pytest_pass` (null for SQL), `checksum_match`, `row_count_match`, `snapshot_pass`, `runtime_ms`, `peak_memory_bytes` (null for SQL), `token_usage_input`, `token_usage_output`, `formatting_violations`, `variant_mismatch`, `critic_review_path` (null in Feature 1 — populated by Feature 2). **Does not include `generation_time_ms`, `flake8_violation_count`, `sqlfluff_violation_count`, `correctness_pass`, or `correctness_detail`.** Must pass T013 tests.

- [ ] T024 [US1] Implement `sql-skill/scripts/eval_task.py` — CLI entry point: `eval-task --engine sql [--task-id SQL-001] [--contracted-only]`. On invocation: (1) reads `assets/task_bank.csv` to resolve `task_id` → three model filenames (FR-018 — no hardcoded paths); (2) invokes `schema_validator.py` on `task_bank.csv` and `eval_results.csv` before scoring begins; (3) filters `eval_results.csv` by the three filenames; (4) invokes `anonymizer.py` on each filename to derive `model_token`; (5) invokes `scorer.py` for correctness on the clean variant and reads performance fields; (6) invokes `variant_scorer.py` if clean correctness = 100%; (7) invokes `artifact_store.py` to persist `result.json`. `--contracted-only` flag: skips tasks where `task_bank.csv.contracted = false` without error. Must pass T014 integration test.

- [ ] T025 [US1] Populate `SKILL.md` for `sql-skill/` — YAML frontmatter with `name: sql-eval` and a specific, action-oriented `description` field (per constitution — this is the primary signal Claude uses to load the skill); body references `assets/task_bank.csv` by path in one line only; no task list embedded inline; no `when_to_use` field; body must be concise (verbose content lives in `references/`).

**Checkpoint**: `eval-task --engine sql --task-id SQL-001` runs end-to-end against fixture data and produces a correctly structured `result.json`. `merge_results.py` runs successfully against fixture per-author files to produce a valid `eval_results.csv`. All unit and integration tests pass. `--contracted-only` correctly filters to SQL-001–SQL-020. User Story 1 is fully functional and independently testable.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Hardening, validation, and quickstart documentation.

- [ ] T026 [P] Write `quickstart.md` for `sql-skill/` — plain language (no jargon, acronyms explained on first use per constitution Principle 3); covers: prerequisites, how to invoke `eval-task --engine sql`, how to use `--contracted-only`, how to read `result.json` output, the per-author authoring workflow for dataset preparation (three `results_*.csv` files merged via `merge_results.py` into `eval_results.csv` before release), and what to do if `schema_validator.py` raises an error. Audience: Analytics Engineers and Evaluation Leads at the Banking Institution with no prior training.

- [ ] T027 Run the quickstart validation — follow `quickstart.md` from scratch against the fixture data; verify all steps succeed without prior knowledge of the codebase; note any step that requires clarification and update `quickstart.md` accordingly.

- [ ] T028 [P] Verify constitution compliance checklist for all produced files — confirm: no hardcoded file paths in scripts (all resolved via `task_bank.csv`); no real model names anywhere in code files, `eval_results.csv` rows, or directory paths (filename-letter convention `a`/`b`/`c` only); all datasets prefixed `synthetic_` with `SYNTHETIC` header label; no database or API framework code anywhere in the tree; client referred to as "Banking Institution" only in all documents and asset files; per-author `results_*.csv` files are **not** present in the release output (only the merged `eval_results.csv` ships).

- [ ] T029 [P] Code review pass: confirm `schema_validator.py` halts pipeline (not just logs a warning) on any `V-TB-*` or `V-ER-*` violation; confirm `merge_results.py` halts release on any `V-MG-*` violation; confirm `scorer.py` reads epsilon from `references/deterministic-rules.md` and never hardcodes a tolerance value; confirm `eval_task.py` reads all paths from `task_bank.csv` and never constructs paths by string concatenation; confirm `result.json` does not contain `generation_time_ms`, `flake8_violation_count`, `sqlfluff_violation_count`, `correctness_pass`, or `correctness_detail`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 completion — BLOCKS all implementation tasks
- **Phase 3 (User Story 1)**: Tests (T010–T014, T012b) can be written as soon as Phase 2 completes; implementation (T015–T025) follows tests
- **Phase 4 (Polish)**: Depends on Phase 3 checkpoint passing

### Within Phase 3

- T010–T014 + T012b (tests): Write first. Ensure FAIL before T015–T025 begin.
- T015–T016 (fixtures and asset stubs): Can run in parallel with T010–T014
- T017 (`merge_results.py`): Depends on T004 (`file-schema.md` merge rules) and T012b (test exists and fails) and T016 (fixture per-author files exist)
- T018 (`anonymizer.py`): Depends on T004 (filename regex defined); no other internal dependencies
- T019 (`schema_validator.py`): Depends on T004 (`file-schema.md` with V-TB-* / V-ER-* rules) and T009 (`task_bank.csv`)
- T020 (`scorer.py`): Depends on T005 (`deterministic-rules.md`) and T015 (reference result sets)
- T021 (`schema_checker.py`): No dependencies beyond Phase 2
- T022 (`variant_scorer.py`): Depends on T020 and T021
- T023 (`artifact_store.py`): Depends on T004 (`result.json` schema)
- T024 (`eval_task.py`): Depends on T018–T023 all passing
- T025 (`SKILL.md`): No code dependencies; can be authored in parallel with Phase 3 implementation

### Parallel Opportunities

All Phase 1 tasks (T001–T003) can run in parallel. All Phase 2 tasks (T004–T009) can run in parallel once Phase 1 is complete. Within Phase 3, all test tasks (T010–T014, T012b) and all fixture/stub creation tasks (T015–T016) can run in parallel.

---

## Parallel Example: Phase 2

```bash
# All four references documents can be authored simultaneously:
Task: "Author references/file-schema.md"                  # T004
Task: "Author references/deterministic-rules.md"          # T005
Task: "Author references/methodology.md"                  # T006
Task: "Author references/rubric.md"                       # T007

# Synthetic datasets and task_bank.csv can be created in parallel:
Task: "Create synthetic fixture datasets in assets/datasets/"  # T008
Task: "Create assets/task_bank.csv"                            # T009
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational — **CRITICAL, blocks all scoring and merge work**
3. Write tests (T010–T014, T012b) — ensure they FAIL
4. Create fixtures and stubs (T015–T016)
5. Implement scripts in dependency order: `merge_results.py` → `anonymizer.py` → `schema_validator.py` → `scorer.py` → `schema_checker.py` → `variant_scorer.py` → `artifact_store.py` → `eval_task.py`
6. **STOP and VALIDATE**: Run integration test end-to-end; run merge test; run quickstart.md from scratch
7. Complete Phase 4 polish

### Incremental Delivery

Feature 1 has a single user story. Once the integration test passes end-to-end, Feature 1 is complete and Feature 2 (SQL Critic) can begin. Feature 2 extends `sql-skill/` in place and does not require Feature 1 to be rewritten.

---

## Notes

- [P] tasks = different files, no blocking dependencies between them
- [US1] label maps all tasks to User Story 1 — SQL Quantitative Evaluation
- The harness never executes model-generated code — `scorer.py` interprets pre-recorded `checksum` / `row_count` / `snapshot_pass` fields against reference result sets; no SQL engine is invoked at runtime
- `formatting_violations` is pre-recorded in `eval_results.csv` — no sqlfluff invocation by the harness
- `generation_time_ms`, `flake8_violation_count`, `sqlfluff_violation_count`, `correctness_pass`, `correctness_detail` are **excluded fields** per Amendments A2 and A3 — they must not appear in any schema, script, fixture, or artifact
- Model identity is encoded in code filenames (`a`/`b`/`c`); `model_token` is derived at load time — no real model names appear anywhere in the pre-recorded data
- Per-author `results_a.csv` / `results_b.csv` / `results_c.csv` are an **authoring convention only** — they are merged via `merge_results.py` (T017) into `assets/eval_results.csv` during dataset preparation and must **never** appear in the released zip
- Commit after each task or logical group; do not batch multiple scripts into one commit
- Stop at the Phase 3 checkpoint to validate User Story 1 independently before beginning Feature 2
