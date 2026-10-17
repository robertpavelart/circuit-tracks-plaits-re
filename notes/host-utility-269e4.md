> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 11 — addressed host utility and high-X reachability

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

2026-10-06. STATIC ANALYSIS ONLY. ARM addresses are byte addresses; DSP ranges
are half-open24-bit word addresses. No device opened, firmware executed or
patched, packet transmitted, original modified, Plaits implemented or compiled.
Continues Phase10 evidence; no upstream refetch or tool installation.

**VERIFIED recovered role:**269E4 is an addressed DSP read/write service
handler for framed request ID5E. Its recovered entry is **SERVICE-ONLY** in
the call graph described here, but it is **not Selection1-only**. The call
precedes the separate enable-flag guard and never requests a diagnostic upload.
Thus a service request can reach private channel-zero X:[5F00,6000) while
Selection0 is active. This is static request-dependent reachability, not an
observed invocation or an ordinary audio/UI publisher.

**Allocation result: UNRESOLVED / POTENTIALLY AVAILABLE after init, with
SERVICE-ONLY OVERLAP.** No normal occupancy witness or verified256/128/64-word
allocation. Two blockers narrowed: the recovered selector7 index is0..63,
and the effect cursor startup values point into low X scratch. Remaining
global writer/modifier, transport and alias proofs are stated separately.

## Reproducible evidence

Reusable replay: tools/ct_host_utility_audit.py. Canonical exports:
builds/phase11/replay/; independent repeat: replay-repeat/. It byte-checks
existing Phase10 dispatcher evidence and the new ARM windows, canonical DSP
rows, protected original/extract hashes and exact in-memory SYX roundtrip.
It exports request/dispatch/mode tables, utility domains, effect cursors,
selector7 destinations and explicit allocation uncertainties.

```powershell
$py='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B tools/ct_host_utility_audit.py --output-dir builds/phase11/new-replay
```

Fresh output directory required; original/ and overwrites refused. New ARM
collectors use existing ct_bank_domain.py, with exact targets/windows retained
in each arm-*/provenance.json. Annotated windows were generated with ct_static.py
disasm; their literal tables are data, even where a linear decoder prints an
instruction. Every claim below uses reviewed code boundaries or explicit raw
data reads. The replay does not execute ARM/DSP instructions or transmit frames.

## Complete utility mechanics

**VERIFIED effective signature:** `utility(Context *ctx)` at269E4. It behaves
as a response-producing procedure; no stable caller-visible r0 status ABI is
established. Context+0 is the reply routing mask; context+4 points to a Buffer
whose+0 is the incoming byte pointer and+4 the byte length. The dispatcher
creates this temporary context at24856/2485A from ingress ID and Buffer*.

269EC..26A00 obtains Buffer length, computes UXTH(length−9), decodes bytes
starting at incoming+8 into stack+90 via391C6. This strips eight prefix bytes
and the final framing byte by length convention. 391C6 reconstructs seven
bytes from each eight7-bit input bytes using cross-byte shifts. For ordinary
small lengths the group count rounds up; larger lengths use a truncated
8-bit counter derived from low length bits. This is not a universal safe
decoder for arbitrary lengths.3924E performs the reverse bit packing.
256 deterministic full-group arithmetic fixtures reproduce exactly; malformed
length/backing-buffer safety is not proved by those fixtures.

| Decoded offset | Width | Instruction-derived meaning |
|---|---|---|
| +0 | byte | operation0 write /1 read; other values rejected with status4 |
| +1 | byte | port/memory-space selector, **not DSP upload selection** |
| +2 |4 bytes | opaque cookie echoed unchanged; unaligned little-endian load |
| +6 |4 bytes | caller-supplied starting address; unaligned little-endian load |
| +A |2 bytes | unsigned transfer count |
| +C |4-byte stride | writes consume only the first byte; reads return32-bit helper values |

The complete body is preserved in arm-initial/080269E4-08026B1E.asm.
Mode routing at26A16..3A:

| Mode | SHI port argument | Private space flag |
|---|---|---|
|0|0|X|
|1|0|Y, OR8000|
|2|1|X|
|3|1|Y, OR8000|
|4..FF|0|X fallback; **not rejected**|

Port0/1 are transport arguments, not proven physical MIDI track/core labels.
For shared starts[30000,38000),26A46/48 selects extended addressing and uses
the raw address instead of the private space flag. Shared X/Y alias semantics
remain conditional on the actual hardware map; do not merge low private spaces.

**VERIFIED validation:**26A3C subtracts30000 and unsigned-compares against8000.
If outside shared,26A4C compares the original address against8000. Otherwise
status3 is emitted. Thus accepted private starts are[0,8000), covering the
16-bit private protocol's15-bit memory address plus a separately chosen space
flag. This is a protocol address envelope, not a statement that8000 RAM words
physically exist. There is no candidate reservation or protection check.

