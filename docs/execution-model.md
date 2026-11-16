# Execution model

There are two kinds of execution path in this project, and they are **not**
equivalent:

- **Host paths** (`bin/mode-a`, `bin/mode-b`, and `bin/mode-c`): OpenCode runs
  directly on the host with `--auto`. These are transitional and are not the
  security boundary.
- **Sandboxed path** (`bin/autonomous`): OpenCode runs inside Bubblewrap with a
  disposable snapshot, mount/network namespaces and allowlisted proxies.

Only `bin/autonomous` is the sandboxed autonomous entry point.

Mode A now defaults to the restricted `light` agent bundled with this showcase
(`agents/light.md`) and honours `MODE_A_AGENT`. That agent is a permission
denylist rather than an isolation boundary: it denies delegation, the `execute`
tool, `sudo` and other privilege-escalation commands, external directories,
common secret-file patterns, and mutating git commands, and it asks (rather than
silently allows) for other shell commands. Under `bin/mode-a`'s `--auto`, those
`ask` decisions are auto-approved, so Mode A does not prompt for ordinary shell
commands: the explicit `deny` rules are the part of the boundary that is
actually enforced automatically, while ordinary reads, edits and cheap tests run
without prompting. (The `ask` level only has an interactive effect when
OpenCode is run without `--auto`.) It is the intended replacement for
the original host `light` agent. It runs directly on the host and does not
provide OS-level isolation: shell commands can still reach host files,
interpreters, environment variables and the network, and permission patterns are
text-based rather than semantic. Mode C defaults to an `envelope` agent that is
not bundled; set `OPENCODE_AGENT` (for example to `build`) if that agent is
unavailable in your OpenCode installation. Overriding `MODE_A_AGENT` may change
the permission posture, so only override it with an agent whose restrictions
you have inspected. Neither default is a claim of complete host isolation.

## Modes

| Mode | Entry point | Agent | Sandboxed? | Status |
|------|-------------|-------|-----------|--------|
| A | `bin/mode-a <project> "<task>"` | `light` (default; override with `MODE_A_AGENT`) | no | transitional host path |
| B | `bin/mode-b <project> "<task>"` | `orchestrator` | no | transitional host path |
| C | `bin/mode-c <project> <spec> [args]` | `envelope` (via `bootstrap`) | no | drives the Rust orchestrator |
| — | `bin/autonomous <project> "<task>"` | allowlisted agent | **yes** | sandboxed boundary |

The mode launchers are thin wrappers. Mode C is the one that invokes the Rust
orchestrator (`bootstrap orchestrate`); its state is kept outside the target
repository under `<showcase-root>/runs/<project-slug>/<spec-slug>/` (where
`<showcase-root>` is the directory containing `bin/`) and linked into the
project as `.bootstrap`.
## Sandboxed autonomous lifecycle (`bin/autonomous`)

```
1. parse args; enforce a closed agent allowlist (deny-by-default, fail-closed)
2. canonicalise + deny-check the project path; resolve symlinks and re-check
3. validate/obtain a run root (default /tmp/opencode/autonomous-XXXXXX, mode 700)
4. allocate a run id; validate run-root children with lstat before mkdir/bind
5. snapshot.py create  → disposable snapshot + SHA-256 manifest
6. start host proxies: ollama-proxy-host.py, git-proxy-host.py (PID + starttime recorded)
7. sweep any leaked proxies from a previous run of this run root (PID-reuse safe)
8. build bwrap args; copy a per-run opencode.json; bind snapshot + state
9. bwrap --unshare-all --unshare-user ... /usr/bin/dash -c '<inner script>'
     inner: socat TCP:11434 → ollama.sock; wait for /api/tags; opencode run --auto
10. on exit: terminate proxies with verified PID identity; remove owned sockets
11. snapshot.py export → working tree back to the host project (conflict-safe)
```

### Execution boundaries

- **Filesystem.** The host project is never bound. The sandbox sees the
  snapshot at `/workspace` (rw) and a per-run state dir at `/sandbox-state`
  (rw). `/etc` is a fresh tmpfs with selective read-only binds; `/usr`, `/bin`,
  `/lib` are read-only.
- **Network.** `--unshare-all` removes the network namespace. The only path out
  is an inner `socat` forwarder from `127.0.0.1:11434` to the host Ollama proxy's
  Unix socket; the proxy allowlists inference endpoints only.
- **Git.** No real git exists inside. `/usr/bin/git` and `/bin/git` are a client
  shim that forwards argv to the host proxy; the proxy allowlists subcommands
  and rejects dangerous options, and runs against the snapshot.
- **Tool permissions.** The copied `opencode.json` is deny-by-default: web tools
  denied, `execute` denied, `sudo *` denied, `*.env`/`*.ssh`/`*.pem`/`*.key`
  denied, and a restricted `build` agent.

### Sandbox status

`bin/autonomous` and the `sandbox/` primitives are **inspected, not executed**
in the preparation of this showcase. The original code itself documents residual
TOCTOU races and a conservative project deny list. See
[security-boundaries.md](security-boundaries.md).

## Rust orchestrator lifecycle

```
read spec → create <work-dir>/.bootstrap/
  ├─ plan: one LLM call → Plan → plan.json + state.json
  └─ loop (while cursor < steps and executed < max_steps and executed < 50):
       execute step → step-NN-result.json → push history
       review result + remaining steps → step-NN-review.json
       apply continue | insert | skip | stop
       persist state.json after each fully processed step
```

When the absolute cap (`MAX_TOTAL_STEPS = 50`) is reached, the loop sets
`finished = true` and persists that terminal state to `state.json` before
stopping.

`--plan-only` stops after planning (and still writes resumable state);
`--resume` loads `state.json` instead of re-planning. The loop is synchronous
and single-slot.

State persistence is best-effort, not crash-safe: `state.json` is written after
a step is fully processed (execution plus review) and at the absolute cap.
An execution or review failure before the next successful state save can leave
the step unrecorded, so resuming may execute that step again. There is no
exactly-once execution, rollback of partially executed work, or deterministic
LLM output guarantee.

## Failure handling

- Executor emits no/invalid envelope → recorded as `status: "unknown"` with the
  raw text as the summary; the reviewer still decides.
- Review verdict unparseable → synthesised `stop` (fail safe to a human).
- `opencode` missing or a call exits non-zero → error propagates and the loop
  stops.
- `insert` requested with no `new_steps` → logged, loop continues.
- `--max-steps` / `MAX_TOTAL_STEPS` bound runaway insert loops. Reaching
  `MAX_TOTAL_STEPS` persists `finished = true` as a terminal state.
- Resume is best-effort: a step that failed before the next successful state
  save can be executed again; partial work is not rolled back.
- Sandboxed path: proxy startup failure exits non-zero; snapshot/export failures
  are logged and do not silently lose data.
