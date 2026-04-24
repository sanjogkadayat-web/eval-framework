---
description: "Task list for Feature 2 — SQL Critic Review"
---

# Tasks: Feature 2 — SQL Critic Review

**Input**: Design documents from `specs/002-sql-critic-eval/`
**Prerequisites**: `feature2_plan.md` (required), `spec.md` (required for user stories), `constitution.md` (required for all guardrails), Feature 1 complete and passing (required — Feature 2 extends `sql-skill/` in place and depends on `anonymizer.py`, `artifact_store.py`, and `eval_task.py` from F1)

**Tests**: Harness self-tests are included. Critic invocation is mocked at unit test level — LLM calls are never tested directly. The integration test verifies end-to-end artifact persistence using a mocked Critic response.

**Organization**: Feature 2 has one user story (US2 — SQL Qualitative Evaluation, Priority P1). It is co-equal with US1 — the four-dimension rubric is incomplete without it. All tasks extend `sql-skill/` in place; no new top-level directories are created.

**Architecture**: Amendments A1, A2, and A3 are all ratified. Under A3, the Critic reads the anonymized `.sql` code file directly from `assets/tasks/[task_id]/task{N}{a|b|c}.sql` — there is no intermediate per-task `answers.csv` extraction step. The formatting violation count is the `formatting_violations` field in `eval_results.csv`, pre-read by Feature 1 into `result.json`.

> 📝 **Re-check gate**: Constitution Check item 7 requires manual verification that `sql_critic_persona.md` contains no model identifiers once authored (T031). This check must be completed before T034 (`critic_runner.py`) is marked done.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US2)
- Task IDs continue from Feature 1 (T030+) to support cross-feature traceability
- Paths follow the single-project CLI skill structure defined in the Feature 2 plan

---

## Phase 1: Setup

**Purpose**: One new asset directory and persona template stub. No new top-level directories — Feature 2 extends `sql-skill/` in place.

- [ ] T030 Create `sql-skill/assets/personas/` directory and add `sql_critic_persona.md` stub — file must exist before `critic_runner.py` is implemented; stub may contain section headers only (strengths, failures, mitigation strategies, observations) with placeholder content

**Checkpoint**: `sql-skill/assets/personas/sql_critic_persona.md` exists. Directory structure matches Feature 2 plan.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The Critic persona template must be fully authored and verified clean of model identifiers before `critic_runner.py` is implemented. This is the only foundational gate for Feature 2 — all `references/` documents were completed in Feature 1.

**⚠️ CRITICAL**: `critic_runner.py` must not be implemented until T031 is complete and the re-check in item 7 of the Constitution Check passes.

- [ ] T031 Author `sql-skill/assets/personas/sql_critic_persona.md` — manually authored; enforces four-section output structure (strengths, failures, mitigation strategies, observations); instructs Critic to produce no numeric score; instructs Critic to produce no model identifier in any section; written in plain language per constitution Principle 3; self-contained within `sql-skill/` — independent from `python-skill/assets/personas/`. **After authoring: perform explicit line-by-line check for the strings "Claude", "Gemini", "ChatGPT", "Sonnet", "Flash", "Codex", and any other model name variant — document the result of this check before proceeding to T034.**

**Checkpoint**: `sql_critic_persona.md` is fully authored, reviewed, and confirmed clean of model identifiers. Constitution Check item 7 re-check is documented and passing.

---

## Phase 3: User Story 2 — SQL Qualitative Evaluation (Priority: P1) 🎯

**Goal**: At the end of every `eval-task --engine sql` invocation, the SQL Critic persona is automatically invoked on the anonymized `.sql` code file, returns structured four-section commentary with no numeric score and no model identifier, and the output is persisted as `critic_review.md` keyed by `task_id/model/category`. The Critic review is also invocable independently via `eval-qualitative --engine sql`.

**Independent Test**: Run `eval-qualitative --engine sql --task-id SQL-001` against fixture data with a mocked Critic response. Verify: (1) the anonymized `.sql` file (e.g., `assets/tasks/SQL-001/task1a.sql`) is passed to the Critic — only the filename letter reveals the model, no real name; (2) the Critic output contains all four sections (strengths, failures, mitigation strategies, observations); (3) no numeric score appears anywhere in the output; (4) `critic_review.md` is written to `outputs/SQL-001/[model]/[category]/critic_review.md`; (5) `result.json` for the same run has `critic_review_path` populated. Run `eval-task --engine sql --task-id SQL-001` end-to-end and verify the Critic is invoked automatically as a subprocess without requiring a separate manual call.

