> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 10 — channel-zero X:[5F00,6000) after-init audit

## Phase 19C-P204B — independent writer remains open (2026-10-06)

**NORMAL high-X result: NOT-YET-DETERMINED.** No defensible positive compiled
count/records/destinations were recovered; resultD. P204B's exact normal write
set is unknown, not a continuous count-sized buffer. It performs one unindexed
X store per record+4 destination.20 is not an enforced count bound. Count is
latched into24-bitLC once; count-cell stores alone do not change currentLC.

**BOUNDED-PROOF:** previously qualified count0/zero-skip entries yield no204B
stores; no new replay. All recovered1B90 direct-caller domains exclude the
count/prospective record window, narrowing a producer concern without proving
global count preservation. SHI effective cursor/space/cache, foreignY cursor/
modifier/entry and other inherited indirect/worker obligations remain unresolved.
No normal high-X collision witness, and no universal exclusion. **P204B is not
removed as a high-X blocker.** Service robustnessNO; verified256-word allocation
NO; no sentinels, firmware edits, hardware or Plaits work.

Current report:[dsp-p204b-provenance.md](<dsp-p204b-provenance.md>).21 reproducible
reports/focused tests and original/extract/core/prior guardsPASS;0 CPU instructions.
Assets frozen. Next: target normalP19D count/table effective endpoint provenance,
not a new high-X/whole-write census. Previous conditional exclusions remain.

## Phase 19C-PARENT — current high-X gate

2026-10-06. **UNRESOLVED actual normal parent high-X result.** No defensible
entry into1E15 was established, so no parent/helper memory access was observed
in this phase. It cannot report PROVEN NO FOR QUALIFIED NORMAL PARENT PATH.
Initialized valid dispatch excludes the parent; mutation/index domains remain
unclosed. A candidate effect-chain call inherits D99 LF1/LA=DAF/LC1..5, outside
the previous LF0 bounded proof. Local pointer publications and prior conditional
low-buffer bounds are retained, not promoted to ownership.13 reproducible static
exports/7 tests/2 refusals pass;0 DSP instructions. See
[dsp-parent-replay.md](<dsp-parent-replay.md>) and builds/phase19c-parent/final-v3/.
Normal safety NOT-YET-DETERMINED; service robustness NO; verified256-word
reservation NO; implementation readiness NO. Next: targeted normal effect
selector/table producer and preservation proof, not another alias/ROM census.

## Phase 18 — minimal offline replay specified, not implemented

**DESIGN:** use pinned C++ DSP56300 core in forced-interpreter mode first.
No replay harness, build or DSP execution occurred. Complete CPU/parallel/P/
peripheral/DMA/worker/host store mediation and selected read/203A-entry logging
are required before trusting a trace. **VERIFIED source gaps:** REP iterations
bypass the ordinary opcode callback; DO runs internally; DMA has memcpy/fill
fast paths independent of JIT. Existing generic hooks are insufficient alone.

**UNRESOLVED prerequisites:** post-upload SR/OMR/memory profile, startup Y clear
outside conditional private RAM, EMC initialization, host table contents/order,
material worker behavior and actual normal reachability of parent1E15→1F5C.
Do not invent a full startup checkpoint or a mandatory1F97 scheduler stage.
Separate conditional unit fixtures from integrated normal stock scenarios.

See [dsp-emulator-spec.md](<dsp-emulator-spec.md>),
[dsp-replay-scenarios.md](<dsp-replay-scenarios.md>),
[dsp-emulator-validation.md](<dsp-emulator-validation.md>), and builds/phase18/final/.
**Next:** Phase19A core/memory/every-write tracing plus ISA/AGU/loop/IRQ coverage
tests only after explicit implementation instruction. Planned19B startup,
19C targeted scheduler/models,20 validated stock replay; gates may add work.

X35F invariant/high-X normal availability remain **NOT-YET-DETERMINED**;
service robustness remains **NO**. Hardware stays disconnected,5E rejected,
no firmware patch/allocation/Plaits work. This supersedes historical next steps.

## Phase 17 — documented OnCE fails the observation gate

**SOURCE-DERIVED:** candidate DSP56724/25 uses DSP56300 OnCE, not SC140 EOnCE.
AN2073 section5 explicitly requires Debug mode, stopping normal execution.
Documented memory inspection injects instructions; flow history contains
program addresses, not effective X/Y write data. No qualifying nonhalting
state-preserving read or sufficient write-trace facility was established.

**STRONG HYPOTHESIS:** DSPB56724AG, supported by first-party board research
and external-memory evidence. A conflicting56725AG public report and exact
unit/package remain **UNRESOLVED**. Public STM32 header references do not
establish DSP JTAG pads. Board access to a qualifying facility is unresolved.

