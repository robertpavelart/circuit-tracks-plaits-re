> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 19C-PACKLINK — archive/native correspondence

2026-10-06. **VERIFIED / SOURCE-DERIVED / NORMAL-PATH:** the recovered installed
Components 1.72.1 Tracks ZIP import and successful transfer route retains archive
slot i as native PCM index i and transfers the original WAV header, including L.
Missing members reset that model slot and request deletion, rather than create a
zero-length WAV. **UNRESOLVED:** actual current native contents/selected source.
These are static code contracts, not observed import execution or device state.

The twelve actual cached datasets can reuse their independent ASSETDATA maps
**conditionally on a completed identical native import**, successful presence
updates, no duplicate native index aliases and no subsequent foreign edits.
Checksum-skipped slots require identical existing content; CRC32 alone does not
prove literal equality. Selected-dataset closure and universal closure are **NO**.
Stop the asset branch absent new existing offline native/selection evidence.
The next independent obligation is **P:0x204B**, not analyzed in this phase.

Strictly offline: no Components launch, hardware, network/download, MIDI/SysEx,
wire message generation, device export, audio rendering, firmware patch, original/
or user-file edits, DSP/ARM CPU execution, or Plaits implementation.

## Evidence and identity scheme (A)

Canonical evidence: `builds/phase19c-packlink/final-v2/`, `final-v2-repeat/`,
`arm-final-v2/` and `checks-v2/`. Earlier exports are preserved as intermediate
evidence. `source-witnesses.json` records exact Unicode character and UTF8 byte
offsets, excerpts and source hashes; ARM listings are checked against the BIN.
Do not use minified-bundle character offsets as byte offsets.

**VERIFIED installed source:** existing ASAR, not an executed application:

`C:\Users\rober\AppData\Local\Components\app-1.72.1\resources\app.asar`

99,579,473 bytes, SHA256
`78e69be6909ecaf9c92e0accb660a28874d8d90fd98afd847c8e02a387f774bf`.
The ASAR manifest and recorded member integrity hashes support the extracted
app JS/package code. Main bundle SHA256
`96304dd0486561a20aa10fcbc5659166ecc9dbd0806a43fb947d12d05c4ca5b8`;
worker SHA256 `9fe51cd33169ed500209d4baba712ac85926e7ccdad8af4ba25f70e4252aad21`.
Extraction excludes node_modules; installed source is never imported/executed.

**ACTUAL-DATA:** all twelve archive `index.json` objects identify product
`circuit-tracks`, version `2.0`, with 64 sample records. They contain name/version/
product and collection metadata, but no embedded stable pack UUID/ID. Full archive
SHA256, actual cache key and metadata are the identity for every dataset, rather
than mtime or archive listing order. `archive-identities.csv` records each one.

Existing cache response `f_0001e4`, SHA256
`2950cc97d1b324b162853f5ca05f4d2606b270f1e67938393dbed508a92f06f2`, has exact
parsed metadata equality to these two index objects:

| Archive | Remote API record ID | Evidence |
|---|---:|---|
|MyPack_01|530016|Existing response metadata equals actual index.json|
|*New Pack1|521732|Existing response metadata equals actual index.json|

Remote IDs are not firmware destination pack IDs. For the other ten datasets a
remote ID/slug/UUID is **UNRESOLVED**; archive content identity is verified. Cached
file URLs were retained as evidence only, never requested.

Read-only targeted cache/storage inspection completed before this continuation:
eight matching files and two whole JSON responses. The firmware-catalog JSON is
not selection evidence. Raw LevelDB/log matches are historical bytes, not an
authoritative reconstructed database state; no database was opened writable and
no authentication/cookie store was read. See `metadata/sources.json`,
`matches.json`, `documents.json` and the sanitized `event/` evidence.

## Import and conversion path (B, D, E)

**VERIFIED source chain:**

```
index.samples[i].url
  → N7.loadPackFileContent: ZIP member .async("arraybuffer")
  → this.samples[i].target.fileData = bytes
  → f0 setter: this.binary = bytes
  → persistent model.slotIndex = i (y0 constructor, 0..63)
  → sendEntitySet: push(model, destinationPackId, model.slotIndex)
  → S8: binary.slice(0), preserving all bytes
  → worker chunk packing, preserving all bits
  → ARM 0x080392FC inverse packing
  → raw native file writes, then name operation
```

