# Source snapshot

This repository contains the reviewed project-authored source snapshot originally imported on 2026-10-09 and subsequently updated with current documentation.

Included source areas:

- `tools/` — reverse-engineering and validation utilities
- `emulator/` — harnesses, stock replay work, and tests
- `plaits/` — Plaits-derived proof-of-concept and integration work
- `notes/` — research log and historical/superseded branches
- `docs/` — current project state and safety/roadmap documentation

Upstream dependency source trees are intentionally **not vendored**. Only provenance/manifests are kept under the corresponding `upstream/` directories.

Proprietary Novation firmware, extracted DSP payloads, build outputs, device dumps, vendor PDFs, samples, and local caches are intentionally excluded.

Original local working tree used during research:

`C:\Proj SSD\CODEX\CIRCUIT`

This file records source-import status only.

The current project direction is no longer the original single-voice VariableSaw first PoC. The active target is a four-track Plaits architecture, while the immediate project step is a controlled diagnostic hardware test after a separately reviewed operational release.

Current authoritative repository status is documented in:

- `README.md`
- `docs/STATUS.md`
- `docs/ROADMAP.md`
- `docs/SAFETY.md`
- `docs/ARCHITECTURE.md`
