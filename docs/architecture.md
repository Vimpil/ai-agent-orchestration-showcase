# Architecture

This project is a curated, public subset of a private local AI-agent workspace.
It contains two independent orchestration approaches plus the execution
boundary that was built around them.

## Components

| Component | Location | What it is |
|-----------|----------|------------|
| Rust orchestrator | `orchestrator/` | A model-agnostic `plan → execute → review` loop. Rust owns the plan, step cursor and history; each role is a stateless `opencode run` call. |
| Specialist role definitions | `agents/` | Seven OpenCode agent definitions (orchestrator, explorer, planner, researcher, coder, verifier, reviewer) with role-scoped tool permissions. |
| Execution boundary | `sandbox/`, `bin/autonomous` | A Bubblewrap sandbox: disposable snapshot, mount/network namespaces, allowlisted Ollama and git proxies, deny-by-default OpenCode permissions. |
| Mode launchers | `bin/mode-a`, `bin/mode-b`, `bin/mode-c` | Thin entry points for three host-execution modes (A/B transitional, C drives the Rust orchestrator). |
| Recorded example | `examples/sample-workflow/` | Real `.bootstrap/` artifacts from an actual orchestrator run. |

## Two orchestration approaches

**1. Code-owned loop (`orchestrator/`).** The Rust binary is the source of truth
for state. A spec becomes a `Plan`; the loop executes one `Step` at a time and
asks a supervising model to `continue`, `insert`, `skip`, or `stop`. All context
is passed explicitly in each prompt, so orchestration control flow and state handling are deterministic and resumable
(`.bootstrap/state.json`); the LLM-generated plans, execution results, and reviews are not. This is the approach that produced the recorded run.

**2. Config-driven role delegation (`agents/`).** OpenCode's own subagent
mechanism is configured with a primary orchestrator and six specialists. The
orchestrator classifies a change (trivial / standard / complex / domain) and
delegates through the role hierarchy. Permissions are enforced by OpenCode's
configuration, not only by prompt text.

These are alternatives, not layers: the recorded run used approach 1; the role
files are the configuration for approach 2.

## Data flow (code-owned loop)

```
spec.txt
  │
  ▼
[PLAN]   planner LLM → Plan{design, notes, steps[]}        → .bootstrap/plan.json
  │
  ▼  Rust owns cursor + history; loop while cursor < steps.len()
  ├─ [EXECUTE] tool-using LLM → StepResult                → .bootstrap/step-NN-result.json
  └─ [REVIEW]  supervising LLM → ReviewDecision           → .bootstrap/step-NN-review.json
        continue → cursor + 1
        insert   → splice new_steps after cursor, cursor + 1
        skip     → remove next step, cursor + 1
        stop     → persist state, halt for human
```

Artifacts for a successfully processed step are written before the next step
begins, so a run can be inspected or resumed (`--resume`) from saved state.
Persistence is best-effort and not crash-safe.

## State and context

- `LoopState` (`orchestrator/src/types.rs`) holds `design`, `steps`, `cursor`,
  `executed`, `history`, `finished`, `stopped_reason`.
- `HistoryEntry` pairs each executed `Step` with its `StepResult`; prior
  summaries are injected into later executor prompts.
- The step list is mutated in place by `insert`/`skip`, which is why the
  orchestrator — not the model — owns it.
- `--max-steps` caps steps per invocation; `MAX_TOTAL_STEPS = 50` caps the whole
  run across resumes.

## Tool integration

The orchestrator does not call a model API directly. It shells out to
`opencode run <prompt> --model <provider/model>` (`orchestrator/src/llm.rs`),
optionally selecting a restricted agent (`OPENCODE_AGENT`, default `envelope`)
and always passing `--auto` unless `OPENCODE_NO_AUTO=1`. All model access goes
through OpenCode, which owns the tool loop, file edits and shell execution.

See [execution-model.md](execution-model.md) for the modes and the sandboxed
path, and [verification.md](verification.md) for the review/failure model.
