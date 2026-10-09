# Phase 19C-BACKENDBOUND — backend validation and normal asset limits

## Phase 19C-PACKLINK — current scoped native correspondence

2026-10-06. **VERIFIED / NORMAL-PATH / SOURCE-DERIVED:** Components1.72.1 ZIP
array position i is the explicit native PCM index i. Wire type5 becomes internal4
at39570/3958A; initialized type map20003730 selects PCM category2. Pack ID selects
the container via3676C, then367DA→26610 uses the same slot. Flags1 absent-file
fallback3B0B4 formats `/%02d%s` with `_PCM.wav`; later rename retains decimal
prefix through39E96→1F1C0 and39EA2 validation. Native rename worker36D82 copies
raw4096-byte chunks; no WAV conversion. These are formulas, not observed paths.

Archive setter/binary clone/worker bit packing/ARM392FC/raw writer25D98 preserve
header L on successful transfer. Missing members request DELETE8→39B0E→worker5
→36CCC→26680, invalidate entry/clear presence/unlink, then2645E reindexes.
Already-absent slots can remain skipped. Full file/presence identity requires
successful completion and no foreign aliases; CRC32-skipped existing content
cannot be certified identical from these offline inputs.

**DATASET-SPECIFIC NORMAL ASSET EXCLUDED**, conditionally, for all12 completed
identical mapped native imports; prior A/S/padding geometry is unchanged.
Selected native source remains **UNRESOLVED** despite historical DLR→23 event.
Current UI send route has a scoped aggregate bound (including240-sample rounding
tolerance), not a universal firmware/backend policy. X11 STATE-DEPENDENT and
other host/async obligations remain open; no parent replay/target recomputation.
The asset branch stops pending new existing offline native/selection evidence.
Next independent blocker:P:0x204B; not analyzed here. Details/reproduction:
[PACKLINK](dsp-pack-native-link.md), builds/phase19c-packlink/final-v2/.

The older stopping condition/next step below is historical and superseded to
this extent; its backend instruction findings and immutable evidence remain.

## Phase 19C-ASSETDATA — real archives recovered, applicability open

2026-10-06. **VERIFIED / ACTUAL-DATA:** bounded read-only local discovery found
12 existing Components cache ZIPs with product=circuit-tracks,64-slot index
metadata and733 real WAVs. All pass stock predicate/file consistency. No hardware,
downloads, device export, app launch, invented samples or user-file changes.
**DATASET-SPECIFIC / GEOMETRIC:** each archive independently yields a resolved
64-record loader model; all requested low cells excluded, no clipped main
transfer/wrap. MaxA64=BF4400 (MyPack_01), not a universal normal bound.
**UNRESOLVED:** selected native pack and archive-to-native slot/filename/content
preservation; sample_i.wav does not pass native decimal-prefix parser. X11 remains
STATE-DEPENDENT. Actual selected/native and all-normal asset mutation gates remain
open; no parent replay/bridge promotion. Blanket missing-source-data stop below is
historical; new missing evidence is selection/native correspondence, not raw WAVs.
See[dsp-asset-offline-data.md](dsp-asset-offline-data.md), canonical
builds/phase19c-assetdata/final/:25 repeat-identical files,733 independent header
checks/768 arithmetic rows/24576 interval checks,1273 source hash/size/mtime guards,
firmware/extract/core checksPASS,0 CPU instructions.

2026-10-06. **Result C: still UNRESOLVED.** No stronger normal aggregate
length bound was recovered in the identified selection/index/open/read chain.
Actual source entries are absent from the repository. The requested data
stopping rule applies: no guessed project files or64-length sequence is created.
Requested X-cell asset contributions remain **UNRESOLVED**. X-space selection
is **STATE-DEPENDENT**, with a conditional Y result for serialized later records.

Strictly offline: no hardware, packets, firmware modifications, original/ edits,
installations, network, Plaits, metadata seeding, CPU execution, generic alias
census or P204B work. Parent replay remains closed; bridge not recomputed.

