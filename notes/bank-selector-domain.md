# Phase 9 — local bank domains and normal parameter destinations

2026-10-06. STATIC ANALYSIS ONLY. No hardware, transmissions, firmware execution,
patching, original/ changes, Plaits implementation or compilation. Continue from
Phase8; no firmware extraction, upstream fetching or broad DSP ownership restart.
DSP addresses below are **24-bit word addresses**; ARM addresses are bytes.

**VERIFIED recovered normal boundary:** synth parameter callbacks receive
bank0/1 despite wider event-selector paths. This removes HOST-BANK as an
exclusion blocker for the recovered normal parameter graph. It does not prove
one global selector domain, complete upstream event ancestry or persistent RAM.

## Reproduction and limits

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/ct_parameter_ranges.py --output-dir builds/phase9/ranges-verified
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/ct_bank_domain_report.py --ranges-dir builds/phase9/ranges-verified --output-dir builds/phase9/verified
```

Choose fresh directories. The existing Capstone dependency is used for ARM
only. No new dependency installed. `ct_bank_domain.py` collects reusable
direct-call/pointer candidates and instruction windows; canonical results are
in **builds/phase9/verified/**. Preliminary range reports are retained.

The address tool is static constant propagation with opaque parameter values,
explicit address-only helper summaries and finite bank/slot premises. Unsupported
paths and destinations are retained separately. There are no unresolved destination
arguments or unsupported control paths in the recovered table exports. This does
not certify every indirect entry or every ARM host operation in the whole firmware.

## A/B. Event thunks and effective signatures

**VERIFIED:** flash table header805B858/85C contains zero words; address point
805B860 contains Thumb29A09,29A13,29A1D. Constructor2989C loads805B858 at
298B4, adds8, stores the primary vptr at298BE; its secondary vptr points at
805B874. The thunks have no direct-call hits; each has one exact Thumb-pointer
reference in the primary table. Raw matches alone are not caller proofs.

| Thunk | Effective inputs and forwarding | Downstream behavior |
|---|---|---|
|08029A08|r0=interface object, unused; r1=event namespace→r0; r2=event key→r1; r3=event level→r2|Tail3BD58→497CA; normal key/level event path reaches21DD4→21D86→219E8|
|08029A12|r0=interface object, unused; r1=event namespace→r0; r2=matching event key→r1; r3 unused|Tail3BD94→49758; matching release path reaches21C48|

Neither thunk masks, checks or bounds the namespace/key/level. These are full
register arguments at this boundary. Default497CA and49758 paths truncate the
namespace to a selector byte when storing20006800; they also use incoming values
in ARM array calculations before/around that store. Byte truncation is not an
accepted-input-range check. Complete upstream normal input bounds remain
**UNRESOLVED**, including exact MIDI/external-parser and sequencer/UI producers.

**VERIFIED namespace branches:**

- 0/1 reach generic event handling and correspond to the two recovered stock
  allocation/parameter banks. Literal UI Synth1/2 ordering remains a hypothesis.
- 0x10 returns immediately from49758 without storing selector.497CA's0x10 branch
  also bypasses the store; keys3C/3E/40/41 dispatch indexed operations0/1/2/3
  via51B54. Key0x40 here is an event key, **not bank64**. This is a verified
  four-trigger namespace; its drum-track interpretation remains **HYPOTHESIS**.
- 0xFF in497CA bypasses the selector store and reaches28FC2, which reads namespace
  0x21 parameter9 and writesY:111.2AB48 suppliesFF in a direct3BD58 witness.
- 0x20/0x21 are verified separate parameter-object identifiers; their validity
  for note-event calls is not implied by parameter lookup validity.
- 0x40 as an event namespace is not clamped by the thunk. No recovered normal
  producer supplies it as a synth bank; it cannot survive the bounded parameter
  dispatcher reset described below. No SERVICE-ONLY classification is invented.

## C. Caller tree and serialization

caller-tree.json distinguishes recovered edges and unresolved upstream edges.

| Recovered chain | Classification | Local bound |
|---|---|---|
|1D5D4 acquires guard→21392→213D4|NORMAL SYNTH/AUDIO service|bank loop0/1; slot loop0..11|
|1F4E4 acquires guard→213B0→214BE→2148C|NORMAL UI/PARAMETER service|explicit bank0 then1|
|29A00→3BDF2→3BE0E/18→49634→2148C|NORMAL UI/PARAMETER bank refresh|input is a refresh bitmask; bit0/1 supply constants0/1|
|805B860+0/+4→29A08/29A12→3BD58/3BD94|NORMAL event/release sinks; producer-origin UNRESOLVED|thunk argument is not bounded there|
|2AB48→3BD58→497CA|NORMAL special parameter-update witness|constantFF, no selector store|
|1F6FE→2989C;1E03C→1F4B0|BOOT/INIT object construction|vptr/child views and one-token guard|
|DSP selection1 upload/test routines|SERVICE/DIAGNOSTIC, separate recovered transition|not20006800's synth-bank domain|
|Six bank callbacks27D0E..27D18; namespace21 callback28FD4|VERIFIED no-op bodies|BX LR, no DSP writes; not a claim all callers dead|

**VERIFIED guard initialization:**1E000 loads2000030C into r5;1E03C constructs
the guard object with1F4B0,1E044 stores its pointer at[2000030C].1F4B4 loads1;
1F4B8 and1F4BA store initial count/capacity at object+C/D.21064 uses LDREXB/
STREXB to decrement the count, waiting when zero;29028 increments only below
capacity. Thus the successful initialized normal object allows one holder.

3BD58 and3BD94 acquire `*[2000030C]+C` at3BD6C/3BDA6 before event-selector
mutation;3BDF2 acquires the same guard at3BE04 before bank refresh. Periodic
parameter service acquires it at1F4E4 and releases through1F4EE→29028.
Audio/slot service uses the same guard at1D5D4 and releases at1D5DC..5FC.
Guard pointer equality, initialization and acquisition/release are instruction
facts, not an assumed OS mutex name. Normal wrappers cannot concurrently replace
the selector during a protected parameter callback.

**UNRESOLVED:** complete indirect producer/object-flow tree for the public note
interface and all MIDI/external source schemas. No fabricated immediate caller
is assigned to the virtual methods. The local parameter proof does not depend
on bounding every upstream event namespace.

## D. Parameter dispatcher and corrected dirty-flag alias

**Phase8 correction:**21F94 PC-relative load is
`align4(21F94+4)+134 = 220CC`;21FB2 similarly resolves220CC with displacement118.
The word at080220CC is **200067FC**. Earlier Phase8 text incorrectly associated
these loads with21FCC/20006A0C. Numeric proximity is not a literal-load resolution.

21E9C maps source parameter IDs into categories. Categories9..18 set halfword
bits0..9 at **parent+18+2*bank** (21FA6); categories1/2/3/5 set slot-dirty bits
at **parent+16+bank** (21FC0). Parent is200067FC in both cases.3602A's70-entry
comparison loop calls21E9C with its saved bank argument;360EE supplies0/1.
The dirty-setter and dispatcher are connected.20006A0C remains a separate
global namespace dirty structure used by0x10/0x20/0x21 updates.

**VERIFIED2148C:**r0 is bank, not parameter ID.21492 forms
`r5=parent+2*bank`;21496 writes bank into parent+4. It scans16 bits with
r6=1,r4=16,r7=805A384. A set bit invokes the associated function pointer at214AC,
then214B0/B2 clears that bit.214B4/B6 shift mask/advance pointer,214BA loops.
Callbacks obtain parameter IDs from their own hardcoded getter calls; the
dispatcher does not pass an index/parameter ID as an ABI argument to them.

**Recovered incoming2148C edges:**214C2(r0=0),214CC(r0=1),4966E(inherits49634's
argument).49634's recovered callers3BE0E/18 supply0/1. No additional direct
edge or exact function-pointer reference to2148C or49634 was found. The scoped
claim covers this recovered immutable normal graph, valid initialization and
shared-guard protocol; it is not a proof against corrupted pointers or arbitrary
injected calls.

**VERIFIED213D4:**starts bank counterr5=0;213E6 stores it into parent+4 before
slot callbacks;2146C/70/72 increments through1 only. Slot counterr7 is0..11,
stored in parent+5 at21414 for matching saved event-bank records. The slot
callback table is separate and uses hardcoded parameter getters.

## E/F. Complete recovered tables and local constructor domains

Bank table805A384 has16 pointer entries: ten implemented callbacks and six
BX LR stubs. Each implemented banked callback has local bank∈{0,1};27AFA uses
fixed global addresses and does not need a bank domain. All sinks below write
one24-bit word; inclusive base lists are translated by the stated stride.

| Index | ARM callback | Writes before adding172*bank | Transfer sinks |
|---:|---|---|---:|
|0|273E4|X:298..2A7,3EE..3EF|18|
|1|27556|X:2A8..2AA,2AC..2AD,2B3..2B6,407; **unbanked2AB,2B2**|12|
|2|27648|X:2B7..2C2|12|
|3|27776|X:2C9..2CB|3|
|4|277D8|X:2D7,2DB,3C4..3CB,3CD..3CE,3E4..3E5|14|
|5|27928|X:2E7..2E8,2EA..2EB,2F2..2F5,3E7,3E9|10|
|6|27A10|Twenty stride5 records2FB+5*i+{0,1,2,4}; tail3D0..3E3; unbanked95; delegated2FA,35F|101 own +2 conditional/deferred|
|7|27AFA|UnbankedX:956..959|4|
|8|27B36|X:3F0,3F7..3FF|10|
|9|27C2E|X:3F1,400..402,406; **Y:77F..781 +E*bank**|8|
|10..15|27D0E,27D10,27D12,27D14,27D16,27D18|No writes|0|

slot table21478 has five adjacent valid function pointers. With slot s∈[0,11],
the destination formulas are:

| Index / callback | Destination sets | Sinks |
|---|---|---:|
|0 /27094|Y:11F..120,148..149 +60*s|4|
|1 /2712E|Y:14B,14D..152 +60*s; unbankedX:2F8|8|
|2 /271E4|Y:14C,153..158 +60*s; unbankedX:2F9|8|
|3 /272A6|Y:159..15C +60*s (some destinations repeated)|6|
|4 /27346|Y:15D..163 +60*s|7|

The bank used for parameter getters is0/1; these slot destinations depend on
slot, not bank. Individual helper argument summaries and all sink addresses,
minima/maxima/strides/holes are exported in callback-tables.csv,
constructor-formulas.csv and parameter-writes.csv. The helpers include28132,
2819C,28204,28336,283D8,27DE0,27F34,27FA4,28096 and shared single-write tails.
Stack-passed destinations are explicitly propagated; opaque numeric results do
not become guessed addresses.

Separate global tables are also exported, never merged into synth banks:

| Namespace | Table | Valid entries | Domain of destinations |
|---|---|---:|---|
|0x10|214F4/214D0→21534|4:287DE,2887A,2890E,289A2|Fixed global fields; getter context10; no bank contribution|
|0x20|21544→805B3B0|10:28A4A,28AB4,28B40,28B80,28C0E,28C9C,28D32,28DC8,28E36,28EA4|Fixed global fields; getter context20; no bank contribution|
|0x21|21578→215B8|3:28F40,28F62,28FD4(stub)|Fixed global fields; getter context21; no bank contribution|

**UNRESOLVED valid-bit producers:**slot dispatcher tests up to8 pending bits
although only five adjacent entries are valid pointers; namespace21 dispatcher
tests four bits although only three entries are valid. The next word at215C4 is
instruction bytesD0002800, not a fourth callback. Parameter ID12 in21FDC's
namespace21 branch can request bit3; its normal producer admissibility remains
unproved. These facts are exported as unresolved reserved-dispatch conditions,
not invented callback functions or proved SERVICE-ONLY paths. They do not turn
into a normal bank64 constructor path.

## G/H. Wider values at27A10 and its delegated work

| Selector at27A10 | Recovered normal-boundary classification |
|---|---|
|0,1|NORMAL REACHABLE via protected bank dispatch|
|0x10|IMPOSSIBLE BY CALLER BOUNDS; special event path bypasses selector store|
|0x40/64|IMPOSSIBLE BY CALLER BOUNDS at this recovered normal callback boundary|
|2..255, including20/21/FF|IMPOSSIBLE BY CALLER BOUNDS at this boundary; no global-byte invariant asserted|

No wider value is labelled SERVICE-ONLY without a proved service caller. The
Phase8 b64→X:5F7B calculation remains valid abstract arithmetic, but is excluded
as a normal parameter-dispatch reachability witness by the recovered local proof.

**VERIFIED delegation:**27ADE reloads the protected bank into r1;27AE4 calls
2872C with count20. Depending on retained state,2873C calls286BC immediately or
sets deferred flags.286F6 later invokes286BC with constants0/1 at2870C/2871E.
286BC writes **X:2FA+172*bank** at286DA and **X:35F+172*bank** at286E4.
This extends27A10's101 own sinks with two possible immediate/deferred destinations;
it does not mean103 words are written synchronously on every invocation.
Count/value timing fields do not contribute to those two addresses.

## I/J. Resulting normal destination intervals

**VERIFIED recovered family union:**456 distinctX words within inclusive
[52,959],375 distinctY words within inclusive[FD,78F]. These enclosing bounds
contain many holes. **normal-parameter-intervals.csv is the exact contiguous
union**, including the specialFF→28FC2→Y:111 update and deferred work. The
finite address sets/formulas preserve skipped record fields and unbanked exceptions.
The total1382 propagated sink records include separate bank/slot contexts and
possible delegated paths; it is not a per-block traffic count or cycles estimate.

This closes recovered bank, slot and global parameter-table destination domains.
It does **not** replace Phase6C's unresolved addressed/bulk/extended host callers
with a claim that every normal host transfer lies in these ranges. Reads and
non-parameter table/sample jobs require their own argument/extent proofs.

## K/M. High-memory candidates and remaining allocation blocker

None of the recovered normal parameter destinations intersects
X:[4000,6000) orY:[3000,4000). HOST-BANK is removed for this graph; no service or
init-only capability is subtracted as if it were normal parameter occupancy.
Candidate-host-exclusion.csv checks every word-aligned64/128/256/512 start:
zero are excluded by the recovered parameter paths. This is a **host-family
exclusion**, not VERIFIED AVAILABLE AFTER INIT.

**POTENTIALLY AVAILABLE / UNRESOLVED:**both candidate ranges remain pending
other normal host/table traffic and exact-region DSP/worker/DMA/save/scratch
exclusions. No allocation is chosen; no layout or Plaits code is produced.
No broad Phase8 audit was repeated, and unrelated DSP pointers were not required
to close the selector chain.

## L. Track identity and desired architecture

**VERIFIED:**constructor2989C creates parameter views with identifiers
0,1,10,20,21 at29906/26/40/5A/74. Lookup3BE60 accepts0/1,10,20,21 and returns
NULL for2,3,40 (ordinary nonnegative inputs). It does not provide synth
parameter objects for those rejected identifiers. This is a parameter namespace
fact, not proof that physical MIDI channels or MIDI-track IDs equal those values.

**HYPOTHESIS:**UI Synth1/Synth2 correspond respectively to allocation/parameter
banks0/1. **UNRESOLVED:**direct UI label ordering and MIDI1/MIDI2 routing IDs.
Their absence from this lookup does not prove they cannot produce external MIDI
or that they already have internal voices. Four-trigger namespace10 is separate.

The user's desired mono/mono/four-voice/four-voice architecture and eight controls
are recorded in **control-architecture.md** as an unimplemented design target.
No MIDI-track redesign or control/parameter-ID assignment was performed.

## N. Single best next step

Audit one exact candidate, **X:[5F00,6000)**, against the remaining normal
non-parameter host/table destinations and retained DSP table-pointer jobs,
starting with the normal mailbox source/destination chain throughX:1B16 and
P:1E15→X:1D3A/1D3B. Bank64 parameter traffic is no longer the blocker for that
candidate. Treat this as a candidate for proof, not a chosen allocation; preserve
DMA/worker/save/scratch exclusions as independent obligations.