Offline emulation is plausible for conditional targeted traces, but full initial
state, peripheral/event fidelity and every effective-write hook need validation.
No emulator build/run or firmware instrumentation occurred. PassiveSPI alone
cannot close internal-write exclusions. Keephardware disconnected and5E rejected.
X35F invariant/normalhigh-X availability stay **NOT-YET-DETERMINED**; service
robustness stays **NO**. No allocation or Plaits work.

See [dsp-debug-observation.md](<dsp-debug-observation.md>),
[board-debug-access.md](<board-debug-access.md>) and `builds/phase17/final/` for
citations/matrices/source witnesses. **Next:** static emulator coverage/readiness
specification for minimal1F97/203A replay; no broad alias census or live debug.
This supersedes historical next-step suggestions below without changing their
verified firmware findings.

## Phase 16 — observation safety gate FAILED

**VERIFIED:** correctly decoded service5E READ (operation1) is distinct from
WRITE (operation0), but a useful private read writes DSP X:10/X:11 and
Y:2000..2005 interrupt-save RAM. Their contents survive return; restored CPU
registers do not restore those RAM words. Therefore this is not a strictly
state-free read mechanism. No hardware action or live utility is justified.

Each requested word also prefetches the following word. Reading X:5FFF would
access6000, outside the conditional core-zero X-RAM bound. A conditional
ARM29344/292F8 address-cache interaction could redirect a subsequent cached
normal write; actual interleaving remains **UNRESOLVED**, not an observed bug.
Synchronous SPI/completion polling and DSP ISR preemption preclude a claim of
glitch-free operation. External physical ingress and global side effects remain
**UNRESOLVED**. See [dsp-readonly-observation.md](<dsp-readonly-observation.md>),
offline audit `tools/ct_readonly_observation_audit.py`, `builds/phase16/final/`.

X:35F invariant and high-X normal availability remain **NOT-YET-DETERMINED**;
SERVICE-ROBUST remains **NO**. No allocation, binary changes, active service
request, debugger use or Plaits implementation. Earlier observation proposals
are conditional schemas, not permission or recommendations to issue5E reads.
Next: assess exact-chip/board documentation for a genuinely passive data
observation facility; documented OnCE memory inspection is not established
as a nonhalting, state-free alternative.

## Phase 15 update — no allocation upgrade

[dsp-p1f97-cursors.md](<dsp-p1f97-cursors.md>), evidence `builds/phase15/verified/`.
The initialized1F97 family reaches A[2CCC,2D0C) or B[2C02,2C22)+[2C24,2C44)
under stock32/recognized modes, without pointer drift across blocks. Its local
Y writes preserve the pointer cells. This is **VERIFIED conditional exclusion**,
not universal normal preservation. Generic foreign Y/SHI/context writers and
actual entry/modifiers remain **UNRESOLVED**; family not removed from35F blockers.
The count invariant and NORMAL-RUNTIME SAFE remainNOT-YET-DETERMINED;
SERVICE-ROBUST staysNO. No candidate re-evaluation,256-word allocation or port.

Broad static alias phases now have diminishing returns without new concrete
producer constraints. No proof of static impossibility. A minimum unperformed
observation schema is documented:203A count loads and1F97 effective X writes,
using a suitable existing read-only/nonhalting facility only if independently
available and hardware use later authorized. No hardware/patch/debug action.

## Phase 14 update — candidate gate unchanged

[dsp-x35f-invariant.md](<dsp-x35f-invariant.md>), `builds/phase14/current/`.
X35F zero invariant **NOT-YET-DETERMINED**; no normal nonzero witness.
204B cannot be its first violator under recovered202B entry/zero-skip mode,
but normal foreign writers remain unclosed. Candidate was **not re-evaluated**
because the requested invariant gate did not reach VERIFIED. Previous normal
safety NOT-YET-DETERMINED/service robustness NO stand; no256-word allocation.

New conditional host-family bound: initializer208FA supplies2740C bytes to
20006990+4 via355E8/47C64;395EC stream stays[E7FFFE,E93A06), excluding35F,
under recorded state/transport premises. This does not close all host traffic.
Next:1F97's Y[1820,1830)/Y[1A10,1A20) cursor preservation, excluding[340,360)
under stock32/linearM7. Other census/context/transition obligations remain.

## Phase 13 update — zero-count consumer, preservation still open

