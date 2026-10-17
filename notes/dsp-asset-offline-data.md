> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 19C-ASSETDATA — existing offline packs and actual-data address maps

## PACKLINK applicability update — 2026-10-06

**VERIFIED / SOURCE-DERIVED NORMAL-PATH:** installed Components1.72.1 Tracks ZIP
loader preserves archive slot i as native PCM index i; direct fileData/binary
assignment and raw transfer/write preserve the archive WAV header L. Successful
missing-member deletion leaves the same native index absent. The native basename
is initially the firmware fallback `pad2(i)+_PCM.wav`; later sample renaming
retains the same prefix and uses the sanitized sample name. These are formulas,
not invented observed filenames. See [PACKLINK](<dsp-pack-native-link.md>).

The unchanged12-dataset/768-record A/S/main/padding map can therefore be reused
for **completed identical native imports**, with successful presence updates,
no foreign duplicate indices/edits and identical content in checksum-skipped
slots. Every mapped requested cell is **DATASET-SPECIFIC NORMAL ASSET EXCLUDED**.
Actual native installations/selected loader source are **UNRESOLVED**; the sole
historical event associates DLR / Sofa Sound with destination23, not current
selection. Source byte geometry is not promoted to an actual X/Y write.

Supersedes the correspondence gap and suggested next step in the historical
ASSETDATA report below. It does not alter any immutable ASSETDATA CSV/evidence.
Selected-dataset closure:NO; conditional known-cache exclusion:YES;
universal closure:NO. X11 stays STATE-DEPENDENT, parent replay:NO, target bridge
unchanged. Stop further asset archaeology without new existing offline native/
selection evidence; next independent obligation is P:0x204B, not analyzed here.
Canonical update: builds/phase19c-packlink/final-v2/ and checks-v2/.

## Historical ASSETDATA findings (retained)

2026-10-06. **VERIFIED / ACTUAL-DATA:** twelve existing Components cache ZIPs
identify themselves as Circuit Tracks packs. Their733 existing WAVs all pass the
stock predicate and contain their declared data regions. Each archive has a
64-element sample map. **DATASET-SPECIFIC / GEOMETRIC:** all twelve separately
computed loader models exclude every requested target; no main clipping or
padding/24-bit wrap. **UNRESOLVED:** which pack applies to the selected native
source and how archive slots/files map to that source without transformation.

X11 remains **STATE-DEPENDENT**. No geometric result is promoted to an actual
X/Y write. The all-normal host-mutation family remains open; parent replay stays
closed. No broad firmware investigation followed the data search.

Strictly read-only local discovery plus offline analysis: no devices, app launches,
hardware exports, network/downloads, MIDI/SysEx, flashing, original/ edits, user
file writes, audio sample decoding, invented PCM/metadata, firmware patching or
Plaits. Copies of real ZIP bytes are confined to project evidence. No DSP/ARM CPU
instructions executed. User source content/size/mtime preservation was checked.

Canonical outputs: `builds/phase19c-assetdata/final/`, `final-repeat/`, `checks/`.
Canonical discovery: `discovery-v2/`; archives retained in `discovery/archives/`.
The first discovery was superseded to explicitly include standalone NCS/NCM and
`*_PCM.wav` hints. The second reuses the same hashed ZIP snapshots, without
duplicating or overwriting user files. All earlier exports remain present.

## A–B. Search scope, provenance and applicability

The metadata-first search covered these explicit roots:

| Root | Regular files visited | ZIPs inspected |
|---|---:|---:|
|C:\Proj SSD\CODEX\CIRCUIT|14,849|7|
|C:\Users\rober\Documents|14,295|2|
|C:\Users\rober\Downloads|479|2|
|C:\Users\rober\Desktop|302|0|
|C:\Users\rober\AppData\Roaming\Components|637|12|
|C:\Users\rober\AppData\Local\Components|159|1|

