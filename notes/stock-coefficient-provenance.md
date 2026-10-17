> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 20B2 — selected original coefficient provenance

2026-10-07. **VERIFIED source / CALCULATED conditional producer results.**
Four previously opaque coefficient words now have a concrete original-file
source for a bounded bank0 binding. **PARTIAL overall; replay REFUSED.** No
DSP/ARM execution, hardware, patching, Plaits feeding or arbitrary preset values.
An offline patch file is not a runtime register/history snapshot.

## Selected source and parameter decoding

Use the existing cached archive snapshot
`builds/phase19c-assetdata/discovery/archives/fae30b90741bfaebfdd94b98e0f8d18fd7be9b1266e3f74291ea9fef02285fa5.zip`,
member `patches/patch_0.syx`, name **Rudi saw poly**. Its SHA256 is
`c542d3f2cc66ab43f361953bff66b1db6535bbb74984d25d963915bc6e83ef1a`.
This is actual authored, pre-existing data, not generated zero/default values.
The study binds its bytes to one bank0/slot0 view; physical-device selection is
not claimed or required for that conditional file-backed study.

**VERIFIED:** the350-byte frame has the original Circuit Tracks header and340
content bytes at[9,349). Already extracted Components1.72.1 code validates350/
352/12-byte forms and slices at9 for this form, with no seven-bit decompression.
Its model puts filter fields at content offset60, with routing+0, driveType+2,
type+3. No Components code was launched/executed. Bounded snippets and character
offsets are exported in components-patch-witnesses.json.

Independent original ARM evidence agrees:

- 2989C constructs bank views with descriptor table805454C and length340;
- 3BB88 stores descriptors, data-pointer view and length;
- 29A34 selects the bank view through3BE60 and its vtable getter;
- vtable805BBAC+4 points to3BBD6, which selects descriptor `base+8*ID`;
- 3BD00 loads from descriptor's content offset. Type0 uses the declared field
  mask/shift. The selected bytes fit their masks, so decoded values equal raw bytes.
- 3BBE2 is the original byte-copy setter; a bound content record is distinct
  from assuming the selected object/slot already exists in a running device.

| ARM ID | Content offset | Descriptor address/raw bytes | Actual byte |
|---|---:|---|---:|
|1E routing|60|805463C /3c0000000002ff3c|0|
|20 nonlinear selector|62|805464C /3e0000000006ff41|1|
|21 filter pair selector|63|8054654 /3f0000000005ff44|1|

Thus mode0 was chosen because this **actual patch** contains routing0, not because
an earlier analyst-selected branch happened to use zero. Raw field maxima are
2/6/5; this selected record satisfies them. No universal malformed-import bound
or all-preset validation is inferred.

## Correction bypass is proved from its original initializer

360B4 loads literal8036110 = **20006024**, the runtime reverse-index array.
It does **not** load the immutable ID list805A2B0.35F28 initializes IDs0..173
toFF then searches the70-byte original ID list and records a matching index.
IDs1E/20/21 are absent, therefore their initialized reverse values areFF.
360BE/360C0 skips all correction halfword arithmetic for these three IDs.

**CALCULATED exact initialized mapping:** each selector above retains its file
value regardless of the macro-offset halfwords. Retention of that initialized
map is a bounded-context premise; this is not a new universal foreign-write/RAM
proof. The other modulated drive/cutoff/source fields are not thereby closed.

## DSP preparation cursors and four closed words

P387 initializesR0=299+bank_stride andR6=bankYbase+1. Each of three lane records
consumes five R0 words:3A0,3B7,3C3,3C4, and either43D or44F. Both flag alternatives
consume exactly one final word, so at47D bank0R0=**2A8**. R7 has emitted three
14-word records fromQ57B, then six words470: R7=**5AB**. These are original
instruction-backed cursor relations under the standard addressing/mode premises.

| Output | Original writer | Immediate source | ARM producer/value |
|---|---|---|---|
|X5AB|47E|47D X2A8|27578 publishesID1E =0|
|X5AC|480|47F X2A9|2758E publishesID20 =1|
|X5B1|49A|497 X2AC|275C8->2819C,ID21=1 ->first pair byte5|
|X5B2|49B|499 X2AD|same helper ->second pair byte5|

ARM arguments use value<<8;291E0 serializes its bits31..8 as the24-bit DSP
word. These are offsets5/5, not1280/1280. No SPI function was executed.
Bank0R0 read advances through2A8..2B4; complete sites are exported. R6's four
reads/lane,46F and six470 reads, then47C decrement give **R6=Y8F** at47F.
The code copies selectors/offsets without a numeric transform. In the reviewed
local lane-combination prefix, subsequent six ramp stores end at5AA and leave
these words intact before post consumption; async/foreign mutation is not proved.

