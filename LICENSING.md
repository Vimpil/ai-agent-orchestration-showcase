# Licensing

This repository is published as a portfolio showcase. It does **not** ship a
blanket root `LICENSE`. Licensing is scoped per component; see the sections
below.

## Approved policy direction

The owner has approved a **Portfolio-Friendly Source-Available Policy with
Permission-Controlled Commercial Use**. That policy is a specification and
decision record, not an operative license: it does not grant reuse rights by
itself, and no custom license text has been drafted or published yet.

Summary of the approved direction (see the owner decision record for full text):

- Public source inspection is allowed.
- Purpose-limited technical evaluation is allowed for individuals and
  organizations, including for-profit organizations, within the stated limits.
- Non-commercial research and education are allowed.
- Private non-commercial personal inspection, execution, experimentation,
  modification, and private forks are allowed for confirmed original showcase
  components.
- Commercial use of confirmed original showcase-specific components requires
  prior individual permission.
- Redistribution (including private redistribution) is conditional: preserve
  notices and licenses, identify modifications, do not expand rights, do not
  transfer commercial permissions, no mandatory public fork or source
  publication.
- No copyleft-like or public/recipient/ongoing source-availability obligation
  is imposed.
- Upstream third-party licenses (including MIT) remain in force and are not
  narrowed by the custom policy.

## Component-level status

| Component | License / status |
|---|---|
| `orchestrator/` (where provenance is verified) | MIT — upstream `softwarewrighter/local-llm-loop`; `orchestrator/LICENSE` preserved byte-for-byte |
| `agents/orchestrator.md`, `explorer.md`, `planner.md`, `researcher.md`, `coder.md`, `verifier.md`, `reviewer.md` | MIT — upstream `gmarland/local-coder`; notices in `THIRD_PARTY_NOTICES.md` |
| `agents/light.md`, `agents/README.md` | No reuse license granted; pending provenance confirmation |
| `bin/`, `sandbox/`, `docs/`, `examples/` (excluding recorded artifacts), root files | No reuse license granted; pending owner confirmation of rights |
| `examples/sample-workflow/recorded-run/*.json` | **Excluded** from all redistributed copies (public and private) until ownership and applicable rights are verified; no custom reuse grant |
| `THIRD_PARTY_NOTICES.md`, `PUBLICATION_MANIFEST.md`, `RELEASE_READINESS.md`, `LICENSE_PENDING.md`, and this file | Project documentation; excluded from the custom software grant; not public domain |

## Third-party notices

See `THIRD_PARTY_NOTICES.md` and `orchestrator/LICENSE`.

## What is still pending (not yet a license)

- Exact file-level scope of the custom (Class C) components: no file has been
  confirmed yet; none is covered by a custom license.
- Public contact/channel for commercial permission requests.
- Qualified legal review of any final custom license text before publication.

Until these are resolved and a license text is published, components marked
"no reuse license granted" above remain all rights reserved, subject only to the
third-party licenses that already apply. Repository publication does not grant
reuse rights.

This file is documentation. It is not a license and does not grant rights.