[dsp-indirect-write-204b.md](<dsp-indirect-write-204b.md>) and
`builds/phase13/final/` supersede the earlier unspecified204B count reasoning.
**VERIFIED:**204B writes one absolute X word per five-word record, with no R4
postincrement. ARM286E4 sends **zero** to35F+172*bank, while286DA sends the
separate source count to2FA+172*bank. Boot clear also sets35F and the inspected
record window zero. In documented zero-skip mode, preserved X35F=0 means an
empty destination set. No nonzero publisher was recovered.

**UNRESOLVED:** universal normal preservation of X35F and table/AGU state.
An absent publisher is not a global non-alias proof. Path collision is
**NOT-YET-DETERMINED** universally; conditional zero-count paths exclude the
candidate. Existing effect/host-transfer/mode obligations remain.
**NORMAL-RUNTIME SAFE: NOT-YET-DETERMINED. SERVICE-ROBUST: NO.** No256-word
allocation proved. Static analysis is not established exhausted. Next: targeted
X35F preservation through the already-open normal indirect writers. No port.

## Phase 12 update — independent safety axes

Current report: [dsp-effect-memory.md](<dsp-effect-memory.md>), evidence
`builds/phase12/final/`, reusable `tools/ct_effect_memory_audit.py`.
**NORMAL-RUNTIME SAFE: NOT-YET-DETERMINED. SERVICE-ROBUST: NO.** Service5E
is no longer counted as a normal allocation blocker. No normal occupancy
witness or verified256/128/64-word allocation; original/init clearing allowed.

**VERIFIED narrowed R7 domains:** the five reviewed algorithm wrappers set
R7=840/880/9C0. If they select1E15, its32*2 Y stores cannot alias effect
cursor tables1820/1A10, with linear M7 or the concrete low3FF ring. Actual
normal1E15 entry remains unresolved: seven indirect sites, valid55-entry table
and algorithm entry+1 targets exclude1E15, but normal X95A..95F index domains
and table preservation still require producer closure. Indirect is not unbounded.

**VERIFIED additional local bounds:** C3E coefficient reads conservatively
X[15C0,1941) with signed24/linear premises; initialized indirect output max2D0B;
reviewed prefix read max2DAE. Full normal effects/scratch union remains open.
M3's temporary load584 reaches restore5BE without any control transfer.

**VERIFIED data and direct DMA closure:**31 INIT RLE records occupyP[2309,2599)
and populate external X[74000,7BC00). Apparent DMA-register instructions there
are data. Remaining direct DMA references are setup and fixed ISR rearm only.
Global normal indirect reconfiguration remains unresolved, particularly the
normal descriptor202B's X store204B whose R4 comes from X364+5*k.

Nine ARM fixed staging records have256 words each, X[C00,D00). Recovered normal
mailbox families remain bounded; universal context/publisher preservation is
not claimed. Boot/service reboot entry census shows no ordinary block clear
of the candidate, but scene/project and indirect-write persistence remains open.
Next: bound normal destination records/count consumed by202B/204B. Four future
service-mitigation options are documented conceptually; none implemented.

## Phase 11 update — 2026-10-06

[host-utility-269e4.md](<host-utility-269e4.md>) supersedes the unresolved-host-
entry and missing-selector7-publisher statements below. Evidence:
`builds/phase11/replay/`, reusable `tools/ct_host_utility_audit.py`.

**VERIFIED recovered utility entry:** incoming framed request ID5E through
1EB30→2484C→1F284→1F30A→269E4. It is a **SERVICE-ONLY** invocation in the
recovered graph, with no check requiring Selection1: the enable/mode-related
guard occurs afterward. It admits single-word private X starts at every
candidate word while Selection0 can remain active. This is **SERVICE-ONLY
OVERLAP**, not a normal synth/UI writer or observed request. Scalar private
writes consume one byte per4-byte input slot and transmit zero; scalar reads
explicitly program the address. Count/backing-buffer constraints beyond the
local start check remain open; no requests were generated or transmitted.

**VERIFIED selector7 publisher found:**49C0A; index atX:C00 comes from
49A80's first argument, supplied0..63 by49A66. Three-word destinations have
maximum1E8B, endpoint1E8C, excluding high X under the recorded linear/staging
premises. Earlier abstract index105D is not a recovered normal witness.

**VERIFIED effect producers found:** startup260A..2623 initializes
Y:[1820,1830) to alternating2CCC/2CEC andY:[1A10,1A20) to2C02/2C24.
Stock32/linear-AGU indirect X output footprint has maximum2D0B. Reviewed local
effect state writes preserve these pointer cells. **UNRESOLVED:** all normal
foreign writers and modifier/entry invariants; no universal effects maximum.

