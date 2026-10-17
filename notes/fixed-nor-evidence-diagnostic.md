# Historical Phase41 diagnostic study - superseded

All candidate identities, qualification banners and next-step instructions below are historical. Later diagnostics supersede them; DO NOT FLASH any image described here. Current authority: [CURRENT_STATUS.md](<../docs/CURRENT_STATUS.md>); exact review identity and tooling locks: [CURRENT_STATUS.md](<../docs/CURRENT_STATUS.md>). Original text follows unchanged.

# Fixed NOR evidence diagnostic — phase41

2026-10-16. **UNKNOWN — overall qualification: UNQUALIFIED.** A working, in-memory ARM prototype captures all535 synthetic bytes through the stock queued NOR path, and the host containment tests pass. The physical DMA/cache questions are substantially resolved by STM32F7 architecture documentation. Complete ownership across incoming USB traffic and queued duplicate dispatch remains UNKNOWN. An exact SC35D8-derived application has not been generated; no hardware-test SYX is released.

**PROVEN:** phase40 symbolic analysis and broad cold-boot emulation were not continued. No hardware/ports were accessed; no reference/pinned sources were changed. The incomplete buffer/concurrency gate in request sections5/9 prevents candidate generation. This is a targeted input-ownership gate, not a demand to emulate every startup peripheral.

Working files: phase41 (local-only reference: `builds/phase41-fixed-nor-diagnostic`; not distributed), qualification data (local-only reference: `builds/phase41-fixed-nor-diagnostic/qualification.json`; not distributed), native and host results (local-only reference: `builds/phase41-fixed-nor-diagnostic/test-results.json`; not distributed), publication tests (local-only reference: `builds/phase41-fixed-nor-diagnostic/publication-results.json`; not distributed).

**1 — Selected reference base and evidence separation**

**HARDWARE-TESTED reference behavior:** SC35D8 is the smallest of the requested diagnostic bases containing the remote rdiag transport. SC35D4/D5 are smaller but lack it. The reference reports successful boot/audio, USB ping, ARM memory reads and a311-request SD download matching the backup. This is a dated reference report, not a new hardware observation. Dated results (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/docs/NOTAS.md:1424`; not distributed).

**PROVEN offline manifest identity:** selected base SC35D8, application size `$5BC8C`, BIN SHA-256 `1525c6662bbff9ced7e6055bb54e864615c30013f1b4dec4be6c404f8c750c05`, SYX SHA-256 `867834b651cb8bd39f34550c8f53971ae3158eca2cc897ee6f2da914cf9ecc50`, image CRC `$73BA1238`. Manifest (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/firmware/sc35d8/manifest.json`; not distributed).

**PROVEN offline scope:** the new adapter is currently exercised in the existing B1.3 running-RAM/native-storage fixture. It is **not** a reconstructed SC35D8 application or its final relocated rdiag extension. Passing this fixture does not establish an exact SC35D8 candidate delta, startup equivalence or new hardware behavior.

**2 — Transport and fixed request**