**Correction to ASSETBOUND:** the actual asset backend slot is **20003738**,
not2000691C. Literal37268=20003730 feeds36AF0/36AF6's `[base+8]` load.
Literal37264=20006914 feeds the separate selection-container load. Earlier
ASSETBOUND source-provenance/graph statements conflated these two literals.
Their page/length/chunk/padding arithmetic remains valid. Existing exports are
preserved; this phase's byte-checked object graph supersedes that attribution.

Canonical evidence: `builds/phase19c-backendbound/final-v3/`,
`final-v3-repeat/`, `checks-v3/`; decoder witnesses `probe-canonical/`.
Earlier probes and final/v2 outputs are retained as intermediate versions.

## A. Complete26610 contract

**VERIFIED function boundaries:**08026610..0802667C, next function26680.
Signature recovered from register/stack use:

`status =26610(C=r0, B=r1, category=r2, index=r3, flags=[entry SP])`.

R4=C, R5=B, SB=category, R8=index, R7=flags. Category pointer is
`C[28+4*category]` (26618/26624). Lookup3B084 loads its list at+2C, calls
vtable+14 (1A9F6), tests presence through vtable+10→5C24A→48EB0, and returns
an indexed40-byte entry through vtable+18→5C16C only if present.

| Path | Exact result / action |
|---|---|
|flags.bit0=0, lookup null|26630 returns12 without opening B|
|flags.bit0=0, entry present|3B08C reconstructs its path; B.vtable+0 opens/selects it|
|flags.bit0=1, missing entry|Fallback path construction using `/%%02d%%s` and category suffix; not taken by stock asset flags0|
|Open result1|Final26674..7A returns1|
|Other final open result|Returns0; do not interpret this generic normalization as validating every metadata field|

No category bounds check exists **inside26610**. Its stock asset caller367DA
supplies type4→category2, byte indexi and flags0; category/index trust is traced
through these callers rather than assumed for arbitrary entry.
It returns a status, not an allocated file/source object. The existing B is
modified by its open method. Missing entries are explicitly possible.

Input classes:

- **CONSTANT:** type4, flags0, loop indexi for each enumerated record0..63.
- **BOUNDED ENUM / INIT-ONLY:** type map20003730 bytes `05 05 00 01 02 03 04 00`;
  type4 maps tocategory2. INIT value provenance is the already verified ARM
  initialized-data decode. Runtime table persistence outside this slice remains
  a premise, not a new global alias exclusion.
- **PROJECT-DATA / UNRESOLVED:** current selection byte, directory presence,
  stored names and parent links. ScopeFF resolves current selection in3676C.
- **INIT-ONLY:** concrete object constructors/publications below, not actual
  CPU boot or a complete runtime allocation-success proof.

## B. Object graph and lifecycle

**VERIFIED original constructor/publication path1F0F0:**

| Slot / object | Construction and layout |
|---|---|
|20003738 backend B|1F0FC allocates90 bytes,1F102 calls25C98,1F11E publishes B. A second instance is published at2000373C|
|B+0|vtable805B150, stored25CA2 (literal25DF4)|
|B+4|Active file-structure pointer; initialized0, set to B+8 on open, cleared on close|
|B+8|Allocated file-structure storage of0x1028=4136 bytes (25CA8..CB0)|
|B+C|Open flag; initialized0, set1 after successful open25D00, cleared25D2C|
|B+D onward|Selected path string;25D06 stores it,5C274 returns its address|
|20006914 selection container C|1F162 constructs40-byte container via263F8;1F166 publishes at[2000690C+8]|
|C+0 /+1 /+24 /+3C|Selection byte /32-byte name /parent link /parent container|
|C+28..38|Five category pointers created263F8..6456|

C is a plain container:263F8 does not assign it a vtable. Its separate category
objects contain indexed-list references. B's vtable, with Thumb bit removed:

| Offset | Function | Recovered role |
|---|---|---|
|+0|25CB8|Open/reuse path; close current path if changed|
|+4|25D10|Close; clear active pointer/open flag|
|+8|0|No target|
|+C|25D32|Path operation; not an asset-length validator|
|+10|25D4C|Read destination/count/offset with output count|
|+14|25D98|Other transfer method; not selected by this read path|
|+18|25E08|Seek through1A12C|
|+1C|25E1C|Return open file's +C extent;0 when closed|
|+20|25E34|File operation through1A010|
|+24|5C274|Return stored path B+D|

