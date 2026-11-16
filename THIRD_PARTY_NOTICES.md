# Third-party notices

This showcase contains components derived from third-party projects. Those
components retain their own licenses and copyright notices; they are not covered
by any license that may later be chosen for the rest of this repository.

## `orchestrator/` — Rust orchestrator

- Upstream project: `softwarewrighter/local-llm-loop`
  (https://github.com/softwarewrighter/local-llm-loop)
- License: MIT
- Copyright: Copyright (c) 2026 Michael A. Wright
- The upstream `LICENSE` is preserved byte-for-byte at `orchestrator/LICENSE`.
- Local changes are limited to compatibility adaptations (for example removed
  private links/paths and genericised script defaults). They do not replace
  upstream authorship or copyright.

## `agents/*.md` — OpenCode specialist role definitions

- Upstream project: `gmarland/local-coder`
  (https://github.com/gmarland/local-coder)
- License: MIT
- Copyright: Copyright (c) 2026 local-coder contributors
- The seven prompt bodies derived from that project are:
  `agents/orchestrator.md`, `agents/explorer.md`, `agents/planner.md`,
  `agents/researcher.md`, `agents/coder.md`, `agents/verifier.md`, and
  `agents/reviewer.md`.
- They are copied here with their role interfaces and permission blocks
  intact, with only the machine-specific `model:` alias changed to a documented
  example value.
- They are not presented as original work by the showcase owner.
- `agents/light.md` is **not** derived from this upstream project; it is a
  showcase-specific restricted agent for `bin/mode-a` and is not covered by the
  upstream MIT license above.
- The complete applicable MIT license text from the verified upstream source
  (`src/local-coder/LICENSE`, copyright holder and year confirmed from that
  file) is reproduced below.

### Complete MIT license text (upstream `gmarland/local-coder`)

```
MIT License

Copyright (c) 2026 local-coder contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Showcase-specific components

The remaining showcase material (`sandbox/`, `bin/`, `docs/`, `examples/`,
root-level files, and any showcase-specific configuration) is not covered by the
MIT licenses above. No root reuse license is granted for it; see `LICENSING.md`
and `LICENSE_PENDING.md`.

Recorded workflow artifacts under `examples/sample-workflow/recorded-run/` are
excluded from all redistributed copies (public and private) until ownership and
applicable rights are verified. No custom reuse grant is made for them.
