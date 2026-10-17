> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# CIRCUITS-HACKS diagnostic reuse audit

2026-10-16. Scope: the local public-reference checkout, especially SC35D4/D5/D8. NOR81000 symbolic/cold-boot qualification is paused. No reference source was modified; no builder, firmware generation, MIDI port operation or hardware test was run.

**PROVEN:** the reference contains both the implementation and explicit dated reports of successful USB diagnostics and synchronous SD-content reads on hardware. **STRONG INFERENCE:** reuse that transport, caller context and small-buffer pattern, adding a fixed raw-NOR adapter. This can simplify evidence acquisition substantially. **UNKNOWN:** hardware success and preservation of the proposed raw-NOR extension. Reuse PASS below is an architectural reuse decision, not hardware-readiness or preservation approval.

**PROVEN evidence distinction:** “tested on hardware” below means the repository explicitly records that result; this audit did not independently repeat it. `PRUEBA.md` files mostly prescribe tests. The later result entries in `docs/NOTAS.md` and the matching `CLAUDE.md` entries supply the actual hardware claims. Older “pending” headings and the original mistaken PCM kind must not override the later results. [Hardware results][results], [summary][claude], [SC35D4 instructions][d4], [SC35D5 instructions][d5], [SC35D8 instructions][d8].

**1. Is there already a hardware-tested USB/SysEx diagnostic transport that we should reuse instead of our new protocol?**

**PROVEN:** yes, as reported for SC35D8 on 2026-10-09. The recorded run includes `ping` version `$35D8`, USB port 0, ARM application-header reads, PCM information, and an entire 19,844-byte WAV downloaded in **311 requests of at most 64 bytes**, matching the SD backup byte for byte. This is much stronger evidence than just the test instructions. [Dated results][results].

**PROVEN code:** `rdiag.arm_code`, entry `c_rdin`, replaces the four-byte prologue at `$0801EB30`; foreign messages execute the original prologue and continue at `$0801EB34`. Requests use `F0 7D 43 54 cmd seq … F7`; replies use `cmd|$40`, the same sequence and incoming port. `c_rdcmd` requires at least `PAD-4` bytes; the host generates **232-byte** requests. Numbers are eight nibbles; bytes are two nibbles. `rc_send` calls the existing router `$08020C90`, obtained through the literal at `$0801EDD0`, with mask `1 << port`. No new USB endpoint or IRQ sender is needed. [Implementation][rdiag], [host codec][codec], [emulator checks][e8].

**PROVEN:** our phase27 is already partly reusing this architecture: `protocol.py` uses the same signature, `PAD=232` and command/reply convention; `receiver.py:WinMMTransport` explicitly wraps `ctremote.Link`. Thus the work is consolidation and a smaller command adapter, not replacement of an entirely independent USB stack. Its CRC-framed multi-packet capture is an extension whose integrity properties are not supplied by the original transport. [Our protocol][oursproto], [our WinMM adapter][oursreceiver].

**PROVEN:** SC36.1 deliberately removed `rdiag` from its normal build path. A historical diagnostic implementation is not evidence that a normal B1.3 installation currently answers these commands. `build_sc35d8.extra` installs both `probe35s` and `rdiag`; its base also enables write-back pads. Reusing the mechanism does not mean adopting that whole diagnostic build or its write commands. [SC36.1 builder][no-rdiag], [SC35D8 builder][b8].

**2. Is there already a hardware-tested Main/UI → Storage task submission path with correct task/IRQ ownership?**

**PROVEN:** the reported SC35D4 UI-pad path made synchronous content requests without hanging: exists=1, status=0, 21 bytes, session size 160,780. SC35D5 changed kind **2 → 4**, producing the expected PCM WAV headers and eight exact file sizes. SC35D8 successfully called the content API from the incoming SysEx task, matching the existing Components calling pattern. [Results and API description][content-results], [SC35D5 builder correction][b5], [probe implementation][probe].

**PROVEN code:** the public content API is `$0803CA52`; exists `$0803CB50`, size `$0803CB6A`, read `$0803CBF0`, write `$0803CC16`. A 12-byte item contains u32 kind, u32 index and u8 pack; `$FF` means current pack. With callback=0, submission uses the synchronous path `$08022A46` rather than asynchronous `$08022A5C`. `probe35s:c_spad` submits from UI; `c_dtick35` only paints LEDs and forwards the service chain. `rdiag:rc_read` submits from its SysEx caller, with callback/context zero and a live `&done` stack slot. File opening/closing stays in the stock storage service. [Probe][probe], [rdiag read][rdiag-read], [stock path documentation][content-api].

