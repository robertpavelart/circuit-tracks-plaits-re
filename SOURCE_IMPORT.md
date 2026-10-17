# Current reviewed source import —17 October2026

This branch contains the current project-authored, redistributable subset of the local CIRCUIT workspace, synchronized onto the existing `docs/final-prehardware-review` branch. It is not a bulk copy of the local research tree.

Included: current tools, authored emulator harnesses/instrumentation/tests, Plaits PoCs/integration work, notes and current documentation. Some project-authored offline scripts historically live under `builds/phase*/` and `builds/final-*/`; only individually reviewed source files are tracked there. Their original paths are preserved so source path calculations are not silently redesigned. Generated output and private inputs remain ignored. Nothing in those source folders is a firmware image or dump.

Selected authored reports are published under `docs/research/<original phase>/`; locked-package operational text/hash metadata is under `docs/operations/`. Markdown links are portable. References to omitted private/generated evidence are rendered as local-only references rather than broken download links. Firmware-derived disassembly blocks, raw job/output transcripts, project inventories and other opaque payloads are not distributed. The original local evidence is unchanged.

These research scripts require authorized local firmware/reference inputs and, where applicable, locally generated checkpoints. Their publication is not a claim that all replay inputs or every historical result can be reproduced from this repository alone. Do not run builders or live tools as a documentation check.

The current candidate is the unchanged Phase63 N63DEV temporary NOR diagnostic, NOT Plaits firmware. No candidate image is included. Phase67 scoped model PASS and final USB joint-path PASS remain limited to their evidence. Operational preflight and post-READY allocation census remain UNQUALIFIED. Hardware, MIDI and transmission are not authorized by this sync; live host/uploader remain locked.

Fetched upstream trees are not vendored. Provenance/manifests and required derivative licenses remain. See `docs/REPOSITORY_POLICY.md`, `docs/CURRENT_STATUS.md`, `docs/NEXT_STEPS.md`, `docs/DOCUMENTATION_INDEX.md` and `licenses/README.md`.

The old bulk-publish helpers were removed because they targeted main. Future updates require a reviewed safe-file allowlist and the explicit target branch; no main merge/push occurred in this sync.
