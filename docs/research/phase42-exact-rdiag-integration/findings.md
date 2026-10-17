> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase42 — exact SC35D8 fixed-NOR integration

**PROVEN — offline qualification PASS.** The internal candidate implements a persistent one-shot transaction latch; queued input cannot restart a capture after return. The exact-image native replay passes the requested A–O cases. Its complete-image selected updater/install replay preserves both evidence regions. No hardware was accessed, no SYX was generated, and no reference or pinned source was modified. This is qualification for the next **offline candidate-SYX generation and independent validation** phase, not hardware validation.

## Exact base and candidate

**PROVEN:** the already-closed SC35D8 reproduction was reused without rerunning its builder. Base official firmware is Circuit Tracks 4486 / 1.2.1. The pinned builder is `source/tools/build_sc35d8.py:extra`, based on its `linein3.main` builder order. Reproduction (local-only reference: `builds/phase42-exact-rdiag-integration/reproduction.json`; not distributed) and 439 input pins (local-only reference: `builds/phase42-exact-rdiag-integration/inputs.json`; not distributed) record the exact sources, tool versions and manifest. Reference hardware results are reported in `C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\docs\NOTAS.md:1424` (2026-10-09); they were not repeated. `source/firmware/sc35d8/PRUEBA.md` describes the build and its original test procedure.

| Artifact | Size | CRC-32/MPEG-2 | SHA-256 |

|---|---:|---|---|

| Reproduced SC35D8 | `$5BC8C` / 375948 | `$73BA1238` | `1525c6662bbff9ced7e6055bb54e864615c30013f1b4dec4be6c404f8c750c05` |

| Internal integrated BIN | `$5BC8C` / 375948 | `$AC9987BA` | `9b29180ff7f88c9c982c60abdfd5e5b296e8f2240ad57580366a5a7f797930a6` |

**UNKNOWN:** authenticated reference Git commit and historical `rdiag.py` commit. This archive has no `.git/HEAD`. Current `rdiag.py` is pinned by SHA-256 `1c5c880d664ad29390497a63c934c59a8eecaea9b76064a6be020603f5f5d3b4` and Git blob SHA-1 `6c66a6dbd1c1cd5c9748b611b8dd416be5d9f3d6`; exact base-image reproduction closes the artifact gate independently of the missing commit.

## Persistent ownership record

**PROVEN in native fixtures:** [integrate.py](<../../../builds/phase42-exact-rdiag-integration/integrate.py>), `gst`, `entry`, `watch`, `factories`, reserve **12 bytes at `$20044D70–$20044D7B`** by extending the existing SC14/Master-FX heap-top reservation downward. This is an explicit new reservation, not a claim that arbitrary unused RAM is safe. It neither allocates a heap object nor borrows parser, DMA, stack, LED or transient boot storage. It lives for the application runtime until reset/reinitialization of the application memory system. There is no diagnostic rearm/reset command.

| Offset | Meaning |

|---|---|

| 0–3 | Magic `$4E4F5234` |

| 4 | IDLE=0, ACTIVE=1, SUCCESS=2, FAILED_QUARANTINED=3 |

| 5 | Accepted session/token |

| 6 | Global data-read index: 0 = identity region, 1–8 = target chunks 0–7; region is derived |

| 7 | Read ownership=1, reply ownership=2, quiescent/free=0 |

| 8–11 | Accepted start tick; unsigned timeout subtraction |

**PROVEN:** heap limit `$20002B44` changes from the reference reservation `$20044D7C` to `$20044D70`; heap cursor is at `$20002B48`. The running-RAM fixture cursor `$20044D68` leaves 8 bytes of headroom. Retained Master-FX storage `$20044D7C–$20044E57` remains 220 bytes at its original address. First-use initialization produces the exact same 220 bytes and preserves supported callee registers/SP as SC35D8. Reinitializing Master FX preserves a terminal diagnostic latch. Reservation tests accept cursor exactly `$20044D70`; higher cursors fail closed without changing state or the heap limit. Native results (local-only reference: `builds/phase42-exact-rdiag-integration/native-results.json`; not distributed), MFX control (local-only reference: `builds/phase42-exact-rdiag-integration/masterfx-init-results.json`; not distributed).

