"""Write Phase49 evidence notes only. No firmware or acquisition operations."""
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
REF=Path(r'C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main')
def link(p,label=None):return f'[{label or p.name}](<{p.as_posix()}>)'
def local(name):return link(OUT/name)
def prior(phase,name):return link(ROOT/'builds'/phase/name)
def ref(name):return link(REF/name)

reports={
'live-geometry-structure.md':f'''# Phase49 — live internal geometry

**PROVEN:** exact published B1.3 application SHA-256 is `2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41` (435220 bytes). It is inspected in memory, never rebuilt or emitted. Phase48 established byte equality of the filesystem/mount/binding code across official4486, SC35D8, B1.3 and the corrected research diagnostic. This permits reusing those native layout results; it does not authenticate the user's mounted state. {local('b13-inspection.json')}; {prior('phase48-current-unit-geometry','geometry-review.json')}.

**PROVEN:** `0801F0A8` loads geometry address `20000A98`, binds disk object `20000AA0` through `0801AE3A`, and binds its wrapper from `[20006968]`. `0801ADDC` mounts `disk+10 = 20000AB0` using `08019A92(..., opt=1)`. The drive-0 filesystem pointer slot is `20005E5C`. The following fields are little-endian scalars, not network-order words. {prior('phase48-current-unit-geometry','app-0801f0a8.asm')}; {prior('phase48-current-unit-geometry','app-0801addc.asm')}.

| Address / FS offset | Size | Meaning / native evidence |
|---|---:|---|
|20000A98 |4|physical NOR base; initialized D4000; disk mapper `0801AF1E` |
|20000A9C |4|physical sector stride; initialized 1000 |
|20000AB0 / +00|1|FAT type: 0 unmounted, 1 FAT12, 2 FAT16, 3 FAT32; commit `08019A32` |
|20000AB1 / +01|1|logical drive, internal = 0 |
|20000AB2 / +02|1|FAT copies, 1 or 2; `080198BC` |
|20000AB3 / +03|1|window dirty flag; transient, not geometry |
|20000AB4 / +04|1|FSInfo flag (80 disabled/unknown, bit0 dirty); `080199CA` |
|20000AB5 / +05|1|padding, no validity claim |
|20000AB6 / +06|2|mount ID; assigned only after successful parse, `08019A40`; can wrap |
|20000AB8 / +08|2|fixed root entry count; `080198E0` |
|20000ABA / +0A|2|sectors/cluster; `080198CC` |
|20000ABC / +0C|2|bytes/sector from disk ioctl, checked against BPB; `08019814`, `0801989E` |
|20000AD0 / +20|4|n_fatent = data cluster count + 2; `08019960` |
|20000AD4 / +24|4|one FAT size, sectors; `080198B6` |
|20000AD8 / +28|4|volume base LBA; `08019962` |
|20000ADC / +2C|4|first FAT LBA; `08019964` |
|20000AE0 / +30|4|fixed root LBA (FAT12/16) or root cluster (FAT32); `08019996` / `08019984` |
|20000AE4 / +34|4|data start LBA; `08019966` |

**PROVEN:** reserved sectors = `fatbase - volbase`; first valid cluster = 2, last = `n_fatent-1`, with the bounds used by `08018698`. Total BPB sectors is consumed in `080198F0..0801992C` but is not retained as a dedicated field in this record. Derive `end = database + (n_fatent-2)*csize`; the BPB total lies in `[end-volbase, end-volbase+csize-1]`, further bounded by physical partition capacity. Do not print an invented exact total when csize > 1. {prior('phase48-current-unit-geometry','app-08019734.asm')}; {prior('phase47-filesystem-state-closure','target-address-equations.md')}.

**PROVEN:** the metadata needed is three spans: A98:8, AB0:14, AD0:24 = 46 bytes. It is not one contiguous 46-byte RAM structure. One encompassing span is `20000A98..20000AE7`, 80 bytes, including 34 unnecessary bytes. The FS header is 3C bytes followed by the 1000-byte sector window at `fs+3C`; next geometry starts at `20001AEC`. **STRONG INFERENCE:** the occupied FS extent is 103C bytes and the disk+FS extent 104C bytes; no C debug type declaration is present.

**PROVEN:** these are static application-RAM objects, initialized afresh at boot, not persistent NOR records. Geometry fields are assigned during mount, while cache flags/window/free-space state can change during operations. The mount commits type last and then ID/sync pointer. Unmount/remount or reset invalidates an old snapshot. **STRONG INFERENCE:** geometry stays stable during an ordinary mounted interval; **UNKNOWN:** atomicity of a hypothetical three-request snapshot during concurrent remount.

**PROVEN:** normal `08019A92` unregister/re-register clears the old object's type at `08019AB6`, clears a new object's type at `08019ABE`, and updates the registered pointer at `08019AC2`. Therefore a completed normal unmount does not leave a nonzero old type in the same record. The parser rejects type0. This does not eliminate a snapshot crossing the type-clear/type-commit interval or prove current device readiness. {prior('phase47-filesystem-state-closure','app-08019a92.asm')} (same byte-equal FatFs module established in Phase48).

**PROVEN:** Storage-owned content work reaches these objects through disk/file wrappers; stock initialization also invokes mounting. The RTOS/file synchronization pointer is `fs+10` (`08019A46`), intentionally omitted from the 46-byte record. **UNKNOWN:** one universally exclusive task owner across all mount/export paths, and current task/mount validity on the user's unit. Type/ID plausibility alone does not prove an ongoing mounted state without acquisition provenance.

The public reference RAM decodes as FAT16, 4096 bytes/sector, csize1, reserved1, FATcount2, FATsize4, volume0, data13, clusters2..7968, inferred exact total7980. **PROVEN for that public snapshot only**; not current-unit evidence. {local('parser-tests.json')}.
''',
'b13-readonly-interfaces.md':f'''# Phase49 — existing interface inventory

**PROVEN:** the reference manual explicitly excludes remote diagnostics from SC36.1, SC36.2, RCs and betas. `build_sc36_1.py:extra` deliberately bypasses the rdiag installer. Exact B1.3 bytes at `0801EB30` are the stock `2de9f04104000d46`, whereas SC35D8 has the diagnostic branch. The known rdiag command-2 RAM reader is absent from B1.3's installed dispatch path. {ref('tools/manual_en.py')} (line816); {ref('tools/make_manual.py')} (line927); {ref('tools/build_sc36_1.py')} (lines5,22–24); {local('b13-0801eb30.asm')}; {prior('phase48-current-unit-geometry','geometry-review.json')}.

| Candidate | Command, bounds, maximum | Geometry? | Persistent/filesystem/mode effects | Hardware evidence |
|---|---|---|---|---|
|rdiag / ctremote ARM mem|`F0 7D 43 54`, cmd2; flash08000000..0807FFFF / RAM20000000..2004FFFF; max64 bytes|Capable in diagnostic builds; **PROVEN absent at B1.3 hook**|Memory encoder + reply, no Storage/file calls in rc_mem; normal app mode|Author reports SC35D8 ping, flash read and current-pack RAM read; not B1.3 geometry |
|rdiag ping/info/file-read|cmd1/4/5; info/read use item kind/index/pack, file offset; read max64|No mounted-FS export; same absent hook|Info/read use Storage/content ops0/1/6; may touch RAM caches/mount state; not equivalent to direct RAM read|SC35D8 report only |
|Universal identity|`0801EC54`, fixed 6-byte request comparison, fixed17-byte response|No arbitrary address, no geometry|Reply through `08020C90`; no FS calls in this handler; normal app|General protocol; no new unit test here |
|Vendor42 mode/identity status|`080248F0→08024918`, sub1 returns 1 mode-derived byte via24954; identity handler2527C additionally supports sub2 returning14 identity bytes|No RAM address parameter or FS record|Query branches no FS writes observed in listing; sub0 is a mode SET with deferred callback, and identity edit commands can write NOR; do not treat whole family as read-only|No isolated B1.3 geometry hardware report |
|Vendor41 parameter/status|`080249B0→08024A10`, sub40 chooses indexed parameter table; reply3 bytes (6 nibbles) through24AB6/24AFC|Parameter-table reader, not supported arbitrary RAM access|Other subcommands emit control events/change enable flags; no geometry-export semantics established|No geometry report |
|Components content transfer|`0802503C→08039674`, file selector mapped by39570; `0803A1DC→0803CBF0`; chunks at most1000 hex bytes|Named file data/size, not RAM/BPB export|Read uses Storage and caches/transfer RAM; neighboring write path `0803A3BC→0803CC16` exists; no whole-protocol read-only assertion|Reference probe35s documents hardware file reads; no live FS geometry export |
|USB descriptor / device status|Standard descriptor/status fields, no supported ARM-address argument|No FAT geometry|Enumeration/status RAM and endpoints; no geometry command found; normal configuration has Audio/MIDI, not MSC|Prior descriptor native review; no current-unit read |
|Existing MSC READ CAPACITY / READ10 backend|57E34 reports8192 sectors×4096 regardless BPB/window; READ10 addresses blocks, not ARM RAM|Capacity cannot identify mounted geometry; VBR only if correct existing exposed window already known|Special mode; mode setter/deferred transition is not a passive geometry query; no mode change authorized or performed|Phase46 code/tests; no user-unit normal-application MSC evidence |
|Printed/debug logs / DSP diagnostics|Stock logging1B3B8; SC35 pad probes/SC35D2–D3 DSP X/Y reads|No demonstrated B1.3 ARM FS export|Debug logging transport/export incomplete; DSP memories are separate from ARM/NOR geometry|Older diagnostic reports do not prove B1.3 availability |

Exact dispatch: B1.3 `0801EB30` calls2484C, dynamic object slot0,248F0,249B0,24B6C,24C4C,24D2C, universal identity1EC54 and Components2503C. Registration is `0801EC80..ED24`. The first dynamic identity object's vtable is assigned by2524C; its handler2527C returns a fixed identity cache, not geometry. Display/control and updater branches are not fallback memory exports. {local('b13-0801eb30.asm')}; {local('b13-0802484c.asm')}; {local('b13-080251a0.asm')}; {local('b13-0802503c.asm')}; {local('b13-0803a614.asm')}.

**PROVEN:** `08024A7A` reads an indexed parameter-table word and sends only3 bytes. An indexed load is not evidence of a supported address/bounds contract for reading arbitrary ARM metadata. No out-of-range indexing, malformed packet or control bypass was attempted. **UNKNOWN:** full bounds and reachability of every computed/virtual USB callback; the saved linear disassembly may stop at literal data and is not a complete system CFG. This prevents a universal claim that no undocumented reader could exist. **STRONG INFERENCE:** no existing supported B1.3 interface in the inspected/publicly documented interfaces retrieves the required record.

Reference hardware evidence is explicitly the author's SC35D8 report dated2026-10-09, {ref('docs/NOTAS.md')} lines1424–1428, not an agent or user-unit test. rdiag ABI and bounds: {ref('tools/rdiag.py')} `HOOK`, `NMAX`, `FLASH`, `RAM`, `rc_mem`, `rc_send`; host decoder {ref('tools/ctremote.py')} `req_mem`, `dec_mem`. File API details: {ref('tools/probe35s.py')} header; native file read {local('b13-08039f00.asm')}; fixed capacity {local('b13-08057e30.asm')}; USB/callback context {prior('phase46-msd-filesystem-closure','findings.md')}.
''',
'minimum-read-plan.md':f'''# Phase49 — minimum evidence plan, no acquisition command

**UNKNOWN:** a supported existing CURRENT B1.3 interface able to export these fields. There is no executable read plan for the installed firmware qualified by this phase. Stop here; no live tool, port enumeration, packet transmitter or new diagnostic is created.

**PROVEN metadata definition:** `20000A98`8 bytes, `20000AB0`14 bytes, `20000AD0`24 bytes, concatenated in that order into46 raw little-endian bytes. {local('live-geometry-structure.md')}. One contiguous enclosing read would be80 bytes at20000A98, not46; it exceeds historical rdiag's64-byte cap. Three reads minimize disclosed bytes; two reads could cover it with extra bytes. No reason to broaden to a RAM dump.

For comparison only, **PROVEN ABI in SC35D8**, not B1.3: cmd2, request address encoded as8 high-to-low nibbles plus one length byte, padded request232 bytes; response `F0 7D 43 54 42 seq`, status8 nibbles followed by2 nibbles per byte, terminalF7. Require correct signature/command/sequence, zero status, expected decoded length, valid nibbles, coherent mount interval and unit/firmware provenance. No request bytes or acquisition script are emitted. Router08020C90; SC35D8 manifest labels c_rdin0806B9F4 / c_rdcmd0806BA9C; these are not B1.3 handler addresses. {ref('tools/rdiag.py')}; {ref('tools/ctremote.py')}; {ref('firmware/sc35d8/manifest.json')}.

**PROVEN offline parser:** {local('geometry_parser.py')} accepts an already captured compact record, not a MIDI response and not an arbitrary RAM image. Invocation: Python with `-B`, parser path, and the local46-byte record path. It prints JSON; it does not modify the input or create a binary. Authentication/acquisition provenance must accompany the record externally; a valid tuple cannot establish its own source. No current-unit file exists to parse.

Validation checks exact46-byte length, mounted FATclass, internal drive0, baseD4000, stride/sector4096, power-of-two csize1..128, FATcount1/2, clean cache/FSInfo flags, nonzero mountID policy, sufficient FAT capacity, correct FAT/root/data equations and bounded32MiB physical end with wide host arithmetic. Zero mountID is conservatively rejected as ambiguous, not proof of invalid stock state (16-bit ID can wrap). Dirty snapshots and alternate partitions are rejected under this narrow evidence contract, not declared globally invalid. Firstcluster2/last=n_fatent-1; reserved=fat-vol. Exact total is printed only when derivable; otherwise null plus possible range. A BPB total from an already available VBR/status export is required to remove that ambiguity, not to bound the normal write domains.

**PROVEN tests:** {local('parser-tests.json')} accepts public reference RAM plus all4 prior normal bounded mount tuples and rejects24 malformed/inconsistent/unsupported records. The reference yields both target ranges outside normal FAT/root/data write domains. These are offline tests, not current-unit closure or a boot-state proof.

Next options, least invasive first:

1. **UNKNOWN:** an already available public/status report from this unit that includes these scalar fields. None found in Phase48 or documented as B1.3-supported here.
2. **UNKNOWN:** host-side read-only inspection of an already acquired authentic internal-volume VBR/image plus backing/mount provenance. SD files, Components file exports and fixed MSC capacity alone do not supply this.
3. **PROVEN historical capability, UNKNOWN current availability:** the existing hardware-tested CIRCUITS-HACKS rdiag mem command could expose the record on a diagnostic image that already includes it. Current B1.3 does not. This is not a recommendation or authorization to install SC35D8.
4. **UNKNOWN / separate future decision:** only if existing evidence/readers cannot suffice, a separately reviewed temporary diagnostic would be a firmware change. None is designed, generated, selected or scheduled here.
''',
'readonly-safety.md':f'''# Phase49 — read-only safety boundary

**PROVEN READ-ONLY (offline tool):** `geometry_parser.py` imports only argparse/json/struct/pathlib, reads one explicitly supplied local file, validates bytes and prints JSON. No MIDI, USB, serial, subprocess, network, Storage, write/flush, reboot or update API exists in that tool. `test_parser.py` writes only Phase49 JSON evidence; `inspect_b13.py` reads existing image representations and writes only assembly text/JSON. No firmware is emitted.

**PROVEN READ-ONLY (reviewed diagnostic command body only):** historical `rdiag.py:rc_mem` decodes/clamps address/length, checks FLASH/RAM, calls nibble encoders c_p32/c_pbytes and branches rc_send→stock router08020C90. It does not call content API, Storage submission, file mutation/flush, NOR program/erase, SD write, update or reboot. It writes its response/request buffer and stack, so read-only means persistent/read-source safety, not zero RAM writes. Ordinary application mode suffices on a build that installs it. Hardware report for SC35D8 is corroborating evidence, not proof the command exists in B1.3. {ref('tools/rdiag.py')} `rc_mem`, `clamp_n`, `rc_send`; {ref('docs/NOTAS.md')} lines1424–1428.

**UNKNOWN (CURRENT B1.3 proposed reader):** no such supported reader has been identified; therefore none of the requested live no-write guarantees can be claimed for an acquisition plan. A code-level capability in another build is not a safe installed-interface proof. Other commands in the same diagnostic and vendor families can write files/NOR or change modes. No such command was executed.

| Required property for current acquisition | Result |
|---|---|
|No persistent write / filesystem mutation |**UNKNOWN**, no qualified acquisition path |
|No Storage write request / flush |**UNKNOWN**, no qualified acquisition path |
|No NOR program/erase / SD write |**UNKNOWN**, no qualified acquisition path |
|No update mode / reboot requirement |**UNKNOWN**, no qualified acquisition path |
|Offline Phase49 execution only |**PROVEN**, file inspection/decoding/reporting only |

**STRONG INFERENCE:** a valid mounted geometry tuple remains constant between mounts, but separate memory replies are not automatically an atomic snapshot. Current mount identity/task ownership/stability cannot be proved without an actual supported acquisition context. Parser rejection of dirty/ambiguous records reduces false acceptance; it cannot solve authenticity or a concurrent remount.

Phase48 reports/evidence and pinned reference sources are checked by {local('validate.py')}; results {local('validation.json')}. Historical firmware/candidates remain unchanged. No full storage replay is rerun, and no missing NOR/peripheral model is invented.
''',
'findings.md':f'''# Phase49 — existing current-B1.3 geometry reader

**PROVEN:** the known hardware-tested CIRCUITS-HACKS rdiag ARM memory reader is absent from the exact published B1.3 dispatch hook. Reference release documentation explicitly says betas omit it. The original B1.3 prologue and stock dispatch are present; no literal rdiag signature occurs in the image (the latter is corroboration only). {local('b13-inspection.json')}; {local('b13-readonly-interfaces.md')}.

**STRONG INFERENCE:** none of the inspected, documented existing B1.3 interfaces supplies the required mounted internal filesystem record. Identity/mode/parameter/status and Components file reads do not constitute a geometry reader. USB capacity is fixed independent of BPB/window. **UNKNOWN:** universal absence of undocumented computed/virtual reader paths. Therefore this phase cannot qualify a safe installed read plan; it does not assert a fully enumerated negative theorem.

**PROVEN:** the needed46 bytes are three metadata spans, with a proven mounted-field layout; they are not a contiguous46-byte structure. Reserved sectors and cluster bounds are derived. BPB total sectors is absent and may only be a bounded range. Exact structure/lifetime/owner limits are recorded in {local('live-geometry-structure.md')}.

**PROVEN:** an offline parser is complete. It accepted5 reference/model records and rejected24 bad/unsupported records; both target ranges lie outside normal writable domains in the reference snapshot. No result is relabeled as current-unit geometry. {local('geometry_parser.py')}; {local('parser-tests.json')}.

**UNKNOWN:** current-unit mounted geometry, coherent live status and a supported CURRENT B1.3 acquisition path. The earlier storage-preservation blocker remains. No new diagnostic, firmware, install plan, hardware access, MIDI port opening or transmission was performed. Historical Phase48/pinned-reference integrity is checked in {local('validation.json')}.

Stop at the existing-reader boundary. Ordered minimal future evidence options, without initiating any, are in {local('minimum-read-plan.md')}; safety classification is in {local('readonly-safety.md')}. Existing geometry/status evidence first; then already acquired host-readable internal-volume evidence; then availability of a historically tested diagnostic command; only last a separately authorized temporary diagnostic.

CURRENT-UNIT GEOMETRY READER = UNQUALIFIED
'''}

def main():
    for name,text in reports.items():(OUT/name).write_text(text,encoding='utf8')
    print('Wrote '+str(len(reports))+' Phase49 reports')
if __name__=='__main__':main()
