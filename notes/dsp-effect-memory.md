# Phase 12 — normal effect/scratch audit and independent safety levels

## Phase 19C-TARGETBRIDGE — table persistence and target sets

2026-10-06. Current report: [dsp-effect-target-bridge.md](dsp-effect-target-bridge.md),
canonical evidence builds/phase19c-targetbridge/final-v2/ and checks-v2/.
**VERIFIED conditional:**55 initialized targets generate six wrapper targets
DB7/DCF/DD3/DDC/DE6/DF3 and eleven algorithm targets, none1E15. DDC's copy
falls throughDE6; DCF reachesDEC through its JSRDDC; DD3 reachesDEC through
JSRDE6. All40 initialized row/stage positions yield an algorithm call under
reviewed counts/returns. DC5/DCD wrappers are absent from initialized valid rows.
**UNRESOLVED normal:**selector domains, target-table/descriptor0 preservation
and all generic writer contexts. Table classification UNRESOLVED; recovered
SERVICE-ONLY5E can zero its words, but service capability does not prove that
normal mutation is excluded. No direct absolute X/L writer names requested
cells. No recovered normal parameter/job destination overlaps them; X parameter
maximum959 ends before95A. SHI19D and record204B remain concrete independent
unclosed mechanisms.640 conditional records/16 reproducible exports/7 tests
pass;0 DSP instructions. No parent bridge or active-loop replay justified.

## Phase 13 update — descriptor count correction

Current scoped report: [dsp-indirect-write-204b.md](dsp-indirect-write-204b.md),
evidence `builds/phase13/final/`, reusable `tools/ct_indirect_204b_audit.py`.
**VERIFIED:**204B performs one X-word read/modify/write per five-word record.
ARM286E4 explicitly sets the compiled/global count35F+172*bank to **zero**;
the normal20 count belongs to the separate2FA source table.657 writes to Y,
and1A70/1B89 smooths the source records rather than building360 records.
Boot clear exports all-zero record positions; no active positive count or
compiled destination publisher is established. Do not impose k<=19 from layout.

**Conditional exclusion:** X35F=0 with documented zero-skip mode gives no204B
stores. **UNRESOLVED:** preserve that count through every normal indirect
writer; if it changes, destinations and M0 need closure. Existing selector,
cursor, host endpoint and transition proofs remain independent. Normal safety
is **NOT-YET-DETERMINED**, service robustness **NO**, no persistent256-word
allocation. Static exhaustion has not been demonstrated. The next focused proof
is X35F non-alias/preservation, without another effect-algorithm audit.

2026-10-06. STATIC ONLY. No hardware, MIDI/SysEx transmission, flashing,
original changes, firmware patches or Plaits implementation. DSP addresses are
24-bit word addresses; ARM addresses are bytes. Existing earlier analyses were
reused. No tool installation or upstream refetch.

**NORMAL-RUNTIME SAFE: NOT-YET-DETERMINED** for channel-zero X:[5F00,6000).
**SERVICE-ROBUST: NO**, from the previously verified5E service overlap.
Service capability is explicitly **not** a blocker in the normal-only search.
No verified256/128/64-word normal-safe allocation or normal occupancy witness.

This phase narrows the original R7 concern to finite reviewed caller families,
parses the startup external tables, bounds another coefficient lookup/staging
path, and identifies a concrete normal table-driven X store still requiring
producer closure. None of these scoped facts is a firmware-wide RAM proof.

## Reproduction and evidence

`tools/ct_effect_memory_audit.py --output-dir fresh-directory` writes the
canonical `builds/phase12/final/` exports. Independent repeat: final-repeat/.
It byte-checks the existing DSP listing, original/extract hashes and in-memory
codec roundtrip; parses structured INIT data; replays reviewed affine address
arithmetic; and retains exact normal-only unresolved mechanisms. It is not
an ARM/DSP emulator, allocator or global points-to solver.

```powershell
$py='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B tools/ct_effect_memory_audit.py --output-dir builds/phase12/new-replay
```

