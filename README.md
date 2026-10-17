# Circuit Tracks Plaits RE

Experimental reverse-engineering and DSP integration research toward running Mutable Instruments Plaits-derived synthesis engines inside a Novation Circuit Tracks.

> **Status — October 2026**
>
> - Long-term goal: four melodic Plaits tracks inside Circuit Tracks.
> - Current artifact: temporary NOR diagnostic firmware, not Plaits firmware.
> - Current candidate: Phase63 `N63DEV`, reviewed through Phase67.
> - Hardware-tested candidate: **NO**.
> - Phase67 scoped model preflight: **PASS**.
> - USB Storage joint path: **PASS**.
> - Operational preflight: **UNQUALIFIED**.
> - Remaining offline uncertainty: post-READY indirect allocation reachability with an 8-byte modeled heap gap.
> - Recovery: bootloader entry/exit physically rehearsed; recovery flashing is not yet proven.
> - Operational host/uploader: intentionally locked.
> - Next step: separately reviewed operational-release preparation, then a controlled hardware test.

## Long-term goal

The project has moved beyond the original single-voice VariableSaw proof of concept.

The current target architecture is:

- four melodic Plaits tracks;
- default mono operation;
- `MAX_TRACKS_PER_MODEL = 2`;
- `MAX_POLY_TRACKS = 2` globally;
- engine-specific polyphony limits;
- shared model code with independent per-track state;
- retain useful Circuit workflow, sequencer, drums, mixer, effects and rollback behavior where feasible.

The current diagnostic firmware does **not** contain Plaits.

## Current diagnostic candidate

`circuittracks-nor-defect-closure-development.syx`

- size: 569229 bytes
- SHA-256: `9b420521a366c65c13fb871778fdbab612ca126cbb4ad60d0fd5bc12ecd253da`
- CRC-32/MPEG-2: `1BB21302`
- marker: `N63DEV`

Decoded BIN:

- size: 413952 bytes
- SHA-256: `edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9`
- application range: `0x08010000 .. 0x08075100`

Phase61 and Phase62 are failed/superseded and are not current candidates.

## Why this diagnostic exists

The immediate research goal is to obtain authentic evidence from NOR/QSPI address `$82000`.

Until that evidence exists:

- reclaim of `P:$0282-$0386` is not finally qualified;
- final safe P/X/Y budget remains **UNKNOWN**;
- full Plaits hardware integration remains blocked.

## Current offline status

Earlier concrete defects were fixed, including:

- reservation/publication logic;
- SD/NOR geometry invalidation;
- status ambiguity;
- DMA lifetime/fence handling;
- late-success failure-state handling;
- focused USB Storage/diagnostic concurrency.

The focused USB joint-path closure is **PASS**.

The stronger operational preflight remains **UNQUALIFIED** because static analysis cannot exhaustively bind every post-READY indirect/virtual callback target.

No post-READY allocation larger than the remaining 8-byte modeled heap gap has been found, but its absence is not proven.

## Recovery status

Physically rehearsed on the user's unit:

- recovery/bootloader mode can be entered;
- recovery mode can be exited by full power cycle;
- B1.3 boots normally afterward.

Not yet proven:

- recovery-mode host enumeration;
- uploader handshake in recovery;
- actual recovery flashing;
- recovery from a non-booting diagnostic candidate;
- guaranteed recovery.

No concrete bootloader-loss path has been identified in the current candidate. Candidate-specific physical recovery remains a hardware-only unknown.

## Operational tools

The frozen host and uploader remain intentionally locked. They are not an enabled operational release.

Do not treat the presence of the diagnostic candidate as authorization to use the locked tools.

## Repository policy

Do not commit proprietary Novation firmware, extracted DSP payloads, vendor PDFs, user projects, sample packs, or device dumps.

See `docs/REPOSITORY_POLICY.md`.

## Source layout

- `tools/` — firmware/DSP analysis and validation utilities
- `emulator/` — DSP56300 replay harnesses and tests
- `plaits/` — Plaits-derived PoC and integration work
- `notes/` — detailed research history and superseded branches
- `docs/` — current project state and research documentation

## Hardware rule

No opening, soldering, multimeter probing, JTAG/OnCE/SWD, or internal access.

Normal external interfaces only.

## Disclaimer

Unofficial research project. Not affiliated with or endorsed by Novation, Focusrite, Mutable Instruments, NXP, or upstream community projects.
