"""Finalize frozen-image preflight results, including demonstrated FAIL gates.
No firmware changes or experimental reruns. Writes Phase62 evidence only.
"""
from pathlib import Path
import sys,json,hashlib,struct
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase61-final-geometry-gated-candidate'
def J(n):return json.loads((O/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def W(n,s):(O/n).write_text(s.strip()+'\n',encoding='utf8')
def L(n):return '['+n+'](<'+(O/n).as_posix()+'>)'
def main():
 c=J('frozen-candidate-identity.json');continuity=J('continuity-status.json');st=J('stack-dma-tests.json');dma=J('dma-ordering-probe.json');hr=J('heap-reset-tests.json');host=J('live-host-tests.json');rb=J('rollback-provisioning.json');modes=J('mount-state-protocol-tests.json')
 assert J('corrected-reservation-tests.json')['passed'] and J('native-tests.json')['all_passed']
 assert not modes['passed'] and not dma['software_no_return_invariant'] and not continuity['continuity_complete']
 for ext,key in [('syx','SYX_sha256'),('bin','BIN_sha256')]:assert sha(O/(c['candidate']+'.'+ext))==c[key]
 preserved=0
 for line in (P/'SHA256SUMS.txt').read_text().splitlines():h,n=line.split('  ',1);assert sha(P/n)==h,n;preserved+=1
 archive=O/'checkpoint-before-resume-report';archive.mkdir(exist_ok=True)
 for n in ('findings.md','README.md','PRE-FLASH-CHECKLIST.txt','SHA256SUMS.txt'):
  if not (archive/n).exists():(archive/n).write_bytes((O/n).read_bytes())
 identity=f'''| Frozen corrected artifact — NOT QUALIFIED | Bytes | SHA-256 |
|---|---:|---|
| {c['candidate']}.syx | {c['SYX_bytes']} | `{c['SYX_sha256']}` |
| {c['candidate']}.bin | {c['BIN_bytes']} | `{c['BIN_sha256']}` |

CRC-32/MPEG-2 **BF2E8F22**; application base08010000/end-exclusive08075100; image headroom44800 bytes; compared-header markerN62RSV. These are image bounds, not hardware RAM margin.
'''
 # Fresh actual selector witness from this corrected-image install replay.
 b=J('b13-to-candidate-summary.json');w=b['actual_RAM_selector_witness'];assert len(w)==1
 assert w[0]['table_address']=='0x20003cc8' and w[0]['selected_pointer']=='0x20003c88' and w[0]['index']==0
 sys.path.insert(0,str(R/'tools'));from ct_data_decode import decode as initialized
 sys.path.insert(0,str(R/'builds/phase43-hardware-test-candidate'));from independent_validate import decode
 b13,_,_=decode((O/'rollback/circuittracks-B1.3-manifest-matched.syx').read_bytes());init,_=initialized(b13)
 assert bytes.fromhex(w[0]['selector_record_bytes'])==init[0x3c88:0x3cd8]
 base,cap=struct.unpack_from('<II',init,0x3c90);assert base==0 and cap==0x80000
 selector=dict(confidence='PROVEN',installed_image_sha256=hashlib.sha256(b13).hexdigest(),actual_native_witness=w,independent_B13_initialized_data_match=True,selector_base=hex(base),selector_capacity=hex(cap),all_staging_instruction_bytes_match_actual_installed_image=b['actual_installed_instruction_bytes_checked'])
 (O/'b13-selector-confirmation.json').write_text(json.dumps(selector,indent=2)+'\n')
 transitions=[]
 for name in ('b13-to-candidate','candidate-to-official','candidate-to-b13'):
  t=J(name+'-summary.json');ops=J(name+'-operations.json')
  assert t['accepted'] and t['actual_install_performed'] and not t['silent_noop'] and t['incoming_image_sha256']==t['final_installed_sha256']==t['staged_image_sha256']
  assert ops['bootloader_unchanged']
  if name=='b13-to-candidate':assert t['incoming_SYX_sha256']==c['SYX_sha256'] and t['incoming_image_sha256']==c['BIN_sha256']
  else:assert t['installed_before_sha256']==c['BIN_sha256']
  for a,z in ((0x81000,0x81017),(0x82000,0x82200)):
   assert not [x for x in ops['operations'] if x['kind'] in ('ERASE','WRITE') and int(x['start'],16)<z and int(x['end_exclusive'],16)>a]
  assert all(0x08010000<=int(x['start'],16)<int(x.get('end_exclusive',x['start']),16)<=0x08080000 for x in ops['internal_operations'] if x['kind'] in ('ERASE','WRITE'))
  transitions.append(dict(transition=name,accepted=True,silent_noop=False,installed_sha256=t['final_installed_sha256'],bootloader_unchanged=True,option_byte_operations=0,identity_overlap=0,coeff_overlap=0,erase_ranges=t['external_erase_ranges'],program_ranges=t['external_program_ranges']))
 (O/'corrected-install-validation.json').write_text(json.dumps(dict(confidence='PROVEN',candidate=c['BIN_sha256'],transitions=transitions,scope='Native selected installed image; task/peripheral/CRC/flash seams explicit, NOT hardware flash'),indent=2)+'\n')
 W('startup-coupled-continuity.md',f'''# Corrected startup→coupled continuity — FAIL

The frozen corrected image was installed **before** any startup instruction. Native scatter/constructor reservation, scheduler/task execution and first mount ran in one live Unicorn instance. No running-RAM or exported-geometry fixture was substituted into this continuity test. The prior prepared-fixture coupled replay is used only for separate stack tests, never to close this gate.

| Milestone | Actual12-byte record / result |
|---|---|
| Before constructor reservation | Reinitialized to`000000000000000000000000` by native init; reset/heap suite records allocator ordering |
| First snapshot committed at0801AE14 |`110000000180003480908F01`|
| Next normal SD mount begins |`1D0000000180003480908F01` — invalidated by0806CF26|
| USB-ready input-service boundary | NOT REACHED in bounded continuation; no fabricated record |
| Geometry export | NOT REQUESTED through an invented ready fixture |
| Authorization | NOT PERMITTED/NOT EXECUTED in this continuity run |
| Raw capture start | NOT REACHED; no raw request is substituted |

**PROVEN implementation defect:** shared call site0801AE02 invokes mount_begin08075014 for both NORFS20000AB0 and SDFS20001B04. begin0806CF00 does not filter itsR0 filesystem argument: after NOR commitsVALID11, the SD mount takes its nonzero-control path and writes1D at0806CF26. This is the **first** invalidation in the trace, before later modeled drive0 remounts. It does not require guessing physical timing. Normal SD handling is not a new NOR mount epoch, so the NOR diagnostic gate is incorrectly invalidated by an unrelated filesystem. Required correction is a scoped NOR-owner predicate, not disabling remount invalidation generally.

Later drive0 re-registration/slow mount/invalidation also occurs under the synthetic incomplete filesystem model; that needs separate interpretation after fixing the first definite SD-owner error. It must not be silently ignored to forceVALID.

The second bounded native continuation executes{continuity['instructions']} instructions and stops at{continuity['frontier']['pc']} ({continuity['frontier']['message']}). The original10000 aggregate-PC visit guard stopped inside a bounded byte-clear loop224A8; that initial attempt is preserved undercontinuity-initial-attempt. Only that finite-loop guard was relaxed; no readiness or success state was manufactured. The later instruction frontier is a **model completion limit**, not proof of a hardware hang.

`continuity-frontier-sram.bin` and selected registers/model events are persisted. The emulator retains its exact live RAM/registers throughout each run, but no successful startup-to-coupled handoff is claimed and the disk snapshot is not claimed to contain a serializable complete peripheral/scheduler model. All inherited JEDEC/BPB/clock/SD/completion seams are explicit in the runner and event log.

Evidence: {L('startup_continuity.py')}, {L('continuity-status.json')}, {L('continuity-startup-frontier.json')}, {L('continuity-frontier-sram.bin')}. Candidate unchanged.
''')
 mainmin=min(int(x['details']['minimum_SP']['Main'],16) for x in st['cases']);stormin=min(int(x['details']['minimum_SP']['Storage'],16) for x in st['cases'])
 W('final-stack-audit.md',f'''# Frozen Phase62 stack and DMA-lifetime audit

**PROVEN new measurements**, not reused Phase42/43/61 numbers:15 corrected-image cases execute the native Main/Storage/QSPI-IRQ/USB model. The fixture is a separately authenticated running-RAM state, so these results **do not close startup continuity**.

| Task | Stack low/high guards | MinimumSP | Margin above low4-byte guard | Used below high guard |
|---|---|---|---:|---:|
|Main|2000775C /20008358|{mainmin:08X}|{mainmin-0x2000775c-4}|{0x20008358-mainmin}|
|Storage|20008D44 /20009240|{stormin:08X}|{stormin-0x20008d44-4}|{0x20009240-stormin}|

Main deepest observedPC0802214C,LR080221A9: diagnostic admission→raw→packet send→USB/router/ring work, ending22190..221A4→2214A. Storage deepestPC08022748,LR080376E1: worker→backend read→37430/controller→3769C command issue→22746. JSON records exact recent instruction paths and LR/PC at each new minimum; these are observed paths, not a claim of a complete symbolic unwind or every possible callee.

The raw function pushes20 bytes then subtracts260 bytes:280 bytes total local/save contribution. Its dedicated64-byte raw buffer is frame+192..+255; packet is+16, guards include+12,+180,+188,+256. It borrows no parser buffer. Caller frames and stock callees contribute the remaining measured depth. Bounds/neighbor/canary checks pass for the measured cases.

Normal completion, actual backend-busy error, disconnect after completed read, and TEF/missing completion at globalchunks0/4/8 are exercised. TEF/missing completion leave Main parked and the request/semaphore retained through lifecycle timeout. Late completion is delivered to the **same** request; it releases that request without a new read and cannot replaceFAILED. This is the15-case normal/fault-model result.

## Required unconditional DMA return invariant: NOT PROVEN / failing countermodel

Prior normal models supplied data, NDTR=0 and DMA.EN=0 before the QSPI TCF IRQ. That is a shared completion-ordering assumption. The new adversarial probe leaves DMA.EN=1,NDTR=64,destination20008258 (the raw stack buffer), then delivers the real native QSPI completion IRQ. Main returns, the request clears, semaphore releases andSUCCESS14 is published **while those DMA fields still target the old stack buffer**. Therefore the software does not independently enforce the requested no-return-with-pending-DMA invariant.

This is **PROVEN in the explicitly injected register ordering**. Whether this ordering can arise on this physical QSPI/DMA implementation is **UNKNOWN**; it is not described as an observed hardware overwrite. Acceptance requires either a source-supported hardware completion-order proof or a software lifetime guard plus adversarial-order tests. Do not treat the successful normal model as that proof. No forced DMA/semaphore cleanup was attempted.

Evidence: {L('stack-dma-tests.json')}, {L('stack_dma_tests.py')}, {L('dma-ordering-probe.json')}, {L('dma_ordering_probe.py')}.
''')
 W('heap-reservation-audit.md',f'''# Heap / reservation — corrected image

Native constructor entry0805B958 branches through08075000 to initializer0806BD00 **before** original constructors. With scatter-initialized limit20044E58/cursor20006A58, init clears all12 bytes before aDMB and publishes limit20044D70. Cursor is unchanged by reservation. The high232-byte reservation consists of existing220-byte MasterFX plus12 diagnostic bytes. Native constructors then advance cursor to20007750; modeled margin at that point is251424 bytes, not8 bytes.

**PROVEN provenance of20044D68:** it comes from public/reference running-RAM dump`ram_dump_firmware_0x08037988.bin`, SHA-256`{hr['reference_RAM_sha256']}`, at dump offset2B48. It is the old running fixture's cursor and leaves8 bytes toD70. It is **not** a measurement of this unit's fresh boot and is not produced by current native startup. The new partial startup frontier reaches cursor2000FE58 with limit20044D70:216856 modeled bytes remain, at an incomplete-boot boundary. Full final-boot/postboot demand is not qualified.

Native allocator1D7D0→1D7D8 rounds to4-byte alignment, compares new cursor to the live limit and stores only when it fits. The native exhaustion branch isBKPT at0801D7F4, not a gracefulNULL allocator return. New boundary tests accept two4-byte allocations up toS, reject4 bytes atS and reject9(round12) bytes with8 remaining, and preserve the record/cursor on those failures.

For ordinary nonoverflow requests through this allocator, allocations ending beyondS are rejected; the record cannot be allocated by those tested paths. This is **not** exhaustive proof of all postboot call sizes, integer-overflow inputs, arbitrary pointer writes or hardware headroom. Physical RAM/stack margin remains UNKNOWN. No complete postboot heap proof is manufactured while continuity fails earlier.

The7 reservation-negative tests and corrected28-case regression remain qualified in their narrow scope and were **not rerun** by this continuation. Evidence: {L('heap-reset-tests.json')}, {L('heap_reset_tests.py')}, {L('continuity-status.json')}, {L('corrected-reservation-tests.json')}.
''')
 # Validate explicit arithmetic used in prose.
 assert 0x20044d70-0x20007750==251424 and 0x20044d70-0x2000fe58==216856
 W('reset-state.md',f'''# Reset / power-cycle state

Four new native tests start with zero, garbage, FAILED15 or SUCCESS14 high-SRAM records, then execute the corrected application's real scatter initializer and constructor hook. Scatter resets allocator cursor/limit to20006A58/20044E58 but leaves the high record bytes temporarily intact. Constructor init then zeroes all12 bytes and reserves the region; geometry validity and authorization are false in all cases.

The same reset entry/initialization code is used for normal cold entry, software-reset entry and watchdog-reset entry; these tests model code execution, **not** electrical reset causes or peripheral reset effects. Full power removal is represented by unknown initial SRAM followed by the same explicit initialization, not by assuming SRAM cells retain or clear a particular value.

Thus FAILED/SUCCESS do **not** survive completed normal scatter+constructor initialization. A warm reset can rearm the software lifecycle and eventually permit another first-epoch capture. The record itself is not a power-cycle detector or a persistent retry lock. Existing durable host markers must not be deleted merely because the application rebooted. A software/watchdog reset is not evidence that a stuck Storage/DMA lifetime is safe.

**FULL PHYSICAL POWER CYCLE IS MANDATORY after any failed/uncertain raw-capture attempt.** No in-session retry, second Storage request, semaphore release or forced DMA cleanup. Host marker rearming requires separately established physical power removal; this tool supplies no automatic reset/rearm path. Evidence: {L('heap-reset-tests.json')}; no hardware reset performed.
''')
 W('b13-updater-confirmation.md',f'''# Actual B1.3 updater and selector — PROVEN scoped

The new B1.3→frozen-corrected replay loads installed image SHA-256`{b['installed_before_sha256']}`, not SC35D8 or4486. Every executed application staging instruction is checked byte-for-byte against that actual installed image. The incoming SYX is the frozen corrected file, and exact installed hash is`{b['final_installed_sha256']}`.

At executed native080390D0, actual registers give index0,R2=20003CC8 and selected pointer20003C88. The actual80 bytes at20003C88..3CD7 equal independently decoded B1.3 initialized data. Selected record gives NOR interface-pointer address20006968, service20003CD8, base0,capacity80000. This is an actual RAM selector witness, not a table assumed from stock names. The previously saved native B1.3 decompressor evidence independently authenticates the initialized-data source.

An instrumentation metadata mistake was caught during review:08039180 is **updater code**, not the selector table. The initial witness-less summary labeled a code-window hash as a selector-table hash. That initial summary is preserved with`code-window-mislabeled` in its filename and must not be used for selector proof. The updated B1.3 replay names it an updater code window and supplies the actual20003CC8 witness. The initial two rollback summaries retain the old helper field names; those fields are explicitly ignored for selector proof. Their exact-image/overlap results remain valid.

Evidence: {L('b13-selector-confirmation.json')}, {L('b13-to-candidate-summary.json')}, {L('corrected_install_replay.py')}, {L('corrected-install-validation.json')}. Peripheral/RTOS/UI/CRC/flash completion seams remain modeled; this is not a physical update.
''')
 W('windows-msd-risk.md','''# Windows / MSD automount — scoped risk decision

Existing Phase46 initialized callback/native SCSI evidence remains applicable to the unchanged SCSI/class/callback code in this corrected image: application startup setting bit17 can register an MSD class; it is not universally safe to assume MIDI-only application enumeration. The initialized backend at20003788 returns write-protected through08057E48, and normal state0 WRITE10 admission rejects before the lower writer. Bootloader's normal registered configuration has Audio/MIDI and no class8 MSD.

Therefore: **no accepted writable volume is demonstrated on the normal initialized application SCSI path**; conditional read-only MSD exposure is possible from retained settings. This is not a universal malformed-BOT/host-write-isolation theorem. The lower write callback exists, and all possible transport states have not been re-proved here. Unknown actual settings must not be replaced with a guessed MIDI-only descriptor.

Safest future setup: use the established MIDI-only path, do not enable/toggle MSD or send vendor-mode commands, do not browse/format/repair any volume, and stop if unexpected storage exposure occurs. Prefer no filesystem mount at all. No Windows setting is changed by this phase.

Conditional preflight defense, BEFORE connecting a separately authorized device: record current automount policy in an elevated DiskPart session (`automount`), then use `automount disable` if required by that chosen test environment. Alternatively `mountvol /N` disables automatic mounting of new basic volumes. Record/restore the previous policy later; do not blindly enable it. These are host-wide configuration changes, not device read-only commands, and are not executed here. They do not guarantee isolation of already-known/already-mounted volumes or all low-level writes. Do not use global mount-point scrubbing as a substitute for a planned isolated environment.

Microsoft definitions: [DiskPart automount](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/automount), [mountvol](https://learn.microsoft.com/windows-server/administration/windows-commands/mountvol). These support the precise new-volume mounting limitation, not a universal storage write block. Project evidence: builds/phase46-msd-filesystem-closure/msd-reachability.md and initialized-ram-callback.md; no device/port inquiry was performed.
''')
 W('timeout-ordering.md',f'''# Timeout ordering and one-shot boundaries

| Boundary | Value / interpretation |
|---|---|
| Device lifecycle |5000 unsigned clock ticks from active admission; wrap arithmetic covered by retained corrected native tests |
| Host pre-send preparation |10 monotonic seconds; failure before send transmits0 diagnostic messages and burns no marker |
| Host geometry |10 monotonic seconds from first attempted geometry transmission |
| Host authorization transmission |2 seconds measured around qualified driver send; driver's own bounded send remains in the pinned transport |
| Host raw stage/EOS |10 seconds from authorization attempt, including send; complete receiver still observes the absolute boundary for duplicates/trailing packets |

If the device counter advances at1ms/tick, its lifecycle deadline is nominally5s and precedes the10s host raw deadline. Physical scheduling/counter progress is unmeasured, so unconditional real-wall-clock ordering is **UNKNOWN**. Safety cannot depend on which fires first. Preauthorization device lifecycle timeout is inactive; host geometry timeout is not a device Storage cancellation.

The host creates/fsyncs its durable marker immediately before the first actual diagnostic send attempt; driver-send uncertainty counts asPOST_SEND. Marker-write failure before send removes only its own incomplete marker. No port/open/preparation failure sends SysEx or consumes a marker. Existing markers block a second launch before inventory/open. After any post-send failure there is no retry or cleanup command and the marker remains; physical power cycle is mandatory before any later attempt.

A successful workflow has2 diagnostic transmissions (geometry0E, authorization0F), not a capture retry. Geometry-only/unsafe stop sends1 and no raw authorization. Device capture contains multiple fixed64-byte chunks; these are parts of one authorized capture, not host resubmissions. Host failure cannot undo already-authorized device work and never attempts forced cancellation.

15 corrected-image ordinary/fault completion-order tests keep Main parked while the failed read request remains outstanding. **The separate TCF-before-DMA-release probe fails the unconditional no-return invariant**: native Main can return with DMA still configured for its former raw stack buffer. Do not cite the nominal deadline table or normal-model successes as closure of that issue. See {L('final-stack-audit.md')} and {L('dma-ordering-probe.json')}.
''')
 W('mount-failure-states.md',f'''# Mount / geometry protocol gate — FAIL

New exact-image native queries cover BOOT0, MOUNTING16, INVALID1D, FAILED15 and VALID11. BOOT/MOUNTING/INVALID/FAILED all emit **zero response packets**, preserve the record and submit no raw read. VALID returns the39-byte geometry response and moves to EXPORTED with session binding.

Thus the actual device protocol cannot distinguish NOT_READY, INVALID and FAILED to a host: they are identical silence. A timeout cannot truthfully be labeled NOT_READY. The host mock suite preserves this mismatch; it does not manufacture status packets that the frozen firmware cannot send. Lack of raw authorization means no raw-capture attempt is made, but the already-sent geometry session's durable marker remains and ambiguous silence isPOST_SEND failure, requiring power cycling. This does **not** satisfy a distinct successful NOT_READY response/nonburning-status workflow.

First successful mount/compact geometry is covered by current startup; first mount failure/nonqualifying geometry takes the existing terminal1D path, with no valid snapshot. Reservation-absent behavior is the already-passed7-case gate, not rerun. Retained28 native cases cover invalid geometry, remount/invalidation, wrong epoch and malformed authorization. The new continuity trace reveals a separate erroneous invalidation by the ordinary SD mount. A host cannot repair that by assuming silence means valid or overwriting state.

UNSAFE is a local host veto, not a permission to raw-read. AUTHORIZED is inferred only after a validated raw reply, not from an invented device ACK; authorization transmission itself is labeledAUTHORIZATION_SENT. FAILED cannot currently be queried as a distinct device reply. The successful compactD4000 format maps above the two target ranges; the mock unsafe case injects a policy veto and is not claimed as a native unsafe-volume discovery.

Required closure is a real, testable no-raw-read status response contract plus NOR-specific mount ownership, followed by fresh corrected-image qualification. Neither change was smuggled into the frozen image. Evidence: {L('mount-state-protocol-tests.json')}, {L('resume_checks.py')}, {L('continuity-startup-frontier.json')}, {L('live-host-tests.json')}.
''')
 table='| Mock | Messages attempted | Raw authorization attempted | Result |\n|---|---:|---|---|\n'+'\n'.join(f"|{x['case']}|{x['result']['diagnostic_messages_attempted']}|{x['result']['raw_authorization_attempted']}|{x['result']['status']}|" for x in host['cases'])
 W('live-host-tests.md',f'''# Runnable Windows host and mock validation

`live_host.py` implements non-sending list, geometry-only and one-shot fixed capture commands using a byte-identical copy of the previously qualified WinMM transport. Imports/help do not load WinMM; live list is never invoked here. Live geometry/capture is locked unless preflight-verdict.json isPASS. It remains **NOT QUALIFIED** because this image fails startup/status/lifetime gates. No CLI bypass flag is exposed.

The injected backend/core has25 passing mock assertions: port ambiguity/open/preparation failures send0 and create no marker; transmitted attempts retain their marker on failure and block another launch before touching ports. Epoch/CRC/order/duplicate/length checks use the existing independent codec. Reconstructed files are published via one atomic directory rename only after a complete receiver and full EOS boundary. The pinned transport sends actual Windows SysEx only when a future qualified live command is explicitly invoked; none was invoked.

{table}

Important scope: the3 NOT_READY/INVALID/FAILED cases deliberately reproduce actual device silence and yieldFAILED_POST_SEND. Those are successful **fail-closed host assertions**, not a passing protocol-state distinction gate. The malformed-auth mock models no reply after rejection, while native malformed authorization rejection is supplied by the retained28-case test. The unsafe mock injects a policy veto; it is not a new unsafe native geometry result. The second-launch marker check is executed after every transmitting case. No actual ports were listed/opened.

This is a real CLI implementation with a safety lock, not a qualified final live workflow. Evidence: {L('live_host.py')}, {L('live_host_tests.py')}, {L('live-host-tests.json')}, {L('ctremote_transport.py')}. Its actual required device-status branch remains impossible to qualify against the frozen protocol. No alternate invented on-wire status format is accepted.
''')
 rbtable='| File | Bytes | SHA-256 | Provenance |\n|---|---:|---|---|\n'+'\n'.join(f"|{x['filename']}|{x['bytes']}|`{x['sha256']}`|{x['source']}|" for x in rb['artifacts'])
 W('rollback-manifest.md',f'''# Locally provisioned rollback chain

Files are physically present underrollback/ and pinned below. They were not sent/opened in a browser. The uploader HTML was copied byte-for-byte from the public reference repository, which was not modified.

{rbtable}

B1.3 SYX independently decodes to BIN`2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41`, the actual installed image used by the new B1.3 updater replay and the exact incoming image in rollback. Its published SYX manifest hash matches exactly. Official4486 decodes to BIN`b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da`.

Official source provenance: **UNKNOWN for authenticated Novation-origin acquisition**. This phase inspected the existing reference/Phase43 files and baseline/provenance notes and found matching local bytes, not an independently authenticated Novation download record. No internet firmware download is substituted as if it were already available evidence.

The pinned reference uploader allowlists official4486 and B1.3, but **does not allowlist this corrected candidate**. Therefore rollback tooling is pinned, while a candidate-update uploader is not admitted. Do not weaken the allowlist or register a failing candidate merely to report readiness. Any future corrected candidate needs a reviewed exact-hash uploader binding. No uploader handshake or physical rollback flashing is claimed.

All3 exact frozen-image update/rollback replays pass: exact installed images, no silent no-op, bootloader equality, no internal operations outside application flash and zero external mutation overlap with either target. The modeled internal-flash calls never reach option bytes; this is not a physical option-byte measurement. See {L('corrected-install-validation.json')}, {L('rollback-provisioning.json')} and the3 transition summaries/operation logs.
''')
 W('recovery-rehearsal-status.md','''# Recovery rehearsal — evidence boundary

User-reported physical evidence only: recovery/bootloader entry can be reached; the device can exit and boot B1.3 normally. No new physical rehearsal occurred.

Do NOT claim uploader handshake tested, candidate update tested, rollback flashed or a non-booting corrected image recovered. Exact offline install/rollback replays are model evidence, not those physical tests. No permanent-brick probability is invented. No bootloader or option-byte modification is performed by this phase.
''')
 verdict=dict(confidence='PROVEN',verdict='FAIL',candidate_BIN_sha256=c['BIN_sha256'],candidate_SYX_sha256=c['SYX_sha256'],candidate_frozen=True,reservation_guard_reused_pass=True,native_28_case_evidence_preserved=True,continuity_gate='FAIL: SD mount invalidates NOR record',device_status_gate='FAIL: non-VALID states indistinguishable silence',software_DMA_return_gate='FAIL under explicit adversarial TCF-before-DMA-release model; physical ordering UNKNOWN',new_stack_cases=15,host_mock_assertions=25,live_host_qualified=False,rollback_artifacts_provisioned=True,candidate_uploader_allowlisted=False,install_rollback_replays_pass=3,full_startup_USB_continuity_complete=False,hardware_access=False,MIDI_ports_opened=0,firmware_transmitted=False,phase61_checksum_entries_preserved=preserved)
 (O/'preflight-verdict.json').write_text(json.dumps(verdict,indent=2)+'\n')
 W('findings.md',f'''# Resumed Phase62 — frozen corrected candidate REJECTED for preflight

**FINAL PREFLIGHT CLOSURE = FAIL. DO NOT FLASH.** The earlier reservation fix remains qualified in its narrow scope. This continuation did not restart/repeat the7 reservation cases or28 native suite and did not alter either candidate. Required new tests found further concrete failures, so the corrected image cannot be promoted.

## Frozen identity

{identity}
Original Phase61 remains permanently **SUPERSEDED / FAILED RESERVATION TEST / DO NOT FLASH**. Its original bytes/evidence remain unchanged; all{preserved} Phase61 manifest entries still verify. The corrected image is **UNQUALIFIED UNTIL PREFLIGHT COMPLETES**, and this run has failed required gates. No future-final designation is made.

## REAL BLOCKERS REMAINING

1. **PROVEN in native startup:** shared mount_begin also handles SDFS20001B04 and invalidates the already committed NOR record at0806CF26. Snapshot`110000000180003480908F01` becomes`1D0000000180003480908F01`. This is an owner predicate defect; it cannot be repaired by a host fixture. Later native drive0 remounts also require interpretation without disabling the intended invalidation policy.
2. **PROVEN native protocol failure:** NOT_READY0/16, INVALID1D and FAILED15 queries emit identical silence. The required distinguishable status/nonburning readiness contract is absent. Host code cannot truthfully decode a nonexistent response.
3. **Requested unconditional stack-DMA invariant fails an explicit countermodel:** with TCF delivered before DMA.EN/NDTR are cleared, native Main returnsSUCCESS while DMA.EN=1,NDTR=64 and destination remains the former stack raw buffer. Physical occurrence of that ordering is UNKNOWN; normal tests assumed it away. Need a valid completion-order proof or explicit software ownership enforcement, not an asserted hardware-safe unwind.
4. Final live workflow cannot qualify until those firmware/continuity contracts are resolved. A real locked Windows utility and25 mock assertions now exist, but the candidate cannot satisfy its required status path. Pinned rollback files/uploader are provisioned; the reference uploader does not allowlist this failing candidate, and no candidate-update uploader is admitted.

## Completed independent checks

- New corrected-image native startup continued beyond the snapshot without substituting RAM/register state; it exposed the SD-owner defect. Full USB-ready→export→auth→raw continuity is **not** claimed. The1,104,592-instruction bound stops in the native continuation; this is a model frontier, not proof of a real hardware hang.
-15 new stack/DMA cases pass under their declared normal/late-completion model. New independent ordering probe falsifies the broader software invariant; these results are deliberately reported separately.
- Native scatter/constructor tests show FAILED/SUCCESS are reset and authorization cleared at each normal initialized boot. Warm reset can rearm the lifecycle; full physical power cycle remains mandatory by H4, enforced operationally by durable host markers rather than by a RAM power-cycle detector.
- New allocator boundary/exhaustion tests establish nonoverflow bounds andBKPT failure. CursorD68 is traced to the reference running-RAM dump, not the current unit. Full postboot/hardware headroom is not promoted from that fixture.
- Exact B1.3→corrected, corrected→official4486 and corrected→B1.3 replays all pass: exact installed images, no no-op, untouched bootloader, no option-byte operations and zero target write/erase overlaps. Actual B1.3 staging instructions and actual RAM selector at20003CC8 are authenticated; a code-window/table metadata labeling error is explicitly corrected/disclosed.
- Rollback SYXs and exact reference uploader are locally pinned. Official Novation-origin acquisition authentication remainsUNKNOWN; local matching hashes are not invented origin proof.
- Windows MSD risk, host timeout/attempt semantics and recovery evidence limits are documented without a device/port inquiry. Help/import/fake transport only; no live listing/open/send was run.

## CHEAP CHECKS / FIXES REMAINING

Correct NOR-only mount ownership and define native status responses, then use a **new identity** and rerun affected integration/continuity tests. Resolve the DMA lifetime ordering gate without forced unsafe cleanup; rerun adversarial ownership cases. Complete the actual startup→USB-ready seam with declared event models, all milestone records and final postboot allocation/path coverage. Bind the eventual passing hash to a reviewed uploader; qualify the live host against actual device responses rather than silence mocks. These are specific failed/unclosed gates, not permission to restart broad reverse engineering or repeat already-passed arithmetic/ports.

## HARDWARE-ONLY UNKNOWNS

Real boot/timing/USB/Storage/DMA behavior, actual geometry/data and RAM margin, hardware faults and exact-candidate rollback remain untested. The adversarial TCF ordering is not asserted as a hardware fact. Software/protocol failures above are **not** hidden in this category.

## CONTROLLED RISKS

H4FAIL remains: partial evidence rejected, no host retry/second diagnostic command, no second Storage attempt after an observed read failure, no forced semaphore/DMA cleanup, and full physical power removal after failed/uncertain capture. Multiple chunks within the single authorized capture are not host retry requests. A software/watchdog reset or new host process is not a power-cycle substitute. Unexpected MSD exposure is a stop condition; avoid filesystem mounting and use the scoped Windows policy described inwindows-msd-risk.md. Recovery entry/exit is only user-reported; handshake/rollback flashing are not tested.

## Package / documentation disposition

All requested focused report topics are recorded in this directory, with failures and remaining limits explicit. Prior stop-point reports are preserved undercheckpoint-before-resume-report. Global Phase61-withdrawal documentation is left unchanged as instructed: corrected-candidate checks have not all completed successfully, so no final designation/update of the4 current handoff pages is made. Existing withdrawal banners still prohibit both images. No firmware architecture or candidate byte was changed in this continuation.

Evidence: {L('startup-coupled-continuity.md')}, {L('final-stack-audit.md')}, {L('heap-reservation-audit.md')}, {L('b13-updater-confirmation.md')}, {L('windows-msd-risk.md')}, {L('reset-state.md')}, {L('timeout-ordering.md')}, {L('mount-failure-states.md')}, {L('live-host-tests.md')}, {L('rollback-manifest.md')}, {L('preflight-verdict.json')}.

FINAL PREFLIGHT CLOSURE = FAIL
''')
 W('README.md',f'''# Resumed Phase62 — FAIL / DO NOT FLASH

{identity}
Candidate bytes are frozen and unchanged. The reservation fix passes its existing focused tests, but new startup ownership, status-protocol and DMA-return requirements fail or remain unproved. See {L('findings.md')}. Original Phase61 hardware eligibility is permanently withdrawn.

The real Windows host implementation is present but live geometry/capture is locked by preflight-verdict.json=FAIL. Its port-listing mode is non-sending but was not invoked. No ports/hardware were accessed.25 mocks,15 measured stack cases and3 exact corrected-image install/rollback replays are recorded with explicit scope. Rollback files/uploader are pinned underrollback/; no candidate-update allowlist was weakened.
''')
 W('PRE-FLASH-CHECKLIST.txt','''DO NOT FLASH — FINAL PREFLIGHT CLOSURE = FAIL

[x] Corrected identity frozen; original Phase61 permanently withdrawn.
[x] Preserve existing reservation7/native28 results; no rerun.
[x] Continue exact live startup state without prepared fixture substitution.
[FAIL] SD mount invalidates NOR geometry; USB-ready continuity not closed.
[FAIL] NOT_READY / INVALID / FAILED wire statuses are indistinguishable.
[x] New Main/Storage stack measurements and15 modeled fault cases.
[FAIL] TCF-before-DMA-release countermodel violates no-return invariant.
[x] Allocator cursor provenance, exhaustion and native reset-entry tests.
[OPEN] Full postboot allocation/path coverage and physical headroom.
[x] Actual B1.3 updater instruction/selector witness; exact install.
[x]3 exact corrected-image install/rollback replays, no target overlap/no no-op.
[x] Local official4486 and B1.3 SYXs + exact reference uploader pinned.
[OPEN] Authenticated Novation-origin acquisition evidence unavailable.
[OPEN] Candidate-update uploader binding; do not allowlist a failing image.
[x] Windows MSD/automount scope and reset/power-cycle policy documented.
[x] Runnable host and25 mocks, no actual ports listed/opened/sent.
[FAIL] Final host/device workflow cannot qualify against missing statuses.
[x] Live query/capture LOCKED; no arbitrary NOR-address option.
[OPEN] Required firmware corrections/new identity and affected validation.
[OPEN] Complete current documentation promotion ONLY after all gates close.

H4: DISCARD PARTIAL OUTPUT / DO NOT RETRY / NO SECOND STORAGE ATTEMPT
AFTER READ FAILURE / NO FORCED CLEANUP / FULL PHYSICAL POWER CYCLE.
No hardware test is authorized. No hardware action was performed.
''')
 # Read-only preservation checks after report generation.
 for ext,key in [('syx','SYX_sha256'),('bin','BIN_sha256')]:assert sha(O/(c['candidate']+'.'+ext))==c[key]
 for line in (P/'SHA256SUMS.txt').read_text().splitlines():h,n=line.split('  ',1);assert sha(P/n)==h,n
 files=sorted(p for p in O.rglob('*') if p.is_file() and p!=O/'SHA256SUMS.txt')
 (O/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.relative_to(O).as_posix()+'\n' for p in files))
 print(json.dumps(verdict,indent=2))
if __name__=='__main__':main()
