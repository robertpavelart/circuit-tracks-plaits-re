"""Write Phase56 conclusions; no firmware image or candidate creation."""
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
REF=Path('C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main')
def link(p):return f'[{Path(p).name}](<{Path(p).as_posix()}>)'
def here(n):return link(OUT/n)
def old(p,n):return link(ROOT/'builds'/p/n)
def save(n,t):(OUT/n).write_text(t.strip()+'\n',encoding='utf8')
def main():
    compact=here('compact-tests.json');census=here('census.json');life=here('liveness-tests.json')
    model=here('lifecycle-tests.json');commit=here('commit-tests.json')
    mount=old('phase55-precleanup-geometry-snapshot','mount-to-persistence-ordering.md')
    native=old('phase49-existing-geometry-reader','live-geometry-structure.md')
    save('minimal-snapshot-layout.md',f'''
# Phase56 — minimized auditable record

**PROVEN:** normal file-backed writes use FAT copies, fixed-root sectors (FAT12/16), data clusters and, for FAT32, FSInfo. They do not require the identity cache, path, mount-ID padding, free-space cache or exact BPB trailing-sector count to calculate their physical target domains. Native mapper1AF1E uses base+stride×LBA in32 bits. Sources: {native}, {old('phase47-filesystem-state-closure','real-filesystem-geometry.md')}, {old('phase55-precleanup-geometry-snapshot','geometry-record.md')}.

|Required canonical field |FS offset / source width |Stored encoding |Reachability role |
|---|---|---|---|
|fatbase |+2C /32 |13 bits |Lowest FAT-write LBA |
|fatsize |+24 /32 |13 bits |Extent of each FAT |
|database |+34 /32 |13 bits |Fixed-root end and data start |
|n_fatent |+20 /32 |13 bits |Upper valid data-cluster bound |
|csize |+0A /16 (native value from BPB byte) |3-bit log2, power-of-two check |Cluster-to-LBA multiplier |
|n_fats |+02 /8 |1 bit, value−1 |One or two FAT copies |
|FAT type |+00 /8 |1 bit: FAT12/FAT16 |FAT capacity check; excludes FSInfo writes |

**PROVEN:** these fields occupy57 bits, rounded to**8 bytes** with7 reserved zero bits. Encoding is lossless for the admitted scalar ranges. Four32-bit words use13 bits each, factors3+1 bits, type1 bit. FAT32 and any scalar>8191 are explicitly unsupported, never silently truncated. A general uncompressed seven-scalar FAT12/16 record is20 bytes (four32-bit words plus csize16,nfats8,type8); retaining volume base for FAT32 raises it to24 bytes, or23 with canonical8-bit csize. The last comparison is a scalar-width design calculation, not a claim FAT32 is fully qualified here.

**PROVEN conditional encoding domain:** native backing must be drive0/NOR with baseD4000 and stride/BPS4096. These are checked contract values, not an assumption that every per-unit BPB matches the reference. Host requires nonwrapping domains within the conservative32MiB partition bound. Then at most7980 logical sectors exist, and13 bits suffice for all admitted words. FAT32 cannot meet its native minimum cluster class within this bounded4096-byte-sector volume; reject it rather than carry unused FSInfo/root-cluster fields. Base/stride/type checks and lifecycle invalidation must be implemented for this omission to be safe. They are not yet a proved lifetime invariant of the new hook.

**PROVEN:** for FAT12/16 the native assignment is root=fatbase+n_fats×fatsize, and database=root+root-sectors. Capture verifies this relationship before omission. Host recomputes FATend, rejects overflow/inconsistency and bounds the whole fixed-root domain[FATend,database), so root-entry count need not be retained separately. Volume base/reserved sectors are not normal FAT12/16 write domains. Exact total sectors and padding have no role in the three retained domains. Native mounted-field provenance remains mandatory; this is not validation of arbitrary guessed RAM.

Host independently reconstructs:

`FAT=[fatbase,fatbase+n_fats*fatsize)`

`ROOT=[FATend,database)`

`DATA=[database,database+(n_fatent-2)*csize)`.

It checks FAT class/capacity and all arithmetic, then maps/expands these domains to physical erase boundaries. The admitted domain has sector-aligned4096-byte mapping, matching the reviewed erase alignment; both targets lie belowD4000. **PROVEN:**5 saved native-mount record round trips,7 rejection cases and16 factor cases pass. All required scalars survive exactly; unsafe/unsupported values fail closed. {here('compact.py')}, {compact}.

**UNKNOWN:** a global information-theoretic minimum under every possible evidence representation. Two reachability bits alone are smaller but do not provide independent host verification. Eight bytes is the smallest implemented, tested canonical representation here, not a claimed impossibility theorem for7-byte enumerative encodings.

## Host versus device derivation

**STRONG INFERENCE — recommend A:** retain the8-byte raw canonical scalars; let the host calculate domains and target safety. OptionB's flags plus checksum cannot reconstruct omitted geometry, and checking a device-supplied checksum is not independent checking of a device-supplied conclusion. A sufficiently auditable B would have to retain equivalent source values and saves little.8 payload +4 control =12 bytes can theoretically reuse existing diagnostic-owned storage without the rejected52-byte extension. This is a proposed re-layout of live storage, not spare RAM.
''')
    save('ram-ownership.md',f'''
# Phase56 — RAM ownership search

**PROVEN:** the new candidate census covers every halfword of the375948-byte exact corrected research application, every byte of initialized RAM for pointer candidates, and the authenticated captured RAM for pointers/names. It records37 direct candidates,18 literal candidates,14 consecutive MOVW/MOVT address constructions and32 pointer candidates. False positives/data decodes/stale captured words are labeled; this is not a complete computed-alias theorem. {here('census.py')}, {census}.

|Address inclusive |Owner, initialization and known accessors |Lifetime / conclusion |
|---|---|---|
|20044D70..20044D7B |Phase42/44 private12-byte diagnostic record. Getter5DBCC→6B6CC reserves downward by changing[20002B44], writes magic at6B714 and zeros+4/+8 at6B708/70A. SysTick watch6B748, entry6B798, raw command6B850 and terminal patch6BC30 read/write it. |PROVEN owner and runtime reservation method; no unused byte. Selected for proposed union redesign, **not qualified for new content**. |
|20044D70..73 |Legacy magic4E4F5234, checked by getter/watch |PROVEN cannot simply substitute generation here while old readers remain. |
|20044D74..77 |Legacy state/session/chunk/owner bytes |PROVEN actively used; not padding. |
|20044D78..7B |Legacy start tick |PROVEN timeout uses full word; not spare until old lifecycle is replaced. |
|20044D7C..20044E57 |220-byte SC35D8 Master FX state, getter/init5DC06 and retained feature service |PROVEN live owner; no additional reservation or audio state borrowing. |
|20044DF4..20044E37 |Historical rdiag68-byte log atMasterFX+120 |PROVEN aliases live Master-FX LEDs; initialization/repaint can overwrite. Not a distinct diagnostic allocation. |
|20044DE4..20044E1B |probe35s14-word report atMasterFX+104 |PROVEN same live LED owner; not long-lived snapshot storage. |
|20044D68..20044D6F |Fixture heap headroom before existing limitD70 |PROVEN only8 bytes in that fixture; forbidden heap-tail strategy, not selected. |
|20044D3C..20044D6F |Proposed Phase55 extra52 reservation |PROVEN overlaps fixture demand by44; explicitly rejected and unused. |
|20002B44..20002B4B |Allocator limit/cursor |PROVEN live metadata, no unused fields. |
|20000AB5;20000ABE..ABF |FS padding candidates |UNKNOWN full semantic padding ownership; at most3 apparent bytes, inside excluded filesystem owner, insufficient and not used. |
|20005148..20005347 |DSP table staging/DMA-read destination |PROVEN reused by native table jobs; excluded. |
|20006868..2000687E |Identity cache, normalization/edit path |PROVEN live native state; excluded. |
|2000775C..20008357;20008D44..2000923F |Main/Storage stacks |PROVEN excluded; IRQ stack region also excluded. |
|Parser buffers;40024000..40024FFF |SysEx and MSD/DMA temporary ownership |PROVEN excluded; no retention claim. |
|Other initialized/BSS/zero gaps, split records |No complete owner/alias exclusion identified by census |UNKNOWN, not safe merely because fixture-zero or not directly addressed. |

Sources: {old('phase42-exact-rdiag-integration','findings.md')}, {old('phase45-nor-mutation-closure','heap-stack-status.md')}, {link(REF/'tools/rdiag.py')}, {link(REF/'tools/probe35s.py')}, {here('app-0806b6cc.asm')}, {here('app-0806b850.asm')}, {here('app-0806bc30.asm')}.

**STRONG INFERENCE — proposed12-byte union:** control32 atD70 contains phase3 bits, sticky unqualified-history bit,28-bit generation;8 bytesD74..D7B contain canonical geometry until raw admission. After geometry export and atomic authorization, the payload can become raw-only bookkeeping: target mask, session, chunk, owner and32-bit start tick. Geometry may be released at this transition because it is no longer independently mutable/re-exportable; every needed raw ownership/timeout field remains representable. Terminal state rejects another raw capture.

**UNKNOWN:** re-laying out the record requires replacing all old getter/watch/admission/raw/terminal access contracts and reserving it before mount. Existing lazy initialization is too late if it clears a snapshot. Reusing the existing12-byte capacity creates0 additional heap demand, but does not prove early reservation timing or whole-boot demand. No new layout is installed, no52-byte reservation is attempted, and no location is declared qualified.

**UNKNOWN:** the requested complete RAM ownership proof across all indirect runtime writes has not been achieved. The scan is comprehensive in input coverage; unresolved computed aliases, boot initialization and new union compatibility remain explicit blockers rather than being hidden behind the scan counts.
''')
    save('snapshot-liveness.md',f'''
# Phase56 — write census and retention lifetime

**PROVEN — the unmodified candidate does overwrite the selected region.** Native getter5DBCC→6B6CC replaces a seeded12-byte new record with legacy magic+8 zero bytes. Preserving magic and putting the8-byte compact record at+4 instead also fails: its first byte is1 for the reference layout, so the native timeout hook interprets it as ACTIVE and changes it to3 after the modeled deadline. Both collisions are persisted, using code byte-equal to the corrected image. {here('liveness_probe.py')}, {life}.

|Writer class |Known path / proof status |
|---|---|
|Initialization/clear |PROVEN getter6B708/70A clears payload;6B714 publishes magic. New early snapshot must prevent this later clear by replacing the owner contract, not just writing earlier. |
|Heap growth |PROVEN allocator1D7D8 reads limit/cursor and traps when exceeding limit. Existing reservationD70 protects bytes only after installed and while its limit is honored; earlier timing and every allocator alias are UNKNOWN. |
|Task stacks |PROVEN modeled Main/Storage bounds do not intersectD70; UNKNOWN all boot/IRQ/FPU stack high-water. No stack margin is counted as available memory. |
|DMA ranges |PROVEN selected QSPI/parser/MSD modeled DMA buffers do not intentionally targetD70; UNKNOWN complete all-controller boot DMA-range closure. |
|SysTick/callback |PROVEN watch6B748 reads state/tick and writes+4; SysTick5998E calls it. It must be converted to the new union phase protocol. |
|USB/SysEx |PROVEN admission6B798 writes state/session/tick and raw6B850 updates chunk/owner; no incoming frame is the retention owner, but these native writers still collide. |
|Audio/Master FX |PROVEN private record sits below retained220 bytes; service uses shared getter, whose repeated or first init behavior must preserve the new schema. All computed interior feature aliases are not globally closed. |
|Delayed work |PROVEN known old timeout accesses; UNKNOWN entire boot/deferred callback census. |
|Terminal success/failure |PROVEN existing corrected PRIMASK fragment6BC30 targets legacy state byte+4; it cannot remain unchanged under the new layout. |

Evidence: {census}, {here('app-0801d7d8.asm')}, {here('app-08059970.asm')}, {here('app-0806b6cc.asm')}, {here('app-0806b850.asm')}, {here('app-0806bc30.asm')}; previous scoped stack/DMA evidence: {old('phase42-exact-rdiag-integration','findings.md')}.

**STRONG INFERENCE:** replacement of those owners with one union lifecycle can preserve retention from mount to export/raw decision without allocating more memory. Read-only geometry export must not update the eight payload bytes; transitions update only control. At ACTIVE, reuse of payload for raw bookkeeping is intentional and occurs only after the geometry decision is committed. Every terminal failure retains no-retry ownership. The abstract model enforces this but is not a replay of all native writers.

**UNKNOWN — liveness gate remains open.** The selected record is owned and suitably sized after minimization, but the current native owner semantics conflict. No normal-path no-overwrite proof exists for a corrected union implementation because that implementation is not emitted. A canary-only host model cannot replace this proof. The two native collisions reject naive reuse; they do not prove a carefully integrated redesign impossible.
''')
    save('async-startup-exclusion.md',f'''
# Phase56 — asynchronous startup and copy atomicity

**UNKNOWN:** no complete proof that all normal concurrent execution cannot initiate persistence between native mount success and snapshot completion. Phase55's1AE06 Main instruction window is retained; it is not promoted to scheduler exclusion.

|Context |Authenticated evidence / unresolved predicate |
|---|---|
|Scheduler |Application kernel/current-TCB is live before Main mounting; captured Main TCB2000835C, Storage20009244. Bootloader SVC/PendSV/SysTick evidence is preserved but does not supply application ready queues at1AE06. Exact ready set/priorities at that point UNKNOWN. |
|Higher-priority tasks/UI |Native Main/UI/Storage/IDLE name candidates are present; one UI name is stale boot evidence. No standalone USB task can be inferred from a missing string. Actual preemption eligibility UNKNOWN. |
|Storage |5767C drains SD worker24014 at576A6 and NOR at576B0, then waits. A pending program/erase operation can execute if present; wrapper return does not attest that every other queue is empty. Normal pre-mount producer/queue closure UNKNOWN, not a claim a write occurred. |
|USB |Native IRQ/ring/TX plumbing can run asynchronously. Main parser work and normal write protection are reused; complete startup USB queue/callback predicates at mount UNKNOWN. |
|SysTick |5998C→6B748 includes the proven record-writing timeout hook. It is not a filesystem producer in the reviewed path, but breaks naive retention. |
|DMA IRQs |573E0→22826 QSPI completion and573EE DMA service notify/drain state. Selected IRQs do not themselves call file write; already active peripheral writes would not be stopped by a later PRIMASK mask. |
|Timers/deferred work |248CE schedules150-tick callback248B4→38C54; known body changes USB mode/class. SC35D8 persist19 resync is RAM/DSP. All deferred stock content producer predicates are not closed. |

Sources: {census}, {here('app-0805767c.asm')}, {here('app-080573e0.asm')}, {here('app-08059970.asm')}, {here('app-080248b4.asm')}, {here('app-08038c54.asm')}, {old('phase37-systick','findings.md')}, {old('phase45-nor-mutation-closure','background-write-analysis.md')}.

**PROVEN conditional capability:** queued op2/3 in native worker24014 reaches backend program/erase. **UNKNOWN:** a normal producer has queued such an operation before initial mount's copy. Neither “a queue could contain a write” nor “one model queue is empty” decides the required normal-boot reachability question. No invented simultaneous writer is presented as a measured failure.

## Native atomic commit microexperiment

**PROVEN scoped:** a46-byte isolated Thumb helper is assembled/executed only inside emulator memory; no image/SYX/patch is produced. Inputs:r0=private record pointer,r1/r2=already encoded payload,r3=expected INVALID generation/control. It preserves r0–r12, SP, supported APSR flags and prior PRIMASK; saves24 stack bytes. It saves flags/mask, masks interrupts, compares current control, writes two payload words, executes DMB, and writes VALID control **last**. A changed generation skips publication. {here('commit_probe.py')}, {here('commit-helper.asm')}, {commit}.

**PROVEN:**12 cases cover PRIMASK0/1, matching/mismatching generation and three supported flag patterns. Adjacent word canaries survive. Matching path16 instructions total,10 entered while a newly set mask is active; mismatch10 total,4 entered masked. The0x500F0000 input flag pattern reads back with GE bits unsupported by this emulator; physical GE preservation is not separately proved. The helper emits APSR_nzcvqg restoration but tests certify only modeled supported flags.

**STRONG INFERENCE estimate:** a no-stall one-instruction-per-cycle accounting gives16 instruction slots for success,10 of them masked, plus branch/load/store/stack/barrier stalls; it is an illustrative approximation, **not** modeled silicon cycles or a safe-latency bound. Actual M7 issue/cache/bus/DMB latency and forbidden IRQ-latency thresholds remain UNKNOWN. Source collection/packing and original caller wrapper add code/time/stack not measured here. Those totals must not be mislabeled a16-instruction complete snapshot.

**UNKNOWN:** the helper does not close the whole mount-success-to-source-read window. Its packed input could already be incoherent unless every geometry writer invalidates before mutation and generation is checked across collection. It masks only conditional copy+publication (plus the compare/control operations), never a wait or filesystem call. No short mask can cancel earlier in-flight NOR DMA. NMI/fault/reset are not masked and abort successful acquisition rather than being silently certified. Full snapshot packing/ownership/latency and asynchronous exclusion remain unqualified.
''')
    save('remount-invalidation.md',f'''
# Phase56 — geometry-changing event inventory

**PROVEN:** exact-image direct/literal/initialized-pointer candidates and corroborating bodies are saved in {census}. Virtual targets are rooted in flash vtable0805BD1C (mount1ADDC,unmount1AE1C). Computed dispatch clients and all automatic predicates are not completely resolved; the table below is a concrete inventory with explicit gaps, not a claim of complete enumeration.

|Path / trigger |Automatic or user |Before geometry / before raw? |Geometry effect / required invalidation |
|---|---|---|---|
|1F0A8→1AE3A→vtable1ADDC |Automatic startup NOR then SD |Yes / yes |Writes backing wrapper atdisk+4, then mounts; initial NOR acquisition only after fresh success |
|1ADDC→19A92 at1AE02 |Mount/reinitialize object |Yes if initialization retried / yes |19AB6/19ABE clear type;19AC2 replaces registered pointer; invalidate NOR before registration |
|1AE1C→19A92 at1AE34 |Unmount via vtable+4 |Root trigger/predicate UNKNOWN; possible later volume teardown |Unregisters FS/type; invalidate before clear, not after |
|197A0 slow path197EC |Automatic lazy remount when type0/not-ready |Yes through ordinary file operations / yes |Clears type and reparses; hooking only19A92 misses this route |
|File APIs calling197A0 |Open19AFE; opendir1A0DA; path/status1A28C; free-space1A368; unlink1A44A; attribute/time1A4E6/1A626 |Normal content jobs; exact automatic vs UI predicates vary |Usually cached fast path; if media status changes, can enter the slow remount path |
|Disk ioctl1AE90 op2 at1AECC..1AEDE |Automatic mount sector-size query and any later supported query |Yes / yes |Stores queried stride togeometry+4; an identical query during initial mount is not proof of a post-valid change. Invalidate before actual change and normalize nested mount events. |
|Binding write1AE3A |Startup direct calls1F0B4/1F0C6; other computed users UNKNOWN |Yes / yes |Changes disk backing pointer even if geometry bytes match; NOR binding must be part of epoch |
|Full parse19A32..19A4A |Successful slow mount |Yes / yes |Publishes type/ID/sync; new snapshot must be tied to this completed generation |
|USB mode/eject248B4→38C54 |Settings/deferred/eject |May be before host/raw |Reviewed mode/class path itself has no direct f_mount/unmount call. Full class teardown virtual clients remain UNKNOWN; do not declare every USB transition a remount or prove none globally. |
|Reset/scatter/object reconstruction |Reset automatic; explicit restart separately controlled |Before new boot host request |Invalidates all volatile evidence; old token must never carry into new acquisition |
|Reformat/partition change |No formatter found in reviewed normal boot chain |UNKNOWN complete native interface root enumeration |Mount code is not formatting. No assumed format operation; any discovered writer/rebuilder must invalidate before changes. |
|Explicit factory/resource/updater/identity commands |User-driven, outside fixed capture workflow |Excluded policy, not quietly enabled |Can bypass file mappings. Keep them excluded; geometry is not authority for arbitrary raw writes. |

Sources: {here('app-08019a92.asm')}, {old('phase55-precleanup-geometry-snapshot','app-08019734.asm')}, {here('app-0801ae1c.asm')}, {old('phase55-precleanup-geometry-snapshot','app-0801ae90.asm')}, {old('phase48-current-unit-geometry','formatter-layout.md')}, {old('phase47-filesystem-state-closure','initialized-ram-callback.md')}.

**UNKNOWN:** full alias proof for all stores into geometry/registered FS/backing objects, all vtable clients, and every reset/rebuilder path. Invalidation at19A92 alone is **PROVEN insufficient coverage** because native cached filesystem APIs can directly enter197A0's slow initialization. A concrete implementation must cover both paths without counting nested initial mount callbacks as independent historical epochs.
''')
    save('generation-gating.md',f'''
# Phase56 — generation and volatile admission model

**STRONG INFERENCE:** reuse12 bytes as control32+payload64. Control holds phase3 bits, sticky history bit and28-bit mount generation. Phases:EMPTY,VALID,EXPORTED,ACTIVE,SUCCESS,FAILED,INVALID,UNSUPPORTED. Do not wrap the generation: exhaustion gives terminal FAILED. Reset also invalidates the transport session;28 bits alone is not a cross-boot token. A fresh host session must re-export geometry after every connection/boot boundary.

At initial normalized mount event:invalidate, generationG; collect/check/pack8 bytes; compare sameG and publishVALID last. Export returns exact scalars, generation and frame CRC; records are immutable through decision. Authorization is explicit, scoped to fixed target mask1(identity),2(coefficients),3(both), and carries the exported generation plus record digest and current host transaction token. Reject unsupported masks/addresses, nonEXPORTED state, stale generation/digest, history taint or failed ownership.

At accepted authorization, atomically transitionEXPORTED→ACTIVE before any raw read/queue submit. The8 payload bytes may then become target/session/chunk/owner/start-tick bookkeeping; geometry is no longer exportable. Timeout/success/failed terminal publication must preserve the old one-shot ownership/quarantine semantics under this new encoding. A remount writer that loses the admission race must be rejected/deferred **before** it changes geometry or initiates persistence; it cannot merely increment a generation after the raw operation is queued.

**PROVEN in abstract model:**7 scenarios and4 event insertion positions reject stale generation/digest, keep identity authorization separate, fail closed on generation exhaustion and serialize ACTIVE versus geometry mutation under the stated interception assumptions. {here('lifecycle.py')}, {model}. It is not native queued I/O proof; no real read occurs.

## Historical preservation correction

**PROVEN logical counterexample:** epochG1 may have unsafe geometry and mutate82000 before the host decides; a subsequentG2 safe mount and perfectly matchingG2 authorization cannot recover original coefficients. Fresh generation prevents using a stale *current* layout, but does not prove the evidence survived *earlier* layouts. This is a reasoning counterexample, not an induced normal firmware overwrite.

**STRONG INFERENCE — smallest conservative repair:** any post-initial geometry-changing event sets a sticky unqualified-history bit for the rest of the boot. Successful new mount may capture new bytes, increment generation and set current geometryVALID, as requested, but **raw_capture_allowed remains false** because earlier-history preservation is not certified. New geometry may still be exported for diagnosis. Clearing the bit on a successful remount would be unsound. Supporting safe raw admission after multiple epochs would require a qualified cumulative history proof or prevention of persistence under every unapproved epoch; neither is implemented.

Nested registration/stride-query/parse events within one initial mount transaction must be normalized so they do not falsely indicate an earlier usable filesystem epoch. **UNKNOWN:** native event normalization and every required pre-mutation hook. Even a conservative policy that rejects every later event must be placed before every actual changer. It cannot be certified from the abstract state model alone.
''')
    save('toctou-review.md',f'''
# Phase56 — TOCTOU and original-byte preservation

|T1 export→T2 read event |Required behavior / status |
|---|---|
|Same mounted geometry, normal settings deletion/flush |PROVEN conditional mapping theorem: changes entries/cache flags, not bounded geometry. Those normal writes remain outside both targets under accepted record/invariants. |
|Unmount/register/remount/lazy reparse |Invalidate before changes; reject old token. Sticky history blocks raw even for a new currently safe record unless all intervening epochs were separately qualified. |
|Backing wrapper/stride change |Invalidate even if FAT scalars coincide. Expected NOR identity/base/stride is part of capture contract. |
|Reset/boot/USB session loss |No token reuse; require fresh export/session binding. Current model has only same-boot generations, not a cross-boot identity proof. |
|Record corruption |Validate reserved bits/frame CRC; compare requested digest with retained bytes before admission. A digest is not complete arbitrary RAM-fault detection or ownership proof. |
|Simultaneous authorization and invalidation |Atomic winner; if invalidation wins,0 submits. If ACTIVE wins, geometry-changing producer must defer/reject before mutation. An increment-only observer is insufficient. |
|Queued/in-flight NOR mutation predating snapshot |Short PRIMASK cannot stop it. Startup producer/queue and source-preservation exclusion must already hold; UNKNOWN. |
|Change after first raw request queued |No safe cancellation/unwind is assumed. Prevent mutation under ACTIVE or fail/discard with original one-shot quarantine; do not release semaphore/retry. Exact native interlock UNKNOWN. |
|Factory/update/resource command |Excluded fixed workflow; geometry proof does not authorize it. An interface capable of bypassing file mappings must not silently be admitted alongside capture. |

Sources: {here('remount-invalidation.md')}, {here('generation-gating.md')}, {old('phase31-storage-error-recovery','findings.md')}, {old('phase47-filesystem-state-closure','target-preservation.md')}.

**PROVEN conditional:** if the initial snapshot predates persistence, every writable mapping is bounded, all geometry-changing writers are intercepted before mutation, and authorization/admission is atomic, the host's same-epoch decision remains valid until raw acquisition. Model event orderings enforce that conditional contract. **UNKNOWN:** all antecedents for the actual native implementation.

**PROVEN:** geometry does not contain the512 coefficient bytes. Native DSP staging reused after35EE6 cannot later supply original evidence without retention. Therefore this architecture still needs the fixed82000..821FF physical read, admitted only after the geometry/preservation gate; it is not replaced by the mapping record. {old('phase54-early-evidence-snapshot','stock-read-lifetimes.md')}.

|Target |Independent intended admission |Current qualification |
|---|---|---|
|81000..81016 |Needs file-mapping exclusion plus separate identity-history policy; explicit identity erase ends82000 exclusive |UNKNOWN, raw disabled |
|82000..821FF |Needs file-mapping exclusion, initial epoch/history and no bypass writer; does not inherit identity-only veto |UNKNOWN, raw disabled |

The model accepts coefficient-only mask2 without identity authorization and rejects identity mask1 unless its separate predicate is provided. The existing combined23+512 command cannot silently become coefficient-only without a separately tested target-mask adaptation. H4 remains FAIL for late raw reads; host discard/no retry/power-cycle boundary containment stays required. No recovery/restore action is executed.
''')
    save('revised-architecture.md',f'''
# Phase56 — proposed minimal architecture and decision

**STRONG INFERENCE — retain optionA:** canonical geometry8 bytes + control4 within the existing12-byte private diagnostic capacity. This avoids the unqualified52-byte extension and does not use heap tail, stack, parser, DMA, filesystem scratch or audio state. The owned capacity is real; its new lifecycle is not yet qualified.

BOOT: reserve the existing12-byte private record before mount without an allocator call; initialize EMPTY. During the first normalized NOR mount transaction, verify binding/source status, gather canonical fields, compare generation and commit VALID last at the established successful-mount boundary. Retain all stock Main/Storage ownership and original mount exactly once.

HOST STEP1: fixed geometry-only request; read retained bytes only, no Storage/NOR/filesystem API. Return exact compact fields, validity/history/generation, protocol/code version and checked framing. Host independently reconstructs domains and evaluates each fixed target.

HOST STEP2: explicit target mask/current-session/generation/record-digest authorization. Device atomically checks admissibility, marks ACTIVE, overlays geometry payload with raw bookkeeping and issues only the requested fixed read(s). No arbitrary address, automatic capture or retry. Every remount/binding changer must invalidate before mutation and lose against ACTIVE admission safely.

|Cost |Phase55 proposal |Phase56 proposal / proof limit |
|---|---|---|
|Geometry payload |46 |8 bytes, tested bounded FAT12/16 scalar encoding |
|Simple geometry+state |52 additional bytes |12-byte union replacing an existing12-byte owner;0 additional reservation proposed |
|New heap allocation |0 but capacity reduction52 |0; early reservation of existing capacity/liveness UNKNOWN |
|Site hook |4-byte mount-call replacement |Same site plus all lifecycle/legacy-owner adaptations; total code UNKNOWN |
|Atomic helper |Not emitted |46 emulator-only ARM bytes;16 success instructions,24-byte temporary stack; not a complete hook |
|Added NOR for geometry |0 |0 |
|Raw H4 |Retained after host gate |Retained; old failure containment must survive union redesign |
|Remount safety |Epoch interlock missing |Abstract interlock and sticky history model tested; native coverage/interlock UNKNOWN |

**PROVEN:** this phase produces documentation, scans, pure models and one isolated emulator commit helper, never a firmware image/SYX. No existing candidate is modified. **UNKNOWN:** total pack/collect/wrapper code size/cycles/latency; the helper's exact counts must not be presented as full integration cost.

**UNKNOWN — architecture remains unqualified.** Concrete progress is the8-byte representation, a12-byte owned-capacity strategy, two reproduced native liveness collisions, a bounded commit helper and a corrected history-aware gate model. Remaining requirements are all-native owner replacement/liveness, early reservation timing, startup producer/queue exclusion, complete geometry-writer interception and real admission/defer behavior. Only after those close may a later phase build a candidate; this phase does not authorize that build.
''')
    save('findings.md',f'''
# Phase56 — geometry snapshot lifecycle

**UNKNOWN: lifecycle is UNQUALIFIED.** The geometry shrinks enough to fit existing private capacity, but that capacity's current writers and the complete native startup/remount interlock are not qualified for reuse.

**PROVEN:** the required bounded FAT12/16 scalars encode losslessly into8 bytes;5 saved native-mount round trips,7 rejects and16 factor cases pass. Host can independently reconstruct and check the mapping domains; no device-only yes/no decision replaces the evidence. Unsupported layouts fail closed. A universal information-theoretic minimum is not claimed. {here('minimal-snapshot-layout.md')}, {compact}.

**PROVEN:**20044D70..20044D7B is an existing12-byte diagnostic-owned reservation. It has no unused bytes under its old format. Native getter initialization destroys a proposed geometry record, and native SysTick timeout corrupts compact geometry interpreted as legacy ACTIVE state. A proposed4+8 union requires adapting all those owners; the unsafe52-byte extension is not used. {here('ram-ownership.md')}, {here('snapshot-liveness.md')}, {life}.

**PROVEN scoped:** isolated native commit helper tests pass12 mask/generation/flag combinations, two payload stores before validity, DMB,24-byte stack and original mask/supported register/flag preservation. Success16 instructions,10 mask-set entry instructions; full snapshot collection/packing/cycles and physical latency remain UNKNOWN. {here('async-startup-exclusion.md')}, {commit}.

**UNKNOWN:** no complete exclusion of every normal asynchronous producer before snapshot; Storage can service already queued work and PRIMASK cannot undo prior DMA. Full computed geometry-write/remount roots remain open. The census scans the entire exact image and saved initialization/RAM but is not represented as a complete alias theorem. A19A92-only invalidation hook would miss native197A0 slow remounts. {here('async-startup-exclusion.md')}, {here('remount-invalidation.md')}, {census}.

**PROVEN logical issue:** a safe later remount plus matching token cannot establish that an earlier unsafe epoch preserved82000. The model therefore sets a sticky history flag after a post-initial geometry change. It can export a new VALID current snapshot but refuses raw capture for the rest of that boot.7 lifecycle scenarios and4 orderings pass under explicit all-writers-intercepted/atomic-admission assumptions. {here('generation-gating.md')}, {model}.

**UNKNOWN:** native authorization→queue-submit and ACTIVE→deferred geometry-change interlock; no successful abstract model is promoted into a firmware proof. Identity81000 and coefficients82000 have independent authorization predicates, but both remain disabled pending shared prerequisites.82000 still requires its fixed physical read after admission; mapping evidence is not coefficient evidence. {here('toctou-review.md')}.

|Gate |Result |
|---|---|
|Small independently auditable record |PROVEN8-byte admitted-domain encoding |
|Owned long-lived capacity |PROVEN existing12-byte owner; UNKNOWN new schema liveness |
|No overwrite through export/raw decision |PROVEN naive reuse fails; UNKNOWN redesigned native owner closure |
|Complete asynchronous startup exclusion |UNKNOWN |
|Atomic copy/publication |PROVEN isolated helper; UNKNOWN full source collection/hook/latency |
|All remount/binding invalidators |UNKNOWN completeness |
|Same-boot stale-token rejection |PROVEN conditional model; UNKNOWN native integration |
|Original-byte preservation across past epochs |PROVEN generation-only gap; STRONG INFERENCE sticky-history repair |
|Architecture build admission |UNKNOWN; no candidate build authorized |

**UNKNOWN — smallest next offline experiment:** integrate the proposed12-byte union owners solely in emulator fragments and replay existing getter/retained Master-FX init, SysTick quarantine, geometry export and atomic raw admission with write guards; preserve all old one-shot failure cases. Separately the normal startup queue and every geometry-changing producer must be closed before a final PASS. Do not build a full firmware or use a no-observed-write replay as a reachability proof. {here('revised-architecture.md')}.

**PROVEN:** nine requested reports, saved test outputs and exact-image listings are present. {here('validation.json')} verifies earlier evidence/pinned-source preservation and all report links. No hardware/MIDI ports, firmware/SYX output/transmission, historical candidate modification, or revival of the exhausted Phase53 branch occurred.

GEOMETRY SNAPSHOT LIFECYCLE = UNQUALIFIED
''')
if __name__=='__main__':main()