**UNKNOWN:** actual heap headroom on a newly booted unit. If the reservation cannot be made, the patched shared getter returns disabled rather than overlapping existing allocations; this can also disable dependent Master-FX behavior. The hardware fixture does not prove this case absent on a real unit. No larger RAM ownership claim is made.

## Admission, RX and parser lifetime

**PROVEN:** USB port 0 alone accepts exactly the padded 232-byte `F0 7D 43 54 0D token 00…00 F7` request. Addresses and lengths are fixed in code: identity `$81000`, 23 bytes, then `$82000 + 64*k`, eight 64-byte reads. No arbitrary-address or remote mutation command remains exposed by the diagnostic filter. Unrelated stock functionality, including its own update/storage operations, still exists.

**PROVEN:** admission saves PRIMASK, masks interrupts, checks IDLE, stores ACTIVE/session/start tick, then restores PRIMASK before entering the command. Every later valid fixed-NOR command is silently rejected in ACTIVE, SUCCESS or FAILED_QUARANTINED. All other rdiag commands are rejected. No rejected request resets the timer or mutates the transaction record. The read loop checks ACTIVE before each read and again after a read returns. SUCCESS requires successful final drain and still-ACTIVE state.

**PROVEN in the coupled replay:** [rx_probe.py](<../../../builds/phase42-exact-rdiag-integration/rx_probe.py>), [coupled.py](<../../../builds/phase42-exact-rdiag-integration/coupled.py>), and [replay.py](<../../../builds/phase42-exact-rdiag-integration/replay.py>) execute native ring enqueue `$08022190`, Main input service `$08020EA0`, parser `$08035C58` through call `$08020F62`, fanout `$0801C894` through call `$08020F82`, and callback `$0801EB30`. Fixture addresses:

- USB interface `$20005824`; RX ring `$20006A98`; ring data `$20006AA4`; capacity 1057 bytes.

- Parser `$20009FF4`; request allocation `$2000A050`, capacity 360 bytes.

- Lent raw window `$2000A070–$2000A0AF`, 64 bytes, inside the explicitly padded request.

The RX ring stores a two-byte length before each USB event packet. An earlier raw-event fixture omitted those lengths; it was corrected before accepting coupled results. Native enqueue during suspended Main changes neither parser/raw bytes, the persistent record, nor Storage request metadata. Main later consumes pending messages through the actual parser/fanout; serial dispatch therefore **delays**, rather than discards, duplicates. The persistent latch supplies rejection after return.

**PROVEN:** before the first handler returns, all 232 original request bytes have been restored for later stock callbacks. After return, adversarial overwrite of all 232 parser bytes leaves the transaction record unchanged; a newly parsed session is still rejected. The record retains only token/index/ownership/timing, not host payload. Natural queued duplicates and a supplemental direct reentry attack at the first command instruction both produce no second capture. Foreign SysEx preserves the original prologue/continuation at `$0801EB34`; a bounded foreign-message case also runs through the coupled Main service.

**UNKNOWN:** complete USB-controller ISR and architectural RTOS exception scheduling. Arrival is injected at native ring enqueue, not fabricated parser dispatch. The fixture runs Main/Storage and native IRQ routines with explicit modeled scheduling/peripheral completion; it does not claim exhaustive arbitrary stock SysEx behavior or all possible concurrent writers. A broad Unicorn read observer caused a valid Thumb IT sequence to fail; raw-read observation was restricted to the owned 64-byte window. Physical SRAM boundaries remain unmapped beyond `$2004FFFF`; write guards and native execution checks remain enabled.

## TX lifetime and failure policy

**PROVEN:** raw bytes are encoded into the Main reply buffer `$200081A8` in the coupled fixture. Native router `$08020C90` calls memcpy `$0801AA14` at `$08020D50`, synchronously copying each encoded reply to `$20009BAC`. Observed lengths are 80 bytes for identity, eight replies of 162 bytes and a 42-byte completion. Native MIDI/USB processing then uses a separate IN source `$20009B04`, with transfers no larger than 64 bytes. [Ownership tests](<../../../builds/phase42-exact-rdiag-integration/test_ownership.py>), ownership results (local-only reference: `builds/phase42-exact-rdiag-integration/ownership-results.json`; not distributed).

