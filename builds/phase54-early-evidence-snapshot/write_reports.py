"""Phase54 architecture decision; writes documentation only."""
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def link(rel,label=None):
    return f'[{label or Path(rel).name}](<{(ROOT/rel).as_posix()}>)'
def here(name):return link('builds/phase54-early-evidence-snapshot/'+name)
def old(phase,name):return link('builds/'+phase+'/'+name)
def save(name,text):(OUT/name).write_text(text.strip()+'\n',encoding='utf8')

def main():
    inspection=here('read-inspection.json');tests=here('reader-boundaries.json')
    completion=old('phase31-storage-error-recovery','findings.md')
    settings=old('phase47-filesystem-state-closure','startup-persistence.md')
    background=old('phase45-nor-mutation-closure','background-write-analysis.md')
    geometry=old('phase47-filesystem-state-closure','findings.md')
    ram=old('phase45-nor-mutation-closure','heap-stack-status.md')
    transport=old('phase42-exact-rdiag-integration','findings.md')
    save('stock-read-lifetimes.md',f'''
# Phase54 — stock read lifetimes

**PROVEN:** inspected instruction ranges are byte-identical across official stock, published B1.3, clean SC35D8 and the existing Phase44 corrected research image. Their SHA-256 identities and per-range comparisons are in {inspection}; no image was generated or changed. Direct-call candidates from a halfword scan are corroborated by the contiguous caller listings below; the scan alone is not a complete indirect call graph.

## A — original NOR81000..81016

**PROVEN:** application Main0801D4B0 calls identity initialization at0801D4B4→0801EC80;0801ECB6 calls0802520C. The wrapper read is BLX at08025220, offset81000, length17hex=23, destination20006868..2000687E. Global20006968 selects the NOR queue wrapper (captured object2000AC94, vtable0805B1D8, +C→08024130). Wrapper→23F68 enqueue→23FD6 wait→Storage24014→backend22F94→37430. Backend/controller addresses are physical ARM addresses, not DSP external SDRAM. Sources: {here('app-0801d3e0.asm')}, {here('app-0801ec80.asm')}, {here('app-0802520c.asm')}, {completion}.

**PROVEN, conditional on successful complete physical read:** all23 original bytes are present on return at08025222. MOVS r2,#0 at25222 changes no evidence byte; the final intact instruction boundary is immediately **before08025224**, whose STRB r2,[r4,#E] changes destination20006876 (offset14 decimal). The first transformation/overwrite is exactly this zeroing, not a NOR write. Capturing before25224 preserves the original byte14; dumping the later identity cache does not. A later identity setter/write08025228/2523E is an independent mutation path. {here('app-0802520c.asm')}.

**PROVEN:** the bootloader has an earlier read, Main08003A10→08005D98 (call03A42), wrapper global200054DC, destination2000546C..20005482, length23. BLX05DAC returns at05DAE; MOVS r2,#0 then STRB05DB0 zeroes byte14 at2000547A. Last intact boundary: before05DB0. This boot buffer has no established retention contract across application startup/scatter initialization; a bootloader hook is a different, unqualified architecture and is not proposed as an already available application patch. {here('boot-08003a10.asm')}, {here('boot-08005d98.asm')}, {old('phase45-nor-mutation-closure','boot-to-idle-mutation-closure.md')}.

## B — original NOR82000..821FF

**PROVEN:** Main0801D582→0801F51E, selector0→0801F554,0801F576→0802108C,080210BE→08035E28. At table ordinal14 the descriptor080567EC supplies source82000 and count0100 (256 sixteen-bit words); extra source offset is0. Native setup doubles count to512 and calls08047C6C at08035EE2. Destination is [20006A00],20005148 in the authenticated running-RAM fixture:20005148..20005347. Assignment0801F55A/55E copies [2000327C] into20006A00; this pointer provenance is not proof of a new fixed retention allocation. {here('app-0801d550.asm')}, {here('app-0801f478.asm')}, {here('app-0802108c.asm')}, {here('app-08035e28.asm')}; prior destination provenance: {link('notes/p0282-0386-reclaim-qualification.md')}.

**PROVEN:** resource helper47C6C maps r0/r1/r2 to wrapper arguments (offset/destination/length), BLX47C7E→24130 and POP47C80 preserves R0 status. First caller return instruction is08035EE6. It immediately replaces R0 with the staging-pointer literal, with no success check. At35EEE→2968E→3BA78 the512 bytes are sent to DSP0 X:C00..CFF with SHI in16-bit mode;35EF4 restores24-bit mode. The ARM branch does not apply an in-place evidence conversion. At35F08/35F0C it advances to another descriptor and repeats35EE2 with the **same staging buffer**; the next physical read can overwrite its beginning, and later table jobs reuse it. Source lifetime is therefore one read/upload iteration, not until USB enumeration. The earliest known next native read submission is35EE2 on the next iteration; the first actual overwrite is asynchronous DMA, with no single ARM STR instruction marking that instant. {here('app-08047c6c.asm')}, {here('app-08035e28.asm')}, {here('app-0802968e.asm')}, {here('app-0803ba78.asm')}.

**UNKNOWN:** a universal time duration or arbitrary-interrupt writer exclusion for this buffer. Copy at35EE6 is the narrowest identified point before stock consumers and reuse; it still requires authenticated completion and ownership proof. No claim is made that the subsequent DSP values are the original512-byte ARM evidence representation.

## Native boundary checks

**PROVEN:** six fresh tests run unmodified instructions with synthetic backend outcomes0/1/2. Identity read arguments are exactly81000/20006868/23; byte14 is zeroed even after failure. Resource read arguments are82000/20005148/512; the unmodified caller reaches upload for all three statuses. Data remains exact at the first return boundaries in the success models; failure models retain seeded stale bytes. These tests establish instruction behavior and the need for status gating, **not** successful DMA, actual NOR contents or full boot. {here('reader_boundaries.py')}, {tests}.
''')
    save('writer-ordering.md',f'''
# Phase54 — source-read ordering

**PROVEN:** application order is identity read0801D4B4→1EC80→2520C; filesystem constructor/mount entry0801D4C0→1F0A8; content/settings construction0801D4C4→1F0F0 (includes1FAD4→2CFB8→2D060); initialization/service loop; then0801D582→1F51E→selector0/1F554→1F576→2108C→35E28→82000 read. This straight-line ordering is common to all four inspected application images. This is static instruction-order evidence, not a completed cold-boot scheduler replay. {inspection}, {here('app-0801d3e0.asm')}, {here('app-0801d550.asm')}, {here('app-0801f0a8.asm')}, {here('app-0801f900.asm')}, {here('app-0801f478.asm')}.

| Producer/stage |81000 application snapshot |82000 stock-read snapshot |
|---|---|---|
| Filesystem mount1F0A8 |PROVEN before this Main call |PROVEN after this Main call |
| Settings validation2D060 |PROVEN before this constructor |PROVEN after constructor; valid/missing case can be read-only, but a cleanup branch exists |
| Settings delete/flush |PROVEN before the Main startup producer |UNKNOWN exclusion: conditional startup DELETE+flush precedes this read if selected |
| Settings-change callback/project/session persistence |STRONG INFERENCE later normal Main feature activity; no complete earlier asynchronous exclusion |UNKNOWN ordering of every callback/queued write before first table read |
| MSD |PROVEN inherited diagnostic normal WRITE10 protection rejects mutation; scheduling before A does not defeat that policy |PROVEN same normal write-protection invariant; no arbitrary B1.3 mode assumption or superseded malformed-host blocker |
| Background persistence |PROVEN before the later Main initialization stages; UNKNOWN complete earlier task/IRQ roots |UNKNOWN full stock background ordering; no invented B1.3 autosave timer |
| Updater metadata/installer |PROVEN selected selector0 installation ranges exclude A; no automatic identity rewrite found in reviewed normal boot |PROVEN selected selector0 installation ranges exclude B; no automatic resource rewrite found in reviewed normal boot |
| SC35D8 persist19 resync |PROVEN reviewed custom hook is RAM/DSP work, not raw NOR mutation |PROVEN same; stock file save surrounding it remains a separate obligation |

**PROVEN:** startup settings are0:/Tracks/Globals/00_GLOB.cg,128 bytes. Nonzero invalid settings can request DELETE0803C97A then flush0803CC54 inside initialization. This is an actual producer before the82000 stock read, not a later hypothetical timer. **UNKNOWN:** whether the actual unit selects that branch and whether any normal file-backed writer can reach82000 under that unit's geometry. No such actual target mutation has been demonstrated. {settings}.

**PROVEN:** Phase47's normal reference FAT16 layout confines file-backed writes to[D4000,2000000); both evidence regions are outside. **STRONG INFERENCE:** a healthy unit retaining that format has the same protection. **UNKNOWN:** the needed current-unit bound/formatter invariant. Phase46's synthetic malformed geometry is superseded as a realistic counterexample; it is not resurrected here. The exhausted Phase53 authentication branch remains closed. Early copying after the82000 stock read does not bypass the missing **pre-read** invariant. {geometry}; {old('phase53-existing-read-final-decision','findings.md')}.

**PROVEN:** explicit identity edit25228 writes81000; resource updater selector2 starts82000; boot/application program/erase primitives remain. Selected updater metadata80000 sector ends81000 and does not itself overlap either target. The scoped normal selector0 installation and boot exclusions, and normal MSD write protection, are preserved from Phase47; excluded explicit update/factory/edit commands and arbitrary earlier histories are not reopened as new qualification requirements. A snapshot cannot recover bytes already changed before its read. The bootloader's earlier81000 read helps identify timing but is not retained across application startup by this design. {old('phase44-preflash-redteam-closure','evidence-preservation.md')}, {old('phase47-filesystem-state-closure','target-preservation.md')}, {old('phase46-msd-filesystem-closure','persistence-routes.md')}.

**PROVEN:** the diagnostic inherits SC35D8 persistence, not late B1.3 features: persist19 load/new set RAM flags; c_rs/c_dtick19 update RAM/DSP; save extension hook precedes stock file persistence. No later15/30-second timer is imported. {background}.

**UNKNOWN — overall pre-mutation ordering for both targets is not qualified.** A read/snapshot point before application mount is identified for81000. For82000 the proposed available stock read is too late to establish the requested simple read-before-all-filesystem-writers proof. Smallest next ordering experiment: trace the bounded Main path from1F0F0 through first35EE6, including accepted settings cleanup/content jobs and deferred callbacks, and establish a target-independent physical write exclusion. If no such invariant exists, the copy-only-after-existing-read design cannot meet its stated preservation goal. Do not reopen host MSD authentication or attempt a complete peripheral cold-boot emulation first.
''')
    save('snapshot-hooks.md',f'''
# Phase54 — proposed minimal hooks, not an implemented patch

| Item | Exact candidate / requirement | Confidence |
|---|---|---|
|81000 application hook |Replace25222 MOVS r2,#0 and25224 STRB [r4,#E] with a4-byte B.W to private ARM code; inspect R0 before clobber; copy23 from r4; replay both displaced instructions and return25226 |PROVEN instruction boundary; UNKNOWN final patch qualification |
|82000 hook |Replace35EE6 LDR r0,literal and35EE8 LSRS r2,r7,#16 with4-byte B.W; inspect R0, verify first expected descriptor/length/offset and first-capture state; copy512 from[20006A00]; replay displaced instructions, including flags; return35EEA |PROVEN instruction boundary; UNKNOWN final patch qualification |
| Reset initialization |Set EMPTY once before first application read; never reinitialize on later engine/table reload |UNKNOWN site/all reset-path coverage |
| Completion observer |If required, latch DMA/QSPI request generation, target/count/error/completion before flags disappear |UNKNOWN extra hook sites and bytes; a two-copy-hook design alone is insufficient |
| Code site replacement |Two4-byte branches =8 replaced ARM bytes |PROVEN arithmetic, conditional proposal |
| Added code/flash placement |Copy/state/check helpers, reset and completion observers, export change and veneers |UNKNOWN exact bytes and safe code pool; no assembled patch |
| Fixed RAM |535 payload + minimum1-byte five-valued state =536 logical bytes; word-aligned23-byte area padded24 +512 +4-byte state =540 bytes before any guards/checksum/completion metadata |PROVEN arithmetic; UNKNOWN owned address |
| Stack delta |A leaf design can avoid a payload stack buffer; register/flags preservation still needs a specified ABI and scratch storage |UNKNOWN actual maximum; not claimed zero |
| Boot cycles |Exactly535 payload bytes must be copied once; instruction count/wait states, cache/IRQ stalls and integrity work depend on implementation |UNKNOWN; no cycle number inferred from byte count |
| Interrupt masking |Do not mask around the535-byte copy or any Storage wait; publish only after full copy; brief atomic metadata update may be required |STRONG INFERENCE design; UNKNOWN exact masking count |

Sources: {here('app-0802520c.asm')}, {here('app-08035e28.asm')}, {tests}, {here('completion-authentication.md')}.

**STRONG INFERENCE:** inserting a leaf copy after the synchronous wrapper has returned can preserve original request/semaphore/DMA ownership: it submits nothing, releases nothing, does not edit descriptors, does not clear hardware flags and leaves the stock source unchanged. Preserve all native-visible registers/SP/LR and condition flags at continuation, including displaced flag-setting operations. Keep all original stock control flow and byte14 normalization. Failure only suppresses diagnostic validity; it must not attempt a forced Storage unwind or a new NOR read. These invariants require native before/after tests of the eventual patch; the boundary tests are not such a patch test.

**UNKNOWN:** a safe validated implementation of the copy hook if another task can recycle the staging buffer between return and copy, or if the first read is incomplete but returns0. Completion and liveness gates must close first. No branch bytes, firmware, SYX or hardware candidate are produced in this phase.
''')
    save('snapshot-ram-liveness.md',f'''
# Phase54 — retention RAM ownership

**UNKNOWN:** no fixed535-byte retention area is qualified. Neither a single dump nor absence of observed writes supplies a lifetime/ownership contract. This phase chooses no destination address.

| Candidate | Known owner/lifetime | Decision |
|---|---|---|
|20006868..2000687E |Stock application identity cache,23 bytes; byte14 immediately zeroed; later identity edits can change it |PROVEN unsuitable for original23-byte retention without a new protection scheme |
|2000546C..20005482 |Bootloader identity cache |UNKNOWN survival through application scatter/BSS/constructors; not reserved across images |
|[20006A00], captured20005148..20005347 |DSP table staging; pointer copied from[2000327C] at1F55A/55E; reused in35E28 descriptor loop |PROVEN lifetime shorter than required; not retention |
|Phase44 latch20044D70..20044D7B |12-byte explicitly reserved one-shot state |PROVEN owned by old diagnostic; not535 free bytes |
|Master FX20044D7C..20044E57 |220-byte retained SC35D8 state |PROVEN live feature, not available |
|Heap below20044D70 |Captured cursor20044D68 leaves8 bytes in corrected diagnostic fixture |PROVEN insufficient in that fixture; UNKNOWN fresh-boot occupancy; no heap allocation allowed here |
|B1.3 heap-top variant20044D6C..20044E57 |Later236-byte feature reservation, different image/version |PROVEN not transferable as unused SC35D8 RAM |
|Main/Storage stacks; top-SRAM exception area |Task/IRQ storage and nesting |PROVEN excluded by requirements; measured margins do not grant ownership |
|MSD/DMA/parser buffers, including40024000 |Live protocol/DMA temporary memory |PROVEN excluded by requirements; cannot retain through arbitrary later activity |
|Other apparent BSS/alignment holes, two separate fixed buffers |No complete static/runtime writer exclusion or lifetime reservation exists |UNKNOWN, not safe based on a dump |

Evidence: {here('stock-read-lifetimes.md')}, {ram}, {transport}, {link('notes/qspi82000-hardware-readiness.md')}. Later B1.3 lazy-state facts are shown only to prevent cross-image reuse, not assumed inherited by the diagnostic.

**PROVEN arithmetic:** extending the existing heap-top reservation down by540 bytes would place its lower edge at20044B54 (20044D70−21C). Captured cursor20044D68 is already above that proposed boundary. Reserving early would remove capacity consumed later; it does not make the existing allocation demand disappear. Even saving only byte14 plus retaining the other22 identity-cache bytes would require protection against later identity edits, and would still leave the512-byte table-retention problem. It is not an accepted optimization.

**STRONG INFERENCE:** explicit static reservation, exclusion from initialized/zeroed ranges after acquisition, allocator bounds and all task/DMA/parser/audio users is a viable methodology. Two disjoint reserved buffers can satisfy the same contract but do not reduce total demand. Preserve reset-time invalidation before every acquisition; retention need not survive reset and must not be reused as though it did.

**UNKNOWN:** exact address, allocator/scatter changes, worst-case demand and boot-to-export lifetime under normal restore/USB/audio. Minimum RAM qualification is a source/byte-derived region-ownership audit plus native startup allocation high-water/fail-closed replay and write guards through export. An explicitly reserved buffer must not disable retained Master FX or starve stock constructors. This cannot currently be certified as a copy-only patch using a known spare hole.
''')
    save('completion-authentication.md',f'''
# Phase54 — internal read completion authentication

**PROVEN:** internal hooks have more visibility than the closed host-MSD interface. Wrapper24130 enqueues and waits; worker24014 publishes backend status at wrapper+18, then synchronization clears. Backend22F94 returns1 for bounds rejection and2 for semaphore acquisition failure, without a read. After37430 returns it releases the semaphore at22FD4 and returns0. Resource47C6C preserves that status; identity25220 also leaves it available at25222. The six native tests show that existing callers do not reject those failures. {here('app-08047c6c.asm')}, {tests}, {completion}.

| Completion obligation | Available internal source | Result |
|---|---|---|
| IRQ |QSPI573E0→22826 acknowledgesTCF/SMF and sets controller softwarebit0;5756E→57664 wakes Storage mask100 |PROVEN stock completion predicate, not a whole-buffer integrity guarantee |
| Request status |Wrapper+18 and R0 at25222/35EE6 |PROVEN statuses0/1/2 are directly inspectable; must reject nonzero |
| Requested bytes |Identity23; resource512; QSPI DLR is length−1; DMA2 stream7 NDTR/M0AR registers400264BC/C4 |PROVEN configured/requested counts are available; UNKNOWN generation-matched terminal invariant |
| DMA setup |1C072 returns0 even when EN is already1 and skips fresh address/count setup |PROVEN selected native Phase52 behavior; UNKNOWN real incidence/reachability for these boot reads |
| Error accounting |QSPI selected read uses TCIE, not TEIE; DMA ISR acknowledges TCIF7/FEIF7, no backend error unwind |PROVEN insufficient explicit per-request error result |
| Destination completeness |Buffer bytes can be observed internally; no authenticated source checksum supplied |UNKNOWN from wrapper return alone; source bytes/CRC cannot be guessed |

Sources: {completion}, {old('phase52-read-authentication','DMA-setup-cases.json')}, {old('phase53-existing-read-final-decision','completion-signals.md')}. Phase53 is reused as saved evidence only, not reopened.

**PROVEN:** TEF-only/missing completion in Phase31 leaves Storage waiting, semaphore held and request/buffer active. A post-return hook does not run in that state. Thus two post-read copy hooks alone cannot guarantee the requested literal FAILED state on every physical failure. EMPTY/partial-valid with no BOTH/export remains safe containment, but is not an implemented all-errors→FAILED contract. A bounded error observer would be additional, separately qualified behavior; it must not force release, retry or add a Storage request. Watchdog feeding by idle does not guarantee a bounded reboot. {completion}.

**STRONG INFERENCE:** a suitable internal attestation can combine request identity/source/destination/count, fresh setup, latched completion/error observations and quiescent DMA with expected remaining count, then publish validity after copy and appropriate memory ordering. Merely sampling NDTR0 or a controller bit later is insufficient if stale, cleared, reused or detached from the current request. Capture provenance before native acknowledgements destroy it; do not clear flags from the copy hook. Cache/coherency and CPU-visible destination freshness must follow the existing qualified platform evidence and an actual hook contract, not an assumed host pattern.

**UNKNOWN:** a minimal complete fence is not yet implemented or replay-qualified for either original boot read. No trustworthy-completion proof is claimed for arbitrary synthetic success returns. Required next completion experiment: execute the actual read/IRQ/backend return path for23 and512 bytes with fresh/stale DMA setup, short transfer, nonzero backend status, TEF and missing completion; require each validity commit to imply the full correct synthetic destination and current request provenance. Reuse Phase31/52 results for unchanged paths; do not fabricate authentic unit bytes or perform an extra raw read.
''')
    save('late-export-design.md',f'''
# Phase54 — volatile snapshot state and RAM-only export

**STRONG INFERENCE — proposed contract, not firmware:** reserve two immutable payload areas plus state initialized EMPTY before either acquisition. State encoding may be0 EMPTY,1 81000_VALID,2 82000_VALID,3 BOTH_VALID,4 FAILED. Copies commit their corresponding valid bit only after qualified completion and full copy. Either order is representable even though the known Main path reads A first. A failure from any nonterminal state moves to FAILED; FAILED is absorbing until reset, never a retry admission. BOTH payloads remain immutable. Duplicate stock table initialization must not replace an accepted snapshot; it is not another acquisition. An export request never triggers a missing acquisition.

| State/event | Required action |
|---|---|
|EMPTY + authenticatedA |Copy23; publish81000_VALID |
|EMPTY + authenticatedB |Copy512; publish82000_VALID |
|81000_VALID + authenticatedB / reverse |Copy missing region; publishBOTH_VALID last |
|Any incomplete, failed or unverifiable read |FAILED, no export; if stock wait never returns, post-hook cannot set FAILED—completion observer remains required |
|Already accepted region read again |Do not update snapshot; no diagnostic retry or NOR submission |
|FAILED + any host request |Reject, no rearm, no storage cleanup |
|NotBOTH + export |Reject, no payload completion |
|BOTH + integrity/guard failure |FAILED, no accepted output |
|Reset/power loss |Old validity lost; new acquisition starts EMPTY, never trust SRAM residue |

**STRONG INFERENCE:** store metadata and integrity value before an atomic final publish. FAILED must dominate any competing commit, including IRQ observer versus Main copy and host export. Preserve caller interrupt state; no interrupt masking across copies, waits or USB sends. Prior terminal-publication review supplies a method, not proof of this unimplemented state machine. {old('phase45-nor-mutation-closure','atomicity-patch-review.md')}.

**PROVEN reusable transport:** the prior fixed evidence protocol already carries23 bytes, eight64-byte pieces, and one whole535-byte completion CRC, with session/index/address/length/frameCRC validation. No new535-byte USB frame or whole-payload stack buffer is needed. Source: {old('phase41-fixed-nor-diagnostic','evidence_protocol.py')} (`REGIONS`, `synthetic_packets`, `Receiver.accept/result/captures`); native routing, asynchronous source ownership and one-shot admission evidence: {transport}. Hardware-tested historical rdiag framing and offline-qualified NOR-command integration remain different scopes; an early-snapshot firmware has not been tested on hardware.

**STRONG INFERENCE:** replace the existing command's per-chunk NOR requests with reads of the immutable retention buffers, retaining checked framing, TX buffer ownership until USB completion, strict one-shot admission and host all-or-nothing acceptance. Host accepts both named files only after the single valid whole535-byte completion, then computes SHA-256 and publishes atomically using the prior publication contract. Do not retain a second fallback source that silently initiates NOR or filesystem access. Packet addresses label the original evidence addresses; a new version/source marker should distinguish boot snapshot from late live read without pretending snapshot time is request time. New exporter/parser/native regressions are still required before adoption.

| Failure | Diagnostic behavior / recovery boundary | Confidence |
|---|---|---|
|81000 read rejects or incomplete |No A validity, FAILED if observer runs; no export, no new diagnostic read |STRONG INFERENCE design; UNKNOWN observer qualification |
|82000 read rejects or incomplete |Same, no BOTH; previous A never accepted alone |STRONG INFERENCE design |
|Retention unavailable/corrupt |Fail closed, no payload; guards/CRC detect only covered corruption, not all memory faults |STRONG INFERENCE design; UNKNOWN address |
|USB never enumerates / host never asks |Keep volatile snapshots if valid; add no Storage work and no cleanup writes |STRONG INFERENCE design |
|Malformed request / interrupted export |Reject/discard; no acquisition or persistent cleanup; preserve one-shot latch/no automatic retry |STRONG INFERENCE design |
|Power cycle before export |Evidence is lost; new boot acquires a new pair, cannot claim old bytes retained |PROVEN volatile-memory consequence |
|Stock read deadlock / failed boot |No **diagnostic** Storage request was submitted; original stock wait/failure remains |PROVEN separation; UNKNOWN complete reboot/recovery safety |

**UNKNOWN:** a successful recovery or preservation guarantee across a power cycle. No persistent diagnostic cleanup is needed, but the stock boot itself may already have issued persistence/installer operations. RAM-only export removes the additional late diagnostic H4 exposure, not original stock-read failure. Host timeout/no-valid-file containment remains required for export failure. No hardware action is authorized by this design.
''')
    save('architecture-comparison.md',f'''
# Phase54 — architecture comparison

| Aspect | Current late-read diagnostic | Proposed early stock-read snapshot |
|---|---|---|
| Added NOR operations |One23-byte read plus eight64-byte reads |Zero, if copying both existing complete reads |
| Added Storage requests |Nine diagnostic reads |Zero for acquisition/export |
| Source preservation until host asks |Required |Not required after each accepted snapshot |
| Preservation before snapshot |Required |Still required;82000 stock read follows settings startup |
| Current-unit geometry |Needed to close prior normal-filesystem exclusion |Not eliminated for pre-82000-read persistence without a separate ordering/range invariant |
| H4 |Additional diagnostic wait/deadlock exposure |No additional diagnostic Storage deadlock; original boot reads still exposed |
| RAM |Existing64-byte temporary parser slice and12-byte latch |At least535 payload bytes plus validity/integrity metadata, fixed reservation unqualified |
| Boot changes |Dormant guarded late command |Two early copy hooks plus initialization/completion contract and fixed RAM reservation |
| USB |Qualified fixed23+8x64+completion transport |Same framing/TX lifetime reusable; source becomes retained RAM |
| Authentication |Qualified transport does not itself authenticate physical read |Internal state accessible but complete read-to-validity fence unqualified |
| Rollback/reset |Existing separate update/recovery assumptions |No new recovery proof; volatile evidence lost on reset |

Evidence: {here('stock-read-lifetimes.md')}, {here('writer-ordering.md')}, {here('snapshot-ram-liveness.md')}, {here('completion-authentication.md')}, {here('late-export-design.md')}; existing transport: {transport}.

**STRONG INFERENCE — recommendation:** prefer a RAM-only snapshot/export architecture as the next design direction because it adds no NOR/Storage request and disconnects export time from acquisition time. **UNKNOWN — admission:** do not select it as qualified or designate a build now. The known82000 stock read follows startup settings handling; safe RAM and physical completion are also unresolved. These are independent obligations, not issues solved by reusing SysEx framing.

**PROVEN:** Phase53's supported-interface branch remains exhausted; this phase does not propose new repeated-read, poison-pattern or probabilistic authentication schemes. **UNKNOWN:** whether the copy-only existing-read strategy can meet the full pre-any-source-mutation requirement. First resolve the bounded startup-to-first82000 ordering/range exclusion; only if it passes should the fixed retention and completion-fence experiments proceed. No second raw read or broad new cold-boot peripheral emulation is proposed here.
''')
    save('findings.md',f'''
# Phase54 — early evidence snapshot decision

**UNKNOWN: the architecture is not qualified.** Both stock read/copy points exist, but three independent admission requirements remain open: pre-read preservation for82000, fixed535-byte RAM ownership/lifetime, and trustworthy physical completion before validity publication.

**PROVEN:**81000 is read as23 bytes into20006868; original byte14 is destroyed by STRB08025224. An application hook at25222 can see the intact original record before that store, conditional on complete read success.82000 is read as512 bytes into the table staging pointer (captured20005148), returned at08035EE6, uploaded then reused by the next descriptor. Six native boundary tests confirm both argument sets and the callers' failure-status handling. {here('stock-read-lifetimes.md')}, {tests}.

**PROVEN:** the application81000 read precedes its Main filesystem mount; the82000 read comes **after** mount and settings initialization, including a conditional delete/flush producer. **UNKNOWN:** that this producer or other prior normal work can modify the actual unit's82000 source; no target mutation was demonstrated. The healthy reference FAT16 bounds exclude it, but are not authenticated current-unit bounds. Copying after that read cannot by itself eliminate the pre-capture preservation problem. Superseded malformed-state countermodels and later B1.3 background features are not imported. {here('writer-ordering.md')}.

**UNKNOWN:** no fixed retention allocation is approved. Existing stock buffers are normalized/reused, and the explicitly reserved prior diagnostic heap-top area has only8 bytes of fixture headroom. No535-byte memory hole is inferred from that dump. {here('snapshot-ram-liveness.md')}.

**PROVEN:** unlike the MSD host path, these internal return points expose backend status. **UNKNOWN:** status0 implies a complete fresh DMA destination under all required failure cases; the native setup can skip DMA reprogramming if already enabled, and TEF/missing completion may never return. A copy-only hook cannot implement FAILED on a permanently waiting stock read. {here('completion-authentication.md')}.

**STRONG INFERENCE:** RAM-only export can reuse the prior23+8x64+completion-CRC protocol and removes all additional diagnostic NOR/Storage requests and their late H4 exposure. It removes preservation dependence **after** snapshots, not before them; it does not prove recovery of a failed stock boot. No early-snapshot exporter/state implementation is claimed. {here('late-export-design.md')}, {here('architecture-comparison.md')}.

| Gate | Result |
|---|---|
|Exact stock readers and intact copy windows |PROVEN, scoped native/static evidence |
|Both reads before possible source mutation |UNKNOWN;82000 after startup persistence is the critical ordering gap |
|535 bytes retained in fixed owned RAM |UNKNOWN |
|Genuine completion before snapshot validity |UNKNOWN |
|RAM-only later export without new NOR reads |STRONG INFERENCE architecture; not implemented/qualified |
|Exact hook bytes/cycles/stack/allocation |UNKNOWN beyond two proposed4-byte sites and payload/state size arithmetic |

**UNKNOWN — smallest next experiment:** bounded native startup/content ordering replay from1F0F0 through the first35EE6, with normal accepted settings states and real queued persistence primitives, establishing a physical-write range invariant before the82000 read. A healthy-fixture no-write trace alone is insufficient. If the exclusion cannot be proved without missing geometry, record that the copy-only strategy does not bypass that prerequisite. Separate RAM reservation/lifetime and completion-fence proofs remain necessary even if ordering passes.

**PROVEN:** all eight requested reports are present. Evidence/source checks are recorded in {here('validation.json')}; Phase53 evidence and the439 pinned reference sources are preserved. Only Phase54 scripts, listings, JSON and Markdown were written. No new firmware/SYX, candidate, hardware access, MIDI enumeration/opening or transmission. The exhausted existing-B1.3 geometry authentication branch was not rerun.

EARLY EVIDENCE SNAPSHOT = UNQUALIFIED
''')

if __name__=='__main__':main()
