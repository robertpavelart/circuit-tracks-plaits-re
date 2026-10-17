> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase50 — normal SCSI reads

**PROVEN:** dispatcher0803B27C selects opcode00 TUR,12 INQUIRY,25 READ CAPACITY10,28 READ10,2A WRITE10 (also03 sense,1A/5A modesense,23 formatcapacity,1B/1E start/stop handling,2F verify). Scope here is ordinary LUN0 reads, not malformed BOT inputs. b13-0803b27c.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-0803b27c.asm`; not distributed); app-08026db0.asm (local-only reference: `builds/phase46-msd-filesystem-closure/app-08026db0.asm`; not distributed).

| Command | Native path and effect |

|---|---|

|TEST UNIT READY00 |3B2C8 requires zero transfer length, then table+8→57E44 returns0; status/sense RAM only |

|INQUIRY12 |3B356; standard path table+20→805B6B8,36 bytes, bounded by allocation length; vendor `Novation`, product `Circuit`, revision `1.00`; no media read |

|READ CAPACITY25 |3B434→table+4→57E34 stores4096/8192 in SCSI geometry cache2000689C/A0; response `00001fff00001000` = last8191,size4096; no media read |

|READ1028 |3B480→ready; CDB bytes2..5 big-endian LBA, bytes7..8 big-endian count; saved in200068A4/A8; LBA+count compared against cached blockcount at3B4D2..D6; transfer byte count checked against CBW length3B4F6; slice<=4096 bytes;3B52E calls table+10→57E88;3B54E transmits on82 |

**PROVEN bounds:** wire count16-bit; ordinary admitted requests satisfy LBA+count<=8192, so maximum nominal request8192 blocks=33554432 bytes at LBA0, delivered in4096-byte callbacks, one block each. Count and start must also remain inside the physical array after base addition; the stock lower callback checks start<8192 only, not selected end or start+count. Use count1 for evidence. No new oversized/overflow/malformed cases were run. READ CAPACITY must establish the geometry cache before READ10. b13-0803b27c.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-0803b27c.asm`; not distributed); b13-08057e30.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08057e30.asm`; not distributed).

**PROVEN physical read sequence:**57E88 zeroes response memory, calls wrapper vtable+1C (`08023FD6` queue drain), then vtable+C (`08024130`) with selected-base+(LBA<<12),buffer,count<<12. Wrapper24130 submits op1 through23F68, waits again via+1C; worker2408A→backend read22F94. It does not submit write op2, erase op3, flush op4, or call a FatFs flush. **PROVEN READ-ONLY for this command's own submission graph**, not for unrelated queued work. b13-08024130.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08024130.asm`; not distributed); b13-08023f68.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08023f68.asm`; not distributed); app-08022f5e.asm (local-only reference: `builds/phase46-msd-filesystem-closure/app-08022f5e.asm`; not distributed).

**PROVEN returned bytes are not universally raw:**57EE6 uses57E4C to search for ASCII `<SERIALUPN123>`;57EDC substitutes14 identity-cache bytes with1D8AC. This mutates the response RAM, not NOR. The tested BPBs contain no marker and were returned unchanged. Do not certify a full exported sector hash as a raw-NOR hash without considering this filter. The parser uses only BPB fields, not arbitrary boot code/text. b13-inspection.json (local-only reference: `builds/phase50-msd-readonly-geometry/b13-inspection.json`; not distributed); b13-08057e30.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08057e30.asm`; not distributed).

**PROVEN error limitation:**57ECC does not test wrapper24130's result before filtering and57EEE returns0. Thus SCSI callback success alone is insufficient proof of a fault-free NOR transfer. Queue waits have no bounded recovery here. **UNKNOWN:** exact error propagation under physical TEF/missing completion in this MSD path. Earlier one-shot/quarantine conclusions are not superseded by a generic SCSI success. [findings.md](<../phase31-storage-error-recovery/findings.md>).

New tests: TUR, INQUIRY, CAPACITY plus4 single-block READ10 cases across three internal modes; no persistent/FS flush functions reached in these slices. Queue waits, NOR wrapper reads and USB TX are explicit model seams; no USB endpoint/DMA or physical NOR was exercised. [native_reads.py](<../../../builds/phase50-msd-readonly-geometry/native_reads.py>); native-reads.json (local-only reference: `builds/phase50-msd-readonly-geometry/native-reads.json`; not distributed).
