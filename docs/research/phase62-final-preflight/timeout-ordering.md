> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: FAILED / SUPERSEDED / DO NOT FLASH.

# Timeout ordering and one-shot boundaries

| Boundary | Value / interpretation |

|---|---|

| Device lifecycle |5000 unsigned clock ticks from active admission; wrap arithmetic covered by retained corrected native tests |

| Host pre-send preparation |10 monotonic seconds; failure before send transmits0 diagnostic messages and burns no marker |

| Host geometry |10 monotonic seconds from first attempted geometry transmission |

| Host authorization transmission |2 seconds measured around qualified driver send; driver's own bounded send remains in the pinned transport |

| Host raw stage/EOS |10 seconds from authorization attempt, including send; complete receiver still observes the absolute boundary for duplicates/trailing packets |

If the device counter advances at1ms/tick, its lifecycle deadline is nominally5s and precedes the10s host raw deadline. Physical scheduling/counter progress is unmeasured, so unconditional real-wall-clock ordering is **UNKNOWN**. Safety cannot depend on which fires first. Preauthorization device lifecycle timeout is inactive; host geometry timeout is not a device Storage cancellation.

The host creates/fsyncs its durable marker immediately before the first actual diagnostic send attempt; driver-send uncertainty counts asPOST_SEND. Marker-write failure before send removes only its own incomplete marker. No port/open/preparation failure sends SysEx or consumes a marker. Existing markers block a second launch before inventory/open. After any post-send failure there is no retry or cleanup command and the marker remains; physical power cycle is mandatory before any later attempt.

A successful workflow has2 diagnostic transmissions (geometry0E, authorization0F), not a capture retry. Geometry-only/unsafe stop sends1 and no raw authorization. Device capture contains multiple fixed64-byte chunks; these are parts of one authorized capture, not host resubmissions. Host failure cannot undo already-authorized device work and never attempts forced cancellation.

15 corrected-image ordinary/fault completion-order tests keep Main parked while the failed read request remains outstanding. **The separate TCF-before-DMA-release probe fails the unconditional no-return invariant**: native Main can return with DMA still configured for its former raw stack buffer. Do not cite the nominal deadline table or normal-model successes as closure of that issue. See [final-stack-audit.md](<final-stack-audit.md>) and dma-ordering-probe.json (local-only reference: `builds/phase62-final-preflight/dma-ordering-probe.json`; not distributed).
