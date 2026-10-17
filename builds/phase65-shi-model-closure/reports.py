from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[1]
load=lambda n:json.loads((O/n).read_text())
x=load('continuity.json');v=load('preflight-verdict.json');a=load('allocation-prefix.json');t=load('transfer-summary.json');m=load('milestones.json')
def link(n):return f'[{n}](<{(O/n).as_posix()}>)'
def write(n,s):(O/n).write_text(s.strip()+'\n',encoding='utf-8')
write('shi-model.md',f'''
# Phase65: exact SHI transition and minimum model

**PROVEN:** `0x200100` is a 24-bit command word, not an ARM address or a register location. ARM `080295E4` emits bytes `20 01 00` at `08029600→0803BAA2→08037960`, on the DSP command lane. The SPI2 peripheral still shifts 8-bit bytes. The receiving DSP's SHI changes its word framing from three bytes to two bytes.

**PROVEN by the original DSP code:** the SHI receive handler reads HRX at `X:$FFFF94`, tests command/data GPIO `X:$FFFFBD` bit8, and stores this command in `X:$12` at P:$0163. The native main loop at P:$0113 clears pending bit21, conditionally calls P:$012D, tests width bit8, and writes HCSR `X:$FFFF91` through `$10A4→$10A5`; HCKR `X:$FFFF90` receives3. P:$013E clears GPIO bit9. `X:$12` retains `$000100`; it is not required to become zero. The reverse command is the two-byte `20 00`, received as `$200000`; native P:$0130–$0134 restores HCSR `$10A9`. Sources: {link('candidate-080295e4.asm')}, {link('DSP-0113-013f.asm')}, {link('DSP-0156-01b3.asm')}, and the existing [DSP command map](<{(R/'notes/dsp-command-map.md').as_posix()}>).

**PROVEN:** command/data and chip-select operations remain native ARM helpers `08029190/080291A2/080291B8/080291CA`. The model observes them and clocks the actual SPI DR bytes; it does not substitute their return values. DSP HRX/data-store semantics are modeled as complete received words: in 16-bit mode the first byte occupies bits23..16, the second bits15..8, and bits7..0 are zero. The saved pointer advances only after the second byte. P:$0198–$019E selects X/Y from saved command flags and performs the receiving store.

**PROVEN within this abstraction:** {link('dsp_peer.py')}, `BootPeer.byte/commit/dma`, keeps word framing and delayed SPI receive completion separate. The inherited {link('spi2_model.py')} supplies bounded TX/RX FIFO progress; TXE does not imply RXNE. Width control is consumed by the original DSP main loop before the parser changes framing. There is no unconditional idle mailbox response for the new table jobs.

{link('native_dsp.py')}, `NativeDSP`, keeps the existing strict-flow emulator alive through all table requests. It loads the unchanged candidate DSP programs, uses original bootstrap entry PCs100/107, pauses at25F3, admits only X/Y values already delivered by this live ARM run, then resumes naturally at113. Subsequent mailbox polling executes `TURN 113`; it does not assign PC, use a P:$7000 trampoline, or patch P:$0281. Native `P:$1C53/$1D41/$1DA8` creates, advances and clears the deferred table work.

**STRONG INFERENCE:** one native main-loop turn per observed mailbox read is a suitable asynchronous progress abstraction for this startup workload. It is not calibrated DSP/ARM timing, a cycle-accurate SHI FIFO/interrupt model, or a proof of all DSP state between ARM polls. Early boot-ready exchange and bootstrap DMA reuse the scoped Phase64 model. Native DSP initialization is staged from wire-derived state; no prepared ARM RAM or geometry state is inserted mid-run.

**UNKNOWN outside this scope:** arbitrary SHI commands, hardware overrun/recovery, cycle deadlines and autonomous DSP progress after ARM stops polling are not qualified. DSP shared/external backing is the existing emulator allocation, not a new grant of physical memory ownership to the diagnostic or Plaits. No firmware image was generated or changed.
''')
write('coefficient-transfer.md',f'''
# Coefficient transfer and completion

**PROVEN:** original ARM `08035E28` initializes the four procedural families, then executes 16 resource-backed families with nine coefficient records each. `08035EC0` reads a 256-word descriptor count; `08035EC8` selects DSP X:$0C00. `08035ECE` enters16-bit SHI mode. `08035EE2→08047C6C` reads512 bytes into the global scratch pointer's observed ARM buffer `$20005148`. For the first record the NOR source is `$82000`.

`08035EEE→0802968E→0803BA96→080377DE` submits those512 bytes through SPI2 DMA1 stream4 TX, paired with stream3 RX. Observed TX CR `$10455` uses byte-width memory/peripheral accesses and incrementing source. SPI2 DR is `$4000380C`. Every modeled two-byte pair becomes one left-justified24-bit DSP word; the completed receiving extent is **X:[$0C00,$0D00)**,256 words. This models source bytes in their actual order; it does not infer an authenticated source-file sample format from all-zero input.

**PROVEN:** the same ARM run delivers **144** such512-byte data DMAs plus144 two-byte restore commands. All data buffers are at `$20005148`, all modeled coefficient payload hashes equal SHA256 of512 zero bytes, and every data transfer advances from C00 to D00. {link('transfer-summary.json')} lists every DMA, source pointer, configuration and hash; {link('shi-evidence.json')} retains the wire/model journal. {link('native-dsp-job.txt')} records actual receiving X writes and unchanged native execution commands.

**PROVEN:** normal DMA completion is modeled only after all descriptor bytes are consumed. RX/TX stream EN and NDTR are cleared, transfer-complete state is raised, and actual native IRQ30 executes. Native `08023414–08023422` waits for its completion byte; the model does not return from that helper on its behalf. `08035EF4` restores24-bit SHI using command `20 00`; `08035F04` then posts the destination/selector0 job to Y:$2C. Before the next coefficient record, `08035EB2–08035EBE` reads the actual DSP mailbox until ARM receives `$80000000`, the left-aligned DSP `$800000` idle value. See {link('candidate-08035e28.asm')}, {link('candidate-080377de.asm')}, {link('candidate-08023414.asm')}.

**PROVEN counts, with an explicit limit:** 148 jobs were **posted**, comprising four procedural and144 resource-backed jobs. Idle completion is observed for147 jobs. The last posted word `$212C00` has no observed idle completion before the later USB stop. The source initializer can leave its final post without another mailbox poll. Earlier wording that all148 completions were verified was too broad; no last completion is manufactured during finalization.

**UNKNOWN current-unit provenance:** these coefficient bytes come from the inherited synthetic NOR-zero model. They are useful offline inputs for control-flow/ownership tests, not evidence of the user's physical `$82000` contents. Generated audio-table contents and resource validity on that unit remain unverified.
''')
write('negative-sanity.md',f'''
# Bounded negative sanity

**PROVEN:** {link('negative-tests.json')} contains seven bounded checks. Three execute the unchanged candidate's `08037960` helper with command `20 01 00`: normal completion, delayed readiness, and absent receive completion. The delayed case returns the same completed command after more native instructions. The absent case stops at `0803798A` after the5000-instruction observer bound, retains24-bit framing and commits no width change. This is an observed firmware wait, not a firmware timeout exit.

The remaining checks exercise incomplete-word framing, a255-word/510-byte stream, exact completion after the final two bytes, and a genuinely programmed255-word stream. Nonzero deterministic test bytes verify byte order and all256 left-justified results. One received byte cannot create a coefficient;510 bytes cannot create coefficient256.

**PROVEN, continuous native negative:** {link('incomplete-transfer/negative-result.json')} reruns the same authentic prefix only because its first evidence writer failed before saving the final result. At the first512-byte coefficient DMA it supplies510 bytes, retains NDTR=2 and EN=1 on both streams, and withholds the completion IRQ. Native ARM remains at `08023414` for256 observed visits. It does not restore24-bit mode or post selector0. Geometry remains `110000000180003480908f01`. The observer stops the test; no semaphore is released and no cleanup command is invented.

**PROVEN distinction:** SHI framing does not independently know that a descriptor should contain256 coefficients. If a caller genuinely requested510 bytes and received completion, the SHI abstraction stores255 words; it does not fabricate an error or pad the last coefficient. The actual normal ARM producer requests512. A separate native wrong-descriptor error exit is **UNKNOWN** and is not claimed. The truncated512-byte case proves the genuine completion wait while bytes remain.
''')
rows=[]
for e in m['milestones']:
 name=e.get('milestone',e.get('event',''))
 if e.get('object'):name+=' '+e['object']
 rows.append(f"|{name}|`{e['record']}`|")
