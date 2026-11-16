# License status: pending implementation

This project has **no operative license yet**. No license file is provided at
the repository root, and no license is invented here. Publicly visible source
without an explicit license does **not** grant general reuse permissions. All
rights remain with the original authors unless and until a license is applied.

A licensing policy has been specified and approved in principle (see
`LICENSING.md`): **Portfolio-Friendly Source-Available Policy with
Permission-Controlled Commercial Use**. That policy is a specification and
decision record, not an operative license. It has not been implemented as
license text, and it does not grant reuse rights by itself.

The owner has confirmed authorship and the right to publish the Class P
showcase files and adaptations in this portfolio. That confirmation covers
publication only; it does not grant additional reuse rights.

## Component licenses

| Component | License | Notice |
|-----------|---------|--------|
| `orchestrator/` (the `local-llm-loop` Rust crate) | MIT | Upstream: `softwarewrighter/local-llm-loop`. Copyright (c) 2026 Michael A. Wright. The original `LICENSE` is preserved at `orchestrator/LICENSE` and its terms continue to apply to that component. |
| `agents/*.md` (seven prompt bodies) | MIT (upstream) | Upstream: `gmarland/local-coder`. Copyright (c) 2026 local-coder contributors. Derived content; keep the upstream notice. See `THIRD_PARTY_NOTICES.md`. |
| `sandbox/*.py`, `bin/*`, `docs/`, top-level `README.md`, `THIRD_PARTY_NOTICES.md`, `PUBLICATION_MANIFEST.md`, `RELEASE_READINESS.md`, `LICENSE_PENDING.md`, `LICENSING.md` | **No license in the source workspace** | These files were copied/adapted from a private workspace that had no top-level license. The MIT licenses above do not automatically cover them. |
| `examples/sample-workflow/recorded-run/*.json` | **No license in the source workspace** | Recorded artifacts of the orchestrator; excluded from all redistributed copies until ownership and applicable rights are verified. No custom reuse grant. |

## What must happen before a custom license is implemented

1. Confirm the exact file-level Class C scope (no file is confirmed yet).
2. Resolve the public contact/channel for commercial permission requests.
3. Obtain qualified legal review of the final custom license text.
4. Prepare and publish the custom license text (`LICENSE-SHOWCASE` or equivalent)
   applying only to explicitly confirmed components, with an explicit closed
   enumeration.
5. Update this file and `LICENSING.md` to point to the implemented license.

Until then, treat the unlicensed components as **all rights reserved**, subject
only to the third-party licenses that already apply. Do not copy or redistribute
this repository's contents outside the terms of the component licenses above.
Recorded workflow artifacts (`recorded-run/*.json`) are excluded from all
redistributed copies, including private redistribution, until ownership and
applicable rights are verified.
