# Phase 19C-ASSETBOUND — 64-record asset address bounds

## Phase 19C-ASSETDATA — concrete archive models

2026-10-06. **ACTUAL-DATA VERIFIED:**12 cached Circuit Tracks archives,733
accepted real WAVs and12 independent64-slot metadata maps. *New Pack1 lacks
archive slots38..63; MyPack_01 lacks49..51/56..61, all with empty metadata names.
No missing L values invented. **DATASET-SPECIFIC GEOMETRIC:** all768 model
records resolve; no clips/wraps/requested-cell hits. Combined interval perpack
[57FFFE,A64-2), largestendsBF43FE. Real archive lengths replace predicate maxima
for these datasets only, not all normal imports. Native filename parsing rejects
sample_i.wav; actual native selection/content preservation remainsUNRESOLVED.
X11STATE-DEPENDENT, no X/Y-write claims, normal host family not closed.
See[dsp-asset-offline-data.md](dsp-asset-offline-data.md) for exact CSVs/provenance,
25 repeat-identical artifacts and protected source/firmware/core checksPASS.
No hardware/user-file modifications/newCPUexecution/bridge recomputation.

## Phase 19C-BACKENDBOUND — correction and current gate

2026-10-06. **VERIFIED correction:** actual asset backend slot20003738 is
loaded via literal37268=20003730 and `[base+8]` at36AF6. The separate slot
20006914 holds the selection container; prior attribution of its+8 as the read
backend was incorrect. Original ASSETBOUND exports remain preserved/historical.
This corrects object provenance, not the verified length/page/chunk/padding math.

**VERIFIED:**26610 flags0 requires a present indexed entry; category2 has a
64-entry presence map and40-byte name records, no recovered sample-byte budget.
Actual backend25C98/vtable805B150 has file-size method25E1C and read25D4C:
read count clips to extent, but headerL is never compared to that size in this
chain. Its mode13 has write permission; seek clamping to originalEOF is not
unconditional. No stronger normal aggregate L bound was recovered.

**STATE-DEPENDENT X11:** page/width controls retain space. Final802C after
C03/cacheC04 forces a private Y setup in uninterrupted stock order; later
records then useY. Foreign host ordering across waits remains unproved, so this
does not globally exclude X mutations. Normal padding feasibility and requested
cell contributions remainUNRESOLVED; asset family NOT CLOSED, replayNO.

**STOP:** exact normal source constraints require absent offline selected PCM
directory/files and selection metadata. See
[dsp-asset-backend-bounds.md](dsp-asset-backend-bounds.md) for exact data list.
12 repeat-identical artifacts,8 tests/overwrite refusal/protection checksPASS,
0 CPU ops. Canonical builds/phase19c-backendbound/final-v3/. Earlier findings
below retain their labels and premises; backend provenance above supersedes them.

2026-10-06. **VERIFIED:** the local header predicate bounds L to at most
19,200,000 bytes. **EXCLUDED:** all main transfers and the first two records'
padding exclude the requested low control cells under the recovered local
transaction premises. **PROJECT-DATA / UNRESOLVED:** subsequent padding can
intersect every requested target in the predicate-permitted address envelope;
actual normal source constraints and retained X/Y selection are not established.
**The normal asset host-mutation family is NOT CLOSED.**

Strictly offline: zero ARM/DSP CPU instructions, no hardware, packets, firmware
patches, original/ changes, tool installation, network, metadata fixtures or
Plaits implementation. No target-bridge recomputation or parent replay. No
P:204B or generic DSP alias census. Numeric domains below are arithmetic
quantifiers derived from original instructions, never loaded record contents.

Canonical evidence: `builds/phase19c-assetbound/final-v2/`,
`final-v2-repeat/`, `checks-v2/`; targeted original-byte decoder evidence:
`probe-canonical/`. Earlier probes/final remain intermediate evidence; the
initial final's N_max calculation was superseded because clipped full chunks
can emit fewer words than a smaller length with an admitted partial tail.

## A. Record structure and completion

**VERIFIED:** function 08049A1C first calls 0803676C with the incoming selection
argument. If it returns 1, the loader returns 0 before any record. Otherwise
49A24 sets A0=580000. Index R6 starts at zero (49A50), is passed as a byte to
49A80 (49A64/66), increments at 49A6C and is tested against 40 at 49A6E/70.
There is no validity-dependent loop break. A completing success path performs
**exactly 64 child calls**, indices 0..63. Across all possible invocations,
64 is an upper bound: the initial refusal or waits/backend failures can prevent
completion. Do not assume all64 execute in an actual session.

