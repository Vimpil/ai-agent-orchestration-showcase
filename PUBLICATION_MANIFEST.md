# Publication manifest

Provenance and status of every file in this public showcase. Source repository: a private local-agent development workspace (curated from the development workspace; not modified).

**Verification legend**

- **TESTED** — executed during preparation (see "Validation performed" below).
- **SYNTAX** — parsed/compiled statically, not executed.
- **INSPECTED** — read and compared with the source, not executed.
- **N/A** — documentation/metadata.

**Status legend**

- **IMPLEMENTED** — real, working code/config in the source workspace.
- **ADAPTED** — copied with documented changes (paths, links, machine-specific values).
- **NEW** — written for this showcase from the source.
- **RECORDED** — real run artifacts copied unchanged.

## Included files

The showcase contains **55 publishable files**: every regular file under the showcase root, excluding generated build artifacts (notably `orchestrator/target/`, which was removed during the final hygiene check), recorded workflow artifacts (Class X1, excluded from all copies), and any cache/log/temporary files. Directories are not counted. This count matches `RELEASE_READINESS.md`. The additional files are `LICENSING.md` (licensing index; documentation only, not a license) and `.gitignore` (Git hygiene; not a showcase component).

| Public path | Original source path | Why selected | Copy / adaptation | Status | Deps included | Verified |
|---|---|---|---|---|---|---|
| `README.md` | new (based on source READMEs) | Top-level overview and honest status | NEW | Documentation | N/A | INSPECTED |
| `LICENSE_PENDING.md` | new | License status and required decisions | NEW | Documentation | N/A | INSPECTED |
| `LICENSING.md` | new | Licensing index and component-level status (documentation only; not a license) | NEW | Documentation | N/A | INSPECTED |
| `THIRD_PARTY_NOTICES.md` | new | Third-party provenance and license notices | NEW | Documentation | N/A | INSPECTED |
| `RELEASE_READINESS.md` | new | Final publication-readiness verdict, blockers, warnings, cleanup, and next steps | NEW | Documentation | N/A | INSPECTED |
| `.gitignore` | new | Git hygiene: ignore secrets, caches, build outputs, local state | NEW | Metadata | N/A | INSPECTED |
| `PUBLICATION_MANIFEST.md` | new | This file | NEW | Documentation | N/A | INSPECTED |
| `docs/architecture.md` | new (from `orchestrator/docs/architecture.md`, `docs/orchestrator.md`) | Component/data-flow overview | NEW | Documentation | N/A | INSPECTED |
| `docs/agent-roles.md` | new (from `agents/*.md`) | Role/permission/workflow reference | NEW | Documentation | N/A | INSPECTED |
| `docs/execution-model.md` | new (from `bin/*`, `orchestrator/docs/*`) | Modes, lifecycle, failure handling | NEW | Documentation | N/A | INSPECTED |
| `docs/verification.md` | new (from `orchestrator/src/*`, `agents/*`) | Reviewer/emit/verifier behaviour | NEW | Documentation | N/A | INSPECTED |
| `docs/INTERVIEW_DEMO.md` | new (from recorded run and source docs) | Interview demonstration walkthrough | NEW | Documentation | N/A | INSPECTED |
| `docs/security-boundaries.md` | new (from `sandbox/*`, `bin/autonomous`) | Boundary mechanics and limitations | NEW | Documentation | N/A | INSPECTED |
| `orchestrator/README.md` | `src/local-llm-loop/README.md` | Crate overview/usage | ADAPTED (removed hardware-fleet/benchmark sections and private paths) | Documentation | N/A | INSPECTED |
| `orchestrator/Cargo.toml` | `src/local-llm-loop/Cargo.toml` | Build metadata | ADAPTED (`license = "MIT"` added) | Metadata | crates via Cargo.lock (not vendored) | INSPECTED |
| `orchestrator/Cargo.lock` | `src/local-llm-loop/Cargo.lock` | Reproducible dependency versions | unchanged | Metadata | crates not vendored | INSPECTED |
| `orchestrator/LICENSE` | `src/local-llm-loop/LICENSE` | MIT license for the crate | unchanged | Metadata | N/A | INSPECTED |
| `orchestrator/.gitignore` | `src/local-llm-loop/.gitignore` | Ignores `target/`, `.bootstrap/` | unchanged | Metadata | N/A | INSPECTED |
| `orchestrator/src/main.rs` | `src/local-llm-loop/src/main.rs` | CLI dispatch, `exec` task runner | unchanged | IMPLEMENTED | Rust crate | TESTED (15 unit tests) |
| `orchestrator/src/orchestrate.rs` | `src/local-llm-loop/src/orchestrate.rs` | plan→execute→review loop, state | ADAPTED (comment link removed) | IMPLEMENTED | Rust crate | TESTED |
| `orchestrator/src/prompts.rs` | `src/local-llm-loop/src/prompts.rs` | role prompts + JSON schemas | unchanged | IMPLEMENTED | Rust crate | TESTED (indirectly) |
| `orchestrator/src/emit.rs` | `src/local-llm-loop/src/emit.rs` | model-facing schema validator | unchanged | IMPLEMENTED | Rust crate | TESTED |
| `orchestrator/src/types.rs` | `src/local-llm-loop/src/types.rs` | serde contracts | unchanged | IMPLEMENTED | Rust crate | TESTED (indirectly) |
| `orchestrator/src/llm.rs` | `src/local-llm-loop/src/llm.rs` | opencode adapter, JSON extraction | ADAPTED (2 comment links/private path removed) | IMPLEMENTED | Rust crate | TESTED |
| `orchestrator/docs/architecture.md` | `src/local-llm-loop/docs/architecture.md` | component/data-flow doc | unchanged | Documentation | N/A | INSPECTED |
| `orchestrator/docs/design.md` | `src/local-llm-loop/docs/design.md` | CLI/JSON/artifact contracts | unchanged | Documentation | N/A | INSPECTED |
| `orchestrator/docs/orchestrator.md` | `src/local-llm-loop/docs/orchestrator.md` | control-flow rationale | ADAPTED (private script reference genericised) | Documentation | N/A | INSPECTED |
| `orchestrator/docs/plan.md` | `src/local-llm-loop/docs/plan.md` | roadmap/status | ADAPTED (POC links → recorded run) | Documentation | N/A | INSPECTED |
| `orchestrator/docs/prd.md` | `src/local-llm-loop/docs/prd.md` | requirements | ADAPTED (POC links → recorded run) | Documentation | N/A | INSPECTED |
| `orchestrator/docs/usage.md` | `src/local-llm-loop/docs/usage.md` | build/run instructions | ADAPTED (config doc link removed) | Documentation | N/A | INSPECTED |
| `orchestrator/examples/spec-greeter.txt` | `src/local-llm-loop/examples/spec-greeter.txt` | reproducible example spec | unchanged | IMPLEMENTED | N/A | INSPECTED |
| `orchestrator/scripts/demo.sh` | `src/local-llm-loop/scripts/demo.sh` | single tool-using exec demo | ADAPTED (private server path comment) | IMPLEMENTED | opencode + model | SYNTAX |
| `orchestrator/scripts/demo-3-steps.sh` | `src/local-llm-loop/scripts/demo-3-steps.sh` | chained exec demo | ADAPTED (private server path comment) | IMPLEMENTED | opencode + model | SYNTAX |
| `orchestrator/scripts/demo-orchestrate.sh` | `src/local-llm-loop/scripts/demo-orchestrate.sh` | full loop demo | ADAPTED (private server path comment) | IMPLEMENTED | opencode + model | SYNTAX |
| `orchestrator/scripts/orchestrate-stepwise.sh` | `src/local-llm-loop/scripts/orchestrate-stepwise.sh` | resume/stepwise demo | ADAPTED (default workspace + model) | IMPLEMENTED | opencode + model | SYNTAX |
| `agents/README.md` | new | role file inventory/notes | NEW | Documentation | N/A | INSPECTED |
| `agents/orchestrator.md` | `workspace/.opencode/agents/orchestrator.md` | primary role + delegation policy | unchanged | IMPLEMENTED (config) | OpenCode | INSPECTED |
| `agents/explorer.md` | `workspace/.opencode/agents/explorer.md` | read-only discovery role | unchanged | IMPLEMENTED (config) | OpenCode | INSPECTED |
| `agents/planner.md` | `workspace/.opencode/agents/planner.md` | read-only planning role | unchanged | IMPLEMENTED (config) | OpenCode | INSPECTED |
| `agents/researcher.md` | `workspace/.opencode/agents/researcher.md` | read-only research role | unchanged | IMPLEMENTED (config) | OpenCode | INSPECTED |
| `agents/coder.md` | `workspace/.opencode/agents/coder.md` | only editing role | unchanged | IMPLEMENTED (config) | OpenCode | INSPECTED |
| `agents/verifier.md` | `workspace/.opencode/agents/verifier.md` | independent validation role | unchanged | IMPLEMENTED (config) | OpenCode | INSPECTED |
| `agents/reviewer.md` | `workspace/.opencode/agents/reviewer.md` | read-only review role | unchanged | IMPLEMENTED (config) | OpenCode | INSPECTED |
| `agents/light.md` | new (restricted Mode A host agent) | restricted primary agent for `bin/mode-a` | NEW | IMPLEMENTED (config) | OpenCode | INSPECTED |
| `sandbox/README.md` | new | component inventory + composition + limits | NEW | Documentation | N/A | INSPECTED |
| `sandbox/snapshot.py` | `sandbox/snapshot.py` | snapshot/export with secret exclusion | unchanged | IMPLEMENTED | python3 stdlib | SYNTAX |
| `sandbox/git-proxy-host.py` | `sandbox/git-proxy-host.py` | host git allowlist proxy | unchanged | IMPLEMENTED | python3 stdlib + host git | SYNTAX |
| `sandbox/git-client.py` | `sandbox/git-client.py` | in-sandbox git shim | unchanged | IMPLEMENTED | python3 stdlib | SYNTAX |
| `sandbox/ollama-proxy-host.py` | `sandbox/ollama-proxy-host.py` | Ollama HTTP allowlist proxy | unchanged | IMPLEMENTED | python3 stdlib | SYNTAX |
| `sandbox/opencode.json` | `sandbox/opencode.json` | deny-by-default sandbox config | ADAPTED (machine-specific sudo allowlist removed) | IMPLEMENTED (config) | OpenCode | INSPECTED (JSON valid) |
| `bin/autonomous` | `bin/autonomous` | sandboxed autonomous entry point | ADAPTED (paths parameterised; machine deny entries removed; report name genericised) | IMPLEMENTED (adapted, **not executed here**) | bwrap, socat, python3, opencode, toolchain | SYNTAX |
| `bin/mode-a` | `bin/mode-a` | Mode A host launcher | ADAPTED (PATH derived from script dir; transitional note) | IMPLEMENTED (transitional) | opencode + model | SYNTAX |
| `bin/mode-b` | `bin/mode-b` | Mode B host launcher | ADAPTED (PATH derived from script dir; transitional note) | IMPLEMENTED (transitional) | opencode + model | SYNTAX |
| `bin/mode-c` | `bin/mode-c` | Mode C orchestrator launcher | ADAPTED (state root derived from script dir; PATH; note) | IMPLEMENTED | bootstrap + opencode + model | SYNTAX |
| `examples/sample-workflow/README.md` | new | example explanation + NOT VERIFIED status | NEW | Documentation | N/A | INSPECTED |

