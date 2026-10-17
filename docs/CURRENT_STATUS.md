# Current authoritative project state

**OPERATIONAL PREFLIGHT = UNQUALIFIED. POST-READY ALLOCATION CENSUS = UNQUALIFIED. USB STORAGE JOINT PATH = PASS.**

Current through 17 October 2026 (Europe/Moscow). The Phase63 artifact is a temporary NOR diagnostic, not Plaits firmware; it has not been hardware-tested. Phase67's FINAL PREFLIGHT CLOSURE = PASS remains valid only within its scoped model. No concrete offline firmware blocker has been demonstrated; the accepted residual software uncertainty is post-READY indirect allocation reachability with an eight-byte modeled heap gap. Tools remain locked. Risk acceptance is neither proof nor authorization to use them.

Evidence precedence: [final allocation decision](<research/final-indirect-resolution/findings.md>) controls the remaining software proof boundary; [USB joint-path closure](<research/final-two-check-closure/usb-joint-closure.md>) records 36 passing focused cases. [Phase67](<research/phase67-final-safety-disposition/findings.md>) retains its bounded configuration/query/authorization-to-capture-entry scope. The frozen [package audit](<research/final-hardware-test-package/final-cheap-checks.md>) preserves the earlier two-gap history, with a current supersession notice. No model PASS is physical proof.

## Current candidate — temporary NOR diagnostic

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| circuittracks-nor-defect-closure-development.syx (local-only reference: `builds/final-hardware-test-package/circuittracks-nor-defect-closure-development.syx`; not distributed) | raw instruction bytes omitted | `9b420521a366c65c13fb871778fdbab612ca126cbb4ad60d0fd5bc12ecd253da` |
| circuittracks-nor-defect-closure-development.bin (local-only reference: `builds/final-hardware-test-package/circuittracks-nor-defect-closure-development.bin`; not distributed) | raw instruction bytes omitted | `edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9` |

CRC-32/MPEG-2: **1BB21302**. Marker: **N63DEV**. Application: **0x08010000 .. 0x08075100**, end-exclusive. The Phase63 originals and package copies have the same bytes; no later candidate was generated. Phase61 and the original Phase62 candidates are **FAILED / SUPERSEDED / DO NOT FLASH**; Phase43 is historical / SUPERSEDED / DO NOT FLASH.

## Primary accepted residual SOFTWARE uncertainty

**POST-READY ALLOCATION CENSUS = UNQUALIFIED.** Static analysis did not exhaustively resolve indirect/virtual targets, including **0x0803C91C**, **0x0803C9C4**, and registry/object-method sites. No actual post-READY allocation >8 bytes was found; its absence is NOT proven. The modeled heap cursor is `20044D68`, cap `20044D70`: eight bytes, not physical stack margin or replenished per-request capacity.

The recovered normal-publisher set for `08022E22` has seven targets. Four are allocator-free; three lead to unresolved virtual continuations. The expanded ledger covers 260 encountered indirect sites, 233 unresolved, and 73 target summaries. These are conservative traversal counts, not 233 proven allocation hazards or an exhaustive complete graph.

PROVEN in four isolated allocator ABI cases: rejection reaches BKPT; if execution is artificially continued after BKPT, R0=`FFFFFFFF`, accepted by the generic wrapper as nonzero. Physical exception routing remains UNKNOWN. Safe failure cannot be assumed. These isolated inputs do not prove a post-READY occurrence. See [findings.md](<research/final-indirect-resolution/findings.md>), indirect-ledger.csv (local-only reference: `builds/final-indirect-resolution/indirect-ledger.csv`; not distributed), and [failure-semantics.md](<research/final-indirect-resolution/failure-semantics.md>).

## CLOSED — known defects and focused synchronization check

