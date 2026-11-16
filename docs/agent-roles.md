# Agent roles

The `agents/` directory contains seven OpenCode role definitions derived from
the third-party project `gmarland/local-coder` (MIT, Copyright (c) 2026
local-coder contributors). They are configuration files (YAML front matter +
prompt body); the prompt bodies are not presented as original work by the
showcase owner. Model aliases were changed from a machine-specific value to a
documented example. See `THIRD_PARTY_NOTICES.md`.

## Roles and permissions

| Role | Mode | Edit | Shell | Web | Delegates to |
|------|------|------|-------|-----|--------------|
| orchestrator | primary | deny | deny | deny | explorer, planner, coder, verifier, researcher, reviewer |
| explorer | subagent | deny | deny | deny | — |
| planner | subagent | deny | deny | deny | — |
| researcher | subagent | deny | deny | allow | — |
| coder | subagent | **allow** | ask, with allowlist | deny | — |
| verifier | subagent | deny | ask, with allowlist | deny | — |
| reviewer | subagent | deny | read-only git | deny | — |

`light.md` is an additional host-path agent used by Mode A and is not part of
the orchestrated role set above. It may edit and run shell commands under a
denylist, denies delegation, `execute`, `sudo` and other privilege-escalation
commands, external directories, common secret-file patterns and mutating git
commands, and asks for other shell commands (auto-approved under `--auto`). It
is not sandboxed and is not an isolation boundary.

All seven upstream-derived roles deny `external_directory` (the showcase-specific `light.md` also denies it). (The sandbox's `build` agent in `sandbox/opencode.json` is different: it uses `ask` for `external_directory`, not `deny`.) The coder's shell allowlist coversread-only git inspection, `grep`/`rg`/`wc`, and project test/build/lint/typecheck
commands; `git commit` requires approval and `git push` is denied. The verifier
can run validation but cannot edit, commit or push.

## Adaptive workflows

The orchestrator prompt defines four workflows and requires it to choose the
least costly one that covers the change:

```
Trivial:  Coder → Verifier
Standard: Explorer → Coder → Verifier
Complex:  Explorer → Planner → Coder → Verifier → Reviewer
Domain:   Explorer + Researcher → Planner → Coder → Verifier → Reviewer
```

A task can be promoted to a more involved workflow if discovery shows it is
larger than it first appeared.

## Task contract

For every repository change, the orchestrator is instructed to create one
versioned JSON **task contract** and repeat it unchanged in every coder and
verifier call. The contract carries:

- `allowedPaths`, `targetFiles`;
- `protectedValues` with a rule (`present` or `unchanged`) and paths;
- `expectedOutcomes` / `forbiddenOutcomes` using a fixed set of outcome kinds
  (`fileExists`, `fileMissing`, `fileContains`, `fileNotContains`, `fileEquals`,
  `fileHashEquals`, `jsonPointerEquals`);
- `preserveUnrelatedContent`, `requiresTests`, `noTestReason`;
- `validationCommands` as `{command, args, cwd, timeoutMs}` (never shell text);
- `maxRepairAttempts`.

The point is to keep exact user values and acceptance criteria attached to the
work instead of relying on a chain of increasingly compressed natural-language
summaries.

## Completion rule

- The orchestrator treats a coder's `STATUS: SUCCESS` only as a hint about where
  to inspect; it independently reads the affected files.
- It then calls the verifier as a **new** task. The verifier must return an
  unambiguous `STATUS: PASS` or `FAIL` with repository evidence for every
  expected outcome and protected value.
- On `FAIL`, the orchestrator makes a narrow repair call (at most two
  verification-repair attempts).
- In complex/domain workflows, the reviewer runs only after the verifier passes;
  at most one review-remediation pass is allowed.
- Completion is reported only after the final verifier `PASS` and a final review
  with no unresolved substantive findings.

## Environment-specific values

The `model:` fields are local Ollama aliases from the original machine and must
be replaced with a model the reader's OpenCode/Ollama setup provides. The
permission blocks and prompt logic are the portable part.

See `agents/README.md` for the file inventory and `verification.md` for how this
relates to the Rust orchestrator's own review loop.
