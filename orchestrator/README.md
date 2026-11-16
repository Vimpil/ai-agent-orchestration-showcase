# local-llm-loop

A small Rust harness that drives [opencode](https://opencode.ai) against a
**local** LLM in an autonomous **plan → execute → review** loop.

Give it a short spec file — a goal plus architectural decisions — and it asks
the model to design a plan, then iterates the steps: a tool-using agent
implements each step and a supervising model reviews the result and decides
whether to continue, insert new steps, skip a step, or stop and request human
intervention.

The harness is **model-agnostic** — it shells out to `opencode run --model
<provider/model>`, so any model opencode can reach works.

> The binary and crate are named `bootstrap`; the upstream project is
> `local-llm-loop`.

## Overview

```
spec.txt
   │
   ▼
[PLAN]   planner LLM → { design, notes, steps[] }              (.bootstrap/plan.json)
   │
   ▼
for each step (Rust owns the cursor + history):
   ├─ [EXECUTE]  tool-using LLM performs the step, emits a JSON result envelope
   │             { summary, new_or_changed_files[], changes, features[],
   │               bugs[], issues[], status }                  (.bootstrap/step-NN-result.json)
   └─ [REVIEW]   supervising LLM sees the result + remaining steps and returns:
                    continue | insert | skip | stop             (.bootstrap/step-NN-review.json)
```

Rust owns all orchestration state; every LLM call is a stateless `opencode run`
with the needed context passed in the prompt. Each role writes its JSON envelope
to a file and validates it with the **`bootstrap emit`** helper (a CLI on the
model's `$PATH`), which checks it against the harness schema and returns a
correctable error — giving the model up to three correction attempts (see
[`emit`](#emit--validate-a-json-envelope-the-model-facing-helper) below). The
harness also extracts JSON robustly from whatever the model produces. See
[docs/orchestrator.md](docs/orchestrator.md) for the full design.

## Prerequisites

- A Rust toolchain (edition 2024; `rustc` ≥ 1.85) via [rustup](https://rustup.rs/).
- The `opencode` CLI on your `$PATH`.
- A model reachable by opencode. The default `--model` value is
  `llamacpp/qwable` (a local OpenAI-compatible endpoint); substitute whatever
  `provider/model` your OpenCode configuration exposes. Model/server setup is
  environment-specific and is not bundled with this project. The Rust harness
  default is `llamacpp/qwable`; bundled examples, scripts, and agent files may
  use Ollama model names such as `ollama/gpt-oss:20b`. These are configurable
  provider/model examples, not a universal provider requirement.

## Build

```bash
cargo build --release
# binary: target/release/bootstrap
```

## Usage

The binary has three subcommands.

### `orchestrate` — plan/execute/review from a spec file

```bash
bootstrap orchestrate path/to/spec.txt \
  --model llamacpp/qwable \
  --work-dir /path/to/target/project \
  --max-steps 20 \
  --verbose
```

| Option | Description | Default |
|--------|-------------|---------|
| `<SPEC_FILE>` | Spec file: goal + description + architectural decisions | (required) |
| `--model` | Model in `provider/model` form | `llamacpp/qwable` |
| `--work-dir` | Directory the agent works in; `.bootstrap/` artifacts go here | `.` |
| `--max-steps` | Safety cap on steps executed in this invocation | `20` |
| `--plan-only` | Produce and print the plan, then stop (cheap planner test) | off |
| `--resume` | Continue from saved state (`.bootstrap/state.json`) instead of re-planning | off |
| `--verbose` | Verbose logging | off |

`--max-steps` caps the steps executed in *this* invocation. `--resume` lets you
run one step at a time across many invocations (`--resume --max-steps 1`) to
spread a slow build over separate, independently inspectable runs. `MAX_TOTAL_STEPS = 50`
is a separate cumulative cap on total executed steps across all resumes.

### `exec` — run an explicit list of tasks

```bash
bootstrap exec "create a test" "run the test" "validate the results" \
  --model llamacpp/qwable --verbose
```

Each task is a separate `opencode run`; by default they chain into one session
(`--no-chain` to isolate them).

### `emit` — validate a JSON envelope (the model-facing helper)

```bash
bootstrap emit <plan|step|review> --file path/to/envelope.json
```

A plain CLI helper (on `$PATH`, **not** MCP) that the **model** calls from
opencode's shell tool. It validates the JSON the model just wrote against the
harness's own schema, rewrites it canonically on success, and prints `OK:` or a
precise, correctable `Error:` with the expected shape:

```text
$ bootstrap emit review --file step-02-review.llm.json
Error: review envelope invalid: missing field `action` …
expected shape:
{"action":"continue|insert|skip|stop","reason":"...","new_steps":[]}
```

The role prompts tell each LLM to write its envelope to a file, run `emit`, fix
on any `Error:`, and only reply `DONE` after `OK:`. This makes the envelope
channel retryable but not guaranteed: the harness retries a rejected envelope up
to three times, feeding the parser error back into the next prompt. Exhausted
retries do not guarantee recovery; the loop may record an `unknown` result or
stop for human review. `emit` exits non-zero on failure, so the model's shell
sees the error.

### Demo scripts

```bash
PLAN_ONLY=1 ./scripts/demo-orchestrate.sh   # one cheap planner call
./scripts/demo-orchestrate.sh               # full loop in an isolated temp workspace
./scripts/demo.sh                           # single tool-using exec call
./scripts/demo-3-steps.sh                   # 3 chained exec tasks
./scripts/orchestrate-stepwise.sh plan      # plan once, then one step per run
```

These scripts build the crate and make real model calls; they are a
reproducibility aid, not an offline test.

## Documentation

- [docs/orchestrator.md](docs/orchestrator.md) — control flow and rationale
- [docs/architecture.md](docs/architecture.md) — components and data flow
- [docs/design.md](docs/design.md) — CLI, JSON contracts, sentinels, artifacts
- [docs/prd.md](docs/prd.md) — product requirements
- [docs/plan.md](docs/plan.md) — roadmap and current status
- [docs/usage.md](docs/usage.md) — build and run instructions

## License

Released under the [MIT License](LICENSE).

Copyright (c) 2026 Michael A. Wright

## Provenance and adaptations

This directory is a copy of the `local-llm-loop` Rust crate from a private
local-agent workspace, with the following presentation-only changes:

- the model/hardware benchmark and test-fleet sections of the original README
  were removed (they describe private infrastructure);
- references to private absolute paths and to benchmark/POC reports not included
  here were replaced with generic wording;
- one default workspace path in `scripts/orchestrate-stepwise.sh` was made
  relative.

The orchestration source (`src/`) is functionally unchanged apart from comment
edits that removed private paths. See `../PUBLICATION_MANIFEST.md` for the
file-by-file record.
