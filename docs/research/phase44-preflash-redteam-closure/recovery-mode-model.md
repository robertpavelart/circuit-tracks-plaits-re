> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: SUPERSEDED / DO NOT FLASH.

# Bootloader recovery intake: independent offline model

PROVEN — This experiment executes the bootloader's own native intake, not the application updater. The authenticated 524,288-byte dump is `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/ctre/Firmware-Analysis/dumpCT_flash_0x08000000.bin`, SHA-256 `f3d85d64c9ead9205e5336dff49bb51f21d270ffa29b47c6f6971125d6d848a8`. Only its first 64 KiB supplies bootloader code. No hardware, ports, MIDI libraries, firmware generation or reference edits occur.

Evidence: [runnable model](<../../../builds/phase44-preflash-redteam-closure/recovery_model.py>), recorded results (local-only reference: `builds/phase44-preflash-redteam-closure/recovery-results.json`; not distributed), native disassembly (local-only reference: `builds/phase44-preflash-redteam-closure/recovery-disassembly.asm`; not distributed). Run with Python `-B recovery_model.py`; outputs stay in this directory. The original Phase43 candidate's existing SYX is read unchanged; these full-stream results do not by themselves certify a subsequently revised candidate.

## Entry, intake and model boundaries

PROVEN — Native `08002FDE` initializes boot storage (`08003A10`), reads metadata (`08003B2A`), then calls `08003B66(150)` at `08002FFC`. `08003000 CBNZ R0,08003006` bypasses automatic application validation/install when recovery is selected. Key handler `08003AB0` tests keys `0x12`, `8`, `9` through `0800489C`; all three selected set byte `20005378`. A separate executed key-handler/wait check returns `1` from native `08003B66` with those three modeled key levels. This is native logic under a modeled key-input seam, not physical confirmation of a button combination.

PROVEN — Full original candidate and official 4486 packet streams run through native `080059C4` vendor validation → `080059FA` dispatcher → `08007B08` initialization → `08007D86` header parsing → `08007BBC` preparation → `08007C06` WRITE/FINISH processing → `08007CBE` CRC decision → `08007D06` publication/reset. Calls do not enter application updater `08024D2C`. Both streams are accepted from a deliberately garbage-filled current application and zero-filled staging/metadata. Each then installs the exact expected decoded image through native `08003B9A`/`08003C24`.

UNKNOWN — Reset-to-USB-enumeration initialization, constructors, physical key sampling, USB interrupts and physical flash completion are not executed end to end. The model constructs the boot storage objects, selector-0 descriptor and state vtables explicitly from disassembled layouts. Storage virtual-method completion, timer/UI calls, CRC peripherals and internal flash primitives are modeled. Native address/length/state/CRC decision instructions execute. No application validity is used as an intake precondition in the executed paths; eventual physical availability of that intake is not proved by the model.

## Matrix

All rows below are PROVEN within those explicit seams. Metadata rows use constructed selector-0 metadata with the authenticated image length and CRC; B1.3 metadata is not claimed to be an independently captured NOR metadata record.

| Case | Native result | Internal program words |

|---|---|---:|

| Valid candidate metadata, current B1.3 | Installs candidate | 93,992 |

| Valid official metadata, current candidate | Installs official | 78,712 |

| Valid B1.3 metadata, current candidate | Installs B1.3 | 108,808 |

| Invalid CRC | No erase/program | 0 |

| Partial metadata | No erase/program | 0 |

| Garbage current application, valid official staged | Installs official | 78,712 |

| Erased application representing interrupted prior install | Installs official | 78,712 |

| Valid candidate staged, invalid current application | Installs candidate | 93,992 |

| Same valid staged and installed official header | Silent installation no-op | 0 |

| Official staged, metadata numeric version `000000` | Installs official | 78,712 |

PROVEN — Full bootloader-owned intake separately accepts both original candidate and official streams, commits metadata, reaches reset and subsequently installs the expected image. Candidate staged/installed SHA-256 is `9b29180ff7f88c9c982c60abdfd5e5b296e8f2240ad57580366a5a7f797930a6`; official staged/installed SHA-256 is `b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da`.

PROVEN — Within the model, candidate range erase is `[000000,05C000)`, official range erase `[000000,04D000)`, and metadata erase `[080000,081000)`. These sector-rounded spans are effects of modeled storage virtual methods, not an additional census of native low-level erase-command implementations. Actual native call sites supply the staging endpoints and metadata address. Program traffic consists of 32-byte staged blocks, followed by exactly 23 metadata bytes `[080000,080017)`. Neither target `[081000,081017)` nor `[082000,082200)` overlaps these selected-path operations.

## Version and no-op behavior

PROVEN — `08003B9A` first checks metadata size `< 0x70001`, selector byte `0`, and CRC not equal to `FFFFFFFF`. `08003BBA` through `08003BCE` compare staged image header bytes `+4/+5` against bootloader header `080001C8+4/+5`. These are compatibility bytes. The routine validates staged CRC, then `08003BE4`–`08003BF6` compares 38 bytes of staged and current application headers at image offset `0x1C8`; equality skips installation. This is not a numeric newer-version ordering test. The executed zero-numeric-metadata-version control still installs, while the same-header control performs no internal writes.

STRONG INFERENCE — Changing executable bytes without changing the compared 38-byte header can produce a silent no-op even if staged CRC is valid. The same-header positive control proves the branch; no claim is made that every arbitrary modified application shares the same header.

## Metadata persistence and interrupted work

PROVEN — Successful recovery publication at `08007D14`–`08007D32` supplies hardcoded `0x80000`, length `0x17`, and erase-first argument `1`, then `08007D40`–`08007D58` requests reset. It replaces the old metadata sector only after the staged CRC-success state. Native `08003B2A` reads metadata; native validator/installer does not clear it. The recorded metadata survives validation/install. A later valid matching staged/current header therefore skips redundant installation.

PROVEN — Invalid CRC and partial-metadata rows perform no internal erase/program. Full uploads starting from corrupted staging, metadata and application still accept official 4486. Thus this modeled corrupt prior state does not prevent a later recovery upload. No forced semaphore release or device-side recovery modification is introduced.

UNKNOWN — Every possible power-loss byte boundary, a torn NOR erase/program, hardware write protection, NOR faults, USB disconnect timing, persistent identity/settings side effects outside these native paths, and recovery after the proposed diagnostic's actual hardware failure are not established. This scoped result is not a claim that recovery always works on hardware.