This is **not a recovered firmware-resident array of 64 fixed-size records**.
Every child clears/reuses the same64-byte header buffer at ARM2000665C
(literal49C20; 49A96) and reads offset0,64 bytes via49ABE. Its three-word
selector on the stack is `(4,index,FF)` (49AA2..49AB0). Valid/invalid is the
predicate below, not a separate table marker. Main reads use source offset
`1C+q` (51B8C, input offset0), advanced by chunk bytes at49B34.
Source object identity, file sizes and normal source correlations are unresolved.

INIT-ONLY original ARM initialized data contains vtable805B9EC at20000A7C.
Its recovered +0/+8/+C/+10 callbacks are49C88/49C96/49C8A/49CFA.
The49C96 callback visits32 positions using index/threshold arithmetic; these
callbacks do not supply a static length table or choose record i's header.
Current runtime vtable persistence is not inferred from initialization.

## B. Metadata provenance

**VERIFIED local data flow:**

`49ABE → 3CBD6 → 3CA52(opcode6) → 22A46/22A5C queued submission/wait`

`22AE4 worker → TBH22B24/table22B28[6] → 22BBE → 36A7E`

For selector type4, 36AD8 calls3676C with selector.scope FF, then367DA selects
the index (through26610). On success,36AF0 loads object20006914+8 and36B02
calls its vtable+10 read method with destination, byte count and offset.
36B08 compares returned byte count with the requested count and returns status;
**49A80 ignores the status returned by3CBD6** at49ABE and49B36.

The metadata word is read by51B80 from `p+18+u32(p+10)`, p=2000665C,
after49C34 repeats51BA0. It is a runtime read-buffer word, not a static
firmware constant. **UNRESOLVED source classification:** backend storage,
normal project/session data versus user/external content, its upstream size
validators and complete file contents. WAV-like signatures support an asset
header interpretation; they do not prove every source is valid normal data.
No asset headers/project files were supplied or reconstructed.

## C. Exact validity predicate

**VERIFIED:** 51BA0..51C08 returns true only if all rows hold. String comparisons
use52B8A with count4; the four nonzero signature characters make equality exact.

| Field | Required value | Instruction evidence |
|---|---|---|
|bytes p+0..3|RIFF|51BA8..51BB0, constant51C10|
|bytes p+8..B|WAVE|51BB4..51BBE, constant51C18|
|bytes p+C..F|fmt followed by space|51BC4..51BCE, constant51C20|
|q=u32(p+10)|Used unchecked to form d=p+14+q|51BD0..51BDC|
|bytes d..d+3|data|51BD8..51BE2, constant51C28|
|L=u32(d+4)|Unsigned L < 0124F801 =19,200,001|51BE4..51BEA, literal51C0C|
|u16(p+16)|1|51BEC..51BF0|
|u32(p+18)|48000|51BF2..51BF8|
|u16(p+22)|16|51BFC..51C00|

The last fields align with mono/48kHz/16-bit WAV header conventions, but the
predicate **does not check** PCM format tag atp+14, RIFF sizep+4, q bounds or
q==16, byte ratep+1C, block alignmentp+20, L parity, available file length,
read success or aggregate64 length. If q takes the data header outside the
64-byte buffer, these are reads of other ARM addresses, not a safely validated
file header. This malformed path is kept distinct from normal valid assets.

Local length bounds assume a stable header across repeated predicate/accessor
loads. The wait completes the read request; it does not independently prove
every possible foreign/async mutation of2000665C is absent. No such mutation
was recovered in this targeted slice; no global exclusion is claimed.

## D–E. Length and cumulative 32-bit domains

**VERIFIED predicate-derived upper envelope**, conditional on stable accepted
headers and completed records:

```
valid:   0 <= L_i <= 19200000
q_i = floor(L_i/512) in [0,37500]
invalid: q_i = 0  (L_i not used)
R8_i = 256*(1+q_i) in [0x100,0x927D00], step0x100
A_i = 0x580000 + 256*i + 256*sum(q_j, j<i)   (ARM u32)
A_i in [0x580000+0x100*i, 0x580000+0x927D00*i], step0x100
A_64 in [0x584000,0x24F74000]
```

No32-bit overflow occurs even at the upper envelope, including a1024-word
chunk addition. No early24-bit truncation was substituted for49A6A's ADD.
The full64 row progression is in `address-progression.csv`; all actual L/A/S
fields are blank, not guessed. These are conservative bounds for real sources,
and exact arithmetic envelopes if independently predicate-permitted q values
are available. **UNRESOLVED NORMAL-PATH:** their actual independence and the
producer's stronger aggregate limit. This is not a fabricated64-length sequence.

