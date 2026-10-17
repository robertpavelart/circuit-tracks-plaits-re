> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase20B6 — DSP debug access ledger

2026-10-07. **PLAUSIBLE-BUT-BOARD-UNVERIFIED**. Design/review only.
Pinned DSP56724RM chapters2/3/5/6/22 and DSP56300FM5/7 read locally. Full
relevant extracted pages and visually inspected CIM map/summary under
builds/phase20b-snapshot-design/final-v4/evidence/. No refetch or hardware access.

**VERIFIED documentation, CONDITIONAL unit applicability:** DSP56724/25 each
have two serially chained4-bit TAPs and per-core OnCE. RM22 allows configurable
coupled debug entry. JTAG0 supportsBYPASS/OnCE; JTAG1 adds boundary/IDCODE
instructions. Family single-device examples cannot be sent unchanged to a
dualTAP chain. Actual upload endpoint→physicalcore, marking/package/mask and
security state remain unresolved. Prior board report56724AG conflicts with
teardown56725AG; no unit photograph/continuity measurement resolved this.

**Required signal functions:** TCK,TMS,TDI,TDO and qualified reference/ground.
RM2 Table2-21 lists four externalJTAG signals. RM22 block/table additionally
showsTRST; separate physicalTRST access is not assumed. Exact package pad numbers,
board routes/test points, orientation, voltage and external controller are
unverified. PublicTC2050-compatible header is not proof of DSP access; it may
refer toMCU debug. No wiring instructions or connections are provided.

**VERIFIED FM7:** OnCE program memory comparators can stop on execution without
patchingP words. Executed program-fetch trigger acknowledges after matching
instruction. MemoryMOVE access trigger acknowledges after the following
instruction. Preferred lastNOP9DC yields candidate rawnext9DD; exact9D9 via
32nd9D8 execution needsDO-exit/pipeline confirmation. User-visible debuggerPC
alone is insufficient. PABEX is would-execute location, not last-retiredPC.

FM7.2.7.3 savesPDB/PIL before injected debug activity; FM7.2.5/7.2.7.4
PABFR/PABDR/PABEX and complete circular flow history supply boundary evidence.
Forced instruction transfers register/memory data intoOGDB thenTAP shifts it
to the external controller. Architecturalregisters/P-X-Y are inspectable by
that mechanism. No continuous private-memory trace or background nonhalting
peek documented. OnCE state access changes pipeline/debug state and may clobber
pointer/modifier/status according to the instruction/tool sequence.

**Stack:** FM5.4.3 defines16×48-bit hardwarestack (15 usableSEN0). ReadingSSH
popsSP; SSL doesn't. SaveSP/SC/LA/LC/SR before any stack walk; readSSL before
SSH for each frame; preserve physical-index/order/raw values and extension
EP/SZ/OMR state. A debugger displaying onlytopSSH/SSL does not capture inherited
frames. Full loop context includesLF/FV and stackedLA/LC/SR. Complete stack
walk/restoration and debugger controller support remain unqualified on this unit.

**Accumulator/status:** capture A2/A1/A0 andB2/B1/B0 raw bits rather than a
possibly limited/scaled full-accumulator transfer. Save originalSR first. Family
debug instructions can execute transiently while retrieving data; not an atomic
shadow register bank. Neither CPUhalt nor paired-core halt provesDMA/peripherals/
ARM/shared writers stop. Freeze/exclude required writers in a proven epoch.

**VERIFIED manual inconsistency:** RM6 Table6-1 (PDF118) placesOGDB atXFFFFFC;
Table6-2 continuation (PDF119) visibly labelsYFFFFFC. FM7 labelsXFFFFFC. Do
not choose an injection opcode solely from the contradictory figure. Device
applicability/errata and controller implementation need qualification. CIMDMAS
is a DMA-stall *interrupt threshold*, not a DMA-freeze control; do not use it
as a guessed quiescence switch.

MCU SWD/JTAG can conditionally dumpARM registers/RAM; it has no directDSP
private-register/stack address mapping throughSPI. Existing29344/29528 memory
helpers can only become a bridge with future qualified execution control and
transport state. Stock5E reads and lastISR save RAM do not recover a coherent
seam CPU snapshot. Serial/SWO/USB debug-output endpoint remains unproven.

**Decision:** candidate architecture is technically plausible, current board/tool
access **UNKNOWN**, exact coherence **UNRESOLVED**. READY-FOR-ACQUISITION-DESIGN
does not mean available, passive, safe-to-connect, or permission to flash. Current
scope ends with design. See runtime-snapshot-acquisition.md for plan/ranking.

## Phase20B7 update — 2026-10-07

**STRONGLY SUPPORTED photographed board:** DSPB56724AG144-LQFP; actual unit/mask
UNRESOLVED. RM PDF48/49/74 package TAP pins724:TMS101,TCK102,TDI103,TDO104;
725:55/56/57/58. RESET724111/72563 resets both cores. No external package TRST,
DE/debug-ACK or core-selector pin established. Internal TRST description does not
permit inventing a header net. I/O nominal3.3V; actual ground/reference/controller
levels and clock/loading require future qualification.

Public J3 Programming Debug is strongly supported MCU SWD by author SWDIO/SWCLK
diagram. Separate six-pad footprint near DSP is visible but all nets unresolved.
**READY-FOR-PIN-VERIFICATION only; connectionNO.** Exact complete pin/power/reset/
pull table and board observations:builds/phase20b-tapqual/final-v2/.

**VERIFIED documentation:** TDI→core1TAP→core0TAP→TDO; two4-bit IRs. JTAG1 has
IDCODE01ED001D; JTAG0 noIDCODE. CHIDR XFFFFF5 distinguishes000724/010724 per core;
P100/P9D8..9E0 original signatures must corroborate runtime mapping. No such test
performed. Per-core OnCE needs DSP-specific protocol beyond generic JTAG shifting.

**VERIFIED source audit:** pinned OpenOCD8da0578 backend uses plain IR/DR scans,
requiresIDCODE, changesSR/N0/N1/M0/M1 during debug init, and exports only topSSH/
SSL. Raw-latch per-core isolation/full-frame export unqualified. Exact controller
pairNONE, toolingPLAUSIBLE TOOLCHAIN. Symphony official56724/25 support supplies
vendor qualification candidate; modern driver/SKU/raw export unknown. TRACE32
family defaultsoftware breakpoints would patchP, so future hardware mode required.

**Coherence remains UNRESOLVED:** no automatic DMA freeze, no generic safe halt
ordering, no snapshot gate opened. All statements are documentary/source findings,
not tested hardware behavior. External OnCE preferred conditionally; hook not
promoted; flashNO. See three new Phase20B7 notes; static checkpoint exhaustion
remains in force. No commands, attachment, hook or hardware access.
