> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Focused existing candidate sources

PROVEN: current file identities match the prior census. UNKNOWN: none establishes original physical NOR $81000..$81016 bytes. All inherited candidates and new-file delta are in candidate-catalog.json.

| Full path | SHA-256 | Documented base / address space | Provenance / decision |

|---|---|---|---|

| C:\Proj SSD\CODEX\CIRCUIT\firmware\circuittracks-firmware-4486.bin | b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da | 0x08010000 / ARM internal application flash | Internal application/update image or other mapped address space, not a raw NOR identity record. Rejected. |

| C:\Proj SSD\CODEX\CIRCUIT\original\circuittracks-firmware-4486.syx | bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd | UNKNOWN / encoded firmware-update SysEx transport; not physical NOR addressable | Internal application/update image or other mapped address space, not a raw NOR identity record. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\stock\circuittracks-firmware-4486-STOCK.bin | b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da | 0x08010000 / ARM internal application flash | Internal application/update image or other mapped address space, not a raw NOR identity record. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\stock\circuittracks-firmware-4486-STOCK.syx | bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd | UNKNOWN / encoded firmware-update SysEx transport; not physical NOR addressable | Internal application/update image or other mapped address space, not a raw NOR identity record. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ext\circuittracksreverseengineering\Firmware-Analysis\dumpCT_flash_0x08000000.bin | f3d85d64c9ead9205e5336dff49bb51f21d270ffa29b47c6f6971125d6d848a8 | 0x8000000 / ARM internal flash | Internal application/update image or other mapped address space, not a raw NOR identity record. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ext\circuittracksreverseengineering\Firmware-Analysis\dumpCT_ram_0x20000000.bin | ebd902ba8a653748fea720af567cc95bcd893f3920f3a2fae5932bdff213efa2 | 0x20000000 / ARM SRAM | Loader proves assigned SRAM base, not historical external-NOR source. Identity cache offset+0xE is overwritten by native reader. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ext\circuittracksreverseengineering\Firmware-Analysis\ram_before_main.bin | 593b2df87e1b8e12bbcd9cfca8af94687f6e007d2df87187f6e2159d5be8b969 | UNKNOWN / UNKNOWN | Generated reset initialization image, not a post-storage physical capture; decodeSramInitData.py writes this file. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ext\circuittracksreverseengineering\Firmware-Analysis\ram_dump_boorloader_0x08003bc6.bin | 9eaa992876ff323a76d81bb1d7b86cdc57b005d00bb460081584b1e1b92bba86 | UNKNOWN / UNKNOWN | File identity verified; SRAM base/capture timing not established by loader. Filename PC is not NOR provenance. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ext\circuittracksreverseengineering\Firmware-Analysis\ram_dump_firmware_0x08037988.bin | 26a29670c0c1918217b7eadf8f89fe6df97994d3cc6e1c0ed65ac522e161094c | 0x20000000 / ARM SRAM | Loader proves assigned SRAM base, not historical external-NOR source. Identity cache offset+0xE is overwritten by native reader. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ext\circuittracksreverseengineering\Firmware-Analysis\diffCompare\bootloader.bin | 09fcb71d6583a5714cb96d496ffb423c0d7049754a4cb4413f588d6f54148643 | UNKNOWN / UNKNOWN | Internal application/update image or other mapped address space, not a raw NOR identity record. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ext\circuittracksreverseengineering\Firmware-Analysis\diffCompare\circuittracks-firmware-4486.bin | b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da | 0x08010000 / ARM internal application flash | Internal application/update image or other mapped address space, not a raw NOR identity record. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ext\circuittracksreverseengineering\Assets\Firmware\BIN\circuittracks-firmware-4486.bin | b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da | 0x08010000 / ARM internal application flash | Internal application/update image or other mapped address space, not a raw NOR identity record. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ext\circuittracksreverseengineering\Assets\Firmware\SYX\circuittracks-firmware-4486.syx | bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd | UNKNOWN / encoded firmware-update SysEx transport; not physical NOR addressable | Internal application/update image or other mapped address space, not a raw NOR identity record. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ctre\Firmware-Analysis\dumpCT_flash_0x08000000.bin | f3d85d64c9ead9205e5336dff49bb51f21d270ffa29b47c6f6971125d6d848a8 | 0x8000000 / ARM internal flash | Internal application/update image or other mapped address space, not a raw NOR identity record. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ctre\Firmware-Analysis\dumpCT_ram_0x20000000.bin | ebd902ba8a653748fea720af567cc95bcd893f3920f3a2fae5932bdff213efa2 | 0x20000000 / ARM SRAM | Loader proves assigned SRAM base, not historical external-NOR source. Identity cache offset+0xE is overwritten by native reader. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ctre\Firmware-Analysis\ram_before_main.bin | 593b2df87e1b8e12bbcd9cfca8af94687f6e007d2df87187f6e2159d5be8b969 | UNKNOWN / UNKNOWN | Generated reset initialization image, not a post-storage physical capture; decodeSramInitData.py writes this file. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ctre\Firmware-Analysis\ram_dump_boorloader_0x08003bc6.bin | 9eaa992876ff323a76d81bb1d7b86cdc57b005d00bb460081584b1e1b92bba86 | UNKNOWN / UNKNOWN | File identity verified; SRAM base/capture timing not established by loader. Filename PC is not NOR provenance. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ctre\Firmware-Analysis\ram_dump_firmware_0x08037988.bin | 26a29670c0c1918217b7eadf8f89fe6df97994d3cc6e1c0ed65ac522e161094c | 0x20000000 / ARM SRAM | Loader proves assigned SRAM base, not historical external-NOR source. Identity cache offset+0xE is overwritten by native reader. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ctre\Firmware-Analysis\diffCompare\bootloader.bin | 09fcb71d6583a5714cb96d496ffb423c0d7049754a4cb4413f588d6f54148643 | UNKNOWN / UNKNOWN | Internal application/update image or other mapped address space, not a raw NOR identity record. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ctre\Firmware-Analysis\diffCompare\circuittracks-firmware-4486.bin | b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da | 0x08010000 / ARM internal application flash | Internal application/update image or other mapped address space, not a raw NOR identity record. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ctre\Assets\Firmware\BIN\circuittracks-firmware-4486.bin | b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da | 0x08010000 / ARM internal application flash | Internal application/update image or other mapped address space, not a raw NOR identity record. Rejected. |

| C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main\ctre\Assets\Firmware\SYX\circuittracks-firmware-4486.syx | bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd | UNKNOWN / encoded firmware-update SysEx transport; not physical NOR addressable | Internal application/update image or other mapped address space, not a raw NOR identity record. Rejected. |
