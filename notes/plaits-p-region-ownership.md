# Phase 20C4-PREGION — one appended P object

## Current follow-up: Phase20C5-ENFORCEDSTATE - 2026-10-07

**PARTIAL design; natural ownership REFUSED remains.** Prefer explicit
P:[3FF0,3FF7) ownership by software mediation. Exactly two domains compared;
X:[57B,582) takeover would require a new request/auxiliary/guard contract and
is not preferred. No memory reservation, patch, load, repack or flash. Owned
Circuit state words remain0.

Whole202B and198 guard clones provide control sites. Review all eight DMA
configurations, prohibit P sources/destinations during ownership, pin audio0/1
and admit safe X/Y2..7 instead of disabling them wholesale. RM115 documents
DTD6/7; FM205 limits DMA I/O accesses to TX/RX data registers, not general DMA
control writes. CPU actual-EA/control coverage, typed owner accesses, computed
flow and trusted pre-quiescence entry remain unclosed. DE0 alone is insufficient.
The344 decoded indirect X/L candidates are obligations, not proved normal writers.

One-way epoch and exact seven-word init are defined. Extra P26 save/P3 spill/P3
control/P30 policy/P32 shadow/P1 fault objects are counted,102P total. Complete
cost remains null:866P partial/1626P planning versus5374 conditional code capacity;
illustrative29548 cycles plus unknown terms uses unproved Q1/N20. Offline patched
construction NO; flashing NO. Next is a finite source/ISA mediation certificate,
not another memory search. See current enforced-state/guard/takeover notes and
final-v3/repeat-v3/checks-v3 evidence. The Phase20C4 report below is preserved.

2026-10-07. **Overall: REFUSED. Ownership classification: CONDITIONAL.**
The exact candidate is **P:[0x3FF0,0x3FF7)**, seven 24-bit words. No normal
collision is proved, but normal non-interference is not proved either. Qualified
stock P words remain **0**; offline patch construction is **not justified**.
This is an insufficient-proof verdict, not proof that P-backed state is impossible.

Strictly offline: no hardware, MIDI/SysEx, OnCE/JTAG/SWD, firmware execution,
repack, flash-ready image, original-file changes, renderer redesign or broad
X/P free-memory search. Existing numerical qualification is reused; the 43-case
suite was not rerun. No new state-address operand or initialized firmware object
was emitted. All earlier evidence remains intact.

Evidence: `builds/phase20c-pregion/final-v1/`, `repeat-v1/`, `checks-v1/`.
Thirteen requested reports plus source witnesses, primary-manual pages,
candidate-specific obligations and ranked alternatives. Tools:
`tools/ct_pregion_audit.py`, `tools/ct_pregion_verify.py`; twelve focused tests in
`emulator/tests/test_pregion_ownership.py`.

## A. Exact candidate and layout

**CALCULATED / CONDITIONAL:** use one 16-word-aligned block near the end of the
documented core-0, MSW1=1/MSW0=0/MS=1 map, P:[0,0x4000). The region is above the
existing high-address standalone renderer, P:[0x2A5E,0x2C83), and the previous
713-word partial module ending at 0x2D27. Absolute MOVEM requires word alignment;
16-word alignment is a layout preference, not an ISA requirement.

| Proposed object component | Half-open P range | Status |
|---|---|---|
| Future appended code budget | [0x2A5E,0x3FEC) | 5,518 words; complete glue must fit, not yet assembled |
| Terminal transfer fence | [0x3FEC,0x3FEE) | Must restore live context and transfer to natural continuation; design only |
| Explicit pre-state padding | [0x3FEE,0x3FF0) | Two owned NOP words, proposed |
| Seven persistent state cells | **[0x3FF0,0x3FF7)** | This phase's only candidate |
| Explicit post-state padding | [0x3FF7,0x3FF9) | Two owned NOP words, proposed |
| Remaining nominal RAM tail | [0x3FF9,0x4000) | No ownership claim |

Every instruction/extension, branch, call, loop end, dispatch target and copy
must respect these boundaries. A complete appended module must exit before the
data; the standalone harness's stop at `done` is not an actual stock continuation.
The fence is a requirement, not constructed patch code. No ownership of the
whole appended range is asserted. Existing MOVEM tests used P:[0x2D29,0x2D30);
they are behavioral support and do not constitute execution at this new address.

## B. Loader ownership

**VERIFIED bytes and ARM control flow:** ARM 0x08029260 calls the sender at
0x08029200 in this order: bootstrap/channel0 at 0x08029284, selected/channel0 at
0x08029294, selected/channel1 at 0x080292A6. The sender uses one BE24 count word,
one BE24 load word and exactly that count of BE24 program words. Its ARM count
arithmetic consumes the low 16-bit count, adds the two headers and sends up to
0xAA words per chunk. Selected pointers are at 0x08029700+4*selection, with +8
for channel1. Channel1 is a different transport endpoint, not a following P
record in channel0; exact board endpoint/core assignment remains conditional.

