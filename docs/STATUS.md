# Project Status

## Current stage

**Final pre-hardware review / operational-release preparation.**

The current candidate is the unchanged Phase63 diagnostic firmware reviewed through Phase67.

The current firmware is **not** Plaits firmware.

No hardware installation of the current diagnostic candidate has occurred.

## Current candidate identity

`circuittracks-nor-defect-closure-development.syx`

- 569229 bytes
- SHA-256: `9b420521a366c65c13fb871778fdbab612ca126cbb4ad60d0fd5bc12ecd253da`
- CRC-32/MPEG-2: `1BB21302`
- marker: `N63DEV`

BIN:

`circuittracks-nor-defect-closure-development.bin`

- 413952 bytes
- SHA-256: `edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9`
- application: `0x08010000 .. 0x08075100`

Phase61 and Phase62 are **FAILED / SUPERSEDED**.

## Current preflight status

- Phase67 scoped model preflight: **PASS**
- USB Storage joint path: **PASS**
- operational preflight: **UNQUALIFIED**
- post-READY allocation census: **UNQUALIFIED**

The operational result is intentionally stronger than the scoped Phase67 result.

## Closed concrete defects

The following concrete issues are considered closed in the current candidate:

- reservation/publication bug;
- SD/NOR geometry invalidation;
- status ambiguity;
- DMA lifetime / stack-buffer hazard;
- late success overwriting failure/quarantine;
- focused USB Storage / diagnostic concurrency defect.

The focused USB joint-path closure is **PASS**.

## Remaining software uncertainty

The post-READY all-root allocation census cannot exhaustively bind every indirect or virtual callback target.

Known unresolved proof boundaries include indirect call sites around:

- `0x0803C91C`
- `0x0803C9C4`

No post-READY allocation larger than the remaining modeled 8-byte heap gap has been proven.

Its absence is also not proven.

Allocator rejection reaches BKPT in the isolated model. Physical exception routing remains **UNKNOWN**.

This is the primary accepted residual software uncertainty.

## Recovery

### PROVEN on physical unit

- recovery/bootloader mode can be entered;
- recovery mode can be exited by full power cycle;
- B1.3 boots normally afterward;
- no firmware was transmitted during the rehearsal.

### NOT PROVEN

- recovery-mode host enumeration;
- uploader handshake in recovery;
- actual recovery flashing of B1.3;
- actual recovery flashing of stock 4486;
- recovery from a non-booting diagnostic candidate;
- guaranteed recovery.

No concrete path to bootloader loss has been identified.

The bootloader remains outside the modeled application erase/program range.

Candidate-specific physical recovery is therefore **HARDWARE-ONLY UNKNOWN**.

## User risk decision

The user accepts the possibility of a soft brick and the possibility that recovery may be required.

This does not change any UNKNOWN evidence into PROVEN evidence.

## H4

H4 remains **FAIL**.

A failed raw-capture session is treated as non-retriable within that session.

## Operational tools

Host:

- `live_host.py`
- version `1.0.0-phase68-locked`
- SHA-256 `9b8a7d3d088cdffe21257824cb16db602659d678d240e7266f468e92c3ae9dc9`
- `live_enabled=false`

Uploader:

- `ct_uploader-final-offline-locked.html`
- SHA-256 `bf1ef00dbca9c3715932235249fcc8ba0a71d6f2f989c047aa8caf66b85e17a5`
- `PREFLIGHT_QUALIFIED=false`

The locks are intentional.

A separately reviewed operational release is required before hardware use.

## Rollback artifacts

B1.3:

- SHA-256 `6f07376b5983a5e0350d4883ae9ed57a69bc735320afde9f43ca75017b8e8736`

Stock 4486:

- SHA-256 `bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd`

The saved 4486 artifact is not independently authenticated against a fresh Novation-origin acquisition.

## Plaits status

Current long-term design:

- four melodic Plaits tracks;
- default mono;
- `MAX_TRACKS_PER_MODEL = 2`;
- `MAX_POLY_TRACKS = 2` globally;
- engine-specific polyphony limits;
- shared model code with independent per-track state.

The current diagnostic candidate contains **no Plaits engine**.

Authentic `$82000` coefficient data has not yet been captured.

Therefore:

- reclaim of `P:$0282-$0386` is not finally qualified;
- final safe P/X/Y budget remains **UNKNOWN**;
- full Plaits hardware integration remains blocked on diagnostic evidence.

## Next step

The next project step is a separately reviewed operational-release preparation followed by the controlled hardware test.

Do not reopen a broad offline reverse-engineering phase unless new evidence justifies it.

## Hardware rule

No opening, soldering, multimeter probing, JTAG/OnCE/SWD, or internal access.

Normal external interfaces only.