(`.../` = `examples/sample-workflow/recorded-run/`.)

## Validation performed

- `bash -n` on `bin/autonomous`, `bin/mode-a`, `bin/mode-b`, `bin/mode-c`, and
  all `orchestrator/scripts/*.sh` — no syntax errors.
- `python3 -m py_compile` on all `sandbox/*.py` — compiles (bytecode cache removed
  afterwards).
- `cargo test --offline` on a **temporary copy** of `orchestrator/` (in
  a temporary directory outside the showcase, not the showcase): **15 passed, 0 failed**. The
  linker was the original workspace's `zig cc` because no system C compiler is
  installed.
- The real `bootstrap emit` binary (built in the temp copy) accepted all seven
  recorded envelopes: `plan` (2 steps), three `step` envelopes
  (`status=completed`), three `review` envelopes (`continue`, `insert`,
  `continue`).
- Structural checks on `state.json`: `finished=true`, `cursor == len(steps) == 3`,
  `executed == len(history) == 3`, exactly one `insert` review, and the inserted
  step id `101` present in both the final plan and the history.
- JSON validity for `sandbox/opencode.json` and all recorded artifacts.
- Confirmed no symlinks, no `__pycache__`/`.bootstrap` build outputs, and no
  absolute private paths or credential patterns. (`orchestrator/target/` was present and
  removed during the final hygiene check; see below.)

