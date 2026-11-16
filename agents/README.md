# agents — OpenCode specialist role definitions

Seven OpenCode agent definitions derived from the third-party project
`gmarland/local-coder` (MIT, Copyright (c) 2026 local-coder contributors).
They are configuration, not executable code: each file is YAML front matter plus
a prompt body. See `../THIRD_PARTY_NOTICES.md` and `../LICENSE_PENDING.md`.

The additional `light.md` file in this directory is **not** derived from
`local-coder`. It is the restricted primary agent used by `bin/mode-a` and is
included here so its effective permissions are inspectable in the showcase. It
is showcase-specific configuration.

| File | Mode | Can edit | Can run shell | Notes |
|------|------|----------|---------------|-------|
| `orchestrator.md` | primary | no | no | User-facing; classifies work, delegates, owns retries and completion. |
| `explorer.md` | subagent | no | no | Read-only discovery and context compression. |
| `planner.md` | subagent | no | no | Read-only implementation planning. |
| `researcher.md` | subagent | no | no | Read-only web research (`webfetch`/`websearch` allowed). |
| `coder.md` | subagent | **yes** | ask (allowlist) | The only role that edits; `git push` denied. |
| `verifier.md` | subagent | no | ask (allowlist) | Independent validation; cannot edit. |
| `reviewer.md` | subagent | no | read-only git | Independent review after verification passes. |
| `light.md` | primary | **yes** | allow (denylist) | Restricted Mode A host agent; no delegation, no `execute`, no `sudo`, no git history mutation. |

## Workflows

The orchestrator prompt defines four adaptive workflows and instructs it to pick
the least costly one:

```
Trivial:  Coder → Verifier
Standard: Explorer → Coder → Verifier
Complex:  Explorer → Planner → Coder → Verifier → Reviewer
Domain:   Explorer + Researcher → Planner → Coder → Verifier → Reviewer
```

## Task contract and verification

The orchestrator is instructed to build a versioned JSON "task contract" and
repeat it unchanged in every coder and verifier call. The verifier must return
an unambiguous `STATUS: PASS` or `FAIL` with repository evidence; the
orchestrator treats a coder's success claim only as a hint and is limited to two
verification-repair attempts and one review-remediation pass. This is the
"agent claims are not evidence" completion rule.

## Model configuration

The `model:` values in these files are now a documented example
(`ollama/gpt-oss:20b`), not a claim that this model is installed or tested on
the reader's machine. They are OpenCode `provider/model` strings; replace them
with any model your own OpenCode/Ollama setup provides, for example:

```text
model: ollama/qwen3:8b
```

Selection guidance:

- Run `ollama list` (or `opencode models`) to see what is actually available.
- Keep the `ollama/` provider prefix unless your OpenCode configuration uses a
  different provider name.
- Context limits are not set in these agent files; the effective limits come
  from your OpenCode provider configuration (compare `sandbox/opencode.json` for
  an example). Do not assume the example model's limits are universally correct.
- The sandbox configuration (`sandbox/opencode.json`) uses the same example
  model family and the same provider; keep them consistent if you change one.
- These prompt bodies remain derived from `gmarland/local-coder`; changing the
  model line does not make them independently authored.
- `light.md` has no `model:` field and therefore uses the caller's OpenCode
  default (or the `--model` passed by `bin/mode-a`). Its permission block, not
  its model, is the reason it exists.

## Relationship to the orchestrator

These role definitions drive OpenCode's own subagent mechanism. The
`orchestrator/` Rust harness is a separate, model-agnostic planner → executor →
reviewer loop that does not depend on them. Both are included because they
demonstrate two different orchestration approaches: prompt/config-driven role
delegation, and code-owned deterministic loop state.
