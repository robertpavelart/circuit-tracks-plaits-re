# Phase 6B — persistent-memory ownership and seam safety

## Phase 12 update — normal versus explicit service

[dsp-effect-memory.md](dsp-effect-memory.md) is current; machine evidence in
`builds/phase12/final/`. X[5F00,6000): **NORMAL-RUNTIME SAFE NOT-YET-DETERMINED**,
**SERVICE-ROBUST NO**.5E service overlap does not prevent a normal-only proof.
No verified normal occupancy or available256/128/64-word region.

**VERIFIED scoped domains:** effect algorithm wrappers set R7 Y840/880/9C0;
stock64 stores exclude cursor tables1820/1A10 under concrete linear/3FF modes.
M3 load584→restore5BE is straight-line.1E15's actual normal target/entry closure
still requires X95A..95F producer domains and preserved X9DB function table.
Selected coefficient lookup/read footprints and initialized buffers remain low
(output max2D0B; reviewed prefix max2DAE). Not a universal effects union.

**VERIFIED INIT table reconstruction:**31 RLE recordsP[2309,2599), external
X[74000,7BC00). Former decoded DMA-register references there are data; eight-
channel direct register census leaves INIT setup and NORMAL fixed rearm only.
Full normal indirect DMA/scratch exclusion remains open:202B/2043 loads an X
destination from X364+5*k,204B writes through it; normal producer/count bounds
must exclude the candidate and peripherals. No arbitrary high normal value
has been proved. Existing worker-private/shared separation remains unchanged.

Normal recovered mailbox families and256-word host staging exclude candidate
under their premises. Whole patch/scene/project persistence and all normal
indirect producers remain unresolved; full reboot clearing is INIT/reset.
Next: close202B destination records. No memory writes, firmware patches or port.

## Phase 10 update — 2026-10-06

See [dsp-high-x-audit.md](dsp-high-x-audit.md), canonical `builds/phase10/replay/`.
**UNRESOLVED:** private channel-zero X:[5F00,6000) persistence. No verified
available 256/128/64-word subrange and no normal occupancy witness established.
Startup clearing is **VERIFIED INIT-ONLY**, not a runtime disqualification.

**VERIFIED local bounds:** the eleven-word snapshot X:[1B16,1B21) saves X
coefficient/workspace cursors and Y generator/output cursors. The recovered
legacy-modulo workspace writes stay X:[2400,2800); selected export reads include
lookahead through2801. X:1D3A/B are saved Y-buffer pointers on reviewed paths.
**UNRESOLVED X effect mechanism:**1F68/6A load R1/R3 from Y:(R6+32/33), then
1F6E/6F and1F97 write X through loaded cursors. Entry reachability, all cursor
producers/modifiers and a universal effects maximum remain open.

**SOURCE-DERIVED + VERIFIED configuration:** eight DMA channels; DMA0 writes
Y:[29,2C), DMA1 reads Y:[21,24) and writes X peripheralFFFFA4. No private X
RAM destination in the reviewed setup. Previous X:21 staging interpretation
below is corrected. Arbitrary/indirect reconfiguration closure is still open.
ARM269E4 addressed-utility private domain below8000 includes the candidate;
normal/service conditions at caller1F30A remain unresolved. Shrinking the
candidate does not bypass that unknown. Worker-private low addresses remain
separate; known shared queue addresses do not prove a high-X collision.
Earlier next-step paragraphs are historical; trace that ARM dispatcher next.

## Phase 8 update — 2026-10-06

See [plaits-poc-memory.md](plaits-poc-memory.md) and builds/phase8/ for the
latest evidence and progressive64/128/256/512/1024-word allocation search.
Both high candidates remain **POTENTIALLY AVAILABLE / UNRESOLVED** after init;
neither has a verified safe subrange. Boot clearing remains **INIT-ONLY**.