N7 is at main-bundle character 1,317,596; the direct setter at 1,207,434;
K0 sample implementation at 1,214,734; S8 at 1,272,500; sender at 3,100,242.
Exact offsets/extent/hash are exported, including the larger UTF8 offsets.
No sort/slot renumbering occurs in this chain. Editing/drag operations can change
content; this proof is for the unchanged archive import, not arbitrary later edits.
All actual datasets have all 64 metadata records, even when a member is absent.

**VERIFIED PRESERVED:** array slot i → immutable model slotIndex i → explicit
wire index i → firmware index i. Numeric indices 0..63 fit without truncation.
Repeated/sanitized sample names do not collide between slots because their
decimal prefixes differ; the proof excludes pre-existing foreign duplicate-index
files. No actual native filename or device listing was manufactured.

**VERIFIED original WAV bytes on the transfer path:** ZIP assignment does not call
K0.loadFile. K0.wav and fileData setters simply store the ArrayBuffer. Channels,
sample rate, bit depth, header, payload, trailing bytes and L are not normalized,
resampled, truncated or padded by this route. S8 clones the complete buffer.

**SOURCE-DERIVED separate individual-file path:** K0.loadFile can call
OfflineAudioContext.decodeAudioData for an incompatible individual audio file,
render mono at 48kHz with gain .95, encode Int16 and construct a new WAV. Its
resulting L is `2 * ceil(decoded.duration * 48000)` on successful rendering.
The Tracks ZIP loader does not invoke that path. No audio was decoded/rendered.

K0.byteLength reads little-endian q at byte16, then L at byte(24+q);
sampleLength=L/2. This is the same header-L position used by stock predicate
0x08051B80. All 733 actual headers have q=16 and L at byte40.

The worker groups up to seven bytes into a high-bit mask plus seven low-bit bytes.
ARM 392FC..393C6 restores each original byte. This is reversible transport bit
packing, not a PCM codec. Pure data-only checks use actual archive bytes; no wire
headers or messages are constructed.

**UNRESOLVED execution-environment detail:** 39320 uses SDIV in its remainder
calculation. Encoded tails below eight bytes have a zero denominator. The data
inverse is correct if the routine completes without a divide-by-zero trap;
authentic CCR/exception state was not recovered or simulated here. A real
Synthwave member, `samples/sample_38.wav`, has a two-byte remainder for both
256- and 8192-byte chunking. This caveat qualifies successful full transfer,
not the first-chunk header-L arithmetic. No boot-state assumption is added.

**VERIFIED IDENTICAL L**, when the archive header is transferred successfully.
Complete native-file byte identity additionally requires successful old-entry
replacement and all writes/rename-copy completion. Interrupted/failed deletion
can leave old content/suffixes; checksum skips can reuse another native file.
Neither case is promoted to a verified actual native copy. No native bytes exist
offline to independently compare with the archive.

## Native entry, filename and selection container (C, G)

| ARM evidence | Verified local role |
|---|---|
|39570 TBB; wire type5 →3958A|PCM becomes internal selector4|
|Initialized table20003730, bytes05 05 00 01 02 03 04 00|Internal4 selects category2, capacity64, PCM|
|397C8 begin; object+1C/+1D/+1E/+1F|Content type / pack ID / slot index / mode copied explicitly|
|39828→3CC34|Attempt old-entry deletion before replacement; its success is a separate premise|
|3A2CC; 3A34A→392FC|Decode original data bytes into transfer buffer|
|39AC4→3CBF0; end handler399FE|Write staged decoded bytes, verify transfer/checksum status|
|Worker7→36B1C, PCM branch36BEC..36CC8|Select pack/category, open native entry and raw-write source/count/offset|
|36C06→3676C; 36C7A→367DA→26610|Pack ID selects container; slot selects indexed PCM entry|
|36C94 backend vtable+14; 25D98→19E50|Raw write, no WAV/header converter|
|36CA4..36CAA|Check actual byte count against requested count|
|36CBC→2645E; 3A520→26494|Reindex/update container after transfer|

