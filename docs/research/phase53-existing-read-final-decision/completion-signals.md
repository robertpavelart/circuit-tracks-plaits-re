> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase53 — internal completion state versus host observability

| Candidate | Internal source | Existing observable read-only interface / decision |

|---|---|---|

|DMA EN/NDTR/TC flags |DMA2 stream7,400264B8/BC and status registers |**PROVEN** internal state; no exported field in resolved SCSI responses or inspected supported B1.3 status handlers |

|QSPI TCF/softwarebit0 |IRQ22826→37596 |Internal wait condition, not returned alongside payload. Native read setup's EN1-skip returns0; no host NDTR attestation. |

|Backend return1/2/0 |22F94→worker240C4→wrapper24160 |MSD57ECE discards it and57EEE returns0; not independently observable through REQUEST SENSE |

|Wrapper pending/sync/status |RAM wrapper+C/+10/+18 |No supported B1.3 RAM export; internal queue drain is not a host completion counter |

|SCSI sense |3B732 queue, REQUEST SENSE03 |Only errors queued by SCSI.57E88 hides underlying failures, so no corresponding medium error is enqueued. Phase51 native failures produce GOOD CSW and zero residue. |

|TUR00 |table+8→57E44 |Always returns0; not a test of last NOR request or DMA state |

|READ CAPACITY/FORMAT |table+4→57E34 |Fixed8192/4096, not success/byte count of prior read |

|INQUIRY/MODE SENSE |Fixed flash response tables |No per-read completion fields |

|VERIFY2F |3B6AA checks BYTCHK/LBA bounds |No NOR read/checksum or comparison callback; cannot attest the previous transfer |

|BOT count/CSW |RAM protocol bookkeeping |Counts submitted USB bytes; no lower physical byte count. Successful CSW survives native backend errors. |

|USB descriptor/status |Enumeration / endpoint state |Does not carry DMA/QSPI status or source address |

|Vendor42 status / identity; vendor41 parameters |24918/2527C/24A10 |Mode/identity/parameter fields, not a NOR completion export; no supported arbitrary register read contract |

|rdiag/ctremote mem |Known diagnostic-build command2 |**PROVEN absent from exact B1.3**; host tool availability is not installed-firmware capability |

Sources: b13-0803b27c.asm (local-only reference: `builds/phase53-existing-read-final-decision/b13-0803b27c.asm`; not distributed); b13-08026d64.asm (local-only reference: `builds/phase53-existing-read-final-decision/b13-08026d64.asm`; not distributed); producer-cases.json (local-only reference: `builds/phase53-existing-read-final-decision/producer-cases.json`; not distributed); [read-error-propagation.md](<../phase51-msd-read-safety/read-error-propagation.md>); read-cases.json (local-only reference: `builds/phase51-msd-read-safety/read-cases.json`; not distributed); DMA-setup-cases.json (local-only reference: `builds/phase52-read-authentication/DMA-setup-cases.json`; not distributed); [b13-readonly-interfaces.md](<../phase49-existing-geometry-reader/b13-readonly-interfaces.md>).

**PROVEN NO under the inspected supported-interface contract:** the required independent physical completion evidence is not exposed. A flag existing internally is not a host-observable signal. Generic sense, a GOOD CSW, fixed capacity and transport byte count cannot recover discarded status. No concrete existing completion-export mechanism remains unresolved. This does not assert that the hardware never completes reads correctly or that all unknown firmware behavior is impossible.

Multi-sector reads: **PROVEN**3B4FC..3B51C chooses at most1000hex bytes and converts this to callback count1 for4096-byte sectors; each slice calls the same57E88, loses its status and reuses the same buffer.3B552..568 advances bookkeeping. There is no separate end-to-end physical checksum/count signal. Because no concrete stronger invariant exists, no multi-sector repetition/fault experiment was pursued. b13-0803b27c.asm (local-only reference: `builds/phase53-existing-read-final-decision/b13-0803b27c.asm`; not distributed).

The established TEF/missing-completion wait behavior is retained, not rerun. No physical/DMA fault was induced in Phase53. [findings.md](<../phase31-storage-error-recovery/findings.md>).