Candidate remains **UNRESOLVED / POTENTIALLY AVAILABLE**, with service overlap;
no normal occupancy witness or verified256/128/64-word allocation. Global
nonparameter/cursor/AGU/reconfiguration/physical alias closure remains separate.
No alternative search was triggered: no disqualification or proved unavoidable
static unknown. Next: prove normal effect pointer-cell preservation and entry
modifier state. No layout, binary changes, hardware or Plaits implementation.

2026-10-06. Static analysis only. Addresses below are DSP 24-bit word addresses
unless prefixed with an eight-digit ARM address. Existing binaries, extracts,
original/, and Plaits source remain unchanged. No execution on hardware or DSP
emulation was performed.

**Result: UNRESOLVED.** No normal-runtime occupancy witness into this exact
candidate has been established, and no contiguous 256-,128-, or64-word region
is **VERIFIED AVAILABLE AFTER INIT**. Absence of direct references is not an
allocation proof. The reviewed table generator and audio DMA do not supply
such a witness; addressed host utilities and indirect effect-state cursors
still prevent a universal exclusion. No theoretical allocation is proposed.

## Evidence and reproduction

The reusable offline replay is `tools/ct_high_x_audit.py`. It verifies the
original hashes, in-memory SYX decode/rebuild equality, DSP listing bytes, and
the bytes of the ARM windows collected in this phase. It uses existing DSP
disassembly, not invented decoding or Capstone DSP support. Reviewed arithmetic
premises are explicit; the replay is not a global points-to solver.

```powershell
$py='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B tools/ct_high_x_audit.py --output-dir builds/phase10/new-replay
```

Output must be a fresh directory; overwrite and original/ destinations are
refused. Canonical evidence is `builds/phase10/replay/`; its independent repeat
is `builds/phase10/replay-repeat/`. Earlier exploratory `verified/` evidence
is superseded by the replay after correcting the selector7 evidence-site label.
The four `arm-*` directories retain byte-checked ARM windows and candidate
caller/pointer scans; each provenance.json records targets and exact windows.
Regenerate those with `ct_bank_domain.py` and its recorded arguments if needed,
using the existing small Capstone dependency. No tool was installed this phase.

The exported inventories retain unresolved entries. A linear listing includes
constant/data decodes: a decoded `jset` in a table is neither a DMA register
write nor a proved executable path. Likewise, an absent direct call does not
prove a function dead. `indirect-X-inventory.json` inventories the low code
prefix, not every possible program entry or a complete normal CFG.

## Candidate-specific access classes

| Class | Evidence / bound | Classification relative to candidate |
|---|---|---|
| Startup clear | P:2779..2789 initializes modifiers and clears X/Y:[0,6000) | **VERIFIED INIT-ONLY**, allowed for after-init allocation |
| Recovered normal parameters | Phase9 bank0/1; X52..959, YFD..78F, with holes | **VERIFIED excluded** for this recovered callback graph |
| Direct X operands | Byte-checked canonical listing has no literal X operand in [5F00,6000) | **VERIFIED census**, not an indirect-access proof |
| Normal table-job X workspace | Initial R1=2400/2500, M1=3FF; ring [2400,2800) | **VERIFIED conditional bound**, addressing premises below |
| Table export read lookahead | Small-N branch reads X:[2400,2802) with linear M2 | **VERIFIED conditional bound**; last read2801, no high-X write |
| Addressed utility | 080269E4 accepts private start below8000; 26A9A write /26AD4 read | **UNRESOLVED normal vs service ancestry**, domain includes candidate |
| Bulk transfer families | 35E28 low staging + external/Y output;48DAA/49A80 page-addressed streams | Selected bounds below; **UNRESOLVED global normal maximum** |
| Selector7 | P:1CBB..1CC7 computes X cursor from X:C00 | **UNRESOLVED normal publisher/index**; not a runtime occupancy witness |
| Effect indirect X output | P:1F68/6A load cursors from Y state,1F6E/6F/97 write X | **UNRESOLVED cursor producers and entry reachability** |
| Reviewed DMA0/1 | Writes Y29..2B and fixed X peripheralFFFFA4 | **Excluded for reviewed configuration**, reconfiguration closure open |
| Reviewed ISR saves | Audio YF3F/F40; SHI Y2000..2005; hardware stack registers | **VERIFIED selected saves**, no universal software allocator bound |
| Worker | Private worker low X is a different domain; queue starts shared30002 | **SOURCE-DERIVED distinction**; capacity/alias closure remains open |

