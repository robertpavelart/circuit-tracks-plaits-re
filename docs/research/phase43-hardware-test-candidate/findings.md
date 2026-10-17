> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: SUPERSEDED / DO NOT FLASH.

# Phase43 — first hardware-test candidate, files only

**PROVEN — offline candidate qualification PASS.** The clean rebuild, deterministic BIN→SYX→BIN→SYX roundtrip, independent file-first validation, final-image native regressions and exact-SYX updater/install replay agree. No MIDI port was opened, uploader launched or firmware transmitted. The package is temporary diagnostic firmware, not production firmware. Hardware action now requires a separate explicit user decision.

## Artifact identity and clean inputs

**PROVEN:** [build_candidate.py:main](<../../../builds/phase43-hardware-test-candidate/build_candidate.py>) decodes the pinned official SYX, compares its BIN with the pinned official BIN, copies/rechecks 439 source inputs into this phase, rebuilds SC35D8 in the established builder order, then reassembles the exact phase42 integration functions. It does not use an intermediate candidate BIN as a build input. All ten reassembled code/template components match phase42 hashes; the final candidate matches the qualified phase42 SHA-256. build-results.json (local-only reference: `builds/phase43-hardware-test-candidate/build-results.json`; not distributed) records full paths and identities.

| Artifact | Bytes | SHA-256 | CRC-32/MPEG-2 |

|---|---:|---|---|

| Existing official input/rollback SYX | raw instruction bytes omitted | `bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd` | decoded BIN below |

| Decoded official 4486 BIN | raw instruction bytes omitted | `b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da` | `$4E74DA9E` |

| Clean rebuilt SC35D8 BIN | raw instruction bytes omitted | `1525c6662bbff9ced7e6055bb54e864615c30013f1b4dec4be6c404f8c750c05` | `$73BA1238` |

| Final diagnostic BIN | raw instruction bytes omitted | `9b29180ff7f88c9c982c60abdfd5e5b296e8f2240ad57580366a5a7f797930a6` | **`$AC9987BA`** |

| **Candidate SYX** | raw instruction bytes omitted | **`59be0e5733c70783c278ff5f89e575d77eef4dd3f6389841eac4a488111df32b`** | declared `$AC9987BA` |

