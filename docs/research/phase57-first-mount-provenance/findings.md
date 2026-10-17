> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase57 — first-mount geometry provenance

**UNKNOWN: first-mount provenance remains UNQUALIFIED.** The12-byte owner/lifetime reconstruction and strict first-epoch design are concrete, but they do not close reset-to-snapshot history or native coalesced-state liveness.

**PROVEN:** exact original12-byte region20044D70..20044D7B has no unused bytes.23 extracted accesses in the known owners show getter clears/magic, timeout,state/session/chunk/owner/tick and corrected terminal stores. Old magic stays live after boot; geometry cannot replace it without owner adaptation. [existing-12byte-ownership.md](<existing-12byte-ownership.md>), ownership.json (local-only reference: `builds/phase57-first-mount-provenance/ownership.json`; not distributed).

**STRONG INFERENCE:** coalesce control4+canonical geometry8, overlaying geometry with raw bookkeeping only after exact host authorization—not merely export. Preserve timeout/one-shot/FAILED ownership by adapting every old interpreter.13 strict-first-epoch model tests pass, but no new native owner implementation is claimed. [coalesced-state-layout.md](<coalesced-state-layout.md>), epoch-model-tests.json (local-only reference: `builds/phase57-first-mount-provenance/epoch-model-tests.json`; not distributed).

**PROVEN new startup detail:** application scatter initializes data below20003D02 and zeroes only through20006A54; constructor dispatch at5B958 follows, providing a specific early state-initialization opportunity. The10-entry relative constructor table is authenticated. Main's own prefix is identity→display/peripheral→explicit NOR mount, with no earlier Main mount. **UNKNOWN:** that this is the complete boot's first relevant epoch. Constructors and already-created Content/UI/Storage tasks require transitive queue/callback closure. [first-mount-provenance.md](<first-mount-provenance.md>).

**UNKNOWN — primary gate:** can the first accepted geometry prove82000 preserved since candidate boot began? No complete ordering proof exists. The saved genuine cold-boot replay stops at051C2 before81000 read completion; exact application obligations include constructor iterator5B978 and Content22ADA→22AE4/UI1D698→1E4BE before Main1D4C0. These are concrete missing operations, not invented destructive epochs. No automatic82000 write is demonstrated. [pre-first-mount-mutations.md](<pre-first-mount-mutations.md>), [epoch-invariant.md](<epoch-invariant.md>).

**PROVEN scoped:** completed selected selector0 install excludes both evidence sectors; later equal-header boot may skip internal install. **UNKNOWN:** complete A(first install boot) and B(later cold boot) reset-to-snapshot chains. Identity-only uncertainty does not veto coefficients: both remain unqualified because shared provenance/liveness gates are open. [install-to-first-mount.md](<install-to-first-mount.md>).

|Gate |Result |

|---|---|

|Original12-byte field ownership/timeline |PROVEN scoped known owners; global aliases UNKNOWN |

|Exactly12-byte coalesced state feasible |PROVEN model; STRONG INFERENCE native architecture |

|Native init/timeout/containment adapters |UNKNOWN, conceptual only |

|First Main explicit mount |PROVEN prefix order |

|First relevant epoch of full boot at1AE06 |UNKNOWN |

|No82000 mutation before accepted snapshot |UNKNOWN |

|No81000 mutation before accepted snapshot |UNKNOWN, separate identity policy |

|Asynchronous exclusion/physical mask latency |UNKNOWN |

|Complete reset-to-terminal state liveness |UNKNOWN |

|Same-epoch authorization interlock |PROVEN conditional model; native integration UNKNOWN |

**UNKNOWN — minimum remaining offline work:** close constructor/pre-Main producer roots and reserve/reset the private record before those roots; replay native getter/watch/admission/terminal adapters against existing one-shot ownership/fault cases without a firmware image. A new failed or unexpected mount must quarantine, never be relabeled “first.” No additional no-observed-write trace can qualify the primary history gate. [async-exclusion.md](<async-exclusion.md>), [state-liveness.md](<state-liveness.md>).

**PROVEN:** all9 requested reports and persisted evidence are present. validation.json (local-only reference: `builds/phase57-first-mount-provenance/validation.json`; not distributed) verifies historical/pinned inputs remain unchanged. Prior passing suites were not rerun; Phase53 remains closed. No firmware/SYX/candidate generation or modification, hardware/MIDI access or transmission occurred.

FIRST-MOUNT GEOMETRY PROVENANCE = UNQUALIFIED