Addresses in tables omit common ARM prefix `0x080`; DSP addresses always use P:.
Backend vtable `0x0805B150` and initialized backend pointer `0x20003738` are reused
from BACKENDBOUND byte-checked evidence, not guessed dynamic instances.

26610 takes `(container, backend, category, index, flags)`. With flags bit0 set,
an absent native index invokes 3B0B4. It appends format `/%02d%s` at 3B10C and
category suffix `_PCM.wav` at 5C058 to the resolved PCM path. Thus the initial
fallback basename is **`pad2(i) + "_PCM.wav"`**, independent of the archive's
member basename. Existing native entries use their stored names, not fallback.

**VERIFIED later name rule**, for PCM sendEntitySet→Q4 (character1,267,685):

```
u = (sample name, or "PCM" if empty).substring(0,23)
v = sanitize(u) + ".wav"
basename character bytes = (pad2(i) + "_" + sanitize(v)).split("")
                          .map(c => c.charCodeAt(0) & 0x7F)
```

The fallback and rename formulas are distinct. The normal later name is not
universally `NN_<name>_PCM.wav`. These formulas do not invent an observed file.
The installed A1 sanitizer (character1,195,356) removes `/ ? < > \\ : * | "`,
ASCII controls00..1F and80..9F, all-dot names, Windows device names
con/prn/aux/nul/com0..9/lpt0..9 with optional extension, and trailing spaces/dots;
it limits UTF8 length to255. Name truncation is JavaScript UTF16 substring before
sanitization; Q4 subsequently applies seven-bit character conversion. For a PCM
name the total pre-wire string is at most30 UTF16 units including prefix/suffix.
Only the ASCII index prefix is required to prove index retention.

PCM rename handler39D7C's branch39E5E copies the proposed name, extracts its
prefix through **39E96→1F1C0**, and validates the parsed new index through
39EA2→3A47C. Parser accepts two decimal digits then underscore; for0..63 it
returns exactly i. Worker9→36D82 preserves/copies raw file contents between the
resolved source/destination entries: 36F68 sets4096 maximum chunk size,
36F8E invokes raw read+10, 36FAE invokes raw write+14, 36FB4 checks byte counts,
36FDE reindexes. There is no WAV conversion in this name/copy loop.

**VERIFIED container linkage:** UI chooses destinationPackId using a pack-list
modal, then passes it to every push/rename. 3676C normalizes IDFF to the existing
selected ID; FE is rejected. An ordinary ID resolves via1F1A2 and, where needed,
26064 updates the selected container object. Category2 plus numeric slot is then
passed to26610. Firmware therefore does not need a native PCM filename from ZIP.
Pack ID determines the container; i determines its PCM entry. An exact observed
pack directory/path or current selected ID is **UNRESOLVED**. Cloud record ID
and upload destination ID are different namespaces.

## Missing slots and checksum reuse (F)

N7 calls `samples[i].target.resetContent()` if that record's member is absent.
Reset sets binary undefined and name empty. S8 passes no data for that slot;
worker empty branch requests **DELETE opcode8**, carrying pack ID and i.
Already-absent files may be skipped by compareChecksum's invalid-file branch
when the local model has no content. It does not create a zero WAV.

**VERIFIED local delete chain:** command8 TBB39734→39754→39B0E;
39B94→3CC34 queues worker5→36CCC; PCM branch36D6C→26680;
266B2→3B04C invalidates the name/index entry and clears its presence bit;
backend unlink25D32 removes the file; **36D7C→2645E** rebuilds the map.
Already-missing status is accepted. A successful completed deletion therefore
leaves that same index absent. Failures, interrupted sends or foreign duplicate
native entries are not silently assumed away.

**ACTUAL-DATA missing sets:** *New Pack1 indices38..63 (26);
MyPack_01 indices49,50,51,56..61 (9). Under successful unchanged import these
remain absent native indices; loader model retains each missing record's R8=256.