## F. Effective page starts

**VERIFIED:** every A_i is256-aligned in this envelope.

`S_i = (((A_i & FFFF00)-2) mod2^24)`.

A0 produces57FFFE. Record1 permits37501 pages; record0 permits one.
For **each record i>=2**, the conservative A interval spans at least one complete
24-bit period on the256 grid, so all65536 page residues are predicate-permitted.
Proof: `i*(927D00-100) >= FFFF00` for i>=2. This is source-domain algebra,
not brute force over arbitrary32-bit lengths. The script enumerates at most
65536 page residues per record solely to verify the finite page projection.

Distinct aligned A values map to the same S exactly when their difference is
a multiple of1000000. Cross-record repeated pages are permitted from record2
in the envelope; none is asserted to occur in an actual project.

## G. Main emission, strict guard and intervals

**VERIFIED:** B=`L & FFFFFE00` byte count; main chunks are
`c=min(B-bytes_consumed,800)` bytes at49B60..6C. The final tail, when present,
is512/1024/1536 bytes (256/512/768 words). Full chunks are2048 bytes,1024words.
The virtual test at49B12..18 is:

`if u32(A_current + c/2) >= E80000: stop BEFORE this chunk`.

The loader reverses16-bit halfwords and transmits width16 via296B0. Per-record
attempted full chunks: `f=floor((B/2)/1024)` (max9375); tail t=(B/2)%1024.
For A<E80000, full chunks accepted =`min(f,floor((E80000-1-A)/1024))`.
If all f fit, tail fits only if `A+1024*f+t<E80000`; otherwise no tail.
For A>=E80000, no main words are emitted. Clipped output NEVER changes R8.

Exact main intervals are `split24(S,N(A,L))`. All main writes lie in the
conservative high envelope `[57FFFE,E7FFFE)` and cannot wrap; **every requested
low target is EXCLUDED for every main transaction** in the local model.

Maximum N over permitted lengths at given A is
`min(927C00,256*floor((E80000-1-A)/256))` when A<E80000, else0.
It must not be computed only at maximum L: atA0, maxL emits8FFC00 words,
while a smaller admitted partial tail can reach8FFF00. Tests cover this
discontinuity. Per-record N maxima and intervals are in `effective-intervals.csv`.

## H–J. Padding, cache and wrap

**VERIFIED:**49B76..94 clears512 ARM bytes and sends them synchronously via
2968E, yielding256 zero words. It does this even on invalid headers or a main
limit exit, at the existing cursor, without another page setup or limit test.
Exact padding: `split24((S+N) mod2^24,256)`.

**VERIFIED cache conclusion (A):**49AC8..49AD0 always extracts the page and
calls294AC directly.294AC emits the address header; it has no scalar-cache
comparison. Thus a stale20003D00 hit cannot suppress a new record's setup.
Main chunks/padding then continue from that cursor. Post-padding Y2C polling
and C00..C03/mailbox metadata traffic occur afterward; next record resets
the page again. This closes the **asset-start scalar-cache suppression** concern,
not all foreign transfer ordering or the shared global scalar cache.

**UNRESOLVED X/Y:** recovered page-write171..178 preserves DSPX11;
data198..19E stores via19D toX whenX11.bit15=0, via19B toY when it is1.
Fresh address setup does not establish fresh memory space. Local nominal
page geometry is verified; actual normal X-space writes require this additional
protocol/ordering premise. The conclusions do not silently setX11 tozero.

Padding wrap is possible **only when A_i mod1000000=0** in this envelope.
Such A_i>=1000000 has no main output. S=FFFFFE and padding writes exactly
`[FFFFFE,1000000)` plus `[0,FE)`. Main never wraps. Records0–1 cannot meet
this condition; every later record permits it in the upper envelope.
`wrap-domains.json` exports every record's condition, with actual wrap UNKNOWN.

## K–M. Requested intersections and ancestry

**EXCLUDED:** records0 and1 main+padding do not intersect any requested target.
**EXCLUDED:** all64 main transfers exclude every target.
**PROJECT-DATA:** each record2..63 permits padding intersections, in the
predicate-only envelope, with selectors[95A,960), table[9DB,A12) and all14
descriptor+0 cells. A predicate-valid L<512 or an invalid header both permit
N=0; these are domain alternatives, not assigned record values.