| Stream | Load | Payload count | End P | Candidate overlap |
|---|---:|---:|---:|---|
| Bootstrap/channel0 | 0 | 0x8 | 0x8 | No |
| Selection0/channel0 | 0 | 0x2A5E | 0x2A5E | No |
| Selection0/channel1 | 0 | 0x16C | 0x16C | No, different endpoint |
| Selection1/channel0 | 0 | 0x328 | 0x328 | No direct count overlap |
| Selection1/channel1 | 0 | 0x168 | 0x168 | No, different endpoint |
| Proposed extended Selection0/channel0 | 0 | 0x3FF9 | 0x3FF9 | All seven cells |

**SOURCE-DERIVED / CONDITIONAL:** DSP56724RM PDF103, Table5-5 documents contiguous
PRAM loading followed by execution at the load address. Thus a correctly
constructed, completed 0x3FF9-word object would initialize all seven literals
once **per load epoch**, and overwrite them on **every** payload reload. That
explicit reset is acceptable. The current stock object does not initialize them.

The proposed framed size is **49,137 bytes**, count+headers=0x3FFB words; it fits
the reviewed non-wrapping 16-bit sender limit and the conditional PRAM size.
These are arithmetic results, not an emitted stream. Existing channel1 begins
at ARM image offset0x8110, exactly where current channel0 ends; any in-place
extension overlaps it. A future enlarged object requires whole-object relocation
and independent container/recovery qualification. No relocation/repack occurred.

## C–E. P writers, DMA destinations and reconfiguration

**VERIFIED scoped instruction inventory:** the byte-checked main listing has one
apparent explicit P store, P:0x28DE. It is **data**, copied to Y by 0x28D3/0x28D7/
0x28D9 from P:[0x28DD,0x29EC); it is not a recovered executable MOVEP writer.
No executable direct MOVEM/MOVEP-to-P was recovered in this listing. This is
not a complete CFG, ROM or self-modification certificate.

