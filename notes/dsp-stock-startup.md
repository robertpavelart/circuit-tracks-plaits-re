> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 19B — original stock startup audit

2026-10-06. **VERIFIED load-only; stock instructions executed: 0.** Entry P:0
and its target P:100 are decoded, not executed. The state gate in
`dsp-boot-handoff.md` prevents a forced prefix or a fabricated worker response.

| PC | Original operation | Earliest live input / consequence |
|---|---|---|
|0|JMP 100|PC defined by boot record; implicit loop/interrupt control must be established|
|100|BCLR bit 13, Y:FFFFFA|Reads old GPIO control word; writes modified word; affects carry|
|101|BSET bit 13, Y:FFFFF9|Reads old GPIO direction word; writes modified word; affects carry|
|102|MOVE Y:FFFFD4,A|ICC read; A receives peripheral transfer under live mode/scaling semantics|
|104|CMP #030002,A|Uses loaded A, generates comparison flags; no note/audio inference|
|106|JNE 102|Polls until exact peer value matches; no fabricated completion allowed|
|107/108|SP=0 / SC=0|Firmware initializes stack control before 10F call, but not incoming SR/OMR|
|109|ORI #03,MR|Sets interrupt mask bits; other MR/EMR bits retained|
|10A|BSET bit 21,SR|Sets rounding mode; does not establish incoming LF/FV or pending events|
|10B|R0=2028|Explicit source for next write; incoming R0 unnecessary for that write|
|10D|X:FFFF7D=R0|Peripheral write; no model in load-only tool|
|10F|JSR 25DB|First main init call; SR/OMR and stack semantics must be correct|
|111|JSR 2071|Further startup; only audited bytes, not reached|
|113|Main service loop|Outside Phase 19B startup scope; no scheduler replay|

