# sandbox — execution-boundary primitives

These are the host-side components of an experimental Bubblewrap (`bwrap`)
execution boundary for an OpenCode coding agent. They are copied from a private
local-agent workspace; `opencode.json` is a lightly adapted copy (see below).
Nothing here has been executed as part of preparing this showcase.

## Components

| File | Role |
|------|------|
| `snapshot.py` | Host-side snapshot/export. Copies a project into a disposable snapshot, excluding secret-pattern files, hardlinks and bare Git repositories; records a SHA-256 manifest; sanitizes credentials out of `.git/config`; later exports the working tree back with conflict detection. |
| `ollama-proxy-host.py` | Host-side Unix-socket → `127.0.0.1:11434` HTTP proxy. Forwards only an allowlist of inference endpoints (`/v1/models`, `/api/tags`, `/api/version`, `/v1/chat/completions`, `/api/show`) and returns 403 for everything else (model create/delete/pull, etc.). |
| `git-proxy-host.py` | Host-side Unix-socket JSON proxy. Validates a git argv against an allowlist of read/write subcommands, rejects dangerous options (`-c`, `-C`, `--git-dir`, `--work-tree`, `--exec-path`, `--force`, pagers), and runs `git -C <snapshot>` with a sanitized environment and hooks/fsmonitor disabled. |
| `git-client.py` | In-sandbox shim bound at `/usr/bin/git` and `/bin/git`. Forwards argv to the host proxy over `/sandbox-state/git.sock`. No real git binary exists inside the sandbox. |
| `opencode.json` | OpenCode configuration copied into the sandbox: deny-by-default permissions, read-only network tools, and a restrictive `build` agent. |

## How they compose

```
bin/autonomous
  ├─ snapshot.py create  → disposable snapshot + manifest
  ├─ ollama-proxy-host.py (Unix socket)   ─┐
  ├─ git-proxy-host.py    (Unix socket)   ─┤ host side
  └─ bwrap --unshare-all --unshare-user   ─┘
        /workspace   ← snapshot (rw)
        /sandbox-state ← per-run state (rw)
        /usr/bin/git ← git-client.py shim
        /opt/opencode/bin/opencode ← host OpenCode binary
        inner: socat TCP:11434 → ollama.sock, then `opencode run --auto`
  └─ snapshot.py export  → working tree back to the host project
```

The boundary is **snapshot isolation + mount namespace + network namespace +
allowlisted proxies**, not a permission prompt. The agent's writes land in the
snapshot; only the working tree is exported back, and only when the host file
has not changed since the snapshot (conflict-safe).

## Adaptations from the original

- `opencode.json`: the original carried a machine-specific `sudo` allowlist
  (passwordless `usermod`/`vgs`/`lvs`/`pvs`/`dmidecode`/`lvextend`/`resize2fs`
  permits). Those entries were removed; the pre-existing `sudo *` deny now
  applies to all `sudo` use. Model names and context limits are unchanged.
- `bin/autonomous`: hardcoded host paths were replaced with script-relative /
  environment-overridable values. See `../docs/security-boundaries.md`.
- Model names and context limits in `opencode.json` are examples requiring a
  compatible local Ollama provider configuration; they are not asserted to be
  correct for every model.

## Prerequisites (for the original boundary)

`bwrap`, `socat`, `python3`, an OpenCode binary, and a host Ollama endpoint.
The wrapper expects a toolchain directory (npm CLI) and an optional ripgrep
cache binary. None of these are bundled.

## Known limitations

- This is an **experimental** boundary, not a verified security guarantee. The
  original code documents residual time-of-check/time-of-use races (for example
  between `lstat` validation and `mkdir`/`bind`, and between PID identity checks
  and `kill`) that cannot be closed with shell tools alone.
- The inherited project deny list refuses any project under `/home` (as well as
  system directories). This is deliberately conservative and limits where the
  boundary can be pointed.
- The wrapper was written for a specific host layout (OpenCode at a fixed path,
  a fixed toolchain version, `dash` as `/usr/bin/dash`). The public adaptation
  parameterizes the paths but has not been run.
- Snapshot export never deletes host files and never resurrects deleted files;
  deletions are logged for human review.