## Final publication-readiness review (this pass)

- Re-verified all relative Markdown links resolve (26 files).
- Re-verified JSON validity of `sandbox/opencode.json` and all eight recorded
  workflow artifacts.
- Re-ran `bash -n` on `bin/autonomous`, `bin/mode-a`, `bin/mode-b`,
  `bin/mode-c`, and all `orchestrator/scripts/*.sh`.
- Re-ran `python3 -m py_compile` on all `sandbox/*.py` (bytecode cache removed).
- Removed `orchestrator/target/` (generated Rust build artifacts) during the final
  hygiene check. Confirmed no other symlinks, build artifacts, caches, logs, or private
  absolute paths remain.
- Sanitized local absolute source paths and machine-specific references in this
  manifest.
- Removed the empty, unused `licenses/` directory.
- Added `RELEASE_READINESS.md`.
- Did not re-run `cargo test` or the sandbox; prior verification evidence is
  unchanged.

## Not executed

- `bin/autonomous` and the sandbox primitives (no bwrap run, no model requests).
- `bin/mode-a`, `bin/mode-b`, `bin/mode-c` (no model requests).
- `orchestrator/scripts/*` (they build and call a model).
- The greeter demo end-to-end. **The example is NOT VERIFIED in this
  environment.**

## Important excluded components

