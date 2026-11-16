# ai-agent-tools (public showcase)

**An experimental local AI coding-agent orchestration and execution environment.**

This repository is a curated, public subset of a private local-agent workspace.
It contains real orchestration code, real agent-role configuration, and the
components of an experimental Bubblewrap execution boundary. It is **not**
production-ready, it does **not** claim complete security isolation, and it does
**not** claim that every mode is sandboxed or that every workflow is fully
autonomous.

Everything here was built to run against **local** models through
[OpenCode](https://opencode.ai) and a local Ollama endpoint. No cloud provider is
required.

## What problem it solves

Pointing a coding agent at a local LLM is easy; making the result dependable is
not. A single long generation drifts, cannot be inspected, and gives the operator
no control points. This project decomposes work into a plan, executes one step at
a time, and has a supervising model review each step — continuing, inserting new
steps, skipping, or stopping for a human. It also wraps the agent in a sandbox so
that autonomous execution does not write directly to the host project.

## Why it is more than a collection of prompts

- A Rust orchestrator owns the plan, the step cursor and the history, and
  persists the plan and state to disk at defined checkpoints
  (`plan.json`, `step-NN-result.json`, `step-NN-review.json`,
  `state.json`), including after successfully processed steps and when the
  absolute step cap is reached. A run can be resumed from those checkpoints;
  this is not crash-safe, and an in-flight or failed transition may not be
  persisted, so an interrupted step may run again after resume.
- The agent's structured hand-offs are validated by a CLI helper (`bootstrap
  emit`) that validates and canonicalizes structured envelopes and returns
  correctable errors; the harness retries a rejected envelope up to three
  times. This improves reliability but does not guarantee recovery.
- Tool access is restricted by configuration and by an execution boundary, not
  only by prompt wording.
- A recorded real run shows the reviewer inserting a missing step into the plan.
- Verification is an explicit, budgeted workflow with fail-safe behaviour (an
  unparseable review stops the loop).

## Key engineering decisions

- **State is owned by code, not by the model.** The Rust loop owns the plan, step
  cursor and history, and persists the plan and state at defined checkpoints
  (`plan.json`, `step-NN-result.json`, `step-NN-review.json`, `state.json`),
  including after successfully processed steps and when the absolute step cap
  is reached. Each LLM call is stateless and receives explicit context, so a run
  is resumable from saved state (best-effort; see recovery limitations below)
  and auditable.
- **Hand-offs are schema-gated.** `bootstrap emit` validates plan/step/review
  envelopes, rewrites them canonically, and returns precise, correctable errors;
  the harness retries a rejected envelope up to three times, feeding the error
  back into the next prompt.
- **Review is a small, fail-safe vocabulary.** The reviewer returns
  `continue` / `insert` / `skip` / `stop`; an unparseable verdict becomes
  `stop` rather than allowing the loop to continue on an unreadable decision.
- **Verification is role-separated and budgeted.** In the agent configuration a
  coder's `STATUS: SUCCESS` is only a hint; the verifier independently checks
  expected outcomes and protected values, and repair attempts are capped (two
  verification repairs, one review remediation).
- **Tool access is enforced by configuration and, for the autonomous path, by an
  execution boundary** (snapshot, namespaces, allowlisted proxies) rather than by
  prompt wording alone.

## Orchestration architecture

Two independent approaches are included:

1. **Code-owned loop** (`orchestrator/`): a model-agnostic Rust harness that
   turns a spec into a plan, then iterates `execute → review`. Rust owns all
   state; each role is a stateless `opencode run` call with the needed context in
   the prompt.
2. **Config-driven role delegation** (`agents/`): seven OpenCode agent
   definitions with role-scoped permissions. The orchestrator classifies a change
   and delegates through explorer → planner → coder → verifier → reviewer.

See [docs/architecture.md](docs/architecture.md).

## Specialized agent roles

`agents/` defines an orchestrator plus six specialists: explorer, planner,
researcher, coder, verifier and reviewer. Only the coder can edit; the verifier
can read and run allowlisted validation commands; the orchestrator can delegate
but not edit or run shell commands. Four adaptive workflows (trivial, standard,
complex, domain) select the least costly path. For each change the orchestrator
is instructed to create a versioned JSON **task contract** (allowed paths,
protected values, expected/forbidden outcomes, validation commands) and repeat it
unchanged in every coder and verifier call, so acceptance criteria stay attached
to the work instead of being recompressed into prose. See
[docs/agent-roles.md](docs/agent-roles.md).

## Execution lifecycle

```
spec → plan → [execute step → review] × N → done / stop for human
```

Step artifacts and state are persisted after each successfully processed step.
An execution or review failure before the next successful state save can cause
that step to be executed again on resume. Reaching the absolute cap of 50 total
steps marks `state.json` as finished and persists that terminal state.
`--max-steps` caps a single invocation and `--resume` continues from saved
state. See
[docs/execution-model.md](docs/execution-model.md).

## Autonomous execution

`bin/autonomous <project> "<task>"` is the sandboxed autonomous entry point. It
snapshots the project, starts allowlisted Ollama and git proxies, runs OpenCode
with `--auto` inside Bubblewrap, and exports the working tree back. `bin/mode-a`,
`bin/mode-b` and `bin/mode-c` are **transitional host-execution paths** and are
not sandboxed; mode C drives the Rust orchestrator. See
[docs/execution-model.md](docs/execution-model.md).

## Tool access and isolation architecture

- The sandboxed autonomous path uses deny-by-default OpenCode permissions: web
  tools denied, `execute` denied, `sudo *` denied,
  `*.env`/`.ssh`/`.pem`/`.key` denied. Mode A's `light` agent is a host-path
  denylist, not a deny-by-default boundary; under `--auto` its `ask` rules are
  auto-approved and permission patterns are text-based.
- The sandbox binds a disposable snapshot at `/workspace`, a per-run state dir,
  a read-only system, and a git client shim with no real git inside.
- Network is removed (`--unshare-all`); the only path is an allowlisted Ollama
  proxy.
- Host proxies validate requests (HTTP endpoint allowlist; git subcommand and
  option allowlist) and run against the snapshot.

See [docs/security-boundaries.md](docs/security-boundaries.md).

## Verification and recovery

- Per-step reviewer: `continue` / `insert` / `skip` / `stop`, with an
  unparseable verdict failing safe to `stop`.
- `bootstrap emit`: the model-facing schema gate that makes malformed envelopes
  self-correcting.
- Defensive JSON extraction and trailing-comma relaxation for imperfect
  local-model output.
- Role-based independent verifier with a two-repair budget and a one-pass review
  remediation.
- Snapshot export is conflict-safe and never deletes host files silently.

See [docs/verification.md](docs/verification.md).

## Model configuration

All model references in this showcase are examples, not requirements:

- `agents/*.md` use `ollama/gpt-oss:20b` as a documented example.
- `bin/mode-a` defaults to `ollama/granite4:3b` (`MODE_A_MODEL`).
- `bin/mode-b`, `bin/mode-c` default to `ollama/gpt-oss:20b`
  (`MODE_B_MODEL`, `MODE_C_MODEL`).
- `bin/autonomous` defaults to `ollama/gpt-oss:20b` (`DEFAULT_MODEL` /
  `--model`).
- `sandbox/opencode.json` lists `ollama` models with example context limits.

Override mechanisms are preserved: `MODE_A_MODEL`, `MODE_B_MODEL`,
`MODE_C_MODEL`, `--model`, `DEFAULT_MODEL`, and `MODE_A_AGENT` /
`OPENCODE_AGENT` for agent selection. To use a different model, confirm it is
available in your own OpenCode/Ollama setup (`ollama list`, `opencode models`)
and replace the example value. Context limits in `sandbox/opencode.json` are
examples and are not asserted to be correct for every model. Local Ollama is the
intended and documented example backend, not a universal requirement, and no
model listed here is claimed to have been tested in this environment beyond the
recorded run.

## Third-party and provenance

- `orchestrator/` is derived from `softwarewrighter/local-llm-loop` (MIT,
  Copyright (c) 2026 Michael A. Wright). Its `LICENSE` is preserved
  byte-for-byte; upstream authorship is not replaced.
- `agents/*.md` prompt bodies (seven files) are derived from
  `gmarland/local-coder` (MIT, Copyright (c) 2026 local-coder contributors).
  They are not presented as original work by the showcase owner.
- `sandbox/`, `bin/`, `docs/`, `examples/`, and root-level showcase files have
  no reuse license pending owner confirmation of rights. See `LICENSING.md`,
  `LICENSE_PENDING.md`, and `THIRD_PARTY_NOTICES.md`.
- Recorded workflow artifacts (`examples/sample-workflow/recorded-run/*.json`)
  are excluded from all redistributed copies until ownership and applicable
  rights are verified.

## Current limitations

- **Experimental.** The sandbox was inspected, not executed, while preparing
  this showcase. It is not a verified security guarantee.
- **Mode A/B/C are not sandboxed.** Only `bin/autonomous` is the sandboxed path.
- **The Rust loop's reviewer does not independently re-read the repository.** It
  judges the executor's reported result and the remaining plan.
- **Local models vary.** Malformed JSON, missing envelopes and tool-use failures
  are expected failure modes; the harness degrades rather than claiming success.
- **Recovery is best-effort, not crash-safe.** State is written after a step is
  fully processed (execution plus review) and when the absolute cap is reached.
  A failure or interruption before the next successful save means the step may be
  executed again on resume; there is no exactly-once execution, rollback, or
  deterministic LLM output guarantee.
- **Environment-specific defaults.** Toolchain layout, the conservative `/home`
  project deny list, and example model names are inherited from the original host
  and must be adapted. See "Model configuration".
- **No operative license has been published for the showcase as a whole.** A
  licensing policy has been approved in principle (see
  [LICENSING.md](LICENSING.md) and [LICENSE_PENDING.md](LICENSE_PENDING.md)),
  but it is not yet implemented as license text, and recorded workflow
  artifacts are excluded from redistribution.

## Installation prerequisites

- Rust ≥ 1.85 (edition 2024) via [rustup](https://rustup.rs/).
- The `opencode` CLI on `PATH`.
- A model reachable by OpenCode (a local Ollama endpoint is the intended target).
- For the sandbox: `bwrap`, `socat`, `python3`, an OpenCode binary, and a
  toolchain directory with an npm CLI. None of these are bundled.

## Running an included example

The Rust greeter demo is the reproducible example:

```bash
cd orchestrator
cargo build --release
export PATH="$PWD/target/release:$PATH"
PLAN_ONLY=1 ./scripts/demo-orchestrate.sh   # one planner call
./scripts/demo-orchestrate.sh               # full loop in a temp workspace
```

This makes real model requests and was **not** run while preparing this showcase
(no model requests were made). It is therefore classified **NOT VERIFIED in this
environment**. A real recorded run, including a reviewer `insert`, was used as evidence while
preparing this showcase, but its artifacts are excluded from this release (see
[LICENSING.md](LICENSING.md)). The greeter demo above is the reproducible
example.

## Current development status

| Capability | Status |
|------------|--------|
| Rust plan → execute → review loop | implemented; unit tests present; recorded run used as evidence (artifacts excluded from this release) |
| `emit` schema helper + bounded retries | implemented |
| Resumable state, plan insert/skip/stop | implemented |
| Seven role definitions + permissions | implemented configuration |
| Bubblewrap snapshot + proxies + deny-by-default config | implemented in the original; adapted, **not executed here** |
| Modes A/B/C host launchers | implemented; transitional, not sandboxed |
| Independent repository verifier inside the Rust loop | **not implemented** (role-based verifier exists separately) |
| Distinct planner/executor models | **not implemented** (single `--model`) |
| Parallel step execution | **not implemented** |

## Interview demonstration

A scripted 5–7 minute walkthrough is in
[docs/INTERVIEW_DEMO.md](docs/INTERVIEW_DEMO.md). It uses the recorded run and
live `bootstrap emit` validation; the core evidence does not require a model
call, and any live model-dependent step is marked as optional or unavailable.

## Publication status

This repository is published as a public engineering portfolio showcase. Every
included file is accounted for in
[PUBLICATION_MANIFEST.md](PUBLICATION_MANIFEST.md), including its source,
adaptation and verification status.

Licensing and release-readiness information is in
[LICENSING.md](LICENSING.md), [LICENSE_PENDING.md](LICENSE_PENDING.md), and
[RELEASE_READINESS.md](RELEASE_READINESS.md). The repository has no general
project-wide license; see `LICENSING.md`.