| Page residue of A | Padding interval | Requested overlap |
|---|---|---|
|0|[FFFFFE,1000000),[0,FE)|EB,F3,FB (103 is outside this exact low interval)|
|100|[FE,1FE)|103,10B,113,11B,123,12B,133,13B,143,14B,153|
|900|[8FE,9FE)|all selectors; table[9DB,9FE)|
|A00|[9FE,AFE)|table[9FE,A12)|

For each row, a permitted cumulative A is determined algebraically by
`A_min + ((residue-A_min) mod1000000) <= A_max`.
`requested-cell-intersections.csv` has2048 results:64×2 transfer parts×16
targets (two ranges plus14 cells).992 rows are INTERSECTION POSSIBLE;
1056 are EXCLUDED FOR ALL VALID L. These are not992 normal observed writes.
All actual-intersection columns remain blank. Each positive row records its
conditional page interval and X-space requirement.

**Updated asset-family classification:** each selector, effect table and
descriptor+0 cell is **PROJECT-DATA DEPENDENT** for the address domain;
actual normal X writability remains **UNRESOLVED**. None is NORMAL ASSET
WRITABLE or globally NORMAL ASSET EXCLUDED on the present evidence.

Call-site ancestry, kept narrowly scoped:

| Site | Verified predecessor | Entry-mode conclusion |
|---|---|---|
|3CC46|wrapper3CC44; inbound30CBC/30E10.30C70 compares notification/state fields, subtype4 and selected byte;30E04 invokes loader before selection-state publication|Selection/load-transition candidate; NORMAL PROJECT LOAD versus SESSION/PATCH/other **UNRESOLVED**, no string-only semantic label|
|5BFD0|wrapper5BFCC loads a byte from its callback argument. Original decoded ARM initialization publishes805BFCD at20000A8C|**INIT-ONLY pointer value**; actual runtime callback ancestry **UNRESOLVED**. Raw pointer match5C628 is compressed data, not evidence of a direct executable call|

No callback pointer alone proves BOOT/INIT execution or SERVICE exclusion.
Asset headers meeting the local predicate are distinct from **VALID NORMAL DATA**:
normal source-file/aggregate constraints are unresolved. Out-of-buffer q,
failed/partial reads or inconsistent file/header lengths are **MALFORMED/CORRUPT
candidate paths**, not normal counterexamples. User/external supply and accepted
normal policy await backend validation evidence; no safety assumption was borrowed
from a file format, product sample capacity or editor UI.

## N–P. Consequence and next step

**UNRESOLVED:** this asset mutation family cannot be removed from the P19D
host-preservation obligations. Fresh page setup and all main-transfer low-cell
exclusions are closed locally; later padding remains data-dependent. No real
normal target-producing state has been recovered, P1E15 is neither established
reachable nor excluded, and active-parent replay stays closed.

Independent obligations remain: other normal host cache/cursor/port/width order
and transition ancestry; P204B; other indirect DSP writers. They were not reopened.

**Single best next step:** trace26610 and the20006914+8 backend's selection/read
validation to derive a bound on accepted **normal cumulative** asset lengths.
That can decide whether the low-page padding alternatives are normal-feasible;
before a positive X-write claim also establish the retainedX11 space at that edge.
If the bound depends on absent project/sample data, request that offline data
instead of manufacturing record lengths or broadening to generic aliases.

## Reproduction and preservation

Run with the existing pinned Python; no dependencies are installed. The probe
requires read access to the existing Capstone copy, as in HOSTWRITE.

```powershell
$py='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B tools/ct_asset_probe.py --output-dir builds/phase19c-assetbound/new-probe
& $py -B tools/ct_asset_bounds.py --probe-dir builds/phase19c-assetbound/new-probe --output-dir builds/phase19c-assetbound/new-audit
& $py -B tools/ct_asset_bounds.py --probe-dir builds/phase19c-assetbound/new-probe --output-dir builds/phase19c-assetbound/new-repeat
& $py -B emulator/tests/verify_asset_bounds.py --probe-dir builds/phase19c-assetbound/new-probe --first builds/phase19c-assetbound/new-audit --repeat builds/phase19c-assetbound/new-repeat --output-dir builds/phase19c-assetbound/new-checks
```

**VERIFIED checks:**11 canonical artifacts byte-identical,9 arithmetic tests,
overwrite refusal, SYX/BIN expected SHA256s and in-memory decode/roundtrip,
all10 stream/payload hashes, sealed19A source audit and prior fullhelper manifest.
Original SYX `bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd`;
BIN `b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da`.
Zero ARM/DSP CPU execution; no metadata state supplied to an emulator or device.