### Harness Self-Tests for User Story 2 ⚠️

> **Write these tests FIRST. Ensure they FAIL before writing the implementation.**

- [ ] T032 [P] [US2] Write unit test `tests/unit/test_critic_runner.py` — mock the Critic LLM invocation; verify `critic_runner.py` passes the anonymized `.sql` file (identified only by its filename letter `a`/`b`/`c`) to the Critic — no real model identifier is ever constructed or passed; verify the returned output is parsed and contains all four sections (strengths, failures, mitigation strategies, observations); verify a missing section raises a clear validation error; verify no numeric score pattern (e.g., digits followed by `/` or `%`) appears in parsed output; verify output is written as `.md` to the correct artifact path.

- [ ] T033 [P] [US2] Write integration test `tests/integration/test_eval_qualitative_pipeline.py` — using fixture `task_bank.csv`, `.sql` code files under `assets/tasks/`, and a mocked Critic response, run the full `eval-qualitative --engine sql --task-id SQL-001` pipeline end-to-end; verify `critic_review.md` is written to `outputs/SQL-001/[model]/[category]/`; verify `result.json` at the same path has `critic_review_path` populated; verify the pipeline completes without error for all three filename letters (`a`, `b`, `c`).

- [ ] T033b [US2] Update integration test `tests/integration/test_eval_task_pipeline.py` (from Feature 1) — extend the existing end-to-end test to verify that `eval-task --engine sql --task-id SQL-001` now invokes `eval_qualitative.py` as a subprocess and that `critic_review.md` is produced alongside `result.json` (depends on T032 stub existing).

### Implementation for User Story 2

- [ ] T034 [US2] Implement `sql-skill/scripts/critic_runner.py` — invokes the SQL Critic persona from `sql-skill/assets/personas/sql_critic_persona.md` within the Claude Agent Skill execution context (no external API call); reads the anonymized `.sql` code file from `assets/tasks/[task_id]/task{N}{letter}.sql` (resolved via `task_bank.csv` — no hardcoded paths); passes the file content to the Critic with no added model identifier; parses the returned output into four sections (strengths, failures, mitigation strategies, observations); validates that no numeric score is present and that all four sections exist; writes output to `outputs/[task_id]/[model]/[category]/critic_review.md`. Must not be implemented until T031 persona re-check is documented and passing. Must pass T032 tests.

- [ ] T035 [US2] Implement `sql-skill/scripts/eval_qualitative.py` — standalone CLI entry point: `eval-qualitative --engine sql [--task-id SQL-001]`; resolves the three model filenames for a task via `task_bank.csv` (no hardcoded paths per FR-018); invokes `critic_runner.py` for each model's anonymized `.sql` file; persists output via `artifact_store.py`. Supplementary to the minimal CLI defined in FR-013 — `eval-task` and `scorecard` remain the required commands. Must pass T033 integration test.

- [ ] T036 [US2] Extend `sql-skill/scripts/artifact_store.py` (from Feature 1) — add persistence of `critic_review.md` alongside the existing `result.json`; update `result.json` to populate the `critic_review_path` field (was `null` in Feature 1) with the relative path to the Critic review file; keyed by `task_id/model/category` per FR-011. Verify existing Feature 1 unit test `tests/unit/test_artifact_store.py` still passes after extension.

- [ ] T037 [US2] Update `sql-skill/scripts/eval_task.py` (from Feature 1) — add subprocess invocation of `eval_qualitative.py` at the end of every `eval-task --engine sql` run; the two entry points must remain independently testable (subprocess call, not a direct import); verify Feature 1 integration test `test_eval_task_pipeline.py` still passes after the update (it will need the extension from T033b to fully pass). Must pass T033b test.

**Checkpoint**: `eval-task --engine sql --task-id SQL-001` runs end-to-end and produces both `result.json` and `critic_review.md`. `eval-qualitative --engine sql --task-id SQL-001` runs independently and produces the same `critic_review.md`. All unit and integration tests pass. No model identifier appears in any Critic output. All four sections are present in every `critic_review.md`.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Quickstart update, compliance verification, and the mandatory post-authoring re-check for model identifier absence.

- [ ] T038 [P] Update `quickstart.md` for `sql-skill/` (from Feature 1) — add section covering: how the Critic review is triggered automatically, how to invoke `eval-qualitative` independently, how to read `critic_review.md`, what to do if a section is missing from Critic output. Maintain plain language and acronym-on-first-use convention per constitution Principle 3.

