from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase63-defect-closure'
load=lambda n:json.loads((O/n).read_text());x=load('continuity.json');v=load('preflight-verdict.json');m=load('milestones.json');a=load('allocation-prefix.json')
def link(n):return f'[{n}](<{(O/n).as_posix()}>)'
def write(n,s):(O/n).write_text(s.strip()+'\n',encoding='utf-8')
write('register-model.md',f'''
# SPI2 register identification and normal subset

**PROVEN (vendor definitions):** `$40003808` is SPI2_SR, base40003800 plus08; reset0002. Its hardware flags are RXNE0, TXE1, MODF5, OVR6, BSY7, FRE8, FRLVL10:9 and FTLVL12:11. CRCERR4 has software clear behavior. CR1 master/SPE and CR2 data-size/threshold govern operation. Sources: [ST STM32F745 header](https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-f7/master/Include/stm32f745xx.h), [ST RM0385 §32.9.3](https://www.st.com/resource/en/reference_manual/dm00124865-stm32f7-series-advanced-armbased-32bit-mcus-stmicroelectronics.pdf). The manual's indexed register excerpt was available; full PDF retrieval was size-limited, not independently archived.

**PROVEN (vendor definitions):** DR reads consume received FIFO data; DR writes enqueue transmit data. RXNE follows the configured receive threshold; TXE indicates available transmit capacity, not completion of reception. Normal SR reads do not consume RX data. Error clearing differs: OVR uses DR-then-SR reads, MODF uses SR read then CR1 write/SPE clear, FRE uses SR read, CRCERR uses SR write. Source: [ST F7 HAL SPI definitions](https://raw.githubusercontent.com/STMicroelectronics/stm32f7xx-hal-driver/master/Inc/stm32f7xx_hal_spi.h), macros CLEAR_OVRFLAG/CLEAR_MODFFLAG/CLEAR_FREFLAG/CLEAR_CRCERRFLAG. These unused error-clear sequences are documented, not claimed exercised or fully modeled.

**PROVEN:** Phase63 lacked a SPI2 status/data model. Zero-backed MMIO left TXE and RXNE clear; native37970/37986 could never progress. A real idle reset has TXE set and RXNE clear. Reset TXE alone is insufficient: receive progress needs clocked data.

**PROVEN:** {link('spi2_model.py')}, `SPI2.read/write/bind`, provides explicit CR1/CR2, four-byte TX/RX queues, delayed shifts only with master+SPE and SPI mode, FIFO-level/status derivation, byte DR enqueue/pop and I2SCFGR/CRC register latches required by initialization. Observed CR2=1703 means DS=7 and FRXTH=1. RCC APB1 enable is performed by unchanged native37858 code; its SPI2EN write is shown in candidate-08037770.asm. Active DMA completion remains the inherited explicit transaction/IRQ model, including MINC semantics; it is not mislabeled as CPU DR access.

**STRONG INFERENCE:** a finite number of SR-poll steps abstracts clock progress for this polling helper's normal path. Delay3 is a deterministic test choice, not measured peripheral latency or DSP cycle timing. TXE and RXNE are never globally forced high. RXNE requires a completed transfer and clears when FIFO consumption falls below threshold. No raw firmware routine, task-ready field, geometry field or native branch return is patched.

**UNKNOWN outside subset:** arbitrary I2S/16-bit/CRC/error recovery, competing DMA/PIO and silicon timing/cache effects are not qualified. Unsupported DR widths, empty DR reads and unmodeled SR writes stop the model. These limits prevent a general STM32 peripheral-model claim.

{link('accessors.md')} enumerates all31 authenticated PC/access/register combinations observed in the completed prefix, with values and counts. Full function listings and direct-call/literal candidates are separately retained. Accesses after the unresolved task frontier remain unknown.
''')
write('device-role.md',f'''
# SPI2's role in this startup

**PROVEN functional role:** this path is the external DSP host/boot/control link. It is not the raw NOR/QSPI, SD or display peripheral. ARM29260→29200 loads the two DSP bootstrap blocks selected by table08029700;3BA96→377DE uses SPI2 DMA1 RX3/TX4;3BAA2→37960 performs24-bit polled word exchanges. Register pointer chain20000264→20003414→40003800 is observed in native startup. ARM29344 sends read-address command then400000 to clock the pipelined DSP word back.

**PROVEN:** extracted **unchanged** candidate core0 image has13072 words, SHA896b2bc39c4273795e812374ab265fa88efb982bae884273dca2c5531e033495; core1 has364 words. The actual receiving program contains the corresponding DSP SHI protocol and readiness producer P2601→Y2B. This association uses both sides of the code, not the SPI instance name. See {link('peer-ready-static.json')}, candidate-080291b8.asm, candidate-0803b9d8.asm and loaded-core0.asm. Existing [DSP command map](<{(R/'notes/dsp-command-map.md').as_posix()}>) records the matching HRX/HTX and GPIO-qualified protocol.

**PROVEN:** SPI2 and DSP-host routines inspected here equal clean SC35D8 byte-for-byte ({link('identity-preservation.json')}). Do not assume later B1.3 background features exist in this diagnostic. SPI2 can carry DSP resources that were first read through the separate NOR path; that does not make SPI2 a NOR reader. Display SPI4 and external NOR QUADSPI are separate retained paths.

**UNKNOWN:** exact physical board-net/pin attribution is not established by this code-only audit. No device was inspected or used. The functional DSP endpoint is established independently of that wiring detail.
''')
write('negative-tests.md',f'''
# Bounded native model tests

**PROVEN:** {link('model-tests.json')} runs the unchanged candidate's actual37960 helper in isolated argument fixtures. These fixtures are not inserted into startup RAM.

| Case | Native result |
|---|---|
| Normal delay3 | Returns after100 instructions; exact transformed test RX bytes; guards intact |
| Delayed completion30 | Returns after343 instructions; same exact output |
| Receive completion absent |5000-instruction observer stops at3798A; no fabricated receive or return |
| SPI disabled |5000-instruction observer stops at3798A; no fabricated receive or return |

The latter stops are observer bounds, not firmware timeout/error returns. The native routine has no bounded failure exit for these conditions. Tests confirm reset SR2 has TXE but no RXNE.

**PROVEN:** eleven peer-contract checks in {link('peer-tests.json')}: absent boot marker, uncompleted ARM request, completed wire marker, initialized idle mailbox, four exact ordered procedural jobs busy→complete, rejection of unsupported selector0, rejection of the unmodeled16-bit transition, and rejection of an unknown consumed readback. A prefetched value that is subsequently discarded may be marked unknown; consuming it instead stops the model. All accepted successful response values are supported separately by native DSP execution, not substituted ARM returns. Exact initialization-memory and job-order assertions prevent reuse of these contracts for unrelated requests.

**PROVEN:** native DSP producer tests ({link('peer-ready-job.txt')}, {link('peer-ready-output.txt')}, ready-writes.txt) run the unmodified extracted program. Zero XFFF remains waiting at25F3; nonzero XFFF reaches2601 and writes Y2B=1. Boot sets Y2C=800000 at2875. This is a targeted DSP execution with modeled peripherals and explicit XFFF stimulus, not a hardware test or full processor-pair replay.

**PROVEN:** {link('peer_mailbox_test.py')} reapplies2951 X-memory values captured from actual SPI words in the continuous ARM prefix and runs original DSP init to113, then invokes original1C53 via an emulator-only caller atP7000. The ordered exact jobs080002/094403/0A8804/0BCC05 reach800000 after1/327/327/327 service invocations. Each deferred job is observed for1024 invocations; its first326 areC00000 and the rest800000. Source1D2B publishesC00000 and1DA8 publishes800000;1D41 advances persistent continuation, including X1B15 and X42/43. The earlier32-service bound was insufficient, not a firmware hang. {link('peer-contract-proof.json')} pins program, observed initialization and native output hashes. This confirms the already saved Phase24 four-job result against this exact candidate's observed wire initialization; it does not reopen the prior investigation or claim cycle timing.

Earlier isolated selector probes mailbox-0/2/3/4/5-output.txt start from a less complete DSP state; they are exploratory and do not qualify full startup or actual deferred-job completion. No P7000 test caller is written to candidate images; extracted BE24 files are unchanged analysis inputs, not new deployable firmware.
''')
milestone_rows=[]
for e in m['milestones']:
 name=e.get('milestone',e.get('event'))
 if e.get('object'):name+=' '+e['object']
 milestone_rows.append('|'+name+'|`'+e['record']+'`|')