**VERIFIED selected N=32/linear-AGU effect prefix:**P:CC4's loop touches
X:[2EF0,2F30),[1BB2,1BF2),[1BF2,1C32),Y:[840,880),[880,8C0),[9C0,A00).
The1157 coefficient arithmetic is further bounded:1166 y0=19,1168 MPY,
116A B1→n2 gives[-19,18] for any signed24 input; alternate branch uses3.
Conditional linear M2 yieldsX:[99E,9C4), excluding candidates. Following
retained buffer pointers/modifiers and helper footprints remain unresolved.
Retained table pointersX:1D3A/1D3B originate atP:1E15; normal reachability,
origins/modifiers/full extents remain **UNRESOLVED**, not runtime occupancy proof.

**SOURCE-DERIVED architectural correction:**M5=00FFFF selects legacy24-bit
linear addressing when SR.EMA=0, not a shared-bank or16-bit ring. Shared
[30000,38000) aliases P/X/Y under the conditional part map; private low addresses
on different cores are distinct. Selected12-voice queue endpoint30902 is a
profile estimate, not an all-mode capacity proof. Architectural wrap is2^24.
References: DSP56300FM4.5.1 and DSP56724RM SR.EMA; links in the Phase8 report.

Reviewed DMA setup2A2D..2A3D/rearm1BC/1BE uses staging Y:21/Y:29 (Phase10
correction). Three-transfer bounds are now source-derived and exported.
All reconfiguration exclusions remain **UNRESOLVED**; no complete DMA-visible
interval set across every possible configuration is claimed.
Hardware stack storage is distinct from X/Y heap, but software save/scratch
and maximum nesting remain unbounded. Eight explicit blocker families are exported.

X:[2C46,2C66) remains **VERIFIED RUNTIME OCCUPIED** global reused output scratch,
with readable/filter neighbor2C66. It cannot hold persistent state. Direct future
rendering is **HYPOTHESIS**, subject to numeric, live-state and lifetime proof.

**Phase 6C correction:** boot initialization does NOT disqualify persistent
allocation afterward. The strict no-initialization-use conclusions below are
historical and superseded by [dsp-runtime-ownership.md](dsp-runtime-ownership.md).
Both candidates are INIT-TOUCHED; availability after init still requires normal
runtime exclusion. Diagnostic capability and private worker numeric equality
are not channel-zero runtime ownership evidence. Reading Plaits only for a
conditional resource comparison is now permitted by the readiness gate;
implementation/fit and safe allocation remain unproved.

2026-10-05. Static analysis only; no DSP execution, device access, transmission,
patches, original/ edits or Plaits work. DSP ranges are half-open 24-bit-word
addresses. **VERIFIED** denotes instruction-supported static evidence; selected
path and device-map premises are stated separately.

**Result: NOT-YET-DETERMINED for a resource-qualified comparison.** Neither
candidate qualifies as VERIFIED AVAILABLE under the requested criteria.
Both are cleared during normal startup; runtime ownership has not been proved
exclusive. This is not proof that the physical RAM is persistently occupied.