**PROVEN offline:** one experimental command13 uses the existing `F0 7D 43 54` rdiag envelope, `cmd|$40` replies, a7-bit transaction id, 232-byte padded requests and the stock SysEx output router `$08020C90`. The request contains **no address or length**: bytes6…230 must be zero; the terminator is `$F7`. USB port0 only. There is no second MIDI transport. The framing adapter for future use remains `ctremote.Link` → existing phase27 `WinMMTransport`; no live entry point is supplied here. [Entry](<../builds/phase41-fixed-nor-diagnostic/entry.py>), [fixed codec](<../builds/phase41-fixed-nor-diagnostic/evidence_protocol.py>), reference transport (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/rdiag.py:78`; not distributed).

**PROVEN offline:** the prototype rejects nonzero request payload, a write command and a shortened framed request before NOR submission. Stock identity and Novation messages execute the original dispatcher prologue and reach `$0801EB34` with the supported input registers preserved. The filter is modeled on rdiag's `c_rdin`; its final placement in SC35D8's `c_rdcmd`/dispatcher is still UNKNOWN.

**3 — Minimal NOR adapter and task ownership**

**PROVEN offline:** each read calls existing `$08047C6C(offset,buffer,length)` → NOR wrapper `$08024130` → enqueue `$08023F68` → synchronous wait `$08023FD6`. Storage `$0805767C` runs worker `$08024014`; op1 reaches backend `$08022F94` → DMA reader `$08037430`. The wrapper is obtained through global `$20006968`. Main yields while Storage owns its backend and completion notification. Main does not directly wait for Storage's IRQ. Existing closure (local-only reference: `builds/phase29-storage-wrapper/closure.json`; not distributed), [replay](<../builds/phase41-fixed-nor-diagnostic/replay.py>).

**PROVEN offline:** all nine observed controller commands are read opcode `$EC`; mutation dispatch/backend entries and CPU flash writes are guarded against by the fixture. No SD content operation is called by the new prototype. Stock IRQ and DMA configuration instructions are retained. The scheduler/event seams and opaque DMA data arrival remain explicitly modeled; this is not full physical peripheral execution.

**4 — Exact fixed read schedule**

| Index | Region id | Physical NOR bytes, inclusive | Length |
|---|---|---|---:|
| 0 | 0 | `$81000–$81016` | 23 |
| 1 | 1 | `$82000–$8203F` | 64 |
| 2 | 1 | `$82040–$8207F` | 64 |
| 3 | 1 | `$82080–$820BF` | 64 |
| 4 | 1 | `$820C0–$820FF` | 64 |
| 5 | 1 | `$82100–$8213F` | 64 |
| 6 | 1 | `$82140–$8217F` | 64 |
| 7 | 1 | `$82180–$821BF` | 64 |
| 8 | 1 | `$821C0–$821FF` | 64 |

**PROVEN offline:** the successful transaction executes exactly this list once. The23-byte read bypasses both identity-normalization helpers; no byte14 zero store occurs. Synthetic byte14 is `$5F` and survives in the reconstructed23-byte capture. These are test bytes, **not original device identity bytes**. No authentic NOR content has been acquired. [Emitter](<../builds/phase41-fixed-nor-diagnostic/stream.py>), exact traces (local-only reference: `builds/phase41-fixed-nor-diagnostic/test-results.json`; not distributed).

**5 — Physical buffer proof and remaining ownership boundary**

| Property | Evidence / confidence |
|---|---|
| ARM address / size | **PROVEN in native fixture:** `$2000A070–$2000A0AF`, one64-byte window; identity uses the first23 bytes |
| Owner | **PROVEN in fixture:** stock Main SysEx parser allocation `$2000A050`, capacity360; raw window at +32 |
| Alignment | **PROVEN:**16-byte aligned; configured DMA PSIZE/MSIZE are byte-sized |
| Address admission | **PROVEN code:** entry requires16-byte-aligned input and its entire232-byte request inside `$20000000–$2000FFFF` |
| Lifetime | **PROVEN in bounded replay:** Main retains its frame across all reads and output drains; no asynchronous return while DMA owns data |
| Ownership begins | After complete fixed-request validation; before enqueueing op1 and before DMA M0AR publication |
| Ownership ends | After backend completion/release and the output path's drain; returning exits then restore the original232 request bytes |
| Failure lifetime | **PROVEN tested:** TEF/missing completion leaves Main suspended and the raw window retained; no reuse or forced release |
| Cacheability | **PROVEN architecture:** this is STM32F74/F75 DTCM, not cacheable AXI SRAM |
| DMA accessibility | **PROVEN architecture:** STM32F7 AHBS permits DMA transfers to/from DTCM |
| Concurrent users | Main, Storage, DMA and output transport are exercised; **UNKNOWN:** complete incoming USB RX queue/parser aliasing and deferred duplicate dispatch |

This choice follows the parser's native owner/allocation/use path; it is not an unreferenced hole in a RAM snapshot. The original rdiag raw window was +160; that historical SD success is not silently transferred to this +32 NOR-DMA window. Synthetic emulator addresses `$20060000/$20060100` are not used. Earlier physical allocation proof (local-only reference: `builds/phase30-chunked-storage/ownership-and-error-audit.json`; not distributed).

**UNKNOWN — full buffer gate:** the physical map, DMA reachability and non-cacheability are established, but complete concurrency ownership is not yet qualified. `Model.tick(duplicate=True)` only increments a deferred-input counter; it does not execute the real USB receive queue while Main is blocked, nor consume that pending command after return. It is explicitly UNKNOWN in the results. No device-side replay latch is implemented. A queued duplicate could be dispatched later; it must not be assumed discarded. This is the concrete reason section5 is not declared complete.

**6 — Cortex-M7 cache/DMA coherency**

**PROVEN architecture:** ST AN4667 §1.3.3 describes DMA access to DTCM through AHBS, and table3 maps F74/F75 DTCM at `$20000000–$2000FFFF`. This differs from devices where ordinary DMA cannot reach TCM. [ST AN4667](https://www.st.com/resource/en/application_note/an4667-stm32f7-series-system-architecture-and-performance-stmicroelectronics.pdf).

**PROVEN architecture:** ST AN4839 states TCM is non-cacheable and provides a DMA-destination DTCM example. The raw NOR path uses peripheral-to-memory DMA. The selected DTCM destination needs no D-cache clean/invalidate; adding such operations is unnecessary for this buffer. The runtime domain check prevents accepting an AXI-SRAM request buffer under this proof. [ST AN4839 §2/§3.2](https://www.st.com/resource/en/application_note/an4839-level-1-cache-on-stm32f7-series-and-stm32h7-series-stmicroelectronics.pdf).

**PROVEN offline:** the simulated DMA replaces the previous raw data, and CPU encoding is forbidden before completion. Every newly supplied byte reconstructs exactly. **UNKNOWN hardware:** no actual NOR→DMA→CPU→host transfer on this device has been observed; Unicorn does not model cache behavior or verify electrical transfers. The cache conclusion comes from the documented memory path, not from Unicorn returning matching bytes.

**7 — Response integrity and two-file publication**

**PROVEN offline:** every reply validates command `$4D`, transaction id, region kind, global chunk index, absolute source address, total535, expected23/64-byte length, nibble encoding and packet CRC-32/MPEG-2. Exactly one kind2 completion at index9 carries the CRC over all535 bytes; any later packet fails. The data packet convention extends the existing fixed diagnostic command inside rdiag framing. [Receiver](<../builds/phase41-fixed-nor-diagnostic/evidence_protocol.py>).

**PROVEN offline:** host reconstruction stays in memory through a5.0-second absolute attempt window, including time after completion. Both validated files and a manifest are staged together, fsynced and published by **one directory rename**. There is no progressively written accepted filename and no half-published pair. The destination is a new capture directory containing:

- `nor_00081000_00081016.bin` — exactly23 bytes.
- `nor_00082000_000821ff.bin` — exactly512 bytes.

The deadline is host policy, not a measured firmware timeout. Successful synthetic hashes printed by the test are respectively `2254f99eb810fab1e48c44d61cf659af96afc67bbeca7c6377a3d15ba7ea4a9a` and `9d1e3afdde67e3d552f21ff82455022114708e02361a8b9b8a8890ae1a2ea484`. Test directories are removed afterward; these are not delivered as device evidence. [Host implementation](<../builds/phase41-fixed-nor-diagnostic/host.py>).

**8 — One-shot failure containment**

**PROVEN offline:** the exact phase32 `DeviceLease` implementation is reused. A failed session cannot run again, another capture sharing that lease cannot send, and another lease cannot claim the same transport. Every sent failing-stream test sends exactly one command. No retry, reset, cancel, semaphore-release or storage cleanup command exists in the host implementation. Decoder/partial framing data are discarded, accepted files are absent, and the report is:

```
CAPTURE FAILED
DO NOT RETRY
POWER-CYCLE REQUIRED
```

**PROVEN within the existing fault model:** TEF and missing completion do not return an error packet; they leave Storage blocked. The host therefore sees silence/truncation and fails at its absolute deadline. No invented TEF return status or device unwind is supplied. **UNKNOWN:** a software lease does not attest a physical power cycle or prevent a separate process deliberately bypassing it. Existing H4 remains FAIL for in-session recovery.

**9 — Offline workload and actual coverage**

**PROVEN offline:** the final test run exits0 and records19 native/prototype cases plus17 host stream cases; two further host publication cases exit0.

| Required workload | Result and limit |
|---|---|
| Full successful535-byte transaction | **PROVEN:** nine reads, ten replies, exact samples/CRC/state reconstruction |
| Identity read TEF / missing completion | **PROVEN:** no data reply, retained active request, no following read |
| Target chunks0 /4 /7 TEF / missing completion | **PROVEN:** no later read; ownership remains retained |
| MIDI backpressure | **PROVEN in modeled USB completion schedule:** no raw reuse before prior output drains |
| Host disconnect | **PROVEN bounded replay:** after identity plus four target chunks, no next read; host publishes nothing |
| Duplicate command while active | **UNKNOWN:** Main non-reentry only; real pending USB input and post-return dispatch not executed |
| Malformed command | **PROVEN:** nonzero request body, write command and short framed request rejected before NOR |
| Unterminated request | **UNKNOWN native handler replay:** it does not complete the parser; no completed descriptor was fabricated |
| Foreign stock messages | **PROVEN:** original prologue/continuation, no experimental NOR call |

Normal replay performs345 guard checks and eight supported callee-saved register checks (`r4–r11`); restores SP and the original request; and leaves semaphore1, queue/pending/sync0 and no active chunk. Minimum modeled SP: Main `$2000814C`, Storage `$20009174`, IRQ `$2004FFF0`. No raw CPU store occurs before normal final request restoration. These are bounded fixture observations, not all-interrupt ownership or full architectural scheduler validation.

Host negatives cover silence/truncation at each requested fault boundary, missing/reordered/duplicate chunks, duplicate/early completion, wrong session, bad packet CRC, wrong address with valid CRC, wrong whole CRC and partial trailing framing. Injected rename failure leaves no accepted/staged files; existing evidence is refused before sending. [Tests](<../builds/phase41-fixed-nor-diagnostic/test_offline.py>), [publication failures](<../builds/phase41-fixed-nor-diagnostic/test_publication.py>).

**10 — Exact prototype size and candidate minimization boundary**

| Executed prototype component | ARM range, end exclusive | Bytes |
|---|---|---:|
| Request filter / forwarding | `$0807A414–$0807A492` | 126 |
| Reused nibble/packet CRC helpers | `$0807A6DE–$0807A736` | 88 |
| Fixed read/encode/send loop | `$0807B000–$0807B1BE` | 446 |
| Incremental whole-data CRC | `$0807B600–$0807B628` | 40 |
| Existing USB-output drain adapter | `$0807B800–$0807B852` | 82 |
| **Total executed code** | noncontiguous prototype placement | **782** |

**PROVEN offline:** immutable request template232 bytes at `$0807BC00–$0807BCE8`; no512-byte device buffer; new static RAM0; new heap0; local frame188 bytes plus command saves20 and entry saves32. Normal nested native calls use more stack, as reported above. Only the88-byte codec tail of phase27 is loaded; the obsolete direct-backend command is excluded. Prototype changes to vectors/DSP/bootloader/option bytes are zero. Code bytes are assembled into emulator memory, not exported as an application image.

**STRONG INFERENCE — minimal SC35D8 integration plan:** retire the old remote/pad diagnostic entries and reuse their ARM code pool `$0806B6CC–$0806BC8C` (1472 bytes), rather than append a large new framework. The manifest identifies `probe35s` and `rdiag` there. Restore the source-view pad slot `$0805AC9C` to `srcview:c_xpad=$0806B588|1`, and the service hook `$080213AA` to `persist19:c_dtick19=$0806B3C6`. Replace the dispatcher hook `$0801EB30` with the new filter, allowing only the new command; retire remote writes and pad write-back. A distinct6-byte application marker would be needed at `$080101E8`. Installer of old pad probe (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/probe35s.py:164`; not distributed), SC35D8 labels (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/firmware/sc35d8/manifest.json`; not distributed).

**UNKNOWN:** this relocation/removal plan is not applied or validated against an exact SC35D8 image. The782-byte figure is exact for the executed prototype, **not** an exact candidate patch-size claim. Final changed-byte count, pool packing, replacement hook bytes, residual call reachability, new image hash/CRC and final RAM budget remain unqualified. No claim of global minimality is made. The buffer/RX gate must close before candidate generation, as requested.

**11 — Installation preservation of BOTH regions**

**PROVEN for the prior selected installer/staging graph:** rechecking every WRITE/ERASE interval in phase33 gives:

| Evidence interval | WRITE overlaps | ERASE overlaps |
|---|---:|---:|
| `$81000–$81016` | 0 | 0 |
| `$82000–$821FF` | 0 | 0 |

The previous selected staging footprint is below `$6BD00`, its sector erases below `$6C000`, plus metadata programming `$80000–$80016` and erase `$80000–$80FFF`. Those ranges exclude both requested records. This is a new overlap check of preserved operations, not a rerun of an old evidence writer. Selected operations (local-only reference: `builds/phase33-preservation-powercycle/installation.json`; not distributed), [phase41 check](<../builds/phase41-fixed-nor-diagnostic/audit.py>).

**UNKNOWN:** that trace uses the earlier phase30/B1.3 prototype image, not the proposed SC35D8 derivative. Complete installation/first-boot preservation for **this exact application** is not proved. The normal identity setter can erase `$81000–$81FFF`; excluding it from the selected update trace is not proof that no other startup path invokes it. No target values are inferred from these interval checks. Exact artifact/update-path closure is still needed; full virtual-device emulation is not asserted as its necessary method.

**12 — Dormancy during boot**

**PROVEN offline local filter behavior:** ordinary messages preserve the original dispatch route; only an explicit, correctly padded USB command13 enters the new NOR loop. No startup invocation of the adapter is added in the prototype. **HARDWARE-TESTED reference behavior:** SC35D8 boots and handles remote requests as recorded. **UNKNOWN exact candidate:** no complete SC35D8-derived byte comparison or retired-probe regression has been performed. Therefore complete pre-UI dormancy/equivalence is not yet claimed. This gate calls for exact hook/call/reachability checks and bounded regressions, not broad peripheral boot emulation.

**13 — Recovery and exact rollback artifact**

**PROVEN offline:** the official4486 rollback artifacts exist and were rehashed:

| Existing artifact | Size | SHA-256 |
|---|---:|---|
| Official4486 SYX (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/stock/circuittracks-firmware-4486-STOCK.syx`; not distributed) | 432961 | `bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd` |
| Official4486 BIN (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/stock/circuittracks-firmware-4486-STOCK.bin`; not distributed) | 314844 | `b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da` |

The existing official SYX decodes through reference `ct_fw.decode` to the exact stock BIN. No new rollback firmware was generated. Proposed modifications lie in application ARM code and do not require bootloader, recovery-button handler, option-byte, vector or DSP changes. **UNKNOWN:** exact final candidate comparison and physical rollback on this unit; no absolute safety claim is made. Existing recovery analysis remains evidence about its analyzed path, not a newly performed recovery test.

**14 — Decision and smallest remaining experiment**

**PROVEN:** exact535-byte normal reconstruction and host failure containment pass in their stated offline scopes. DMA reachability and cache policy are now documented independently of emulator assumptions. All451 previously pinned reference inputs,183 Plaits sources and preserved phase26–39 evidence hashes checked by `audit.py` remain unchanged.

**UNKNOWN:** full ownership of the borrowed parser window under real incoming USB activity; duplicate queuing/replay after return; exact SC35D8 integration/removal of legacy mutators; and preservation through that exact update path. Consequently **no firmware image, candidate SYX, live capture command or flashing step is supplied**.

**STRONG INFERENCE — next smallest experiment:** replace the duplicate counter seam with a bounded native USB-RX/Main input-service replay while the new callback is suspended in Storage, then drain pending input after normal return. Verify that no IRQ/parser writer overwrites `$2000A070–$2000A0AF`, no deferred duplicate initiates another capture, and failure never releases its live frame. Qualify that ownership or select/protect a different explicitly owned buffer before assembling the SC35D8-derived candidate. This stays within diagnostic ownership; phase40 and broad cold boot remain paused.

FIXED NOR EVIDENCE DIAGNOSTIC = UNQUALIFIED

## Phase42 � exact SC35D8 integration qualified offline

**PROVEN:** the closed exact-base gate was reused: SC35D8 size `$5BC8C`, CRC `$73BA1238`, SHA-256 `1525c6662bbff9ced7e6055bb54e864615c30013f1b4dec4be6c404f8c750c05`. The internal candidate has the same size, CRC `$AC9987BA`, SHA-256 `9b29180ff7f88c9c982c60abdfd5e5b296e8f2240ad57580366a5a7f797930a6`. No new SYX or hardware access occurred.

**PROVEN in bounded native replay:** a 12-byte record at `$20044D70�$20044D7B` survives parser reuse and implements IDLE / ACTIVE / SUCCESS / FAILED_QUARANTINED. It extends the reference heap-top reservation by 12 bytes, preserves the existing 220-byte Master-FX state, and fails closed if reservation is unavailable. Duplicates and new sessions cannot rearm it. All requested A�O adversarial cases pass; the native RX ring, Main parser/fanout, Storage read path and native TX router execute. Pending input can overwrite the parser after return; the persistent latch, rather than serial dispatch, prevents another capture. Full 232-byte adversarial overwrite after return changes neither state nor admission.

**PROVEN:** native TX copies replies synchronously to `$20009BAC`; asynchronous USB IN uses independent `$20009B04`. Delayed/lost completion tests verify no premature buffer reuse. At 5000 counter ticks the device only quarantines; it never forces Storage release. H4 remains FAIL for in-session recovery. The host has a separate 5.0-second deadline, atomic publication, and one-attempt guards for both transport Link and lease. Native USB output reconstructs exactly 23 + 512 synthetic bytes; truncation/duplicate completion publishes nothing. The output under `builds/phase42-exact-rdiag-integration/synthetic-capture/` is synthetic, not device evidence.

**PROVEN for this exact image in the selected updater/install model:** both `$81000�$81016` and `$82000�$821FF` have zero direct writes and zero erase overlaps. Minimum half-open WRITE/ERASE gaps are respectively 4073/0 bytes and 8169/4096 bytes; zero means adjacent, not overlapping. Native validation/installer loops install the exact candidate. DSP, vectors, bootloader and option bytes remain unchanged. All pinned reference/Plaits and prior validated evidence hashes remain unchanged.

**STRONG INFERENCE:** guarded entry structure and unchanged startup keep the command dormant before an explicit request. **UNKNOWN:** complete cold-boot write census, actual unit heap headroom, physical I/O timing, actual NOR contents and hardware recovery. The selected updater trace uses modeled interfaces/completion; unchanged identity maintenance can erase its own sector if invoked. This offline qualification does not close those broader hardware/boot claims.

See [phase42 findings](<../docs/research/phase42-exact-rdiag-integration/findings.md>), exact patch map (local-only reference: `builds/phase42-exact-rdiag-integration/patch-map.json`; not distributed), native cases (local-only reference: `builds/phase42-exact-rdiag-integration/native-results.json`; not distributed) and installation trace (local-only reference: `builds/phase42-exact-rdiag-integration/installation.json`; not distributed).

**STRONG INFERENCE � next and only next phase:** candidate-SYX generation plus independent offline validation from this pinned BIN; no transmission. That phase has not been started.

EXACT RDIAG NOR INTEGRATION = PASS
