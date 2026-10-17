"""Phase57 qualification reports only; input images remain untouched."""
from pathlib import Path
import json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def link(p):return f'[{Path(p).name}](<{Path(p).as_posix()}>)'
def here(n):return link(OUT/n)
def old(p,n):return link(ROOT/'builds'/p/n)
def save(n,t):(OUT/n).write_text(t.strip()+'\n',encoding='utf8')
def main():
    own=json.loads((OUT/'ownership.json').read_text());refs=here('ownership.json');model=here('epoch-model-tests.json')
    prior=old('phase56-geometry-snapshot-lifecycle','findings.md')
    bytetable='\n'.join('|'+r['address']+'|'+r['meaning']+'|'+', '.join(r['writer_candidates'])+'|' for r in own['byte_ledger'])
    ctortable='\n'.join('|'+r['record']+'|'+r['target']+'|' for r in own['constructor_table']['entries'])
    save('existing-12byte-ownership.md',f'''
# Phase57 — original12-byte ownership, before redesign

**PROVEN:** region20044D70..20044D7B is the existing Phase42/44 diagnostic reservation below220-byte Master FX state20044D7C..20044E57. The shared getter5DBCC branches to6B6CC; it lowers allocator limit[20002B44] toD70 only if the expected old limitE58 and cursor≤D70 hold. It uses no allocator call. Initial stores6B708/70A clear+4..11;6B714 writes magic4E4F5234 at+0..3. This is lazy runtime reservation, not reset initialization. {old('phase42-exact-rdiag-integration','findings.md')}, {old('phase56-geometry-snapshot-lifecycle','app-0806b6cc.asm')}.

|Byte address |Current meaning |Writer candidates in exact owner bodies |
|---|---|---|
{bytetable}

**PROVEN scoped extraction:**23 accesses in known getter/watch/admission/raw/terminal bodies; {here('ownership.py')} performs register constant tracking and expands accesses to all12 bytes. {refs} includes every extracted read PC as well as these writes. This is not an alias-complete global scanner. The old success store6B9EC is unreachable under the corrected6B9DC branch; actual success store is6BC46. Do not count the retired store as a live additional writer.

|Owner |Exact native activity |Before USB-ready / after USB-ready / required later |
|---|---|---|
|Getter6B6CC |Writes all12 at first reservation; checks magic at6B722 on subsequent calls; initializes separate Master FX via5DC06 when needed |Can run before USB; remains callable after USB; reservation/retained feature access still required |
|SysTick5998E→6B748 |Checks limit/magic, reads state+4/starttick+8, sets state3 at6B794 after5000 ticks if ACTIVE |Callable before/after USB; inert before reservation or outsideACTIVE; quarantine timeout still required during raw capture |
|USB admission6B798 |Reads+4 at6B818; writesACTIVE6B820,session6B824,starttick6B830 |On an admitted explicit USB request; pre-ready admission is structurally absent under no host request, but early IRQs exist; duplicate rejection still required |
|Raw6B850 |Reads session6B864; state checks6B8D0/6B918/6B9F6; writes chunk6B8DA,owner6B8DE/6B924/6BA02; failure6B9FE |After admission; tracking/ownership stays live through reads and USB drain, including a stuck transaction |
|Corrected terminal6BC30 |Reads state6BC3E; conditionally writesSUCCESS6BC46 under restored PRIMASK |Required after final successful transmit/drain; may never overwrite quarantine |

**PROVEN:** magic has runtime-long liveness; status/session/chunk/owner/tick overlap once a capture is ACTIVE. No existing byte is simply dead immediately after boot or geometry export. Before the first explicit request, session/chunk/tick are semantically dormant but getter/watch still interpret their storage. The region cannot accept new contents without replacing those interpretation contracts. Native collisions from Phase56 are retained, not rerun: {old('phase56-geometry-snapshot-lifecycle','liveness-tests.json')}.

Original timeline:RESET(unreserved/old SRAM residue)→first getter(reserve+zero+magic)→IDLE(watch checks)→explicit request(ACTIVE/session/tick)→chunk/read/reply ownership→SUCCESS or FAILED_QUARANTINED→no new capture before reset. Full reset-to-first-getter timing is UNKNOWN; the captured heap fixture alone does not establish it.
''')
    save('coalesced-state-layout.md',f'''
# Phase57 — field lifetime coalescing and adaptation

**STRONG INFERENCE:** exactly the same12-byte capacity can carry the following union after all legacy owners are adapted. No extra fixed reservation, heap allocation or audio/parser/stack borrowing is proposed. The rejected52-byte extension remains unused.

|Addresses |BOOT / first mount in progress |VALID through export/host decision |After atomic raw admission |After terminal result |
|---|---|---|---|---|
|D70..D73 |Control32:phase3 bits,unexpected-event bit,epoch28; BOOT0→MOUNTING/epoch1 |VALID/EXPORTED,epoch1; control is sole publisher |ACTIVE,epoch1; admission/quarantine atomically mutate only control |SUCCESS orFAILED terminal; never rearm |
|D74 |Part of8-byte payload not valid until commit |Compact geometry byte0 |Target mask |Retain terminal bookkeeping |
|D75 |Same |Geometry byte1 |Session token |Same |
|D76 |Same |Geometry byte2 |Global chunk |Same |
|D77 |Same |Geometry byte3 |Read/reply/free ownership |Keep ownership while a request remains active |
|D78..D7B |Same |Geometry bytes4..7 |32-bit start tick |No timer rearm; preserve until safe end/reset |

**PROVEN lifetime condition:** the geometry becomes dead for this transaction only after exact-epoch/digest authorization is accepted and the transition toACTIVE is atomic. **Export alone is not enough**: the host has not yet approved, and the device still needs the retained bytes to validate the token. The model refuses geometry export afterACTIVE; no live geometry is overwritten sooner. {here('first_epoch_model.py')}, {model}.

|Legacy write/read |Conceptual adaptation |Semantics retained / proof limit |
|---|---|---|
|6B708/70A payload clear and6B714 magic store |Move one-time initialization/reservation to before constructors; remove later diagnostic-record clearing from lazy getter |Keep separate Master-FX initialization; getter must preserve all12 thereafter |
|Magic reads6B722/6B764 |Replace with reserved-limit and new lifecycle validity contract; code/protocol version supplies schema identity |Old4-byte magic cannot coexist with control32 in the same bytes |
|Timeout6B794 writing+4 |Read phase from control; onlyACTIVE uses starttick+8; setFAILED in control |5000-tick deadline, wrap arithmetic, no release/retry remain |
|Admission writes6B820/824/830 |Validate geometry token before overlay; publishACTIVE then initialize raw session/tick/target/owner under one admitted owner contract |Duplicate/second transaction rejected; no speculative Storage submit |
|Raw chunk/owner stores |Retain at+6/+7 only inACTIVE raw union |Read and USB-buffer lifetimes remain; fail does not free active descriptor/buffer |
|6BC46 success and6B9FE failure |Atomic control-phase publication;FAILED absorbs late completion |Preserve corrected terminal-race semantics; a byte+4 store is now incorrect |

**PROVEN model scope:**13 scenarios cover idempotent later getter use, nonACTIVE ticks, unexpected events before/during/after snapshot/export/admission, tick wrap, timeout/late success, normal success, reservation refusal and wrong epoch/digest/identity authorization. No second diagnostic transaction follows failure. Counts are model admissions, not9 native read requests. {model}.

**UNKNOWN:** all native adapters, raw target-mask command, same-boot session binding and exact caller register/flag ABI are not implemented as a new image. Saved old native tests continue to qualify the unchanged old format only. The conceptual coalescing is feasible in12 bytes; it is not a passed native union regression.

**STRONG INFERENCE — initial publication requirement:** the new initializer must not publish allocator-limitD70 while the record still contains warm-entry residue that an ISR could interpret asACTIVE. Under a separately bounded ownership/PRIMASK contract, recheck old limit/cursor, initialize BOOT/payload first, then publish reserved limit last; restore the incoming mask. Later getter calls never repeat this initialization. The pure model treats reservation as atomic; its Python assignment order is not a proposed native store-order proof. Exact native early-reservation race/latency testing remains UNKNOWN.
''')
    save('first-mount-provenance.md',f'''
# Phase57 — first relevant epoch provenance

**UNKNOWN — is1AE06 the first relevant filesystem epoch of the complete boot?** No earlier epoch was demonstrated; absence of one in the Main prefix is not the required full-chain proof.

**PROVEN application reset chain:** vector08010004→0805C00C; platform setup1BC78 then5C19C→5B990→scatter dispatcher5B590. Scatter record5B7B4 selects zero helper1A7EA, zeroing[20003D04,20006A54); record5B7C4 selects596C4 for initialized data[20000000,20003D02). Record5B7D4 selects constructor-dispatch handler**0805B958**, whose iterator5B978 walks the relative constructor table[5B5B8,5B5E0). After it,5B9AE calls1D3C8. Sources: {here('app-0805c00c.asm')}, {here('app-0805c19c.asm')}, {here('app-0805b990.asm')}, {here('app-0805b590.asm')}, {here('app-0805b958.asm')}, {here('app-0801a7ea.asm')}, {refs}.

|Constructor table slot |Authenticated Thumb target |
|---|---|
{ctortable}

**PROVEN:**1F050 in that list invokes1ADD0 to initialize disk vtable/drive/geometry pointers.1ADD0 only writes those object fields; it does **not** call mount. Other entries include USB/peripheral structures, raw backend/controller setup and state initialization. Listed bodies/callees have not all received a complete transitive callback closure; the table itself is enumerated, not guessed from function names.

**PROVEN:**1D3C8 creates Main/UI/Storage/Content via1DDD4 before scheduler start1DE78. The Content task22ACC waits/drains22AE4; its queue22A0C→366E0 initializes input/output indices0 at366FC/FE. This is native queue-initialization evidence, not a proof that no producer subsequently submits before Main's snapshot. {here('app-0801d3c8.asm')}, {here('app-0801dd80.asm')}, {here('app-08022a0c.asm')}, {here('app-080366e0.asm')}.

**PROVEN Main prefix:**1D4B0→1EC80(identity,including2520C read), then1EEAA→25AC6→2448C/24484/3ADBC→2445C peripheral/display service, then1F0A8→NOR1ADDC→f_mount19A92→197A0→return1AE06; SD follows. No earlier Main filesystem mount is present in this prefix. Do not treat that prefix as a reset-to-Main trace. {here('app-0801d4b0.asm')}, {here('app-0801eeaa.asm')}, {here('app-08025ac6.asm')}, {here('app-0803adbc.asm')}; successful mount details reused from {old('phase55-precleanup-geometry-snapshot','mount-to-persistence-ordering.md')}.

**UNKNOWN exact earlier obligations:** completed bootloader control after the real81000 read at051C2; all10 application constructor subgraphs/registered callbacks before1D3C8; and normal producer ordering between queue initialization22A40 and Main mount1D4C0. Concrete dispatch boundaries include UI1D698→1E4BE and Content22ADA→22AE4. No earlier actual filesystem epoch is invented to fill these gaps. The current saved cold-boot execution never reaches application1AE06.

**STRONG INFERENCE:**5B958 entry offers a new preconstructor initialization point after scatter memory initialization. Replacing its initial4 bytes(PUSH r4,lr;MOV r4,r0) with a correctly wrapped hook could reserve/reset the same12 bytes before any constructor. The helper must replay the displaced prologue and preserve the scatter argument/return contract. This is a site proposal, not patched code or proven all-boot liveness. Any earlier unexpected application mount encountered after that guard would quarantine, not become an accepted first snapshot.
''')
    save('pre-first-mount-mutations.md',f'''
# Phase57 — pre-snapshot target mutation closure

**UNKNOWN:** complete normal reset-to-first-snapshot mutation closure. This is not replaced by a replay with no observed writes.

|Stage |82000..821FF |81000..81016 |
|---|---|---|
|Completed selected selector0 install |PROVEN no program/erase overlap in saved native transition |PROVEN same; metadata erase ends81000 exclusive |
|Boot metadata load03B2A |PROVEN reads23 at80000; not itself erase/cleanup |PROVEN separate sector from identity |
|Boot validator03B9A/internal install03C24 |PROVEN selected staged-image operations program internal flash; not a resource-selector NOR rewrite |PROVEN selected model excludes identity sector |
|Boot identity03A10→05D98 |PROVEN read81000, RAM byte14 zero; not a NOR write |PROVEN normalization is RAM; callback writer05DB4 is separate explicit identity editing |
|Boot pre-application callbacks/intake |UNKNOWN full normal dispatch closure after saved read boundary; no automatic target writer demonstrated |UNKNOWN same, with distinct identity edit capability excluded by normal workflow |
|Application reset/scatter |PROVEN inspected memory operations initialize RAM and platform registers, not evidence array bytes |PROVEN same |
|Application constructors |PROVEN disk1F050→1ADD0 is object setup, not mount/format |UNKNOWN full constructor callback closure applies to both |
|Raw NOR/backend init1E062→22F1E |PROVEN reviewed status/address-mode initialization; no array write in reviewed direct helper |UNKNOWN full callback/descriptor closure; not a demonstrated identity rewrite |
|Content/Storage startup |PROVEN queue starts empty by code; worker can later process write/erase only with a submitted operation |UNKNOWN complete pre-snapshot producer/queue closure for both |
|Settings bootstrap/cleanup |PROVEN Main1D4C4 later than intended snapshot;2D060 conditional DELETE/flush cannot precede its own construction |PROVEN same Main order |
|Repair/format/prior teardown |No automatic formatter/repair found in reviewed mount;19734 clears dirty before VBR load; no earlier teardown epoch demonstrated |UNKNOWN universal absence; not a claim actual repair occurs |
|SC35D8 persist19 |PROVEN resync custom work is RAM/DSP; stock session save remains separate |UNKNOWN all pre-snapshot scheduling of surrounding stock file work |

Sources: {old('phase44-preflash-redteam-closure','b13-updater-replay.md')}, {old('phase45-nor-mutation-closure','update-noop-review.md')}, {here('boot-08002fde.asm')}, {here('boot-08003b9a.asm')}, {old('phase38-nor81000','findings.md')}, {old('phase47-filesystem-state-closure','startup-persistence.md')}, {old('phase45-nor-mutation-closure','background-write-analysis.md')}, {here('first-mount-provenance.md')}.

**PROVEN normal-scope separation:** identity editor erases[81000,82000), so its sector erase does not overlap82000. The allowed selector0 metadata/install sequence excludes both targets. Explicit factory/resource update/identity edit commands remain excluded; superseded malformed-host/filesystem countermodels are not reopened. **UNKNOWN:** completed normal-prefix closure for82000 is independently missing, so its status is not downgraded merely because identity history is weaker.

**UNKNOWN — primary earlier-epoch question:** the first *accepted model snapshot* is epoch1 by construction, but current native evidence does not establish that every preceding actual relevant epoch/producer has been guarded or excluded. An epoch counter initialized late cannot prove that fact. The exact known execution boundary remains boot read051C2; the new exact application obligations are constructor iterator5B978 and pre-Main Content/UI dispatch. These are unresolved operations, not proven earlier destructive epochs.
''')
    save('install-to-first-mount.md',f'''
# Phase57 — installation boot versus later cold boot

No new candidate exists. “Candidate” below refers to the historical corrected research image inspected read-only. A future first-mount adaptation would require a new offline qualification; these saved traces are not automatically its admission.

|Question |A: first boot after completed installation |B: later cold boot already installed |
|---|---|---|
|Prior staging |PROVEN named selector0 transfer overwrites all staged/metadata bytes subsequently read in saved model |Metadata/staging state inherited from previous successful boot; exact actual contents UNKNOWN |
|External update writes |PROVEN staged[0,5C000), metadata[80000,81000); neither target overlaps |No completed new upload assumed; do not automatically infer external metadata cleanup |
|Boot metadata handling |03B2A reads80000;03B9A checks selector/size/CRC/header |Same native validator; matching38-byte header can skip internal install |
|Stale but valid staged image |Selected completed transition does not depend on prior array bytes |Can be evaluated on boot. Compatible different compared header can reinstall internal image; equal header skips. This is a code capability, not a demonstrated rollback on this unit. |
|Evidence-sector mutation by reviewed installer |PROVEN absent in selected trace |STRONG INFERENCE same raw-read/internal-program structure; full boot dispatch closure UNKNOWN |
|Application pre-mount cleanup |PROVEN Main settings cleanup is later than intended NOR mount hook |Same Main order; all-task constructor/deferred closure UNKNOWN |
|Filesystem initialization before geometry |Reviewed mount reads/parses, not format; saved native8 cases add no writes |Same; actual-unit first-epoch provenance still UNKNOWN |
|Complete reset→accepted snapshot |UNKNOWN, authentic read boundary and startup/liveness gates remain |UNKNOWN, plus actual persisted metadata state is not newly acquired |

**PROVEN:** named updater/no-op/rollback results are preserved, not rerun.03BE4..03BF6 compares38 bytes at app+1C8..1ED; equal headers skip, different compatible headers install. A changed header is not a rule requiring a numerically higher build.80000 metadata is not relocated to81000. No automatic metadata-clear erase is proved merely because installation succeeds. {old('phase45-nor-mutation-closure','update-noop-review.md')}, {old('phase44-preflash-redteam-closure','b13-updater-replay.md')}, {here('boot-08003b9a.asm')}.

**UNKNOWN:** interrupted/power-cut uploads and arbitrary prior command histories are outside this normal completed-install sequence, not newly introduced attack scenarios. No safe physical recovery/rollback guarantee follows from the snapshot design, and no firmware transfer or restore is performed.
''')
    save('async-exclusion.md',f'''
# Phase57 — asynchronous exclusion

**PROVEN:** application startup creates Main/UI/Storage/Content before enabling normal scheduling. Main begins1D4B0; UI1D680 services1E4BE/209E4; Storage5767C drains wrappers24014; Content22ACC waits and drains22AE4. Queue constructor366E0 stores read/write indices0. Exact ready/priorities/queued callbacks when Main reaches1AE06 remain UNKNOWN. A running-RAM snapshot is not the mount-time scheduler state. {here('app-0801dd80.asm')}, {here('app-0801d680.asm')}, {here('app-08022a0c.asm')}, {here('app-080366e0.asm')}.

|Context |A: pre-snapshot evidence mutation |B:12-byte overwrite |C: remount/invalidate before commit |
|---|---|---|---|
|Storage |UNKNOWN normal queued write producers; capability22FDC/23078 is known |No selected intentional private-record writer; complete DMA/alias closure UNKNOWN |Pending file jobs can call197A0 slow mount; pre-snapshot presence UNKNOWN |
|Content |Queue initially empty by native code; complete producer ordering after construction UNKNOWN |No direct private-record owner in reviewed worker |22AE4 content file paths can trigger lazy mount |
|UI/Main callbacks |Main cleanup is later; earlier UI dispatch transitive closure UNKNOWN |Shared getter can run from retained feature paths |Computed callback/lifecycle roots not fully closed |
|SysTick |Reviewed watch does no NOR/file write |PROVEN old6B794 private status write; needs new control adapter |No direct mount call in reviewed watch; total scheduler consequences UNKNOWN |
|USB service/IRQs |Normal WRITE10 protection reused; full pre-ready normal callback closure UNKNOWN |PROVEN explicit diagnostic admission/raw writers after accepted command; no authorization before geometry in proposed contract |Deferred mode callback reviewed; class teardown aliases not fully closed |
|DMA/QSPI IRQs |Reviewed handlers complete existing I/O, not file API producers; in-flight write before hook not excluded by masking |No selected intended payload overlap withD70; every initial DMA range not globally proved |Controller notifications can schedule queued work |
|Timers/deferred work |Known150-tick USB-mode callback; SC35D8 resync RAM/DSP |Known timeout owner remains live |Other native callback root predicates UNKNOWN |

**UNKNOWN — can any concurrent normal execution mutate a target before the snapshot?** No actual such write was established; complete queue/root exclusion is missing. **PROVEN:** current timeout/getter owners can overwrite new data unless adapted. **UNKNOWN:** complete native pre-commit invalidation interlock. These three questions have distinct statuses.

**PROVEN scoped reused atomicity:** Phase56 isolated commit helper success uses16 instructions,10 mask-set entry instructions,24-byte stack and DMB before validity;12 tests preserve supported registers/flags and incoming PRIMASK. This helper excludes a short publication race, not all earlier initialization/packing/preexisting DMA. It is reused as evidence, not rerun or installed. {old('phase56-geometry-snapshot-lifecycle','commit-tests.json')}.

**UNKNOWN:** exact physical latency, forbidden interrupt budget and all-task pending work at mount. A bounded critical section is insufficient if a target write was already active or an earlier filesystem epoch already existed. No interrupts are disabled on hardware, and no unqualified short mask is asserted to close the global provenance requirement.
''')
    save('state-liveness.md',f'''
# Phase57 — reset-to-terminal12-byte liveness

**PROVEN:** initialized data ends20003D02; scatter zero span[20003D04,20006A54) does not touchD70. Therefore the private record has no automatic fresh-reset clear in those records; warm-entry SRAM residue cannot be trusted. Constructor iteration5B958 is an identified place to reserve/initialize before constructors without extending capacity. This is not yet an executed adapter. {refs}, {here('app-0805b590.asm')}, {here('app-0805b958.asm')}, {here('app-0801a7ea.asm')}.

|Lifetime stage |Permitted intended writes / existing conflicts |
|---|---|
|Reset/scatter |Native named ranges do not touch record. New one-time init must setBOOT once after allocator initialization; location/timing is proposed, not fully qualified. |
|Constructors/heap growth |Early limitD70 must protect region. Existing allocator traps above limit; all-constructor demand/aliases remain UNKNOWN. No new allocation. |
|First mount |Control→MOUNTING/epoch1; payload two words;VALID last. Any unexpected earlier root must quarantine; no accepted late first-use fallback. |
|Normal startup/USB-ready |Adapted lazy getter must not clear record; SysTick must ignore nonACTIVE geometry union. Existing native bodies violate these requirements, as saved collision tests prove. |
|Geometry export |Payload read only; control may changeVALID→EXPORTED. No Storage work and no parser ownership transfer of retained bytes. |
|Host authorization |Compare exact retained record/epoch/session; only then overlay8 payload bytes with raw transaction bookkeeping. |
|Raw read/reply |Existing session/chunk/owner/start-tick semantics move into the documented raw union; target mask occupies first payload byte. Source buffer itself remains separately owned by existing raw path. |
|Success |Conditional ACTIVE→SUCCESS only after output completion; ownerfree only if actually released. |
|Failure/timeout |FAILED absorbs late success and duplicate commands; keep active read ownership; no forced release/cleanup/retry. |

**PROVEN model:**13 cases show these logical transitions fit exactly12 bytes without hidden persistent model fields for epochs/state; `limit` denotes the already-existing allocator metadata, and `submits` is test observation, not proposed RAM. Event interception and atomicity are modeled assumptions. {here('first_epoch_model.py')}, {model}.

**UNKNOWN complete liveness:** direct owner references are enumerated in {refs}; indirect computed writes, all range-based clears, task/IRQ high-water and all DMA setup lifetimes have not been closed from reset through raw completion. Known Main/Storage stacks do not intersectD70 in prior fixtures, which does not prove every boot stack/DMA range. No fixture-only no-write result is offered as complete ownership proof.

**PROVEN:** old native getters/watch/admission/terminal logic still uses the historical schema. Historical native regression results remain valid because those bytes are unchanged; they cannot certify the unimplemented new coalesced owner adapters. A conceptual model passing does not satisfy the requested complete native liveness gate.
''')
    save('epoch-invariant.md',f'''
# Phase57 — strict first-mount invariant

**STRONG INFERENCE — proposed policy:** initialize BOOT_EPOCH_STARTED before any relevant application constructor or task can invoke filesystem code. Only the expected first NOR mount root may moveBOOT/epoch0→MOUNTING/epoch1. Nested registration/stride-query/parse operations belonging to that same initial native call must be normalized, using actual caller/task provenance; another root, early unmount or unexpected mount sequence quarantines.

At complete successful return1AE06, require MOUNTING/epoch1, expected registered FS/binding and no unexpected-event bit. Copy canonical geometry and publishVALID last. Invalid parse/unsupported bounds/changed epoch gives no valid snapshot. No later successful mount may become an admitted replacement epoch; later geometry changes invalidate authorization and set terminal quarantine for this boot. This stricter policy intentionally avoids certifying a safeG2 after unknownG1 history.

HOST:request fixed geometry-only response→independently validate exact8 bytes/mapping/code/session→explicitly authorize target mask and exactepoch/digest. DEVICE:atomically compare epoch1/EXPORTED/unexpected=false, claimACTIVE, then submit only authorized fixed read(s). Geometry export alone never captures NOR; missing/invalid snapshot never starts a request.

If a geometry-changing event races admission, invalidation wins with0 new submits, or ACTIVE wins and the changer must refuse/defer **before** mutation. A queued/active read cannot be safely canceled by clearing a flag; existing H4 quarantine remains. Old host tokens cannot rearm after failure, reset or remount. Cross-boot transport session freshness also requires integration; a volatile epoch1 value alone repeats every boot.

**PROVEN abstract tests:**13 cases in {model} preserve deadline4999/5000,32-bit tick wrap, FAILED over late success, reservation refusal, duplicate rejection and identity/coefficient target separation. There is no new capture after an unexpected earlier or later mount event. All native event interception, first-root identity and queue-admission atomicity remain **UNKNOWN**.

## Primary question

Can the first accepted geometry snapshot be considered valid evidence about whether82000 was preserved since the beginning of this candidate boot?

**UNKNOWN.** The policy would establish that conclusion only after earlier mutation exclusion and complete guard placement are proved. Concrete unresolved operations are bootloader81000-read completion/consumer control beginning051C2, the10 global constructor subgraphs dispatched by5B978, and pre-Main Content/UI queue/callback ordering (22ACC/22AE4,1D680/1E4BE) before1D4C0. No actual earlier mounted epoch or82000 mutation has been demonstrated. An exactly matching later epoch number cannot substitute for that missing history.

## Independent target gates

|Target |Intended raw admission |Current status |
|---|---|---|
|82000..821FF |First-epoch validated mapping, no pre-snapshot target mutation, same epoch/session, no bypass writer |UNKNOWN; disabled |
|81000..81016 |Shared prerequisites plus distinct identity-history authorization |UNKNOWN; independently disabled |

Identity erase[81000,82000) does not touch82000. Coefficient-only target mask2 does not require identity predicate; existing combined command must be adapted/tested before such a mask is usable. Required coefficient bytes still come from a later fixed physical read, not from geometry. No arbitrary address is accepted and no hardware action occurs.
''')
    save('findings.md',f'''
# Phase57 — first-mount geometry provenance

**UNKNOWN: first-mount provenance remains UNQUALIFIED.** The12-byte owner/lifetime reconstruction and strict first-epoch design are concrete, but they do not close reset-to-snapshot history or native coalesced-state liveness.

**PROVEN:** exact original12-byte region20044D70..20044D7B has no unused bytes.23 extracted accesses in the known owners show getter clears/magic, timeout,state/session/chunk/owner/tick and corrected terminal stores. Old magic stays live after boot; geometry cannot replace it without owner adaptation. {here('existing-12byte-ownership.md')}, {refs}.

**STRONG INFERENCE:** coalesce control4+canonical geometry8, overlaying geometry with raw bookkeeping only after exact host authorization—not merely export. Preserve timeout/one-shot/FAILED ownership by adapting every old interpreter.13 strict-first-epoch model tests pass, but no new native owner implementation is claimed. {here('coalesced-state-layout.md')}, {model}.

**PROVEN new startup detail:** application scatter initializes data below20003D02 and zeroes only through20006A54; constructor dispatch at5B958 follows, providing a specific early state-initialization opportunity. The10-entry relative constructor table is authenticated. Main's own prefix is identity→display/peripheral→explicit NOR mount, with no earlier Main mount. **UNKNOWN:** that this is the complete boot's first relevant epoch. Constructors and already-created Content/UI/Storage tasks require transitive queue/callback closure. {here('first-mount-provenance.md')}.

**UNKNOWN — primary gate:** can the first accepted geometry prove82000 preserved since candidate boot began? No complete ordering proof exists. The saved genuine cold-boot replay stops at051C2 before81000 read completion; exact application obligations include constructor iterator5B978 and Content22ADA→22AE4/UI1D698→1E4BE before Main1D4C0. These are concrete missing operations, not invented destructive epochs. No automatic82000 write is demonstrated. {here('pre-first-mount-mutations.md')}, {here('epoch-invariant.md')}.

**PROVEN scoped:** completed selected selector0 install excludes both evidence sectors; later equal-header boot may skip internal install. **UNKNOWN:** complete A(first install boot) and B(later cold boot) reset-to-snapshot chains. Identity-only uncertainty does not veto coefficients: both remain unqualified because shared provenance/liveness gates are open. {here('install-to-first-mount.md')}.

|Gate |Result |
|---|---|
|Original12-byte field ownership/timeline |PROVEN scoped known owners; global aliases UNKNOWN |
|Exactly12-byte coalesced state feasible |PROVEN model; STRONG INFERENCE native architecture |
|Native init/timeout/containment adapters |UNKNOWN, conceptual only |
|First Main explicit mount |PROVEN prefix order |
|First relevant epoch of full boot at1AE06 |UNKNOWN |
|No82000 mutation before accepted snapshot |UNKNOWN |
|No81000 mutation before accepted snapshot |UNKNOWN, separate identity policy |
|Asynchronous exclusion/physical mask latency |UNKNOWN |
|Complete reset-to-terminal state liveness |UNKNOWN |
|Same-epoch authorization interlock |PROVEN conditional model; native integration UNKNOWN |

**UNKNOWN — minimum remaining offline work:** close constructor/pre-Main producer roots and reserve/reset the private record before those roots; replay native getter/watch/admission/terminal adapters against existing one-shot ownership/fault cases without a firmware image. A new failed or unexpected mount must quarantine, never be relabeled “first.” No additional no-observed-write trace can qualify the primary history gate. {here('async-exclusion.md')}, {here('state-liveness.md')}.

**PROVEN:** all9 requested reports and persisted evidence are present. {here('validation.json')} verifies historical/pinned inputs remain unchanged. Prior passing suites were not rerun; Phase53 remains closed. No firmware/SYX/candidate generation or modification, hardware/MIDI access or transmission occurred.

FIRST-MOUNT GEOMETRY PROVENANCE = UNQUALIFIED
''')
if __name__=='__main__':main()
