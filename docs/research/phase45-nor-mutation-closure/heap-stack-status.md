> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Strongest offline heap/stack status

**PROVEN scoped:** correction from Phase43→Phase44 adds no allocations, data records or image length. It only changes the marker, branch and terminal commit in existing P/ARM flash slack. The diagnostic inherits a12-byte latch at20044D70–20044D7B; existing220-byte Master FX state remains20044D7C–20044E57.

| Item | Result / evidence limit |
|---|---|
| Startup allocator demand/call delta |0 relative to exact SC35D8; newly reachable pre-command wrappers do not call allocator |
| Heap capacity delta |−12 bytes, not zero RAM footprint |
| Running-RAM fixture cursor/limit |20044D68 /20044D70;8 modeled bytes remaining |
| Reservation refusal | If cursor exceeds20044D70 or expected limit/state contract fails, getter returns0; admission rejects without diagnostic Storage read |
| Post-boot allocations | Inherited dynamic allocations remain; complete site/predicate/high-water closure across restore/file/USB activity is **UNKNOWN** |
| Main minimum modeled margin |2460 bytes above the selected lower guard across saved25 native cases |
| Storage minimum modeled margin |1068 bytes above the selected lower guard across saved25 native cases |
| IRQ minimum modeled margin |3800 bytes in that separately bounded exception fixture; not a physical nesting theorem |
| Actual fresh-boot headroom |**UNKNOWN** on hardware |

The native tests include boundary cursor values, retained-state reinitialization and error ownership. They do not prove every stock allocation-failure path safe, nor that all possible later allocations fit in the remaining eight fixture bytes. The raw64-byte buffer is lent from the padded parser allocation, not allocated as a new512-byte heap object. It must remain owned while a failed DMA/Storage operation remains active.

Main/Storage margins are measured in the exact selected running-RAM task/stack fixtures and supported instruction paths. They do not cover every FPU exception frame, every nesting depth, all project/content jobs or full cold boot. The PRIMASK fragment adds no stack frame or calls. Instruction masking length is bounded separately in the independent review.

**H4 = FAIL remains:** TEF/missing completion has no qualified bounded in-session unwind. Post-send failure means discard partial output, no retry/second request or forced release, full power cycle. Host pre-send failures send no request and need no power cycle for that unsent attempt.

Evidence: original heap preflight (local-only reference: `builds/phase43-hardware-test-candidate/heap-preflight.json`; not distributed), corrected native cases (local-only reference: `builds/phase44-preflash-redteam-closure/native-results.json`; not distributed), resume margin extraction (local-only reference: `builds/phase45-nor-mutation-closure/resume-evidence-status.json`; not distributed), [independent atomicity review](<atomicity-patch-review.md>).