**PROVEN in delayed-completion tests:** the IN source is independent of parser and Main stack and remains byte-exact until completion. CPU writes into the pending source are rejected by instrumentation. The router does not retain the diagnostic caller's stack pointer. USB completion is asynchronous. The implementation conservatively waits for native output queue empty, stream-not-busy and IN semaphore release before starting another NOR read. Each backend read asserts that the prior transfer is fully released; every active-request admission asserts no concurrent read.

**PROVEN:** the SysTick wrapper preserves the original helper `$080599B8`. At elapsed 5000 native counter ticks it only latches FAILED_QUARANTINED. It does not cancel Storage, release the backend semaphore, restore a live DMA buffer or issue cleanup/retry commands. The original helper increments the counter before the deadline check: pre-entry elapsed 4998 remains ACTIVE; 4999 reaches 5000 and quarantines. Unsigned rollover passes. Lost Storage completion leaves read owner=1; lost IN completion leaves reply owner=2 and Main's live frame retained. Late normal completion cannot promote FAILED to SUCCESS or initiate another read.

**STRONG INFERENCE:** 5000 intended millisecond ticks corresponds to about five seconds under the stock clock configuration. **UNKNOWN:** physical timing and USB completion behavior. The independent host deadline is **PROVEN** at 5.0 seconds in its controllable-clock tests. Device quarantine is containment, not recovery: **H4 remains FAIL for in-session Storage recovery**. A full power cycle remains required after failure.

## Regression evidence

**PROVEN:** [test_native.py](<../../../builds/phase42-exact-rdiag-integration/test_native.py>) records 25 native cases, [test_ownership.py](<../../../builds/phase42-exact-rdiag-integration/test_ownership.py>) eight supplemental cases, [test_filters.py](<../../../builds/phase42-exact-rdiag-integration/test_filters.py>) ten cases, and the native MFX initialization control passes. These are 44 case/control records, including variants, not 44 independent hardware tests.

| Required case | Offline result |

|---|---|

| A normal | Nine reads, ten replies; exact 535 bytes, packet/whole CRCs |

| B duplicate immediately after acceptance | Queued duplicate and paused direct reentry; zero additional requests |

| C duplicate after handler return | Native parser/fanout runs again; terminal latch unchanged |

| D parser overwrite after return | All 232 bytes overwritten; no state/read changes |

| E–H duplicate during identity / target chunks 0, 4, 7 | Native RX enqueue preserves live request/raw data; later dispatch rejected |

| I other rdiag while ACTIVE | Retired command 6 rejected |

| J unrelated stock SysEx while ACTIVE | Queued, then processed on original route; capture unchanged |

| K TX backpressure | Delayed completions; no premature reuse |

| L disconnect | After replies and during pending IN; no next read |

| M Storage timeout/error | TEF and missing completion at identity and target chunks 0, 4, 7; quarantine without forced unwind |

| N command after SUCCESS | Same and new session IDs rejected |

| O command after FAILED_QUARANTINED | Direct attack rejected while blocked; queued command rejected after late completion/return |

**PROVEN:** additional coverage includes malformed SysEx while ACTIVE, retired read/write commands, short/unterminated requests, forced preemption after notify, PRIMASK preservation, heap boundary refusal, Master-FX reinitialization, final-TX quarantine, lost IN completion and timer rollover. Instrumented diagnostic paths enter no NOR write/erase or content-mutator routines and perform no CPU flash writes.

**PROVEN:** host tests retain 17 stream cases and two publication-failure cases; three native-output end-to-end cases and four Link-adapter containment cases also pass. [host.py](<../../../builds/phase42-exact-rdiag-integration/host.py>) adds framing over the injected reference `Link.send/q/_readd` interface without opening a Link or MIDI port. `_readd` returns host input buffers only. Pure pinned `ctremote.build/parse` helpers match command framing. The same Link cannot construct a fresh diagnostic transport, and the same lease cannot send another command. No automatic retry or Storage cleanup command exists.

**PROVEN:** complete native USB output, fragmented into fake host callback byte groups, reconstructs the following files under `synthetic-capture/`. Publication occurs by atomic directory rename only after full validation and the observation deadline. These are **synthetic test data, not device evidence**; byte14 is preserved as `$5F` in this synthetic identity.

