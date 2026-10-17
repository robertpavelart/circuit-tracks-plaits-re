> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase46 — address and integer bounds

**PROVEN:** native arithmetic is32-bit; several layers lack a physical range guard. **UNKNOWN:** a resulting overwrite in this unit's boot-to-capture sequence. A theoretical or synthetic wrapped destination is not silently classified as an ordinary-boot writer.

| Layer | Arithmetic and predicate | Result |
|---|---|---|
| File length | `08019E82–08019E90` detects file-position+requested-bytes overflow and shortens request | Protects file length; does not bound physical sector address. |
| Cluster | `08018698`: unsigned subtract2 and compare against n_fatent-2; MLA of cluster index, sectors/cluster and database | Rejects invalid clusters relative to the BPB; trusted oversized BPB can still admit physically invalid LBAs. |
| FAT geometry | BPB arithmetic in`080198C4`, `08019914–60`: FATs*fatsize, reserved+rootdir+FAT sectors, volume-relative cluster count, addition of volume start |32-bit multiply/add, no carry rejection at these instructions; mount internal-consistency checks are not equivalent to device-capacity checks. MBR start and totals come from disk. |
| Disk map | `0801AF30` MLA and`0801AF34` MUL |`a=(D4000+(LBA<<12)) & FFFFFFFF`; `n=(count<<12) & FFFFFFFF`. No LBA/count/last-sector test here. High LBA bits above bit19 are lost. Count`100000` wraps byte length to0. What a zero-length downstream request does is not used as a preservation guarantee. |
| NOR backend | Phase45 native mapper review forwards WRITE+erase-first to wrapper24164 | A wrapped valid low address is not rejected merely because the pre-wrap LBA was too large. Sector erase can destroy bytes outside the23/512-byte payload even if a shorter program follows. |
| SCSI WRITE(10) initial state | `0803B5AA` protection first, then32-bit LBA +16-bit count compared unsigned with8192 | All18 actual initialized cases rejected by protection. If this gate were bypassed, carry from addition is not tested. No claim that malformed accepted BOT can bypass it. |
| SCSI chunk | `0803B600–08` multiplies LBA/count by block size, then transfer slices to<=4096 and divides by4096 | Nominal one4096-byte block per backend callback; direct callback count>1 is outside that nominal chunk contract. State-continuation/CBW invariants still need a complete malformed-stream proof. |
| Lower MSD callback | `08057F0E` unsigned block<8192; address base+(block<<12), right/left shifts round down to4096 | No selected-end or full-transfer range check; numeric arithmetic for accepted block alone is small enough not to32-bit-wrap. Default/window addresses can nevertheless exceed nominal NOR capacity. |

For well-bounded drive0 writes, `0 <= LBA < 1F2C`, `1 <= count <= 1F2C-LBA`, sector4096 guarantee `[D4000,2000000)` with no wrap. Last permitted single-sector LBA`1F2B` starts`1FFF000`; last valid extent ends exactly`2000000` (half-open). LBA`1F2C` is one past the partition and must not be accepted. The mapper does not enforce that distinction.

Critical examples:

```
(D4000 + FFFAD * 1000) mod 2^32 = 81000
(D4000 + FFFAE * 1000) mod 2^32 = 82000
```

**PROVEN:** Phase46 native mount + cluster + f_write tests accept the corresponding synthetic oversized volume/constructed FIL states. [native_cases.py:fat_mount](<../../../builds/phase46-msd-filesystem-closure/native_cases.py>) and native-cases.json (local-only reference: `builds/phase46-msd-filesystem-closure/native-cases.json`; not distributed); lower mapper submissions were already persisted in Phase45 mapped-write-review.json (local-only reference: `builds/phase45-nor-mutation-closure/mapped-write-review.json`; not distributed). **UNKNOWN:** native directory lookup and an automatic startup producer can form those FIL states from this unit's actual media. They were not passed off as authentic NOR bytes.

The USB lower callback's mode3 can address both evidence sectors directly. Mode1's accepted blocks cover numeric `94000,2094000)` for count1; mode2 `[D4000,20D4000)`; mode3 `[0,2000000)`. These are numeric callback extents, not proof that hardware wraps or that advertised write-protected MSD writes them. Advertised32MiB capacity ignores selected partition base. Actual NOR out-of-array response remains **UNKNOWN**.

Listings: [mount (local-only reference: `builds/phase46-msd-filesystem-closure/app-080197a0.asm`; not distributed), mapper (local-only reference: `builds/phase46-msd-filesystem-closure/app-0801ae00.asm`; not distributed), SCSI (local-only reference: `builds/phase46-msd-filesystem-closure/app-0803b27c.asm`; not distributed), callbacks (local-only reference: `builds/phase46-msd-filesystem-closure/app-08057e30.asm`; not distributed).
