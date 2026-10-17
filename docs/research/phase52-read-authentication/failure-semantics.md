> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase52 — returned bytes versus physical outcomes

**PROVEN saved evidence:** authentication-experiment.json (local-only reference: `builds/phase52-read-authentication/authentication-experiment.json`; not distributed) stores exact first512 returned bytes as `returned_512_hex` in each trace, complete4096-byte hashes, command LBA, prior-buffer hash, refresh length and CSW status. Common synthetic vectors are included; all vector bytes after offset511 are zero. No transcript is an actual-unit sector. A timeout records `returned_512_hex=null`, not an invented zero USB reply.

| Outcome | First512 bytes / full USB response | Meaning |

|---|---|---|

|A complete success model |Exact source512,4096 bytes, GOOD |**PROVEN** native path under physical-completion seam |

|B no DMA bytes, completion nevertheless returned |512 zeroes,4096 bytes, GOOD |**PROVEN** fault-model result; native source of false completion **UNKNOWN** |

|Native early bounds/busy1/2 |512 zeroes,4096 bytes, GOOD |**PROVEN** Phase51 native status results, reused; not newly injected as TEF |

|C n prefix bytes, completion returned |source[0:n] plus zero tail;4096 bytes, GOOD |**PROVEN** model for0<=n<=512; not silicon fault reproduction |

|D timeout / partial128 then timeout |No data stage or CSW; active wait remains |**PROVEN** modeled stop at physical boundary; no subsequent command issued on that Model |

|E stale completion, no new DMA bytes |Zero-filled response, indistinguishable fromB |**PROVEN** upper-path behavior; actual stale notification/IRQ producer **UNKNOWN** |

The unread portion is deterministically zero under the tested clear/prefix/serialized-completion model. Prior target/control/poison is not retained. **UNKNOWN:** unread contents under late concurrently active DMA or USB ownership violations. Prior Phase31 TEF/missing-completion cases wait indefinitely, not return a success status; those are not reclassified asB/E. [findings.md](<../phase31-storage-error-recovery/findings.md>); [read-error-propagation.md](<../phase51-msd-read-safety/read-error-propagation.md>).

**PROVEN:**18 independent modeled fault placements cover T1,C1,T2, including no-byte/partial128/partial512/stale-completion/timeout/partial-timeout. Timeout sequences stop immediately and never retry a live request. Native early-return error tests are reused rather than repeatedly disturbing held ownership. Physical partial-completion hypotheses are labeled throughout.

Replay distinctions: replaying the immediately preceding control intoT2 fails target equality/BPB. A hypothetical older, internally valid target substituted for bothT1/T2 passes all host comparisons against a different valid control. That is an observational ambiguity at the physical-data seam, **not proof a native firmware cache replays old BPBs**. Native reachability is **UNKNOWN**; do not infer wrong current geometry was observed. authentication-experiment.json (local-only reference: `builds/phase52-read-authentication/authentication-experiment.json`; not distributed) `immediate_control_replay`, `older_target_replay`.
