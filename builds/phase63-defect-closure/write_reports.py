from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[1]
load=lambda n:json.loads((O/n).read_text());c=load('development-identity.json');v=load('preflight-verdict.json');u=load('uploader-binding.json');a=load('allocation-coverage.json');s=load('continuity-status.json')
def link(n):return f'[{n}](<{(O/n).as_posix()}>)'
def write(n,t):(O/n).write_text(t.strip()+'\n',encoding='utf-8')
write('findings.md',f'''
# Phase63 narrow defect closure — development image remains ineligible

**FINAL PREFLIGHT CLOSURE = UNQUALIFIED. Do not use this image for a hardware test.**

The three Phase62 defects have targeted implementation changes and passing scoped regressions. The mandatory continuous startup and full postboot allocation gates are incomplete. Passing prepared-RAM tests does not replace those gates. No hardware was accessed, MIDI ports opened, firmware transmitted, or reference repository modified.

| Requirement | Evidence / result | Confidence |
|---|---|---|
| SD cannot invalidate unchanged NOR | NOR FS/object predicates; native SD mount/unmount/remount and binding/stride tests | PROVEN within tested paths |
| Actual NOR remount/change invalidates authorization | Post-export remount rejects; pre-export repeat must exactly match the first snapshot | PROVEN within tested paths |
| Explicit statuses | Actual dispatch emits READY/AUTHORIZED/SUCCESS; classifier tests cover remaining states; 39-byte CRC-protected wire replies | PROVEN within native boundary tests |
| DMA stack lifetime | No CPU consumption or wrapper return before EN=0, NDTR=0, request=0, backend semaphore=1; 31 coupled cases | PROVEN in declared model |
| New reservation / prior native suite | 7 reservation and 28 native cases pass | PROVEN |
| Host containment | 32 fake-transport cases pass; NOT_READY query can repeat; failures cannot retry/publish | PROVEN in mocks |
| Continuous reset→capture | Same-state startup survives NOR/SD; still stops before USB service | UNKNOWN beyond current frontier |
| Complete postboot allocations | {a['observed_request_count']} requests observed in prefix; subsequent startup/runtime not reached | UNKNOWN |
| Install / both rollbacks | All three exact-stream native replays pass, no silent no-op, bootloader excluded, protected ranges unchanged | PROVEN within stated seams |
| Uploader binding | Exact candidate/rollback hashes bound to a tested, MIDI-locked review copy | PROVEN; live admission withheld |

## New identity, development only

- BIN: `{c['candidate']}.bin`, {c['BIN_bytes']} bytes; SHA-256 `{c['BIN_sha256']}`.
- SYX: `{c['candidate']}.syx`, {c['SYX_bytes']} bytes; SHA-256 `{c['SYX_sha256']}`.
- CRC-32/MPEG-2 `{c['CRC']}`; compared-header marker `N63DEV`; application `08010000..08075100` exclusive; 44,800 image bytes remain below the application limit. This is not a RAM margin measurement.
- Independent disk SYX decode equals BIN; all 1,558 changed bytes versus frozen Phase62 are classified in {link('development-identity.json')}. No bootloader bytes are part of the generated application image.

## Remaining gates and smallest continuation

**UNKNOWN:** final continuous startup→USB-ready→geometry query→authorization→raw capture. Latest native prefix executes {s['instructions']:,} instructions, ends at `{s['frontier']['pc']}`, and retains record `{s['record']}`. The exact missing model is SPI2 polled TXE/RXNE and received-data behavior at `$08037960-$0803799C`, status register `$40003808`. The native wait is not bypassed and no replacement running-RAM fixture is spliced in. It is a model frontier, not evidence of a hardware hang or a new firmware corruption defect.

**UNKNOWN:** allocation coverage through that missing continuation. Ordinary nonoverflow allocator bounds and diagnostic no-allocation behavior are tested; they do not enumerate every later startup/runtime owner. Hardware heap/stack headroom remains separately **UNKNOWN (HARDWARE-ONLY)**.

The smallest next experiment is to complete that exact SPI2 exchange model using the pinned DSP startup protocol, resume the same-state runner through USB readiness and capture, and record remaining allocations. Do not restart the NOR investigation, rebuild an unchanged candidate, rerun successful install/rollback tests, or force readiness counters. If that requires candidate changes, every invalidated image-specific gate must be rerun.

See {link('sd-mount-fix.md')}, {link('status-protocol.md')}, {link('buffer-ownership.md')}, {link('startup-allocation.md')}, {link('install-uploader.md')} and {link('CHECKPOINT.md')}.

Phase61's 112 manifest entries and both frozen Phase62 images verify unchanged: {link('historical-preservation.json')}. Neither historical image is reinstated. There is no final hardware-eligible candidate or enabled uploader.

FINAL PREFLIGHT CLOSURE = UNQUALIFIED
''')
write('sd-mount-fix.md',f'''
# Mount ownership correction

**PROVEN:** original `$0801AE02` calls the same adapter for NOR FS `$20000AB0` and SD FS `$20001B04`. Phase61 `begin` treated any nonzero lifecycle word as invalid and stored `1D`, including after NOR snapshot `11` when SD mounted. This was a shared callback-owner predicate bug, not a demonstrated shared NOR/SD generation counter.

**PROVEN:** new `build_ops.begin` at `$0806CF00` ignores all but R0=`20000AB0`. `snapshot` at `$0806D500` independently requires outer-mount R4=`20000AA0` (its FS is object+10), exact reserved heap limit `$20044D70`, and cursor at/below that limit. Existing drive-0 predicates remain in register/slow/binding/stride adapters. SD registration `1:` and its object/stride are ignored. The seven negative reservation cases still execute installed AE06 and original AE14 tail.

**PROVEN:** startup legitimately mounts NOR again through `$08026250→0801ADDC` before export. `11→17` now denotes pre-export recheck. Registration/slow mount and 4096-byte stride are permitted only in first-mount `16` or recheck `17`. Snapshot recomputes all packed fields; recheck compares both 32-bit words with the original, writes neither payload word, then returns to `11`. A mismatch, failed mount, or later exported/active-state remount invalidates authorization. Binding change still invalidates.

**PROVEN in tested paths:** SD mount/failing mount/unmount/remount, SD binding/stride, unchanged pre-export NOR remount, changed NOR geometry, and post-export NOR remount: {link('status-mount-tests.json')}. All previous native cases remain: {link('native-tests.json')}. Native startup private writes show `16→11→17→11` with no SD invalidation; only first snapshot writes payload.

**STRONG INFERENCE:** owner predicates separate NOR lifecycle from SD activity for other invocations of these same adapters. This is not a universal proof about arbitrary writes to geometry outside the inherited mutation closure.

Implementation: {link('construct.py')}, `module` asserted transforms of the unchanged Phase61 emitters. Full M-class listings are in `reviewed-*.asm`.
''')
write('status-protocol.md',f'''
# Explicit status protocol and host containment

**PROVEN:** new commands retain fixed 232-byte request ownership, geometry `0E`, authorization `0F`, session 1..127 and exact same-epoch geometry echo. No arbitrary address command or storage cleanup/retry command is added.

`F0 7D 43 54 4F session code epoch[8 nibbles] zero[15] CRC[8 nibbles] F7` is exactly 39 bytes. CRC-32/MPEG-2 covers bytes4..29. Epoch=0 for NOT_READY and1 otherwise. The 15 reserved bytes must be zero.

| Code | Meaning / behavior |
|---:|---|
|1 NOT_READY|BOOT, MOUNTING or pre-export recheck; no state publication/raw request. After a complete valid quiet response window, host removes only its query marker and permits another query.|
|2 INVALID|Geometry/lifecycle rejected; no authorization/raw request.|
|3 UNSAFE|Mapping veto; clean stop with no authorization.|
|4 READY|Geometry follows. An unconsumed export may be queried again; session replacement invalidates the old session token.|
|5 FAILED|Fatal attempt; no raw retry, full physical power cycle required.|
|6 AUTHORIZED|Actual successful native authorization ACK, before raw dispatch.|
|7 SUCCESS|Actual terminal native success, after raw completion; host requires both the complete valid data stream and this status.|

**PROVEN:** `{link('status_emitter.py')}` emits `status`74100, `classify`74400 and USB-only `status_drain`74700. Drain has a 5000-tick bound independent of FAILED/INVALID record gating. It invokes stock router20C90, which copies into its retained ring; no Storage API is called. Stack reply memory is not the USB hardware destination. Disconnection cannot be answered over a disconnected link.

**PROVEN:** device classification tests exercise all seven codes. READY→AUTHORIZED→SUCCESS packets also execute through actual command dispatch. UNSAFE is explicitly a classifier-state injection test: supported valid compact D4000 mappings cannot overlap these lower fixed targets. No authentic unsafe mounted geometry is claimed. Host additionally applies independent target reachability veto before authorizing.

**PROVEN in mocks:** {len(load('host-tests.json')['cases'])} cases in {link('host-tests.json')}; malformed CRC/framing, stale session/epoch, duplicates/order/missing completion, disconnect, timeout and partial tails fail without output. Evidence publication remains the inherited all-validated atomic-directory rename. Raw time window10s starts before authorization send; send bound2s; geometry/query window10s. No automatic raw retries. Durably marked uncertain sends remain non-retryable.

**PROVEN in declared model:** if fatal storage ownership never releases, Main deliberately remains in its live frame. It cannot simultaneously send a new status from that blocked Main call. The host's absolute deadline therefore explicitly reports FAILED / DO NOT RETRY / POWER-CYCLE DEVICE BEFORE ANOTHER ATTEMPT. Native FAILED packets are sent on quiescent failure exits or processable status queries; this does not promise an outbound packet from an unrecoverably blocked/disconnected task.

**PROVEN:** initial 24-byte status integration failed in stock router/copy execution (`20D5A`); saved {link('status24-coupled-counterexample.json')}. Its hardware cause is **UNKNOWN**. That encoding was rejected. Current 39-byte framing follows the already exercised geometry reply length and passes coupled router/USB execution. This does not classify the 24-byte fault as firmware-independent emulator behavior.

Host: {link('live_host.py')}; pure parser {link('status_protocol.py')}; deterministic mocks {link('host_tests.py')}. CLI remains locked by UNQUALIFIED preflight; no MIDI inventory operation was run.
''')
write('buffer-ownership.md',f'''
# DMA destination lifetime and quarantine

**PROVEN:** the old frozen Phase62 counterexample is preserved in its original `dma-ordering-probe.json`. It returned SUCCESS with DMA stream7 EN=1, NDTR=64 and M0AR pointing at dead Main stack. Physical occurrence of that ordering remains **UNKNOWN**; its software consequence was demonstrated, not assumed away.

**PROVEN:** current `construct.FENCE` is called immediately at `read_ok` (before any CRC/encoding raw read) and at the common raw-frame exit. It reads:

- `$400264B8` DMA2 stream7 CR, EN must0;
- `$400264BC` NDTR must0;
- `[$20006968]+16` stock synchronous request flag, must0;
- `[[$20006968]+4]+8` backend semaphore, must1/released.

Until all pass, native scheduler yield `$0801BE60` repeats without popping the Main frame. The fence never writes a DMA control register, releases a semaphore, clears the request, resubmits a read, or aborts Storage. H4 remains no bounded in-session unwind. A stalled/failed transfer can retain the frame until full power cycle. Late physical completion permits return only once ownership is actually released; FAILED remains absorbing.

**STRONG INFERENCE:** these peripheral and software conditions, with no queued second request and no reentrant Main callback, exclude the demonstrated stale-pointer rearm. Reference [ST RM0385](https://www.st.com/resource/en/reference_manual/dm00124865-stm32f7-series-advanced-armbased-32bit-mcus-stmicroelectronics.pdf) identifies stream EN low as configuration-ready. Search-index excerpt was available; full PDF fetch timed out. No silicon timing/cache/bus experiment was performed and no forced-disable sequence is asserted qualified.

| Resource | Owner / lifetime | Writers / readers |
|---|---|---|
|64 raw bytes, R7+192..255 in260-byte frame|Single Main diagnostic invocation until fence permits unwind; retained indefinitely on unresolved failure|Stock QSPI DMA writes; Main CRC/encoder reads only after fence; guard words outside payload|
|12-byte record20044D70..D7B|Early-reserved diagnostic lifetime; reset by installed constructor|Reviewed lifecycle/mount/watch/authorization helpers; host cannot supply addresses|
|Packet areaR7+16|Main live frame; router copies before release|Main encoder; stock router20C90 reads/copies|
|Existing transport rings/parser|Existing native retained ownership|Native parser/router/USB; no new heap allocation|

**PROVEN in fixtures:** option B, an additional fixed64-byte allocation, lacks demonstrated free ownership: reference running RAM has only8 bytes before the reserved record. No unrelated buffer is borrowed and that margin is not current-unit headroom. Option A was chosen because a native non-return fence can be tested without a new RAM claim. It intentionally sacrifices bounded return on fatal failure. A separately qualified fixed buffer could provide an additional lifetime invariant later; it is not silently assumed here.

**PROVEN in declared model:** {len(load('dma-regression.json')['cases'])} cases in {link('dma-regression.json')}, from {link('dma_regression.py')}: normal, TEF/missing IRQ at0/4/8, timeout, early TCF with DMA outstanding, duplicate IRQ, late physical release, disconnect during pending reads, late completion while disconnected, producer preemption/queued duplicate, busy backend. No second read follows failure. Canaries persist through their live ownership; checks end at actual raw-frame return because subsequent status calls legitimately reuse stack. Native register checks remain enabled.

Normal measured Main minimumSP200080FC (2460 bytes to fixture lower guard), Storage20009174 (1068). These are prepared-running-RAM model measurements, not final startup/hardware headroom. The guarded software path passes; full boot→capture continuity remains **UNKNOWN**.
''')
write('startup-allocation.md',f'''
# Continuous startup and allocation coverage — remaining gate

**PROVEN:** current exact decoded candidate executes reset prefix, native constructor reservation, real RTOS launch, first NOR mount/snapshot, SD initialization and native later NOR verification in one emulator state. No separate exported record, running-RAM fixture or hand-edited task context is inserted at a startup seam. Final retained NOR record is `{s['record']}`. State remains valid through all observed activity.

**PROVEN:** original inherited startup model stopped in repeated display progress because analog input acquisition events were absent. The extension uses actual ADC IRQ34 and DMA IRQ72 previously mapped in Phase60. It does not set readiness counters. The first extension reached missing factory calibration memory1FF0F44A; later explicit synthetic calibration1500 and ADC sample1024 allow native readiness processing. These numbers are **not current-unit evidence**. Earlier frontiers remain in `startup-before-adc-model/` and `startup-before-calibration-model/`.

**PROVEN:** native DSP upload next blocked in SPI2 RX wait23414. Actual SPI2 RX DMA IRQ30 and its exact POP-R4/EXC_RETURN are now modeled. TX completion disables its modeled stream; RX writes honor MSIZE/MINC. An initial wrong contiguous-write model corrupted a fixed RX discard destination when MINC was disabled: that attempt is preserved under `startup-spi-increment-model-invalid/` and is excluded as invalid model evidence, not a candidate bug. Valid earlier frontier is `startup-before-spi-model/`.

**UNKNOWN:** latest run stops at `{s['frontier']['pc']}` after {s['instructions']:,} native instructions in the polled SPI2 full-duplex loop37960. Actual pointer chain is20000264→20003414→40003800; SR40003808 TXE(bit1)/RXNE(bit0) predicates and data-register behavior are not yet modeled. It waits during DSP startup. This is the exact remaining mechanism; do not claim a hardware hang, synthesize higher-level readiness, or count it as completed USB-ready/capture coverage.

**PROVEN:** {a['observed_request_count']} allocation requests are enumerated in {link('allocation-coverage.json')} with native call sites, arguments and instruction indices; heap cursor `{s['heap_cursor']}`, cap `{s['heap_limit']}`. Native scatter/constructor and nonoverflow round-four boundary/exhaustion cases pass in {link('heap-reset-tests.json')}. Rejected exhaustion stops at BKPT1D7F4; it is not graceful NULL behavior. Diagnostic helpers add no heap allocation. Raw/packet buffers are live Main stack; no fixed RAM allocation was introduced.

**STRONG INFERENCE:** future ordinary calls through the same bounded allocator cannot cross the cap while arithmetic stays in its qualified domain. This alone is not complete owner/caller enumeration and says nothing about arbitrary-size overflow, other allocators/direct writes, or remaining stack consumers.

**UNKNOWN:** later allocations during remaining initialization, USB readiness and diagnostic lifetime are not reached continuously. Reference fixture cursor44D68 and partial fresh-boot cursorFE58 are distinct. Neither proves current-unit final headroom. Heap/stack margin on hardware is separately **UNKNOWN (HARDWARE-ONLY)**.

Continuation scripts: {link('startup_continuity.py')}, {link('startup_adc_completion.py')}, {link('startup_spi_completion.py')}. Current live emulator is not serialized by the SRAM dump alone; the saved register subset is not a complete peripheral/scheduler checkpoint. The runner currently replays the prefix to resume in-memory state. Any future rerun should be only for this pending gate, not already passed investigations.
''')
write('install-uploader.md',f'''
# Exact identity, updater and rollback review

**PROVEN:** file-first independent decode and CRC equal the new BIN; 1,558 byte differences are classified in development-identity.json. MarkerN63DEV changes the native38-byte compared header at080101C8..080101EE; same-version header equality is not relied on to trigger installation.

**PROVEN in inherited explicit RTOS/peripheral models:** actual installed B1.3→development candidate, candidate→official4486 and candidate→B1.3 all install exact incoming bytes, with silent_noop=false. All selected application-staging instructions are checked against the actual installed source image, and actual RAM selector20003CC8→20003C88 is recorded. {link('install-validation.json')} links summarized results; full operations and native summaries remain available.

All three transitions exclude internal bootloader00000..10000, use application internal flash10000..80000, preserve sentinels and have zero NOR write/erase overlap with81000..81017 and82000..82200. Metadata erase80000..81000 is exclusive at81000. Staging erases end at66000 for candidate,4D000 for official,6B000 for B1.3. These are offline updater-path results, not hardware rollback tests or complete cold-boot preservation proof.

**PROVEN:** review uploader `{u['uploader']}`, SHA-256 `{u['uploader_sha256']}`, derived from exact reference ct_uploader.html SHA `{u['upstream_sha256']}`; upstream has no explicit semantic version. Its allowlist is narrowed to exactly the new candidate SYX and the two pinned rollbacks. Product0164, manufacturerF0 00 20 29 00, command order71/7C/72*/73, decoded size and MPEG-2 CRC checks remain. Marker and native header comparison are separately validated by the install replays.

**PROVEN:** {link('uploader-tests.json')} executes the exact HTML parser in isolated Node VM, decodes all three files, verifies hash membership and tests MIDI/identify/send guards. Mock navigator MIDI call count=0. This is not a browser or device test. `PREFLIGHT_QUALIFIED=false` deliberately locks all three live handlers. Future approval requires a separately reviewed enabled copy with a new recorded hash; no enabled uploader is delivered for this ineligible image.

Rollback official SYX SHA bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd; B1.3 SYX SHA6f07376b5983a5e0350d4883ae9ed57a69bc735320afde9f43ca75017b8e8736. Files are in rollback/. Local manifest/file matching is **PROVEN**; independently authenticated vendor-origin acquisition of the local official file remains **UNKNOWN**, unchanged from Phase62.

No uploader/browser was opened, no port enumerated, and no transmission occurred. Existing Windows/MSD operational cautions and H4 full physical power-cycle requirement are unchanged; no OS storage setting was changed.
''')
write('CHECKPOINT.md',f'''
# Saved narrow-closure checkpoint

Current image is immutable for the passed results unless intentionally starting a new development iteration. Identity: BIN `{c['BIN_sha256']}`, SYX `{c['SYX_sha256']}`. No hardware eligibility.

Completed: independent file decode/CRC/diff, seven reservation cases,28 native cases,13 status/mount cases,31 DMA ownership cases,32 host mocks, reset/heap boundary cases, three native exact-image install/rollback replays, locked uploader/parser binding. Each result is persisted. Historical Phase61/62 unchanged.

Pending only: native polled SPI2 startup exchange37960 (SR40003808); subsequent same-state USB-ready→query→authorization→raw continuity; remaining postboot allocation/stack coverage. No Plaits work or new NOR research.

`startup_spi_completion.py` is the latest bounded runner. It currently must replay its prefix because SRAM+selected-register dumps do not serialize a complete live emulator. Preserve all frontier directories. `startup-spi-increment-model-invalid/` is explicitly invalid and excluded. Do not substitute `dma_regression.M`/`native_regression.N` RAM into the continuous startup runner.

Successful long install/rollback evidence needs no rerun if both selected image hashes stay unchanged. `finish_evidence.py` verifies saved results and historical hashes without rerunning those tests. `write_reports.py` regenerates these reports from those results. Both intentionally retain UNQUALIFIED until missing gates are implemented and actually pass; manually changing the verdict file is not qualification.

FINAL PREFLIGHT CLOSURE = UNQUALIFIED
''')
write('README.md',f'Phase63 development checkpoint remains UNQUALIFIED. No hardware action. Read {link("findings.md")} and {link("CHECKPOINT.md")}.')
# Correct complete listings: Cortex-M MRS/MSR require Capstone MCLASS mode.
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);image=(O/(c['candidate']+'.bin')).read_bytes();meta=load('construction.json')
for n,d in meta['components'].items():
 at=int(d['address'],16);b=image[at-0x08010000:at-0x08010000+d['bytes']];ins=list(md.disasm(b,at));assert sum(i.size for i in ins)==len(b),n
 write('reviewed-'+n+'.asm','\n'.join(f'{i.address:08X}: {i.mnemonic} {i.op_str}' for i in ins))
note=R/'notes/qspi82000-hardware-readiness.md';raw_note=note.read_bytes();tag='<!-- phase63-current -->'
# Existing historical note mixes legacy and UTF-8 bytes; preserve it byte-for-byte.
if tag.encode() not in raw_note:note.write_bytes((tag+'\n**Phase63 update: UNQUALIFIED.** Targeted mount/status/DMA fixes pass scoped regressions; continuous startup and complete postboot allocation coverage remain open. All live tools are locked. See [Phase63 findings](<'+(O/'findings.md').as_posix()+'>). Historical Phase61 and Phase62 images remain ineligible.\n\n').encode('utf-8')+raw_note)
manifest=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name!='SHA256SUMS.txt':manifest.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(O).as_posix())
(O/'SHA256SUMS.txt').write_text('\n'.join(manifest)+'\n')
print('Reports and checkpoint written; manifest entries',len(manifest))
