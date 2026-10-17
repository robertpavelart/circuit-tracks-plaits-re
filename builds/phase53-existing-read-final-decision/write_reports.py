"""Final decision documentation; no new firmware, protocols or hardware plans."""
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def link(p):return f'[{p.name}](<{p.as_posix()}>)'
def here(n):return link(OUT/n)
def old(n,p='phase52-read-authentication'):return link(ROOT/'builds'/p/n)
reports={
'buffer-producers.md':f'''# Phase53 — existing transfer-buffer producers

**PROVEN:** exact B1.3 SHA-256 `2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41`. Geometry READ10 uses40024000..40024FFF (4096 bytes); first512 bytes are the BPB prefix, not the USB block length. Producer57E88 first clears the full requested buffer, then fills it through NOR wrapper24130/DMA37430. SCSI3B54E→24754→389C6 retains the same pointer in the IN endpoint record;4862A starts endpoint hardware, not a separate sector reconstruction. {here('b13-0803b27c.asm')}; {here('b13-08057e30.asm')}; {old('b13-08024754.asm')}; {old('b13-080389c6.asm')}; {here('b13-0804862a.asm')}.

| Producer / normal path | Classification | Full512 deterministic independent of NOR? |
|---|---|---|
|57EA2→1A7E4 clear before READ |CPU-generated zeroes across4096 |**PROVEN** internal full clear; no distinct second pattern; target repeats this same clear |
|57ECC→24130→worker→22F94→37430 |External-NOR DMA |No; this is the operation being authenticated |
|57EDC serial-token replacement |Conditional RAM copy,14 bytes per found token |No independent512 guarantee; requires returned NOR bytes and identity cache |
|REQUEST SENSE03 |CPU clear/fill response18 bytes |No |
|INQUIRY12 |Fixed flash→RAM copy36 bytes (EVPD7) |No |
|MODE SENSE1A/5A |Fixed flash→RAM copy8 bytes |No |
|READ CAPACITY25 |CPU-generated8 bytes |No |
|READ FORMAT CAPACITIES23 |CPU clear/fill12 bytes |No |
|WRITE102A reception,3B61C/634 |Host-data buffer, then NOR write path if admitted |Not a read-only producer; ordinary entry rejected by writeprotect callback57E48=1 |
|BOT26E5C generic data-IN |Consumer of generated response pointer |No producer; response length capped, no512-byte padding generated |
|CBW / CSW |Protocol RAM2000679C /200068C4 |Not this buffer;31-byte CBW and13-byte CSW do not fill it |
|SD-backed operation |No SD read callback in initialized LUN0 backend |No existing supported path identified |

**PROVEN new native tests:** nine ordinary data-in cases execute exact B1.3 dispatcher. Actual generated sizes are36/7/18/8/8/12 as above; all transmitted response bytes are initialized for those model states. PoisonA5 in buffer offsets36..511 remains unchanged after every non-NOR generated command. The same destination is used but no command fully initializes512 bytes. Merely requesting a larger host allocation does not enlarge these generated payloads. {here('producer_cases.py')}; {here('producer-cases.json')} `commands`.

**PROVEN registered-path closure:**3B27C dispatch and resolved initialized table cover all normal MSD opcodes; unsupported/vendor SCSI opcodes fall to3B704 sense/error rather than an arbitrary buffer/memory reader. TUR/startstop/prevent/verify are no-data/status paths. No new command or malformed request was tried. {here('b13-0803b27c.asm')}; {old('initialized-ram-callback.md','phase46-msd-filesystem-closure')}.

**PROVEN census scope:** whole B1.3 byte/literal scan plus PC-relative-load scan finds real40024000 literals at8026F18 and803B788, consumed by the BOT/SCSI paths listed above. No initialized-data pointer into40024000..40024FFF is found. Four additional unaligned byte patterns resemble subrange addresses but have no PC-relative consumers in the scan; they are candidate bytes, not established buffer producers. {here('existing-paths.json')}. This is not a theorem about arbitrary computed aliases or corrupted execution. No concrete additional supported producer is left unresolved; hypothetical aliases do not supply an existing usable command.
''',
'synthetic-msd-sectors.md':f'''# Phase53 — mode1 LBAs00..3F are NOR-backed

**PROVEN:** every one of the64 LBAs00..3F takes57E88's same valid-block branch, clears its response, and invokes raw NOR wrapper24130. There is no branch by LBA within this range selecting a virtual sector, flash template, RAM image, synthesizedMBR, or fixed zero response. Native isolated callback tests record every physical start/end and one4096-byte wrapper read per LBA. {here('producer-cases.json')} `mode1_LBAs_00_3F`; {here('b13-08057e30.asm')}.

For each LBA L in00..3F: `physical_start=94000+1000*L`, end=start+FFF. Thus00→94000..94FFF,01→95000..95FFF,...,3F→D3000..D3FFF. The JSON contains all64 individual rows, not only an inferred total. The range exactly covers the selected window's nominal94000..D3FFF backing. LBA40 beginsD4000, the separately mounted filesystem region. {old('b13-08038c10.asm','phase50-msd-readonly-geometry')}.

**PROVEN classification for all64:** external serial NOR-backed; not SD, not DSP SDRAM, not RAM-backed or firmware-generated sectors. A preformatted or help/MBR-looking image could reside in that NOR region, but **UNKNOWN** actual current-unit contents. A sector containing zeroes still depends on a physical NOR read. Zeroes after a failed read are the caller's clear, not a qualified synthetic-sector command. The conditional serial-text substitution does not change that dependency.

**PROVEN:** capacity57E34 remains8192×4096 regardless of the nominal selected-window end, so a capacity response is not evidence of a512-byte synthetic façade or a generated filesystem. Every tested low LBA uses the physical path. No expected512-byte payload can be provided for those addresses without acquiring their NOR contents, which Phase53 does not do.

Tests inject no source bytes and stop at the raw wrapper seam; they prove routing, not physical sector values. No TARGET/CONTROL sequence from Phase52 was repeated. {here('producer_cases.py')} `low_lba`.
''',
'deterministic-poison-analysis.md':f'''# Phase53 — deterministic poison decision

**PROVEN:** a full internal zero overwrite exists: READ callback57EA2→1A7E4. It is already the known initial state before every target read. No existing normal read-only non-NOR command establishes a second full512-byte pattern; non-NOR SCSI generators touch at most36 bytes. Any short-header changes made before TARGET are overwritten by TARGET's own4096-byte zero clear. This means A supplies only the already-tested single zero pattern, not a new authentication primitive. {here('buffer-producers.md')}; {here('producer-cases.json')}.

**PROVEN collision limit:** if poison P[i] equals real target T[i] in an unread position, returned bytes alone cannot prove that position was refreshed. The previous zero-tailedBPB counterexample yields exactly identical4096 bytes after512-byte refresh versus4096-byte refresh. Its512 metadata bytes really were refreshed; it does not prove an incorrect BPB. The general missing property is current-read byte provenance, not ordinary BPB plausibility. {old('partial-dma-exhaustive.md')}; {old('authentication-experiment.json')}.

Two-pattern mathematical condition: suppose two known full512-byte patternsP andQ differ at every position, remain intact until current-target writes, and any refreshed byte equals the correctly addressed currentT[i]. Equal final vectors then imply each position was refreshed in at least one run: both unrefreshed would leave unequalP[i]/Q[i]. For forward-prefix writes this also implies at least one run refreshed all512 bytes. This can establish the combined metadata value under those assumptions; it does not require each run individually complete.

**PROVEN not implementable by inspected B1.3 interfaces:** no operation chooses two such full patterns, and57EA2 collapses both hypothetical pre-target patterns to the identical zero vector anyway. Short INQUIRY/MODE SENSE/other headers cannot survive this clear or cover the full512-byte requirement. No command skips the target clear in a normal accepted READ10. A software-only host validation change cannot manufacture that missing primitive.

**PROVEN NO for the proposed existing-interface poison mechanism:** neither a guaranteed-different target pattern nor a surviving pair of deterministic full-buffer poisons is available. No513-length rerun was performed because no new qualified poison producer was found and the user prohibited repeating Phase52. The saved513-case evidence is reused unchanged. {old('validation.json')}.

No full-buffer fill via WRITE10, arbitrary RAM poke, malformed command, firmware modification or diagnostic installation is used as a substitute for a read-only primitive.
''',
'completion-signals.md':f'''# Phase53 — internal completion state versus host observability

| Candidate | Internal source | Existing observable read-only interface / decision |
|---|---|---|
|DMA EN/NDTR/TC flags |DMA2 stream7,400264B8/BC and status registers |**PROVEN** internal state; no exported field in resolved SCSI responses or inspected supported B1.3 status handlers |
|QSPI TCF/softwarebit0 |IRQ22826→37596 |Internal wait condition, not returned alongside payload. Native read setup's EN1-skip returns0; no host NDTR attestation. |
|Backend return1/2/0 |22F94→worker240C4→wrapper24160 |MSD57ECE discards it and57EEE returns0; not independently observable through REQUEST SENSE |
|Wrapper pending/sync/status |RAM wrapper+C/+10/+18 |No supported B1.3 RAM export; internal queue drain is not a host completion counter |
|SCSI sense |3B732 queue, REQUEST SENSE03 |Only errors queued by SCSI.57E88 hides underlying failures, so no corresponding medium error is enqueued. Phase51 native failures produce GOOD CSW and zero residue. |
|TUR00 |table+8→57E44 |Always returns0; not a test of last NOR request or DMA state |
|READ CAPACITY/FORMAT |table+4→57E34 |Fixed8192/4096, not success/byte count of prior read |
|INQUIRY/MODE SENSE |Fixed flash response tables |No per-read completion fields |
|VERIFY2F |3B6AA checks BYTCHK/LBA bounds |No NOR read/checksum or comparison callback; cannot attest the previous transfer |
|BOT count/CSW |RAM protocol bookkeeping |Counts submitted USB bytes; no lower physical byte count. Successful CSW survives native backend errors. |
|USB descriptor/status |Enumeration / endpoint state |Does not carry DMA/QSPI status or source address |
|Vendor42 status / identity; vendor41 parameters |24918/2527C/24A10 |Mode/identity/parameter fields, not a NOR completion export; no supported arbitrary register read contract |
|rdiag/ctremote mem |Known diagnostic-build command2 |**PROVEN absent from exact B1.3**; host tool availability is not installed-firmware capability |

Sources: {here('b13-0803b27c.asm')}; {here('b13-08026d64.asm')}; {here('producer-cases.json')}; {old('read-error-propagation.md','phase51-msd-read-safety')}; {old('read-cases.json','phase51-msd-read-safety')}; {old('DMA-setup-cases.json')}; {old('b13-readonly-interfaces.md','phase49-existing-geometry-reader')}.

**PROVEN NO under the inspected supported-interface contract:** the required independent physical completion evidence is not exposed. A flag existing internally is not a host-observable signal. Generic sense, a GOOD CSW, fixed capacity and transport byte count cannot recover discarded status. No concrete existing completion-export mechanism remains unresolved. This does not assert that the hardware never completes reads correctly or that all unknown firmware behavior is impossible.

Multi-sector reads: **PROVEN**3B4FC..3B51C chooses at most1000hex bytes and converts this to callback count1 for4096-byte sectors; each slice calls the same57E88, loses its status and reuses the same buffer.3B552..568 advances bookkeeping. There is no separate end-to-end physical checksum/count signal. Because no concrete stronger invariant exists, no multi-sector repetition/fault experiment was pursued. {here('b13-0803b27c.asm')}.

The established TEF/missing-completion wait behavior is retained, not rerun. No physical/DMA fault was induced in Phase53. {old('findings.md','phase31-storage-error-recovery')}.
''',
'existing-b13-final-verdict.md':f'''# Phase53 — final existing-B1.3 decision

**PROVEN NO.** Under the user's decision definition, the inspected existing normal B1.3 interfaces cannot establish filesystem-geometry physical-read authenticity sufficiently for the preflash preservation decision. This existing-MSD authentication branch is closed; no further READ10 repetition/control scheme is proposed.

**PROVEN:** B1.3 exposes the correct physical storage path: mode1 USB LBA40hex→D4000. **PROVEN:** it discards lower-read failure information. **PROVEN:** low LBAs00..3F are all NOR-backed, generated SCSI responses supply at most36 bytes, and the only full deterministic clear supplies zeroes that the target itself reapplies. **PROVEN:** no independent completion signal is exported by the inspected supported SCSI/status interfaces. Therefore neither candidate mechanism A nor B closes the missing authenticity contract. {here('buffer-producers.md')}; {here('synthetic-msd-sectors.md')}; {here('deterministic-poison-analysis.md')}; {here('completion-signals.md')}.

This is a decision about **sufficiency of the existing interfaces**, not a claim that a real BPB was corrupted or a universal impossibility theorem about undocumented/memory-corrupt execution. Native/data-flow closure covers the registered MSD dispatcher, initialized callbacks and the supported protocol inventory. Raw scan limitations and unknown physical fault incidence are retained. There is no specific existing usable mechanism pending that would justify another UNQUALIFIED iteration.

Current-unit geometry consequently remains unqualified through existing B1.3 MSD alone. Reference geometry, valid-looking BPBs, matching repeated reads or an internal DMA flag must not be promoted into authenticated current-unit evidence. Earlier bounded mapping and parser results remain valid in their own scopes.

Conceptual next options only:

| Option | Consequence |
|---|---|
|A — explicitly accept geometry preservation as hardware-only uncertainty |Requires an explicit user decision to accept the remaining uncertainty. It does not turn the offline evidence gate into PASS, authenticate geometry or authorize a firmware/hardware action. |
|B — separate minimal read-only diagnostic with correct success/failure propagation |Could expose the missing contract, but must preserve source/address/count provenance and report physical completion/errors correctly. Merely forwarding22F94's normal0 or adding a payload CRC is insufficient where the underlying DMA/wait contract remains unqualified. Existing TEF quarantine/no-retry limits still apply. Separate design, validation and authorization would be needed. No diagnostic is designed, generated, installed or transmitted here. |

Neither option is selected or executed in Phase53. This report does not promote any historical firmware candidate or recommend hardware action.
''',
'findings.md':f'''# Phase53 — existing read path final decision

**PROVEN NO.** Existing unmodified B1.3 does not provide the required full-buffer authentication mechanism or independently observable physical-read completion signal through the inspected supported interfaces. The existing-MSD authentication branch should stop. {here('existing-b13-final-verdict.md')}.

**PROVEN:** all64 mode1 LBAs00..3F invoke external-NOR reads; none is a synthetic firmware/RAM sector. Nine native non-NOR SCSI data-in cases generate at most36 bytes in the shared4096-byte buffer, leaving offsets36..511 unchanged. The target's own full zero clear exists but supplies no second surviving poison pattern. {here('producer-cases.json')}; {here('buffer-producers.md')}.

**PROVEN:** the necessary backend status is discarded before host success/sense handling. Internal DMA/QSPI/wrapper fields have no exported completion contract in the existing supported interface inventory. Multi-sector slicing uses the same lossy callback. {here('completion-signals.md')}.

**STRONG INFERENCE:** ordinary fault-free reads could return accurate BPB geometry. **UNKNOWN:** actual-unit geometry and physical fault incidence; neither changes the interface-sufficiency decision or supplies an unresolved concrete mechanism. No claim is made that a wrong BPB was captured.

The six requested reports, exact-image census, nine native generator tests and64 isolated low-window binding tests are saved. Phase52 TARGET/CONTROL experiments were not repeated. Phase52 evidence and439 pinned reference sources remain unchanged. No hardware/port access, firmware generation/modification/transmission or new diagnostic occurred. {here('validation.json')}.

OptionsA (explicit uncertainty acceptance) andB (separately qualified minimal diagnostic) are compared conceptually in {here('existing-b13-final-verdict.md')}; neither is initiated.

EXISTING B1.3 GEOMETRY AUTHENTICATION = FAIL
'''}
def main():
    for n,t in reports.items():(OUT/n).write_text(t,encoding='utf8')
    print(f'Wrote {len(reports)} reports')
if __name__=='__main__':main()
