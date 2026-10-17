> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Mount ownership correction

**PROVEN:** original `$0801AE02` calls the same adapter for NOR FS `$20000AB0` and SD FS `$20001B04`. Phase61 `begin` treated any nonzero lifecycle word as invalid and stored `1D`, including after NOR snapshot `11` when SD mounted. This was a shared callback-owner predicate bug, not a demonstrated shared NOR/SD generation counter.

**PROVEN:** new `build_ops.begin` at `$0806CF00` ignores all but R0=`20000AB0`. `snapshot` at `$0806D500` independently requires outer-mount R4=`20000AA0` (its FS is object+10), exact reserved heap limit `$20044D70`, and cursor at/below that limit. Existing drive-0 predicates remain in register/slow/binding/stride adapters. SD registration `1:` and its object/stride are ignored. The seven negative reservation cases still execute installed AE06 and original AE14 tail.

**PROVEN:** startup legitimately mounts NOR again through `$08026250→0801ADDC` before export. `11→17` now denotes pre-export recheck. Registration/slow mount and 4096-byte stride are permitted only in first-mount `16` or recheck `17`. Snapshot recomputes all packed fields; recheck compares both 32-bit words with the original, writes neither payload word, then returns to `11`. A mismatch, failed mount, or later exported/active-state remount invalidates authorization. Binding change still invalidates.

**PROVEN in tested paths:** SD mount/failing mount/unmount/remount, SD binding/stride, unchanged pre-export NOR remount, changed NOR geometry, and post-export NOR remount: status-mount-tests.json (local-only reference: `builds/phase63-defect-closure/status-mount-tests.json`; not distributed). All previous native cases remain: native-tests.json (local-only reference: `builds/phase63-defect-closure/native-tests.json`; not distributed). Native startup private writes show `16→11→17→11` with no SD invalidation; only first snapshot writes payload.

**STRONG INFERENCE:** owner predicates separate NOR lifecycle from SD activity for other invocations of these same adapters. This is not a universal proof about arbitrary writes to geometry outside the inherited mutation closure.

Implementation: [construct.py](<../../../builds/phase63-defect-closure/construct.py>), `module` asserted transforms of the unchanged Phase61 emitters. Full M-class listings are in `reviewed-*.asm`.
