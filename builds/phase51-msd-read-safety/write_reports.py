"""Phase51 evidence reports, no firmware or device operations."""
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def link(p):return f'[{p.name}](<{p.as_posix()}>)'
def here(n):return link(OUT/n)
def old(n,p='phase50-msd-readonly-geometry'):return link(ROOT/'builds'/p/n)
reports={
'mode1-entry-exit.md':f'''# Phase51 — separate entry, read and exit

**PROVEN:** existing transient entry is normal application SysEx dispatcher0801EB30→248F0 (vendor command byte5=42hex,subcommand byte6=0,mode byte7=1)→24918→38C10→248CE (150 timer ticks)→248B4→38C54. No rdiag or new firmware is involved. **STRONG INFERENCE:** ordinary incoming SysEx/Main application callback context, not QSPI IRQ; the timer callback runs through the application timer service. **UNKNOWN:** fully reconstructed RTOS scheduling/current-task state on the real unit. {old('b13-080248b4.asm')}; {here('b13-0801eb30.asm')}.

**PROVEN new native scope:** full incoming dispatcher, not merely248F0, followed by real deferred callback, class reset/register, descriptor merge, USB wrapper/controller setup and endpoint closure, executes twice for entry1 and twice for exit0. It visits685 distinct instruction addresses. USB HAL stop/start/init/FIFO/endpoint register operations, the disconnect delay and timer enqueue are explicit seams. Unlike Phase50,24630/245C6/246A8/2464C and their application wrappers execute natively. No Storage enqueue23F68, mount19A92, unmount1AE1C, settings-save2D2AC, content-write/delete/flush, NOR program/erase, or updater-reset39042 is reached. {here('mode_cases.py')}; {here('mode-cases.json')}; {here('b13-080245c6.asm')}; {here('b13-08024630.asm')}; {here('b13-080246a8.asm')}.

| Route | Persistent producers and state changes |
|---|---|
|A transient mode1 entry |**PROVEN tested route:** none; mode RAM/window pointer, timer state and USB controller/class state change. Registers MIDI200000EC + MSD200000F8; base94000. No MCU reboot or FS mount/unmount. USB stop/re-enumeration is not MCU reset. |
|B READ10 |**PROVEN:** read op1 plus queue-drain waits; no new write/erase/FS flush producer. Existing unrelated queued operations can complete during the waits. |
|C transient mode0 exit |**PROVEN tested route:** none; same class rebuild with MIDI only, mode0. No FS restore/remount because no FS was unmounted. |
|UI Advanced Setup bit17 toggle, either direction |**PROVEN conditional producer:** setting commit353C0→registered changed-settings callback2D278→2D300→2D2AC→128-byte write3C920+flush. This is not a read-only substitute for transient mode control. |
|SCSI START STOP/eject |**PROVEN:**57FB4→248CE→248B4 re-applies mode1, not mode0 exit; no explicit FS flush in this route. |

Sources for UI/save/eject: {old('mode-entry.md')}; {old('persistence-routes.md','phase46-msd-filesystem-closure')}; {old('msd-reachability.md','phase46-msd-filesystem-closure')}. No project/session, SD, NOR or updater metadata write producer was found solely in the tested transient entry/exit route. **UNKNOWN:** universal closure through modeled USB HAL/MSP/IRQ effects and independently scheduled background work; zero observed writes in these slices is not an exhaustive whole-system theorem. Entry assumes ordinary application state, no active updater or Storage fault.

Power-cycle alternative: **PROVEN** an abrupt power loss would bypass later execution of the normal exit routine; **UNKNOWN** persistence during the next boot, queued-write interruption, and cold-boot cleanup predicates. Prior phases explicitly leave those tied to actual filesystem state. It cannot be certified as a safer no-mutation exit or as evidence that entry/READ were safe. No physical action is recommended or performed. {old('startup-persistence.md','phase47-filesystem-state-closure')}.
''',
'read10-physical-path.md':f'''# Phase51 — exact physical read and statuses

**PROVEN exact image:** B1.3 SHA-256 `2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41`. All22 newly inspected path ranges match official4486. Firmware files are read only. {here('path-inspection.json')}.

1. **PROVEN:** ordinary BOT-admitted READ10 opcode28 enters3B27C→3B480; big-endian CDB2..5 LBA40hex and7..8 count1; cached8192 blocks/4096 bytes; transfer direction/length checks.3B52E calls initialized table20003788+10→57E88. {old('b13-0803b27c.asm')}.
2. **PROVEN:**57E88 clears4096 bytes at transfer buffer40024000, drains NOR queue via23FD6, selects base `[ [200037C0] ]`=94000 in mode1 and computes94000+(40<<12)=D4000.57ECC calls wrapper24130 with buffer40024000,length1000hex. {old('b13-08057e30.asm')}.
3. **PROVEN:**24130 builds24-byte op1 descriptor,23F68 queues it;23FD6 waits. Storage24014 pops op1→2408A→backend22F94. Backend checks start against capacity and byte semaphore; normal path calls37430; worker240C4 saves status to wrapper+18; wrapper24160 returns that byte. {old('b13-08024130.asm')}; {old('b13-08023f68.asm')}; {here('b13-08022f94.asm')}.
4. **PROVEN:**37430 prepares DMA at1C072, issues NOR command3769C→22746, waits37596, disables QSPI DMA request afterward. Common read opcodeEC and IRQ/wait model are already audited in Phase31; no read-side program/erase path is introduced. {here('b13-08037430.asm')}; {here('b13-08037596.asm')}; {old('findings.md','phase31-storage-error-recovery')}.
5. **PROVEN:**57ECE ignores wrapper status, optionally substitutes serial marker text in response RAM, then returns0 at57EEE. SCSI3B530 sees success and sends4096 bytes on endpoint82 through24754. Native BOT status26DB0→26EAE sends13-byte CSW with status0 and zero residue in every new completed case, including native failures1/2. {here('read-cases.json')}.

The coupled runner executes wrapper, enqueue, worker, actual backend bounds/semaphore path, response clear/filter, SCSI data and CSW. Queue byte movement and task wake/yield are modeled; CPU contexts switch outside emulator hooks. Physical37430 DMA completion/bytes and USB TX/RX are seams. Runtime fixture construction explicitly applies native constructor values: backend vtable805B1AC, capacity02000000 and wrapper pending/capacity0/1. This is not claimed to be a cold boot or a physical read. {here('read_cases.py')}.

**PROVEN:** the mode1 physical equation is unchanged. **UNKNOWN:** actual current mode, physical completion or mounted/cache state from the user's unit; none was acquired. The inspected buffer is a fixed memory-mapped4KiB region, not a newly allocated512-byte heap object. Its memory address is proven; no claim about retention across power loss is needed.
''',
'read-error-propagation.md':f'''# Phase51 — where error evidence is lost

| Layer | Return / failure behavior |
|---|---|
|Backend22F94 |**PROVEN:** start>=capacity returns1 at22F9E without DMA; semaphore0 returns2 at22FCC without DMA; otherwise37430 then semaphore release1BA12 and returns0 at22FD8. No length-out field and no TEF return branch. |
|NOR DMA37430 / wait37596 |**PROVEN:** completion wait has no returned error contract; loop requires software bit0. TCF IRQ22826 sets it; TEF-only does not. No NDTR-versus4096 check in37430 after wait. |
|Worker24014 |**PROVEN:** stores backend return byte in wrapper+18 at240C4 and clears sync when drained. |
|Wrapper24130 |**PROVEN:** returns saved status byte at24160. Error is not lost here. |
|MSD57E88 |**PROVEN:** first loss at57ECE, immediately after57ECC call: unconditional branch to filter, no test/save ofR0;57EEE overwritesR0=0. No done-byte count forwarded. |
|SCSI/BOT |**PROVEN:** completed failures1/2 look like normal successful4096-byte data stages, CSW GOOD0, residue0; no new medium-error sense queued. |

Native sources: {here('b13-08022f94.asm')}; {here('b13-08037430.asm')}; {here('b13-08037596.asm')}; {here('b13-08022826.asm')}; {old('b13-08024130.asm')}; {old('b13-08023f68.asm')}; {old('b13-08057e30.asm')}; {here('read-cases.json')}.

**PROVEN native failure tests:** busy0 semaphore and capacity-mismatch bounds rejection each run with two prior buffer contents. They return2/1 through native backend→worker→wrapper, yet host data length4096 and successful CSW are unchanged. The valid D4000 address in a correctly configured32MiB backend is not a bounds failure; that case deliberately lowers the fixture capacity to test propagation, not to claim normal firmware config is wrong. Busy reachability under actual scheduling is **UNKNOWN**, but the native return contract and caller behavior are proven.

**PROVEN prior fault-model results:** Phase31 TEF/missing completion leave Storage waiting, semaphore held and request active; no successful wrapper return, so the new 'lost-return' cases must not be conflated with a TEF return1/2. **STRONG INFERENCE:** the same size-independent wait predicates apply to4096-byte MSD reads. **UNKNOWN:** actual4096-byte silicon TEF/DMA state, incidence, and whether independent errors always suppress TCF. Earlier44-assertion/six-fault evidence is reused, not rerun or relabeled as a new MSD fault reproduction. {old('fault-replay.json','phase31-storage-error-recovery')}; {old('findings.md','phase31-storage-error-recovery')}.

**UNKNOWN physical completeness:** hypothetical partial DMA followed by a modeled37430 completion-return is accepted by upper layers. This is not proof real TEF produces a successful partial response. It demonstrates the software checks above37430 cannot independently establish DMA completeness; firmware's native wait observes a controller bit, not a checksum of the returned sector.
''',
'stale-buffer-analysis.md':f'''# Phase51 — stale, zero and partial data

**PROVEN:** READ10 uses40024000..40024FFF. Native57E88→1A7E4 clears the requested4096 bytes before any queue wait or physical read. Both an A5 poison fill and a previous complete valid BPB were seeded as prior contents in each case. Native early failures1/2 return a full all-zero sector, never those old contents. The lower backend alone leaves its destination unchanged on those early failures; the MSD caller's earlier clear makes that unchanged destination zero. {here('b13-0801a7e4.asm')}; {old('b13-08057e30.asm')}; {here('read_cases.py')}; {here('read-cases.json')}.

| New coupled cases (two priors each) | Returned data | Parser | Confidence/scope |
|---|---|---|---|
|Normal read model |4096-byte model BPB |passes structure |**PROVEN** native upper path; DMA bytes modeled |
|Native busy2 |4096 zero bytes, GOOD CSW |rejects signature |**PROVEN** native backend failure propagation |
|Native bounds1 |4096 zero bytes, GOOD CSW |rejects signature |**PROVEN** with capacity-mismatch fixture |
|Hypothetical128-byte DMA then completion-return |prefix plus cleared tail; no55AA |rejects signature |**PROVEN** model behavior; **UNKNOWN** silicon reachability |
|Hypothetical512-byte DMA then completion-return |complete BPB/signature, cleared tail |passes structure |**PROVEN** model ambiguity; **UNKNOWN** silicon reachability |

In the512-byte model the remaining3584 bytes of the normal test sector are zero, so a partial DMA and full transfer produce **identical returned4096 bytes and hash**. This is not a demonstrated incorrect BPB, nor a parser bug. It proves byte-only checks cannot attest the full physical transaction's completion. If all geometry-bearing bytes really came from the correct NOR address, those bytes can still describe correct geometry. Establishing that condition under physical faults remains **UNKNOWN**.

**PROVEN:** no previous-sector/unrelated-RAM contamination survives normal clearing in the tested sequence. **UNKNOWN:** concurrent buffer reuse, DMA writes after a failed/hung read, or physical corruption; these were not fabricated as observed failures. A hung TEF read may partially alter the buffer but does not reach ordinary USB data-send in the prior tested wait model. Do not re-use that active session.

**PROVEN:** existing Phase50 parser rejects zeroes, missing signature, wrong length and inconsistent geometry. New {here('acceptance_gate.py')} preserves that structural rejection and labels every structurally valid candidate UNQUALIFIED for physical completion, rather than promoting a plausible sector into authenticated evidence. It cannot distinguish byte-identical partial/full histories; no parser can do so from those bytes alone. No firmware or historical parser is changed.
''',
'geometry-acceptance-gate.md':f'''# Phase51 — strict evidence acceptance

**PROVEN structural gate:** reuse unmodified {old('geometry_from_sector.py')}. Require exact4096-byte sector(s); proven mode1/LUN0 physical binding; stock-recognized jump/FAT marker plus55AA; bytes/sector4096; csize power2 in1..128; reserved>0; FATcount1/2; nonzero FAT size; fixed-root alignment; total16-or32 selection; internally consistent stock FAT class; enough FAT entries; primary MBR/VBR selection in stock order; volume and FAT/root/data regions within disk0's normal7980-sector backing. Missing MBR candidate, malformed/incomplete sector or any bound failure means **evidence=INVALID**, infer no geometry. Phase50's five native matches and15 rejection cases remain unchanged. {old('geometry-tests.json')}.

**PROVEN additional acceptance boundary:** correct source unit/firmware, stable selected window, requested LBA/count, exact-length host completion and no-retry containment must accompany the bytes. **UNKNOWN:** a trustworthy independent signal that the lower NOR operation physically completed correctly despite lost status. The Phase51 gate {here('acceptance_gate.py')} returns INVALID for structural failure, otherwise UNQUALIFIED; it has no option to force an authenticated PASS. Adapter fields in Phase50 are derived validators, never captured RAM mount status.

| Candidate validity signal | Assessment |
|---|---|
|SCSI GOOD / CSW residue0 |**PROVEN insufficient:** native failures1/2 also produce them |
|4096 returned bytes |**PROVEN insufficient:** caller always clears/sends that length after returned failures |
|Zero initialization |**PROVEN useful rejection:** catches native no-data failures, excludes tested old-buffer reuse; not a completeness checksum |
|FAT signature/BPB consistency |**PROVEN** rejects distinguishable errors; **STRONG INFERENCE** of meaningful geometry under ordinary successful-read assumptions; not transaction authentication |
|USB transport CRC / saved SHA-256 |**UNKNOWN** actual host transport result; saved hash only records returned bytes and cannot recover lower status; no application-level NOR sector checksum is present in this path |
|Backup VBR / second sector |**UNKNOWN** applicable copy/provenance for this unit; normal bounded FAT12/16 has no mandatory independent backup used by this mount path; MBR+VBR gives structure/binding corroboration, not read-status recovery |
|Repeated identical reads |**PROVEN** byte-identical histories can remain indistinguishable; **UNKNOWN** extra assurance on this unit; not prescribed because a stuck Storage read has no qualified retry/unwind |
|Mounted RAM cross-check |**UNKNOWN** no supported current B1.3 RAM geometry export, perPhase49 |

**PROVEN target equations conditional on authenticated BPB:** N=floor((total−reserved−nFAT*fatsz−rootS)/spc); data=vol+reserved+nFAT*fatsz+rootS; cluster2..N+1 maps to `D4000+1000*(data+(cluster−2)*spc+withinCluster)`. Bound FAT copies/root/FSInfo as well.81000 and82000 are below disk0 base by53000/52000hex (negative normal LBAs53/52hex); valid bounded maps cannot reach them. {old('physical-binding.md')}.

**UNKNOWN current-unit preservation result:** no sector was acquired/authenticated. A hypothetical/model BPB must not close that gate. Geometry proves normal filesystem write bounds only, not unrelated raw-write producers or all boot/background mutation.
''',
'minimum-hardware-read-plan.md':f'''# Phase51 — no admitted hardware query

**UNKNOWN:** the prerequisite of reliably authenticated successful physical read is unmet. Therefore no hardware execution is authorized or recommended by this report. The following is a bounded candidate specification only, not an instruction to enter a mode or read a device.

**PROVEN minimal candidate:** existing transient vendor42/sub0 mode1, deferred150-tick application callback completes to stable mode1; LUN0 READ CAPACITY establishes8192×4096, then one READ10 at USB LBA40hex (64), count1, expected4096 bytes from NOR D4000. Ordinary MIDI and MSD coexist. Normal exit candidate is transientmode0 through the same dispatcher/callback, not UI settings toggle or SCSI eject. No reboot is needed by these native application bodies. {here('mode1-entry-exit.md')}; {old('minimum-sector-plan.md')}.

One VBR sector suffices for superfloppy geometry. A second sector is necessary when the first is MBR and identifies the volume VBR; it materially resolves volume location but does not authenticate lower completion. Additional FAT/backup/data reads are not justified solely to hide the lost-status problem. No read of81000/82000 payloads is needed.

Required before any future use: current-unit/B1.3 provenance; independently established stable mode/window and raw LUN binding; prevent host filesystem automount/repair; no active update, queued mutation, or pre-existing Storage fault; successful-read validity signal beyond byte plausibility or a justified lower completion invariant; explicit containment. Read-only OS access and no host FS mount would be required. No drive index, live command packet, MIDI/USB helper or acquisition script is generated here.

Abort/invalid conditions: timeout, stalled command, USB error, wrong length, changed binding, unexpected metadata or any structural gate failure. Do not save an accepted geometry file, retry, flush, send storage cleanup, force-release semaphores, issue update commands or infer geometry from partial data. Structurally valid but physically unauthenticated data remains UNQUALIFIED. Existing one-shot containment is retained; power-cycling is not certified as a no-persistence substitute for normal exit. {here('geometry-acceptance-gate.md')}; {here('read-error-propagation.md')}.

Smallest remaining offline qualification: exercise the actual37430/37596/controller IRQ and DMA completion predicates at4096 bytes through this coupled wrapper/BOT runner, without replacing physical-read completion with a success seam. Determine whether every native return0 guarantees all geometry-bearing bytes came from the addressed NOR and whether a completed fault can pass the gate. Reuse Phase31 wait/TEF evidence; do not redo completed mapping or invent a new firmware command. USB HAL callback/lifetime and background scheduling limits remain separately stated.
''',
'findings.md':f'''# Phase51 — MSD geometry read safety

**PROVEN:** full existing B1.3 SysEx dispatcher→transient mode1/0→deferred class rebuild executes two entry/exit cycles with zero guarded Storage/persistence/mount/reset calls. This improves Phase50's isolated-handler evidence. USB HAL/scheduler boundaries remain modeled, so complete real-device side effects are not claimed. UI setting entry/exit can persist settings; transient exit itself has no such producer in the tested route. {here('mode1-entry-exit.md')}; {here('mode-cases.json')}.

**PROVEN:** mode1 USB LBA40hex→NOR D4000 is retained. Ten coupled native read cases execute clear→queue wrapper→worker→actual backend bounds/semaphore return→SCSI data→CSW. Four native early-error cases return1/2 yet deliver4096 zero bytes with GOOD CSW and zero residue. The parser rejects those zero sectors; prior successful contents were cleared. {here('read10-physical-path.md')}; {here('read-cases.json')}.

**PROVEN status loss:** wrapper24130 returns the backend status correctly; MSD57ECE ignores it and57EEE returns0. **PROVEN** SCSI success/length alone cannot authenticate NOR success. **PROVEN model limitation:** a hypothetical512-byte DMA plus completion-return is byte-identical to a complete zero-tailed test BPB, so structural validation accepts it. This is not a demonstrated physical TEF success, incorrect geometry, or parser defect. **UNKNOWN:** real partial/error completion reachability and an independent trustworthy completion signal. {here('read-error-propagation.md')}; {here('stale-buffer-analysis.md')}.

**STRONG INFERENCE:** normal fault-free single-sector reads could provide correct BPB geometry without persistent commands. **UNKNOWN:** the full requested admission criterion—safe entry/exit under real callbacks/background context and reliable physical-read acceptance. No current-unit geometry is authenticated. Do not upgrade evidence based on a FAT-looking sector or assumed success. The strict offline gate reports INVALID or UNQUALIFIED, never a fabricated accepted capture. {here('geometry-acceptance-gate.md')}; {here('acceptance_gate.py')}.

The minimal conditional one-sector candidate, MBR exception, abort rules and smallest remaining offline experiment are recorded in {here('minimum-hardware-read-plan.md')}. No hardware action, MIDI opening, transmission, firmware generation/modification or historical candidate change occurred. PriorPhase50 and439 pinned reference sources are checked unchanged in {here('validation.json')}.

MSD GEOMETRY READ SAFETY = UNQUALIFIED
'''}
def main():
    for name,text in reports.items():(OUT/name).write_text(text,encoding='utf8')
    print(f'Wrote {len(reports)} reports')
if __name__=='__main__':main()
