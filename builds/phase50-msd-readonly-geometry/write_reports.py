"""Write Phase50 documentation only."""
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
REF=Path(r'C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main')
def link(p):return f'[{p.name}](<{p.as_posix()}>)'
def here(n):return link(OUT/n)
def old(n,p='phase46-msd-filesystem-closure'):return link(ROOT/'builds'/p/n)
reports={
'msd-backing-store.md':f'''# Phase50 — exact B1.3 MSD backing

**PROVEN:** the inspected published B1.3 application is435220 bytes, SHA-256 `2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41`. Its initialized backend table and selected-window pointer are decoded from existing bytes. All examined MSD/SCSI/storage/mode ranges match official4486. The Advanced Setup range4709A differs because B1.3 patches the separate button24 branch; the button9 bit17 branch47070..47098 is intact. No image is built/emitted. {here('b13-inspection.json')}; {here('b13-08047016.asm')}; {here('b13-0804709a.asm')}.

**PROVEN:** RAM200037AC points to table20003788. Callbacks (Thumb pointers) are init8057E31, capacity8057E35, ready8057E45, writeprotect8057E49, read8057E89, write8057EF5, maxLUN8057FB1, eject8057FB5, inquiry805B6B8. This is a raw NOR wrapper, **not the SD drive and not a FatFs file object**. Read loads `[20006968]` and calls its vtable+C, wrapper08024130; write calls vtable+10,08024164. {here('b13-08057e30.asm')}; {old('callback-table.json')}; {old('filesystem-lba-binding.md')}.

| Property | Exact code result |
|---|---|
|Logical unit |Max-LUN callback returns0: intended sole LUN0; no advertised SD LUN |
|Interface |Stock MSD class200000F8; class descriptor805B3D8, interface2, class08/subclass06/protocol50, endpoints82 IN /02 OUT,64-byte max packets |
|Capacity |Always8192 blocks of4096 =32MiB; independent of selected base/end |
|Default initialized mode |Internal1, window record8038C3C = base94000,endD3FFF |
|Internal2 |Record8038C4C = baseD4000,end1FFFFFF |
|Internal3 |Record8038C44 = base0,end1FFFFFF |
|Physical medium |ARM external serial NOR via global20006968; independent of DSP external SDRAM and SD |
|Read |NOR address = selected base +4096×USB LBA; length4096×callback count |
|Write |Lower callback can read/compare/erase-first program; normal WRITE10 is blocked by constant protection1 |

**PROVEN:** the read callback does not enforce the window record's end. Even internal1 can read LBA64 (`94000 +40*1000 = D4000`), within its advertised8192-block limit and the real32MiB physical range. Native SCSI→callback tests observed exactly this wrapper submission. Thus the nominal94000..D3FFF descriptor must not be mistaken for the actual read admission bound. {here('native-reads.json')}.

Answer: **PROVEN same physical NOR backend; PROVEN addressable same disk0 volume baseD4000**, by mode1 LBA64, internal2 LBA0 or internal3 LBAD4. **UNKNOWN:** the currently selected mode and active USB configuration on the user's unit. LUN0 LBA0 is not invariably that filesystem: in ordinary mode1 it is the different94000 region. **STRONG INFERENCE:** a coherent BPB acquired with established mode1 binding reconstructs the geometry used by stock mount. It still does not reveal RAM mount/cache/dirty state.

**PROVEN caveat:** USB class GET_MAX_LUN handler58ECC calls the max-LUN callback, then its zero result branches at58F08 to the error/stall path. The callback's intended LUN0 result is not proof a successful one-byte control reply is produced. **UNKNOWN:** actual Windows enumeration/fallback behavior for this exact composite mode. {here('b13-08058eb0.asm')}. No hardware-tested B1.3 raw-MSD geometry capture was found; older SC35D8 rdiag reports are not MSD evidence.
''',
'scsi-read-path.md':f'''# Phase50 — normal SCSI reads

**PROVEN:** dispatcher0803B27C selects opcode00 TUR,12 INQUIRY,25 READ CAPACITY10,28 READ10,2A WRITE10 (also03 sense,1A/5A modesense,23 formatcapacity,1B/1E start/stop handling,2F verify). Scope here is ordinary LUN0 reads, not malformed BOT inputs. {here('b13-0803b27c.asm')}; {old('app-08026db0.asm')}.

| Command | Native path and effect |
|---|---|
|TEST UNIT READY00 |3B2C8 requires zero transfer length, then table+8→57E44 returns0; status/sense RAM only |
|INQUIRY12 |3B356; standard path table+20→805B6B8,36 bytes, bounded by allocation length; vendor `Novation`, product `Circuit`, revision `1.00`; no media read |
|READ CAPACITY25 |3B434→table+4→57E34 stores4096/8192 in SCSI geometry cache2000689C/A0; response `00001fff00001000` = last8191,size4096; no media read |
|READ1028 |3B480→ready; CDB bytes2..5 big-endian LBA, bytes7..8 big-endian count; saved in200068A4/A8; LBA+count compared against cached blockcount at3B4D2..D6; transfer byte count checked against CBW length3B4F6; slice<=4096 bytes;3B52E calls table+10→57E88;3B54E transmits on82 |

**PROVEN bounds:** wire count16-bit; ordinary admitted requests satisfy LBA+count<=8192, so maximum nominal request8192 blocks=33554432 bytes at LBA0, delivered in4096-byte callbacks, one block each. Count and start must also remain inside the physical array after base addition; the stock lower callback checks start<8192 only, not selected end or start+count. Use count1 for evidence. No new oversized/overflow/malformed cases were run. READ CAPACITY must establish the geometry cache before READ10. {here('b13-0803b27c.asm')}; {here('b13-08057e30.asm')}.

**PROVEN physical read sequence:**57E88 zeroes response memory, calls wrapper vtable+1C (`08023FD6` queue drain), then vtable+C (`08024130`) with selected-base+(LBA<<12),buffer,count<<12. Wrapper24130 submits op1 through23F68, waits again via+1C; worker2408A→backend read22F94. It does not submit write op2, erase op3, flush op4, or call a FatFs flush. **PROVEN READ-ONLY for this command's own submission graph**, not for unrelated queued work. {here('b13-08024130.asm')}; {here('b13-08023f68.asm')}; {old('app-08022f5e.asm')}.

**PROVEN returned bytes are not universally raw:**57EE6 uses57E4C to search for ASCII `<SERIALUPN123>`;57EDC substitutes14 identity-cache bytes with1D8AC. This mutates the response RAM, not NOR. The tested BPBs contain no marker and were returned unchanged. Do not certify a full exported sector hash as a raw-NOR hash without considering this filter. The parser uses only BPB fields, not arbitrary boot code/text. {here('b13-inspection.json')}; {here('b13-08057e30.asm')}.

**PROVEN error limitation:**57ECC does not test wrapper24130's result before filtering and57EEE returns0. Thus SCSI callback success alone is insufficient proof of a fault-free NOR transfer. Queue waits have no bounded recovery here. **UNKNOWN:** exact error propagation under physical TEF/missing completion in this MSD path. Earlier one-shot/quarantine conclusions are not superseded by a generic SCSI success. {old('findings.md','phase31-storage-error-recovery')}.

New tests: TUR, INQUIRY, CAPACITY plus4 single-block READ10 cases across three internal modes; no persistent/FS flush functions reached in these slices. Queue waits, NOR wrapper reads and USB TX are explicit model seams; no USB endpoint/DMA or physical NOR was exercised. {here('native_reads.py')}; {here('native-reads.json')}.
''',
'minimum-sector-plan.md':f'''# Phase50 — minimum sectors and conditional host plan

**PROVEN geometry payload:** no FAT chains, files, identity region or coefficient region is needed. For an ordinary superfloppy FAT volume, one4096-byte sector at internal disk0 LBA0 suffices. If it is an MBR, add only the primary candidate VBR sector(s) in the order the stock mount probes them; normally2 sectors total, worst root+4 candidates=5 sectors/20480 bytes. No extended/GPT traversal is implemented by this stock mount path. {old('app-08019734.asm','phase48-current-unit-geometry')}.

| BPB offset (hex) | Field |
|---|---|
|0B u16 |bytes/sector, must4096 |
|0D u8 |sectors/cluster, power2 in1..128 |
|0E u16 |reserved sectors |
|10 u8 |FAT count1/2 |
|11 u16 |root entry count |
|13 u16,20 u32 |total sectors: use16 if nonzero else32 |
|16 u16,24 u32 |FAT size: use16 if nonzero else32 |
|2A u16 /2C u32 (FAT32) |version/root cluster |
|1FE |55AA boot signature, even on4096-byte sectors |

Stock recognizer additionally checks first byteE8/E9/EB and `FAT` at36hex or `FAT32` at52hex. Do not infer FATclass from its text label. For MBR, four16-byte entries at1BEhex: startLBA atentry+8 and extent at+C. Mount uses starts, not BPB hidden-sectors28hex, to establish volbase. Decoder imposes normal physical partition bounds in addition to native mount constraints.

Let `rootS=rootEntries*32/bps`; `overhead=reserved+nFAT*FATsize+rootS`; `N=floor((total-overhead)/spc)`. Stock class is FAT12 ifN<FF6, FAT16 ifN<FFF6, otherwise FAT32 ifN<0FFFFFF6. FATbase=vol+reserved; fixedroot=FATbase+nFAT*FATsize; data=vol+overhead; validclusters2..N+1. This internal32MiB/4096-byte backing cannot normally fit enough clusters for FAT32. Bounds/FATcapacity are checked, not assumed. {here('geometry_from_sector.py')}; {here('geometry-tests.json')}.

**UNKNOWN full-session qualification: this is an offline conditional plan, not instructions to execute now.** Prerequisites: independently establish exact B1.3, stable internal mode1, LUN0 raw-block binding, a quiescent/no-unrelated-save interval, and host raw access without automount/repair or unsolicited mode/update traffic. The current state has not been queried. Do not toggle a persistent UI setting to satisfy this plan.

If those prerequisites are qualified separately, use the OS's existing read-only raw block/SCSI interface for the identified device; no drive number is guessed and no executable acquisition script is supplied. Expected inquiry `Novation`/`Circuit`/`1.00`, LUN0, capacity8192×4096; those alone are not a unit identity or base-window proof. In stable mode1, read ONLY:

1. USB LBA64 (`40` hex), count1,4096 bytes; save `msd_mode1_lun0_lba00000040.bin` atomically after exact-length successful transfer.
2. If and only if it is MBR, read USB LBA64+partition-start, count1,4096 bytes for the next needed primary candidate; stop at first stock-recognized VBR. Save each with its exact eight-digit USB LBA.
3. Save a host provenance manifest: unit/firmware, selected-mode evidence, backing relation, timestamps, command/OS status, LBA/count/length and SHA-256 of each complete returned sector. Hashes authenticate saved returned bytes, not unfiltered physical NOR or live RAM status. Reject failures/partial output and do not auto-retry a stalled Storage operation.

No volume/filesystem mount, directory listing, FAT read, read of81000/82000, save, flush, eject, reboot or firmware update belongs in this plan. Windows raw-device availability, permissions and preventing automount are **UNKNOWN** on this unit; no OS/device enumeration was performed. READ CAPACITY/TUR/INQUIRY add only their scalar replies, not unrelated sectors. Do not scan other bases in lieu of establishing mode.

Decoder accepts local files only: repeated `--sector USB_LBA=FILE`. It reuses Phase49 invariants without editing Phase49. Exact BPB total is now available; RAM mount/cache status is still **UNKNOWN**. Native B1.3 mount and parser agree on4 bounded superfloppies and1 primary-MBR layout;15 invalid/incomplete/binding cases are rejected. No generated test BPB is presented as actual-unit data. {here('test_geometry.py')}; {here('geometry-tests.json')}.
''',
'physical-binding.md':f'''# Phase50 — physical binding, not FAT resemblance

**PROVEN code equation:** USB LUN0→SCSI3B52E→initialized callback57E88→`[20006968]` raw NOR wrapper24130→op1/worker2408A→backend22F94. The callback reads base from `[200037C0]`; internal mode1 selects record8038C3C/base94000. It passes `address=base+(USB_LBA<<12)`, not a disk-file offset. {here('b13-08057e30.asm')}; {here('b13-08024130.asm')}; {here('b13-08023f68.asm')}; {old('filesystem-lba-binding.md')}.

**PROVEN independent application binding:**20000A98 holds internal disk0 baseD4000,stride1000;20000AA0 is disk0,FS20000AB0. Application filesystem mapper1AF1E uses `D4000+1000*disk_LBA`. Thus, in stable mode1, `USB_LBA=40hex+disk_LBA` gives exactly the same physical NOR address. This is established by native address arguments and unchanged initialized objects, not sector contents. {old('live-geometry-structure.md','phase49-existing-geometry-reader')}; {here('native-reads.json')}.

**PROVEN narrow native checks:** mode1 LBA0→94000; mode1 LBA40→D4000; internal2 LBA0→D4000; internal3 LBAD4→D4000. Synthetic response bytes were injected at the wrapper seam. These results prove address calculation/selection; they do not prove an acquired sector's source or current mode. Capacity and inquiry are identical across windows and cannot establish the selected base. A FAT-looking sector alone is insufficient.

For a mounted volume starting at disk LBA V, first VBR is USB LBA40+V, FAT is40+V+reserved, data is40+V+reserved+nFAT*fatsz+rootS. Valid file mappings are `NOR=D4000+1000*(database+(cluster-2)*spc+sectorWithinCluster)`; both FAT copies and root/FSInfo domains must also be bounded. The decoder uses wide arithmetic and rejects a volume outside disk0's normal7980 sectors to prevent treating wrapped mappings as normal.

**PROVEN normal target relation:**81000−D4000 =−53000, or disk LBA−53hex;82000−D4000 =−52000, disk LBA−52hex. These are below any normal bounded internal volume mapping. In mode1 they would be negative USB LBAs−13hex/−12hex. No such read is requested. A validated BPB closes the geometry equations for those normal write domains; it does not independently close unrelated raw writers, dirty RAM lifetime, or current-unit acquisition provenance. {old('target-address-equations.md','phase47-filesystem-state-closure')}; {here('geometry-tests.json')}.

**UNKNOWN:** a physical binding record from an actual capture. The parser requires the external contract of verified mode1 and does not invent one from BPB text. Its adapter supplies synthetic clean header constants only to reuse Phase49 arithmetic checks, explicitly removes mount/status outputs, and labels live mount status UNKNOWN. It never calls those constants captured RAM.
''',
'readonly-safety.md':f'''# Phase50 — read-only safety and limits

**PROVEN READ-ONLY, command producer scope:** ordinary READ10 submits only raw read op1. TUR/INQUIRY/CAPACITY mutate only response/protocol RAM. No filesystem write, settings save, FatFs metadata flush, NOR program/erase, SD write, update state or reset is called by the reviewed read-command bodies. Native slices guard write/erase/content/FS flush entry points and observe zero calls. {here('native_reads.py')}; {here('native-reads.json')}; {here('scsi-read-path.md')}.

**PROVEN important distinction:** backend57EB2 and wrapper2415E invoke queue-drain23FD6. That sets RAM wait bit, wakes worker, yields until clear; it does not enqueue op4 or call FatFs sync1859A/18612. Nevertheless worker24014 can drain pre-existing writes/erases queued by other producers. Therefore 'no write requested by this host command' is proven; 'zero NOR writes occur during the whole session' is **UNKNOWN** without queue/background context. No forced release, cleanup or retry is proposed. {here('b13-08023f68.asm')}.

| Requirement | Result |
|---|---|
|Zero NOR program/erase, FS writes, settings saves, metadata flush caused by READ10 itself |**PROVEN** for reviewed submission graph and tested native slices |
|Zero unrelated queued/background mutation during read |**UNKNOWN**, barrier may run existing work; not measured on unit |
|No firmware update state |**PROVEN** for read handler and isolated mode42 sub0 body; complete upstream dispatcher/session effects not replayed |
|No reboot |**PROVEN** no MCU reset call in read/isolated mode transition; USB class rebuild can disconnect/re-enumerate |
|Mode entry without saving settings |**PROVEN** isolated vendor42 transient route uses mode RAM/timer/USB registration, with zero persistence calls in tested slice; UI bit17 route is a settings mutation |
|Complete entry/USB-driver/host no-persistence qualification |**UNKNOWN**; USB driver callbacks and host behavior are not a coupled replay |
|Read error cannot look successful |**UNKNOWN** at physical-fault level; read callback ignores wrapper return and returns0 |

**STRONG INFERENCE:** with an already established stable mode1, idle work queue and ordinary successful NOR/USB operation, one read of USB LBA40 returns enough BPB bytes without persistent changes. **UNKNOWN:** complete current-unit execution meeting those prerequisites. Overall proposed acquisition session remains **UNKNOWN**, so final path admission is UNQUALIFIED rather than an inferred PASS.

Earlier Phase31 TEF/missing-completion failures and Phase32 no-retry containment are not invalidated. The new SCSI wrapper is not a newly proven error-unwind mechanism. **PROVEN** it cannot be labeled a replacement for the one-shot policy merely because normal SCSI callbacks returned0. {old('findings.md','phase31-storage-error-recovery')}; {old('findings.md','phase32-host-containment')}.

**PROVEN offline-only scope:** scripts read authenticated existing code, emulate slices, decode synthetic ordinary sectors and write only local Phase50 text/JSON. Decoder imports argparse/sys/struct/json/hashlib/pathlib plus Phase49 pure decoder; it reads local files only. No hardware/port inventory, MIDI/USB access, firmware build/modification or transmission occurred. Prior Phase49 evidence and439 pinned reference sources are verified unchanged by {here('validation.json')}.
''',
'mode-entry.md':f'''# Phase50 — mode entry is not a filesystem read

**PROVEN startup route:**29DDC constructs a setting observer,29E30 reads setting record2 bit17 and calls38C54 with packed101hex (MIDI+MSD1) or1 (MIDI only). Initialized mode1 is not proof the user's active setting enables MSD. Bit17 is called 'probably Easy Start' in reference notes, not conclusively named by code. {here('b13-08029ddc.asm')}; {link(REF/'docs/NOTAS.md')} lines86,1014.

**PROVEN UI code:** Setup object advanced flag+24 !=0, method47016, button ID9→47070 toggles setting record2 bit17 then commits353C0 via470C8/470EA. Other advanced IDs15/24 are different functions; B1.3's patched button24 branch must not be conflated with button9. **UNKNOWN:** fully authenticated physical-button label and gesture entering this advanced view from the current unit. No user action is prescribed. This UI toggle is not a read-only acquisition step: the registered changed-settings subscriber2D278→2D300→2D2AC can request128-byte settings write3C920 and flush. {here('b13-08047016.asm')}; {here('b13-0804709a.asm')}; {old('app-08035398.asm')}; {old('persistence-routes.md')}.

**PROVEN existing transient control route:** vendor prefix checked by248F0, command byte5=42hex, subcommand byte6=0, requested mode byte7.24918/2492E calls38C10 and248CE schedules248B5 after150 timer ticks (not asserted milliseconds). Timer callback248B4 builds config with MIDI byte1 and stored mode, then38C54 rebuilds classes. This is stock code present in B1.3, not rdiag or firmware installation. No packet/transmitter is generated and none is sent. {here('b13-080248b4.asm')}.

| Requested mode / config MSD byte | Immediate internal selection | After deferred callback | Final base |
|---|---|---|---|
|0|0 (disabled)|0, MIDI only|old pointer irrelevant |
|1|1|1, MIDI+MSD|94000 |
|2|2 (D4000)|3, MIDI+MSD|0 |
|3|3 (0)|2, MIDI+MSD|D4000 |

**PROVEN:**38C54 maps config2→internal3 and config3→internal2. These numbers cannot be interchanged in read-address calculations. Mode1 is stable under this remap and is the only mode in the decoder/conditional plan. START STOP/eject can schedule the same reapplication; exclude eject from a stable acquisition interval. {here('b13-08038c10.asm')}; {here('native-reads.json')}; {old('msd-reachability.md')}.

**PROVEN native slice:** real vendor248F0 parser→setter→timer scheduling, then real248B4 callback→38C54→class clear/register/descriptor build were executed for modes0..3. Low-level USB driver reset/config/start/endpoint-close calls are seams; no Storage/persistence calls observed. Mode1 registers200000EC MIDI and200000F8 MSD together, so they are not mutually exclusive. Mode change reconfigures USB; no MCU reboot is requested. {here('native_reads.py')}; {here('b13-08036374.asm')}; {here('b13-08036460.asm')}.

**PROVEN in inspected bodies:** no mount19A92/unmount1AE1C, settings save, FS flush or NOR write is directly called by transient42/38C54. **UNKNOWN:** complete upstream dispatcher and USB-driver callback closure and pre-existing background/queued work during the transition. The model does not prove the entire live mode-entry session has no persistence. This is the remaining mode-entry gate; an untested driver seam is not a hardware-tested no-write result.
''',
'findings.md':f'''# Phase50 — MSD read-only geometry feasibility

**PROVEN:** existing exact B1.3 contains a USB/SCSI NOR read path capable of reaching the required filesystem's physical backing, without diagnostic firmware. In stable internal mode1, USB LBA40hex (64), count1,4096 bytes maps to NOR D4000, the same base used by disk0/FatFs. Its declared window endD3FFF is not enforced by READ10/backend; fixed capacity is8192×4096. This corrects the assumption that ordinary MSD necessarily exposes only the unrelated94000 window. {here('msd-backing-store.md')}; {here('physical-binding.md')}.

**PROVEN:** seven normal SCSI slices (TUR, INQUIRY, CAPACITY, fourREAD10 mappings) pass with zero guarded persistence/FS-flush calls; four existing vendor-mode/deferred class-rebuild slices pass. Queue, NOR and USB-driver/transport seams are explicit. **PROVEN:** offline sector decoder matches native B1.3 mount for four normal superfloppies and one MBR volume;15 rejected cases cover invalid/incomplete/binding data. No current-unit sectors were acquired. {here('native-reads.json')}; {here('geometry-tests.json')}.

**PROVEN READ-ONLY:** the read command's own producer graph submits raw read op1, not a write/erase/FatFs flush; no settings/update/reset call is in the reviewed read body. **STRONG INFERENCE:** an established stable mode1, idle queue and successful physical read could retrieve the one/two required sectors using standard raw block access. {here('scsi-read-path.md')}; {here('minimum-sector-plan.md')}.

**UNKNOWN — final admission remains open:** complete transient entry/USB-driver no-persistence closure, current selected mode/host raw-device binding without automount, and physical read failure/completion propagation. Backend read drains an existing queue and discards the NOR-wrapper result before returning0. UI bit17 enablement can save settings, so it is not an acceptable assumed read-only entry. BPB bytes also do not directly export live mount/cache status. These are specific limitations, not proof the existing path cannot work. {here('mode-entry.md')}; {here('readonly-safety.md')}.

The minimal **conditional** plan is LUN0, fixed mode1, READ10 LBA64 count1; only if MBR, the selected primary VBR candidate(s). No unrelated files/FAT chains/target payloads, new firmware, hardware action, port opening or transmission. The parser and full field derivation are ready in {here('geometry_from_sector.py')}.

Smallest next offline experiment: close the existing vendor42 mode1 entry through full upstream dispatcher plus real USB-class/driver callbacks with write/erase/settings/flush traps; then couple the existing read wrapper/worker error outcomes to SCSI completion without replacing those boundaries with success. No new firmware or hardware is required for that experiment. Do not repeat the completed geometry/mapping investigation.

Least-invasive evidence options remain: existing actual-unit geometry/status or previously acquired relevant raw sectors; existing stock MSD route after its admission gaps are closed; historically tested rdiag only if independently already installed (B1.3 omits it); only last a separately authorized temporary diagnostic. None is initiated here. Current-unit geometry and candidate admission remain unchanged. Prior49 and pinned reference integrity checks: {here('validation.json')}.

MSD READ-ONLY GEOMETRY PATH = UNQUALIFIED
'''}
def main():
    for name,text in reports.items():(OUT/name).write_text(text,encoding='utf8')
    print(f'Wrote {len(reports)} Phase50 reports')
if __name__=='__main__':main()