Operations at26A52/56/5A select write/read. Count0 performs no transfer and
still produces status2. Nonzero counts are not clamped locally to32 or checked
against a final DSP endpoint. Private loops26A90..A0 and26ACE..AE0 increment
the encoded cursor by one, then UXTH before the helper. Crossing8000/10000 can
change the space flag or wrap the16-bit encoded address. DSP private handler
P181 masks address7FFF; P18A/199 use bit15 for X/Y. Single-word requests
inside5F00..5FFF avoid these boundary issues. Alignment is one DSP word;
no multiword alignment requirement is enforced here.

**VERIFIED surprising write behavior, not intended semantics:** private branch
26A90 LDRB consumes a byte at each four-byte stride and26A9A passes it unchanged
to292F8.291E0 serializes value bits31..8. Consequently the private DSP data word
is zero for every possible consumed byte. Shared branch26A74 shifts by8 and
29336 shifts by8 again: the transmitted DSP word is the consumed byte<<8.
Do not rename the input slots as full32-bit writes or assume intended repair.

Read branches26AB6/26AD4 store helper r0 as four bytes per slot at stack+10.
Reply fields at26AF0..26B02 contain status,mode,cookie,address,count, followed
by4*count scratch bytes; length12+4*count is UXTH before3924E encoding.
26B14 responds with the same request ID5E via37B0C. Status2 means accepted,
3 invalid start,4 unsupported operation. Write branches do not initialize the
read-response payload area: its content is unspecified by this routine.

Count is a16-bit input, but no backing-buffer/end check is present locally.
The read scratch span stack[10,90) is128 bytes; count32 fits it. For count32,
140 decoded reply bytes pack to160 bytes, fitting stack[90,130). This is a
**conditional capacity calculation**, not a verified enforced count bound.
Claims about large requests require upstream buffer/schema proof; no malformed
request was constructed, sent or executed.

## Upward trace and classification

| Producer/consumer | Evidence | Classification |
|---|---|---|
| Boot constructor1EC80 |1EC92 loads1EB31 from literal1EDE0 and registers it through251E8 | **BOOT/INIT**, callback installation |
| Incoming callback1EB30 | ingress identifier0 or1 calls2484C at1EB40; pointer exported at1EDE0 | **VERIFIED framed-message ingress**; physical transport ancestry not fully assigned |
|2484C| compares prefix F0 00 20 29 01 at24862; byte5=63, length≥9, byte6=70;24880 calls1F284 | **VERIFIED service-protocol dispatch**, independent of later enable flag |
|1F284| byte7=5E at1F28C/28E branches1F308 | **SERVICE/DIAGNOSTIC** utility request |
|1F308 /1F30A| context passed unchanged to269E4 | **VERIFIED service entry**, not an allocation/voice function |
|1F30E..314| tests global flag bit4 after the utility returns | guards other consumers; **does not guard5E** |
|1F292..302| separate request60 flag/mode-control path; can restore mode0 | distinct from5E utility |
|269E4→3924E→37B0C| encodes reply under ID5E and routes using context mask | **service response**, not a synthesized normal request publisher |

1F228/1D4DE initialize related service objects during application startup.
Boot1D582 supplies zero mode to1F51E, whose0 branch loads Selection0;
1F51E's1 branch loads Selection1. None of these mode checks lies on the
recovered5E branch. Nor does2484C require1F276's enable flag before24880;
its enable check2488E occurs after service dispatch.

**Explicit normal-reachability answer: SERVICE-ONLY in the recovered graph.**
Ordinary voice/audio/UI parameter producers do not supply this request in the
recovered graph. **VERIFIED YES to service invocation while Selection0 is
active:** no diagnostic-selection transition is required. No unconditional
VERIFIED NO about execution during normal-mode operation is justified.
Every decoded direct269E4 call found is1F30A; exact flash/decoded-init pointer
scan finds no additional entry pointer. That census does not prove arbitrary
computed calls impossible. All upstream physical publishers/actual request
occurrence remain unobserved; this qualification is not a second invented gate.

For a backed single-word request, op0/mode0 with each start5F00..5FFF is
accepted and uses channel-zero private X; op1/mode0 similarly reads it.
The recovered protocol therefore overlaps every candidate word. The write
conclusion assumes the transport's valid cached-cursor invariant; scalar reads
explicitly program an address. These are **static service capability/entry
witnesses**, not evidence that normal synth operation writes that region.

## Effect cursor closure: initialization and local preservation

**VERIFIED producers found:** boot25E4 calls260A.260A..2623 performs eight
iterations, each storing two pointer words into each Y table:

| Pointer cells | Initial X values |32-word footprint with linear AGU |
|---|---|---|
|Y:[1820,1830)| alternating2CCC /2CEC |X:[2CCC,2D0C), highest2D0B|
|Y:[1A10,1A20)| alternating2C02 /2C24 |X:[2C02,2C22) /[2C24,2C44), highest2C43|

1F5C's R6 starts1800 or19F0 from X1D40;1F68/6A fetch+32/+33 for initial
clear, and1F89 fetches+32 for per-pass accumulation. The16-iteration loop
1F72..98 advances R6 once at1F8C, reading all16 cells of the selected table.
1F8C writes Y[R6] and1F98 writes Y[R6+47] after that increment. Under linear
setup these touch parameter/state cells, not the pointer-table cells.
1F13's coefficient output region starts1840 or1A30 and writes160 words,
ending18E0 or1AD0; again no cursor-cell overwrite.1E6C's16-word parameter
loop ends1820 exclusively. Local cursor use therefore preserves the tables
under its stated addressing premises; it does not make them generally immutable.

