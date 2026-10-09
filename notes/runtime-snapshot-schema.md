# Phase20B6 — minimal stock post snapshot schema

2026-10-07. **DESIGN ONLY**. No snapshot acquired or importer implemented.
Machine-readable contract: builds/phase20b-snapshot-design/final-v4/
snapshot-schema.json and emulator-import-schema.json; each field/range classified
in snapshot-live-fields.csv. Architecture-specific liveness is **CONDITIONAL**
on captured routing0/nonlinear1/offset5/5, valid modifiers, counts and no material
asynchronous writes. Other modes fail this narrow profile; no universal minimum.

## Address erratum and minimum memory

**CALCULATED correction:** old20B5 prose/formula saidS+12 while intending12
decimal words. Correct hexadecimal post base is **S+0C**, S=59F+28*i.
Y:[S+0C,S+1A) is14 words; slot0:[5AB,5B9). Earlier exported reports are
preserved as historical evidence. Actual capturedR4 is the authority and must
be correlated with slot, not synthesized from a guess. X base isQ+30 with
Q=57B+4A*i; X/Y strides differ. This is a transcription correction, not
a new stock event/initialization proof.

|Field/range|Class|Minimum obligation|
|---|---|---|
|PC/SR/OMR|A MUST CAPTURE|raw pipeline-derived nextPC/status/mapping; preserve normalization proof|
|R4;M0/1/2/3/4/6/7|A|actual historycursor/modifiers; no resetdefaults|
|R0;otherR/N;A/B/data inputs|D for selected numerical9D9 entry|redefined/unused locally; rawR0 MUST be captured for9DD normalization. Full-state capture requires all retained values|
|M5|E MODE-DEPENDENT|selected path replaces it fromY19/Y1A; other modes may requireincomingM5|
|SP/SC/LA/LC/activehardwareframes|A|residentphysical-index order; capacity and inherited loops|
|LF/FV|C DERIVE|SRbits15/16, not independently guessed values|
|EP/SZ/extensionmemory|E|ifSEN set or extension relevant; otherwiseomit; unsupportedextensionrefuses|
|Pcode/literals|B STOCK IMAGE|exact originalP payload andhash|
|X:[2C46,2C67)|A|33 words: original32 mono plus naturalguard|
|Y7;Y10/19/1A/1C|A|coefficientcursor, signmask, modifierrestore and normalizationpointer|
|X:[Q+30,Q+38),[Q+40,Q+43)|A|11 preparedcontrol/gain words, slot0[5AB,5B3),[5BB,5BE)|
|X:[Q+38,Q+40)|D|eight skipped coefficients, slot0[5B3,5BB), omitted forselectedpath|
|Y:[S+0C,S+1A)|A|14 retained nonlinear/control/recursivewords|
|XCC;X39/3A/3B/40|A|group selector, ramp/block/paircount/shiftactualvalues|
|selectedgroup32words|C address;A contents|XCC=0:[2DF0,2E10),else[2E50,2E70)|
|X normalization table|C address;A/E contents|fromY1C and qualifiedmodifier/domain;512-word domain only if verified|
|X:[1600,1940)|E|832 coefficienttablewords; capture or prove exactknownupload/tableepochhash|
|Y:[F64,F69)|D underselectedproof|C2D writes beforeC9D reads; only correctoffsets/linearaddressing/nointerveningwriter|
|Y:[8F,92)|D|upstreamP657results already included in preparedtargets; addonlyforeventprovenance|
|alternate scratch input/X3C/otherYcoefficients|E|additionalmodes require theiractualinputranges; not silentlyzeroed|

Initial output scratch can be omitted where original instructions write before
read. Sparse RAM must distinguish omitted-but-defined-dead from unavailable:
unexpected undefined read is an error, never silent zero. Material modifier or
count changes invalidate the bounded footprint. Full register comparison and
timing emulation have stricter requirements than numeric post-only replay.

The selected core data inventory is100×24-bit words (300 bytes). Conservative
complete register archive43 words, active SEN0 stack0..30 words,metadata/work24..48:
167..221 words before tables. Optional full selected tables add1344 words. These
are **CALCULATED inventory / ESTIMATE allocation**, not proven free RAM placement.

## Bundle and encoding

Six canonical files: snapshot.json (manifest), x-memory.bin, y-memory.bin,
registers.json, stack.json, metadata.json. Additional raw pipeline/transport logs,
patch file and immutable table files are provenance attachments, each hashed.
No example with guessed stock values has been created.

