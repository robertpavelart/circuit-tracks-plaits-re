"""Phase55 documentation only; no builder or device imports."""
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
REF=Path('C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main')
def link(path,label=None):return f'[{label or Path(path).name}](<{Path(path).as_posix()}>)'
def here(n):return link(OUT/n)
def old(p,n):return link(ROOT/'builds'/p/n)
def reference(n):return link(REF/n)
def save(n,t):(OUT/n).write_text(t.strip()+'\n',encoding='utf8')
def main():
    mount=here('app-08019734.asm');wrapper=here('app-0801addc.asm');tests=here('mount-cases.json')
    prior_geometry=old('phase49-existing-geometry-reader','live-geometry-structure.md')
    phase47=old('phase47-filesystem-state-closure','target-preservation.md')
    persistence=old('phase46-msd-filesystem-closure','persistence-routes.md')
    transport=old('phase42-exact-rdiag-integration','findings.md')
    save('mount-to-persistence-ordering.md',f'''
# Phase55 — mount to first persistence

**PROVEN:** the application Main task calls0801F0A8 at0801D4C0, then content/settings initialization0801F0F0 at0801D4C4.1F0A8 binds NOR disk20000AA0 to[20006968] and invokes its initialization vtable,0801ADDC. It then initializes the separate SD disk20001AF4. This is synchronous Main initialization, not a new Storage job. Mount's sector reads are serviced through the existing disk/Storage path. {here('app-0801d4b0.asm')}, {here('app-0801f0a8.asm')}, {wrapper}; prior task context: {old('phase54-early-evidence-snapshot','writer-ordering.md')}.

**PROVEN:**1ADDC builds0:, calls08019A92(fs=disk+10,path,opt=1) at0801AE02.19A92 clears the old and new FS types at19AB6/19ABE, registers the pointer at19AC2, then calls197A0. The mount validates and assigns BPB-derived geometry. On the full successful parse,19A32 commits FAT type,19A40 writes mount ID,19A46 writes synchronization pointer and19A4A clears an internal field. At19A4C all these are complete and R0=0. At the caller **0801AE06** the complete successful mount has returned, before logging and before the next SD mount or content/settings construction. The common19A4C is also an error/fast-path exit and is not by itself a success-only hook. {mount}, {here('app-08019a32.asm')}, {wrapper}.

**PROVEN YES — a deterministic instruction window exists in the native synchronous Main path:**

`NOR mount success → 0801AE06 snapshot boundary → return from1ADDC/1F0A8 → 0801D4C4 content/settings construction → conditional persistence`.

This is a proof of the instruction window and ordering of these producers, not a universal no-other-task-write theorem. **UNKNOWN:** complete preemption/deferred-job closure across all normal boot roots has not been established. No full cold boot is claimed. A qualification requiring that no normal asynchronous persistence has already run must still establish that startup queue/root invariant, or place acquisition under an existing correctly owned mount exclusion. No long interrupt masking is proposed to hide this obligation.

| Producer | Earliest established edge relative to window | Result |
|---|---|---|
|Mount itself |19734 clears dirty flag before loading boot sector; BPB parse/optional FAT32 FSInfo read and metadata assignments follow |PROVEN no array-write calls in eight modeled native mount cases; reviewed code is read/parse, not formatting |
|Settings validation |1D4C4→1F0F0, constructor1FAD4→2CFB8→2D060 |PROVEN after Main NOR snapshot point |
|Conditional deletion/flush |2D060 invalid nonempty settings branch→3C97A/3CC54 |PROVEN known first startup persistence producer downstream; conditional, not every boot |
|FAT/directory updates |Unlink1A440→191A8/188E0→18612→1859A, or file writes |PROVEN downstream of initiating filesystem producer; earliest all-task invocation UNKNOWN |
|Settings changed callback |2D052 registration→3BAFC; callback2D278→2D2AC |PROVEN registration in later settings construction; later dirty save cannot precede its own registration |
|Project/session restoration/save |Later constructed content/session objects; stock save path2FE88→3C946 |STRONG INFERENCE normal Main startup is later; UNKNOWN full background scheduling closure |
|SC35D8 persist19 |c_pl_load/c_rs/c_dtick19 RAM/DSP work; c_pl_save funnels stock save |PROVEN no new custom raw NOR writer in reviewed resync; stock save remains separate |
|Deferred USB work |Normal write protection/mode callbacks preserved |PROVEN reused normal-path exclusions; no new malformed-host or late B1.3 timer investigation |

The exact first *physical* write for every boot state is **UNKNOWN**: valid/missing settings may produce no write, while conditional cleanup can. Do not relabel the earliest known producer as a proved exhaustive earliest scheduler event. Sources: {persistence}, {old('phase47-filesystem-state-closure','startup-persistence.md')}, {old('phase45-nor-mutation-closure','background-write-analysis.md')}, {phase47}.

**PROVEN:** eight fresh native tests run1ADDC and, in one case, the enclosing1F0A8 NOR-then-SD constructor. They include invalid BPB, failed read, not-ready disk, stale geometry, a changed valid layout and mount-ID wrap. No disk program/erase entry executes; mounted geometry is available at1AE06 only on success. Disk data/status/ioctl completion and UART logging are explicit seams. This does not rerun Phase47 or supply actual-unit NOR bytes. {here('audit.py')}, {tests}.
''')
    save('geometry-record.md',f'''
# Phase55 — minimum practical geometry record

**PROVEN:** reuse the existing **46-byte packed record**, not a contiguous46-byte structure:20000A98:8 ||20000AB0:14 ||20000AD0:24. It contains mapping context and mounted geometry while omitting the filesystem sector window, path/FILE state, RTOS sync pointer and cached free-space values. This is the smallest already-reviewed compatible record, not a claim of mathematical minimum bit packing. {prior_geometry}; {old('phase49-existing-geometry-reader','geometry_parser.py')}.

|Packed offset |Source / FS offset |Bytes |Meaning |
|---|---|---:|---|
|0 |20000A98 |4 |Physical partition base |
|4 |20000A9C |4 |Disk mapper sector stride |
|8 |FS+00 |1 |FAT type0/1/2/3 = unmounted/FAT12/FAT16/FAT32 |
|9 |FS+01 |1 |Logical drive, must be0 |
|10 |FS+02 |1 |FAT count |
|11 |FS+03 |1 |Dirty-window status, not geometry |
|12 |FS+04 |1 |FSInfo flags |
|13 |FS+05 |1 |Padding, carries no validity meaning |
|14 |FS+06 |2 |Mount ID, may legitimately wrap to0 |
|16 |FS+08 |2 |Fixed root entry count |
|18 |FS+0A |2 |Sectors per cluster |
|20 |FS+0C |2 |Bytes per sector |
|22 |FS+20 |4 |n_fatent |
|26 |FS+24 |4 |Sectors per FAT |
|30 |FS+28 |4 |Volume base LBA |
|34 |FS+2C |4 |First FAT LBA |
|38 |FS+30 |4 |Fixed root LBA or FAT32 root cluster |
|42 |FS+34 |4 |Data start LBA |

**PROVEN:** FS=20000AB0, registered drive0 pointer[20005E5C]; FS header3C bytes followed by1000-byte sector cache. Occupied FS extent103C and disk+FS extent104C are **STRONG INFERENCE** from adjacent object layout and native offsets, not debug type declarations. Disk=20000AA0: +4 wrapper,[20006968] must match; +8 geometry pointer20000A98; +C drive0; +10 embedded FS. These backing checks must be performed by acquisition, since46 bytes alone do not contain the wrapper pointer or code identity. {prior_geometry}, {here('app-0801f0a8.asm')}, {here('app-0801ae90.asm')}.

**PROVEN:** derive reserved=fatbase−volbase; first cluster2, last=n_fatent−1; dataend=database+(n_fatent−2)*csize. The BPB total is not retained as an exact scalar. Its possible interval is[dataend−volbase,dataend+csize−1−volbase], subject to independently accepted physical bounds. With csize1 this is exact; otherwise do not invent an exact total. The native data/FAT/root/FSInfo write domains can be bounded without the lost trailing-sector remainder. FAT32 root is a cluster, not an LBA. {prior_geometry}; {old('phase47-filesystem-state-closure','real-filesystem-geometry.md')}.

**STRONG INFERENCE:**46 bytes plus explicit fresh-success/binding/epoch validity is sufficient for the Phase47 normal-write exclusion calculation. A separate volatile header should convey version, success/FAILED, boot/mount epoch and integrity checks. Minimum logical payload+validity=47 bytes; an aligned46-byte payload padded48 plus a32-bit state is52. More metadata increases that number; no claim that a robust epoch/CRC header fits the minimum52 is made. The optional checksum authenticates transport/integrity, not the device's identity or physical medium by itself.

**PROVEN:** the supplied-record host model reuses the old parser and correctly handles a native successful zero mount ID with explicit fresh-success provenance, leaving the original bytes unchanged. It accepts the bounded model layouts and rejects incomplete/provenance-failed records. {here('host_gate.py')}, {here('host-gate-cases.json')}. No current-unit record has been obtained.
''')
    save('geometry-authenticity.md',f'''
# Phase55 — authoritative native geometry

**PROVEN:** native mount197A0 assigns the fields used by native filesystem operations:18698 bounds clusters using+20 and computes sectors from+34/+A;1859A flush uses+38/+24/+2;18612 handles FAT32 FSInfo using+28; native disk mapper1AF1E uses disk+8 base/stride and disk+4 backing wrapper. A record copied from those actual objects at the successful mount boundary describes the very geometry controlling subsequent normal mappings, irrespective of whether an external host can authenticate a separate READ(10). Sources: {mount}, {here('app-0801859a.asm')}, {here('app-0801ae90.asm')}, {old('phase46-msd-filesystem-closure','filesystem-lba-binding.md')}.

**PROVEN:** full f_mount19A92 invalidates the old registered object at19AB6 and new object at19ABE before registration19AC2 and parse. Thus an old type3 plus stale data cannot masquerade as success in the tested fresh mount path. Error tests leave type0 at1AE06, even if other geometry scalars retain old/partial values. A nonzero type or plausible fields alone are not an admission predicate. Check native returnR0=0, expected registered object, logical drive and physical binding. {mount}, {tests}.

**PROVEN:** direct inner197A0 can take its cached-mounted fast path197D0..197EA when type is nonzero and disk status permits. That is not proof of a fresh parse. The proposed site wraps the full19A92 call in1ADDC; it must not silently move to a generic successful cached filesystem call. Full parse commits type at19A32 *before* ID/sync publication ends19A4A, so copying immediately at the type store is too early. The caller1AE06 is after complete return. {mount}, {wrapper}.

**PROVEN:** mount-ID counter increments in16 bits at19A3C, and valid success can carry ID0 at19A40. The Phase49 conservative parser rejects0 without corroboration; Phase55 native-ID-wrap test supplies that corroboration. IDs alone cannot be boot/session authenticity tokens or remount guards. {tests}, {here('host_gate.py')}.

**STRONG INFERENCE:** if a qualified hook on the actual running unit copies the actual registered drive0 object after this fresh native success, validates its wrapper binding and retains a coherent record, it supplies authoritative **current mounted mapping**. It need not authenticate a second raw physical read of the BPB. Even a stale but accepted disk-read payload would affect the geometry native code actually uses; this is a control-state provenance question, not certification that the physical BPB is correct. Failed/stale mount structures must still be excluded by the native fresh-success path.

**UNKNOWN:** actual current-unit geometry, full hook implementation, all-task exclusion and safe retention. None of the synthetic BPB tests is promoted into a unit capture. The record and transport CRC are not cryptographic attestation against altered firmware or a malicious device; that threat model is not introduced. Authenticity here means exact-image native data/control provenance under the normal firmware path. Phase53 remains closed.

**UNKNOWN:** an old record cannot automatically remain authoritative after unmount/remount, backing rebinding, stride changes via disk ioctl2, reset or another geometry publication. Snapshot validity needs a software epoch/invalidation contract covering those writers; mount ID/type checks once at startup do not prove lifetime identity. {prior_geometry}, {here('host-gating.md')}.
''')
    save('snapshot-ram-liveness.md',f'''
# Phase55 — small fixed retention search

**UNKNOWN:** no small fixed destination is qualified. This conclusion comes from a new47/52-byte candidate analysis and actual owner review, not reuse of Phase54's535-byte requirement.

|Candidate |Ownership/liveness result |
|---|---|
|Extend existing heap-top reservation by52 |PROVEN proposed lower bound20044D3C; fixture cursor20044D68 is44 bytes above it. Existing limit20044D70 has8-byte headroom. Reservation at mount time would overlap prior allocation; reservation before constructors removes capacity later used in the fixture. Actual fresh demand remains UNKNOWN. |
|Compact47 bytes including one-byte state |PROVEN still exceeds8-byte fixture headroom by39; alignment/epoch/CRC would cost more. |
|Existing12-byte one-shot latch20044D70..20044D7B |PROVEN independently owned, too small for46 payload; still needed by separate raw capture. Cannot overwrite it with geometry. |
|Master FX state20044D7C..20044E57 |PROVEN220-byte live retained state. No newly proved padding46-byte slot. |
|Historical rdiag68-byte watch log |PROVEN aliases c_gst()+120 in the84-byte Master-FX LED buffer, not a separate allocation; showing Master FX repaints it. WATCH=False/retired log code does not retire LED ownership. Rejected. |
|probe35s14-word report area |PROVEN c_gst()+104, the same idle LED buffer; idle use is not boot-to-export liveness. Rejected. |
|Parser/DMA/filesystem sector scratch, Main/IRQ stacks |PROVEN excluded by the requested ownership contract; unused capacity does not grant retention. |
|FS metadata padding / existing live46 bytes |PROVEN original geometry is live filesystem state and not a retained pre-cleanup copy; small padding fields do not provide46 bytes. Rejected. |
|Other apparent static RAM gaps / split fixed records |UNKNOWN complete ownership and writer exclusion; no location selected on the basis of one dump. |

Evidence: {here('inspection.json')} (`RAM_candidate`); {old('phase45-nor-mutation-closure','heap-stack-status.md')}; {transport}; {reference('tools/rdiag.py')} (`LOG_OFF=120`, `LOG_N=8`, header describing repaint); {reference('tools/probe35s.py')} (SC14+104 report area); {prior_geometry}.

**STRONG INFERENCE:** an explicit small reservation remains a plausible design if allocator demand can be reduced or a genuinely retired fixed owner identified. It must be initialized/invalidate before first mount, excluded from heap/task/DMA/audio/parser owners, guarded and traced through boot/USB/export, and never reinitialized by a lazy Master-FX getter after capture. Retained features must not be disabled to make the reservation appear available. No allocator is called by the proposed copy hook.

**UNKNOWN:** worst-case fresh-boot allocation/high-water and an exact nonoverlapping52-byte location. The dump overlap rejects the simple proposed address in that fixture; it does not prove that every possible small reservation is impossible. A separate52-byte epoch/CRC-capable design may need more than52. No candidate region has been written, claimed safe or incorporated into firmware.

**UNKNOWN — minimum next RAM experiment:** identify a statically retired fixed owner of at least52 bytes, or prove sufficient reclaimed allocation demand before reserving a named extent; then guard that extent across native constructor allocation, normal retained feature initialization, USB service and export. A fail-closed allocation refusal alone is insufficient for PASS if it prevents geometry acquisition on the intended boot.
''')
    save('snapshot-hook.md',f'''
# Phase55 — smallest defensible hook design

**STRONG INFERENCE:** replace the4-byte BL at**0801AE02** with a BL to a wrapper. Execute the original19A92 call exactly once with unchanged arguments and ownership. After its return, before native1AE06 MOVS/ITEE, perform only the geometry copy/validity work if this is the first NOR startup mount. Continue at1AE06 with original registers/flags/SP/control flow. This relocates the existing mount call; it adds no mount or other filesystem operation. Acquisition work after successful return has no calls to Storage, NOR, SD, filesystem or allocator. {wrapper}, {here('app-0801f0a8.asm')}.

**PROVEN:** replacing1AE06 MOVS plus1AE08 ITEE as a naive four-byte hook would displace the beginning of an IT block. Returning by a branch from a replayed ITEE would consume a conditional instruction slot incorrectly. The call-site wrapper avoids that hazard. The common mount epilogue19A4C also includes failure/fast-return paths and is not an unconditional success site. No bytes are patched in this phase.

**STRONG INFERENCE — required sequence:** initial volatile EMPTY; invoke original mount; reject nonzeroR0, wrong disk/FS pointer/drive/binding or unexpected lifecycle; copy A98:8,AB0:14,AD0:24 to owned retention; publish GEOMETRY_VALID last. Error gives terminal FAILED for that boot. No acquisition retry through later lazy mounts. Distinct reset initialization and remount/backing-change invalidators are needed for same-boot lifetime claims. Subsequent SD mount is ignored; it cannot overwrite the NOR snapshot.

|Impact |Estimate / limit |
|---|---|
|Call-site replacement |PROVEN4 ARM bytes at1AE02 |
|Added ARM code |UNKNOWN exact wrapper/copy/validation/invalidation/export bytes and safe flash pool; no fragment assembled |
|Fixed RAM |PROVEN46 payload, minimum47 with one-byte validity; aligned simple record52; extra epoch/version/CRC increases this |
|Stack |UNKNOWN actual delta until wrapper ABI is emitted; preserve LR, caller-visible scratch registers and flags, maintain8-byte call alignment. No payload stack buffer required. Do not claim zero. |
|Cycles |UNKNOWN exact modeled cycles. A simple6-instruction byte-copy loop entails276 payload-loop instructions for46 bytes, plus setup, checks and save/restore; this is an illustrative instruction calculation, not measured DSP/ARM cycles. |
|Interrupt masking |STRONG INFERENCE no mask over copy/storage/mount; publish last. Any brief epoch/state atomic update must preserve caller PRIMASK and be separately bounded. |
|Storage/NOR/SD operations added |PROVEN0 by the proposed call graph; not an implementation replay result |

**PROVEN:** the eight native tests preserve supported callee registers in the unmodified mount paths. **UNKNOWN:** before/after register/flag equivalence, retention canaries and timing of a future patched hook. This architecture-only phase does not claim those tests already cover emitted hook code. {tests}, {here('audit.py')}.
''')
    save('host-gating.md',f'''
# Phase55 — export, host admission and same-boot lifetime

**STRONG INFERENCE:** reuse rdiag framing, padded request validation, nibble encoding, checked transaction token, frame CRC and native USB router. Add a fixed geometry-only command returning the saved46 bytes plus version/magic, GEOMETRY_VALID/FAILED, mount-success/binding provenance and a software epoch. A bounded record fits the historical64-byte payload limit if header design stays within18 bytes; larger metadata needs checked fragmentation. Do not expose arbitrary RAM addresses or preserve an alternate live-Storage fallback. Exact command ID/wire encoding/export code are not allocated or implemented. Historical transport hardware evidence and prior offline command qualification are not hardware qualification of this new command. {reference('tools/rdiag.py')}, {transport}.

The geometry command reads the **retention record only**, never initiates Storage/NOR/SD/filesystem work and never automatically starts raw evidence acquisition. Snapshot pointer/binding checks happen at the mount hook. Remount/binding invalidation must update volatile validity/epoch when the underlying owner changes; a host token alone cannot establish that lifecycle. Packet CRC protects the transmitted record, not a missing RAM ownership proof.

**STRONG INFERENCE — future workflow, not present authorization:**

1. A separately qualified future build boots and captures native geometry before persistence.
2. USB becomes ready; host asks for the fixed snapshot only.
3. Host requires success/validity, expected version/code identity, fresh-mount/binding provenance, coherent epoch, exact46 bytes and CRC.
4. Validate native FAT class/count/size, sector/cluster constraints, root/data relationships and bounded nonwrapping physical mappings. Derive FAT copies, root/data and FAT32 FSInfo domains, expanding to physical erase boundaries where relevant.
5. Evaluate81000..81016 and82000..821FF independently. If82000 file-backed mutation is excluded and the retained non-filesystem exclusions and same-boot epoch still hold, host MAY admit the separate one-shot read. Geometry export itself does not admit/send it.
6. If unsafe, invalid or unknown: send no NOR evidence request. The future policy calls for restoring normal firmware by the separately qualified recovery procedure; no automatic cleanup/reset/restore is issued or certified here.

**PROVEN:** the native mapper computes32-bit base+stride*LBA. The supplied-record policy conservatively requires baseD4000, stride/BPS4096 and all normal domains within the reviewed32MiB bound, excluding wrap and both targets. For the modeled mounted FAT16 it derives FAT[D5000,DD000), root[DD000,E1000), data[E1000,2000000), so both target intervals are excluded. This reproduces Phase47 arithmetic, not an actual-unit conclusion. The physical capacity bound is a conservative acceptance condition; no new capacity query occurs. {old('phase49-existing-geometry-reader','geometry_parser.py')}, {here('host_gate.py')}.

**PROVEN:** nine pure host-gate tests accept authenticated-model layout, valid changed layout and fresh-success zero ID; reject nonzero mount status, invalid state, old mount, wrong backend, changed epoch and truncated record. Provenance booleans are explicit modeled inputs, not acquired attestation. `allow_raw_evidence=True` in these synthetic cases is not authorization to access this unit. {here('host-gate-cases.json')}.

## Same-boot reasoning

**PROVEN, conditional mapping theorem:** with fixed registered FS/binding/base/stride and validated nonwrapping geometry, later normal FAT/directory/data/FSInfo writes remain inside those same domains. Settings deletion, flushing, file creation and allocation change entries/dirty state, not the geometry used to bound all valid clusters. Therefore they need not be prevented or delayed while the host examines the saved record. The exclusion also applies to writes made after snapshot but before USB/host acceptance. The conclusion does not rely on one particular file cluster. {old('phase47-filesystem-state-closure','real-filesystem-geometry.md')}, {old('phase47-filesystem-state-closure','startup-persistence.md')}.

**UNKNOWN — unconditional same-boot admission:** the future implementation must invalidate the snapshot on unmount/re-registration19A92, a changed binding1AE3A or sector-stride assignment1AEDE, and on reset. It must keep the raw command disabled if invalidated after geometry export but before the later raw request. Reuse the existing one-shot raw-capture latch/no-retry policy and add this epoch admission predicate; merely remembering that USB stayed connected is insufficient. Normal captures under an unchanged mounted epoch are architecturally plausible, but this lifetime interlock is not implemented/qualified. {here('app-0801ae90.asm')}, {prior_geometry}.

## Separate evidence-region decisions

**PROVEN conditional:** validated mapping excludes file-backed writes to both81000 and82000 in the model. **UNKNOWN:** current-unit acquisition and full pre-snapshot ordering. Identity-specific explicit writer25228/boot05DB4 programs81000 and erases[81000,82000), whose upper bound does **not** touch82000. Identity historical semantics therefore need not veto coefficient-only capture if shared prerequisites pass. The current combined23+512 command remains all-or-nothing until separately changed/qualified; do not silently call its identity output authenticated while relaxing that gate. {phase47}, {old('phase44-preflash-redteam-closure','evidence-preservation.md')}.

**PROVEN:** C retains late raw-read H4 exposure. TEF/missing completion has no qualified bounded unwind: host discards partial output, does not retry/send another request/cleanup, and requires a power-cycle boundary under the established containment policy. No safe reboot/rollback proof is added by geometry capture. Geometry-command timeout alone adds no diagnostic Storage transaction; it still must not admit a raw request. {old('phase31-storage-error-recovery','findings.md')}, {old('phase32-host-containment','findings.md')}.
''')
    save('architecture-comparison.md',f'''
# Phase55 — three architecture choices

|Aspect |A: late raw diagnostic |B: Phase54 stock-read535 snapshot |C: geometry gate + later conditional raw read |
|---|---|---|---|
|Boot modification |Guarded late command; dormant before request |Two early copy points plus completion/reset/retention logic |NOR mount-success copy plus validity/epoch lifecycle |
|Retention RAM |Existing12-byte latch/64-byte borrowed temporary |At least535 payload plus metadata |46 payload,47 minimum or52 aligned simple state, plus optional epoch/CRC |
|NOR operations added |23-byte plus8×64-byte raw reads |0 if stock-read copying suffices |0 for geometry; same9 raw reads only after separate gate |
|Storage/H4 |Additional raw-read deadlock exposure |No diagnostic reads, stock-read failure remains |Geometry adds none; later raw step retains H4 |
|Pre-read preservation |Unqualified without current-unit mapping |82000 stock read already after settings initialization |Could close with authoritative pre-cleanup mapping and stable epoch |
|Current-unit geometry |Missing prerequisite |Not eliminated for pre-82000-stock-read activity |Captured directly from actual native mounted objects, if hook/retention qualify |
|Containment |One shot, discard/no retry on failure |No BOTH/no export on failure; stock deadlock remains |No raw admission on missing/invalid geometry; old raw containment still required |
|Complexity |Small command already tested offline |Large retention and completion fences |Small copy but new retention/epoch/host interlock and separate raw admission |
|Current decision |Preservation unqualified |UNQUALIFIED |UNQUALIFIED: RAM ownership and lifecycle/global ordering still open |

Sources: {old('phase54-early-evidence-snapshot','architecture-comparison.md')}, {here('mount-to-persistence-ordering.md')}, {here('snapshot-ram-liveness.md')}, {here('host-gating.md')}.

**STRONG INFERENCE — recommendation:** prefer C for the next bounded architecture work. It obtains the mapping native file operations actually use and needs far less retention than B. It does not depend on reviving the exhausted MSD authentication branch, and it avoids adding storage operations merely to query geometry. Keep A's already-qualified one-shot transport and failure containment for the separately admitted raw step.

**UNKNOWN:** C is not ready for a build or hardware designation. The mount window is established for the synchronous path, but full asynchronous pre-window exclusion, a fixed small RAM reservation, hook equivalence and mount-epoch invalidation remain unqualified. Do not treat47 bytes as automatically available because535 were not. No firmware/SYX or hardware action is initiated.
''')
    save('findings.md',f'''
# Phase55 — pre-cleanup geometry snapshot

**UNKNOWN: architecture remains UNQUALIFIED.** A precise native mount boundary and sufficient compact record are established. Safe fixed retention and a complete startup/lifetime interlock are not.

**PROVEN YES — synchronous instruction window:** NOR f_mount returns at0801AE06 with complete geometry before the enclosing1F0A8 finishes and before Main calls settings/content construction at0801D4C4. The full mount clears stale type, parses geometry, commits ID/synchronization state and returns0 on success. **UNKNOWN:** a universal no-prior-asynchronous-persistence claim across every boot root; the scoped Main order is not mislabeled full RTOS closure. {here('mount-to-persistence-ordering.md')}.

**PROVEN:** eight native mount tests pass, including stale/failed mounts, not-ready media, different layout, mount-ID wrap and the NOR-then-SD constructor. Nine offline supplied-record host tests pass. Model disk completions/logging and provenance predicates are explicit; no current-unit filesystem bytes or full cold boot were acquired. {tests}, {here('host-gate-cases.json')}.

**PROVEN:** the46-byte record consists of three spans, not a contiguous structure. It captures the fields native filesystem mappings actually use; fresh successful mount/binding provenance can supply current-unit authority without another physical READ(10). A mount ID of0 is valid after wrap and is not sufficient failure evidence. **STRONG INFERENCE:** the proposed capture contract supplies authoritative mounted-state geometry when correctly implemented on the unit. {here('geometry-record.md')}, {here('geometry-authenticity.md')}.

**UNKNOWN:** no47/52-byte fixed retention location is qualified. Extending the current reservation by52 places its boundary at20044D3C,44 bytes below the fixture cursor20044D68. Historical diagnostic log buffers belong to live Master-FX LEDs. No parser/stack/DMA/filesystem scratch or unproved RAM hole is borrowed. {here('snapshot-ram-liveness.md')}.

**STRONG INFERENCE:** use a4-byte replacement of the mount call at1AE02, preserving the existing call exactly once and copying after its success. Do not patch through the1AE06 IT block naively. Exact added bytes/cycles/stack and fixed RAM remain UNKNOWN until a concrete hook is emitted and verified; none is emitted now. {here('snapshot-hook.md')}.

**PROVEN conditional:** stable validated geometry bounds later normal writes even after cleanup changes files, allowing a same-boot argument. **UNKNOWN unconditional:** remount/rebinding/stride/reset invalidation and raw-admission epoch enforcement are not implemented. Geometry export must never submit Storage or automatically trigger raw capture.81000 identity-specific uncertainty is separate from82000 coefficient preservation. Architecture C is recommended conditionally; later raw capture retains H4/no-retry containment. {here('host-gating.md')}, {here('architecture-comparison.md')}.

|Gate |Result |
|---|---|
|Precise native fresh mount success window |PROVEN YES, synchronous Main path |
|All normal boot tasks cannot persist before acquisition |UNKNOWN complete queue/root exclusion |
|Record suffices for native mapping bounds |PROVEN fields/arithmetic; STRONG INFERENCE actual-unit hook contract |
|Small fixed RAM ownership through USB export |UNKNOWN |
|Read-only geometry export |STRONG INFERENCE design,0 added Storage requests; not implemented |
|Same-boot admission after geometry |PROVEN conditional geometry theorem; UNKNOWN epoch interlock |
|Actual-unit82000 preservation |UNKNOWN until qualified acquisition/host gate, independent of identity-only concern |

**UNKNOWN — smallest next experiment:** qualify one named small retention reservation (at least52 bytes for the simple aligned record, more if retaining epoch/CRC), including constructor allocation and retained LED/Master-FX/USB liveness. The trivial heap-top extension fails the existing fixture. In parallel conceptually, the identified mount site still requires bounded startup queue exclusion and lifecycle invalidation; no new engine port, firmware build or hardware action is authorized.

**PROVEN:** all eight requested reports and saved tests are in this directory. {here('validation.json')} checks prior Phase54 preservation, pinned sources, exact-image equality and report links. Earlier suites and Phase53's exhausted authentication branch were not rerun. No firmware generation/modification, SYX, candidate designation, hardware access, MIDI enumeration/opening or transmission occurred.

PRECLEANUP GEOMETRY SNAPSHOT = UNQUALIFIED
''')
if __name__=='__main__':main()
