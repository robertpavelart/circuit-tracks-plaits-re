# Reverse-engineering state — final pre-hardware review

**OPERATIONAL PREFLIGHT = UNQUALIFIED. POST-READY ALLOCATION CENSUS = UNQUALIFIED. USB STORAGE JOINT PATH = PASS.**

Current through 17 October 2026 (Europe/Moscow). The Phase63 artifact is a temporary NOR diagnostic, not Plaits firmware; it has not been hardware-tested. Phase67's FINAL PREFLIGHT CLOSURE = PASS remains valid only within its scoped model. No concrete offline firmware blocker has been demonstrated; the accepted residual software uncertainty is post-READY indirect allocation reachability with an eight-byte modeled heap gap. Tools remain locked. Risk acceptance is neither proof nor authorization to use them.

Evidence precedence: [final allocation decision](<research/final-indirect-resolution/findings.md>) controls the remaining software proof boundary; [USB joint-path closure](<research/final-two-check-closure/usb-joint-closure.md>) records 36 passing focused cases. [Phase67](<research/phase67-final-safety-disposition/findings.md>) retains its bounded configuration/query/authorization-to-capture-entry scope. The frozen [package audit](<research/final-hardware-test-package/final-cheap-checks.md>) preserves the earlier two-gap history, with a current supersession notice. No model PASS is physical proof.

# Stock ARM

The working MCU identity is STM32F745VEH6, inherited from project/device identification. Firmware mapping supports the STM32F745 family; this is not a new physical package inspection. **PROVEN:** application base `0x08010000`; bootloader `0x08000000–0x0800FFFF`. Official 4486 / 1.2.1 application size 314844 (`0x4CDDC`), end exclusive `0x0805CDDC`; BIN SHA-256 `b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da`, CRC-32/MPEG-2 `4E74DA9E`.

# Updater protocol

**PROVEN in decoded protocol/native replay:** `0x71 INIT`, `0x7C HEADER`, `0x72 WRITE`, `0x73 FINISH`. Data blocks are 32 bytes; block 0/vectors arrive through FINISH. Updates stage in external NOR before validated internal-flash installation. CRC is non-reflected CRC-32/MPEG-2, not reflected ZIP CRC.

The unchanged Phase63 candidate has12935 WRITE packets plus INIT/HEADER/FINISH =12938 messages,12936 data blocks and0 FF tail-padding bytes. Its exclusive image/programming end is0x08075100. Install/rollback replay models physical completion; it is not a hardware flash or complete cold-boot recovery test.

# Recovery model

PROVEN by user report: recovery entry/exit and normal B1.3 boot afterward were physically rehearsed without transmission. Recovery enumeration, handshake and actual recovery flashes remain UNKNOWN. See CURRENT_STATUS.md for the accepted risk and exact limits; recovery is not guaranteed.

# DSP architecture

**PROVEN from extracted/rebuilt programs:** DSP56724 / DSP56300-family dual-core architecture, separate P and X/Y spaces. DSP external SDRAM word addresses are distinct from ARM NOR byte addresses.

| Image/core | P interval | Used words |
|---|---|---:|
| Stock core0 | `$0000–$2A5D` | 10846 |
| Stock core1 bootstrap/service | `$0000–$016B` | 364 |
| B1.3 core0 | `$0000–$3FEC` | 16365 |
| B1.3 core1 | `$0000–$07FE` | 2047 |

Occupancy alone does not qualify neighboring tails under initialization, aliases or service contracts.

# Audio block

**PROVEN:**32 samples/block. **STRONG INFERENCE, conditional timing model:**246 MHz and 48046.875 Hz yield 163840 cycles/block/core. These rates are not a new physical measurement. Aggregate two-core arithmetic does not establish balanced scheduling or safe core1 service latency.

# B1.3 seams

| Patch point | Destination/role |
|---|---|
| P:`$010B` | `$2A5E`, custom init |
| P:`$023C` | `$336E`, vpre insertion |
| P:`$0274` | `$2ACE`, Master FX |
| P:`$09C3` | `$2C54`, line/noise hook |

**PROVEN reference architecture:** ARM `c_vnon`, `c_vnoff`, `c_vtick`, `c_vsend` carry note/control events. Encoding is `tag<<23 | code<<16 | signed16` at X:`$3B80 + 48*t`. Two 48-word mailboxes plus 16 save words occupy X:`$3B80–$3BEF`; these are retained infrastructure.

Known stock generation/output neighborhood includes P:`$09B9`, P:`$09D9` and X:`$2C46–$2C65`. Scratch/output ownership is not persistent-state permission. The generation-disabled study places RTS at P:`$0281`; candidate reclaim starts at `$0282`. Disabling generation after boot does not prove initialization/data references removable.

# Intended retained functionality

Preserve sequencer, patterns, scenes, automation, note handling, mixer strips, track level/pan/sends/sidechain, Master FX, drums, project/session workflow, transport and clock. Retained B1.3 MIDI modes include line, granular, FX sequencer, routing/control and step-drummer where independent of removed synthesis. **UNKNOWN:** complete dependency-removal qualification for the final architecture.

# Current tooling/layout

`tools/` contains offline stock extraction, protocol and memory/control analysis; `emulator/` contains DSP execution/upstream sources; `plaits/` contains pinned upstream and PoCs. `firmware/`, `builds/`, `notes/`, `original/`, `ghidra/` and `circuit-tracks-plaits-re/` preserve evidence/artifacts/earlier work. Some historical builders/validators write artifacts; do not run them as a documentation check. No REA/Ghidra native firmware opening is required by this snapshot.

Evidence: [baseline](<../notes/baseline.txt>), [firmware map](<../notes/firmware-map.md>), [recovery gate](<../notes/firmware-recovery-gate.md>), [four-track architecture](<../notes/four-track-plaits-resource-architecture.md>), [vpre analysis](<../notes/plaits-midi-vpre-offline.md>), [diagnostic reuse audit](<../notes/circuits-hacks-diagnostic-reuse-audit.md>), [historical Phase43 — SUPERSEDED](<research/phase43-hardware-test-candidate/findings.md>), [tool README](<../tools/README.md>).

## Current corrected diagnostic — scoped evidence

First-mount reserved geometry/lifecycle snapshot → RAM-only 0E export → independent host geometry validation → exact first-epoch/geometry/session 0F authorization → fixed read. Phase63 distinguishes SD/NOR owners, adds 39-byte status replies and fences DMA/request/backend ownership before CPU use or raw-frame return. Phase67 callbacks reach capture entry without new allocation; USB bus/output seams are modeled, not real enumeration.

H4 remains FAIL for bounded recovery: discard partial evidence, no retry/second Storage request/forced cleanup, full physical power cycle after failed/uncertain capture. Current identity/locks: [CURRENT_STATUS.md](<CURRENT_STATUS.md>). Phase61 schema is HISTORICAL background, to be read with [status-protocol.md](<research/phase63-defect-closure/status-protocol.md>), [sd-mount-fix.md](<research/phase63-defect-closure/sd-mount-fix.md>) and [buffer-ownership.md](<research/phase63-defect-closure/buffer-ownership.md>); its failed reservation assumptions are not current.