Do not confuse vtable+24's stored path with the size method+1C.
The alleged2000691C read-object slot is not established by this chain and was
not subjected to a generic alias investigation.

## C. Source classes and64 optional entries

**VERIFIED initialized descriptor table805A4F8:** five12-byte descriptors.
Capacities are64,16,64,2,2. Category2 has tag2, capacity64, label `PCM`
and nominal suffix `_PCM.wav`. Constructor2642A passes capacity64 to3ADF0;
its presence bitmap uses8 bytes (48E84), entry storage64×40 bytes (3AE0E..26).
This bounds index/state allocation, **not file payload bytes**.

3AE34 scans a filesystem directory and clears the presence map before rebuilding
it. Accepted names yield a byte index through1F1C0;3AE90/3AE9A rejectFF and
indices>=capacity. Successful entries store index and up to32 name bytes,
set presence and increment the directory count. Absent indices need not exist.
All64 indices are structurally supported; no fixed subset is absent by design.
Their actual presence is **PROJECT-DATA**, not known from firmware.

**VERIFIED prefix rule:** two or three decimal characters followed by underscore;
three-digit conversion is truncated to8 bits at1F20E. Thus filename aliases and
duplicate overwrites are structurally possible. The stored scanned filename is
used for present entries; do not substitute an invented `%02d_PCM.wav` filename
for every index. This format is a fallback in26610's flags1 missing-entry path.
Directory-order/index data is needed if multiple names map to the same byte index.

Source class: **VERIFIED filesystem-backed selected-container/category entry**,
not a fixed embedded PCM asset. Specific project/session/user/external origin
is **UNRESOLVED**. PCM naming plus local WAV checks supports audio-asset
interpretation; it does not establish upstream normal acceptance policy.

## D. File extent, seek and read validation

**VERIFIED:**25CB8 reuses an already-open identical path. On change it closes
the old file, points B+4 to its storage, and opens at19AE4 with mode13 (25CE4).
19AF4 retains low6 mode bits and19C04 stores them in file+10. On-disk directory
record+1C is decoded into file+C at19BE0..BE8; file+14 is initialized position0.
The backend therefore knows the file extent and exposes it through25E1C.
No maximum sample size or64-file aggregate comparison occurs in this open path.

**VERIFIED read25D4C:** closed object returns1. A differing requested offset
calls vtable+18 seek25E08; its status is ignored before calling19CC6. That read:

- initializes output count0 (19CD4);
- checks object validity, saved error and read-permission bit0;
- sets transfer count to `min(requested, file_extent-file_position)` at19CF6..9D02;
- copies only transferred prefix bytes and advances file position/output count;
- returns success0 on EOF short count; errors may return after partial progress.

**Important qualification:**1A12C clamps a beyond-EOF seek to extent only if
write-permission bit1 is clear (1A14C..158). Mode13 retains bit1, so this clamp
is **not unconditional** for this backend. The write-enabled seek path may
allocate additional clusters and increase file+C (1A1CE..1DA,1A20A..21A).
This describes stock instructions only; no storage writes were performed.

The read still bounds emitted bytes by its then-current extent. There is no
unconditional backend test `requested_offset+requested_count<=original_size`;
it clips reads instead of validating the complete request against original size.
Filesystem allocation/sector/cluster checks impose backing-volume constraints,
but no concrete normal volume geometry or per-container aggregate byte budget
was recovered. No product UI capacity was borrowed.

## E–F. L consistency and aggregate bounds

**VERIFIED:** no recovered selection/open/read/index operation compares header
L with file extent or total other asset lengths.49C34/51B80 uses L from the
header independently, as in ASSETBOUND. EOF/short-count clipping does not
change R8. Main limit clipping likewise does not change it.

For a successful full request, backend count establishes only that those requested
bytes were delivered. If an entire un-clipped main payload is read, it covers
`B=L&FFFFFE00`, which can be511 bytes less than L. For clipped main output,
only its shorter prefix is demanded. Neither yields an unconditional metadata-L
bound because the loader ignores read status/count and header/file consistency.

