> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: FAILED / SUPERSEDED / DO NOT FLASH.

# Reset / power-cycle state

Four new native tests start with zero, garbage, FAILED15 or SUCCESS14 high-SRAM records, then execute the corrected application's real scatter initializer and constructor hook. Scatter resets allocator cursor/limit to20006A58/20044E58 but leaves the high record bytes temporarily intact. Constructor init then zeroes all12 bytes and reserves the region; geometry validity and authorization are false in all cases.

The same reset entry/initialization code is used for normal cold entry, software-reset entry and watchdog-reset entry; these tests model code execution, **not** electrical reset causes or peripheral reset effects. Full power removal is represented by unknown initial SRAM followed by the same explicit initialization, not by assuming SRAM cells retain or clear a particular value.

Thus FAILED/SUCCESS do **not** survive completed normal scatter+constructor initialization. A warm reset can rearm the software lifecycle and eventually permit another first-epoch capture. The record itself is not a power-cycle detector or a persistent retry lock. Existing durable host markers must not be deleted merely because the application rebooted. A software/watchdog reset is not evidence that a stuck Storage/DMA lifetime is safe.

**FULL PHYSICAL POWER CYCLE IS MANDATORY after any failed/uncertain raw-capture attempt.** No in-session retry, second Storage request, semaphore release or forced DMA cleanup. Host marker rearming requires separately established physical power removal; this tool supplies no automatic reset/rearm path. Evidence: heap-reset-tests.json (local-only reference: `builds/phase62-final-preflight/heap-reset-tests.json`; not distributed); no hardware reset performed.