| Item | Closure and scope |
|---|---|
| Phase61 reservation bug: VALID could publish into unreserved memory | Reservation guard added in Phase62, retained with seven Phase63 regressions. Phase61 FAILED / SUPERSEDED |
| SD mount invalidated retained NOR geometry | Phase63 separates NOR binding/epoch semantics; SD/NOR native tests pass |
| NOT_READY / INVALID / FAILED status ambiguity | Explicit 39-byte CRC-protected status protocol and matching host handling |
| DMA still referenced former Main stack storage after return | Ownership fence before CPU use and common return; 31 saved DMA cases and later focused joint cases pass in their scopes; no forced unwind |
| Late SUCCESS overwrote failure/quarantine | Absorbing failure/atomic terminal handling fixed earlier and retained |
| USB Storage / diagnostic joint path | **USB STORAGE JOINT PATH = PASS**: 36 focused cases, both request orders, failure/late completion, disconnect/remount and resets; declared native/model seams |

Evidence: [findings.md](<research/phase63-defect-closure/findings.md>), [sd-mount-fix.md](<research/phase63-defect-closure/sd-mount-fix.md>), [status-protocol.md](<research/phase63-defect-closure/status-protocol.md>), [buffer-ownership.md](<research/phase63-defect-closure/buffer-ownership.md>), [usb-joint-closure.md](<research/final-two-check-closure/usb-joint-closure.md>) and joint-results.json (local-only reference: `builds/final-two-check-closure/joint-results.json`; not distributed).

Saved Phase63 results: 7 reservation, 28 native, 13 status/mount, 31 DMA, 32 host containment and 3 install/rollback transitions. None was rerun for this documentation update. CLOSED refers to demonstrated defects and stated regression scopes, not guaranteed physical behavior.

## Model-coverage history — scoped evidence

Phase64 closed narrow SPI2 startup modeling. Phase65 closed 16-bit SHI coefficient-transfer framing (144 uploads; 148 jobs posted; 147 idle completions observed), using synthetic coefficients. Phase66 reached USB controller READY with geometry intact and 3,186 allocator returns across two layers, without observed allocation failures or diagnostic-owned overlap. Phase67's bounded boot-SRAM fixture reached configuration/query/authorization and capture entry with zero new allocations and preserved geometry. It stopped at raw entry and is not uninterrupted reset-to-capture or real USB enumeration proof.

Further peripheral emulation has diminishing safety value; no SPI2/SHI/USB/DWT continuation or endless reverse-engineering loop is the current next step. The allocation proof boundary remains SOFTWARE UNKNOWN, distinct from HARDWARE-ONLY UNKNOWN timing, physical stack margin, current-unit bytes, completion behavior and candidate-specific recovery.

## Independent review and user decision

The independent Claude review is **reported by the user** as: **REASONABLE TO PROCEED WITH CONTROLLED HARDWARE TEST**, subject to explicitly accepted residual risk. The reported review found no concrete offline firmware blocker or bootloader-loss path and recognized the actual defect fixes. This records the supplied review conclusion, not a new independent review in this task. Later allocation findings remain SOFTWARE UNKNOWN even though earlier review emphasized hardware/model uncertainty. Neither favorable review nor accepted soft-brick risk changes OPERATIONAL PREFLIGHT = UNQUALIFIED or enables tools.

## Recovery and accepted risk

**PROVEN — by user report on the physical unit:** recovery/bootloader mode can be entered; full power cycling exits recovery; B1.3 boots normally afterward; no firmware was transmitted during that rehearsal. This does not mean the diagnostic candidate was tested.

**UNKNOWN / NOT PROVEN:** recovery-mode host enumeration, uploader handshake in recovery, actual recovery flashing of B1.3 or official 4486, recovery from a non-booting diagnostic candidate, and guaranteed recovery. Physical candidate-specific recovery is **HARDWARE-ONLY UNKNOWN**.

**STRONG INFERENCE from the saved offline scope:** no concrete bootloader-loss path has been identified. **PROVEN in modeled install/rollback operations:** bootloader lies outside application erase/program ranges and remains unchanged. This is narrower than physical recovery success.

The user explicitly accepts the possibility of a soft brick requiring recovery, provided the bootloader remains accessible. Recovery success is not guaranteed. Acceptance does not convert UNKNOWN into PROVEN, close the allocation census, enable tools or authorize hardware action in this documentation task. See [recovery-status.txt](<operations/recovery-status.txt>).