The64-entry list capacity and40-byte entry allocation are not a64-asset sample
byte budget. Directory entry records contain names/presence, not recovered
sample-length constants. **UNRESOLVED NORMAL-PATH:** any stronger validation
when the backing container/files were originally created/imported, their normal
sizes, available storage and aggregate coupling. No claim is made that no such
validator exists elsewhere in the firmware/application ecosystem.

Per-index `source-records.csv` retains unknown presence/path/size/L/normal bounds.
Absent entries that fail selection before copying leave the cleared header zero,
take invalid-header advance256; their actual indices are not known.

## G–I. Cumulative domain and critical residues

There is **no recovered stronger normal upper bound** to substitute for the
ASSETBOUND predicate envelope. The exact formula remains:

```
A_i=580000+256*i+256*sum(valid_j*floor(L_j/512), j<i)
S_i=((A_i&FFFF00)-2) mod2^24
R8_i=256+((L_i&FFFFFE00)>>1) if valid, else256
```

The previously verified conditional envelope hasA64<=24F74000, no32-bit wrap.
It is retained as an **upper envelope**, not relabeled accepted normal data.
`normal-address-progression.csv` has64 unseeded rows, unknown actual sequence
and unchanged exact main/padding formulas. All main low-target exclusions and
the first two records' padding exclusions remain **EXCLUDED locally**.

Critical-page constraint for residue p:

`sum(q_j,j<i)=(p+n*1000000-580000-256*i)/256`, `q_j=valid_j*floor(L_j/512)`.

For each p=0,100,900,A00:

| Records | Predicate envelope | Normal accepted constraints |
|---|---|---|
|0–1|EXCLUDED|IMPOSSIBLE UNDER NORMAL BOUNDS, within stable local envelope|
|2–63|POSSIBLE arithmetically|UNRESOLVED; actual presence/L/aggregate/storage domains absent|

No concrete length sequence was fabricated to satisfy this equation. Per-record
256 critical-page rows are exported;248 remain normal-UNRESOLVED. These four
pages cover all low targets potentially hit by256-word padding at S+N. In this
envelope, low-page records haveA>=1000000, mainN=0, so other padding residues
cannot add a requested low target: pages0/100 cover descriptors;900/A00 cover
selectors/table. Normal padding intersection remains **UNRESOLVED**, not
POSSIBLE UNDER NORMAL BOUNDS on predicate bounds alone.

## Read failures and destination contents

**VERIFIED:**36B08 compares output count with requested count; short count
returns4, backend error1 maps to2, selection failure follows separate status5.
49ABE/49B36 ignore the resulting3CBD6 status.

Header destination2000665C is zeroed64 bytes before each header request.
Missing-entry/open/early failure with no copy therefore leaves zero, usually
invalid signatures. A partial transfer overwrites only its prefix; the suffix
remains cleared. A sufficiently complete header prefix may still pass the local
predicate despite short count. No backend tail zero-fill was found.

Main alternating buffers are not cleared for each read. A short/error transfer
may leave suffix bytes from earlier transformed contents, then the loader reverses
halfwords and sends the requested chunk length. Such bytes are **UNRESOLVED**,
not seeded zero or reconstructed samples. Failure/corrupt paths are not asserted
normal; they also cannot justify a metadata consistency guarantee.

## J. Narrow loader ancestry

3CC46 belongs to3CC44; reviewed incoming edges30CBC/30E10 retain their
selection-notification/load-transition context.30E04 invokes assets before
further selection/state publication. Exact **NORMAL PROJECT LOAD / NORMAL
SESSION LOAD / PATCH / SERVICE** provenance remains **UNRESOLVED**; filenames
alone were not used to choose one. No whole project/session format investigation.

5BFD0 belongs to callback5BFCC. Decoded ARM initialization stores its Thumb
pointer at20000A8C (**INIT-ONLY publication**); that does not prove the callback
executes at boot or establish its normal/service ancestry. These unresolved
entry classes prevent global normal path conclusions independently of file data.

## K. X11 space requirement

**VERIFIED local protocol:** page171..178 updatesX10 and retainsX11.
Control word20xx branches163 and width-handler12D modifyX12/HCSR, notX11.
Data19B/19D choosesY/X usingX11.bit15.

