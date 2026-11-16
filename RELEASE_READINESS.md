# Release readiness

## Final verdict

**PUBLISHED — DOCUMENTED LIMITATIONS**

This is a small, honest, experimental portfolio project. The initial public
release has been published to GitHub. The disclosure, provenance, and
verification-evidence issues found in preparation were corrected or documented.
It is not production-ready and must not be described as a verified security
boundary.

## BLOCKERS

None of the disclosure, path, secret, or verification-evidence kind remain
after this review. No file was found to contain credentials, private URLs,
internal hostnames, customer/employer information, or other sensitive
material. Generated Rust build artifacts under `orchestrator/target/` were
present at the start of the final hygiene check and have been removed (see
Completed cleanup); no build artifacts remain now.

## WARNINGS

- **No root license chosen.** `orchestrator/` is MIT (Copyright (c) 2026
  Michael A. Wright); all other components are unlicensed. The project is
  therefore not ready for unrestricted public reuse until the owner chooses a
  license or scopes per-component licensing. See `LICENSE_PENDING.md`.
- **Sandbox unverified.** `bin/autonomous` and the `sandbox/` primitives were
  inspected but not executed in this environment. They are an experimental
  boundary, not a verified containment system. Residual TOCTOU races are
  inherited and documented.
- **Environment-specific defaults remain.** Machine-specific model aliases were
  replaced with documented example model names in `agents/*.md`, `bin/mode-b`,
  and `bin/mode-c`; `bin/mode-a` still defaults to `ollama/granite4:3b`. These
  are examples only and must be changed to models available in the reader's own
  OpenCode/Ollama setup. Toolchain/model defaults in `bin/autonomous` are also
  environment-specific.
- **Host launchers are not sandboxed.** `bin/mode-a`, `bin/mode-b`, and
  `bin/mode-c` run OpenCode directly on the host.
- **Rust loop reviewer is not an independent repository verifier.** It judges
  the executor's reported result and the remaining plan.
- **Recorded run is evidence of the harness's own reports**, not an independent
  repository verification. It was not re-executed.

## Completed cleanup in this review

- Sanitized `PUBLICATION_MANIFEST.md`: removed the local absolute source path
  and machine-specific references (a local username/absolute path pattern,
  "local subset", temporary test-directory path); replaced with generic
  provenance wording.
- Removed the empty, unused `licenses/` directory.
- Added this `RELEASE_READINESS.md`.
- Updated the manifest file inventory to account for `RELEASE_READINESS.md`
  (55 tracked files in the published release).
- Verified JSON validity of `sandbox/opencode.json`. The eight recorded workflow
  artifacts were excluded from this release (Class X1) and are not present.
- Verified relative Markdown links resolve.
- Removed `orchestrator/target/` (generated Rust build artifacts and build
  metadata, ~188 MB) during the final hygiene check. Confirmed no other build
  artifacts, caches, logs, or symlinks remain, and no private absolute paths
  remain.
- Preserved `orchestrator/LICENSE` (MIT) and all component notices.
- Corrected a stale shell comment in `bin/mode-c` (state root wording) without
  changing executable logic.
- Did not modify the Rust implementation, sandbox code, or recorded evidence.

## Remaining user decisions

1. Confirm the exact file-level Class C scope (no file is confirmed yet). See
   `LICENSING.md`.
2. Resolve the public contact/channel for commercial permission requests. No
   address or identity is invented.
3. Confirm attribution/copyright notice for the MIT component.
3. Confirm the example model defaults (`ollama/gpt-oss:20b`,
   `ollama/granite4:3b`) and context limits are acceptable as documentation-only
   examples.
4. Confirm the adapted `sandbox/opencode.json` (sudo allowlist removed) matches
   the intended posture.
5. Confirm the Mode A agent fallback (`light` by default, overridable via
   `MODE_A_AGENT`) and the documented `envelope` dependency for Mode C are
   acceptable. The `light` agent must be installed into the user's OpenCode
   configuration for the default to work; `bin/mode-a` fails clearly if it is
   missing.
5. Confirm the recorded run contains no sensitive values (reviewed; it is a
   Python `greet` exercise).

## Licensing policy status
A licensing policy has been specified and approved in principle
(Portfolio-Friendly Source-Available Policy with Permission-Controlled
Commercial Use). It is not yet implemented as operative license text. The
custom license applies only to explicitly confirmed components, and no file has
been confirmed yet. Recorded workflow artifacts (`recorded-run/*.json`) are
excluded from all redistributed copies until ownership and applicable rights
are verified. See `LICENSING.md` and `LICENSE_PENDING.md`.

## Post-publication notes

The initial public release is published. The following are optional
future-work items, not blockers for this release:

1. If a custom license is pursued later: confirm Class C scope, resolve the
   commercial permission contact/channel, and obtain qualified legal review.
2. Re-run the low-cost checks (JSON validity, relative links, private-path
   scan) after any further edits.
3. Review `README.md`, `LICENSING.md`, and `PUBLICATION_MANIFEST.md` for
   accuracy against the file set.

## File count

55 files in the showcase directory (61 original, plus `LICENSING.md` and
`.gitignore`, minus 8 excluded recorded workflow artifacts).
