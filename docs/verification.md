# Verification and failure handling

Verification in this project happens at three levels: the orchestrator's
per-step reviewer, the model-facing `emit` schema gate, and (in the role-based
approach) an independent verifier agent. They are related but separate.

## 1. Per-step reviewer (Rust orchestrator)

After each executor step, a supervising model receives the step, the executor's
raw JSON result and the remaining planned steps, and returns one of:

| Action | Meaning | Effect |
|--------|---------|--------|
| `continue` | step acceptable | advance to the next planned step |
| `insert` | a gap was found | splice `new_steps` after the cursor, then advance |
| `skip` | next step no longer needed | remove the next step, then advance |
| `stop` | human intervention needed | persist state and halt |

Failure handling is deliberately fail-safe:

- An unparseable review becomes a synthesised `stop` — the loop never continues
  on a verdict it could not read.
- A missing executor envelope is recorded as `status: "unknown"` rather than
  silently dropped, so the reviewer can still judge it.
- The reviewer's decision is persisted as `step-NN-review.json` alongside the
  executor's result when the step is fully processed. Persistence is best-effort
  and not crash-safe; see `execution-model.md`.

**Limitation.** The reviewer judges the executor's *reported* result and the
remaining plan; it does not independently re-read the repository. The recorded
run's `completed` statuses are the executor's own claims.

## 2. `emit` — the model-facing schema gate

`bootstrap emit <plan|step|review> --file <path>` validates a JSON envelope
against the same schema the harness parses, rewrites it canonically on success,
and prints a precise, correctable `Error:` on failure. Each role prompt tells the
model to write its envelope to a file, run `emit`, and retry on error.

This makes the hand-off channel retryable but not guaranteed: `emit` returns a
correctable error, and the harness retries a rejected envelope up to three times,
feeding the parser error back into the next prompt. Exhausted retries do not
guarantee recovery; the loop may record an `unknown` result or stop for human
review. `emit` exits non-zero on failure so the model's shell observes the
error.

## 3. Defensive JSON extraction

`orchestrator/src/llm.rs` strips ANSI, prefers the sentinel-delimited span
(`<<<PLAN_JSON>>>`, `<<<STEP_RESULT_JSON>>>`, `<<<REVIEW_JSON>>>`), and otherwise
takes the first brace-balanced object (string-aware, so braces inside strings do
not count). A tolerant parse removes trailing commas before `}`/`]` while
tracking string literals. These are the concrete mechanisms that keep the loop
running on imperfect local-model output.

## 4. Independent verifier (role-based approach)

In the `agents/` configuration, verification is a separate role with its own
permissions:

- The verifier can read and run allowlisted validation commands but cannot edit.
- It must return `STATUS: PASS` or `FAIL` with repository evidence for every
  expected outcome and protected value, plus test/typecheck/lint/build results.
- The orchestrator treats a coder's success claim as a hint, independently reads
  the affected files, and caps verification repairs at two attempts.
- The reviewer runs only after the verifier passes and is limited to one
  remediation pass.

This is the "agent claims are not evidence" rule expressed as an executable
workflow with a repair budget.

## 5. Recorded evidence (excluded from this release)

The recorded-run artifacts (`examples/sample-workflow/recorded-run/*.json`) are
**excluded from this public release**; ownership and applicable rights have not
been verified. The description below is retained for context. The directory
was a real run of the Rust orchestrator:
a two-step plan, an executor `completed` report, a reviewer `continue`, a second
step, a reviewer `insert` (the reviewer judged the executor's reported result and
concluded `greet.py` was missing), the inserted step, and a final `continue`
with `finished: true`. The artifacts demonstrate plan modification, insertion of
step 101, execution history, and completion state. They are a record of the
harness's own reports, not an independent repository verification: they do not
independently establish that `greet.py` was actually missing, and they do not
prove that the resulting files existed in the original workspace.

## Test status

- The Rust crate contains unit tests for JSON extraction/relaxation, envelope
  validation, and path recovery (`src/llm.rs`, `src/emit.rs`,
  `src/orchestrate.rs`). See the validation section of the publication manifest
  for whether they were executed here.
- The sandbox Python components have no test suite in the source repository; they
  were syntax-checked only.
- The recorded run was not re-executed.