write('continuity-allocation.md',f'''
# Exact-image continuous prefix and allocation status

**PROVEN:** the same Unicorn instance executes the unchanged Phase63 image throughout the observed startup. Initial SRAM is freshly zeroed plus authenticated initializer bytes, with inherited reset-clock/constructor/RTOS entry and peripheral-completion models. This reuses the prior qualified starting boundary; it does not reexecute every decompressor instruction or claim a new complete hardware reset proof. There is no running-RAM/geometry/task fixture substituted after mount or at the SPI seam. The independent helper-test RAM is never used here.

| Recorded milestone |12-byte lifecycle record |
|---|---|
{chr(10).join(milestone_rows)}
|Current DSP task frontier|`{x['record']}`|
|USB-ready|UNKNOWN — not reached|
|Geometry query|UNKNOWN — not reached|
|Authorization|UNKNOWN — not reached|
|Raw capture start|UNKNOWN — not reached|

**PROVEN:** {x['executed_instructions']:,} native instructions;{x['SPI2']['SR_polls']:,} SPI status reads;{len(x['SPI2']['TX_hex'])//2:,} transmitted polled bytes. These are model counts, not timing/feasibility measurements. Final heap cursor{x['heap_cursor']}, cap{x['heap_limit']}; the geometry record remains valid through NOR, SD and the later unchanged NOR mount.

The old cumulative10,000-PC-visit guard falsely stopped finite repeated GPIO/SPI operations during table upload. The new guard requires absence of byte-transfer progress for20,000 instructions before treating a heavily visited PC as stalled. Native chunk/exception bounds remain; missing receive completion cannot fake byte progress. This changes only replay termination policy, not firmware or readiness.

The inherited result field `private_unchanged=false` compares the final record with its initial all-zero marker. The actual snapshot intentionally changes it to11 plus geometry. It is not a failed memory-canary assertion; all record milestones are printed above. Full lifetime preservation is still unqualified.

**PROVEN:** boot-ready Y2B and initial mailbox idle responses now travel through actual SPI DR FIFO reads. No native read helper is replaced. SHI command/data selection is observed through native29190/291A2 and291B8 helpers; the protocol commits each word only after its third modeled byte completes. The XFFF request hook logs intent only; it cannot make DSP ready before the wire word commits. Each of the four exact ordered jobs returns its posted busy word before the independently supported idle result. **STRONG INFERENCE:** this finite busy→complete stutter is a valid progress abstraction for these observed mailbox values; it is not cycle-accurate processor-pair scheduling or a full DSP-state comparison.

**PROVEN model frontier:** native295E4 sends width-control bytes20/01/00 at29600. `BootPeer.commit` deliberately raises UnknownPeerRead at native37986 after the third byte, because the peer's16-bit SHI receive/DMA semantics and subsequent resource-backed selector0 job are not modeled. DSP main-loop113→12D is the width producer; HCSR10A5 selects16-bit words. ARM35ECE..35EF4 subsequently uploads16-bit coefficients;35F04 posts selector0 (first word0D1000). See the existing [command map](<{(R/'notes/dsp-command-map.md').as_posix()}>) and [Phase24 evidence](<{(R/'builds/phase24-init-transition/four-job-baseline-result.json').as_posix()}>). Full normal boot remains **UNKNOWN**. This is a model refusal, not a firmware crash or unchanged-SR wait.

An exploratory pass that ignored the width command reached selector0 and refused completion there. That pass is not admitted as a qualified continuity prefix: ignoring width and bulk-recipient updates cannot prove the coefficient upload. The final runner stops at the earlier, exact unsupported transition instead.

**PROVEN:** {a['observed_requests']} allocation requests and their actual caller sites are enumerated in {link('allocation-prefix.json')}. No additional Main heap allocation occurs across the newly modeled SPI prefix. Native allocator cap remains44D70 and observed record writes are only the intended lifecycle/snapshot operations. Ordinary bounded-allocator exclusion and raw-stack ownership remain supported by unchanged Phase63 tests, not rerun here.

**UNKNOWN:** complete postboot filesystem/transport/diagnostic allocation enumeration, postboot stack peak and absence of overlap across the *remaining* lifetime. The raw buffer has not yet been created in this continuous path, and no host transport session has begun. Do not infer complete coverage from176 prefix requests or a stopped cursor. No new fixed ARM RAM allocation is introduced by the Python peripheral/DSP-peer model.

Inherited synthetic models are explicit: FAT16 BPB/NOR payloads, JEDEC identity, absent SD completion, ADC1024 and factory calibration1500, clocks, DMA events and architectural exception delivery. These are not measurements of this unit. Real hardware memory margin and peripheral/USB timing remain hardware-only unknowns.
''')
write('findings.md',f'''
# Phase64 — SPI2 offline model closure

**FINAL PREFLIGHT CLOSURE = UNQUALIFIED.** The original zero-SR blocker is resolved in a bounded SPI2 register subset. Full startup still requires faithful16-bit SHI/DMA recipient handling and the resource-backed DSP table job; startup-to-capture and complete postboot allocation coverage remain incomplete. No new firmware defect is demonstrated. No candidate was modified or generated; no hardware, MIDI port or firmware transmission was used.

| Requested result | Conclusion | Confidence |
|---|---|---|
|1 Register identification|SPI2_SR, offset08/reset0002; status/FIFO and error-clear semantics documented|PROVEN vendor definitions|
|2 Accessors / stop cause|31 observed PC/access combinations, exact function listings; zero-shadow SR prevented TX/RX progress|PROVEN within traced prefix; post-frontier closure UNKNOWN|
|3 Device role|DSP bootstrap and SHI control/readback link, established on both ARM and DSP code|PROVEN functional role; exact board nets UNKNOWN|
|4 Minimal normal model|CR/mode setup, byte FIFO, TXE/RXNE, delayed transfer and DR side effects; boot-ready and four exact job contracts|PROVEN bounded tests; complete normal-boot peer model UNKNOWN|
|5 Negative sanity|Normal/delayed exact output; absent completion/disabled SPI block at3798A; eleven peer checks|PROVEN|
|6 Startup continuity|Same-state NOR/SD/geometry prefix advances past four procedural DSP jobs; stops at width command200100|PROVEN prefix; complete path UNKNOWN|
|7 Postboot allocation|176 prefix requests enumerated; later lifetime not reached|PROVEN prefix; complete audit UNKNOWN|
|8 Failure classification|A: missing16-bit SHI/DMA recipient and subsequent table-job model, not demonstrated candidate defect|PROVEN explicit model refusal; future full behavior UNKNOWN|
|9 Final reassessment|No PASS: continuity and allocation gates still open; old passing suites retained without unnecessary reruns|UNKNOWN overall|

The exact remaining mechanism begins at **SHI width command200100**, emitted by ARM295E4/29600 and consumed through DSP113→12D. It precedes the16-bit coefficient DMA upload and Y:$2C selector0 job0D1000. A model that merely acknowledges DMA and returns800000 would omit the actual recipient/work. The four procedural jobs are now independently completed; their earlier32-step probe did not establish a hang. No Phase63 change is justified by this model gap.

Reports: {link('register-model.md')}, {link('accessors.md')}, {link('device-role.md')}, {link('negative-tests.md')}, {link('continuity-allocation.md')}. Machine-readable gates: {link('preflight-verdict.json')}. The final geometry record is `{x['record']}`.

The **smallest next experiment** is to carry the first actual200100 width command and the following DMA TX buffer into an explicit16-bit SHI recipient, preserving byte order and data-word shift, then execute the unchanged DSP selector0 job with that exact modeled upload. Keep its actual continuation until native1DA8 completion and continue the same ARM instance. Record the inherited NOR payload's synthetic provenance separately; it cannot authenticate current-unit coefficients. Do not force mailbox values, skip read loops, substitute a running fixture, modify candidate firmware, or reopen NOR mutation research.

Remaining hardware-only unknowns are real heap/stack margin, physical bus/clock/error timing, ADC/calibration values and live USB/host interoperability. These are separate from the remaining **offline** DSP-peer/continuity/allocation gaps. H4's already proven lack of bounded unwind is not relabeled unknown; the existing quarantine/power-cycle containment policy still applies.

**PROVEN preservation:** all199 Phase63 manifest files verify unchanged, including its candidate, old test evidence, locked host/uploader and its UNQUALIFIED verdict. BIN SHA `{v['candidate_BIN_sha256']}`; SYX SHA9b420521a366c65c13fb871778fdbab612ca126cbb4ad60d0fd5bc12ecd253da. The inspected SPI2/DSP-host code also equals clean SC35D8. No install/rollback,28-native,31-DMA or32-host tests were repeated because their image and scope are unchanged. See {link('identity-preservation.json')}.

FINAL PREFLIGHT CLOSURE = UNQUALIFIED
''')
write('CHECKPOINT.md',f'''
# Resume Phase64 model checkpoint

Phase63 is immutable and remains ineligible; all199 manifest entries matched. Do not rebuild or rerun closed Phase63 suites absent new invalidation.

Completed: SPI2 register/mode/FIFO subset,4 native helper sanity cases,11 peer contract cases,31 accessor combinations, functional DSP role, exact DSP Y2B producer/initial Y2C proof, and native observed-state completion of four ordered procedural jobs. Data and model limitations are in findings.md. No native branch/geometry/task-ready return was stubbed to bypass SPI2.

Latest continuous frontier: `{x['frontier']['message']}`, nativePC{x['frontier']['pc']}; record{x['record']}; heap{x['heap_cursor']}/{x['heap_limit']};176 allocation requests. USB service/query/auth/raw and remaining allocation coverage are unexecuted.

`startup.py` is the flattened latest runner. Current implementation recreates its prefix because its SRAM dump plus result JSON do not serialize every CPU/peripheral/closure state. `CAPTURED` retains the live instance only within that process; do not reconstruct from frontier-sram.bin alone or splice in Phase63 native/coupled fixtures.

Next: command200100→16-bit SHI→first coefficient DMA upload→native selector0 job0D1000. Jobs080002/094403/0A8804/0BCC05 already complete at1/327/327/327 services; do not redo that investigation. Their contracts are exact-word, initialization-hash and order constrained; timings are stutter abstractions, not cycle measurements. Reuse the exact observed SPI init memory and unchanged DSP image. The final runner refuses the width transition; the earlier exploratory path that ignored it and reached selector0 is not a qualified prefix.

Commands for invalidated/new model checks only: Python -B model_tests.py; peer_tests.py; startup.py. peer_ready_audit.py extracts unchanged DSP analysis inputs; peer_mailbox_test.py performs the targeted native DSP probe. `finish.py` verifies identities and saved gates; `reports.py` writes reports and manifest. Both currently retain UNQUALIFIED intentionally. Changing a verdict file is not qualification.

FINAL PREFLIGHT CLOSURE = UNQUALIFIED
''')
write('README.md',f'Phase64 offline model evidence. **UNQUALIFIED**; no hardware action. Start with {link("findings.md")} and {link("CHECKPOINT.md")}. No new firmware image is delivered.')
manifest=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name!='SHA256SUMS.txt':manifest.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(O).as_posix())
(O/'SHA256SUMS.txt').write_text('\n'.join(manifest)+'\n')
print('Phase64 reports saved; files',len(manifest))