Memory bins concatenate declared sparse fragments. Each fragment has space,
word address, count, byte offset, role, epoch andSHA256. Words are unsignedraw 24-bit,
exactly three bytes MSB-first. Count/offset/file length/overlap/mapping are validated
before import; reject padding, duplicate conflicting addresses or missing material
bytes. Record both fragment and whole-file integrity in sealed metadata.

Registers use6-digit uppercase hex 24-bit raw patterns. A/B use14-digit raw 56-bit
patterns reconstructed from 8-bit extension plus two 24-bit subfields. SC is the
5-bit *stack counter*, encoded with zero upper bits; SR.SC bit13 is distinct.
R/N/M haveeight entries; omitted D values may be null only with per-field proof
in the certified numeric profile. Material null values refuse admission. Do not
derive incoming status/memory mode from core constructor/reset defaults.

Stack frames carry physical index,high24,low24,provenance and initial SP/SC;
record LA/LC/SR LF/FV and conditional extensionEP/SZ/ranges. Save effects from
SSH pop are logged separately from original preinspection state. No arbitrary
push-order remapping or forced empty stack.

Metadata includes firmware build 4486/SYX/ARM/DSP/table hashes,capture ID/epoch,
raw/normalized PC,method,trigger,last retired instruction,pipeline evidence,
halt status, all injected/capture instructions,original instructions after trigger,
timestamp/block index if available,board/core mapping evidence,logical track,bank,
actual slot,patch bytes/hash and exclusion of all material writers. Unknown event or
track provenance cannot be replaced by a header label. Modified execution is
explicit; a hook capture is never labelled an unchanged stock pipeline.

## Existing emulator compatibility

**VERIFIED localAPI; future importer required:** ordinary registers use typed
DSP::writeReg(TReg24). M uses that API to derive mMask/mModulo. A/B use typed
TReg56raw 56-bit; the local core stores accumulators *left-aligned internally*, so
direct readRegs().a/b struct copy is wrong for this format. SC uses TReg5.
Core writeRegSSH/SSL writes selected top *in place*, unlike architectural MOVEC SSH
which pushes/pops; future installation sets physical SP index, writes each frame,
then restores original SP/SC/LA/LC/SR. SR API resolveslazy CCR state. No adapter written.

Importer sequence: verifyidentity/boundary/coherence/profile and sparse memory
coverage before CPU creation; immutable P load; strict X/Y map; typed actual modes/
AGU; active indexed stack; explicit captured/derived/dead tags;PC 9D9 last. Force
qualified interpreter andstop **before** A95; missing IRQ/peripheral/undefined memory
fails closed. Original readiness gate remains unchanged and refuses current state.

For raw9DD capture after 9DC, future automated normalization must verify R0=Y7,
unchanged prefix and no intervening mutation/IRQ. Preserve raw record; set replay PC
through a labelled proof rule, never hand-edit it. Numerical equivalence at9DD
does not imply equal hardware cycles,cache,pipeline orinterrupttimeline.

JSONSchema represents format/shape; cross-file hash/range/stack/semantic admission
requires future validator/importer. Current eight tests check structural consistency
anddesign invariants only; no full metaschema library installed, no stock file imported,
no CPU created, no replay executed. See runtime-snapshot-acquisition.md for ranking.

## Phase20B7 acquisition admission refinements — 2026-10-07

No schema/importer implementation changed. **Admission remains refused.** Future
bundle must retain dual-TAP/core association, CHIDR and original P signatures,
rawPIL/PDB/PAB and complete12-entry flow history before injections, original
pre-tool-mutationSR/N/M, all active indexed stack frames/extension state, and
controller script/version/automatic effects. Expected rawPABEX9DD andPIL56D800
are conditional on qualified no-intervening-IRQ boundary, never filled defaults.

100-word numeric minimum unchanged (slot0Y[5AB,5B9),S+0C twelve decimal words).
Actual OMR mapping/private ownership, every relevant DMA address domain and
SHI/injected-IRQ exclusion must establish one epoch; repeated equal reads alone
do not prove coherence. No universal DSP-first/ARM-first ordering established.

Correlated observed ARM pointer chain view→model→pointercell→340-byte buffer,
length/hash/publication/cache state and actual bank/slot/track/project identity
remain required, with unknown root recordedUNRESOLVED. Cached metadata is not
active proof. The existing noIRQ local replay scope is not a hardware assertion.
Future raw9DD→numeric9D9 normalization retains Phase20B6 proof requirements and
raw record. No actual capture/import/replay. Details:snapshot-coherence-plan.md;
evidencebuilds/phase20b-tapqual/final-v2/.
