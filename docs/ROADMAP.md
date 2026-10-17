# Roadmap

## Current position

The project is at the **final pre-hardware review / operational-release preparation** boundary.

The current artifact is a temporary NOR diagnostic firmware, not a Plaits firmware.

Current candidate:

- Phase63 `N63DEV`
- reviewed through Phase67
- Phase67 scoped model preflight: **PASS**
- USB Storage joint path: **PASS**
- operational preflight: **UNQUALIFIED**
- post-READY allocation census: **UNQUALIFIED**

The remaining offline uncertainty is indirect/virtual post-READY allocation reachability. No allocation larger than the modeled 8-byte heap gap has been found, but its absence is not proven.

## Completed research milestones

- firmware container / SYX reverse engineering
- exact SYX ↔ BIN round-trip
- DSP payload extraction and mapping
- DSP56300 emulator instrumentation
- bounded stock execution
- Plaits-derived fixed-point renderer work
- stock DSP seam mapping
- update-protocol reconstruction
- application/bootloader range separation
- diagnostic NOR/QSPI read design
- geometry snapshot and authorization protocol
- reservation/publication defect closure
- SD/NOR geometry-lifetime defect closure
- explicit status-protocol closure
- DMA ownership/lifetime fence closure
- late-success failure-state closure
- SPI2 startup model closure
- SHI coefficient-transfer model closure
- USB controller safety classification
- bounded diagnostic-path model closure through capture entry
- focused USB Storage/diagnostic concurrency closure
- final indirect callback/allocation census to the current proof boundary
- physical recovery-mode entry/exit rehearsal

## Current blocker / evidence dependency

Authentic `$82000` coefficient data has not yet been captured from hardware.

Until that evidence exists:

- reclaim of `P:$0282-$0386` is not finally qualified;
- final safe P/X/Y budget remains **UNKNOWN**;
- full Plaits hardware integration remains blocked.

## Immediate next step

Do not start another open-ended offline reverse-engineering phase unless new evidence justifies it.

Next sequence:

1. prepare a separately reviewed operational host/uploader release;
2. verify all hashes on the actual sending machine;
3. apply the prepared Windows/removable-storage policy;
4. perform a controlled hardware test;
5. issue geometry query first;
6. authorize only after valid host-side geometry approval;
7. perform exactly one fixed capture;
8. restore B1.3 on success;
9. on capture failure, power off fully and do not retry within the failed session.

## After authentic capture

If the capture succeeds and validates the expected coefficient data:

1. re-evaluate the final DSP P/X/Y memory budget;
2. decide whether `P:$0282-$0386` can be reclaimed safely;
3. bind the Plaits model/resource plan to authentic hardware evidence;
4. resume Plaits integration around the four-track target architecture;
5. preserve rollback and bootloader isolation throughout.

## Long-term architecture target

- four melodic Plaits tracks;
- default mono;
- `MAX_TRACKS_PER_MODEL = 2`;
- `MAX_POLY_TRACKS = 2` globally;
- engine-specific polyphony limits;
- shared model code with independent per-track state;
- retain the useful Circuit workflow where feasible.

The old one-mono-VariableSaw-first-PoC roadmap is historical and no longer describes the active project direction.