All outputs require a fresh directory and original/ is protected. Earlier
replay/ and verified/ are exploratory versions, superseded by final/. Static
ARM caller scans remain in arm-callers/ and reboot-entry/, with exact targets
and source provenance. Their candidate calls/data decodes require review.

## R7 and the retained Y-buffer path

**VERIFIED:**1E15 saves incoming R6→X1D3A and1E17 saves R7→X1D3B.1EED/EEF
restore them.1EF1 sets N6=2.1F01 loops over X3A (stock32);1F03 reads Y:(R6)+N6,
1F0D and1F0E each store Y:(R7)+. Thus a linear destination writes exactly
64 consecutive Y words; the input reads32 even-offset samples with stride2.
X1D3A/B are save containers, not intrinsically X-space output pointers.

Backward tracing found these algorithm-call wrappers:

| Indirect call | R6 source | R7 destination |64-word output, linear M7 |
|---|---|---|---|
|DBD, set atDB8/DBA|840|840|Y:[840,880)|
|DC5, set atDC0/DC2|800|880|Y:[880,8C0)|
|DCD, set atDC8/DCA|880|880|Y:[880,8C0)|
|DEC, set atDE6/DE8|880|9C0|Y:[9C0,A00)|
|DF9, set atDF3/DF5|840|9C0|Y:[9C0,A00)|

**VERIFIED register setup; conditional path result:** if1E15 is selected by
one of these wrappers, its saved R7 is one of840/880/9C0, not an arbitrary
24-bit pointer. All listed stores exclude both cursor tables1820/1A10. Even
M7=3FF, with these concrete initial addresses and legacy EMA=0, remains in
the aligned low Y ring[800,C00), also excluding those tables. This does not
infer a ring from M7 alone or establish an unknown caller's register state.

**UNRESOLVED actual normal1E15 entry:** there is no direct1E15 edge. The
seven canonical indirect transfers are DB6,DBD,DC5,DCD,DEC,DF9,19AC. DB6
is the chain wrapper dispatch;19AC loads function addresses from descriptors.
Init assigns the twelve voice entries281, then global entries202B and1A2B.
No initialized descriptor selects1E15. Recovered ARM parameter destinations
exclude the watched effect selector/function-table fields, but that is not
proof against every DSP indirect writer.

The chain atD87..DB6 uses X95A to select a five-wrapper row beginning X9EA,
then X95B..95F as indices into X9DB.29EC copies55 entries from P29F6..2A2D.
The first15 are algorithm marker addresses; the following40 contain eight
five-wrapper rows. The algorithm wrapper advances the table-derived R0 before
its indirect call. **VERIFIED:** neither1E15 nor its predecessor1E14 occurs
in that table; valid algorithm entry+1 targets also exclude1E15.

The necessary normal domains are therefore X95A=0..7 and X95B..95F=0..14,
with table preservation. INIT zero defaults satisfy them. **UNRESOLVED:** all
normal producers of those fields and table preservation. The absence of direct
stores/literal1E15 cannot establish dead code. Wider computed indices cannot
be called normal merely because the DSP lacks a local bounds check. R7's
reviewed low domains remain useful independently of an unsupported dead-code
or universal reachability claim.

## Initialized cursors and modifier evidence

Initialization260A..2623 writes eight pairs into each Y cursor table:

| Cells | Fixed X cursor values | Stock32/linear footprint |
|---|---|---|
|Y:[1820,1830)| alternating2CCC/2CEC |X:[2CCC,2D0C)|
|Y:[1A10,1A20)| alternating2C02/2C24 |X:[2C02,2C22),[2C24,2C44)|

1F5C reads these using R6=1800 or19F0, with offsets32/33 initially and32
over16 increments.1F6E/6F clears X through the first two cursors, and1F97
accumulates through each selected cursor. Initialized indirect output maximum
is2D0B. Local Y state/coefficient writers preserve the pointer cells under
the reviewed linear setup, as established in Phase11. The wrapper-family
R7 outputs above cannot alias them. Other actual entry/indirect-writer paths
remain separate obligations; these are writable RAM tables, not ROM constants.

