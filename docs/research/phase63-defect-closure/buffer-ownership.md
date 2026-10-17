> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# DMA destination lifetime and quarantine

**PROVEN:** the old frozen Phase62 counterexample is preserved in its original `dma-ordering-probe.json`. It returned SUCCESS with DMA stream7 EN=1, NDTR=64 and M0AR pointing at dead Main stack. Physical occurrence of that ordering remains **UNKNOWN**; its software consequence was demonstrated, not assumed away.

**PROVEN:** current `construct.FENCE` is called immediately at `read_ok` (before any CRC/encoding raw read) and at the common raw-frame exit. It reads:

- `$400264B8` DMA2 stream7 CR, EN must0;

- `$400264BC` NDTR must0;

- `[$20006968]+16` stock synchronous request flag, must0;

- `[[$20006968]+4]+8` backend semaphore, must1/released.

Until all pass, native scheduler yield `$0801BE60` repeats without popping the Main frame. The fence never writes a DMA control register, releases a semaphore, clears the request, resubmits a read, or aborts Storage. H4 remains no bounded in-session unwind. A stalled/failed transfer can retain the frame until full power cycle. Late physical completion permits return only once ownership is actually released; FAILED remains absorbing.

**STRONG INFERENCE:** these peripheral and software conditions, with no queued second request and no reentrant Main callback, exclude the demonstrated stale-pointer rearm. Reference [ST RM0385](https://www.st.com/resource/en/reference_manual/dm00124865-stm32f7-series-advanced-armbased-32bit-mcus-stmicroelectronics.pdf) identifies stream EN low as configuration-ready. Search-index excerpt was available; full PDF fetch timed out. No silicon timing/cache/bus experiment was performed and no forced-disable sequence is asserted qualified.

| Resource | Owner / lifetime | Writers / readers |

|---|---|---|

|64 raw bytes, R7+192..255 in260-byte frame|Single Main diagnostic invocation until fence permits unwind; retained indefinitely on unresolved failure|Stock QSPI DMA writes; Main CRC/encoder reads only after fence; guard words outside payload|

|12-byte record20044D70..D7B|Early-reserved diagnostic lifetime; reset by installed constructor|Reviewed lifecycle/mount/watch/authorization helpers; host cannot supply addresses|

|Packet areaR7+16|Main live frame; router copies before release|Main encoder; stock router20C90 reads/copies|

|Existing transport rings/parser|Existing native retained ownership|Native parser/router/USB; no new heap allocation|

**PROVEN in fixtures:** option B, an additional fixed64-byte allocation, lacks demonstrated free ownership: reference running RAM has only8 bytes before the reserved record. No unrelated buffer is borrowed and that margin is not current-unit headroom. Option A was chosen because a native non-return fence can be tested without a new RAM claim. It intentionally sacrifices bounded return on fatal failure. A separately qualified fixed buffer could provide an additional lifetime invariant later; it is not silently assumed here.

**PROVEN in declared model:** 31 cases in dma-regression.json (local-only reference: `builds/phase63-defect-closure/dma-regression.json`; not distributed), from [dma_regression.py](<../../../builds/phase63-defect-closure/dma_regression.py>): normal, TEF/missing IRQ at0/4/8, timeout, early TCF with DMA outstanding, duplicate IRQ, late physical release, disconnect during pending reads, late completion while disconnected, producer preemption/queued duplicate, busy backend. No second read follows failure. Canaries persist through their live ownership; checks end at actual raw-frame return because subsequent status calls legitimately reuse stack. Native register checks remain enabled.

Normal measured Main minimumSP200080FC (2460 bytes to fixture lower guard), Storage20009174 (1068). These are prepared-running-RAM model measurements, not final startup/hardware headroom. The guarded software path passes; full boot→capture continuity remains **UNKNOWN**.
