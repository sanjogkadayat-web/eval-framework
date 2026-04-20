---
description: "Task list for Feature 5 — Comparative Scorecard"
---

# Tasks: Feature 5 — Comparative Scorecard

**Input**: Design documents from `specs/005-comparative-scorecard/`
**Prerequisites**: `feature5_plan.md` (required), `spec.md` (required for user stories)
**FRs satisfied**: FR-012, FR-013
**User Story**: US5 — Comparative Scorecard and Failure Analysis (Priority: P3)

**Architecture**: Amendments A1, A2, and A3 are all ratified. Feature 5 is largely insulated from A3 because `collector.py` reads `result.json` artifacts from `outputs/`, not the pre-recorded data directly. The A3-facing adjustments are narrow: `result.json` now carries the A3 field names (`formatting_violations`, `pytest_pass`, `checksum_match`, `row_count_match`, `snapshot_pass`, `variant_mismatch`) and does NOT carry the excluded fields (`generation_time_ms`, `flake8_violation_count`, `sqlfluff_violation_count`, `correctness_pass`, `correctness_detail`). The `contracted` flag is resolved from `assets/task_bank.csv` upstream and propagated via `result.json`; `collector.py` continues to cross-validate contracted task IDs against `task_bank.csv`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Exact file paths from `feature5_plan.md` are used throughout

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the `scorecard/` package structure and test fixtures needed by all
subsequent phases. No business logic lives here — only scaffolding and sample data.

- [ ] T001 Create the `scorecard/` package directory at zip root with `scorecard/__init__.py`
      (empty); create `run_scorecard.py` at zip root as an empty file with a module-level
      docstring: `"""CLI entry point for the scorecard command. See feature5_plan.md."""`

- [ ] T002 [P] Create `tests/fixtures/sample_result.json` — a minimal valid `result.json`
      fixture containing one record per model × task × variant with all required metric
      fields populated per `references/file-schema.md` §4: `task_id`, `model_token`,
      `filename`, `dataset_variant`, `category`, `contracted`, `correctness_score`,
      `pytest_pass` (Python) or `checksum_match` + `row_count_match` + `snapshot_pass`
      (SQL), `runtime_ms`, `peak_memory_bytes` (Python only), `token_usage_input`,
      `token_usage_output`, `formatting_violations`, `variant_mismatch`,
      `critic_review_path`. Include both an SQL example record and a Python example
      record in the fixture to exercise per-language null patterns.
      **Excluded fields**: `generation_time_ms`, `flake8_violation_count`,
      `sqlfluff_violation_count`, `correctness_pass`, `correctness_detail` —
      must not appear in the fixture.

- [ ] T003 [P] Create `tests/fixtures/sample_critic_review.md` — a minimal valid
      `critic_review.md` fixture containing all four required sections in order:
      `## Strengths`, `## Failures`, `## Mitigation Strategies`, `## Observations`.
      Each section must contain at least two bullet points of placeholder text.

**Checkpoint**: `scorecard/` package exists; `run_scorecard.py` exists at zip root;
two fixture files exist under `tests/fixtures/`. No logic implemented yet.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build `collector.py` — the single entry point that walks the `outputs/`
directory and returns a normalised list of run records. Every downstream module
(`aggregator.py`, `baseline_delta.py`, `json_emitter.py`, `markdown_emitter.py`)
operates on the list that `collector.py` produces. Nothing else in F5 can be
implemented or tested without it.

⚠️ **CRITICAL**: No Phase 3 work can begin until this phase is complete.

- [ ] T004 Implement `scorecard/collector.py` — core collection logic:

      Responsibilities:
      - Walk the `outputs/` directory tree, locating all `result.json` files under
        `outputs/[task_id]/[model]/[category]/`
      - Read and deserialise each `result.json`
      - Apply `--engine` filter (sql | python | all) by inspecting the `filename` field
        in each record (`.sql` → SQL, `.py` → Python) — language is not a top-level
        field in `result.json` under A3 but is derivable from `filename`
      - Apply `--model` filter against the `model_token` field (values:
        `model_a`, `model_b`, `model_c`)
      - Apply `--dataset-variant` filter against the `dataset_variant` field
      - Return a list of run record dicts — one dict per `result.json` read
      - If `outputs/` does not exist or is empty, return an empty list (not an error)

      Input: path to `outputs/` directory, optional filter values for engine, model,
      dataset-variant
      Output: list of run record dicts

