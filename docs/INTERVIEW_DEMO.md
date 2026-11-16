# Interview demonstration: AI agent orchestration showcase

This document describes a **5–7 minute** technical walkthrough of the existing
showcase. It is written for a live or recorded interview and uses only
commands, files, and capabilities that exist in this repository.

The recommended path references recorded evidence, but the recorded-run artifacts
are **excluded from this public release** (see `../LICENSING.md`). Commands
below that read files under `examples/sample-workflow/recorded-run/` will not
run in this copy; the `bootstrap emit` validation steps can be run on equivalent
envelopes you construct. It does not require a model call for the core evidence
and does not claim that any
unverified component was executed.

## Scope and honesty rules

- Treat `examples/sample-workflow/recorded-run/` as **recorded**, not live, and
  **excluded from this public release** (ownership/rights unverified).
- Treat `bin/autonomous` and `sandbox/` as **inspected but not executed**.
- Do not describe Mode A/B/C as sandboxed; only `bin/autonomous` is sandboxed.
- Do not claim the Rust loop has an independent repository verifier.
- Do not claim production readiness, security guarantees, or autonomous
  completion beyond the recorded evidence.

## Prerequisites for the presenter

- A terminal at the repository root (or the equivalent checkout).
- Optional, for the live schema checks:
  - Rust toolchain (`cargo`, `rustc`) and a C linker, **or** the pre-built
    `orchestrator/target/release/bootstrap` binary.
  - Build once with `cd orchestrator && cargo build --release`, then
    `export PATH="$PWD/target/release:$PATH"`.
- No model, Ollama endpoint, or OpenCode agent installation is required for the
  recommended path.

## Recommended demo sequence (6–7 minutes)

### 0:00–0:45 — What the project is

**Presenter does**

- Open `README.md`, then `docs/architecture.md`.
- Point to the status table in `README.md` ("Current development status").

**Interviewer should observe**

- The project is an experimental local orchestration environment, not a
  product claim.
- Two independent approaches: a code-owned Rust loop and config-driven
  OpenCode role delegation.

**Demonstrates**

- `README.md`
- `docs/architecture.md`

**Proves**

- The scope, components, and verification status are stated explicitly.

**Does not prove**

- Implementation quality beyond the documented and recorded evidence.

### 0:45–1:30 — Submitting a task

**Presenter does**

- Show the example spec:

  ```bash
  sed -n '1,80p' orchestrator/examples/spec-greeter.txt
  ```

- Explain the real submission entry point without running it:

  ```bash
  bin/mode-c <project-dir> <spec-file> [bootstrap args...]
  # or, for the sandboxed path:
  bin/autonomous <project-dir> "<task>" [--model <provider/model>] [--agent <name>]
  ```

- Note that `bin/mode-c` stores state outside the repository under
  `runs/<project>/<spec>/` and links it into the project as `.bootstrap`.

**Interviewer should observe**

- A task is plain text plus explicit architectural decisions.
- State is kept outside the target repository and linked in.

**Demonstrates**

- `orchestrator/examples/spec-greeter.txt`
- `bin/mode-c`
- `docs/execution-model.md`

**Proves**

- Task input and state placement are explicit and inspectable.

**Does not prove**

- A live model call or successful autonomous run. The original spec for the
  recorded run was not preserved; `plan.json` is the source of truth for what
  was asked.

### 1:30–2:30 — Planning and task decomposition

**Presenter does**

- Show the recorded plan:

  ```bash
  cat examples/sample-workflow/recorded-run/plan.json
  ```

- Validate it live:

  ```bash
  bootstrap emit plan --file examples/sample-workflow/recorded-run/plan.json
  ```

**Interviewer should observe**

- `design`, `notes`, and an ordered `steps[]` array.
- Each step has `id`, `title`, `instructions`, `context`, and `acceptance`.
- The command prints:

  ```text
  OK: plan envelope valid — 2 step(s)
  ```

**Demonstrates**

- `examples/sample-workflow/recorded-run/plan.json`
- `bootstrap emit plan`

**Proves**

- The plan is structured, machine-readable, and passes the same schema gate the
  harness uses.

**Does not prove**

- Planner quality for arbitrary tasks; this is one recorded exercise.

### 2:30–3:30 — Execution by stage

**Presenter does**

- Show the executor reports:

  ```bash
  cat examples/sample-workflow/recorded-run/step-01-result.json
  cat examples/sample-workflow/recorded-run/step-02-result.json
  ```

- Validate one report:

  ```bash
  bootstrap emit step --file examples/sample-workflow/recorded-run/step-01-result.json
  ```

**Interviewer should observe**

- `status: "completed"`, `summary`, `new_or_changed_files`, `changes`,
  `features`, `bugs`, and `issues`.
- The command prints:

  ```text
  OK: step envelope valid — status=completed
  ```

**Demonstrates**

- `examples/sample-workflow/recorded-run/step-01-result.json`
- `examples/sample-workflow/recorded-run/step-02-result.json`
- `bootstrap emit step`

**Proves**

- Execution reports are structured and schema-validated.

**Does not prove**