| Excluded | Reason |
|---|---|
| `src/local-coder/` (Node/TS CLI, `node_modules/`, catalogue, dist) | Separate upstream project; large; third-party dependencies; not needed for the orchestration/boundary story. |
| `etc/` (model catalogues, OpenCode patch, `rustup-init.sh`, `backups/`) | Machine-specific catalogues (local subset), internal patch/backup artifacts. |
| `workspace/.opencode/local-coder-state.json`, `local-coder-ownership.json`, `opencode.json`, `AGENTS.md` | Machine-local state and ownership records; not portable. |
| `workspace-light/` | Duplicate reference configuration. |
| `runs/` beyond the one recorded run | Only one run was needed as evidence. |
| `toolchain/` (npm, zig, linklibs) | Large third-party binaries; not redistributed. |
| `src/local-llm-loop/target/` | Build output containing private absolute paths. |
| `examples/sample-workflow/recorded-run/*.json` | Recorded workflow artifacts (Class X1); excluded from all redistributed copies until ownership and applicable rights are verified. No custom reuse grant. (Removed from this release candidate per approved Decision C, Option 1.) |
| `src/local-llm-loop/docs/config/`, `docs/*poc*`, `docs/performance-analysis.md`, `docs/test-fleet.md`, `docs/fleet-strategy.md`, `docs/older-hardware.md`, `docs/future-research.md`, `docs/glm-models.md`, `docs/optimizations-plan.md`, `docs/plan-*.md` | Machine-specific benchmark/POC/fleet reports and model-download scripts; the task excludes internal reports and local machine configuration. |
| `src/local-llm-loop/README.md` benchmark sections | Private test-fleet/hardware details. |
| `logs/` | Runtime logs. |
| `.git/` directories | Git metadata; the task forbids touching it. |

## Known functionality gaps

- No independent repository verifier inside the Rust loop; the reviewer judges
  reported results and the plan.
- Single model for planner/executor/reviewer (`--model`); no `--top-model` /
  `--exec-model`.
- No parallel step execution; no resume after a reviewer `stop` with human edits.
- Sandbox export does not delete host files and does not resurrect deleted files.
- The sandbox boundary is adapted and unverified; residual TOCTOU races are
  inherited and documented.
- The conservative project deny list refuses projects under `/home`.

## Known security limitations

- The sandbox is an experimental boundary, not a verified containment system.
- `bin/autonomous` was not executed here; its adaptation is unverified.
- The sandbox restricts reachability, not correctness of the agent's work.
- See `docs/security-boundaries.md` for the full list.

## Notes for manual review

1. **Licensing status** — see `LICENSING.md` and `LICENSE_PENDING.md`. A
   licensing policy has been approved in principle (Portfolio-Friendly
   Source-Available, Permission-Controlled Commercial Use) but is not yet
   implemented as operative license text. The `orchestrator/` component is MIT;
   the remaining components remain unlicensed pending owner confirmation of
   scope, a commercial permission contact, and legal review.
2. **Model defaults** — `bin/mode-b`, `bin/mode-c` and the `agents/*.md` files
   contain the original machine's Ollama aliases; decide whether to keep,
   genericise, or document them (currently documented).
3. **Sandbox config** — confirm the adapted `sandbox/opencode.json` (sudo allowlist
   removed) matches the intended posture.
4. **Private-path scan** — re-run the scan on the final tree; the current scan
   found no absolute private paths or credential patterns.
5. **Recorded run** — confirm the artifacts contain no sensitive values (they are
   a Python `greet` exercise; reviewed).
6. **Attribution** — confirm the MIT copyright for `orchestrator/` and the
   provenance notes are acceptable.