No entry in the UNRESOLVED rows is promoted to NORMAL RUNTIME or SERVICE-ONLY
solely from its ability to address the range. The apparent addressed service is
a **HYPOTHESIS** about role, supported by request decoding and response encoding,
not proof that ordinary Selection0 audio excludes it.

## X:1B16: asynchronous table-job saved context

**VERIFIED:** the structure is eleven words X:[1B16,1B21), not one retained
destination pointer. X:1B15 is the job-active/remaining field; X:1B21 separately
holds the size used by table export. P:1D26 sets R2=1B16,1D32..3C saves the
following state,1D41 resets R2, and1D48..52 restores it:

| Offset | Saved state | Established instruction use |
|---|---|---|
| +0 | R0 | X coefficient-input cursor |
| +1 | R1 | X workspace cursor |
| +2 | M1 | Workspace addressing modifier |
| +3 | R4 | **Y** generator cursor |
| +4 | N4 | Generator step |
| +5 | M4 | Generator modifier |
| +6 | R5 | **Y** output cursor |
| +7 | N5 | Output-stage stride |
| +8 | B1 | Coefficient-stage bound/progress |
| +9 | X0 | Stage/progress code |
| +10 | R3 | X export/interpolation cursor |

1D5D/1D6A/1D90/1D96 reset R2 before common re-save1D32.1D30 updates1B15;
1DA2 clears it and1DA8 publishes completion Y2C=80. Main mailbox processing
calls resume1D41 at1CCD, so this is an incremental job spanning service passes.
The canonical direct-reference census and exact context instructions are
exported. Foreign SHI writes into these fields are not excluded globally.

**VERIFIED local producer path:**1C57 defaults N1=2400; selector3 overrides
2500 at1C8B.1CFE stores N0→X42 and clearsX43;1D00 stores size→X1B21;
1D05 M4=3FF,1D07 R4=1400,1D09 calls1DAA, which fills Y:[1400,1800).
1D0B copies M4→M1,1D0C R1=N1,1D0D clears1024 X workspace words.
1D1A initializes R0=C00; coefficient generation1DF2 reads X:(R0)+.

**SOURCE-DERIVED addressing + VERIFIED setup:** under SR.EMA=0 legacy
DSP56300 addressing, M=3FF is a1024-word modulo ring. Both concrete initial
addresses2400 and2500 lie in the aligned ring [2400,2800). This is not a
generic assumption that every M=3FF pointer uses that ring. R2 inherits R1/M1
for the writes at1E08/1E0A. No writer in this reviewed job approaches5F00.

The reviewed recurrence1D74..84 starts with X43=0 and B=1. The first four
stages consume one coefficient each; following stages consume2,2,4,4,... .
For X42=16 the total is256; for18 it is512, giving coefficient-source
intervals X:[C00,D00) /[C00,E00). `coefficient-stages.json` replays the old-bit
carry behavior of BSET/BCHG explicitly. These bounds assume no foreign state
mutation and the recorded loop/addressing setup. They do not bound arbitrary
host changes to X42/43 or a resumed context.

**Memory-space correction:**1DBF's final stores are **Y:(R5)+**, not X.
For the reviewed positive sizes,1D13..18 form output start=base+17*N and
N5=2*N; retained R5 belongs to Y. Small-N branch1DCD exports1024 words,
reading X2400/2401 before a512-iteration two-read body: linear read
[2400,2802), including the two lookahead words beyond the workspace.
Large-N interpolation branch1DD5 restores M2=M1 and uses the same X ring.
An external/shared alias requires actual mapping evidence; a numerical Y
address equal to5F00 is not a private X access.

## Mailbox selectors and host table traffic

**VERIFIED:** selectors0/1/3/4/5 enter the above generator and export to Y.
Selector2 uses1CF4..1DAF with count1 and a Y destination. Selector6 copies
512 words X:C00→Y:(R5)+ at1CB2..B5. Selectors1/6 have no proved normal ARM
publisher in the recovered graph; avoid inventing normal usage.
Backup transforms1CD0/1CD9/1CE6 read X:[2800,2A00) and write X:[C00,E00)
under the reviewed linear modifiers. Together with the ring, the highest
reviewed X table-job write is27FF; selected backup reads end29FF.

**VERIFIED selector7 capability:**1CBB reads X:C00;1CBC..C3 forms
R1=1D8D+4*index;1CC4..C7 copies the next three X source words to X:(R1)+.
For an abstract index105D, the destination is[5F01,5F04) with a linear M1.
No normal selector7 publisher or such index value has been established.
This is an explicit counterexample to unconstrained index safety, **not** a
reason to classify the candidate RUNTIME OCCUPIED. Modifier/caller constraints
must be retained; the main epilogue restores linear M1 only afterward at1CCC.