- That the reported files or tests actually exist or pass. In this loop the
  reviewer judges the executor's reported result and the remaining plan; there
  is no independent repository verifier inside the Rust loop.

### 3:30–4:30 — Validation and plan mutation

**Presenter does**

- Show the review decisions:

  ```bash
  cat examples/sample-workflow/recorded-run/step-01-review.json
  cat examples/sample-workflow/recorded-run/step-02-review.json
  ```

- Validate the insert decision:

  ```bash
  bootstrap emit review --file examples/sample-workflow/recorded-run/step-02-review.json
  ```

- Show final state:

  ```bash
  python3 -c 'import json;s=json.load(open("examples/sample-workflow/recorded-run/state.json"));print("cursor",s["cursor"],"/",len(s["steps"]));print("executed",s["executed"]);print("finished",s["finished"]);print("stopped_reason",s["stopped_reason"]);print("step ids",[x["id"] for x in s["steps"]])'
  ```

**Interviewer should observe**

- Step 1 review: `continue`.
- Step 2 review: `insert`, with a new step (`id: 101`) spliced into the plan.
- Final state: `cursor 3 / 3`, `executed 3`, `finished true`,
  `stopped_reason null`, step ids `[1, 2, 101]`.
- The command prints:

  ```text
  OK: review envelope valid — action=insert
  ```

**Demonstrates**

- `examples/sample-workflow/recorded-run/step-01-review.json`
- `examples/sample-workflow/recorded-run/step-02-review.json`
- `examples/sample-workflow/recorded-run/state.json`
- `bootstrap emit review`

**Proves**

- The supervising model can mutate the plan mid-run. State is persisted after
  successfully processed steps and when the absolute step cap is reached; this is
  best-effort and not crash-safe, so an interrupted or failed step may run again
  on resume.

**Does not prove**

- That the inserted step was necessary or that its result was independently
  verified. The recorded artifacts do not establish that `greet.py` was actually
  missing, and they do not prove that the resulting files existed in the original
  workspace; the reviewer evaluated the executor's reported result.

### 4:30–5:30 — Failure handling

**Presenter does**

- Create a malformed review envelope and run the schema gate:

  ```bash
  printf '{"reason":"x","new_steps":[]}' > /tmp/opencode/bad-review.json
  bootstrap emit review --file /tmp/opencode/bad-review.json
  ```

- Optionally show the empty-plan case:

  ```bash
  printf '{"design":"x","notes":"","steps":[]}' > /tmp/opencode/bad-plan.json
  bootstrap emit plan --file /tmp/opencode/bad-plan.json
  ```

- Point to the implementation paths in `orchestrator/src/orchestrate.rs`:
  - `execute()` records `status: "unknown"` when no valid envelope is found.
  - `review()` synthesizes a `stop` verdict when the review cannot be parsed.

**Interviewer should observe**

- The malformed review command prints an error and exits non-zero, for example:

  ```text
  Error: review envelope invalid: failed to parse JSON from LLM output (strict error: missing field `action` ...)
  expected shape:
  {"action":"continue|insert|skip|stop","reason":"...","new_steps":[]}
  ```

- The empty plan command prints an error such as:

  ```text
  Error: plan envelope invalid: `steps` is empty — a plan needs at least one step.
  ```

**Demonstrates**

- `bootstrap emit review`
- `bootstrap emit plan`
- `orchestrator/src/orchestrate.rs`
- `orchestrator/src/llm.rs`

**Proves**

- Malformed model output is surfaced as a correctable error, and the loop fails
  safe to `stop` on an unreadable review.

**Does not prove**

- That all model variance is handled. Local models can still cause `unknown`
  results or early stops; the harness degrades rather than claiming success.

### 5:30–6:15 — Permission controls vs. OS isolation

**Presenter does**

- Show the sandbox configuration and one agent definition:

  ```bash
  sed -n '60,110p' sandbox/opencode.json
  sed -n '1,45p' agents/coder.md
  ```

- Read the boundary summary:

  ```bash
  sed -n '1,80p' docs/security-boundaries.md
  ```

**Interviewer should observe**

- Deny-by-default tool permissions: web denied, `execute` denied, `sudo *`
  denied, secret-file patterns denied.
- Agent roles split edit, shell, and delegation permissions.
- The sandbox uses a disposable snapshot, namespaces, and allowlisted proxies.
- Only `bin/autonomous` is sandboxed; Modes A/B/C are host paths.

**Demonstrates**

- `sandbox/opencode.json`
- `agents/coder.md`
- `docs/security-boundaries.md`
- `docs/execution-model.md`

**Proves**

- The project distinguishes orchestration-level permission policy from an
  OS-level boundary design, and documents that the boundary is unverified.

**Does not prove**

- That `bin/autonomous` or the sandbox was executed, or that the boundary
  contains a determined attacker.

### 6:15–6:45 — Provenance and status

**Presenter does**

- Show provenance and publication status:

  ```bash
  sed -n '1,80p' THIRD_PARTY_NOTICES.md
  sed -n '1,60p' PUBLICATION_MANIFEST.md
  ```

**Interviewer should observe**