- [ ] T005 Extend `scorecard/collector.py` with `--contracted-only`
      filtering and `task_bank.csv` cross-validation:

      Responsibilities:
      - Accept `--contracted-only` flag as an optional parameter
      - When `--contracted-only` is set: read the `contracted` field from each
        `result.json`; exclude records where `contracted` is `false` or absent
      - Cross-validate contracted task IDs against `assets/task_bank.csv`:
        load `task_bank.csv`, extract all rows where `contracted = true`
        (expected: exactly 40 rows — SQL-001–SQL-020 and PY-001–PY-020),
        compare the set of contracted `task_id` values present in the collected
        `result.json` artifacts against the expected contracted set from `task_bank.csv`
      - If any expected contracted task IDs are absent from the artifact set, do NOT
        silently produce an incomplete scorecard — instead surface a list of missing
        task IDs as a clear error message and halt (per spec edge case: "Contracted-only
        on partial artifact set")
      - `task_bank.csv` path resolved relative to zip root (never hardcoded — per FR-018)

      Input: `--contracted-only` boolean, path to `assets/task_bank.csv`
      Output: filtered list of run record dicts; error if contracted task IDs are missing

- [ ] T006 [P] Write `tests/unit/test_collector.py` — unit tests for `collector.py`:

      Tests for T004 (core, can be written immediately):
      - Directory walk returns correct number of records from fixture structure
      - `--engine sql` filter returns only records where `filename` ends in `.sql`
      - `--engine python` filter returns only records where `filename` ends in `.py`
      - `--model` filter correctly excludes non-matching records (test all three
        `model_token` values)
      - `--dataset-variant` filter correctly excludes non-matching records
      - Empty `outputs/` directory returns empty list without error
      - Malformed `result.json` raises a clear parse error (not a silent skip)

      Tests for T005 (contracted-only filtering):
      - `--contracted-only` returns only records where `contracted = true`
      - `--contracted-only` with a complete contracted set passes cross-validation
      - `--contracted-only` with missing contracted task IDs raises a clear error
        listing the absent task IDs

**Checkpoint**: `collector.py` core and contracted-only logic are both complete and
all unit tests pass. Phase 3 can now begin.

---

## Phase 3: User Story 5 — Comparative Scorecard and Failure Analysis (Priority: P3) 🎯

**Goal**: Deliver the complete scorecard pipeline — five processing modules plus the
CLI entry point — so that an Evaluation Lead can run `scorecard --outdir <path>` and
receive a unified `scorecard.json` and a human-readable `scorecard.md` without manual
intervention. Both `--contracted-only` (40 tasks — client deliverable) and full
(200 tasks — value-add) modes must be supported.

**Independent Test**: Run `scorecard --outdir ./out` against the fixture artifacts
in `tests/fixtures/`. Verify `out/scorecard.json` and `out/scorecard.md` are both
produced. Verify `scorecard.json` contains one record per model × task × variant with
all metric fields populated per `file-schema.md` §4 (no `generation_time_ms`,
`flake8_violation_count`, `sqlfluff_violation_count`, `correctness_pass`, or
`correctness_detail`) and a `contracted` flag on every record. Verify `scorecard.md`
contains per-model aggregates, variant pass rates, baseline deltas, and Critic review
summaries. Verify `--contracted-only` produces a scorecard covering only contracted
tasks and is labelled as the client deliverable.

---

### Tests for User Story 5 ⚠️

> **Write these tests FIRST; ensure they FAIL before implementation of the module
> they cover.**

- [ ] T007 [P] [US5] Write `tests/unit/test_critic_parser.py` — unit tests for
      `scorecard/critic_parser.py`:
      - A valid four-section `critic_review.md` returns a dict with keys `strengths`,
        `failures`, `mitigation_strategies`, `observations` — each a non-empty string
      - A file missing one section raises a clear parse error identifying the absent section
      - Section content does not include the section header line itself
      - An empty file raises a clear parse error

- [ ] T008 [P] [US5] Write `tests/unit/test_aggregator.py` — unit tests for
      `scorecard/aggregator.py`:
      - Correctness pass rate computed correctly from a known set of records
        (Python: from `pytest_pass`; SQL: from `checksum_match` AND `row_count_match`
        AND `snapshot_pass` all true)
      - Mean formatting violations (from `formatting_violations` field) computed
        correctly (two decimal precision)
      - Mean runtime (`runtime_ms`) and mean peak memory (`peak_memory_bytes`,
        Python records only) computed correctly from pre-populated fixture records
      - Mean token usage (`token_usage_input` and `token_usage_output`) computed
        correctly
      - Variant pass rate computed correctly per variant name (five canonical
        variant values)
      - Failure category counts (correctness failure, variant mismatch, edge-case
        failure) computed correctly
      - Empty record list returns zero/empty aggregates without error
      - Excluded fields (`generation_time_ms`, `flake8_violation_count`,
        `sqlfluff_violation_count`, `correctness_pass`, `correctness_detail`) are
        not referenced anywhere in the aggregator output — verify their absence

- [ ] T009 [P] [US5] Write `tests/unit/test_baseline_delta.py` — unit tests for
      `scorecard/baseline_delta.py`:
      - Baseline is identified as `model_token = "model_c"` (ChatGPT 5.2 Codex)
      - Delta is computed as `evaluated_model_metric − baseline_metric` for each
        numeric metric (`runtime_ms`, `peak_memory_bytes`, `token_usage_input`,
        `token_usage_output`)
      - Epsilon tolerance is read from `references/deterministic-rules.md` — test
        verifies the value is NOT hardcoded in the module
      - Positive delta (evaluated model is higher than baseline) is represented
        correctly
      - Negative delta (evaluated model is lower than baseline) is represented
        correctly
      - Missing baseline record raises a clear error identifying the missing model
      - `generation_time_ms` is not a valid metric — verify it is not referenced

- [ ] T010 [P] [US5] Write `tests/unit/test_json_emitter.py` — unit tests for
      `scorecard/json_emitter.py`:
      - Output file is written to the path specified by `--outdir`
      - Output contains one record per model × task × variant
      - Every record contains all required fields per `file-schema.md` §4:
        `task_id`, `model_token`, `filename`, `dataset_variant`, `category`,
        `contracted`, `correctness_score`, `pytest_pass` (Python) or
        `checksum_match` + `row_count_match` + `snapshot_pass` (SQL), `runtime_ms`,
        `peak_memory_bytes` (Python only), `token_usage_input`, `token_usage_output`,
        `formatting_violations`, `variant_mismatch`, `critic_review_path`
      - Excluded fields (`generation_time_ms`, `flake8_violation_count`,
        `sqlfluff_violation_count`, `correctness_pass`, `correctness_detail`) are
        NOT present on any record — verify their absence
      - Per-language null patterns correctly preserved (e.g.,
        `peak_memory_bytes` null for SQL records; `checksum_match` null for Python)
      - File is valid JSON (parseable by `json.loads`)
      - `contracted` flag is present on every record and matches source `result.json`

- [ ] T011 [P] [US5] Write `tests/unit/test_markdown_emitter.py` — unit tests for
      `scorecard/markdown_emitter.py`:
      - Output file is written to the path specified by `--outdir`
      - Report contains per-model sections: correctness pass rate, mean
        `formatting_violations`, mean `runtime_ms`, mean `peak_memory_bytes` (Python
        models only), mean token usage
      - Report does NOT contain a generation time section — verify its absence
      - Report does NOT reference excluded field names (`flake8_violation_count`,
        `sqlfluff_violation_count`, `correctness_pass`, `correctness_detail`)
      - Report contains variant pass rate section (five canonical variant values)
      - Report contains baseline delta section (baseline = model_c / ChatGPT 5.2 Codex)
      - Report contains failure category breakdown section
      - Report contains Critic review summary section
      - Contracted-only report contains a label clearly identifying it as the
        client deliverable
      - Full report does NOT carry the contracted-only label

- [ ] T012 [P] [US5] Write `tests/integration/test_scorecard_pipeline.py` — end-to-end
      integration test:
      - Run the full pipeline from `run_scorecard.py` CLI using fixture artifacts in
        `tests/fixtures/`; verify both `scorecard.json` and `scorecard.md` are
        produced in `--outdir`
      - Verify `scorecard.json` passes JSON schema validation (all required fields
        present per `file-schema.md` §4; excluded fields absent)
      - Verify `scorecard.md` contains all required sections (no generation time
        section)
      - Run with `--contracted-only` flag; verify output covers only contracted task
        IDs; verify report is labelled as client deliverable
      - Run without `--contracted-only` flag; verify output covers full fixture set;
        verify report is NOT labelled as contracted-only

---

### Implementation for User Story 5

- [ ] T013 [P] [US5] Implement `scorecard/critic_parser.py`:

      Responsibilities:
      - Accept a path to a `critic_review.md` file
      - Parse the known four-section structure deterministically using string/line
        matching on section headers (`## Strengths`, `## Failures`,
        `## Mitigation Strategies`, `## Observations`) — no regex, no LLM invocation
      - Return a dict with keys `strengths`, `failures`, `mitigation_strategies`,
        `observations`; each value is the full text content of that section (header
        line excluded)
      - Raise a clear parse error if any section is absent, identifying the missing
        section by name

      Input: path to `critic_review.md`
      Output: dict with four string fields

- [ ] T014 [P] [US5] Implement `scorecard/aggregator.py`:

      Responsibilities:
      - Accept the list of run records produced by `collector.py`
      - Compute per-model aggregates using `statistics.mean` (stdlib):
        correctness pass rate, mean `formatting_violations`, mean `runtime_ms`,
        mean `peak_memory_bytes` (Python records only — skip SQL records where
        this field is null), mean `token_usage_input`, mean `token_usage_output`
      - Correctness pass rate derivation:
        - For Python records: `pytest_pass == true` is a pass
        - For SQL records: `checksum_match AND row_count_match AND snapshot_pass`
          all true is a pass
      - Excluded fields (`generation_time_ms`, `flake8_violation_count`,
        `sqlfluff_violation_count`, `correctness_pass`, `correctness_detail`)
        are not referenced — do not include them in any aggregate
      - Compute variant pass rate per dataset variant name
      - Compute failure category counts: correctness failure, variant mismatch,
        edge-case failure (as defined in `references/rubric.md`)
      - Return a structured dict of aggregate results keyed by model
      - Return zero / empty aggregates (not an error) for an empty record list

      Input: list of run record dicts
      Output: dict of per-model aggregate results

- [ ] T015 [P] [US5] Implement `scorecard/baseline_delta.py`:

      Responsibilities:
      - Accept the per-model aggregates dict produced by `aggregator.py`
      - Identify the baseline model record by `model_token = "model_c"`
        (ChatGPT 5.2 Codex)
      - For each evaluated model (`model_a`, `model_b`) and each numeric metric
        (`runtime_ms`, `peak_memory_bytes`, `token_usage_input`,
        `token_usage_output`), compute
        `delta = evaluated_model_metric − baseline_metric`
      - Excluded fields (`generation_time_ms`, `flake8_violation_count`,
        `sqlfluff_violation_count`) — no delta is computed for any of them;
        they do not appear in the output
      - Read epsilon tolerance from `references/deterministic-rules.md` before
        any float comparison — never hardcode the epsilon value in this module
        (per Constitution Check #16)
      - Return a dict of per-model, per-metric deltas
      - Raise a clear error if the baseline model record is absent

      Input: per-model aggregates dict
      Output: dict of per-model delta values

- [ ] T016 [US5] Implement `scorecard/json_emitter.py` (depends on T004, T013):

      Responsibilities:
      - Accept the list of run records from `collector.py` and the parsed Critic
        review dict from `critic_parser.py` (keyed by `task_id/model/category`)
      - Produce one output record per model × task × variant; each record contains
        the full field set defined in `references/file-schema.md` §4:
        `task_id`, `model_token`, `filename`, `dataset_variant`, `category`,
        `contracted`, `correctness_score`, `pytest_pass` (Python only),
        `checksum_match` + `row_count_match` + `snapshot_pass` (SQL only),
        `runtime_ms`, `peak_memory_bytes` (Python only), `token_usage_input`,
        `token_usage_output`, `formatting_violations`, `variant_mismatch`,
        `critic_review_path`
      - Excluded fields (`generation_time_ms`, `flake8_violation_count`,
        `sqlfluff_violation_count`, `correctness_pass`, `correctness_detail`) are
        NOT added to any record — do not include them
      - Preserve per-language null patterns correctly
      - Write output to `<outdir>/scorecard.json`
      - Re-associate model identifiers (`model_token` → real model name) only after
        all numeric fields are populated (per Constitution Principle 2 / Check #5).
        Real-name lookup comes from `model_token_lookup.csv` held outside the zip;
        if not provided, the scorecard retains `model_token` values.

      Input: list of run records, Critic review dict, `--outdir` path
      Output: `<outdir>/scorecard.json`

- [ ] T017 [US5] Implement `scorecard/markdown_emitter.py` (depends on T014, T015):

      Responsibilities:
      - Accept the per-model aggregates dict, the per-model delta dict, and the
        parsed Critic review summaries
      - Render a human-readable `scorecard.md` with sections (in the order defined
        in `data-model.md`):
        1. Per-model correctness pass rate
        2. Per-model mean formatting violations
        3. Per-model mean runtime and mean peak memory (peak memory reported for
           Python models only)
        4. Per-model mean token usage (input and output)
        5. Variant pass rates (five canonical variants)
        6. Performance delta vs. ChatGPT 5.2 Codex baseline (model_c)
        7. Failure category breakdown (correctness failure, variant mismatch,
           edge-case failure)
        8. Condensed Critic review summaries per model (extracted by
           `critic_parser.py` — no LLM summarisation)
        9. Suggested mitigations (extracted from `mitigation_strategies` section
           of each Critic review)
      - Note: generation time is not reported — it is not captured in V1 (A2).
        Excluded field names (`flake8_violation_count`, `sqlfluff_violation_count`,
        `correctness_pass`, `correctness_detail`) must not appear in the rendered
        report — use the unified names (`formatting_violations`, `pytest_pass`,
        etc.)
      - Report title MUST reflect any applied filter flags (e.g., append
        `[Engine: sql]` or `[Model: model_a]` to the title when those flags are
        set)
      - When `--contracted-only` is set, the report title and a prominent header
        line MUST clearly label the output as the client deliverable (Banking
        Institution contracted scope — 40 tasks)
      - Write output to `<outdir>/scorecard.md`

      Input: aggregates dict, delta dict, Critic summary dict, filter flags,
      `--outdir` path
      Output: `<outdir>/scorecard.md`

- [ ] T018 [US5] Implement `run_scorecard.py` — CLI entry point (depends on T004,
      T013, T014, T015, T016, T017):

      Responsibilities:
      - Parse CLI arguments using `argparse` (stdlib):
        - `--outdir` (required): path to write scorecard outputs
        - `--engine` (optional): `sql` | `python` | `all` (default: `all`)
        - `--dataset-variant` (optional): filter to a specific variant name
        - `--model` (optional): filter to a specific model token
        - `--contracted-only` (optional flag): produce contracted-scope scorecard
      - Orchestrate the full pipeline in order:
        1. Call `collector.collect()` with all filter arguments → run records
        2. Call `critic_parser.parse()` for each unique `critic_review_path`
           in the run records → Critic review dict
        3. Call `aggregator.aggregate()` on the run records → aggregates dict
        4. Call `baseline_delta.compute()` on the aggregates dict → delta dict
        5. Call `json_emitter.emit()` → write `<outdir>/scorecard.json`
        6. Call `markdown_emitter.emit()` → write `<outdir>/scorecard.md`
      - Print a completion message to stdout listing the two output paths
      - No manual intervention required beyond invocation (per FR-012)
      - Invocable via `python run_scorecard.py --outdir <path>`

      Input: CLI arguments
      Output: `<outdir>/scorecard.json`, `<outdir>/scorecard.md`; exit code 0
      on success, non-zero on any pipeline error

**Checkpoint**: All Phase 3 modules are implemented and all unit tests pass.
`python run_scorecard.py --outdir ./out` runs end-to-end from fixture artifacts
and produces both output files in both full and contracted-only modes.

---

## Phase 4: Polish and Cross-Cutting Concerns

**Purpose**: Documentation, quickstart validation, and verification that all FR-012
and FR-013 acceptance scenarios pass.

- [ ] T019 [P] [US5] Add docstrings to all six modules (`collector.py`,
      `critic_parser.py`, `aggregator.py`, `baseline_delta.py`, `json_emitter.py`,
      `markdown_emitter.py`) and to `run_scorecard.py` — each docstring must be
      understandable to a non-developer stakeholder (per Constitution Principle 3):
      describe what the module does, what it reads, and what it writes, in plain
      language

- [ ] T020 [P] [US5] Validate `run_scorecard.py --help` output covers all flags
      defined in FR-013: `--outdir`, `--engine`, `--dataset-variant`, `--model`,
      `--contracted-only`. Confirm help text is plain-language and matches flag
      descriptions in `feature5_plan.md`.

- [ ] T021 [US5] Run the quickstart validation per `specs/005-comparative-scorecard/
      quickstart.md` (Phase 1 deliverable): invoke `scorecard --outdir ./out` against
      the full fixture set, verify both output files are produced, spot-check that
      real model names are NOT present in any metric field before the
      re-association step in `json_emitter.py` (re-association only in
      the final output, per Constitution Principle 2), confirm no hardcoded
      epsilon values appear in `baseline_delta.py` or elsewhere in the scorecard
      package, and confirm excluded fields (`generation_time_ms`,
      `flake8_violation_count`, `sqlfluff_violation_count`, `correctness_pass`,
      `correctness_detail`) do not appear anywhere in either output file.

---

## Dependencies and Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — **blocks all Phase 3 work**
- **User Story 5 (Phase 3)**: Depends on Phase 2 (`collector.py` complete)
  - Tests T007–T012 can all be written in parallel (they will fail until their
    target module is implemented)
  - Implementation tasks T013–T015 can run in parallel (different files, no
    inter-dependency)
  - T016 depends on T004 (collector) and T013 (critic_parser)
  - T017 depends on T014 (aggregator) and T015 (baseline_delta)
  - T018 depends on T004, T013, T014, T015, T016, T017 — implement last
- **Polish (Phase 4)**: Depends on all Phase 3 implementation tasks complete

### Within Phase 3

- **Write tests first** — T007–T012 must exist and fail before the module they
  cover is implemented
- `critic_parser.py`, `aggregator.py`, `baseline_delta.py` (T013–T015) are
  independently implementable after Phase 2 is complete
- `json_emitter.py` (T016) requires `collector.py` (T004) and `critic_parser.py`
  (T013)
- `markdown_emitter.py` (T017) requires `aggregator.py` (T014) and
  `baseline_delta.py` (T015)
- `run_scorecard.py` (T018) requires all six modules to be complete

---

## Parallel Opportunities

```bash
# Phase 1 — all tasks parallel:
Task T001: scorecard/__init__.py + run_scorecard.py scaffold
Task T002: tests/fixtures/sample_result.json
Task T003: tests/fixtures/sample_critic_review.md

# Phase 2 — T004, T005, and T006 can all start together:
Task T004: collector.py core logic
Task T005: collector.py contracted-only filtering + task_bank.csv cross-validation
Task T006: test_collector.py (will fail until T004/T005 complete)

# Phase 3 — once Phase 2 is complete, all test tasks parallel:
Task T007: test_critic_parser.py
Task T008: test_aggregator.py
Task T009: test_baseline_delta.py
Task T010: test_json_emitter.py
Task T011: test_markdown_emitter.py
Task T012: test_scorecard_pipeline.py

# Phase 3 — implementation tasks T013–T015 parallel:
Task T013: critic_parser.py
Task T014: aggregator.py
Task T015: baseline_delta.py

# T016 and T017 follow after their deps; T018 last.
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 (Setup)
2. Complete Phase 2 (Foundational — collector core and contracted-only logic)
3. Write and fail tests T007–T012
4. Implement T013–T015 in parallel
5. Implement T016, then T017, then T018
6. **STOP and VALIDATE**: run end-to-end integration test in both full and
   contracted-only modes against fixtures
7. Complete Phase 4 (Polish)

---

## Notes

- `[P]` tasks = different files, no dependencies — safe to run in parallel
- Under A3, model anonymization is **structural** throughout Features 1–4 —
  `model_token` values (`model_a`, `model_b`, `model_c`) flow through `result.json`
  and into Feature 5. Re-association to real model names (Claude Sonnet 4.5,
  Gemini 2.5 Flash, ChatGPT 5.2 Codex) occurs in `json_emitter.py` only, after all
  numeric fields are populated — never earlier (Constitution Principle 2)
- Epsilon tolerance for float comparisons is read from
  `references/deterministic-rules.md` inside `baseline_delta.py` — never hardcoded
  (Constitution Check #16)
- No LLM invocation anywhere in F5 — `critic_parser.py` uses deterministic text
  parsing only
- Excluded fields per A2 and A3 (`generation_time_ms`, `flake8_violation_count`,
  `sqlfluff_violation_count`, `correctness_pass`, `correctness_detail`) must not
  appear in any fixture, any module output, or either scorecard file. Any occurrence
  is a bug.
- Client is referred to as "Banking Institution" in all generated output — never by
  actual name (Constitution Security)
- Scoring weights and thresholds remain deferred to post-V1 [TBD] — the scorecard
  emits raw scores and deltas only; no model is declared a winner
- Commit after each completed task or logical group; verify tests pass before moving
  to the next phase
