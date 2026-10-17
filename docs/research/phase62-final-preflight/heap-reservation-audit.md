> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: FAILED / SUPERSEDED / DO NOT FLASH.

# Heap / reservation — corrected image

Native constructor entry0805B958 branches through08075000 to initializer0806BD00 **before** original constructors. With scatter-initialized limit20044E58/cursor20006A58, init clears all12 bytes before aDMB and publishes limit20044D70. Cursor is unchanged by reservation. The high232-byte reservation consists of existing220-byte MasterFX plus12 diagnostic bytes. Native constructors then advance cursor to20007750; modeled margin at that point is251424 bytes, not8 bytes.

**PROVEN provenance of20044D68:** it comes from public/reference running-RAM dump`ram_dump_firmware_0x08037988.bin`, SHA-256`26a29670c0c1918217b7eadf8f89fe6df97994d3cc6e1c0ed65ac522e161094c`, at dump offset2B48. It is the old running fixture's cursor and leaves8 bytes toD70. It is **not** a measurement of this unit's fresh boot and is not produced by current native startup. The new partial startup frontier reaches cursor2000FE58 with limit20044D70:216856 modeled bytes remain, at an incomplete-boot boundary. Full final-boot/postboot demand is not qualified.

Native allocator1D7D0→1D7D8 rounds to4-byte alignment, compares new cursor to the live limit and stores only when it fits. The native exhaustion branch isBKPT at0801D7F4, not a gracefulNULL allocator return. New boundary tests accept two4-byte allocations up toS, reject4 bytes atS and reject9(round12) bytes with8 remaining, and preserve the record/cursor on those failures.

For ordinary nonoverflow requests through this allocator, allocations ending beyondS are rejected; the record cannot be allocated by those tested paths. This is **not** exhaustive proof of all postboot call sizes, integer-overflow inputs, arbitrary pointer writes or hardware headroom. Physical RAM/stack margin remains UNKNOWN. No complete postboot heap proof is manufactured while continuity fails earlier.

The7 reservation-negative tests and corrected28-case regression remain qualified in their narrow scope and were **not rerun** by this continuation. Evidence: heap-reset-tests.json (local-only reference: `builds/phase62-final-preflight/heap-reset-tests.json`; not distributed), [heap_reset_tests.py](<../../../builds/phase62-final-preflight/heap_reset_tests.py>), continuity-status.json (local-only reference: `builds/phase62-final-preflight/continuity-status.json`; not distributed), corrected-reservation-tests.json (local-only reference: `builds/phase62-final-preflight/corrected-reservation-tests.json`; not distributed).