sendEntitySet.compareChecksum can skip a present slot if device CRC32 and name
match. Static code proves the condition, not actual byte equality of the reused
native file. Map reuse is valid when its header/presence match the archive; the
strict exported premise requires identical content rather than assume CRC cannot
collide. No device checksum/name response was fetched or invented.

## Selected identity and concrete maps (H–K)

**VERIFIED historical metadata:** raw existing LevelDB log000007.log contains a
queued `sendPack` event at byte12447: product Circuit Tracks, factory name
`DLR / Sofa Sound`, destination packId23, timestamp1734192810836 (2024).
Sanitized export omits telemetry/user/device identifiers. Event provenance SHA256
`158e58f35c8a11fe166b0eaeebe88aa91fc3d6c9861ec56010191bcdb22688c7`.
The inspected current installed code records sendPack telemetry after its send
task returns, but its version/execution is not proved for that historical event.

This establishes an historical app-level source/target association only. It does
not prove a completed identical native installation now, current playback pack,
or the selected source at49A1C/26610. **Selected-pack identity: UNRESOLVED**, with
historical selection-related evidence; neither NO SELECTION EVIDENCE nor VERIFIED
PACK IDENTITY is an appropriate promotion. Cache residency/mtime are insufficient.

**DATASET-SPECIFIC map reuse proof:** accepted transferred WAVs retain L;
native index i/presence retain archive i/presence under the stated premises.
The per-record A/R8/S/main/padding equations consequently have identical inputs.
`mapped-native-progression.csv` retains every value from the prior768-row map,
adds native slot and transfer/presence scope, and asserts exact row equality.
No archive concatenation, new synthetic WAV, native listing or CPU state is used.

| Actual archive dataset | Native present/absent | A64 under mapped import |
|---|---:|---|
|Shawn Rudiman Circuit Pack|64/0|0x7CA800|
|*New Pack1|38/26|0x998E00|
|Synthwave|64/0|0x81F000|
|BlankFor.ms Circuit Pack|64/0|0x82CA00|
|Ali The Architect Circuit P|64/0|0x832100|
|Post Industrial Punch|64/0|0x7C8300|
|Peak Sample Pack|64/0|0x828B00|
|Team Novation|64/0|0x7F3B00|
|Circuit Factory Pack|64/0|0x6F4F00|
|Shadow Child|64/0|0x6F9200|
|DLR / Sofa Sound|64/0|0x6DCE00|
|MyPack_01|55/9|0xBF4400|

For each mapped dataset, combined main+padding reach is exactly
`[0x57FFFE,A64-2)` in the prior loader model; largest endpoint0xBF43FE.
No main clipping/page wrap, no geometric intersection with X:[95A,960),
X:[9DB,A12), or descriptor+0 EB,F3,FB,103,10B,113,11B,123,12B,133,13B,143,14B,153.
All24,576 prior interval tests stay negative. Every such mapped cell is
**DATASET-SPECIFIC / NORMAL ASSET EXCLUDED**, conditional on identical native
inputs; **actual selected dataset remains UNRESOLVED**. X11 remains
**STATE-DEPENDENT**; no geometric interval is promoted to an actual X/Y write.

## Universal limitation and next mechanism (L–O)

**SOURCE-DERIVED bounded application route:** Tracks d7.MAX_SAMPLES=9,436,800
16-bit samples. The standard sendPack route checks remaining sample time before
and after lazy ZIP loading. H0 computes
`Math.round((9436800-sum(L/2))/48000*100)/100` and rejects if negative.
On well-formed integer sample lengths, rounding tolerates up to240 excess
samples. Conservative aggregate A64 bound is
`0x580000 + 9436800 + 240 + 64*256 = 0xE83F70`, below24-bit wrap.
This is an additional scoped current-app policy, not universal firmware
acceptance. It also does not prove every main path stays below the stricter
E80000 clipping guard; the twelve actual datasets independently do.

Individual J5.loadFile rejects files above9,436,844 total bytes, but ZIP import
bypasses that validator. Other versions/call paths, malformed headers, foreign
native contents, concurrency and interrupted writes remain outside the scoped
policy. Twelve real unchanged datasets do not prove universal normal closure.