30,721 file metadata entries,24 ZIPs, zero canonical scan errors. No unrestricted
disk crawl. Reparse/cloud placeholder entries, git/node_modules/venv and generated
phase19c-assetdata outputs were skipped. Non-ZIP archives remained metadata-only;
opaque installed ASAR/browser databases were not decoded. This is a bounded
search, not proof that no other asset copies exist anywhere on the computer.
No standalone native `*_PCM.wav`, `.ncs` or `.ncm` clue files were found in this
coverage. Initial sandbox denial for Components folders was resolved through
approved read-only access; no ACLs or permissions were changed.

All verified pack sources are in:

`C:\Users\rober\AppData\Roaming\Components\Cache\Cache_Data\`

Identification uses actual ZIP index metadata `product="circuit-tracks"`,
version2.0,64 sample entries and actual members, not the opaque `f_*` filenames.
The current device/session selection cannot be inferred from their mere presence
or mtime. Cache firmware SYX files and filename-only JSON hints are catalogued
separately, not classified as sample datasets.

| Actual pack name (index.json) | Cache source | Present samples | Total actual L bytes | Derived A64 | Archive SHA256 prefix |
|---|---|---:|---:|---|---|
|Shawn Rudiman Circuit Pack|f_00008c|64|4,787,544|0x7CA800|fae30b90741bfaeb|
|*New Pack1|f_000133|38|8,568,382|0x998E00|b8f90f282c564235|
|Synthwave|f_000185|64|5,479,454|0x81F000|fbb3dd399ef71edb|
|BlankFor.ms Circuit Pack|f_000186|64|5,591,186|0x82CA00|624d1ffd2036b5f2|
|Ali The Architect Circuit P|f_000197|64|5,637,914|0x832100|ec6212cb026518bd|
|Post Industrial Punch|f_000198|64|4,770,114|0x7C8300|7b9e00951c76f2aa|
|Peak Sample Pack|f_000199|64|5,559,758|0x828B00|4d4466ad6c6b7e0f|
|Team Novation|f_00019a|64|5,123,710|0x7F3B00|baf12dff59da614f|
|Circuit Factory Pack|f_00019b|64|3,034,412|0x6F4F00|19f1dfc2499b5eac|
|Shadow Child|f_00019c|64|3,072,936|0x6F9200|20805a2892a5cc46|
|DLR / Sofa Sound|f_00019d|64|2,841,988|0x6DCE00|586b4fdb0d03ec1a|
|MyPack_01|f_0001d1|55|13,513,416|0xBF4400|930387785cd24072|

Full source paths, sizes, SHA256s and source mtimes: `local-candidates.csv` and
`discovery-v2/snapshots.json`. Full member paths (`archive::member`), sizes,
hashes, ZIP times/listing order and duplicate counts: `dataset-manifest.csv`,
1601 file-member rows. Original archive snapshots total52,223,108 bytes. ZIP
members are streamed through SHA256 and CRC validation; no samples are decoded.
Only existing index.json bytes are exported as metadata evidence.

Each archive is analyzed independently. No length sum or slot sequence is formed
by concatenating packs. Names containing “Factory” or an artist do not prove the
pack represents every normal project or that it was selected in the investigation.

## C. Real archive slot/presence maps and native qualification

**VERIFIED archive mapping:** every index has64 entries; at each array positioni,
`samples[i].url == samples/sample_i.wav`. Every present WAV is unique and occurs
once in the archive. No duplicate members/slot URL aliases were found. Archive
central-directory listing order is exported; it is not treated as device
filesystem enumeration order.

Ten archives contain all sample slots0..63. Actual absent archive slots:

- **`*New Pack1`:**38..63 (26 slots).
- **`MyPack_01`:**49,50,51,56,57,58,59,60,61 (9 slots).

For all35 absent slots, index metadata also has an empty sample name. These are
archive-level empty positions, not fabricated zero WAV files. Their L remains
blank; the model uses missing-record R8=256 as requested. No nonempty sample
metadata points to an absent member, and no slot is filled from another pack.

**UNRESOLVED native mapping:** actual archive basenames `sample_i.wav` returnFF
under the firmware's decimal-prefix/underscore parser1F1C0. They are **not**
native indexed `nn_...` filenames, so their indices are not forced through that
parser. The64-slot archive association is evidenced by index.json. No native
PCM directory, device presence map, importer conversion or selection link is
invented. `record-map.csv` explicitly exports native_filename_index=255 and
labels its archive-model scope on every row.

Some archives include genuine `projects/project_i.ncs` members: counts4,8,12,
16,32 or64; others have none. Index entries for unused project slots can reference
absent members. This is associated archive metadata, not a recovered selected
`_SESSION.ncs`/`_META.ncm` native directory. The archives are clearly Circuit
Tracks pack-format datasets; native selection applicability remains ambiguous.

## D. Actual WAV values and exact stock predicate

**ACTUAL-DATA:**733 WAV headers checked, all:

- RIFF/WAVE/fmt/data signatures at the stock positions;
- fmt size16, data offset44;
- mono,48,000Hz,16-bit; actual PCM format tag1;
- `1640 <= L <= 1,454,496`, within the local19,200,000 maximum;
- file extent contains header, declared RIFF region and declared data region.

Each actual L, complete file size, data offset, header fields and member SHA256
is in `wav-metadata.csv`. All733 are **STOCK-PREDICATE ACCEPTED**, with separate
file-consistency status “VERIFIED complete declared regions.” No rejected,
malformed or header-uncertain file was found among these samples. The stock
predicate itself does not check format tag or file extent; those additional
checks are reported separately, not attributed to firmware.

Headers are read as bytes; full streaming is for provenance/CRC only. Independent
Python wave header interpretation confirms733 mono/48kHz/16-bit parameters and
frame count×2 equals actual L, without decoding sample values.

## E–G. Actual-data progression and padding maps

**DATASET-SPECIFIC derived model:** source lengths and archive associations are
real; application of them to native firmware is conditional on preservation of
archive slot membership and PCM headers/contents. This is arithmetic, not a
CPU replay or observed device address trace. `actual_device_A` is left blank.

For each archive independently:

```
A0=580000
R8_i=256+((L_i&FFFFFE00)>>1) for accepted present source
R8_i=256 for archive-missing source (L blank)
A_(i+1)=u32(A_i+R8_i)
S_i=((A_i&FFFF00)-2)mod2^24
```

All768 rows are resolved **within the archive map**. No main transaction clips
at the strictE80000 guard. Thus N_i=`(L_i&FFFFFE00)>>1` for present samples,
zero for missing; transfer/padding endpoints follow from these exact real values:

`main=[S_i,S_i+N_i)`, `padding=[S_i+N_i,S_i+N_i+256)`.

Since every A is256-aligned and belowE80000, S=A-2; padding ends atA_out-2,
which equals next record's S. Each pack's entire combined main+padding interval
is therefore **exactly `[0x57FFFE,A64-2)`** in this model, including all missing
slots' padding. The largest ends at**0xBF43FE** (`MyPack_01`). No gaps, no main
clipping, no24-bit/page wrap. All critical residues0,100,900,A00 are absent.

`actual-address-progression.csv` exports768 rows with A_in/L/R8/A_out, actual-data
page residues, S, main words/intervals, padding start/256 words/intervals/wrap,
and the explicit archive/native scope. Per-pack A64 values are in the table and
`datasets.json`; the exact per-record page set is retained in CSV.

The bound is also independent of order for any permutation/subset of one pack's
unchanged present samples with at most64 records and no duplicated slots: its
total advance never exceeds the reported A64. This does **not** establish that
an importer preserves headers, forbids duplication or selects that pack.

## H–K. Intersections, space and blocker consequence

**GEOMETRIC / DATASET-SPECIFIC EXCLUDED:** all main and padding intervals for
each archive-model record exclude:

`[95A,960)`, `[9DB,A12)`,
`EB,F3,FB,103,10B,113,11B,123,12B,133,13B,143,14B,153`.

`actual-padding-intersections.csv` includes both main/padding parts:24,576
record×part×target rows, all **NO GEOMETRIC OVERLAP**. No positive case was
discarded on a memory-space assumption. **X11 STATE-DEPENDENT** is retained;
X WRITE PROVEN/Y WRITE PROVEN are never asserted. No geometry-to-X promotion.

**J — blocker for itself:** the length/page/padding concern is removed for each
unchanged archive dataset **under its stated loader-model mapping**. The actual
selected native source is **UNRESOLVED**, so this does not close its host-mutation
obligation or the all-normal asset family. No parent replay is admitted.

**K — not universal:** these twelve existing packs are observations, not the
firmware's acceptance policy for every possible normal import/project. They
do not establish the backend's universal aggregate bound, actual native selection,
all importer transformations, filesystem missing-entry behavior or foreignX11
ordering. Other host cache/order/ancestry, P204B and DSP indirect writes remain
independent and were not revisited. No target-bridge recomputation.

## L–M. Remaining data and single best next step

The former blanket “no offline source assets available” stopping condition is
superseded: twelve real archive datasets were recovered. Remaining missing
applicability evidence is narrower:

1. Which cached pack, if any, corresponds to the selected source at the investigated
   loader invocation. Cache residency/mtime is insufficient.
2. Existing offline native PCM directory/presence/listing and selection metadata,
   **or** documented offline archive-to-native slot/filename/header/content
   preservation sufficient to connect the real archive map to that source.
3. Native listing order only if native names alias; all archive mappings here are
   unambiguous. Actual volume geometry remains needed only for a separate
   universal partition-budget claim.

**Single best next step:** establish the selected-pack identity and archive-to-native
correspondence using existing offline selection/import metadata. Then apply the
already exported concrete map; obtain neither replacements nor hardware exports
automatically. A text clarification about the pack was requested while all twelve
were analyzed independently; no answer was used to invent a selection.

## Reproduction and preservation

```powershell
$py='C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
& $py -B tools/ct_assetdata_discover.py --output-dir builds/phase19c-assetdata/new-discovery --reuse-snapshots builds/phase19c-assetdata/discovery/snapshots.json --root 'C:/Proj SSD/CODEX/CIRCUIT' --root 'C:/Users/rober/Documents' --root 'C:/Users/rober/Downloads' --root 'C:/Users/rober/Desktop' --root 'C:/Users/rober/AppData/Roaming/Components' --root 'C:/Users/rober/AppData/Local/Components'
& $py -B tools/ct_assetdata_analyze.py --discovery-dir builds/phase19c-assetdata/discovery-v2 --output-dir builds/phase19c-assetdata/new-analysis
& $py -B tools/ct_assetdata_analyze.py --discovery-dir builds/phase19c-assetdata/discovery-v2 --output-dir builds/phase19c-assetdata/new-repeat
& $py -B emulator/tests/verify_assetdata.py --discovery-dir builds/phase19c-assetdata/discovery-v2 --first builds/phase19c-assetdata/new-analysis --repeat builds/phase19c-assetdata/new-repeat --output-dir builds/phase19c-assetdata/new-checks --verify-original-sources
```

Original-cache discovery/source checks require approved read-only access on this
host; analysis of snapshots uses project files only. The new-discovery command
is for rechecking search coverage; analysis reproduction intentionally reuses the
fixed canonical snapshot manifest, so it does not depend on a changing live cache.
Fresh output paths required, overwrites refused, symlink/cloud entries skipped.

**VERIFIED checks:**25 recursively counted files repeat byte-identically;
733 independent actual header checks;768 independent instruction-loop arithmetic
checks;24,576 target interval checks; zero clips/wraps/hits; overwrite refusal.
1273 source candidate hashes/sizes/mtimes unchanged, including original cache
archives. Access-time updates caused by normal OS reads are not overridden.
Original firmware hashes/roundtrip, all10 extracts, sealed19A and prior fullhelper
manifests pass. No new CPU execution, firmware patches or user-file modification.