## Rollback artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| circuittracks-B1.3-manifest-matched.syx (local-only reference: `builds/final-hardware-test-package/circuittracks-B1.3-manifest-matched.syx`; not distributed) | raw instruction bytes omitted | `6f07376b5983a5e0350d4883ae9ed57a69bc735320afde9f43ca75017b8e8736` |
| circuittracks-firmware-4486-STOCK.syx (local-only reference: `builds/final-hardware-test-package/circuittracks-firmware-4486-STOCK.syx`; not distributed) | raw instruction bytes omitted | `bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd` |

PROVEN: local byte identities. UNKNOWN: independent authentication of the local 4486 artifact against a fresh Novation-origin download. Modeled exact install/rollback, no silent no-op, bootloader equality and no target write/erase overlap do not prove physical rollback. See install-validation.json (local-only reference: `builds/phase63-defect-closure/install-validation.json`; not distributed).

## Operational tools — LOCKED

| Tool | Exact identity | Lock |
|---|---|---|
| [live_host.py](<../builds/final-hardware-test-package/live_host.py>) | Version `1.0.0-phase68-locked`; SHA-256 `9b8a7d3d088cdffe21257824cb16db602659d678d240e7266f468e92c3ae9dc9` | `live_enabled=false` |
| [ct_uploader-final-offline-locked.html](<../builds/final-hardware-test-package/ct_uploader-final-offline-locked.html>) | SHA-256 `bf1ef00dbca9c3715932235249fcc8ba0a71d6f2f989c047aa8caf66b85e17a5` | `PREFLIGHT_QUALIFIED=false` |

PROVEN in saved mocks: 32 host cases pass. No live host or uploader operation was run for this update. The same exact frozen uploader is intended for candidate install and both rollback files. Do not manually toggle locks. A separately reviewed operational release with new hashes is required before hardware use; the current locked package is not that release.

**H4 remains FAILED (H4 = FAIL) for bounded in-session recovery.** On any failed or uncertain raw capture: discard all partial evidence; DO NOT RETRY; send no second diagnostic/Storage request or cleanup command; full physical power OFF, USB unplugged, session ends. No forced semaphore release. A reset, new process, session identifier or deleted attempt marker is not a power-cycle substitute.

## Windows / MSD — prepared, not physically applied or tested

Automount control alone is NOT sufficient isolation. Removable-storage access denial policy is prepared in [windows-msd-policy.txt](<operations/windows-msd-policy.txt>); applicability/enforcement with this unit remains HARDWARE-ONLY UNKNOWN. No scan/repair, format, Explorer browsing, SD changes or filesystem utilities. Close Components, DAWs and other MIDI users. Unexpected mounted volume or storage access means STOP. No OS policy was changed here.

## Plaits dependency and current stop point

Authentic `$82000-$821FF` coefficients have NOT been captured. P:`$0282-$0386` (261 words) is not finally qualified; final safe P/X/Y capacity and complete Plaits hardware integration remain UNKNOWN. Synthetic inputs do not qualify physical provenance. The diagnostic exists to obtain that evidence; it is not an engine release.

1. Keep repository documentation current and operational tools locked.
2. Prepare a **separately reviewed operational release**, with new exact tool hashes and explicit treatment of the accepted allocation uncertainty; do not manually toggle the frozen locks.
3. In a future explicitly authorized session, verify all hashes on the actual sending machine and apply/verify Windows/MSD policy before connection. Stop if isolation cannot be established.
4. Conduct the controlled hardware test only under that separately reviewed release and explicit user decision.
5. Query geometry first; independently validate the retained geometry and `$82000` safety on the host.
6. Authorize only the exact validated epoch/geometry/session; exactly one fixed capture. Optional `$81000` identity requires separate target authorization.
7. On success, validate/hash/archive complete evidence and restore B1.3 using the agreed rollback plan.
8. On any failure, discard partial evidence, no retry or second diagnostic/Storage request, full physical power OFF, USB unplugged, session ends.

No hardware, MIDI or transmission is authorized by this documentation update. See [FINAL_DOCUMENTATION_AUDIT.md](<FINAL_DOCUMENTATION_AUDIT.md>).