**VERIFIED ARM instruction findings:**

- 08035E28 publishes selectors2/3/4/5/0 at35E66/35F04. Its low coefficient
  staging begins at X:C00 (35EC2/35EC8); bulk count comes from halfwords in
  flash records (35EC0), then cached streaming2968E. Complete record/count
  closure is not claimed here. Published bases start100000 and advance by
  28800 or4800; generated output accesses are Y/external, not private X5F00.
- 08048DAA uses page setter294AC at48DCA. The reviewed caller395EC supplies
  E80000, then48E26 streams chunks. This caller targets external memory;
  it does not prove that every caller or page transition is bounded there.
- 08049A80 obtains its initial page from the second argument at49AC8..D0,
  streams via296B0/2968E, and publishes low metadata X:C00..C03 plus Y2C at
  49BBC..49C0A.49A66 calls it repeatedly with an accumulating address and
  identifiers0..3F. The initial address's ancestors remain unclosed.
- 080269E4 decodes request fields into operation (stack90), mode (91),
  address (96..99) and count (9A..9B).26A3C..50 accepts either shared
  [30000,38000) or a private start below8000; this private range includes
  every word of the candidate.26A90..9A increments a cursor and passes
  UXTH address to292F8;26ACE..AD4 does the matching read. Shared paths use
  29314/295BA. Mode chooses port and the8000 space flag at26A24..3A.
  Caller1F30A is verified as an instruction, but full dispatcher condition
  and normal/service restriction remain **UNRESOLVED**. Response encoding
  at26B08/26B14 does not itself establish SERVICE-ONLY.

**UNRESOLVED:** universal normal host X read/write maximum, full cached
stream cursor extents/wrap, and addressed utility mode restrictions. Normal
parameter bounds from Phase9 are preserved and were not re-analyzed.

At21E58 the returned32-bit word is shifted16, then values≥2001 are mapped
through `>>2 +1800` at21E62/64. This intermediate is at most57FF;21E70 adds
a separate4000 flag from R4 before storing ARM state. This is an
**instruction-derived intermediate bound**, not a proved high-X read or
exclusion: the transformed value is not passed to SHI in this window.

## P:1E15 / X:1D3A and1D3B, including indirect effects

**VERIFIED:**1E15/17 are direct writers saving incoming R6/R7.1E33/1EC2
load1D3A into R4 for **Y** reads at1E3D/40 and1ED2.1EED/1EEF restore
R6/R7;1F03 reads Y:(R6)+N6 and1F0D/E write Y:(R7)+. Thus those saved
values are pointers by use, specifically Y-buffer pointers on these paths.
The low X containers are not proof of high-X pointer dereferences.

No canonical direct call/branch target or exact aligned24-bit value1E15
was found in this payload. This is a census finding, **not** proof of dead
code. Normal entry, incoming pointer producers, and all modifiers remain
**UNRESOLVED**. Boot zeroing initializes the containers; the direct state
reference inventory lists every decoded direct writer/reader. Indirect/host
writers are not automatically excluded by that census.

**Important remaining X mechanism:**1E74..7E sets X1D40/41/42 to
1800/1840/18E0;1ED7..EE1 alternatively uses19F0/1A30/1AD0.1F5C reloads
these as R6/R5/R4.1F68/6A reads **Y:(R6+32/33)** into R1/R3, then1F6E/6F
clears **X:(R1)+ /X:(R3)+** for X3A samples (stock32).1F89 loads a similar
Y-state cursor into R7;1F93/97 reads/writes X:(R7), advancing each sample.
These are actual X pointer dereferences sourced from Y state, unlike1D3A/B.
For the first pass, relevant Y cells include1820/1821 or1A10/1A11; later
16-iteration progression must also be accounted for. Their complete producer,
modifier and reachability closure remains open. This prevents asserting an
effects/scratch maximum or treating the entire1E15 subtree as X-safe.

Selected local scratch is still low:1E4E/1E50 X1D43/1D53;1ECC X2C46;
1EE7..F0 X2C02/2C24/1D6D/2CCC/2CEC;1F74..7C X2C44/2C66/2C88.
N=32 bounds these local loops under linear setup, but they are not a bound
on the loaded cursors. Previously proved filter/effect prefix intervals remain
valid under their recorded premises. **Global normal effects maximum: UNRESOLVED.**

## DMA, interrupts, stack, worker and persistence