## Reproduction and coverage

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/ct_memory_ownership.py --output-dir builds/phase6b
```

Choose a fresh directory; existing outputs and original/ targets are refused.
The script verifies input hashes, decoding/roundtrip, encoded instruction bytes
and copied-table hashes. It exports:

- `absolute-intervals.csv`: 1,102 decoded X/Y absolute operands across all four images.
- `pointer-immediates.csv`: 845 immediate address-register values; values are not assumed to be pointers.
- `indirect-origins.csv`: 2,766 indirect operands with lexical origin hints and unresolved address envelopes.
- `hardware-loops.csv`: 219 DO/REP entries with count expressions and indirect body counts.
- `reachable-intervals.csv`, `witnesses.json`: reviewed affine address propagation and explicit base/count/linear-AGU premises.
- `initialized-values.csv`: every word in the four previously reconstructed P-to-X copies, with hashes checked; not a complete initialization snapshot.
- `host-call-candidates.json`: existing ARM direct-call candidates for addressed services; not a proof of complete callers or argument bounds.
- `seam-clobbers.csv`, `region-ledger.csv`, `ownership.json`, `reviewed-paths.asm`.

**Coverage limit:** inventory is exhaustive for the *canonical decoded listing
rows*, not every reachable instruction or initialized pointer in the firmware.
Code/data ambiguity and unreviewed indirect entries remain. All unknown indirect
origins conservatively cover [0,1000000), not an asserted actual access range.
Lexical origins are hints, never interprocedural range proofs. The affine
analyzer rejects unsupported control flow in its reviewed bodies and propagates
pointer steps mathematically; it does not emulate DSP instructions. A complete
global points-to proof and all-loop bound resolution remain **UNRESOLVED**.

## 1. Initialization and candidate classification

**VERIFIED:** normal startup P:25DE calls P:2779. P:2779..2781 sets
m0..m7=FFFF; P:2782 sets r0=0; P:2784 sets x1=6000; P:2786 performs
DO x1 with X:(r0) store at 2788 and Y:(r0)+ store at 2789. Address propagation
gives X:[0,6000), Y:[0,6000), stride one, 24,576 iterations.
Both candidate ranges are written once on this startup path. P:278A..2791
also clears shared X:[30000,38000), 32,768 iterations. They are not preserved
through reinitialization/reload. No heap allocator was identified; absence of
one is not a proof of fixed scratch bounds.

| Candidate | Startup | Runtime ownership | Qualification |
|---|---|---|---|
| X:[4000,6000), 8192 words | VERIFIED clear writes entire interval | UNRESOLVED indirect/host bounds | Fails strict no-initialization-use criterion; not VERIFIED AVAILABLE |
| Y:[3000,4000), 4096 words | VERIFIED clear writes entire interval | UNRESOLVED effects/indirect/host bounds | Fails strict no-initialization-use criterion; not VERIFIED AVAILABLE |
| Shared:[34003,38000), 16381 words | VERIFIED normal clear | UNRESOLVED queue/service extents and physical aliases | Not VERIFIED AVAILABLE |

No subrange can evade these initialization writes. There is no basis to label
them VERIFIED OCCUPIED by persistent runtime data or VERIFIED RESERVED for
an undocumented purpose; their *runtime* classification is **UNRESOLVED**.
The earlier POTENTIALLY AVAILABLE label is retained only as a future allocation
candidate after startup, with a new ownership proof and explicit reset policy.
Y:[4000,6000) lies outside the conditional core0 Y RAM map and is not a
storage candidate merely because the program attempts to clear it.

**Largest VERIFIED AVAILABLE range:** X none (0 words), Y none (0 words).
No 256/512/1024/2048/4096-word contiguous or split allocation has been proved.
This reports proof status, not physical exhaustion. No shrinking to a safe
subrange is justified by the unresolved indirect envelopes.

## 2. Pointer and loop evidence

Reviewed finite intervals are in the export, including startup clears,
post-result copy X:[2D2E,2D4E)→X:[2C46,2C66), gain-current X:5BD,
bank0 sum X:[2DF0,2E10), and cached interleaved Y lane stores for N=32.
Their origins, count, stride, phase/caller and premises accompany the rows.
Runtime counts depend on initialized block constants and selected paths;
host-addressed changes have not been excluded globally.

**VERIFIED caution on apparent pointers:** P:27AF r0=3C00 is stored to
X:FFFE53; P:27BC r0=4900 goes to X:FFFE1A; P:27CA..27F2 values
4063/4863/5863 go to X:FFFE4B, followed by X:40000 reads. Under the
[DSP56724 reference manual](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf),
these are EMC refresh/option/SDRAM mode registers, not accesses to low X/Y
RAM at those numeric values. Classifying them as candidate RAM pointers would
be wrong. Likewise X:3235/3237/3239 global bases are not Y pointers merely
because they numerically fall inside the Y candidate interval.

Dynamic DO x:(r0)+ at P:7C8, indexed parameter/table accesses, retained
effect pointers, mailbox-derived pointers and unknown call contexts remain
unresolved. No absence-of-absolute-access argument establishes availability.
The existing coarse region ledger covers state/tables, rings, scratch, ISR
save areas and shared/external regions; it is an overlapping activity ledger,
not a complete partition. Table-copy value exports cannot substitute for all
runtime-generated pointers.

## 3. Worker and physical address correlation

**VERIFIED worker code:** r5 begins at 30002 (P:105). Shared endpoint
X:30000 controls DO count at P:11E via endpoint−r5. P:120 loads a queued
word into r0; P:125 reads X:(r0); P:126 replaces X:(r5)+ with that result.
No source-address validation appears in this fetch body. m5=FFFF is set at
10B. Queue endpoint and source values are data-controlled; no global bound
on their arithmetic progression has been proved. Its one DO loop is not a
fixed maximum-work proof. ICC at Y:FFFFD0/D1/D7 carries state and completion.

Wrapper P:12B..16A saves/restores registers at private Y:[0,16) (22 words)
with r0=0, m0=FFFF; P:16B is RTS. Normal worker has no SHI receive handler
analogous to normal channel-zero's addressed service. Generic queued X fetches
do not constitute a Y table-access path.

**Conditional physical interpretation:** separate cores have private low X/Y
RAM; equal numeric addresses on different cores do not identify the same
storage. P/X/Y:[30000,38000) instead aliases shared physical memory. A worker
X:4000 read therefore is not automatically a read of channel-zero X:4000.
Exact physical channel/core assignment and external mapping remain unresolved.
No claim that arbitrary worker fetches alone clobber candidate core0 RAM is
made. Queue writes can only be excluded globally after endpoint/wrap bounds
are proved; private/shared correlation must remain part of that proof.

## 4. Host protocol, table jobs and diagnostics

**VERIFIED normal ARM construction:** 080292DC transmits ordinary address
bytes from its argument; 080292F8 takes destination r2, compares the cache,
then invokes address setup and data transmission. DSP P:181 masks the
ordinary address with 7FFF, saves flags at 185 and pointer at 186. P:19B
writes Y or P:19D writes X, selected by bit15. Extended/paged branches have
larger address reach and inherited selector state. Read-next and write-next
increment a linear address without a candidate-range guard.

Thus normal protocol *can legally express* X:4000..5FFF and Y:3000..3FFF.
This is not proof that a normal stock caller supplies them. Reviewed fixed
event/coefficient/table/ring destinations are documented in the existing
command/descriptor maps; complete normal-call argument propagation remains
**UNRESOLVED**. The candidate caller export retains this distinction.

**VERIFIED mailbox reach:** P:1C53..1C5F reads Y:2C, separates selector
low nibble, computes r5=((W & 7FFFF0)<<1), low 24 bits. Selector6
P:1CB2..1CB5 copies 512 X:C00 words to Y:(r5)+ without a destination
range check in that branch. Table-generation selectors use the same derived
base and asynchronous retained state. Normal ARM 08035E28's reviewed pointer
list starts 100000, stride 28800, and publishes external table jobs. No normal
candidate-range mailbox request was proved; no complete exclusion was proved.

Selection1 listings are separately tagged diagnostics in every inventory.
Their low-memory tests must not be combined with Selection0 ownership as if
both run concurrently. Loading Selection0 again invokes its destructive-to-state
startup clear. No normal persistent reset-survival contract is established.

DMA reviewed setup P:2A2D..2A3D and rearm P:1BC/1BE target staging Y:21,
Y:29 and ESAI endpoints; ISR P:1C7..1CA uses the 1000..13FF ring. No reviewed
normal direct DMA candidate destination exists. Arbitrary host register writes,
unreviewed indirect programming and exact DMA arbitration are not excluded.
Architectural hardware return/loop stack is separate from a guessed RAM heap;
all software save/scratch pointer growth is not yet globally bounded.

## 5. Program extension

**VERIFIED ARM transport:** 08029208/29210 reads the count's low two bytes;
08029224 adds two header words; the chunk loop sends at most AA (170) words
from input pointer+3*index. A hypothetical 4000-word payload needs 4002
stream words, 49158 bytes, within these count/chunk calculations; no uploader
semantic change is required. Header load/start remains P:0.

Under the conditional core0 memory mode, this fills P:[0,4000), adding
5538 words beyond the current end 2A5E without moving existing DSP addresses.
The other normal record is sent to channel1, not deliberately concatenated
into the same P space; physical core assignment is still conditional. Existing
vector/constant addresses could remain unchanged; this does not prove appended
instructions, new references or ROM/memory-mode acceptance are safe.

**VERIFIED layout conflict in ARM flash:** original offset1F0 plus expanded
49158-byte stream ends at C1F6; channel1 currently starts8110. Therefore
in-place growth would overlap the following stored stream. Repacking stream
data and updating ARM metadata would be necessary. No patch is made.

**Overall extension status: LIKELY POSSIBLE, conditional.** ARM format/count
transport is supported; complete image extension remains **UNRESOLVED** until
physical mode/ROM acceptance and firmware data relocation are established.
It is not VERIFIED POSSIBLE merely because a counter fits.

## 6. Seam clobber contract and guard reads

Scope: selected mode0 post path. E=57A+4A*i, S=59F+28*i.
The machine-readable formal table is `seam-clobbers.csv`.

| Register/state | Live at 9DD? | Preservation / restoration evidence |
|---|---|---|
| r0 | VERIFIED live | Must be X coefficient cursor E+31; first instruction reads it |
| r4 | VERIFIED live | Must be Y post-state cursor S+C; AA8/BDD consume and advance |
| r1/r3 incoming values | Dead on selected mode0 entry | A19/A1B install buffers before selected reads; not all-mode permission |
| r2/r5/r6/r7 | Incoming need not established on selected witness | Many local resets; conservatively preserve pending full interprocedural/all-mode proof |
| Incoming A/condition codes | Dead at immediate entry | 9DD overwrites A; 9DE CMP defines branch flags |
| B/x0/x1/y0/y1 | UNRESOLVED general clobber set | Helpers redefine selected operands; no universal liveness proof |
| m0/m4 | VERIFIED addressing dependency | Numeric pointers alone are insufficient; preserve expected linear addressing |
| Other m registers | UNRESOLVED all paths | Selected AA8 changes/restores m5; other AGU requirements remain |
| n registers | UNRESOLVED all paths | Several assigned in AA8/BDD/filter/mix; no blanket caller-clobber permission |
| SR/MR modes | VERIFIED live | Preserve scaling/rounding/interrupt mask; CA2 sets scaling, CB6 clears |
| Return/loop stack, SP/SC/SSH/SSL/LA/LC | VERIFIED calling-context obligation | Balanced calls and nested DO/REP; stock consumer does not repair corruption |
| X:CC, X:2C, counts/tables/filter/gain/lifecycle | VERIFIED live shared state | Downstream and scheduler consumers require validity; exact all-mode field set unresolved |
| Bitmap/queue/ICC state | VERIFIED invariant | Must match request/completion scheduling; not repaired by filling mono buffer |

**VERIFIED prefetch:** BE2 loads first raw word; BE6 executes 32 further
loads while BE7 stores prior computed sample and prepares the next. Total
address envelope is X:[2C46,2C67), including X:2C66. A89/A93 similarly
prefetch 33 raw words during 32 gain/mix outputs. Last prefetched value is
unused for the selected block output, but the memory must be readable. The
32-word output contract remains valid; a relocated/inaccessible boundary at
2C66 would violate the read contract. Adjacent scratch must not be reclaimed
without checking all such lookahead accesses.

## 7. Worker bypass obligations

The stock no-lookup branch establishes a narrowly verified schedule:

1. Global P:759 clears both group sums, resets queue using ICC bit23
   handshake, initializes X:2F31/2F32 and auxiliary2F34. It remains required
   by the existing scheduler even if one voice submits no requests.
2. Request pass P:198D sets pass bit23 in X:2F30. P:791..799 ORs the
   current context bit into its pending bitmap before lane processing.
3. Mode<8 P:7B4 skips cache-copy during request; P:99E..9A4 returns without
   post/mix. It does not submit P:775 work or advance lookup counters there.
4. P:19BF clears pass bit23; its bitmap shift/test selects completion calls.
   Completion P:788..78D clears 96 lane words, and P:7BA/7BB supplies cached
   lane data without waiting for worker fetches. Pointer/counter bookkeeping
   at P:99A..99D still occurs; post/gain/mix executes only on completion.
5. Selected lookup mode normally commits phase at P:7F9 during completion,
   not request; P:980..998 can update prepared coefficient fields. A direct
   mono producer bypassing these instructions needs an explicit compatible
   state policy, not an assumed automatic stock update. Mode<8 is not proof
   that arbitrary lookup-mode phase obligations can be discarded.

For a mono-only producer, lane placeholders are unnecessary only if *all*
lane consumers are bypassed; this is **HYPOTHESIS**, not a verified patch.
Keep other voices/table jobs, mailbox completion, bitmap consumption and
queue producer/consumer consistency intact. No global worker removal or
safe all-mode alternate producer has been proved.

## 8. Timing categories and revised gates

**KNOWN MINIMUM / selected-profile subtotals:** 4355 channel-zero issued
instructions per active voice in reviewed major loops. Partition of those
counted bodies: request 750; completion generation/ramp/combination 2197;
retained post/gain/mix 1408. This is not the entire request/completion pass.
The post-result copy adds a separate 64 instructions on the selected path.
Worker fetch adds1152 issued instructions/voice on its core, potentially
overlapping request/completion work. Idle/release/mode changes alter costs.

**KNOWN BOUNDED COST:** the explicitly counted loop bodies under N=32 and
the stated three-lane/one-repeat/profile premises. Request descriptor traversal
covers fourteen eight-word descriptors; completion examines twelve context bits.
These bound traversal iterations, not handler execution time. Ring ISR body
is finite but interrupt count during a stalled service period is not bounded.

**UNBOUNDED/UNKNOWN:** P:768..76F ICC reset handshake, P:775 completion
polling, dynamic lane-repeat counts, main-loop host/table jobs, all group/effect
branches, memory wait states, interrupt interference and full helper expansions.
No finite worst-case service bound or substitute-generation window follows.
The nominal 163840-cycle/32-frame period remains conditional on the Phase6
clock-source chain; it is not a proven available execution window. Deadline
remains output-ring ISR consumption, not a new DMA half/full event.

| Gate | Answer |
|---|---|
| A: ≥512 persistent X/Y words verified? | NOT-YET-DETERMINED physical availability; no verified allocation exists |
| B: ≥1024 verified? | NOT-YET-DETERMINED; same missing proof |
| C: normal-loader extension supported? | NOT-YET-DETERMINED overall; ARM count/transport supports it, mode/ROM/layout proof incomplete |
| D: sufficient clobber contract? | NOT-YET-DETERMINED; selected live pointers and guard reads known, all-mode proof missing |
| E: safe lookup bypass? | NOT-YET-DETERMINED for alternate producer; stock request-free branch and obligations verified |
| F: bounded generation window? | NOT-YET-DETERMINED; synchronization and total service bounds missing |
| G: comparison without more archaeology? | NOT-YET-DETERMINED; no hard state or headroom fit can yet be decided |

**Single best next step:** close normal ARM addressed-service call arguments
and mailbox destination ranges, starting with 080292F8/08029314/08029528
and Y:2C jobs. Export proven normal destination intervals and separate service
mode callers. This removes a concrete normal-operation alias blocker before
the remaining DSP effects/indirect-access proof. Any later availability claim
must also explicitly account for the already proved startup clear.
