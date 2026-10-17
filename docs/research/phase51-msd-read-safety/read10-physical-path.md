> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase51 — exact physical read and statuses

**PROVEN exact image:** B1.3 SHA-256 `2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41`. All22 newly inspected path ranges match official4486. Firmware files are read only. path-inspection.json (local-only reference: `builds/phase51-msd-read-safety/path-inspection.json`; not distributed).

1. **PROVEN:** ordinary BOT-admitted READ10 opcode28 enters3B27C→3B480; big-endian CDB2..5 LBA40hex and7..8 count1; cached8192 blocks/4096 bytes; transfer direction/length checks.3B52E calls initialized table20003788+10→57E88. b13-0803b27c.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-0803b27c.asm`; not distributed).

2. **PROVEN:**57E88 clears4096 bytes at transfer buffer40024000, drains NOR queue via23FD6, selects base `[ [200037C0] ]`=94000 in mode1 and computes94000+(40<<12)=D4000.57ECC calls wrapper24130 with buffer40024000,length1000hex. b13-08057e30.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08057e30.asm`; not distributed).

3. **PROVEN:**24130 builds24-byte op1 descriptor,23F68 queues it;23FD6 waits. Storage24014 pops op1→2408A→backend22F94. Backend checks start against capacity and byte semaphore; normal path calls37430; worker240C4 saves status to wrapper+18; wrapper24160 returns that byte. b13-08024130.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08024130.asm`; not distributed); b13-08023f68.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08023f68.asm`; not distributed); b13-08022f94.asm (local-only reference: `builds/phase51-msd-read-safety/b13-08022f94.asm`; not distributed).

4. **PROVEN:**37430 prepares DMA at1C072, issues NOR command3769C→22746, waits37596, disables QSPI DMA request afterward. Common read opcodeEC and IRQ/wait model are already audited in Phase31; no read-side program/erase path is introduced. b13-08037430.asm (local-only reference: `builds/phase51-msd-read-safety/b13-08037430.asm`; not distributed); b13-08037596.asm (local-only reference: `builds/phase51-msd-read-safety/b13-08037596.asm`; not distributed); [findings.md](<../phase31-storage-error-recovery/findings.md>).

5. **PROVEN:**57ECE ignores wrapper status, optionally substitutes serial marker text in response RAM, then returns0 at57EEE. SCSI3B530 sees success and sends4096 bytes on endpoint82 through24754. Native BOT status26DB0→26EAE sends13-byte CSW with status0 and zero residue in every new completed case, including native failures1/2. read-cases.json (local-only reference: `builds/phase51-msd-read-safety/read-cases.json`; not distributed).

The coupled runner executes wrapper, enqueue, worker, actual backend bounds/semaphore path, response clear/filter, SCSI data and CSW. Queue byte movement and task wake/yield are modeled; CPU contexts switch outside emulator hooks. Physical37430 DMA completion/bytes and USB TX/RX are seams. Runtime fixture construction explicitly applies native constructor values: backend vtable805B1AC, capacity02000000 and wrapper pending/capacity0/1. This is not claimed to be a cold boot or a physical read. [read_cases.py](<../../../builds/phase51-msd-read-safety/read_cases.py>).

**PROVEN:** the mode1 physical equation is unchanged. **UNKNOWN:** actual current mode, physical completion or mounted/cache state from the user's unit; none was acquired. The inspected buffer is a fixed memory-mapped4KiB region, not a newly allocated512-byte heap object. Its memory address is proven; no claim about retention across power loss is needed.