## Address construction and original coefficient data

The original12-byte table at **ARM080281C8** contains six pairs:

`(5,25), (5,5), (10,25), (10,10), (20,25), (20,20)`.

For file type1, helper2819C loads080281CA/CB, both5. C10/C1A read those DSP
coefficient words, add **F5F**, then transferA intoR5. The selected intended
addresses are therefore **Y:F64**, and both filters consume the five words
**Y:[F64,F69)**. Units are24-bit word offsets, target spaceY, not an ARM byte
address or a pointer into the uploaded P stream.

**BOUNDED-PROOF / CONDITIONAL:** these effective addresses require the material
full-accumulator pointer-transfer/SA/scaling modes and original linearM5 to be
qualified. They are not observed runtime addresses and must not silently assume
entry scaling bits are zero. The operands and file-selected offsets are closed;
numeric checkpoint modes and coefficient values are still not qualified.

For linearM5, C9D preloads a coefficient atCA3. Its16 two-sample iterations
read atCA6..CAF using ten postupdates per iteration: +1,+1,+1,-4,+1,
+1,+1,+1,-4,+1. Each call makes161 reads, spanning exactlyF64..F68, and leaves
R5=F65. N1=N3=2,N4=-3,N5=-4 have local producersC0E/C0F/BE8/BEA. The two
calls reuse the same five-word sequence for this particular type1 case.

These five words are **not immutable constants**. BDD setsR5=F68 before C2D;
the original builder stores:

| Y word | Last builder store before C9D |
|---|---|
|F68|C65 B|
|F67|C78 A|
|F66|C7C B|
|F65|C7D Y0|
|F64|C7E B|

C88 continues belowF64, so it does not overwrite these five stores. Their
initial values can be irrelevant **if** this original builder is admitted and
executes before C9D. Filling them directly from the ARM pair table would be
wrong. Numerical values depend on original C2D control histories, interpolated
coefficient data and arithmetic modes, which remain unresolved.

## Remaining scalar and history chains

| Field | Original numerical source / unresolved predecessor |
|---|---|
|X5AD,481|Y8F ->6D9: max(0,X2E7+modulatedY8F)|
|X5AE,487|482..485: Y10 minus product ofY90 andX2AA|
|X5AF,48B|486..48B: square ofY90 XOR Y10, full transfer semantics matter|
|X5B0,498|X2AB=0 from275AC..B0, so490's parallel copy keeps oldY91; result max(0,Y91-020000)|
|Y5AB..5AD|retained AA8 nonlinear/ramp histories; AD0/AEF/AF6 update them|
|Y5AE|retained BDD control history;BED/BF3/BFD|
|Y5B7/5B8|retained coefficient-control/peak fields;C2D andC04/C08/C2A|
|X5BC/5BD|gain ramp/current from4C9..4D1 and primary envelopeY130|

X2AB=0 is an **explicit original ARM writer**, not a boot-clear assumption.
It removes Y94 from this selected X5B0 expression. Y8F/Y90/Y91 remain needed.
P676 clears31 bankY words, but685..690 then writes modulation results through
runtime table pointers. 6D9 writesY8F,6DE writesY90,6ED writesY91 from those
results and parameters/slot-source state. The preceding clear is not their final
value. X2E7/2E8 publishers27928/2794A/27964 are identified; knowing patch bytes
does not furnish all envelope/LFO/modulation/note history consumed by657.

Selected trigger loops33B..33E clearY[S+16,S+24) andY[S+30,S+38). They exclude
S+12..15 (5AB..5AE) andS+24/25 (5B7/5B8). Note activation therefore does not
justify resetting the needed retained histories to zero. Startup-clear evidence
is a possible older producer, not their proved last writer at this invocation.

**Exact remaining producer frontier:** original657 modulation input record and
slot-source/history values ->690/6D9/6DE/6ED ->47F..498, plus retained AA8/BDD/
C2D histories and the bounded CPU/AGU/stack environment. No values are invented.
This phase stops at that material frontier and does not broaden RAM/ROM analysis.

## Phase20B3 refinement

See stock-p657-input-record.md andstock-filter-history.md. Selected original
routes12→Y91,0→Y7C give a conditional zero modulation term for8F/90, but not91.
Raw filter bytes10/2/13/79/0 map to runtime-corrected IDs1F/24/22/26/23;
their active values remain unknown. In particular raw79 atcontent68 is nominal
15 after28314 subtract64; it is not modulation row0's nominal49.1B89 smooths
X2E9 and modulation amounts across updates. RetainedY5AB..5AE/5B7/5B8
have no qualified last numerical writer. Thus YF64..68 remain null, and
originalC2D/independent numerical reconstruction are both refused. No change
to the earlier selector/offset proof or prepared four expected fields.
