> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: FAILED / SUPERSEDED / DO NOT FLASH.

# Phase61 final candidate qualification

**PROVEN — FINAL PRE-FLASH HARDWARE-TEST CANDIDATE. NOT YET HARDWARE-TESTED.** Offline qualification is complete for the constructed candidate below. No hardware, MIDI port, firmware transmission or reference-source modification occurred. Work resumed from saved Phase61 results; the binary was not rebuilt during final packaging.

|Artifact|Bytes|SHA-256|

|---|---:|---|

|circuittracks-final-geometry-gated-nor-test.syx| raw instruction bytes omitted |`fe36e18bc83448b0e25cc21b8323e0e64e153f6e04abc042546f4a20e83731d3`|

|circuittracks-final-geometry-gated-nor-test.bin| raw instruction bytes omitted |`af5b62e371c1f9e6972b573e766088e54da6fadfcba911e62f25bd0edb0c763f`|

CRC-32/MPEG-2: **6ECE2ED4**. Application `08010000,08075100)`; exclusive end **08075100**; image headroom **44,800 bytes** to08080000. Protocol product64/version572; distinct compared-header marker **N61GEO**. InitialSP20050000/reset0805C00D are unchanged. No Plaits code is present.

## Integrated behavior

**PROVEN:** all five legacy entries are redirected together:0806B6CC getter preserves MasterFX ABI;0806B748 invokes retained clock update then lifecycle-only timeout;0806B798 dispatches geometry/auth while rejecting old start;0806B850 uses stack-local raw buffering and authorized transport fields;0806BC46 redirects to masked ACTIVE→SUCCESS. Old diagnostic bodies in6B6CC..6BC8C are cleared except explicit redirects, preventing mixed-schema stores. Native helpers and original call-site trampolines are hash-bound in construction.json and independently reviewed full M-class listings.

**PROVEN:** installed constructor initialization plus actual first-mount snapshot at0801AE06 passes the59548-instruction native startup replay under the already-declared Phase59 peripheral completion/RTOS models. The valid compact snapshot is0180003480908F01. The runner now stops at0801AE14 after the installed hook; its reportedR0 at that tail is a reconstructed logging-string pointer, not the mount status. The original stock mount returned0 before the hook. First-mount stride4096 publication is permitted only during that mount; subsequent changes invalidate.

**PROVEN:**28 native boundary cases pass: initialization/constructors, first snapshot, export, invalid binding, remount/binding/stride/earlier registration invalidation, correct/wrong epoch, geometry/session mismatch, malformed/arbitrary payload, unauthenticated raw, duplicates, parser overwrite, both fixed-read modes, chunk0/4/7 read errors and timeouts, native wrapping timeout, disconnect, absorbingFAILED, repeated terminal requests, supported register/APSR/PRIMASK preservation and getter ABI. Native boundary tests explicitly model read completion and USB output; they do not claim physical DMA execution.

**PROVEN:** the coupled Main/parser→Storage worker→QSPI IRQ→USB-ring/completion replay passes with the final bytes for explicit identity+coefficients.9 reads/10 frames are reconstructed exactly; native Main returns, semaphore is free, queue/pending/sync are zero. It records345 guard checks and8 callee-saved register checks; minimumSP Main200080FC/Storage20009174/IRQ2004FFF0, with2460/1068/4076 bytes respectively to lower guards. Coeff-only exact output is separately covered by the native boundary suite. The coupled case uses a prequalified exported-geometry fixture; it is not one uninterrupted electrical reset-to-USB capture.

**PROVEN:**19 deterministic host cases pass, including14 required stream patterns, geometry silence/malformed/CRC cases, explicitly optional identity, and injected second-file IO failure. Timeout is10 seconds per host stage using a monotonic clock model. Failure creates no accepted capture directory, no retry, no second diagnostic request, and no storage cleanup command. Host requests are one geometry request and, only after validation, one authorization request. The two-request workflow is not a retry. Failure reports CAPTURE FAILED / DO NOT RETRY / POWER-CYCLE DEVICE BEFORE ANOTHER ATTEMPT.

## File-first and diff review