The official source is C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\stock\circuittracks-firmware-4486-STOCK.syx (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/stock/circuittracks-firmware-4486-STOCK.syx`; not distributed). The new deliverables are circuittracks-4486-nor-evidence-test.syx (local-only reference: `builds/phase43-hardware-test-candidate/circuittracks-4486-nor-evidence-test.syx`; not distributed) and its same-named `.bin` in this directory. official-4486-decoded.bin (local-only reference: `builds/phase43-hardware-test-candidate/official-4486-decoded.bin`; not distributed), clean-sc35d8.bin (local-only reference: `builds/phase43-hardware-test-candidate/clean-sc35d8.bin`; not distributed) and independently-decoded.bin (local-only reference: `builds/phase43-hardware-test-candidate/independently-decoded.bin`; not distributed) preserve the intermediate validation products. None is a capture of physical NOR data.

## Fresh-boot heap gate

**PROVEN — FRESH-BOOT HEAP DELTA FROM SC35D8 = 0, meaning allocation demand and allocator calls.** [preflight.py:main](<../../../builds/phase43-hardware-test-candidate/preflight.py>) closes the newly reachable pre-command wrappers' outgoing edges and executes both the base and candidate getter/initializer plus 20 native ticks. No new malloc/bump-allocator call or extra stock startup allocation request is introduced; the allocator cursor is unchanged. New getter branches reach unchanged initializer `$0805DC06`; the watchdog calls unchanged counter helper `$080599B8`; the admission filter's only other new call is the explicitly validated command. Removed pad/tick diagnostics return to pre-existing retained service/UI code.

**PROVEN:** this is **not zero additional RAM footprint**. The latch is a checked fixed 12-byte reservation at `$20044D70–$20044D7B`; available heap capacity decreases by 12 bytes. Existing Master-FX state remains `$20044D7C–$20044E57`. The authenticated running-RAM fixture cursor `$20044D68` leaves 8 bytes before the new limit. Reservation checks cursor ≤ `$20044D70`; otherwise it fails closed. The raw buffer is the previously qualified padded parser window, not another heap allocation. heap-preflight.json (local-only reference: `builds/phase43-hardware-test-candidate/heap-preflight.json`; not distributed) records the full wrapper edges and bounded native traces.

**STRONG INFERENCE:** unchanged startup allocation-producing code has the same allocation demand as hardware-tested SC35D8. **UNKNOWN:** actual fresh-boot heap headroom and timing on this unit. The lack of additional allocation demand does not measure physical headroom, erase the 12-byte capacity cost, or prove complete cold-boot equivalence. Base hardware behavior remains inherited reference evidence.

## Application bounds and complete binary diff

**PROVEN:** application starts `$08010000`, size `$5BC8C` = 375948, end **exclusive** `$0806BC8C`. Maximum accepted size is `$70000` = 458752; remaining headroom is **82804 bytes (`$14374`)**. Native bootloader `$08003B9A–$08003BA6` rejects sizes ≥ `$70001`, independently matching the requested limit. The last installed 32-byte block includes 20 FF bytes, so actual modeled programming ends at `$0806BCA0`.

**PROVEN:** complete-diff-map.json (local-only reference: `builds/phase43-hardware-test-candidate/complete-diff-map.json`; not distributed) enumerates every changed half-open byte range and its classification. No range is unexplained.

| Comparison | Changed bytes | Classification totals |

|---|---:|---|

| Final vs exact SC35D8 | 1450 | 1440 new diagnostic code/hooks; 4 expected literal/routing adjustments; 6 marker |

| Final vs official 4486 | 61896 | 60401 inherited SC35D8; 1483 new diagnostic; 6 expected literal/routing adjustments; 6 marker |

New differences remain confined to marker `$080101E8–$080101ED`, dispatcher `$0801EB30–$0801EB33`, restored service hook `$080213AA–$080213AD`, watchdog BL `$0805998E–$08059991`, restored pad slot `$0805AC9C–$0805AC9F`, reservation getter branch `$0805DBCC–$0805DBCF`, and retired diagnostic pool `$0806B6CC–$0806BC8B`. The pool contains 1142 executable bytes, 232 template bytes, 6 alignment bytes and 92 FF slack bytes. Application length grows by zero relative to SC35D8; build marker is `N42ONE`.

**PROVEN:** vector-table changes from SC35D8=0; DSP payload changes=0. Bootloader bytes and option bytes are outside the application update image. No bootloader/recovery path is patched, and modeled installation preserves its complete `$08000000–$0800FFFF` bytes. See the phase42 patch map plus this phase's independent component hashes and diff map; inherited differences against official firmware are not misclassified as new diagnostic changes.

## Serialization and independent validation

**PROVEN:** the established pinned source/tools/ct_fw.py:encode (local-only reference: `builds/phase43-hardware-test-candidate/source/tools/ct_fw.py`; not distributed) creates the actual SYX. Its decoder returns the exact candidate BIN; re-encoding is byte-identical. [independent_validate.py](<../../../builds/phase43-hardware-test-candidate/independent_validate.py>) starts from the **produced SYX file**, before reading expected images, and imports neither `ct_fw` nor the builder. It uses a bit-list 7-bit block decoder and a bitwise CRC implementation instead of the encoder's integer packing/table CRC.

It independently validates strict vendor framing, product `$64`, protocol `$572`, INIT `$71`, selector-0 HEADER `$7C`, declared size/CRC, **11748 sequential WRITE `$72` packets**, FINISH `$73` carrying block 0, total **11749 data blocks / 11751 messages**, three zero packing-pad bits per block, and the 20 FF image-tail bytes. It verifies SP `$20050000`, Thumb reset vector `$0805C00D`, bounds, SHA-256 and byte equality with both the clean build output and qualified phase42 image. Bad product, corrupt block, missing terminator and trailing garbage are rejected. Results: independent-validation.json (local-only reference: `builds/phase43-hardware-test-candidate/independent-validation.json`; not distributed).

**PROVEN:** file-first Capstone inspection finds actual `$81000`/`$82000` load pairs in the fixed read loop. All reviewed function bytes match their phase42 hashes. [native_regression.py](<../../../builds/phase43-hardware-test-candidate/native_regression.py>) loads these SYX-derived bytes before native initialization and sweeps all 256 command opcodes on both USB and DIN: only opcode 13 on USB enters the command. A nonzero address-supplied payload is rejected. There is no generic raw-address or diagnostic NOR write/erase command. Inherited stock update/storage facilities remain part of the application.

## Exact-SYX updater and internal installation replay

**PROVEN within the stated model:** [install_exact_syx.py](<../../../builds/phase43-hardware-test-candidate/install_exact_syx.py>) reads this exact SYX, feeds every actual packet through native vendor updater `$08024D2C` and its state handlers, and runs the native request queue, dequeue and Storage worker `$08024014`. It executes all native backend program/erase address algorithms and native boot validator/installer loops. The first SYX INIT reaches `$20003800`; HEADER/preparation reaches programming state `$200037F0`; final FINISH/CRC reaches success state `$200037F8`, then commits update metadata before the reset boundary.

The initial fixture incorrectly passed queued write flags directly to the backend, causing repeated erasure and a staging CRC mismatch. The native worker at `$0802409A–$080240B2` proves record flag 1 maps to backend erase-first=0. Executing that worker removes the host assumption. The candidate bytes were not changed. Final replay instruments 11749 native block-unpack calls and 11750 native write-flag conversions, including metadata.

**PROVEN:** external activity includes 11750 writes and 93 erases: 11749 payload blocks plus 23-byte metadata at `$80000–$80016`; 92 payload sectors below `$5C000` plus metadata sector `$80000–$80FFF`. Native application CRC verification also reads its staged image. Both evidence sentinels survive byte-exact.

| Evidence region | Read overlaps | Direct write overlaps | Erase overlaps | Closest WRITE gap | Closest ERASE gap |

|---|---:|---:|---:|---:|---:|

| `$81000–$81016` | 0 | 0 | 0 | 4073 | 0, adjacent |

| `$82000–$821FF` | 0 | 0 | 0 | 8169 | 4096 |

Closest actual write is metadata `$80000,$80017)`; closest erase is `[$80000,$81000)`. Gaps are between half-open boundaries: zero denotes adjacency, not overlap. Full reads/writes/erases, message/state trace and native request records are in [installation.json (local-only reference: `builds/phase43-hardware-test-candidate/installation.json`; not distributed).

**PROVEN:** effective internal erases are sectors 2–5:

- `$08010000,$08018000)`

- `[$08018000,$08020000)`

- `[$08020000,$08040000)`

- `[$08040000,$08080000)`

The native wrapper's additional `$08080000` erase call is a no-op. Exactly 93992 padded words are programmed in `[$08010000,$0806BCA0)`. Final application bytes equal the candidate; no byte in `[$08000000,$08010000)` is erased/programmed.

**UNKNOWN beyond this replay:** task-switch timing, preparatory timer/DSP acknowledgement, progress UI/ACK transport, CRC peripheral, NOR read-data completion, boot storage construction and physical flash primitives are modeled at explicit seams. It is not complete reset-to-USB-ready execution. Full cold-boot preservation remains unknown, including any independent identity-maintenance path; zero read overlaps here does not mean ordinary complete boot never reads identity NOR. Actual NOR values are not inferred from synthetic sentinels.

## Dormancy and final host utility

**PROVEN in bounded final-image replay:** before an explicit request, the initialized latch remains IDLE and unchanged over 20 native ticks; allocator cursor remains unchanged; diagnostic Storage requests, diagnostic `$81000`/`$82000` reads and diagnostic persistent writes are zero. After explicit request, the complete native Main/RX/Storage/TX path again reconstructs exactly 535 synthetic bytes. [native-regression.json (local-only reference: `builds/phase43-hardware-test-candidate/native-regression.json`; not distributed) records all observables. **STRONG INFERENCE:** guarded command entry plus unchanged allocation-producing startup code preserves pre-request dormancy. **UNKNOWN:** full peripheral cold boot and real interrupt timing.

**PROVEN:** [capture_nor_evidence.py](<../../../builds/phase43-hardware-test-candidate/capture_nor_evidence.py>) is standalone except for packaged [ctremote_transport.py](<../../../builds/phase43-hardware-test-candidate/ctremote_transport.py>) and Python's standard library. Only its explicit `capture --out NEW_DIRECTORY` subcommand constructs a Link. The WinMM receive/callback path comes from pinned `ctremote.Link`; generic ask/other-command CLI paths are omitted. Selection requires a unique input/output name match. No uploader is included or launched.

The final tool embeds the qualified receiver and one-shot lease/framing logic. A durable exclusive `NOR-CAPTURE-ATTEMPT.json` is created beside the tool **before** opening ports; another launch, even with a different output path, stops before Link construction. No reset/retry/rearm path is provided. It cannot verify a physical power cycle or prevent somebody deliberately bypassing the package; the device latch separately rejects repeated sessions until reset.

**PROVEN in 25 offline cases:** a full 5.0-second observation window, exact addresses/indices/lengths, packet/whole CRC and single completion are required. Atomic directory publication creates exactly the two requested BIN files, 23 and 512 bytes; stdout prints lengths, SHA-256 and combined status. Any failed transaction publishes no new evidence and sends no retry, second diagnostic request or Storage cleanup. Existing evidence is never replaced. Failure output is:

```text

