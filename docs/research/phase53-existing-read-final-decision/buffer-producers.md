> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase53 — existing transfer-buffer producers

**PROVEN:** exact B1.3 SHA-256 `2e8a926190c86c6d76ab1c80c5f4ec34cf75f4753995f73cf5d170ce8f838c41`. Geometry READ10 uses40024000..40024FFF (4096 bytes); first512 bytes are the BPB prefix, not the USB block length. Producer57E88 first clears the full requested buffer, then fills it through NOR wrapper24130/DMA37430. SCSI3B54E→24754→389C6 retains the same pointer in the IN endpoint record;4862A starts endpoint hardware, not a separate sector reconstruction. b13-0803b27c.asm (local-only reference: `builds/phase53-existing-read-final-decision/b13-0803b27c.asm`; not distributed); b13-08057e30.asm (local-only reference: `builds/phase53-existing-read-final-decision/b13-08057e30.asm`; not distributed); b13-08024754.asm (local-only reference: `builds/phase52-read-authentication/b13-08024754.asm`; not distributed); b13-080389c6.asm (local-only reference: `builds/phase52-read-authentication/b13-080389c6.asm`; not distributed); b13-0804862a.asm (local-only reference: `builds/phase53-existing-read-final-decision/b13-0804862a.asm`; not distributed).

| Producer / normal path | Classification | Full512 deterministic independent of NOR? |

|---|---|---|

|57EA2→1A7E4 clear before READ |CPU-generated zeroes across4096 |**PROVEN** internal full clear; no distinct second pattern; target repeats this same clear |

|57ECC→24130→worker→22F94→37430 |External-NOR DMA |No; this is the operation being authenticated |

|57EDC serial-token replacement |Conditional RAM copy,14 bytes per found token |No independent512 guarantee; requires returned NOR bytes and identity cache |

|REQUEST SENSE03 |CPU clear/fill response18 bytes |No |

|INQUIRY12 |Fixed flash→RAM copy36 bytes (EVPD7) |No |

|MODE SENSE1A/5A |Fixed flash→RAM copy8 bytes |No |

|READ CAPACITY25 |CPU-generated8 bytes |No |

|READ FORMAT CAPACITIES23 |CPU clear/fill12 bytes |No |

|WRITE102A reception,3B61C/634 |Host-data buffer, then NOR write path if admitted |Not a read-only producer; ordinary entry rejected by writeprotect callback57E48=1 |

|BOT26E5C generic data-IN |Consumer of generated response pointer |No producer; response length capped, no512-byte padding generated |

|CBW / CSW |Protocol RAM2000679C /200068C4 |Not this buffer;31-byte CBW and13-byte CSW do not fill it |

|SD-backed operation |No SD read callback in initialized LUN0 backend |No existing supported path identified |

**PROVEN new native tests:** nine ordinary data-in cases execute exact B1.3 dispatcher. Actual generated sizes are36/7/18/8/8/12 as above; all transmitted response bytes are initialized for those model states. PoisonA5 in buffer offsets36..511 remains unchanged after every non-NOR generated command. The same destination is used but no command fully initializes512 bytes. Merely requesting a larger host allocation does not enlarge these generated payloads. [producer_cases.py](<../../../builds/phase53-existing-read-final-decision/producer_cases.py>); producer-cases.json (local-only reference: `builds/phase53-existing-read-final-decision/producer-cases.json`; not distributed) `commands`.

**PROVEN registered-path closure:**3B27C dispatch and resolved initialized table cover all normal MSD opcodes; unsupported/vendor SCSI opcodes fall to3B704 sense/error rather than an arbitrary buffer/memory reader. TUR/startstop/prevent/verify are no-data/status paths. No new command or malformed request was tried. b13-0803b27c.asm (local-only reference: `builds/phase53-existing-read-final-decision/b13-0803b27c.asm`; not distributed); [initialized-ram-callback.md](<../phase46-msd-filesystem-closure/initialized-ram-callback.md>).

**PROVEN census scope:** whole B1.3 byte/literal scan plus PC-relative-load scan finds real40024000 literals at8026F18 and803B788, consumed by the BOT/SCSI paths listed above. No initialized-data pointer into40024000..40024FFF is found. Four additional unaligned byte patterns resemble subrange addresses but have no PC-relative consumers in the scan; they are candidate bytes, not established buffer producers. existing-paths.json (local-only reference: `builds/phase53-existing-read-final-decision/existing-paths.json`; not distributed). This is not a theorem about arbitrary computed aliases or corrupted execution. No concrete additional supported producer is left unresolved; hypothetical aliases do not supply an existing usable command.
