# Sample workflow

This example shows the orchestration loop producing real artifacts. It has two
parts:

1. **A reproducible spec** — `../../orchestrator/examples/spec-greeter.txt`
   (Rust greeter CLI) used with the `bootstrap orchestrate` demo.
2. **A recorded real run** — its `.bootstrap/` artifacts were used as evidence
   while preparing this showcase but are **excluded from this public release**
   (see `../../LICENSING.md`). They are not present in this copy.

## Recorded run

The recorded-run artifacts (`.bootstrap/` JSON envelopes) are **excluded from
this public release**. They are recorded workflow artifacts whose ownership and
applicable rights have not been verified, and no custom reuse grant is made for
them (see `../../LICENSING.md` and `../../LICENSE_PENDING.md`).

The harness's plan-mutation behaviour is still described here for context: a
two-step plan (create `greet.py`, create `test_greet.py`) grew to three
executed steps when the supervising model judged `greet.py` was missing and
inserted a new step (step 101) into the plan. The original spec file for this
run was not preserved; the plan artifacts were the source of truth for what was
asked, but those artifacts are not included in this release.

## Reproducing it

The workflow needs a model reachable by OpenCode. It was **not** re-run while
preparing this showcase (no model requests were made), so it is classified
**NOT VERIFIED in this environment**.

```bash
cd ../../orchestrator
cargo build --release
export PATH="$PWD/target/release:$PATH"
./scripts/demo-orchestrate.sh          # full loop in a temp workspace
# or, for just the planner:
PLAN_ONLY=1 ./scripts/demo-orchestrate.sh
```

Prerequisites: Rust ≥ 1.85 (edition 2024), the `opencode` CLI, and a configured
local model. See `../../orchestrator/docs/usage.md`.

## What is not shown

- No sandbox execution. `bin/autonomous` is the sandboxed entry point; the
  recorded run used the plain orchestrator on the host.
- No claim that the model's self-reported `completed` status was independently
  confirmed. The reviewer evaluated the executor's reported result and the
  remaining plan; it did not independently inspect the repository. The recorded
  artifacts are the harness's own reports and demonstrate plan modification,
  insertion of step 101, execution history, and completion state. They do not
  independently establish that `greet.py` was actually missing, and they do not
  prove that the resulting files existed in the original workspace.