**VERIFIED conditional maximum:**2D0B for those initialized indirect X buffers,
excluding5F00. Other selected1F5C/C9D work uses fixed X2C44/2C66/2C88/2C8A
scratch with fixed +2/-1 offsets and stock counts under linear modifiers.
**UNRESOLVED global normal maximum:** all indirect Y writers, actual entry
to1E15 and modifier state at that entry. The exported M1/M3/M6/M7 census
shows M6's only explicit canonical writer is startup2780; M3 has a runtime
load from Y state at584 and a restore5BE. M1/M7 also have temporary modes.
Do not infer a caller invariant from a local absence of modifier writes.
Arbitrary service writes to these Y cells also lie outside the init-value proof.

One exact unclosed writer is inside the surrounding1E15 path itself:1EEF
reloads the caller-supplied Y output pointer from X1D3B, and1F0D/0E store
through Y:(R7)+. Without its incoming destination bound, subsequent calls
could encounter changed cursor-table contents if that output aliases them.
This is an unresolved alias mechanism, not a demonstrated overwrite. The
remaining proof must include this retained Y output destination, not merely
the direct stores within1F5C.

## Selector7 closure

**VERIFIED publisher:**49C0A writes Y2C=word with low nibble7. For end address
belowE80000,49BFC loads mask7FFFF0 from49C30, forms `(end>>1)&mask`, adds7,
then shifts8 for scalar transfer. Otherwise49BF8 loads74000700 from49C2C,
transmitting740007. Both select7 at DSP1C59..5E. This corrects Phase10's
unfound-publisher statement; publisher is not a hypothetical service selector.

The job index comes separately from49BBC's write to X:C00, using49A80's
first argument (LD byte at49BB2,shift8). Its sole recovered direct caller
49A66 supplies R6 initialized0 at49A50 and increments until40 at49A6E:
**VERIFIED index0..63**.49BCC/49BDC/49BEA write the next three metadata words.
DSP1CBB..C7 copies them to X:[1D8D+4*i,1D90+4*i), count3,stride1.
Maximum start1E89, maximum written1E8B, endpoint1E8C. This excludes5F00
for the recovered publisher under linear M1 and unmodified mailbox staging.

49A1C is a loader iterating64 input records, starting its external cursor at
580000. Its caller3CC46 and an unreviewed decode candidate5BFD0 are retained
as separate census results; constant-region decodes are not automatically callers.
Outer load/reload mode ancestry is **UNRESOLVED**; the0..63 argument bound
does not depend on assigning an unsupported UI/sample-library label.
Other service/malformed/interleaved publishers are not excluded by this local
publisher proof. Nevertheless selector64/105D is not a recovered normal witness.

## Scratch, candidate verdict, alternatives and static limits

Reviewed hardware/SHI saves and low scratch remain as Phase10. Newly bounded
effect cursor buffers end2D0C. A **universal scratch maximum remains UNRESOLVED**
because saved modifier/cursor producer closure, other nonparameter streams and
reconfiguration have not all been proved. No new high-X stack/allocator growth
witness was established; no broad allocator audit was restarted.

| Requested size | Placements in[5F00,6000) | Verdict |
|---|---:|---|
|256|1| **UNRESOLVED** normal persistence; **SERVICE-ONLY OVERLAP** |
|128|129| same; no verified placement |
|64|193| same; no verified placement |

No proven normal reaches were subtracted from this exact candidate. Service
overlap alone does not disqualify ordinary after-init availability, and absence
of a normal witness does not prove it. Largest VERIFIED AVAILABLE AFTER INIT
subrange: none established. No layout or Plaits integration.

**Alternative search not triggered:** this candidate is not disqualified, and
the remaining unknowns have not been shown to be a single unavoidable static
limit. Recommending another private high-X range would merely move the same
unclosed writer/modifier proof; high Y has its own unknown buffer cursors. No
firmware-wide search or fabricated ranking was performed.

**Can static analysis alone finish? NOT-YET-DETERMINED.** Producer/AGU and
loader/transport closure may still be proved statically; this phase does not
establish that dynamic tracing is necessary. Actual external request occurrence
would require a trace/observation, but is not needed to prove this service
capability. Actual silicon/core assignment and physical alias map require
independent hardware evidence unless recoverable from board records. No such
observation, emulation, tracing or instrumentation was performed.

**Single best next step:** close the normal producer/modifier invariant of
Y:[1820,1830) andY:[1A10,1A20), starting from260A initialization and actual
reachable entries to1E15/1F5C, especially the incoming R7→X1D3B→Y output
stores1F0D/0E. Prove all normal stores preserve those cells and
that M1/M3/M6/M7 at the effect consumer give the reviewed low bounds. This
turns the newly recovered constants into an exclusion rather than repeating
the now-classified external utility capability.
