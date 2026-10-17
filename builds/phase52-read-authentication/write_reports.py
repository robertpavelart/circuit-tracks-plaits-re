"""Write Phase52 reports only."""
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def link(p):return f'[{p.name}](<{p.as_posix()}>)'
def here(n):return link(OUT/n)
def old(n,p='phase51-msd-read-safety'):return link(ROOT/'builds'/p/n)
reports={
'transfer-buffer-lifetime.md':f'''# Phase52 — READ10 buffer lifetime

**PROVEN:** normal LUN0 READ10 uses fixed buffer40024000..40024FFF (4096 bytes). SCSI3B508 loads40024000,3B52E passes it to57E88, and3B54E passes the same pointer/4096-byte slice to24754 for endpoint82. Next command/block reuses that address. A normal READ10 is not a512-byte transfer: the512-byte record in this phase is the BPB-bearing prefix of the4096-byte USB response. No truncated512-byte USB result is accepted. {old('b13-0803b27c.asm','phase50-msd-readonly-geometry')}; {old('b13-08057e30.asm','phase50-msd-readonly-geometry')}.

**PROVEN:**57EA2→1A7E4 zeroes all requested4096 bytes before queue wait and raw read. Physical DMA then overwrites some/all of that buffer. After normal return the optional serial-marker filter may change response RAM; our BPB/FAT/root fixtures have no such marker. The buffer remains the returned data after the data stage and CSW, until another clear/write. CSW uses its separate protocol structure. {old('b13-0801a7e4.asm')}; {old('read10-physical-path.md')}.

**PROVEN pointer flow:**24754→389C6 stores the supplied buffer pointer at the selected IN endpoint record+0C, length at+14, then calls4862A. No sector-sized copy occurs in SCSI or these wrappers; the USB driver retains a pointer into the shared buffer. **UNKNOWN:** complete USB FIFO/IRQ ownership/quiescence across real command completion; the native runner snapshots bytes at the TX boundary and models completion before admitting the next command. {here('b13-08024754.asm')}; {here('b13-080389c6.asm')}.

**PROVEN modeled lifetime:** all sequential commands use the same emulator RAM allocation. Each physical-read seam asserts4096 zero bytes before supplying data, irrespective of the previous target/control. Thus a partial target gives `new target prefix + zero suffix`, not `new target prefix + old control suffix` in this model. An actual late DMA/USB race is not disproved by that assertion. Native response clearing, queue wrapper/worker, backend semaphore/release, SCSI and CSW execute; DMA bytes, task wake/queue movement and USB transfer completion are explicit seams. {here('native_sequence.py')}; {here('authentication-experiment.json')}.

**PROVEN fixture correction:** sequential reuse needs both native constructor semaphore bytes backend+8=current1 and+9=maximum1. Phase51's isolated single-read fixture initialized+8 but not+9. Phase52 sets both, matching22F10, and asserts native1BA12 restores current1 after every completed request. No forced release is used; this corrects the sequential test fixture without editing Phase51 or invalidating its single-read status/zeroing observations. {old('08022ed0.asm','phase31-storage-error-recovery')}; {here('b13-0801ba12.asm')}.
''',
'failure-semantics.md':f'''# Phase52 — returned bytes versus physical outcomes

**PROVEN saved evidence:** {here('authentication-experiment.json')} stores exact first512 returned bytes as `returned_512_hex` in each trace, complete4096-byte hashes, command LBA, prior-buffer hash, refresh length and CSW status. Common synthetic vectors are included; all vector bytes after offset511 are zero. No transcript is an actual-unit sector. A timeout records `returned_512_hex=null`, not an invented zero USB reply.

| Outcome | First512 bytes / full USB response | Meaning |
|---|---|---|
|A complete success model |Exact source512,4096 bytes, GOOD |**PROVEN** native path under physical-completion seam |
|B no DMA bytes, completion nevertheless returned |512 zeroes,4096 bytes, GOOD |**PROVEN** fault-model result; native source of false completion **UNKNOWN** |
|Native early bounds/busy1/2 |512 zeroes,4096 bytes, GOOD |**PROVEN** Phase51 native status results, reused; not newly injected as TEF |
|C n prefix bytes, completion returned |source[0:n] plus zero tail;4096 bytes, GOOD |**PROVEN** model for0<=n<=512; not silicon fault reproduction |
|D timeout / partial128 then timeout |No data stage or CSW; active wait remains |**PROVEN** modeled stop at physical boundary; no subsequent command issued on that Model |
|E stale completion, no new DMA bytes |Zero-filled response, indistinguishable fromB |**PROVEN** upper-path behavior; actual stale notification/IRQ producer **UNKNOWN** |

The unread portion is deterministically zero under the tested clear/prefix/serialized-completion model. Prior target/control/poison is not retained. **UNKNOWN:** unread contents under late concurrently active DMA or USB ownership violations. Prior Phase31 TEF/missing-completion cases wait indefinitely, not return a success status; those are not reclassified asB/E. {old('findings.md','phase31-storage-error-recovery')}; {old('read-error-propagation.md')}.

**PROVEN:**18 independent modeled fault placements cover T1,C1,T2, including no-byte/partial128/partial512/stale-completion/timeout/partial-timeout. Timeout sequences stop immediately and never retry a live request. Native early-return error tests are reused rather than repeatedly disturbing held ownership. Physical partial-completion hypotheses are labeled throughout.

Replay distinctions: replaying the immediately preceding control intoT2 fails target equality/BPB. A hypothetical older, internally valid target substituted for bothT1/T2 passes all host comparisons against a different valid control. That is an observational ambiguity at the physical-data seam, **not proof a native firmware cache replays old BPBs**. Native reachability is **UNKNOWN**; do not infer wrong current geometry was observed. {here('authentication-experiment.json')} `immediate_control_replay`, `older_target_replay`.
''',
'control-sector-strategy.md':f'''# Phase52 — what control sectors establish

**PROVEN:** mode1 maps USB LBA40hex→D4000. In the reference normal-layout model, target64 is VBR, controlA65 is first FAT and controlB73 is fixed-root start. These are distinct physical sectors in the same internal disk, all read-only metadata. For another valid layout, derive controls from candidateBPB: USB LBA64+fatbase, then64+dirbase. Do not hardcode65/73 for the current unit. No current-unit sector contents or full512-byte inequality are known. {old('physical-binding.md','phase50-msd-readonly-geometry')}; {here('native_sequence.py')} `SECTORS`.

**STRONG INFERENCE safest candidate:** the first FAT sector is preferable to arbitrary file/data sectors because its location is derived, it is metadata, and reserved FAT entries give some structural checks. This is conditional on a bounded candidateBPB and proven binding; it is not authenticated by location alone. Root metadata is a possible second control but may be mostly/all zero. A second FAT copy may be identical to the first and is not independent control entropy.

**PROVEN baseline:** native T1→C1→T2 satisfies full4096-byte equality T1=T2 and inequality T1!=C1, as well as the same512-byte comparisons and BPB validation. **PROVEN counterexample:** no-byte false completion atC1 returns zeroes; T1=T2!=zero still passes the requested basic rule. Adding a control-FAT header check rejects that zero-control case, but a partial FAT prefix can reproduce the full normal zero-tailed FAT sector and pass even full4096-byte comparisons. {here('authentication-experiment.json')} `baseline`, `independent_faults`.

**PROVEN two-control limit:** T→A(partial8)→T→B(partial27)→T passes equality of all targets, full-sector target/control inequalities and A!=B. The modeled FAT's last nonzero byte is7; root directory's last nonzero byte is26. After clearing, those short prefixes are byte-identical to their full sectors. This is not incorrect target geometry; it disproves using the sequence to certify that every control read fully refreshed its buffer. {here('authentication-experiment.json')} `five_read_partial_controls` includes all five native traces.

**PROVEN:** interleaving does disturb the buffer at successful control-return, but that disturbance is erased before the next target DMA. It cannot act as a host-selected nonzero fill pattern for the next target. More controls cannot replace the missing native completion/provenance contract merely by adding comparisons. **UNKNOWN:** a finite normal-read sequence that closes the actual fault model rather than the restricted prefix model. No smallest fully authenticating sequence has been qualified.
''',
'partial-dma-exhaustive.md':f'''# Phase52 — all513 target prefix lengths

**PROVEN:** new native coupled runner independently executes T1 complete→C1 complete→T2 n-byte-prefix/completion for every n=0..512 inclusive. Exact same physical buffer is reused within each triple. All513 cases assert native full clear, op1 only, backend release,4096-byte TX and GOOD CSW. Full512 outputs,4096 hashes and all command traces are saved. {here('experiment.py')}; {here('native_sequence.py')}; {here('authentication-experiment.json')} `partial_T2_exhaustive`.

| n refreshed into T2 | Full512 comparison + BPB gate | Full4096 comparison + control gate |
|---|---|---|
|0..511 (512 cases)|reject all |reject all |
|512 (one case)|accept |accept for this zero-tailed4096-byte source |

**PROVEN narrow positive result:** in a contiguous forward-prefix model, every accepted T2 refreshed all512 BPB bytes. Offset511 must beAA after a zero clear; reaching that offset requires writing the entire prefix under this model. No stale-control suffix remains, and no target prefix shorter than512 is falsely accepted. This is not merely testing one or two differing signatures: exact full512/4096 equality is evaluated, and the nonzero footer explains the exhaustive boundary.

**PROVEN limit:** atn512 only512 of4096 physical-block bytes were refreshed. Full4096 equality still passes because the expected tail is zero. This does not violate the 'all512 metadata bytes refreshed' condition, but it cannot certify a complete4096-byte physical transfer. Likewise partial controls can match their full sectors. Neither example demonstrates an incorrect BPB.

**UNKNOWN remaining contract:** native lower execution must guarantee that delivered bytes are a contiguous correctly addressed prefix of the current command, and that old DMA/USB activity cannot supply them after clear. The experiment deliberately models this boundary; it cannot prove its own premise.

**PROVEN new native setup check:**1C072 branches at1C112 past address/count programming if DMA EN already1, and still returns0 at1C13C. Two native helper tests show EN0 programs M0AR40024000/NDTR4096; EN1 preserves old M0AR20025000/NDTR123 and returns0. These are modeled register-memory states, not evidence EN remains1 after a real completed read.37430 does not check this setup result or independently compare NDTR after37596. {here('b13-0801c100.asm')}; {here('DMA-setup-cases.json')}; {old('b13-08037430.asm')}.

Thus an EN0/current-command/quiescence invariant remains necessary before extending the prefix-model proof to real B1.3. No completion bit or malformed peripheral state is assumed to occur physically. No unsafe retry follows a modeled timeout.
''',
'cross-sector-consistency.md':f'''# Phase52 — filesystem relations are secondary evidence

**PROVEN BPB gate:** reuse Phase50 parser unchanged: stock jump/FAT markers,55AA,4096-byte sectors, power2 cluster size, reserved>0, FATcount1/2, sufficient FAT size, exact total selection, root alignment, stock-derived FAT class, data/cluster bounds and physical partition extent. The table text is not the FAT-class oracle. Native mount already matches five normal fixtures. {old('geometry_from_sector.py','phase50-msd-readonly-geometry')}; {old('geometry-tests.json','phase50-msd-readonly-geometry')}.

**PROVEN relations:** firstFAT=vol+reserved; secondFAT=firstFAT+fatsz whennFAT2; fixedroot=firstFAT+nFAT*fatsz; data=fixedroot+rootEntries*32/bps. Valid clusters2..N+1 map through D4000+1000*(data+(cluster−2)*spc+withinCluster). For an authenticated bounded BPB, normal domains cannot reach81000/82000 below D4000. No current-unit BPB is acquired here.

| Cross-sector relation | Evidence value and limitation |
|---|---|
|First FAT reserved entries/media descriptor |A plausible normal FAT16 corroboration; the model usesFFF8/FFFF and allocated cluster entries. **UNKNOWN** exact current bytes. Native mount197A0 does not authenticate the volume by checking these FAT entry bytes, so literal model values are not a mandatory current-unit signature. |
|Two FAT copies |**PROVEN** stock window-flush1859A writes the second copy when configured. **STRONG INFERENCE** normally synchronized metadata; copies can share the same read failure/replay and are not independently authenticated. |
|Fixed-root location and directory records |BPB determines location; plausible entry clusters can be checked against2..N+1. **UNKNOWN** current names/allocation; zero unused entries/suffixes are legitimate and weaken completeness detection. |
|Reserved sectors |Only BPB/signature and volume offset are established; no supported invariant says all remaining reserved sectors have a fixed independent payload. |
|FAT32 backup VBR |Not used as an assumption. Bounded32MiB internal4096-byte layout cannot normally reach FAT32 cluster counts; no mandatory FAT16 backup sector is established by this mount. |

Native sources: {old('app-08019734.asm','phase48-current-unit-geometry')}; {old('app-0801855c.asm','phase46-msd-filesystem-closure')}; {old('app-080185de.asm','phase46-msd-filesystem-closure')}. No current-unit FAT chain, root, volume label or fixed reference layout is inferred.

**PROVEN logical limitation:** coherent BPB/FAT/root bytes can be returned unchanged from a previous coherent snapshot and retain these relations. Host-side consistency is useful for rejecting distinguishable corruption, but it cannot alone attest current physical provenance. The older-target substitution test is a model of that ambiguity, not a newly found native replay path. {here('authentication-experiment.json')}.
''',
'authenticated-read-plan.md':f'''# Phase52 — authenticated hardware plan withheld

**Authentication answer: UNKNOWN.** Single remaining ambiguity: no qualified current-command DMA/USB ownership-and-source invariant proves that an accepted512-byte BPB came from the intended current NOR read rather than a late/old operation or replay. The restricted contiguous-prefix/zero-clear model passes the required target freshness check; actual native reachability of broader stale-completion/replay outcomes is not established. More equality-only controls do not prove that invariant.

**PROVEN:** T→C→T is insufficient to detect every modeled control failure. T→A→T→B→T still accepts byte-identical partial controls. **PROVEN:** within the tested prefix model, no n<512 target result passes; n512 is fully refreshed metadata but incomplete4096-byte physical block. These distinct findings must not be collapsed into either 'all partial reads pass' or 'physical authentication proven'. {here('partial-dma-exhaustive.md')}; {here('control-sector-strategy.md')}.

Because the requested answer is not PROVEN YES, no future hardware procedure is qualified or issued. There is no acquisition script, port operation, device enumeration, firmware action, filesystem mount/repair or new binary. Model addresses64/65/73 are evidence fixtures, not an instruction to read those LBAs on the unit. Existing Phase51 acceptance boundary remains INVALID on structural failure, otherwise UNQUALIFIED for physical authentication. {old('acceptance_gate.py')}.

Smallest next offline question: establish or reject the existing37430/37596/IRQ-to-DMA ordering invariant that EN is clear before1C072, all BPB-bearing bytes correspond to this read, and USB consumes the buffer before reuse. The native EN1-skip behavior is now explicit. This requires closing the actual completion boundary rather than adding more control reads or another firmware diagnostic. No new experiment is started here.
''',
'findings.md':f'''# Phase52 — read interleaving authentication

**Authentication answer: UNKNOWN.** The proposed finite read sequences have not qualified current-unit physical-read authentication. The single remaining ambiguity is whether native DMA/USB ownership and completion guarantee fresh, correctly addressed BPB bytes from the current command; repeated equality cannot establish that boundary by itself.

**PROVEN:**513 native coupled T2 prefix cases cover0..512. Every prefix shorter than512 is rejected;512 passes with all BPB bytes refreshed under the modeled contiguous-prefix assumption. The actual READ10 response remains4096 bytes, so this is not proof all4096 were refreshed. {here('partial-dma-exhaustive.md')}; {here('authentication-experiment.json')}.

**PROVEN:** basic T1=T2 andT1!=C1 accepts a zero-returning control failure. A control header check rejects that case, but partial zero-tailed controls pass full-sector comparisons. Two-control/five-read sequence does not fix that. Immediate-control replay is rejected; an older valid target substituted twice at the physical-data seam passes. **UNKNOWN:** an actual native producer for that older-target replay; no incorrect physical-unit geometry is claimed. {here('control-sector-strategy.md')}; {here('failure-semantics.md')}.

**PROVEN:** new native DMA helper tests return0 without changing old address/count when EN is already1. This exposes the precise invariant still needed, not a hardware reproduction of a stale transfer. **STRONG INFERENCE:** a fault-free correctly serialized read could yield accurate geometry, and BPB/FAT/root checks offer corroboration. They remain secondary evidence. {here('DMA-setup-cases.json')}; {here('cross-sector-consistency.md')}.

Seven requested reports and exact512-byte model transcripts are saved. Eighteen independent fault placements are tested; all six timeout/partial-timeout sequences stop without a subsequent request. Historical Phase51 and439 pinned reference sources are preserved; no hardware, MIDI, firmware generation/modification/transmission or new diagnostic occurred. Validation: {here('validation.json')}. No hardware plan is admitted: {here('authenticated-read-plan.md')}.

MSD PHYSICAL READ AUTHENTICATION = UNQUALIFIED
'''}
def main():
    for n,t in reports.items():(OUT/n).write_text(t,encoding='utf8')
    print(f'Wrote {len(reports)} reports')
if __name__=='__main__':main()
