> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: FAILED / SUPERSEDED / DO NOT FLASH.

# Frozen Phase62 stack and DMA-lifetime audit

**PROVEN new measurements**, not reused Phase42/43/61 numbers:15 corrected-image cases execute the native Main/Storage/QSPI-IRQ/USB model. The fixture is a separately authenticated running-RAM state, so these results **do not close startup continuity**.

| Task | Stack low/high guards | MinimumSP | Margin above low4-byte guard | Used below high guard |

|---|---|---|---:|---:|

|Main|2000775C /20008358|200080FC|2460|604|

|Storage|20008D44 /20009240|20009174|1068|204|

Main deepest observedPC0802214C,LR080221A9: diagnostic admission→raw→packet send→USB/router/ring work, ending22190..221A4→2214A. Storage deepestPC08022748,LR080376E1: worker→backend read→37430/controller→3769C command issue→22746. JSON records exact recent instruction paths and LR/PC at each new minimum; these are observed paths, not a claim of a complete symbolic unwind or every possible callee.

The raw function pushes20 bytes then subtracts260 bytes:280 bytes total local/save contribution. Its dedicated64-byte raw buffer is frame+192..+255; packet is+16, guards include+12,+180,+188,+256. It borrows no parser buffer. Caller frames and stock callees contribute the remaining measured depth. Bounds/neighbor/canary checks pass for the measured cases.

Normal completion, actual backend-busy error, disconnect after completed read, and TEF/missing completion at globalchunks0/4/8 are exercised. TEF/missing completion leave Main parked and the request/semaphore retained through lifecycle timeout. Late completion is delivered to the **same** request; it releases that request without a new read and cannot replaceFAILED. This is the15-case normal/fault-model result.

## Required unconditional DMA return invariant: NOT PROVEN / failing countermodel

Prior normal models supplied data, NDTR=0 and DMA.EN=0 before the QSPI TCF IRQ. That is a shared completion-ordering assumption. The new adversarial probe leaves DMA.EN=1,NDTR=64,destination20008258 (the raw stack buffer), then delivers the real native QSPI completion IRQ. Main returns, the request clears, semaphore releases andSUCCESS14 is published **while those DMA fields still target the old stack buffer**. Therefore the software does not independently enforce the requested no-return-with-pending-DMA invariant.

This is **PROVEN in the explicitly injected register ordering**. Whether this ordering can arise on this physical QSPI/DMA implementation is **UNKNOWN**; it is not described as an observed hardware overwrite. Acceptance requires either a source-supported hardware completion-order proof or a software lifetime guard plus adversarial-order tests. Do not treat the successful normal model as that proof. No forced DMA/semaphore cleanup was attempted.

Evidence: stack-dma-tests.json (local-only reference: `builds/phase62-final-preflight/stack-dma-tests.json`; not distributed), [stack_dma_tests.py](<../../../builds/phase62-final-preflight/stack_dma_tests.py>), dma-ordering-probe.json (local-only reference: `builds/phase62-final-preflight/dma-ordering-probe.json`; not distributed), [dma_ordering_probe.py](<../../../builds/phase62-final-preflight/dma_ordering_probe.py>).