**PROVEN:** independent SYX decoder checks product64/protocol572, ordering/framing/nibbles/padding/image bounds and bitwise MPEG-2 CRC, then matches BIN. Four malformed serialized files are rejected. Exact structural reconstruction independently accounts for39469 changed/added bytes against clean pinnedSC35D8: explicit hooks/marker, cleared obsolete diagnostic pool, appended native helpers/trampolines and explicitFF alignment/reserved gaps. [classified-diff.json (local-only reference: `builds/phase61-final-geometry-gated-candidate/classified-diff.json`; not distributed) gives every exact span and category;0 unexplained bytes. Unused appended gaps are requiredFF, not counted as executable code. Existing DSP bytes remain unchanged fromSC35D8; cleanSC35D8's inherited changes versus official4486 remain inherited reference behavior, not Plaits changes.

**PROVEN:** the generated code's only direct calls below appended code are retained clock599B8, fixed read wrapper47C6C, USB route20C90, USB service35A50 and scheduler yield1BE60. Reviewed getter/trampolines have explicit original return/initialization tails. There is no diagnostic NOR write/erase entry or host-address decoding command. Fixed raw address-load pairs are81000 and82000. The full native raw loop and failure tests bind lengths and prevent unauthenticated/second reads. Bootloader/option bytes are outside the app image; exact update replay independently verifies bootloader equality.

## Exact installation and rollback

|Transition|Native result|Silent no-op?|External erase ranges (half-open)|External program ranges|81000 /82000 write-or-erase overlaps|

|---|---|---|---|---|---|

|b13-to-candidate|PASS; exact image installed|No|`[['0x0', '0x66000'], ['0x80000', '0x81000']]`|`[['0x0', '0x65100'], ['0x80000', '0x80017']]`|0 /0|

|candidate-to-official|PASS; exact image installed|No|`[['0x0', '0x4d000'], ['0x80000', '0x81000']]`|`[['0x0', '0x4cde0'], ['0x80000', '0x80017']]`|0 /0|

|candidate-to-b13|PASS; exact image installed|No|`[['0x0', '0x6b000'], ['0x80000', '0x81000']]`|`[['0x0', '0x6a420'], ['0x80000', '0x80017']]`|0 /0|

**PROVEN:** all three saved native replays install their exact incoming image and leave bootloader64KiB byte-identical. N61GEO differs within the38 compared header bytes, so B1.3→candidate is not suppressed by header equality. Both rollbacks also execute actual installation. Candidate staging erases0,66000), programs[0,65100); metadata erases[80000,81000), programs[80000,80017). Metadata erase ends exactly at81000; it does not include it. Both target sentinels remain exact. Internal erases stay within application08010000..08080000; candidate programming ends08075100. These are native address/state-machine replays with modeled flash/NOR completion, not tested physical installation or recovery.

## Remaining status

|Classification|Result / limit|

|---|---|

|PROVEN|No remaining known offline software blocker in the integrated candidate and required saved validation gates; historical Phase43/44 bytes and360 files across6 checked historical manifests are preserved;439 pinned sources remain identical.|

|PROVEN|H4 in-session Storage recovery remains FAIL by design. Any TEF/missing completion/timeout/disconnect/malformed capture requires no retry and full power cycle. No forced semaphore unwind exists or is attempted.|

|STRONG INFERENCE|Under admitted ordinary boot/task/control paths and successfully validated current geometry, no concrete preauthorization82000 corruption path remains. This reuses the completed Phase45–60 producer/mapping/IRQ triage, not merely the new no-write replay. Identity mapping and explicit permission remain separate; no authentic bytes have yet been acquired.|

|HARDWARE-ONLY UNKNOWN|Physical USB/DMA/NOR completion and electrical timing, real device geometry/target contents, physical SRAM/stack behavior, and successful hardware installation/rollback of this exact candidate. User-reported recovery entry/exit is not proof of rollback flashing. Offline replay is not a risk-free guarantee.|

Evidence: [final-validation.json (local-only reference: `builds/phase61-final-geometry-gated-candidate/final-validation.json`; not distributed), file-validation.json (local-only reference: `builds/phase61-final-geometry-gated-candidate/file-validation.json`; not distributed), construction.json (local-only reference: `builds/phase61-final-geometry-gated-candidate/construction.json`; not distributed), native-tests.json (local-only reference: `builds/phase61-final-geometry-gated-candidate/native-tests.json`; not distributed), candidate-startup.json (local-only reference: `builds/phase61-final-geometry-gated-candidate/candidate-startup.json`; not distributed), coupled-tests.json (local-only reference: `builds/phase61-final-geometry-gated-candidate/coupled-tests.json`; not distributed), host-tests.json (local-only reference: `builds/phase61-final-geometry-gated-candidate/host-tests.json`; not distributed), [schema-and-protocol.md](<schema-and-protocol.md>), b13-to-candidate-summary.json (local-only reference: `builds/phase61-final-geometry-gated-candidate/b13-to-candidate-summary.json`; not distributed), candidate-to-official-summary.json (local-only reference: `builds/phase61-final-geometry-gated-candidate/candidate-to-official-summary.json`; not distributed), candidate-to-b13-summary.json (local-only reference: `builds/phase61-final-geometry-gated-candidate/candidate-to-b13-summary.json`; not distributed).

Construction metadata erratum: its historical `name` field says snapshot_return because a loop reused that Python variable. The filenames, all bytes, hashes, CRC and native replay identities are correct; final-validation.json is the authoritative final candidate identity. This packaging fixes no firmware bytes. Earlier truncated .asm checkpoint views are preserved; `reviewed-components-*.asm` and `reviewed-trampolines-*.asm` decode every byte in M-class mode and are the complete review listings.

STOP. Await explicit user decision. No hardware action is authorized by this report.

FINAL HARDWARE-TEST CANDIDATE = PASS
