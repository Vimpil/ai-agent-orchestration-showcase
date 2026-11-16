# Security boundaries

This document describes the execution boundary in `sandbox/` and
`bin/autonomous`, what it actually enforces, and what remains unverified.

## What the boundary is

`bin/autonomous` runs an OpenCode agent inside Bubblewrap with:

- a **disposable snapshot** of the project (the host project is never bound);
- `--unshare-all --unshare-user --die-with-parent --disable-userns
  --assert-userns-disabled`, with a fixed inner uid/gid;
- a **deny-by-default OpenCode configuration** (`sandbox/opencode.json`);
- an **allowlisted Ollama proxy** (inference endpoints only);
- an **allowlisted git proxy** (no real git inside the sandbox);
- **no network namespace** except the single forwarder to the Ollama proxy;
- **conflict-safe export** of the working tree back to the host after the run.

The security claim is snapshot isolation + namespaces + allowlisted proxies, not
permission prompts.

## Mode A host path (not a boundary)

`bin/mode-a` is not a security boundary. It runs OpenCode directly on the host
with `--auto` and the `light` agent. The `light` agent is a permission denylist
layered on OpenCode's permission system; it is not OS-level isolation and does
not prevent a determined or accidental misuse of shell access. Under `--auto`,
`ask` permissions are auto-approved, so only explicit `deny` rules are enforced
automatically. Permission patterns match command text and file paths with
whole-value wildcards; they are not semantic analysis and can be bypassed by
interpreters, command substitution, renamed binaries, or file access through
non-file commands. File-read permission rules do not by themselves prevent shell
commands from reading host files. OpenCode tool permissions are not shell-level
host access controls: a shell command that is allowed or auto-approved can still
reach arbitrary host files, interpreters, environment variables and the network.
Secret-file restrictions and `external_directory` are OpenCode permission rules,
not OS-level protection, and they do not protect arbitrary host secrets from a
shell command that bypasses or ignores them. Residual host-access risks remain
and are acknowledged; only `bin/autonomous` provides snapshot/namespace
isolation. Mode A is intended for trusted local repositories and code you are
willing to run on the host; it is not suitable for untrusted code and does not
protect arbitrary host secrets.

The effective `light` agent configuration can be affected by global and
project-level OpenCode configuration. `bin/mode-a` now resolves the selected
agent in the target project context and, for the bundled `light` agent,
validates its critical permissions before running; this is an availability and
configuration check, not proof of security. An agent override or a permissive
global/project configuration can still change the permission posture.

## Enforced restrictions

| Boundary | Mechanism |
|----------|-----------|
| Host project not writable in place | snapshot bind at `/workspace`; export only changed files |
| Secret-pattern files | excluded from snapshot and export (`snapshot.py`) |
| Hardlinks / bare Git repos | excluded from snapshot and export |
| `.git` hooks/config/refs | never exported; `.git/config` credentials sanitized |
| Network | `--unshare-all`; only `socat` → Ollama proxy |
| Ollama API | allowlist: `/v1/models`, `/api/tags`, `/api/version`, `/v1/chat/completions`, `/api/show`; 403 otherwise |
| Git | client shim → host proxy; subcommand + option allowlist; hooks/fsmonitor disabled |
| Shell / edits | OpenCode permissions: `execute` denied, `sudo *` denied, web denied, `*.env`/`.ssh`/`.pem`/`.key` denied |
| Agent choice | closed allowlist; unknown agent exits 2 before any snapshot work |
| Run root | default `/tmp/opencode/autonomous-XXXXXX`, mode 700, invoking uid |
| Proxy cleanup | PID starttime + exact cmdline match before any signal; stale/mismatched PIDs are never killed |

## Verified vs not verified

**Inspected only.** Neither `bin/autonomous` nor the `sandbox/` primitives were
executed while preparing this showcase. The original implementation was written
for a specific host layout and was not re-run in this environment. The public
adaptation parameterizes host paths but has not been validated end-to-end.

**Inherited, not re-audited.** The boundary code contains its own inline notes
about residual races and limitations. This showcase does not claim to have
audited or fixed them.

## Known limitations

- **Residual TOCTOU races.** Validation and use are separate syscalls
  (`lstat` → `mkdir`/`bind`, PID identity → `kill`). The original documents
  these and notes they cannot be closed with shell tools without
  `dirfd`/`O_NOFOLLOW` or `pidfd` primitives.
- **Conservative project deny list.** The wrapper refuses any project under
  `/home` (and system directories). This is inherited from the original and
  limits where the boundary can be pointed; it is not a portability fix.
- **Host-layout assumptions.** The inner script assumes `dash` at
  `/usr/bin/dash`, `node` at `/usr/bin/node`, and a toolchain bound at
  `/opt/toolchain`. The npm CLI path is configurable (`NPM_CLI_REL`) but the
  layout must exist.
- **No independent verifier inside the sandbox.** The sandbox restricts what the
  agent can reach; it does not verify that the agent's work is correct. The
  orchestrator's reviewer and the role-based verifier are separate mechanisms.
- **Not a general security product.** This is an experimental boundary for a
  local agent, not a hardened sandbox. Do not assume it contains a determined
  attacker with host access.

## Adaptations

- `bin/autonomous`: hardcoded workspace/OpenCode/toolchain/ripgrep paths were
  replaced with script-relative or environment-overridable values; the
  machine-specific project deny entries were removed.
- `sandbox/opencode.json`: the machine-specific `sudo` allowlist was removed, so
  the existing `sudo *` deny applies.

See `sandbox/README.md` for the component inventory and composition diagram.
