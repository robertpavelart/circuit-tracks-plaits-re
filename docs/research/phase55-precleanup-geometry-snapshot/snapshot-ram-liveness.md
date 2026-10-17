> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase55 — small fixed retention search

**UNKNOWN:** no small fixed destination is qualified. This conclusion comes from a new47/52-byte candidate analysis and actual owner review, not reuse of Phase54's535-byte requirement.

|Candidate |Ownership/liveness result |

|---|---|

|Extend existing heap-top reservation by52 |PROVEN proposed lower bound20044D3C; fixture cursor20044D68 is44 bytes above it. Existing limit20044D70 has8-byte headroom. Reservation at mount time would overlap prior allocation; reservation before constructors removes capacity later used in the fixture. Actual fresh demand remains UNKNOWN. |

|Compact47 bytes including one-byte state |PROVEN still exceeds8-byte fixture headroom by39; alignment/epoch/CRC would cost more. |

|Existing12-byte one-shot latch20044D70..20044D7B |PROVEN independently owned, too small for46 payload; still needed by separate raw capture. Cannot overwrite it with geometry. |

|Master FX state20044D7C..20044E57 |PROVEN220-byte live retained state. No newly proved padding46-byte slot. |

|Historical rdiag68-byte watch log |PROVEN aliases c_gst()+120 in the84-byte Master-FX LED buffer, not a separate allocation; showing Master FX repaints it. WATCH=False/retired log code does not retire LED ownership. Rejected. |

|probe35s14-word report area |PROVEN c_gst()+104, the same idle LED buffer; idle use is not boot-to-export liveness. Rejected. |

|Parser/DMA/filesystem sector scratch, Main/IRQ stacks |PROVEN excluded by the requested ownership contract; unused capacity does not grant retention. |

|FS metadata padding / existing live46 bytes |PROVEN original geometry is live filesystem state and not a retained pre-cleanup copy; small padding fields do not provide46 bytes. Rejected. |

|Other apparent static RAM gaps / split fixed records |UNKNOWN complete ownership and writer exclusion; no location selected on the basis of one dump. |

Evidence: inspection.json (local-only reference: `builds/phase55-precleanup-geometry-snapshot/inspection.json`; not distributed) (`RAM_candidate`); [heap-stack-status.md](<../phase45-nor-mutation-closure/heap-stack-status.md>); [findings.md](<../phase42-exact-rdiag-integration/findings.md>); rdiag.py (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/rdiag.py`; not distributed) (`LOG_OFF=120`, `LOG_N=8`, header describing repaint); probe35s.py (local-only reference: `C:/Proj SSD/CODEX/CIRCUITS-HACKS-RC-main/CIRCUITS-HACKS-RC-main/tools/probe35s.py`; not distributed) (SC14+104 report area); [live-geometry-structure.md](<../phase49-existing-geometry-reader/live-geometry-structure.md>).

**STRONG INFERENCE:** an explicit small reservation remains a plausible design if allocator demand can be reduced or a genuinely retired fixed owner identified. It must be initialized/invalidate before first mount, excluded from heap/task/DMA/audio/parser owners, guarded and traced through boot/USB/export, and never reinitialized by a lazy Master-FX getter after capture. Retained features must not be disabled to make the reservation appear available. No allocator is called by the proposed copy hook.

**UNKNOWN:** worst-case fresh-boot allocation/high-water and an exact nonoverlapping52-byte location. The dump overlap rejects the simple proposed address in that fixture; it does not prove that every possible small reservation is impossible. A separate52-byte epoch/CRC-capable design may need more than52. No candidate region has been written, claimed safe or incorporated into firmware.

**UNKNOWN — minimum next RAM experiment:** identify a statically retired fixed owner of at least52 bytes, or prove sufficient reclaimed allocation demand before reserving a named extent; then guard that extent across native constructor allocation, normal retained feature initialization, USB service and export. A fail-closed allocation refusal alone is insufficient for PASS if it prevents geometry acquisition on the intended boot.
