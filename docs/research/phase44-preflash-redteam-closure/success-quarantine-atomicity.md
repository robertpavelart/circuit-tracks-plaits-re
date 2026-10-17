> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: SUPERSEDED / DO NOT FLASH.

# ACTIVE → SUCCESS versus SysTick quarantine

**PROVEN:** the original Phase43 candidate is not atomic at this decision. Exact bytes at `0x0806B9E4` load state, `0x0806B9E6` compare ACTIVE, `0x0806B9E8` branch, `0x0806B9EA` load SUCCESS and `0x0806B9EC` store it. No PRIMASK/critical section covers that sequence. SysTick `0x0805998C` calls watchdog `0x0806B748` through the patched BL at `0x0805998E`.

**PROVEN:** interrupt injection after the ACTIVE load/before its store lets the real native watchdog write FAILED_QUARANTINED=3; resumed stale-register code then writes SUCCESS=2. This is recorded by [success_atomicity.py](<../../../builds/phase44-preflash-redteam-closure/success_atomicity.py>) and results (local-only reference: `builds/phase44-preflash-redteam-closure/success-atomicity.json`; not distributed). The earlier “timeout during final TX” case interrupted before the later state load, so it missed this narrower window.

**PROVEN scoped consequence:** this is terminal-state/success classification, not a demonstrated second request or corrupted evidence. The race occurs after all reads and completion TX. Both states 2 and 3 reject new admission, and neither forces Storage release. The host's independent deadline/CRC/length acceptance remains. Nevertheless it invalidates the advertised monotonic quarantine contract, so retaining that exact image as the corrected candidate would be wrong.

## Minimal implementation

The 32-byte fragment at `0x0806BC30–0x0806BC4F` uses `MRS r2,PRIMASK; CPSID i`, performs the ACTIVE test and conditional SUCCESS store, restores the caller's mask with `MSR PRIMASK,r2`, then branches to existing finish `0x0806B9EE`. A four-byte branch at `0x0806B9DC` replaces the original state-address load. It uses existing FF pool slack, no new RAM or image growth, and preserves existing downstream addresses. R 2 is caller-volatile and the inherited caller-preservation tests pass. See fragment disassembly (local-only reference: `builds/phase44-preflash-redteam-closure/success-atomicity-fix.asm`; not distributed).

**PROVEN:** instruction-boundary tests cover the fragment with PRIMASK initially 0 and 1, pending IRQ delivery after unmask, and an already-quarantined record. All 25 corrected checks preserve the original mask and never promote observed quarantine. Six original boundary cases retain the failure evidence. The authenticated final corrected bytes equal this fragment.

## Separate corrected artifacts

Only after that failing test, [qualify_atomic_fix.py](<../../../builds/phase44-preflash-redteam-closure/qualify_atomic_fix.py>) created separately named Phase44 BIN/SYX. Original Phase43 files remain unchanged. The marker becomes `N44ATM` at `0x080101E8–0x080101ED`: the bootloader compares 38 header bytes, so this marker change is required to prevent original→corrected installation silently becoming a no-op. Changed-code/same-header control (local-only reference: `builds/phase44-preflash-redteam-closure/header-noop-control.json`; not distributed) executes both the no-op and distinct-marker install.

**PROVEN offline:**39 actual byte differences from Phase43, limited to the branch, fragment and marker; unchanged image size, heap footprint, vectors, DSP, bootloader and option-byte scope. Identity is in atomic-candidate-identity.json (local-only reference: `builds/phase44-preflash-redteam-closure/atomic-candidate-identity.json`; not distributed). All 25 inherited coupled native cases pass; final-file admission regression (local-only reference: `builds/phase44-preflash-redteam-closure/atomic-native-regression.json`; not distributed) passes 512 USB/DIN opcode cases, supplied-address rejection, 20-tick dormancy and capture. Supplement (local-only reference: `builds/phase44-preflash-redteam-closure/atomic-supplement.json`; not distributed) runs actual corrected-SYX native USB output through the revised host and separately through bootloader-owned recovery intake.

**UNKNOWN:** physical exception timing and every unmodeled reset/peripheral/task interaction. Fixing this race does not close normal boot/background NOR mutation-producer reachability. H4 remains FAIL. Neither artifact is authorized for hardware use by this report.
