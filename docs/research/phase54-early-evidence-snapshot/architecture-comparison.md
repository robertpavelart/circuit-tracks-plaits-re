> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase54 — architecture comparison

| Aspect | Current late-read diagnostic | Proposed early stock-read snapshot |

|---|---|---|

| Added NOR operations |One23-byte read plus eight64-byte reads |Zero, if copying both existing complete reads |

| Added Storage requests |Nine diagnostic reads |Zero for acquisition/export |

| Source preservation until host asks |Required |Not required after each accepted snapshot |

| Preservation before snapshot |Required |Still required;82000 stock read follows settings startup |

| Current-unit geometry |Needed to close prior normal-filesystem exclusion |Not eliminated for pre-82000-read persistence without a separate ordering/range invariant |

| H4 |Additional diagnostic wait/deadlock exposure |No additional diagnostic Storage deadlock; original boot reads still exposed |

| RAM |Existing64-byte temporary parser slice and12-byte latch |At least535 payload bytes plus validity/integrity metadata, fixed reservation unqualified |

| Boot changes |Dormant guarded late command |Two early copy hooks plus initialization/completion contract and fixed RAM reservation |

| USB |Qualified fixed23+8x64+completion transport |Same framing/TX lifetime reusable; source becomes retained RAM |

| Authentication |Qualified transport does not itself authenticate physical read |Internal state accessible but complete read-to-validity fence unqualified |

| Rollback/reset |Existing separate update/recovery assumptions |No new recovery proof; volatile evidence lost on reset |

Evidence: [stock-read-lifetimes.md](<stock-read-lifetimes.md>), [writer-ordering.md](<writer-ordering.md>), [snapshot-ram-liveness.md](<snapshot-ram-liveness.md>), [completion-authentication.md](<completion-authentication.md>), [late-export-design.md](<late-export-design.md>); existing transport: [findings.md](<../phase42-exact-rdiag-integration/findings.md>).

**STRONG INFERENCE — recommendation:** prefer a RAM-only snapshot/export architecture as the next design direction because it adds no NOR/Storage request and disconnects export time from acquisition time. **UNKNOWN — admission:** do not select it as qualified or designate a build now. The known82000 stock read follows startup settings handling; safe RAM and physical completion are also unresolved. These are independent obligations, not issues solved by reusing SysEx framing.

**PROVEN:** Phase53's supported-interface branch remains exhausted; this phase does not propose new repeated-read, poison-pattern or probabilistic authentication schemes. **UNKNOWN:** whether the copy-only existing-read strategy can meet the full pre-any-source-mutation requirement. First resolve the bounded startup-to-first82000 ordering/range exclusion; only if it passes should the fixed retention and completion-fence experiments proceed. No second raw read or broad new cold-boot peripheral emulation is proposed here.