**STRONG INFERENCE:** reuse the tested task-context/public-submission pattern instead of issuing NOR DMA from UI, DSP service or IRQ code. **UNKNOWN:** those successful **SD file** operations do not establish complete NOR IRQ ownership, DMA completion, error unwind, or all scheduler interleavings for a new raw command. Both reference emulator suites stub the content API and MIDI/router endpoints; they do not execute those lower layers. Our phase29–31 native NOR closure remains relevant. [Emulator D4][e4], [emulator D8][e8], [our NOR ownership/error audit][nor-errors].

**PROVEN negative reuse lesson:** SC34D's generic file-vtable interception was reported to break pack duplication, leaving copied packs without sessions. It is not the mechanism to revive. [Failure report][sc34d].

**3. What physical buffers/RAM regions did those diagnostics use successfully on hardware?**

| Mechanism | PROVEN source allocation / addressing | Hardware-evidence limit |
|---|---|---|
| SC35D4/D5 `c_spad` | A **64-byte local stack frame**, `FR=64`; callback/context/`&done` at +0/+4/+8, done at +12, item at +16, **21-byte read at +28…+48** | Reported UI reads succeeded; absolute runtime SP is not recorded by those reports |
| SC35D4/D5 CC dump | `c_gst()+104…+159`, **14 u32 words / 56 bytes**, borrowed from the idle Master FX LED area while the source view is open | Reported dumps succeeded; this is conditional sharing, not permanently free RAM |
| SC35D8 `rc_read` | **Caller-owned incoming SysEx buffer +160…+223**, at most 64 bytes; response starts at the same buffer's beginning; 232-byte padded request | Reported 64-byte content reads succeeded; absolute hardware buffer address is not published there |
| SC35D8 `c_rdcmd` | **40-byte local frame**, including item +16, done +12 and output message descriptor +32 | This is local frame size, not the total nested stack usage |

Sources: [probe constants and frame][probe], [inherited dump buffer][probe32], [rdiag constants][rdiag-constants], [read/send code][rdiag-read].

**PROVEN:** `emu_sc35d8.py` uses `MSG=$20060000`, `BUF=$20060100`. The inherited emulator explicitly maps that artificial scratch area separately from physical SRAM `$20000000…$2004FFFF`. These are **not hardware buffer addresses**, and must not be copied into a firmware allocation plan. [E8 fixture][e8], [base emulator mappings][e05].