write('continuity-allocation.md',f'''
# Continuous prefix and allocation coverage

**PROVEN within the inherited reset boundary:** one Unicorn ARM instance runs from the authenticated reset-clock prefix and constructors through scheduler launch, NOR mount/snapshot, absent-SD initialization, SPI2/DSP boot and all144 coefficient transfers. It then reaches USB initialization. The actual scheduler/NOR/SD ordering precedes Main's coefficient work; events were not reordered to match a requested checklist. Starting SRAM is zeroed plus authenticated initializer bytes. The inherited starting boundary does not newly reexecute every reset decompression instruction.

| Milestone | Exact12-byte record |
|---|---|
{chr(10).join(rows)}
|USB initialization stop|`{x['record']}`|
|USB configured/ready|UNKNOWN — not reached|
|Geometry query / same-epoch authorization|UNKNOWN — not reached in this continuous run|
|Raw capture start|UNKNOWN — not reached in this continuous run|

**PROVEN:** {x['executed_instructions']:,} ARM instructions reach `08048316`. The old observation bound flagged GPIO helper `080291B2` after a long computation solely because its cumulative visit count was high. The saved last40 PCs contain that helper only once; this is not a tight firmware wait. {link('observer-false-stall.json')} preserves the rejected observation. The corrected observer also requires local repetition and a much longer absence of byte progress. It changes no ARM/DSP instruction, MMIO readiness value, task-ready field or geometry record. The repeated prefix was required because the existing runner does not serialize every CPU/peripheral/closure state; no RAM dump was spliced into a running fixture.

**PROVEN allocation prefix:** {a['total_requests']} requests are enumerated in {link('allocation-prefix.json')}, including {a['new_requests']} newly observed after the Phase64 prefix. All old176 request entries match their saved evidence. At USB initialization the actual heap cursor is `{a['heap_cursor']}` and cap is `{a['heap_limit']}`. The record still has valid11 state and the same geometry. The existing private-write trace records its intended lifecycle/snapshot transitions. `private_unchanged=false` compares against initial zeroes; it is not a failed canary assertion.

**STRONG INFERENCE, bounded:** the unchanged nonoverflow allocator cap and the unchanged Phase63 reservation regressions support exclusion of ordinary bounded heap growth from the reserved record. The currently observed cursor is below that cap. Request enumeration and final cursor do not prove every allocation's return extent, all future frees/reuse, or the entire postboot lifetime.

**UNKNOWN:** all allocations after this USB boundary, USB transport-session state, raw-frame construction and full same-epoch query→authorization→raw lifetime. No raw capture frame exists yet in this continuous run. Phase63's stack-buffer/DMA fence and host containment results remain scoped evidence; they are not substituted for these missing events. Complete postboot allocation coverage therefore remains unqualified.

**HARDWARE-ONLY UNKNOWN:** actual heap/stack headroom and timing remain unmeasured. Inherited model inputs include synthetic FAT16 geometry/NOR data, JEDEC identity, absent SD, clocks, ADC/calibration values, and explicit DMA/exception scheduling. They do not establish the physical unit's resources or USB interoperability.
''')
write('stop-rule-and-safety.md',f'''
# Final stop-rule assessment

**PROVEN — category B, new peripheral-model gap:** native `080381C8` calls `08048316` with R0=`$40040000`. Instruction `ldr r1,[r0,#8]` attempts `$40040008`; the inherited emulator maps peripheral memory only at `40000000..4002FFFF`. Unicorn reports READ_UNMAPPED before the subsequent write. Code then clears bit0 and stores the value back. Listings: {link('candidate-080381be.asm')}, {link('candidate-080482d0.asm')}; map source: [Phase42 Physical.__init__](<{(R/'builds/phase42-exact-rdiag-integration/environment.py').as_posix()}>).

**PROVEN vendor identification:** this is USB OTG HS `GAHBCFG` at base40040000+8, the global AHB configuration register. The bit0 operation disables global USB interrupts. Source: [ST STM32F745 device definitions](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-f7/master/Include/stm32f745xx.h), USB_OTG_HS_PERIPH_BASE, USB_OTG_GlobalTypeDef.GAHBCFG and USB_OTG_GAHBCFG_GINT. It is unrelated to SHI word framing and is not an invalid firmware pointer into absent physical hardware.

**PROVEN narrow safety effect:** the failed instruction is a peripheral read. It has not written bootloader flash, NOR, the geometry record, or a raw buffer. No raw buffer is active and no authorization was accepted in this continuous prefix. This stop demonstrates missing emulator coverage, not a concrete firmware corruption path. The Phase63 image and its already passed install/rollback/reservation/status/DMA/host suites are unchanged.

**STRONG INFERENCE:** controller register/reset/endpoint/FIFO/IRQ progress is needed to continue real USB initialization and configure a host link. Mapping zeroes or forcing a ready/configured field would not qualify that sequence. No such shortcut was added.

**UNKNOWN, safety-relevance limit:** the USB controller as a whole is not declared irrelevant. It ultimately supplies diagnostic input and transmission/completion events; its buffers and lifetime interact with transport and authorization. The exact failed read is not a corruption operation, but this phase cannot exclude every later USB-buffer/allocator interaction merely from its absence. Separate scoped parser/host/DMA tests remain useful and preserved. No new concrete bootloader/NOR/authorization/rollback defect is demonstrated.

**Stop rule applied:** no general USB peripheral model, enumeration research, endpoint simulation or new peripheral phase was started. The residual gap is **MODEL COVERAGE LIMITATION / HARDWARE-ONLY UNKNOWN** for physical USB operation; the continuous offline path and allocation enumeration are also explicitly incomplete. Calling physical behavior hardware-only does not convert an unexecuted offline safety assertion into PROVEN. With the mandatory continuous gates unexecuted, the final result remains UNQUALIFIED.
''')
write('findings.md',f'''
# Phase65 final model-closure result

**FINAL PREFLIGHT CLOSURE = UNQUALIFIED.** The specific16-bit SHI transfer gap is closed for the declared offline workload. The corrected continuous replay reaches USB initialization, where an unmapped USB-controller register stops execution. No firmware defect is demonstrated. The stop rule is applied; no broad USB research or new peripheral model is started.

| Gate | Evidence / result | Confidence |
|---|---|---|
|Identify0x200100|DSP SHI command word, not ARM memory; selects16-bit framing|PROVEN|
|Coefficient transfer|144 ×512-byte transfers,256 words each to X:C00–CFF;24-bit restore handled|PROVEN in stated model|
|DSP progress|148 posts;147 observed idle completions; last212C00 completion unobserved|PROVEN counts; last completion UNKNOWN|
|Negative sanity|Seven bounded helper/framing checks plus continuous truncated-DMA wait|PROVEN within stated scopes|
|Observer false stop|Corrected; original GPIO helper executes normally beyond prior stop|PROVEN|
|Continuous startup|Same ARM state reaches USB init after4,421,081 instructions; no USB-ready/query/auth/raw start|PROVEN prefix; complete path UNKNOWN|
|Allocation coverage|298 requests total,122 new; cursor20011334 below cap20044D70|PROVEN prefix; full postboot UNKNOWN|
|New stop|B: unmodeled USB OTG HS GAHBCFG read40040008 at08048316|PROVEN model gap|
|Firmware defect|None demonstrated; image unchanged|UNKNOWN future behavior; no concrete defect finding|

The last continuous geometry record is `{x['record']}`. Coefficient inputs are **synthetic zero bytes**, not authenticated contents of the user's physical unit. All144 uploads completed, but the earlier claim of148 verified table-job completions was too broad:148 jobs were posted and147 idle completions were observed. The last job is not marked complete by assumption.

The exact new MMIO read cannot itself corrupt diagnostic RAM or NOR. USB's later transport/buffer behavior cannot be categorically called non-safety-relevant, however, and full postboot allocations and same-epoch capture continuity were not executed. Thus this is not PASS and not evidence of a concrete FAIL in the firmware. Physical USB behavior, actual geometry/resources, real memory margin, scheduling/cache/fault behavior and candidate-specific physical rollback remain **HARDWARE-ONLY UNKNOWN**. H4's known missing bounded storage unwind remains a proven limitation handled by the existing no-retry/power-cycle containment policy.

Reports: {link('shi-model.md')}, {link('coefficient-transfer.md')}, {link('negative-sanity.md')}, {link('continuity-allocation.md')}, {link('stop-rule-and-safety.md')}. Machine-readable result: {link('preflight-verdict.json')}.

**PROVEN preservation:** all199 Phase63 manifest files and all72 Phase64 manifest files still match. The exact BIN SHA256 is `{x['candidate_sha256']}`. No firmware was generated or modified; no hardware, MIDI access or transmission occurred. No reference repository file was edited. Closed historical suites were preserved instead of rerun.

No additional broad peripheral-research phase is proposed. The remaining decision is the disposition of the declared continuous USB/allocation coverage limit; it must not be silently waived or relabeled as completed evidence.

FINAL PREFLIGHT CLOSURE = UNQUALIFIED
''')
write('CHECKPOINT.md',f'''
# Phase65 final checkpoint

This scoped model-closure attempt is finished with UNQUALIFIED. Do not restart SHI analysis or run a broad new USB model phase automatically.

The final corrected normal replay is saved in continuity.json and selected-startup.py.txt. It reached USB OTG HS GAHBCFG at08048316 /40040008. ClassificationB: new peripheral-model gap. There is no demonstrated firmware defect. Record{x['record']}, heap{x['heap_cursor']}, cap{x['heap_limit']}.298 allocation requests;122 new. USB-ready/query/auth/raw start and complete postboot allocations remain unexecuted.

144 coefficient uploads and144 restores completed.148 mailbox jobs were posted;147 completions were observed. Last212C00 completion is not observed. Do not repeat the earlier overstatement. The DSP peer remains an explicitly staged/coupled abstraction and the coefficients are synthetic zero NOR inputs.

The normal native DSP process was closed after saving its transcript. The SRAM file is not a complete CPU/peripheral checkpoint. Replaying is required by the current implementation to continue a full machine; do not splice it into a prepared-RAM test. Source/observation changes do not authorize firmware modifications.

Negative tests:7 helper/framing checks plus incomplete-transfer/negative-result.json, native completion wait with2 remaining bytes and EN1 on both streams. An initial evidence writer lacked the PC constant import; only that incomplete-transfer replay was rerun to persist the missing result. No closed prior suites were restarted.

Finalization: finish.py checks saved evidence and prior manifests; reports.py writes these reports; validate.py verifies file consistency/manifests. Neither qualifies unexecuted gates by changing labels. Firmware and prior Phase63/64 files remain immutable.

FINAL PREFLIGHT CLOSURE = UNQUALIFIED
''')
write('README.md',f'Phase65 offline SHI model closure. Start with {link("findings.md")}. **UNQUALIFIED**; no hardware action. No firmware image was generated.')
manifest=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name!='SHA256SUMS.txt':manifest.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(O).as_posix())
(O/'SHA256SUMS.txt').write_text('\n'.join(manifest)+'\n')
print('Reports and manifest saved',len(manifest))
