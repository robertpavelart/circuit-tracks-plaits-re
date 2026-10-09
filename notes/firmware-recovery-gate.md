# Phase20C — firmware recovery gate

2026-10-07. **UNRESOLVED. FLASHING NOT JUSTIFIED.** Documentation/design only.
No firmware-update software launched, device command, debug session or recovery
experiment. Original files and reproducible encoding are preserved.

**VERIFIED:** original SYX/BIN hashes and codec round-trip were established in
the baseline; current guards confirm those files unchanged. This demonstrates
file integrity and encoder behavior. It does not demonstrate recovery of a unit
whose DSP boot or ARM/DSP handshake is broken.

Before any future flash, prove separately:

- The official update-entry path and bootloader below08010000, including whether
  entry/recovery works independently of functioning DSP code or normal startup.
- Recovery when a DSP fails boot, loops indefinitely, corrupts its protocol,
  or causes the ARM uploader/initialization handshake to wait forever.
- Actual unit identity/flash capacity, partition/protection layout, accepted
  image size/alignment, integrity/version checks and changed-stream placement.
- Official updater acceptance of the larger container and behavior on interrupted
  transfer or power failure, without inventing a boot pin or debugger route.
- A supported known-good restoration/rollback route, with the exact original
  official image preserved and a procedure whose prerequisites remain available
  after the specific possible patch failure.
- Proven code and RAM lifetimes, wrapper/IRQ/stack behavior, pitch/amplitude and
  complete deadline headroom, followed by separate authorization for a concrete
  reviewable future test artifact.

No claim that backup, CRC regeneration, stock flash capacity or a successful
offline renderer test satisfies these gates. Live natural context removes the
checkpoint-reconstruction requirement; it does not remove recovery risk.
No flash-ready firmware may be produced in this phase. recovery-gate.json records
the same independent refusal. Hardware flash readiness remains **NO** even if
offline construction becomes justified in a later phase.