- Upstream-derived components and their licenses are identified.
- Showcase-specific components carry no reuse license for this release; a custom
  license may be considered in a future release.
- The manifest records verification status for each file.

**Demonstrates**

- `THIRD_PARTY_NOTICES.md`
- `PUBLICATION_MANIFEST.md`
- `LICENSE_PENDING.md`

**Proves**

- Provenance and verification status are documented rather than implied.

**Does not prove**

- That a publication license has been chosen.

## Fallback path

If a local model or provider is unavailable, use the recommended path above:
recorded artifacts plus `bootstrap emit` validation. This avoids model calls
entirely and still demonstrates planning, execution reporting, review, plan
mutation, state persistence, schema gating, and failure handling.

If the `bootstrap` binary is not available:

1. Skip the `bootstrap emit` commands.
2. Inspect the recorded JSON directly and describe the same schema.
3. If a toolchain is available, build with `cd orchestrator && cargo build --release`
   (a C linker may be required; the original environment used Zig as the linker).
4. Do not run Modes A/B/C or `bin/autonomous` as a fallback; they are not
   verified here and Modes A/B/C are not sandboxed.

## Steps that cannot currently be demonstrated reliably

| Step | Status | Reason |
|------|--------|--------|
| Live end-to-end Rust loop | Optional / prepared only | Requires a model, OpenCode, and the `envelope` agent; not verified in this environment. |
| `bin/autonomous` sandbox run | Unavailable | Inspected but not executed; residual TOCTOU races are documented. |
| Mode A with restricted `light` agent | Prepared only | Requires installing `agents/light.md` into the OpenCode configuration; `bin/mode-a` exits clearly if it is missing. |
| Independent repository verification in the Rust loop | Not implemented | The Rust reviewer judges reported results and the remaining plan. |
| Parallel step execution | Not implemented | The loop is synchronous and single-slot. |
| Distinct planner/executor models | Not implemented | A single `--model` is used. |

## Interview talking points

### Three engineering decisions worth discussing

1. **Code owns orchestration state.** The Rust binary, not the model, owns the
   plan, cursor, history, and mutation. Each LLM call is stateless and receives
   explicit context, which makes runs resumable, inspectable, and bounded by
   `--max-steps` (per invocation) and `MAX_TOTAL_STEPS = 50` (cumulative across resumes).
2. **Schema-gated hand-offs with bounded retries.** `bootstrap emit`
   validates and canonicalizes plan/step/review envelopes and returns precise,
   correctable errors. The harness retries a rejected envelope up to three times,
   feeding the parser error back into the next prompt. Exhausted retries do not
   guarantee recovery; the loop may record an `unknown` result or stop for human
   review. This is retry behaviour, not automatic recovery from arbitrary
   failures.
3. **Fail-safe review and bounded repair.** An unparseable review becomes `stop`;
   a missing executor envelope becomes `status: "unknown"` rather than being
   dropped; verification repairs are capped at two attempts and review
   remediation at one pass.

### Two meaningful trade-offs or limitations

1. **Strict schemas versus local-model variance.** Defensive JSON extraction
   and fail-safe stops reduce end-to-end automation, but they prevent the system
   from silently reporting success on malformed output.
2. **Boundary strength versus portability.** The sandbox is experimental,
   conservative, and host-specific; the host modes remain transitional because
   they run OpenCode directly on the host. Stronger isolation would require
   validating the Bubblewrap path end to end.

### Orchestration-level permission controls vs. OS-level isolation

- **Orchestration-level controls** are OpenCode permissions and role definitions:
  which tools an agent may call, whether it may edit or delegate, and task
  contracts that carry allowed paths and protected values. They are enforced by
  OpenCode configuration and prompt structure, and they govern intent and
  workflow, but they are not a kernel boundary.
- **OS-level isolation** is the `bin/autonomous` Bubblewrap boundary: a
  disposable snapshot, mount and network namespaces, read-only system binds, and
  allowlisted host proxies. It restricts what the process can reach at the
  operating-system level. It applies only to `bin/autonomous`, is documented as
  inspected but not executed here, and is not presented as a general security
  product.

### Upstream-derived vs. showcase engineering work

- **Upstream-derived**
  - `orchestrator/` is derived from `softwarewrighter/local-llm-loop` (MIT,
    Copyright (c) 2026 Michael A. Wright). Its `LICENSE` is preserved; the
    source is functionally unchanged apart from presentation edits such as removed
    private paths and genericised defaults.
  - `agents/orchestrator.md`, `agents/explorer.md`, `agents/planner.md`,
    `agents/researcher.md`, `agents/coder.md`, `agents/verifier.md`, and
    `agents/reviewer.md` are derived from `gmarland/local-coder` (MIT,
    Copyright (c) 2026 local-coder contributors). Only the machine-specific
    model alias changed.
- **Showcase-specific work**
  - `sandbox/`, `bin/`, `docs/`, `examples/`, root-level files, and
    `agents/light.md` are showcase material. They have no root reuse license;
    see `LICENSE_PENDING.md`.
  - The recorded run is real evidence of the harness's own reports, not an
    independent repository verification, and it was not re-executed.