**VERIFIED local modifier restore:** the temporary M3 load at584 reaches
5BE's Y1A→M3 restore through a branch/call-free segment. M6's only explicit
canonical modifier write is startup2780. M7's normal temporary3FF at265 is
restored from Y1A at27F. M1 has linear restores after its indexed/circular
helpers and the table-job snapshot paths. The full census is exported.

**SOURCE-DERIVED premise:** legacy addressing requires SR.EMA=0; FFFF is
linear. Concrete ring bases and alignment are needed for modulo interpretation.
Y1A is initializedFFFF; its sole direct store is27FA, and recovered normal
parameter destinations exclude it. **UNRESOLVED global invariant:** every
indirect Y1A producer, arbitrary computed entry, and all return/callee paths.
The local M3 restore is proved; a complete M1/M3/M6/M7 invariant is not silently
substituted for it. No high-X occupancy follows merely from unknown modifiers.

## Bounded private-X effect subset, intervals and holes

**VERIFIED conditional arithmetic:** C3E masks y1's band, and C4E shifts
signed24 y0 right17 before the cancelling ASL/ASR. N1/N3 are conservatively
[-64,63]. With its concrete table bases and linear M1/M3, coefficient reads
are bounded by X:[15C0,1941), including the possible lookahead at1940.
This excludes5F00 even without assigning semantic names or proving a valid
preset uses both extremes. It is not a coefficient-quality proof.

The selected1E15 tail reads X[1D6D,1D8E) including prefetch, X[2C02,2C22),
X[2C24,2C44),X[2CCC,2D0C). C9D work uses fixed neighboring scratch at
2C44/2C66/2C88; the reviewed scratch hull is[2C44,2CAA), preserving the
extra-readable2C66 contract.1FB2 additionally reads32 X words at2D70 with
stride2: highest2DAE (odd addresses are holes), not2D0B. Its EF2 helper uses
low X0/1 scratch and coefficient record7D..84 under linear setup.

`bounded-effect-subset.json` exports merged conservative hulls and explicit
scope. **Lowest bounded subset X:0; highest:2DAE.** These are bounds on
reviewed buffers/helper accesses, **not the lowest/highest of all normal
effects**. Tail/prefix exports preserve strides; adjacent addresses in a hull
need not all be accessed. Scalar state fields and unreviewed branches are
not asserted fully partitioned by this subset.

**Global normal effect X union: UNRESOLVED.** Remaining cursor mechanisms
include chain table/index producers and state-loaded delay/other effect pointers.
Neither an initialized low cursor nor a missing5F00 literal supplies the global
proof. No normal effect access to the candidate has been established.

## Concrete normal scratch/routing writer and DMA

**VERIFIED normal descriptor body:**202B is initialized in the first global
descriptor at X14B and visited by19AC.2035 starts R0=35F;203A reads its
loop count and203B..3E a four-word header. Each iteration2043 loads R4
from X364+5*k, then204B stores X:(R4). The code does not clamp that address.
No normal high-X value is demonstrated, but the destination producer is not
closed. Its normal count/record producer must be bounded before excluding
either candidate writes or indirect DMA register programming. This is a
specific normal-only obligation, not service5E or a full-address-space guess.

**VERIFIED new INIT data map:**22F8..2308 parses31 records beginning2309.
Each is destination, run-count, then (value,repeat) pairs; all repeat counts
are positive, each expands to1024 words, and the parser ends exactly2599.
Sorted output union X:[74000,7BC00),31744 words, external under the documented
conditional map. Therefore [2309,2599) is structured data, including apparent
DMA-register jset instructions. It is not DSP boot compression or normal code.
The full record/run map is exported without modifying any extract.