| Synthetic file | Bytes | SHA-256 |

|---|---:|---|

| `nor_00081000_00081016.bin` | 23 | `2254f99eb810fab1e48c44d61cf659af96afc67bbeca7c6377a3d15ba7ea4a9a` |

| `nor_00082000_000821ff.bin` | 512 | `9d1e3afdde67e3d552f21ff82455022114708e02361a8b9b8a8890ae1a2ea484` |

Truncation, corrupt CRC/address/session, missing/reordered/duplicate chunks, early/duplicate completion, silence, partial trailing framing and publication errors produce no newly accepted evidence. Existing output is refused before sending. End-to-end results (local-only reference: `builds/phase42-exact-rdiag-integration/end-to-end-results.json`; not distributed), host negatives (local-only reference: `builds/phase42-exact-rdiag-integration/test-results.json`; not distributed), publication (local-only reference: `builds/phase42-exact-rdiag-integration/publication-results.json`; not distributed), adapter containment (local-only reference: `builds/phase42-exact-rdiag-integration/host-adapter-results.json`; not distributed).

## Exact patch and resource map

**PROVEN:** integration.json (local-only reference: `builds/phase42-exact-rdiag-integration/integration.json`; not distributed) records component sizes/hashes and exact hook bytes. patch-map.json (local-only reference: `builds/phase42-exact-rdiag-integration/patch-map.json`; not distributed) lists every actual changed-byte run, end exclusive: **1450 changed bytes**, confined to the following replaced regions. Image growth is zero.

| Replaced application region | Purpose |

|---|---|

| `$080101E8–$080101ED` | Marker `N42ONE` |

| `$0801EB30–$0801EB33` | Incoming diagnostic filter branch |

| `$080213AA–$080213AD` | Retire diagnostic tick; restore `persist19:c_dtick19=$0806B3C6` |

| `$0805998E–$08059991` | Existing SysTick BL → watchdog wrapper; vector unchanged |

| `$0805AC9C–$0805AC9F` | Retire writeback pads; restore `srcview:c_xpad=$0806B589` |

| `$0805DBCC–$0805DBCF` | SC14 getter → reservation wrapper |

| `$0806B6CC–$0806BC8B` | Replace old probe35s/rdiag ARM pool |

| New pool component | Start | Bytes |

|---|---|---:|

| Reservation wrapper | `$0806B6CC` | 124 |

| Timeout wrapper | `$0806B748` | 80 |

| Admission filter | `$0806B798` | 184 |

| Fixed read/encode/send | `$0806B850` | 544 |

| Incremental CRC | `$0806BA70` | 40 |

| Output drain | `$0806BA98` | 82 |

| Nibble32 / byte encoder / packet CRC | `$0806BAEC` / `$0806BAFC` / `$0806BB18` | 16 / 26 / 46 |

| Immutable request template | `$0806BB48` | 232 |

**PROVEN:** replacement executable code = 1142 bytes; constants = 232; alignment = 6; used pool = 1380 of 1472 bytes; remaining FF slack = 92. This is replacement code inside retired diagnostics, not a 1142-byte increase in application length. New persistent RAM and heap-capacity reduction = 12 bytes; new heap allocation calls = 0. No 512-byte device allocation is introduced.

**PROVEN:** local command frame remains 188 bytes plus 20 saved command bytes and 32 entry bytes (240 bytes beneath callback entry before nested calls). Coupled normal Main SP minimum is `$200080FC`, Main stack usage 604 bytes against the fixture's upper guard; supported `r4–r11` and SP are preserved. Storage minimum `$20009174`, usage 204 bytes. Enqueue fixture IRQ minimum `$2004FEDC` includes its deliberately chosen 256-byte initial stack gap; it is not a physical maximum ISR-depth claim. The 80-byte Main difference from phase41's direct-callback fixture comes from executing the Main service and fanout frames. **UNKNOWN:** workload-equivalent maximum-stack delta against original SC35D8 rdiag and all real exception nesting.

**PROVEN:** vector table, embedded DSP payloads and all bytes outside the declared ARM/marker changes remain identical to the reproduced base. DSP changes=0, bootloader changes=0, option-byte changes=0. The internal candidate is application-only, below `$08080000`. The selected installer actually erases four effective application sectors and programs 93992 padded words, leaving the bootloader byte-exact.