**SOURCE-DERIVED peripheral identities** under the DSP56724-compatible profile:
Y:FFFFFA is PCRG, Y:FFFFF9 is PRRG, and Y:FFFFD4 is read-only ICDR4, reflecting
the other core's ICDR3. GPIO reset values alone do not establish post-ROM values.
[NXP DSP56724RM §8.2.5, §13.2.2](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf#page=143).

**VERIFIED static peer dependency:** existing channel-one listing P:105 loads
R5=030002; P:109 writes that value to Y:FFFFD7 (ICDR3). Main P:102/104 expects
the corresponding 030002 at ICDR4. These bytes explain the first peer readiness
dependency. Its real timing, ordered handoff and event model are **UNRESOLVED**;
the worker was not loaded or executed. Classification: **UNRESOLVED / NOT
REACHED**, not an approved stub and not proof that full worker execution is
required for this first publication.

The canonical load report verifies native decoding of 16 entry/vector/startup
instructions against existing byte-checked witnesses: same opcode bytes and
instruction lengths, with decoded direct targets 100,1B4,156,102. Formatting
aliases differ between listings. This is **MATCH for load/decoding**, not an
execution differential. No branch, loop count, effective runtime address or
executed store has been measured.

| Expected initialization | Existing evidence | Replay result |
|---|---|---|
|X/Y clear|2779 modifiers; 2786 DO, X store2788 then Y store2789/postincrement; 6000 iterations, 24576 stores each|NOT REACHED|
|Shared X clear|278F..2791, 8000 words at30000..37FFF|NOT REACHED|
|Modifiers|2779..2781 sets M0..7=00FFFF|NOT REACHED|
|Cursor family A|260A..2623, Y1820..182F alternate2CCC/2CEC|NOT REACHED|
|Cursor family B|Same loop, Y1A10..1A1F alternate2C02/2C24|NOT REACHED|
|Four reviewed P→X tables|2620/2629/271D/29F2; source bytes match prior table hashes|NOT REACHED; source integrity MATCH|
|Descriptor initialization|27F8 and2644 regions, existing descriptor map|NOT REACHED|
|SHI setup/unmask|25DD/25F2 bit9 ofXFFFFBD,25F1 ANDI FC,MR|NOT REACHED; chip/event model NOT MODELED|

Expected results are assertions exported separately, never preloaded X/Y
state. No same-value boot-zero writes occurred. In later authorized replay,
boot clears must be classified INIT and every store logged, including zero→zero.
Do not equate startup zeroing with normal ownership or persistent allocation.

**UNRESOLVED later gates:** startup Y:[4000,6000) exceeds the conditional
device/core0 Y RAM extent; do not silently enlarge RAM or ignore writes. EMC
setup/external accesses start in2779; tables depend on ARM-side readiness at
X:FFF/193F in25DB; interrupt state and peripheral scheduling need contracts.
These are static anticipated dependencies, not actual faults or reached waits.

Watch declarations: X35F, X[340,360), X[5F00,6000). The runtime watch log is empty,
explicitly because the execution gate is closed. No X35F invariant or high-X
ownership status changes. Full scheduler entry and Phase19C work were not begun.

## Phase19B-HANDOFF refinement — 2026-10-06

`dsp-rom-handoff.md` records exact opcodes/reads/writes for five instructions at
100,101,102,104,106. Neither stack nor R/N/M addressing is an explicit operand
there; requiring arbitrary zeros for these unused registers would be excessive.
Live loop/IRQ/mode state and GPIO latch inputs remain blocking unknowns.

**DOCUMENTED:** PCRG/PRRG reset1E1 and are configuration-latch reads; PDRG pin
samples are not read by the prefix. After100/101 bit13 is configured output;
actual output-latch/pin level and board wiring remain unresolved. The second ROM
pass's latch preservation is unproved. ICC data read acknowledges/clears the
interrupt condition according to13.1.2; disabled/empty ACK edge cases must not
be invented. **VERIFIED:** worker109 publishes its initial queue cursor30002,
later121/128 republish progress, and main779 also consumes that progress.

ARM upload order is main thenworker; exact publication versus first main poll
is unresolved. Worker also needs unmodeled peripherals/control state before
109. Both execution gates remain closed; no stock prefix, worker or bootstrap
was executed. The longest currently defensible prefix remains0 instructions.

## Phase19B-ROM result — 2026-10-06

Authentic ROM source/exit instructions were not recovered. Public browser access
to the historical discussion succeeds but source links are absent; API/archive
recovery limitations are documented in `dsp-rom-loader-source.md`. Matching
register addresses in the two official manuals cannot justify a guessedROMexit.
Main/worker manifests retainunknown handoff values separately; no original
instruction executed. Clear/table/cursor and realICCbranch/ACK checks remain
NOT REACHED. No19B2/19C resumption is enabled.

## Phase 19B-SYMBOLIC result

Local PCRG/PRRG bit operations work with unrelated bits unknown:100 defines
bit13=0;101 defines bit13=1; carry remains the old bit13. These tested partial
transfers are not architectural execution. The live interrupt predicate remains
unknown, blocking both originals before JMP100 and the requested main100 entry.
Original counts0; ICC polling/publication/receive and startup clear remain
NOT REACHED. Full-word requirements give way to actual known-bit dependencies;
qualified live control state is still required.

## Phase 19B-IRQ — 2026-10-06

**UNRESOLVED interrupt-exclusion/convergence contract; original main0 / worker0.**
See `notes/dsp-interrupt-handoff.md` and `builds/phase19b-irq/final/`.

DOCUMENTED: PIC field00 is disabled,01/10/11 select IPL0/1/2; SR.I is bits9:8.
The always-on source at VBA+FC needs no external event when enabled. ICC NMI
and DMA-stall are IPL3 sources; ordinary mask3 alone cannot exclude them.
The SHI mode0 description specifies loading/entry, not a reviewed SR/PIC/FIFO
cleanup or interrupt-pipeline contract. No post-ROM reset value was promoted.

VERIFIED conditional on VBA0: main vector44 JSR156 writes Y2000..2002 and can
write HRX through inherited X10 to X/Y RAM; main vector3E JSR1B4 writes RAM/DMA.
Other nonreserved main vectors and every nonreserved worker vector are NOP/NOP.
Fast NOPs do not prove persistent peripheral requests clear or finite convergence.
VBA0 itself is not established after ROM. Upload order does not prove the exact
cross-core entry/publication interleaving. No 30002 was seeded.

SYMBOLIC source/vector classes are conditional architecture classes, not verified
reachable ROM exits. Exact first fetch also depends on pending/already fetched
interrupts and documented pipeline timing. The abstract field predicate alone
is insufficient. Loop inheritance remains deferred because IRQ resolution failed.
No stock or handler instructions executed; no scheduler replay enabled.

TESTED:16 canonical files match final/final-repeat;24 existing partial-state
checks pass;16 PIC/SR predicate cases pass; protected SYX/BIN and all ten DSP
extraction hashes match; sealed203-file concrete-core/harness guard passes.
Evidence: builds/phase19b-irq/checks/reproducibility.json.

The next prerequisite is a matching authoritative final SHI ROM-exit fragment
or handoff guarantee covering effective interrupt state/pipeline and VBA,
including second ROM entry. A full register dump is not required. Previous
phase gates and X35F/high-X ownership verdicts remain unchanged.
