> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase51 — where error evidence is lost

| Layer | Return / failure behavior |

|---|---|

|Backend22F94 |**PROVEN:** start>=capacity returns1 at22F9E without DMA; semaphore0 returns2 at22FCC without DMA; otherwise37430 then semaphore release1BA12 and returns0 at22FD8. No length-out field and no TEF return branch. |

|NOR DMA37430 / wait37596 |**PROVEN:** completion wait has no returned error contract; loop requires software bit0. TCF IRQ22826 sets it; TEF-only does not. No NDTR-versus4096 check in37430 after wait. |

|Worker24014 |**PROVEN:** stores backend return byte in wrapper+18 at240C4 and clears sync when drained. |

|Wrapper24130 |**PROVEN:** returns saved status byte at24160. Error is not lost here. |

|MSD57E88 |**PROVEN:** first loss at57ECE, immediately after57ECC call: unconditional branch to filter, no test/save ofR0;57EEE overwritesR0=0. No done-byte count forwarded. |

|SCSI/BOT |**PROVEN:** completed failures1/2 look like normal successful4096-byte data stages, CSW GOOD0, residue0; no new medium-error sense queued. |

Native sources: b13-08022f94.asm (local-only reference: `builds/phase51-msd-read-safety/b13-08022f94.asm`; not distributed); b13-08037430.asm (local-only reference: `builds/phase51-msd-read-safety/b13-08037430.asm`; not distributed); b13-08037596.asm (local-only reference: `builds/phase51-msd-read-safety/b13-08037596.asm`; not distributed); b13-08022826.asm (local-only reference: `builds/phase51-msd-read-safety/b13-08022826.asm`; not distributed); b13-08024130.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08024130.asm`; not distributed); b13-08023f68.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08023f68.asm`; not distributed); b13-08057e30.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08057e30.asm`; not distributed); read-cases.json (local-only reference: `builds/phase51-msd-read-safety/read-cases.json`; not distributed).

**PROVEN native failure tests:** busy0 semaphore and capacity-mismatch bounds rejection each run with two prior buffer contents. They return2/1 through native backend→worker→wrapper, yet host data length4096 and successful CSW are unchanged. The valid D4000 address in a correctly configured32MiB backend is not a bounds failure; that case deliberately lowers the fixture capacity to test propagation, not to claim normal firmware config is wrong. Busy reachability under actual scheduling is **UNKNOWN**, but the native return contract and caller behavior are proven.

**PROVEN prior fault-model results:** Phase31 TEF/missing completion leave Storage waiting, semaphore held and request active; no successful wrapper return, so the new 'lost-return' cases must not be conflated with a TEF return1/2. **STRONG INFERENCE:** the same size-independent wait predicates apply to4096-byte MSD reads. **UNKNOWN:** actual4096-byte silicon TEF/DMA state, incidence, and whether independent errors always suppress TCF. Earlier44-assertion/six-fault evidence is reused, not rerun or relabeled as a new MSD fault reproduction. fault-replay.json (local-only reference: `builds/phase31-storage-error-recovery/fault-replay.json`; not distributed); [findings.md](<../phase31-storage-error-recovery/findings.md>).

**UNKNOWN physical completeness:** hypothetical partial DMA followed by a modeled37430 completion-return is accepted by upper layers. This is not proof real TEF produces a successful partial response. It demonstrates the software checks above37430 cannot independently establish DMA completeness; firmware's native wait observes a controller bit, not a checksum of the returned sector.