Every record's predecessor49A5E→297D6 is a tail call to1EB1E. Its entire body
storesAAAA to ARM40003000, then returns; it does not send a DSP address setup.
Header backend reads and width controls precede the fresh page command.

After a record's padding, the recovered sequence is:

`Y2C read → scalar C00,C01,C02,C03 → scalar802C → next record`.

In uninterrupted order, C03's scalar suffix stores cachedC04. Final802C
cannot hitC04, so292DC emits private header00802C; DSP185 publishesX11.bit15=1.
This conclusion does not require initial scalar-cache coherence: each scalar
suffix updates the cache regardless of a hit. Subsequent width/page commands
do not clear that Y flag.

**Conditional VERIFIED Y:** every later record selectsY under complete serialized
stock transfer order with no foreign host/cache/X11 mutation. Record0 inherits
unknown prior space. Blocking source reads, backend waits and width/control waits
do not themselves prove absence of other host activity. Thus the requested
all-normal classification is **STATE-DEPENDENT**, not PROVEN X or globally
PROVEN Y. No actual X-overlap witness is claimed from page geometry.

## L–O. Asset contribution, stopping rule and missing data

**Result C: still UNRESOLVED.** Every requested selector95A..95F,
table[9DB,A12) and14 descriptor+0 cells has asset-loader contribution
**UNRESOLVED**. Later predicate padding geometry remains possible; accepted
normal aggregate/entry state and X-space interleaving are not closed.
No universal ownership promotion or removal of this family from host obligations.

**STOP applied:** no source assets/project files were found in the project inputs.
Minimum offline data needed:

1. Existing unmodified copy of the selected source container/pack directory,
   preserving actual subdirectories, names, listing order where relevant,
   duplicate index aliases and missing entries.
2. All its indexed PCM-category entries0..63, with actual file sizes and complete
   headers through each data-length field. Full original files are needed to
   close payload consistency/short-read behavior; directory/headers suffice
   initially to compute metadata-derived advancement.
3. Selection context tying that directory to the loader invocation, plus its
   existing `_SESSION.ncs`/`_META.ncm` or equivalent exported path/index metadata
   when needed to resolve the parent association. These names are code-derived
   suffixes, not invented file contents.
4. Only if claiming a filesystem/partition budget: existing offline backing-volume
   geometry/allocation metadata or original storage image. No hardware export
   or transmission is requested as part of this phase.

Actual files cannot by themselves prove all possible normal imports or X11
ordering. They provide a specific admissible dataset; universal acceptance
policy and host serialization remain separate if that stronger claim is desired.

Independent mechanisms retained without reopening: other normal host
cache/cursor/port/width/order and entry ancestry; P204B; other indirect DSP writers.
P1E15 reachability staysUNRESOLVED; parent replayNO, target bridge unchanged.

## P. Single best next step and reproducibility

**Obtain the existing offline selected PCM directory/files and selection metadata,
then compute their actual64-record metadata advancement and page/padding map.**
Do not substitute guessed lengths or a generic writer census. Any normal X-write
claim still needs the independent host-order/retainedX11 condition.

```powershell
$py='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B tools/ct_backend_probe.py --output-dir builds/phase19c-backendbound/new-probe
& $py -B tools/ct_backend_bounds.py --probe-dir builds/phase19c-backendbound/new-probe --output-dir builds/phase19c-backendbound/new-audit
& $py -B tools/ct_backend_bounds.py --probe-dir builds/phase19c-backendbound/new-probe --output-dir builds/phase19c-backendbound/new-repeat
& $py -B emulator/tests/verify_backend_bounds.py --probe-dir builds/phase19c-backendbound/new-probe --first builds/phase19c-backendbound/new-audit --repeat builds/phase19c-backendbound/new-repeat --output-dir builds/phase19c-backendbound/new-checks
```

Existing Capstone access was read-only; no installation. Decoder windows label
code/data boundary review and halfword edge candidates; data/pointer matches
are not silently promoted to normal calls. **VERIFIED checks:**12 canonical files
byte-identical on repeat;8 contract tests; overwrite refusal; original SYX/BIN
hashes and in-memory decode/roundtrip; all10 extracts; sealed19A/prior fullhelper
guards. Zero ARM/DSP CPU execution. All actual lengths/witnesses remain unknown.
