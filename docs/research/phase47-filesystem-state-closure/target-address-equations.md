> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase47 — fixed-target equations

**PROVEN:** both targets are outside the reconstructed normal writable filesystem range. Byte offsets throughout this note are external NOR offsets, not CPU pointers or DSP addresses.

For normal geometry:

```
P(L) = D4000 + 1000*L
L(C,k) = D + (C-2) + k, k=0 (one sector/cluster)
0 <= L <= 1F2B; 2 <= C <= 1F20
```

The native mapper's32-bit form reduces LBA modulo100000 before its12-bit shift. The following equations describe why the earlier values do not fit normal bounds; they are not requests to test invalid inputs.

| Quantity |81000..81016 |82000..821FF |
|---|---|---|
|Physical sector |`81000,82000)` |`[82000,83000)` |
|Signed sector relative to D4000 |−53 (−83 decimal) |−52 (−82 decimal) |
|Least unsigned LBA satisfying wrapped equation |FFFAD |FFFAE |
|Required cluster with **normal** data startD |FFFA2 |FFFA3 |
|Offset within that cluster |0 for target start |0 for target start |
|If file were contiguous from cluster2: chain index |FFFA0 |FFFA1 |
|Corresponding file offset in that hypothetical chain |FFFA0000 |FFFA1000 |
|Normal maximum LBA / cluster |1F2B /1F20 |1F2B /1F20 |
|Normal filesystem classification |outside normal writable filesystem range |outside normal writable filesystem range |

A file could otherwise start at any allocated valid cluster, so a target-reaching chain position is not unique without its real chain. Starting directly at either required invalid cluster would be chain index0/offset0, which is still outside valid allocation. For comparison, Phase46's **different** data start1001 required FEFAE/FEFAF; do not reuse those cluster numbers for the normal FAT16 geometry.

FAT writes are in LBAs1..8; fixed root writes9..C; subdirectory/data writesD..1F2B. None can meet either target equation. Valid final data sector1F2B maps`[1FFF000,2000000)`. Whole-sector erase-before-program stays inside each aligned sector and cannot extend downward across D4000 into either target. A normal FAT16 sync does not issue FAT32 FSInfo writes.

**PROVEN scoped:** all7967 native cluster conversions satisfy these bounds, and modeled native file/delete/sync traces preserve both targets. **UNKNOWN:** current user-unit geometry. These equations alone do not authenticate it or qualify all non-filesystem storage producers.

Evidence: [target-equations.json (local-only reference: `builds/phase47-filesystem-state-closure/target-equations.json`; not distributed), normal-states.json (local-only reference: `builds/phase47-filesystem-state-closure/normal-states.json`; not distributed), [geometry derivation](<real-filesystem-geometry.md>).