**PROVEN within our existing fixture:** phase30 identifies the stock parser allocation `$2000A050`, capacity360, with its own raw window `$2000A070…$2000A0AF` (**+32**, not rdiag's +160). The latter is classified there as DTCM; the fixture also shows that allocating 64 heap bytes can fail or disable retained state. **UNKNOWN:** the historical SD-content reads do not prove direct QSPI-DMA suitability of either relative window. Do not replace the physical-buffer qualification with the reference's synthetic `$20060100` fixture or assume its stack/LED region is DMA-safe. [Phase30 allocation/lifetime evidence][physical].

**4. Is there already a safe method for chunked reads without allocating 512 bytes?**

**PROVEN:** for SD-content reads, yes: `ctremote:dump` advances the file offset and requests at most `NMAX=64`; `rdiag:rc_read` reuses the same 64-byte raw window after each synchronous operation and response. The reported 311-request download exercises this pattern on hardware. Reconstruction is on the host. A 512-byte device allocation is unnecessary. [Host dump loop][dump], [hardware result][results].

**STRONG INFERENCE:** the same bounded-buffer architecture fits eight fixed 64-byte NOR chunks plus a 23-byte identity read. **UNKNOWN:** SD success does not qualify the changed backend or failure handling. Preserve the live buffer until DMA has finished; a failed/absent completion must quarantine the attempt, not trigger reuse. [Our fault evidence][nor-errors], [host containment][containment].

**5. Does any existing diagnostic or stock API expose raw external NOR/QSPI reads, directly or indirectly?**

**PROVEN:** no raw-NOR command exists in the inspected `rdiag` dispatcher. Command2 directly loads **ARM internal flash/SRAM** only: `[08000000,08080000)` and `[20000000,20050000)`. Command5 reads a **pack item**, not a physical NOR offset. Commands3/8, when enabled, access DSP memory through the DSP service, not NOR. The targeted search of reference `tools/*.py` found no QSPI/raw-NOR adapter for the requested physical ranges. This is a scoped source finding, not a claim that no such utility can exist elsewhere. [Whitelist and commands][rdiag-constants], [mem/read implementations][rdiag-mem].

**PROVEN from our already-established stock API evidence:** a raw NOR read API does exist. `$08047C6C(offset,buffer,length)` loads the NOR wrapper and enters synchronous `$08024130`; the wrapper is published through `$20006968`. Enqueue `$08023F68`, wait `$08023FD6`, Storage worker `$08024014`, and operation1 dispatch reach backend `$08022F94` and DMA reader `$08037430`. This is distinct from content API `$0803CBF0`. No new controller driver is needed. [Phase29 closure][closure], [phase31 exact users][nor-errors], [native synchronous wrapper][sync-read].

**6. Is there any existing code/path capable of reading physical NOR around `$81000…$81016` and `$82000…$821FF`?**

**PROVEN:** the application identity reader `$0802520C` calls that wrapper with offset `$81000`, destination `$20006868`, length23. It then writes zero to byte14 at `$08025224`. The bootloader counterpart `$08005D98` reads into `$2000546C` and zeroes byte14 at `$08005DB0`. The target range is also within the same backend; phase30 already exercises its eight-chunk read offline. [Identity readers][identity], [phase30 command][stream], [stock backend][nor-errors].

**PROVEN:** reading the application's 23-byte SRAM cache with existing `mem` cannot recover the original byte14; nor does it prove the other bytes' history. For the requested **raw** 23 bytes, use a fresh read of physical `$81000`, without calling the normalizing identity helper. **UNKNOWN:** an already hardware-tested diagnostic command for either physical interval was not found. The stock protocol's additional read/send path around `$08024FDC`, identified in phase31, is not admitted as a ready unrestricted read command: its routing/state prerequisites were not qualified, and the surrounding handler also includes mutation commands. [Phase31 protocol-user inventory][nor-errors], [prior normalization evidence][identity].

**7. What is the SMALLEST change to hardware-tested rdiag infrastructure to add a fixed, read-only raw-NOR command?**

**STRONG INFERENCE — smallest per-command adapter:** add one explicitly reserved command branch alongside `rc_read`, retaining `c_rdin`, the signature/sequence codec, same-port router, 232-byte input ownership and small raw window. Replace the content item/offset/API call with `$08047C6C(fixed_address,raw_window,fixed_length)` in the SysEx task. Expose **only nine enumerated blocks**: one23-byte block at `$81000`, then eight64-byte blocks at `$82000+64*i`, `i=0…7`. Reject every other selector; accept no arbitrary address, length, storage selector, WRITE or ERASE operation. Copying/encoding starts only on successful completion. [Reusable read branch][rdiag-read], [existing raw API][closure].

**STRONG INFERENCE:** this is a wrapper/dispatcher change, not a storage-worker, QSPI driver, IRQ, scheduler or bootloader change. Omit the SC35D8 base's write-back pads and mutation commands from a purpose-specific derivative; do not assume its complete builder is read-only. If the single-trigger multi-packet containment contract is retained, place our existing phase30 fixed capture loop behind that branch instead; extending its fixed schedule by the23-byte block is smaller than another controller implementation. A nine-successful-request host sequence is another design, but needs new session-level tests and must send nothing after the first failure. [SC35D8 builder flags][b8], [existing fixed loop][stream], [containment contract][containment].

**UNKNOWN — work still required before such an adapter is qualified:** verify the real raw window's DMA accessibility, lifetime and alignment; disjoint encoding/raw areas; caller register preservation; exact op1-only dispatch; output-drain ownership; every supported error path; and the extra23-byte host validation. Original `rc_read` replies fit in151 bytes below `RAW=160`; larger metadata/CRC frames require a new overlap calculation. This audit does not specify a new untested allocation or generate its machine code.

**8. Which parts of phase27–phase39 are redundant because the reference already proves them on hardware?**

| Existing work | Reuse decision / confidence |
|---|---|
| Basic USB diagnostic signature, hook, same-port replies, WinMM receive/send and nibble codec | **PROVEN:** implemented and reported exercised in SC35D8; avoid re-establishing these from reset as a prerequisite for proposing a capture |
| Task-context synchronous content submission and small-buffer repeated downloads | **PROVEN:** reported in D4/D5/D8; avoid a new file-vtable hook or 512-byte heap allocation |
| Phase27 host transport | **PROVEN:** already reuses `ctremote.Link`; consolidate, rather than discard it as wholly independent |
| Phase29/30 raw-NOR worker, request ownership, DMA/IRQ path, parser-window and drain checks | **UNKNOWN hardware qualification:** not replaced by SD stubs or file tests; retain these results and constraints |
| Phase31 error ownership; phase32 CRC, absolute deadline, no-retry and atomic evidence publication | **PROVEN:** add guarantees absent from the reference host; retain |
| Phase33 install footprints and preservation reasoning | **UNKNOWN complete preservation:** reference successful diagnostic use does not prove target preservation across installing our derivative |
| Phase34–39 cold-start/scheduler/peripheral investigation | **STRONG INFERENCE:** unnecessary as a universal prerequisite to designing a post-boot data-acquisition experiment; still useful evidence, and still required if claiming a complete cold-boot/preservation proof |

**PROVEN:** `ctremote.Link.ask` sends once and has a default3-second reply timeout, but has no device-quarantine lease. `parse/dec_read` do not enforce full capture size, address sequence or CRC; `dump` accumulates in memory and then directly opens the final filename, rather than staging and atomically publishing. A pure codec check here confirms that done64 with only63 decoded bytes is accepted by the decoder. Reference transport reuse must not weaken phase32's acceptance rules. [Host implementation][host-link], [dump][dump], [our containment][containment], [audit checks][checks].

**9. Which blockers genuinely remain unsolved?**

- **UNKNOWN:** hardware qualification of the fixed raw-NOR adapter and its actual DMA buffer. The reference establishes SD-content success, not that new backend/buffer combination.
- **PROVEN within tested fault models:** phase31's TEF/missing-completion path retains Storage/request/semaphore/buffer ownership. No reference mechanism supplies a bounded NOR unwind. Keep H4 FAIL and one-shot quarantine until full power cycle; no forced release or retry.
- **UNKNOWN:** complete install/first-boot/cold-restart nonmutation of `$82000…$821FF`, H1/H2/P2/P3 at their existing scopes. `LEEME.md` gives updater/bootloader reasoning, not a universal audit of every application storage mutation or an identity-taint closure. [Updater document][leeme], [current preservation boundary][preserve].
- **UNKNOWN:** original raw23 bytes and authentic512-byte target capture are not acquired by this audit. A later post-install read would establish contents at that capture time, not automatically pre-install contents or an unchanged history.
- **UNKNOWN:** native cold-boot continuation across the blocked identity read and all asynchronous observers. This remains a blocker for an all-values boot theorem, although it need not prevent the smaller acquisition experiment from being designed and tested offline.
- **PROVEN:** host-only containment is not automatically wired into a new live command merely because its tests passed. Preserve exact lengths/addresses, CRCs, complete-capture checks, atomic output and failure lease when adapting it. [Phase32 scope][containment].

**PROVEN boundary:** SC35D2/D3 are **DSP external SDRAM** investigations. Their `X:$37F00`, `X:$3B80…$3BAC`, `Y:$580000`, `$337000…$57F000` and `$E80000…$FFF000` are DSP word-space allocations/observations, not ARM NOR byte addresses. SC342D's `Y:$3B40` copy window likewise does not expose NOR `$82000`. Do not use their memory map as a NOR-buffer or raw-NOR-read proof. [D2/D3 evidence][dsp-map], [resource map][resources], [DSP transport definitions][rdiag-constants].

**10. Can we obtain the needed23+512 bytes with one minimal diagnostic build instead of fully emulating every remaining cold-boot peripheral first?**

**STRONG INFERENCE:** yes as an acquisition architecture: one purpose-specific derivative can retain the proven USB task route and read all535 bytes through the stock NOR submission API using one reusable ≤64-byte window. One build does not require two installations or a512-byte device allocation. Full cold-boot emulation is not intrinsically necessary for a functioning device to perform a post-boot read.

**UNKNOWN:** that build has not been made or tested, and this is not permission or evidence to install it. Neither acquisition success nor original/pre-install preservation is yet proved. Obtaining the bytes would help concrete replay; it would not by itself close phase40's requested universal all-values/control-dependence proof.

**STRONG INFERENCE — smallest next experiment:** offline only, qualify a fixed raw-read branch at the existing rdiag dispatcher against the already available phase30 Storage/DMA/IRQ harness and phase32 failure/acceptance cases. Cover the23-byte block and eight64-byte blocks, exact source addresses, bounds, raw/encoded overlap and lifetime, op1-only dispatch, and no subsequent request/output publication after a failed chunk. Keep the reference transport tests as regression coverage; do not resume peripheral-by-peripheral cold-boot emulation merely to redesign USB transport. No implementation or build is performed in this audit.

**PROVEN audit validation:** all21 inspected source/document/manifest files were fully read and hashed, with the same hashes at the final source check. Pure host-code checks exercised all128 sequence values, all256 byte encodings, exact64-byte reply sizing and a length-validation counterexample, without importing WinMM or touching ports. Reference native suites were inspected, not rerun: they require firmware images and stub the relevant storage endpoints. No newly generated image was substituted for that missing test scope. [Source hashes and checks][checks].

[results]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/docs/NOTAS.md:1424>
[claude]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/CLAUDE.md:77>
[d4]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/firmware/sc35d4/PRUEBA.md>
[d5]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/firmware/sc35d5/PRUEBA.md>
[d8]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/firmware/sc35d8/PRUEBA.md>
[rdiag]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/rdiag.py:78>
[rdiag-constants]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/rdiag.py:40>
[rdiag-read]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/rdiag.py:197>
[rdiag-mem]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/rdiag.py:175>
[codec]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/ctremote.py:43>
[host-link]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/ctremote.py:134>
[dump]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/ctremote.py:227>
[probe]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/probe35s.py:24>
[probe32]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/probe32b.py:25>
[e4]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/emu_sc35d4.py:1>
[e8]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/emu_sc35d8.py:1>
[e05]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/emu_sc05.py:18>
[b5]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/build_sc35d5.py:1>
[b8]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/build_sc35d8.py:29>
[no-rdiag]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/build_sc36_1.py:1>
[content-results]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/docs/NOTAS.md:1448>
[content-api]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/docs/NOTAS.md:1466>
[sc34d]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/docs/NOTAS.md:1546>
[dsp-map]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/docs/NOTAS.md:1483>
[resources]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/docs/RECURSOS.md:88>
[leeme]: <C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/LEEME.md:18>
[oursproto]: <C:/Proj SSD/CODEX/CIRCUIT/builds/phase27-qspi-read/protocol.py:4>
[oursreceiver]: <C:/Proj SSD/CODEX/CIRCUIT/builds/phase27-qspi-read/receiver.py:6>
[closure]: <C:/Proj SSD/CODEX/CIRCUIT/builds/phase29-storage-wrapper/closure.json>
[physical]: <C:/Proj SSD/CODEX/CIRCUIT/builds/phase30-chunked-storage/ownership-and-error-audit.json>
[stream]: <C:/Proj SSD/CODEX/CIRCUIT/builds/phase30-chunked-storage/stream.py:13>
[nor-errors]: <C:/Proj SSD/CODEX/CIRCUIT/builds/phase31-storage-error-recovery/findings.md>
[sync-read]: <C:/Proj SSD/CODEX/CIRCUIT/builds/phase30-chunked-storage/08024130.asm>
[containment]: <C:/Proj SSD/CODEX/CIRCUIT/builds/phase32-host-containment/findings.md>
[identity]: <C:/Proj SSD/CODEX/CIRCUIT/builds/phase39-nor81000-symbolic/findings.md>
[preserve]: <C:/Proj SSD/CODEX/CIRCUIT/notes/qspi82000-preservation-powercycle.md>
[checks]: <C:/Proj SSD/CODEX/CIRCUIT/builds/reference-diagnostic-reuse/evidence.json>

CIRCUITS-HACKS DIAGNOSTIC REUSE = PASS