CAPTURE FAILED

DO NOT RETRY

FULL POWER CYCLE REQUIRED

```

Tests cover TEF represented by missing completion at each relevant boundary, timeout, malformed/checksum/address/sequence failures, duplicates, omissions, reordering, disconnect, output timeout, publication failure, existing output and repeated process-style attempts. [test_capture_tool.py](<../../../builds/phase43-hardware-test-candidate/test_capture_tool.py>) uses fake Links and a controllable clock. Its WinMM tests execute extracted class definitions with **mock functions only**; live transport initialization is never imported/executed.

**PROVEN:** [final_host_roundtrip.py](<../../../builds/phase43-hardware-test-candidate/final_host_roundtrip.py>) also feeds final-SYX native USB bytes through the final standalone tool, verifies atomic publication of exactly 23 and 512 bytes, and removes the temporary synthetic outputs. Result (local-only reference: `builds/phase43-hardware-test-candidate/final-host-roundtrip.json`; not distributed) records one request and SHA-256 `2254f99eb810fab1e48c44d61cf659af96afc67bbeca7c6377a3d15ba7ea4a9a` / `9d1e3afdde67e3d552f21ff82455022114708e02361a8b9b8a8890ae1a2ea484`. These hashes identify synthetic test input, not this device's contents.

**PROVEN software change from reference Link:** send checks preparation/submission/release errors, raises on its two-second output timeout, and retains a pending driver buffer instead of prematurely releasing it. No second `LongMsg` occurs. Those paths are mock-tested; **UNKNOWN:** real WinMM timing/error behavior. The inherited RX path does not make these new error branches hardware-tested. `_readd`/close concern host MIDI resources, not device Storage commands.

## Rollback, remaining unknowns and stop

**PROVEN:** rollback/circuittracks-firmware-4486-STOCK.syx (local-only reference: `builds/phase43-hardware-test-candidate/rollback/circuittracks-firmware-4486-STOCK.syx`; not distributed) is a byte-exact copy of the existing official artifact, independently decoded with CRC `$4E74DA9E`. rollback-validation.json (local-only reference: `builds/phase43-hardware-test-candidate/rollback-validation.json`; not distributed) records source/package identities. Instructions only are in rollback/README.txt (local-only reference: `builds/phase43-hardware-test-candidate/rollback/README.txt`; not distributed) and HARDWARE-TEST-README.txt (local-only reference: `builds/phase43-hardware-test-candidate/HARDWARE-TEST-README.txt`; not distributed): power off → power on holding Scales + Preset + Note → stock bootloader/recovery → send official 4486 through the separately selected existing update workflow. No such action occurred.

**STRONG INFERENCE:** recovery behavior is supported by the reference's bootloader analysis (`LEEME.md:19–26`, `docs/NOTAS.md:38–48`) together with its reported hardware-tested uploader workflow (`docs/NOTAS.md:29–36`). The reports do not constitute a new test of recovering this candidate from a non-booting application. **UNKNOWN:** recovery of THIS candidate on this unit. Bootloader preservation is proven offline; recovery is not guaranteed.

**UNKNOWN, retained explicitly:** physical boot/USB/DMA/WinMM timing, fresh-boot headroom, complete cold-boot NOR preservation, actual original 23+512 bytes and unit-specific recovery. **H4 remains FAIL:** failure cannot safely unwind Storage in-session. One successful capture means stop; any failure means discard, no retry/second request, full power cycle before further action.

**PROVEN:** SHA256SUMS.txt (local-only reference: `builds/phase43-hardware-test-candidate/SHA256SUMS.txt`; not distributed) covers candidate SYX/BIN, capture tool, its transport dependency, user README, rollback artifact and validation/replay tools. Source/pinned-input and prior-phase checks are recorded by validation.json (local-only reference: `builds/phase43-hardware-test-candidate/validation.json`; not distributed). No phase42/reference/pinned artifacts were modified. The hardware README includes the prerequisites, one-command procedure, success/failure stopping policy and planned firmware restoration.

**PROVEN — phase ends here, files only.** Do not flash automatically. Wait for explicit user decision before any hardware action.

HARDWARE-TEST CANDIDATE = PASS