**SOURCE-DERIVED:** [DSP56724RM table3-7](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf)
defines eight DMA channels. For channel c, DCR=FFFFEC−4*c,DCO=+1,DDR=+2,
DSR=+3. The expanded census includes channels6/7; Y:FFFFE6 is EMBC, not
X:FFFFE6 DDR2. Worker Y:FFFFD0..D7 belongs to ICC, not DMA.

Space and update fields follow [APR23 table1-2](https://www.nxp.com/docs/en/application-note/APR23.pdf):
DSS bits1:0,DDS3:2, source mode6:4,destination9:7,D3D10.
Mode4 holds its address; mode5 increments. The stock controls select D3D=0
and counter modeA. The count2 means three transfers per
[DSP56300FM section10.5.3.1](https://www.nxp.com/docs/en/reference-manual/DSP56300FM.pdf).

| DMA | Stock control and PCs | Source | Destination |
|---|---|---|---|
| 0 |285AC4;2A2D..33 | fixed X:FFFFA8 (ESAI RX0) | Y:[29,2C) |
| 1 |286251;2A35..3B | Y:[21,24) | fixed X:FFFFA4 (ESAI TX4) |

1BC rearms DDR0=29;1BE rearms **DSR1=21**. Earlier notes reversed the
channel1 source/destination registers and mislabeled21 as X staging; corrected
here. There is **no private X RAM destination in this reviewed DMA setup**.
The numerically largest X destination is the peripheralFFFFA4, not an X RAM
extent. All indirect/host reconfiguration and channel-enable closure remains
**UNRESOLVED**; an eight-channel register census is not that proof.

Audio ISR1B4 saves Y0/Y1 at YF3F/F40 using M0=Y1A=FFFF and hardware
SSH/SSL for R0/M0/N0.1C1 sets M0=3FF; R0 comes from YFFE.1C7/1C9
write the Y input ring;1C8/1CA read the X output ring;1CB/1CC write Y22/21.
With the initialized cursor and retained legacy modifier these are
[1000,1400), followed by balanced restores1CF..1D8. SHI's reviewed save
area is Y:[2000,2006). Hardware return/loop stack is distinct from X RAM.
The context save X:[1B16,1B21) is bounded locally. Arbitrary software
scratch/context redirection, global nesting and all indirect saves are not
globally proved safe. No verified allocator growing to5F00 was found; no
universal allocator exclusion is asserted.

**SOURCE-DERIVED conditional part map:** core-private low X spaces must be
kept separate. Shared [30000,38000) is numerically outside this candidate;
the known worker queue starts30002 with endpoint30000 and legacy M5=FFFF.
The selected192*12 request count is an estimate, not capacity/backpressure
proof. No worker write into channel-zero private [5F00,6000) was established.
Physical part/core assignment, all aliases and queue extent remain unresolved.

**Persistence:** INIT clear is permitted. The reviewed32-frame paths, table
workspace, saves and DMA do not clear this range. No candidate-specific
periodic clear was established. **UNRESOLVED:** contents surviving every
successive block/background job/mode transition, because the host utility and
effect cursor producers are not closed. Conditional non-interference of selected
paths is not universal persistence.

## Allocation verdict and exact next proof

`allocation-search.json` checks all contiguous placements:1 of256 words,
129 of128 words,193 of64 words inside [5F00,6000). Each lies within the
unclosed addressed utility's private input domain. Shrinking the candidate
cannot remove that uncertainty. This is a proof about the **remaining domain**,
not a simulated trace or a proof that a request occurs.

- Entire range: **UNRESOLVED / POTENTIALLY AVAILABLE**, with **VERIFIED
  INIT-ONLY** clearing; no normal occupancy witness established.
- Largest **VERIFIED AVAILABLE AFTER INIT** subrange: **none established**.
-256-word persistent allocation: **not proved**. No layout, sentinels, state
  reservation, or memory writes were made.
- Stock output X:[2C46,2C66) and readable/filter neighbor2C66 retain their
  existing scratch contract; they are not persistent-storage alternatives.

**Single best next step:** trace the dispatcher branch feeding ARM1F308/1F30A
into269E4, recover its operation/mode/request-address schema and all normal
entry conditions, then propagate those constraints through26A90..AD4. This is
one explicit mechanism whose current domain covers every candidate word; it
can establish SERVICE-ONLY or a concrete normal interval without another broad
RAM audit. Independently retain the1F5C Y-state X-cursor producer proof and
DMA/global AGU closure as subsequent obligations.

## Phase 19C-CHECKPOINT — 2026-10-06

**TESTED / BOUNDED-PROOF:** original-opcode address-only checkpoint slices are
implemented using the sealed Phase19A interpreter and authoritative memory hooks.
See notes/dsp-checkpoint-replay.md and notes/dsp-checkpoint-state.md.
Canonical traces: builds/phase19c-checkpoint/final/ and final-repeat/.

4164 cases execute24656 original opcodes per invocation:24576 at1F92..1F97,
64 cursor loads at1F89,14 zero-consumer instructions at203A..2040, and2
single204B consumer-calibration instructions. Unknown arithmetic/store data
remains SYMBOLIC/null. Numeric backing encodings are not stock values.
No authentic boot, full1F5C/1F90 DO loop or positive-count consumer loop executes.

The32 initialized cursor cells and each32-address body projection reproduce
X[2CCC,2CEC),[2CEC,2D0C),[2C02,2C22),[2C24,2C44), for M7FFFF/3FF.
There are no cursor-slice writes to X35F, X[340,360) or X[5F00,6000).
Both initialized-zero203A entries read35F0, load the four initial fields and
perform the Y prefetch before DO0 skips204B. One-word204B behavior is calibrated
separately with cleared destination0; no normal positive producer is invented.

These are PROVEN FOR CHECKPOINT DOMAIN address properties, not universal stock
invariants. Isolated slices do not replay inherited loop edges/stack/call paths
or async interference. Cursor/count/record/modifier preservation and parent
reachability remain UNRESOLVED. No family is removed from the universal blocker
set. X35F normal invariant / persistent high-X availability remain
NOT-YET-DETERMINED; service robustness remains NO. No Plaits PoC gate passes.

TESTED:13 canonical files identical;6 schema tests;5 native refusal gates;
protected original SYX/BIN and all ten extraction hashes intact; sealed203-file
core plus existing19A harness guard passes. Linked-library/binary hashes are
exported separately. Evidence: builds/phase19c-checkpoint/final-checks/reproducibility.json.

Next: qualify the complete1F5C nested-loop checkpoint stack/control relation
and symbolic-data interface to join the isolated body slices through original
DO/call instructions. Do not invent stack defaults or turn this into a ROM
search, hardware session, firmware patch or automatic scheduler replay.

## Phase 19C-FULLHELPER — 2026-10-06

**TESTED / BOUNDED-PROOF:** complete original P:[1F5C,1F9B) helper and
P:[C9D,CB8) callee now execute as joined control flow, including the real
caller JSR at1E80/1EE5 and natural return to1E82/1EE7.
See notes/dsp-full-helper-replay.md; canonical exports are
builds/phase19c-fullhelper/final/ and final-repeat/.

The admitted class is explicit: initialized caller pointers/counts/cursors,
retained M0..6FFFF and M7FFFF/3FF; healthy resident SP=SC=d, d3..7 before
caller; inactive LF/FV; opaque prefix and incoming LA/LC. These depths/flags
are SYMBOLIC finite structural class bindings, not recovered actual stock
stack values or normal-runtime invariants. Other/active/extension-dependent
classes refuse; no guessed ROM or reset stack is used.

40 cases per invocation execute385880 original opcodes,9647 per case
(including one caller JSR). Original DO yields16 contexts x32 stores at1F97,
64 initial clears,32 C9D calls and returns,66 DO executions. Complete helper
per case writes1728 X words and160 Y words. Actual LC countdowns, address
ordering, return frames, peak d+6, restored depth/LA/LC and unchanged opaque
prefix all match. Cursor words remain unchanged; all body intervals match
Phase19C-CHECKPOINT. Numeric arithmetic data/results remain SYMBOLIC/null.

PROVEN FOR CHECKPOINT DOMAIN: no read/write to X35F, X[340,360) or
X[5F00,6000). This is not an incoming-zero proof or universal ownership.
No natural helper-to203A chain or positive-count publisher is established.
Actual normal parent entry/stack/loop class, foreign mutations and async
interference remain UNRESOLVED. Universal X35F invariant/high-X persistence
and service robustness verdicts remain unchanged. No persistent Plaits layout
or firmware-implementation gate passes; only explicitly hypothetical design
assumptions remain possible. No Plaits work was performed.

TESTED:11 canonical exports match byte-for-byte, including full traces,
watched accesses and final symbolic CPU/X/Y state. Seven refusal gates pass;
protected SYX/BIN and all ten extraction hashes match; sealed203-file core
and19A harness source guard plus validated19A binary identity pass.
Evidence: builds/phase19c-fullhelper/checks/reproducibility.json.

Single best next step: resolve actual normal reachability and stack/loop entry
of parent1E15 feeding1E80/1EE5, connecting the local structural class to a
specific normal path. Do not artificially join203A or launch broad alias,
ROM-source, hardware, scheduler or Plaits work automatically.