**SOURCE-DERIVED:** DSP56724RM PDF79/80 and115/116 define **eight** DMA channels,
including6/7. For channel c: DCR=0xFFFFEC−4*c, DCO=DCR+1, DDR=DCR+2,
DSR=DCR+3, in X peripheral space. Y registers at numerically similar addresses
belong to ICC/other blocks. FM PDF195/200/201 supplies the DMA control fields:
DDS bits3:2 select X=0/Y=1/**P=2**; DE is23; DRS is15:11. All eight channels can
architecturally target P. That capability is not an attained normal configuration.

| Channel | Recovered configuration | Trigger / extent | Candidate conclusion |
|---|---|---|---|
| 0 | DCR0=0x285AC4, then DE set at P2A3D; DSR0=0xFFFFA8; DDR0=0x29 | DRS11 ESAI receive, DCO2 ⇒ three transfers, destination Y:[0x29,0x2C) per reviewed block | **BOUNDED-PROOF NO** while DDS remains Y |
| 1 | DCR1=0x286251, then DE set at P2A3E; DSR1=0x21; DDR1=0xFFFFA4 | DRS12 ESAI transmit, DCO2 ⇒ three transfers, fixed X peripheral destination | **BOUNDED-PROOF NO** while DDS remains X |
| 2–7 | No recovered executable direct setup/enable in the selected listing | Post-ROM DE/DDS/DDR/count/offset/trigger state unknown | **UNRESOLVED**, not assumed disabled |

DTM5 uses peripheral word requests and repeats without clearing DE at each block
end. Hardware may advance the cursors. Space alone excludes the candidate for
the two reviewed configurations even if more blocks occur before ISR rearm.
It does not prove DDS remains unchanged.

**VERIFIED direct normal register writers:** audio ISR P1BC sets **DDR0=0x29**;
P1BE sets **DSR1=0x21**, not DDR1. The other ten executable direct references
are setup/enable P2A2D..2A3E. Initialization table data is excluded. The report
projects reconfiguration obligations onto exactly the32 channel registers;
shared DOR offsets remain relevant for an unknown 2D/3D mode.

**Largest exact normal blocker:** P203A loads count X35F; P2040 latches it into
LC. At P2043, R4 comes from **X[0x364+5*k]** under the recorded linear table
premise. P2048 reads X:(R4), and **P204B stores B to X:(R4)** without a mask or
destination clamp. The previous Phase19C-P204B result still has no recovered
normal nonzero count, active record constructor, attained destination or normal
stored-value domain. It also has no universal zero-count preservation proof.

For each DMA register at address a, the unresolved necessary condition is:

`an active normal record has X[0x364+5*k] == a`

with a compatible stored value, enable/trigger and transfer state. A DCR/DDR/
count mutation could permit a P transfer into the seven cells. **No such normal
record or P collision has been recovered.** Conversely, it cannot be excluded
by declaring DMA configuration permanent or by substituting cleared records
for all runtime records. A zero-count checkpoint has an empty P204B write set
only in its qualified zero-skip class.

**Second precise register-reach obligation:** the SHI paged path P171/175 is
`saved_cursor=((page<<8)-2)&0xFFFFFF`, followed by X/Y writes at P19D/19B.
It is not the separate P17B extended path's 0x3FFFF mask. A hypothetical pageFFFF
gives0xFFFEFE; finite cursor offsets can numerically reach DMA registers.
This is a necessary address equation, not a normal pageFFFF/transfer/context
witness. Complete normal ARM argument/cursor/cache/order closure remains open.

**Channels2–7:** documented reset DE=0 is not evidence of post-ROM DE=0. No
authentic matching ROM cleanup/register contract is available. No count,
destination or trigger was invented to fill that gap.

## F–G. Service/debug and ROM

**VERIFIED / BOUNDED-PROOF local exclusions:** recovered service5E at ARM269E4
can run while Selection0 is active, before the later enable guard. It directly
writes only private X/Y or shared RAM through P19B/19D. Under the documented
map, shared PXY:[0x30000,0x38000) is distinct from this low private P object.
Coherent accepted starts/counts miss the DMA peripheral registers; saved-cursor
and first cached-write ordering are separate unresolved obligations.

The recovered private service data word is always0; the shared word is the
consumed byte<<8. Even if such a store aliased a DCR, its **DDS=0 and DE=0**,
so it cannot itself create an enabled P-destination DMA configuration. This
value proof does not certify every service side effect or erase unknown prior
DMA/ROM states. X/Y readback also changes cursor/save state and can interact
with later cached writes; it is not a state-free observation path.

Recovered diagnostic commands5C/5D/71 can call1F51E at26962/2698A/269AA to load
the fixed Selection1 program. Request60's mode path and the boot caller1D582
also reach1F51E. Returning Selection0 uses1F532→1F554→1F568→29260(r0=0).
These transitions end the ownership epoch; they are not ordinary audio-block
stores. Short Selection1 counts do not touch this candidate directly, but
tail persistence across its ROM/mode/DMA changes is not guaranteed. No arbitrary
private-P write command was recovered; that nonhit is not a universal proof.

**ROM: UNRESOLVED.** The eight-word shim explicitly changes OMR and jumps
to PFFFFFE. The normal main listing has no recovered direct ROM call, but all
computed targets, saved returns and exception ancestry are not closed. The
documented boot loading behavior does not prove later ROM write exclusion or
all-channel/mode cleanup. No unobservable ROM path is classified safe.

## H–J. Memory mode, cache, execution and guards

**SOURCE-DERIVED / CONDITIONAL:** RM PDF76/77 maps the candidate into writable
core-0 PRAM in MSW1=1/MSW0=0/MS=1. Other switch combinations redistribute RAM
banks; some cannot contain the candidate. The shim sets these bits before ROM,
but authentic application-entry OMR and all normal mode preservation remain
unproved. No executable direct OMR destination was recovered in the reviewed
main listing; that does not close computed execution or code mutation.

**New manual caveat:** RM PDF95 lists an on-chip cache among PCU features, but
RM PDF100 Table5-2 marks **SR bit19 reserved**, where generic FM defines CE.
Do not transplant generic cache-enable control or emulator constructor defaults
to this device. FM153/154 documents PMOVE read/write cache/backing behavior and
non-coherent DMA/cache writes; applicability and actual chip cache control
remain unresolved. The passing standalone interpreter does not answer that
hardware question. Under a fixed compatible PRAM map, MOVEM read/write is legal;
mode stability, other-writer exclusion and device-specific behavior are still gates.

**BOUNDED-PROOF vector exclusion:** FM PDF101 forces VBA[7:0]=0. RM PDF115 marks
interrupt offsetsC0..FA reserved; valid FC/FE slots lie beyond the candidate.
Candidate offsetsF0..F6 therefore cannot be valid documented vector starts or
their second words for **any aligned VBA**, without guessing its value. Handler
computed transfers and RTS/RTI stack restoration remain separate obligations.

No decoded direct branch, JSR or loop end in the scoped original listing targets
the candidate. The final original word P2A5D is RTS, not a tail fall-through.
Seven decoded computed transfers remain: DB6, DBD, DC5, DCD, DEC, DF9,19AC.
Known initial dispatch values are low P addresses, including twelve281 descriptors,
202B,1A2B and the55 entries copied to X:[9DB,A12). **All-normal index/table/
descriptor/return preservation is UNRESOLVED.** A scan nonhit is not a complete
execution-target proof. No normal entry into the seven data words is demonstrated.

**Guard recommendation:** at least two explicit words on each side plus a terminal
transfer and strict no-target/no-loop/no-copy-overrun rules. Two words cover the
existing decoder's extension/lookahead requirement. RM95's seven-stage pipeline
and FM150/151's external burst of up to four reads do not establish a universal
two-word hardware padding bound. Prefetch is a read, not a state writer; neither
padding nor alignment prevents a computed jump or DMA write. Complete appended
glue/copy counts and hardware prefetch behavior are unqualified.

## K. Reload semantics

| Event | Required state policy | Qualification |
|---|---|---|
| Normal audio blocks | Retain all seven | Standalone continuity TESTED; all-normal stock preservation UNRESOLVED |
| Project load | Retain unless an explicit DSP reload occurs | Complete loader/mode/foreign-write ancestry UNRESOLVED |
| Patch load | Retain or explicitly reseed by a defined lifecycle | Reviewed parameter path has no P upload; universal preservation UNRESOLVED |
| Selection0 payload reload | Reset all seven once from exact literals | CONDITIONAL on the future complete0x3FF9-word owned object |
| Diagnostic selection | Suspend ownership; do not run the PoC | VERIFIED selection path; no tail-persistence assumption |
| Return Selection0 | Reload and reseed before rendering | Verified call chain; enlarged object not implemented |
| Full restart | New owned-load epoch, then exact initialization | CONDITIONAL; unknown RAM is not assumed zero |

Exact literals stay `[0,0,0x200000,0,0xA3D7,0x200000,0]`. No eighth flag is
needed **if** the load/activation epoch is guaranteed. That epoch is not yet
qualified, so no first-PoC allocation assumption is upgraded.

## L–P. Verdict, ranked alternatives and next step

**Ownership: CONDITIONAL. Overall qualification: REFUSED.**
Seven-word P state now qualified: **NO**. Offline patch construction justified:
**NO**. The result neither proves a collision nor certifies this block as safe.
The largest blocker is normal DMA-register preservation via the exact
P204B record/count/destination domain; paged SHI ordering and unknown post-ROM
channels2–7 independently prevent universal DMA exclusion. Computed execution,
mode/ROM and complete object/epoch proof are also unfinished.

No additional memory search is started. Remaining architectures, all design-only:

1. **B — temporary instrumented software state object.** Prefer an explicit
   object plus DMA admission/enforcement and software write-coverage contract,
   using external interfaces only. Monitoring alone cannot prove ownership;
   complete mediation, observer cost, recovery and future authorization are required.
2. **A — one-way selected-generator takeover.** Transfers ownership of a bounded
   selected generator record, but requires disabling its producers/readers in
   both passes, host/foreign protection and a new auxiliary/lifecycle contract.
   It conflicts with retaining all original selected-generator work unchanged.
3. **C — controlled replacement payload with explicit whole-module ownership.**
   A software-only mode/loader/DMA/dispatch contract could avoid inherited opaque
   ownership, but preserving Synth2/stock processing and recovery becomes much
   harder. It is the largest redesign and is not the current mono PoC.

**Single best next step:** specify architectureB's temporary software-enforced
object and DMA configuration admission/coverage contract offline. Require a finite
proof of all applicable write paths before construction; do not launch another
broad memory census or recommend OnCE/JTAG/SWD acquisition. No patch is built now.

## Validation and reproduction

**VERIFIED / TESTED:**8,682 original DSP listing rows and727 ARM rows byte-check;
12 direct executable DMA references, all8 channels and32 targeted channel registers;
12 focused arithmetic/source/refusal tests; overwrite refusal; all13 requested
reports;56 exported members repeat byte-for-byte;740 guarded inputs unchanged.
These tests validate evidence and bounded implications, not the unresolved
normal reachable state. CPU instructions executed0; no new numeric run or seed.

```powershell
$taskPython='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $taskPython -B tools/ct_pregion_audit.py --output-dir builds/phase20c-pregion/new-final
& $taskPython -B tools/ct_pregion_audit.py --output-dir builds/phase20c-pregion/new-repeat
& $taskPython -B tools/ct_pregion_verify.py --first builds/phase20c-pregion/new-final --repeat builds/phase20c-pregion/new-repeat --out builds/phase20c-pregion/new-checks
```

Fresh destinations required. Pinned local manuals/tools only; no download,
installation, firmware builder or hardware interface. Earlier probe-v1 stops
at an inventory assertion; probe-v2 is superseded by the finalized vector and
additional diagnostic/reload evidence. Earlier reports are preserved.