## Dormancy and installation preservation

**PROVEN structural dormancy:** the only command BL is `$0806B838`, following exact request validation and atomic IDLE admission. The conservative external wide-branch scan finds only the dispatcher, SysTick and getter hooks into the replacement pool; no external literal pointers remain into the retired pool. Previous retained code ends with `POP … PC` at `$0806B6CA`. Watchdog/getter contain no Storage submission path. Native unreserved, IDLE and bad-magic SysTick controls match the base's nonstack writes, supported registers and SP. No automatic capture is added. [Audit](<../../../builds/phase42-exact-rdiag-integration/audit.py>), audit results (local-only reference: `builds/phase42-exact-rdiag-integration/audit-results.json`; not distributed).

**STRONG INFERENCE:** unchanged startup plus the guarded entry structure keeps the diagnostic dormant during ordinary boot/UI startup. **UNKNOWN:** complete cold-boot peripheral/scheduler equivalence and universal indirect reachability. These were not broadened or emulated in this phase; the native diagnostic path is run from the authenticated running-RAM fixture.

**PROVEN in the exact-image selected update model:** [install.py](<../../../builds/phase42-exact-rdiag-integration/install.py>) replays all 11749 padded 32-byte blocks of **this candidate**, including native ARM block decoding, native NOR address construction, page programming, sector erase logic, metadata, boot validation and native installer loops. It records every external WRITE/ERASE in that model. Staging uses 92 sector erases below `$5C000`, plus metadata sector `$80000–$80FFF`; 11750 writes include the 23-byte metadata record `$80000–$80016`. Both synthetic evidence sentinels survive byte-exact; installed application bytes match the candidate hash.

| Evidence interval | Direct writes | Erase overlaps | Closest WRITE gap | Closest ERASE gap |

|---|---:|---:|---:|---:|

| `$81000–$81016` | 0 | 0 | 4073 bytes | 0 bytes, adjacent |

| `$82000–$821FF` | 0 | 0 | 8169 bytes | 4096 bytes |

Gaps measure the space between half-open boundaries: an erase ending at `$81000` is adjacent to, and does not overlap, the first evidence region. Full operation lists and boundary conventions are in installation.json (local-only reference: `builds/phase42-exact-rdiag-integration/installation.json`; not distributed).

**UNKNOWN beyond that model:** application update-message/RTOS scheduling is replaced by the selected staging schedule; boot storage interfaces, peripheral completion and internal-flash primitives are modeled; full boot constructors/background/SD/recovery execution is not replayed. This is not a full cold-boot write census. In particular, the unchanged identity setter can erase `$81000–$81FFF` if invoked; this phase does not prove it absent in every possible boot/maintenance circumstance. No original NOR values are inferred from sentinel preservation.

## Recovery, preserved evidence and decision

**PROVEN:** audit-results.json (local-only reference: `builds/phase42-exact-rdiag-integration/audit-results.json`; not distributed) verifies all 451 previously pinned reference files, 183 pinned Plaits sources, 439 phase42 source inputs and all evidence covered by 15 available prior-phase validation manifests remain unchanged. Phase40 and broad cold boot were not continued. Official rollback artifacts remain present and hash-exact: BIN `b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da`; existing SYX `bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd`. No new SYX was produced. Recovery-button/bootloader code is unchanged. **UNKNOWN:** physical recovery on the unit, actual captured NOR bytes, fresh-boot heap headroom, real DMA/USB timing, and complete first-boot target preservation.

**PROVEN — decision:** the bounded exact-integration gates pass: persistent admission, parser independence, native RX/TX ownership, adversarial containment, exact patch confinement, synthetic host reconstruction and zero overlaps for this exact candidate in the requested updater/install model. H4 is still FAIL; a timeout requires power cycling, never a retry or forced release. No claim of completed hardware qualification or absolute recovery safety follows from this offline PASS.

**STRONG INFERENCE — next and only next phase:** generate and independently validate a hardware-test candidate SYX from the pinned integrated BIN. Do not transmit it. No generation or transmission is performed in phase42.

EXACT RDIAG NOR INTEGRATION = PASS