After removing that proved data, the eight-channel DMA direct-reference census
contains INIT setup/enable2A2D..3E and NORMAL ISR rearm1BC/1BE only. The latter
resets DDR0=29 and DSR1=21. Stock DMA0 writes Y[29,2C); DMA1 readsY[21,24)
and writes fixed X peripheralFFFFA4. **VERIFIED direct-reconfiguration exclusion**
for the candidate. **Complete normal DMA exclusion: NOT-YET-DETERMINED**
until the remaining indirect normal destination producers, including204B,
are closed. No actual high-X DMA configuration witness is established.

Reviewed interrupt saves remain low Y; the table snapshot remains X[1B16,1B21).
Hardware stack is separate from X/Y heap. No normal scratch allocator growing
to5F00 was found. **Maximum other normal scratch X: UNRESOLVED**, rather than
promoting the largest known scalar/container address to a global maximum.
Worker-private low memory remains separate; shared traffic is not numerically
identified with channel-zero private X without an actual alias.

## Mailbox and block persistence

35E28's nine fixed records at ARM80567EC have word counts256 each; record
stride12 and the16-bit transfer send512 bytes to X[C00,D00). This closes the
fixed coefficient-staging count, not every paged transfer elsewhere.
Selectors0/2/3/4/5 generate to Y; backup transformations write X[C00,E00);
workspace writes stay[2400,2800). Recovered selector7 has index0..63 and
maximum1E8B. **VERIFIED recovered normal mailbox-family exclusion**, under
retained modifier/staging premises. Selectors1/6 have no recovered normal ARM
publisher and also use Y output. Universal publisher/context preservation
still depends on normal indirect-writer closure; no new high-X selector witness.

BOOT clear2779 touches X[0,6000), permitted for this allocation contract.
Its recovered direct entry is25DE initialization. ARM1F554 has one recovered
direct caller1F536 (Selection0 mode branch);1F51E's callers are application
boot1D582 and the previously classified service/mode consumers. No ordinary
block reset reaches the clear in the recovered graph. Normal voice lifecycle
and synth-bank callbacks retain their earlier low destination bounds.

**UNRESOLVED full persistence:** patch/scene/project entry closure and normal
indirect writes/stream wrap have not all been proved. A DSP reboot is distinct
from a block reset. No periodic candidate clear was established, but no universal
survival guarantee follows while the normal destination204B and other producer
proofs are open. Service requests are not counted in this normal-only decision.

## Allocation and conceptual service mitigations

| Safety axis | Entire256 words /128 /64 placements |
|---|---|
|NORMAL-RUNTIME SAFE| **NOT-YET-DETERMINED**; no verified subrange |
|SERVICE-ROBUST| **NO**; explicit5E service overlap |

All1/129/193 placements were re-evaluated with service overlap removed from
the normal blocker set. Remaining blockers are normal producer/AGU and
persistence proofs. No normal occupancy witness, allocation layout or memory
write. Stock X[2C46,2C66) and its readable/filter neighbor stay scratch.

The user-requested future options are conceptual only:

| Option | Potential benefit | Proof/design obligation |
|---|---|---|
|A: prohibit5E while custom state active| simple service isolation | active-state guard and all service entry handling |
|B: reject overlapping writes| retain non-overlapping service access | whole transfer, encoded-space changes/wrap, shared aliases and cursor state; not just start-address check |
|C: save/restore state around service| potentially preserve contents | consistent quiescence/snapshot and separate safe storage; restoring afterward does not protect intermediate audio use |
|D: outside accepted domain| avoid a specific utility overlap | conditional private X/Y RAM lies within its accepted private window; no verified alternate allocation; no-end-check prevents inferring safety from an excluded start alone |

No option implemented and none presented as an established mitigation.

**Single best next step:** trace normal producers of the destination records
X364+5*k and countX35F consumed by202B/204B. Establish their finite destination
domain and show exclusion of5F00..5FFF and DMA registers. This one concrete
normal writer is relevant to both scratch safety and DMA reconfiguration;
retain the chain selector/table preservation proof as a separate obligation.