| Next-mechanism gate | Answer |
|---|---|
|A. Archive slot i→native index i?|**VERIFIED PRESERVED** for unchanged recovered import route|
|B. Native WAV L equals archive L?|**VERIFIED IDENTICAL** when its header is transferred; actual skipped/native contents unobserved|
|C. Missing slots preserved?|**VERIFIED** absent after successful delete/reindex, or already absent|
|D. Selected-pack identity known?|**NO / UNRESOLVED**; historical DLR→23 association only|
|E. Remove asset family for actual selected dataset?|**NO**; actual selected native input not established|
|F. Remove for all twelve cached datasets?|**Conditional YES / DATASET-SPECIFIC** for completed identical native imports; not evidence of actual installations|
|G. Universal asset-family closure?|**NO**|
|H. Further asset analysis worth continuing?|**NO** without new existing offline selection/native-content evidence|

Stop this branch. Missing applicability evidence is the native source identity
and actual header/presence correspondence at the particular loader invocation,
including checksum-skipped content. More generic length/asset archaeology cannot
establish that state. No hardware/export/download is proposed.

**Single best next step:** address the independent P:0x204B positive-count/record
destination provenance obligation in a separately authorized phase, retaining
the scoped asset exclusions. Other host/cache/space/order and indirect mutators
remain open. Parent1E15 reachability and active-parent replay remain
UNRESOLVED/NO; target bridge is not recomputed. X35F invariant and persistent
RAM availability are not promoted. No P204B analysis or Plaits work was begun.

## Verification, preservation and reproduction

Reusable tools: ct_packlink_extract.py, ct_packlink_metadata.py,
ct_packlink_event.py, ct_packlink_arm.py, ct_packlink_audit.py;
focused verifier `emulator/tests/verify_packlink.py`.
This continuation reused completed installed-code extraction and metadata search;
only targeted ARM decoder windows and final reports/checks were generated.

Historical ARM/metadata hash-manifest writers included their just-opened empty
self file. They are fixed for new exports without overwriting old evidence.
`input-manifest-status.json` explicitly records the preserved historical metadata
self-entry defect; every other member is hash-verified, and the entire original
manifest is itself hashed in the new inputs manifest. Corrected canonical ARM
manifest excludes itself. No defective self-entry is treated as evidence.

Fresh output directories required; scripts refuse existing destinations.

```powershell
$py='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B tools/ct_packlink_arm.py --output-dir builds/phase19c-packlink/new-arm
& $py -B tools/ct_packlink_audit.py --arm-dir builds/phase19c-packlink/new-arm --output-dir builds/phase19c-packlink/new-final
& $py -B tools/ct_packlink_audit.py --arm-dir builds/phase19c-packlink/new-arm --output-dir builds/phase19c-packlink/new-repeat
& $py -B emulator/tests/verify_packlink.py --arm-dir builds/phase19c-packlink/new-arm --first builds/phase19c-packlink/new-final --repeat builds/phase19c-packlink/new-repeat --output-dir builds/phase19c-packlink/new-checks --verify-original-sources
```

The decoder uses existing small local Capstone; approved read-only access may
be needed on this host. Original-source preservation checks similarly read only
the already identified Components sources/archives; no new search/extraction is
needed. Snapshot-only checks omit `--verify-original-sources`.
Canonical test counts and hashes are in `checks-v2/reproducibility.json`.

**TESTED / PASS:**12 canonical files repeat byte-identically;17 source excerpts
match both character and UTF8 offsets;733 actual WAVs/68,013,066 raw bytes pass
pure reversible encoding checks (266,055 chunks at256 bytes and8,677 at8192).
35 actual missing slots and all768 reused numerical map rows checked. Thirteen
small-tail cases retain the explicit CPU-state caveat (12 at256, one at8192).
No tail test executes ARM or assumes a trapping-state value. Three existing-path
overwrite refusals pass.21 identified existing user sources retain SHA256/size/
mtime; original SYX/BIN match expected hashes and in-memory decode/roundtrip;
all10 DSP stream/payload extracts, sealed19A core/harness and prior FULLHELPER
source manifests pass. No CPU, app or wire-message execution/generation occurred.
