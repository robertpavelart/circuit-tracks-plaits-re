# Source snapshot

This repository now contains the reviewed project-authored source snapshot supplied on 2026-10-09.

Included:

- `tools/` — reverse-engineering and validation utilities
- `emulator/` — harnesses, stock replay work, and tests
- `plaits/poc/` — VariableSaw / Plaits-derived proof-of-concept work
- `plaits/seam/` — stock seam adapters and validation
- `notes/` — research log and phase notes

Upstream dependency source trees are intentionally **not vendored**. Only provenance/manifests are kept under the corresponding `upstream/` directories.

Proprietary Novation firmware, extracted DSP payloads, build outputs, device dumps, vendor PDFs, samples, and local caches are intentionally excluded.

Original local working tree used during research:

`C:\Proj SSD\CODEX\CIRCUIT`

This file records source-import status only; it is not a claim that every historical research branch is still active. Current project direction is documented in `docs/STATUS.md`, `docs/ROADMAP.md`, and `docs/SAFETY.md`.
