> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase63 narrow defect closure — development image remains ineligible

**FINAL PREFLIGHT CLOSURE = UNQUALIFIED. Do not use this image for a hardware test.**

The three Phase62 defects have targeted implementation changes and passing scoped regressions. The mandatory continuous startup and full postboot allocation gates are incomplete. Passing prepared-RAM tests does not replace those gates. No hardware was accessed, MIDI ports opened, firmware transmitted, or reference repository modified.

| Requirement | Evidence / result | Confidence |

|---|---|---|

| SD cannot invalidate unchanged NOR | NOR FS/object predicates; native SD mount/unmount/remount and binding/stride tests | PROVEN within tested paths |

| Actual NOR remount/change invalidates authorization | Post-export remount rejects; pre-export repeat must exactly match the first snapshot | PROVEN within tested paths |

| Explicit statuses | Actual dispatch emits READY/AUTHORIZED/SUCCESS; classifier tests cover remaining states; 39-byte CRC-protected wire replies | PROVEN within native boundary tests |

| DMA stack lifetime | No CPU consumption or wrapper return before EN=0, NDTR=0, request=0, backend semaphore=1; 31 coupled cases | PROVEN in declared model |

| New reservation / prior native suite | 7 reservation and 28 native cases pass | PROVEN |

| Host containment | 32 fake-transport cases pass; NOT_READY query can repeat; failures cannot retry/publish | PROVEN in mocks |

| Continuous reset→capture | Same-state startup survives NOR/SD; still stops before USB service | UNKNOWN beyond current frontier |

| Complete postboot allocations | 176 requests observed in prefix; subsequent startup/runtime not reached | UNKNOWN |

| Install / both rollbacks | All three exact-stream native replays pass, no silent no-op, bootloader excluded, protected ranges unchanged | PROVEN within stated seams |

| Uploader binding | Exact candidate/rollback hashes bound to a tested, MIDI-locked review copy | PROVEN; live admission withheld |

## New identity, development only

- BIN: `circuittracks-nor-defect-closure-development.bin`, 413952 bytes; SHA-256 `edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9`.

- SYX: `circuittracks-nor-defect-closure-development.syx`, 569229 bytes; SHA-256 `9b420521a366c65c13fb871778fdbab612ca126cbb4ad60d0fd5bc12ecd253da`.

- CRC-32/MPEG-2 `1BB21302`; compared-header marker `N63DEV`; application `08010000..08075100` exclusive; 44,800 image bytes remain below the application limit. This is not a RAM margin measurement.

- Independent disk SYX decode equals BIN; all 1,558 changed bytes versus frozen Phase62 are classified in development-identity.json (local-only reference: `builds/phase63-defect-closure/development-identity.json`; not distributed). No bootloader bytes are part of the generated application image.

## Remaining gates and smallest continuation

**UNKNOWN:** final continuous startup→USB-ready→geometry query→authorization→raw capture. Latest native prefix executes 787,221 instructions, ends at `0x8037968`, and retains record `110000000180003480908f01`. The exact missing model is SPI2 polled TXE/RXNE and received-data behavior at `$08037960-$0803799C`, status register `$40003808`. The native wait is not bypassed and no replacement running-RAM fixture is spliced in. It is a model frontier, not evidence of a hardware hang or a new firmware corruption defect.

**UNKNOWN:** allocation coverage through that missing continuation. Ordinary nonoverflow allocator bounds and diagnostic no-allocation behavior are tested; they do not enumerate every later startup/runtime owner. Hardware heap/stack headroom remains separately **UNKNOWN (HARDWARE-ONLY)**.

The smallest next experiment is to complete that exact SPI2 exchange model using the pinned DSP startup protocol, resume the same-state runner through USB readiness and capture, and record remaining allocations. Do not restart the NOR investigation, rebuild an unchanged candidate, rerun successful install/rollback tests, or force readiness counters. If that requires candidate changes, every invalidated image-specific gate must be rerun.

See [sd-mount-fix.md](<sd-mount-fix.md>), [status-protocol.md](<status-protocol.md>), [buffer-ownership.md](<buffer-ownership.md>), [startup-allocation.md](<startup-allocation.md>), [install-uploader.md](<install-uploader.md>) and CHECKPOINT.md (local-only reference: `builds/phase63-defect-closure/CHECKPOINT.md`; not distributed).

Phase61's 112 manifest entries and both frozen Phase62 images verify unchanged: historical-preservation.json (local-only reference: `builds/phase63-defect-closure/historical-preservation.json`; not distributed). Neither historical image is reinstated. There is no final hardware-eligible candidate or enabled uploader.

FINAL PREFLIGHT CLOSURE = UNQUALIFIED