- [ ] T039 [P] Verify constitution compliance for all Feature 2 files — confirm: `sql_critic_persona.md` contains no model identifier strings (Claude, Gemini, ChatGPT, Sonnet, Flash, Codex, or any variant); `critic_runner.py` produces no numeric score; `critic_review.md` artifacts are stored under `task_id/model/category`; no database or API framework code introduced; `eval_qualitative.py` resolves all paths via `task_bank.csv` and never hardcodes paths.

- [ ] T040 Regression check — run the full Feature 1 test suite (`tests/unit/test_anonymizer.py`, `test_scorer.py`, `test_schema_validator.py`, `test_merge_results.py`, `test_artifact_store.py`, `tests/integration/test_eval_task_pipeline.py`) after all Feature 2 changes are merged; confirm zero regressions from the `artifact_store.py` extension (T036) and the `eval_task.py` update (T037).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Depends on Feature 1 complete — `sql-skill/` tree must exist
- **Phase 2 (Foundational)**: Depends on Phase 1 — persona stub must exist before it can be authored
- **Phase 3 (User Story 2)**: Tests (T032–T033b) can be written as soon as Phase 2 completes; implementation (T034–T037) follows tests and requires Phase 2 checkpoint to pass
- **Phase 4 (Polish)**: Depends on Phase 3 checkpoint passing

### Within Phase 3

- T032, T033 (unit + new integration tests): Write first. Ensure FAIL.
- T033b (extension to F1 integration test): Can be written in parallel with T032/T033
- T034 (`critic_runner.py`): Depends on T031 (persona re-check documented) and T032 (test exists and fails)
- T035 (`eval_qualitative.py`): Depends on T034
- T036 (`artifact_store.py` extension): No dependency on T034/T035 — can be implemented in parallel
- T037 (`eval_task.py` update): Depends on T035 and T036 both complete

### Parallel Opportunities

T032 and T033 can be written in parallel. T034 and T036 can be implemented in parallel once T032 passes. T038 and T039 (polish) can run in parallel once Phase 3 checkpoint passes.

---

## Parallel Example: Phase 3 Tests

```bash
# Write all tests simultaneously before any implementation:
Task: "Unit test for critic_runner.py in tests/unit/test_critic_runner.py"        # T032
Task: "Integration test for eval_qualitative pipeline"                              # T033
Task: "Extend F1 integration test to verify Critic subprocess invocation"           # T033b
```

---

## Implementation Strategy

### MVP First (User Story 2 Only)

1. Confirm Feature 1 checkpoint is passing (prerequisite)
2. Complete Phase 1: create persona stub
3. Complete Phase 2: author persona fully; perform and document model identifier re-check
4. Write tests (T032, T033, T033b) — ensure they FAIL
5. Implement in dependency order: `critic_runner.py` → `artifact_store.py` extension → `eval_qualitative.py` → `eval_task.py` update
6. **STOP and VALIDATE**: Run end-to-end `eval-task` and `eval-qualitative` against fixture data; confirm both produce `critic_review.md`; run full test suite including F1 regression check
7. Complete Phase 4 polish

### Incremental Delivery

Feature 2 delivers the qualitative half of the four-dimension rubric. Once the Phase 3 checkpoint passes, the combined F1+F2 pipeline produces the complete per-attempt artifact set (`result.json` + `critic_review.md`), which is the input required for Feature 5 (Comparative Scorecard). Feature 3 (Python Quantitative) can proceed in parallel with Feature 2 since they operate on independent skill trees.

---

## Notes

- [P] tasks = different files, no blocking dependencies between them
- [US2] label maps all tasks to User Story 2 — SQL Qualitative Evaluation
- Task IDs begin at T030 to maintain cross-feature traceability with Feature 1 (T001–T029)
- The Critic is the **only** LLM-generated content at harness runtime — all numeric scoring remains deterministic and script-enforced
- Under A3, model anonymization is **structural** — the Critic receives an anonymized code file identified only by its filename letter. There is no separate string-stripping step for the Critic; model identity is never constructed in Feature 2's code path.
- `eval_qualitative.py` is supplementary to FR-013; `eval-task` and `scorecard` remain the required CLI entry points
- `critic_runner.py` must mock the LLM in unit tests — never test LLM calls directly
- The persona template re-check (T031) is a hard gate for T034 — do not skip it
- `sql-skill/` and `python-skill/` are independent trees; the SQL Critic persona must not reference anything from `python-skill/assets/personas/`
- Commit after each task; run the F1 regression suite (T040) before marking Feature 2 complete
