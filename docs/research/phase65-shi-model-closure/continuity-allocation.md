> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Continuous prefix and allocation coverage

**PROVEN within the inherited reset boundary:** one Unicorn ARM instance runs from the authenticated reset-clock prefix and constructors through scheduler launch, NOR mount/snapshot, absent-SD initialization, SPI2/DSP boot and all144 coefficient transfers. It then reaches USB initialization. The actual scheduler/NOR/SD ordering precedes Main's coefficient work; events were not reordered to match a requested checklist. Starting SRAM is zeroed plus authenticated initializer bytes. The inherited starting boundary does not newly reexecute every reset decompression instruction.

| Milestone | Exact12-byte record |

|---|---|

|reset prefix before constructors|`000000000000000000000000`|

|constructors complete|`000000000000000000000000`|

|first scheduler architectural launch boundary|`000000000000000000000000`|

|mount return 0x20000aa0|`110000000180003480908f01`|

|mount return 0x20001af4|`110000000180003480908f01`|

|mount return 0x20000aa0|`110000000180003480908f01`|

|USB initialization stop|`110000000180003480908f01`|

|USB configured/ready|UNKNOWN — not reached|

|Geometry query / same-epoch authorization|UNKNOWN — not reached in this continuous run|

|Raw capture start|UNKNOWN — not reached in this continuous run|

**PROVEN:** 4,421,081 ARM instructions reach `08048316`. The old observation bound flagged GPIO helper `080291B2` after a long computation solely because its cumulative visit count was high. The saved last40 PCs contain that helper only once; this is not a tight firmware wait. observer-false-stall.json (local-only reference: `builds/phase65-shi-model-closure/observer-false-stall.json`; not distributed) preserves the rejected observation. The corrected observer also requires local repetition and a much longer absence of byte progress. It changes no ARM/DSP instruction, MMIO readiness value, task-ready field or geometry record. The repeated prefix was required because the existing runner does not serialize every CPU/peripheral/closure state; no RAM dump was spliced into a running fixture.

**PROVEN allocation prefix:** 298 requests are enumerated in allocation-prefix.json (local-only reference: `builds/phase65-shi-model-closure/allocation-prefix.json`; not distributed), including 122 newly observed after the Phase64 prefix. All old176 request entries match their saved evidence. At USB initialization the actual heap cursor is `0x20011334` and cap is `0x20044d70`. The record still has valid11 state and the same geometry. The existing private-write trace records its intended lifecycle/snapshot transitions. `private_unchanged=false` compares against initial zeroes; it is not a failed canary assertion.

**STRONG INFERENCE, bounded:** the unchanged nonoverflow allocator cap and the unchanged Phase63 reservation regressions support exclusion of ordinary bounded heap growth from the reserved record. The currently observed cursor is below that cap. Request enumeration and final cursor do not prove every allocation's return extent, all future frees/reuse, or the entire postboot lifetime.

**UNKNOWN:** all allocations after this USB boundary, USB transport-session state, raw-frame construction and full same-epoch query→authorization→raw lifetime. No raw capture frame exists yet in this continuous run. Phase63's stack-buffer/DMA fence and host containment results remain scoped evidence; they are not substituted for these missing events. Complete postboot allocation coverage therefore remains unqualified.

**HARDWARE-ONLY UNKNOWN:** actual heap/stack headroom and timing remain unmeasured. Inherited model inputs include synthetic FAT16 geometry/NOR data, JEDEC identity, absent SD, clocks, ADC/calibration values, and explicit DMA/exception scheduling. They do not establish the physical unit's resources or USB interoperability.
