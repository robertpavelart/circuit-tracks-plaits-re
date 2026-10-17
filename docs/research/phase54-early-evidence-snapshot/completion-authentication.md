> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase54 — internal read completion authentication

**PROVEN:** internal hooks have more visibility than the closed host-MSD interface. Wrapper24130 enqueues and waits; worker24014 publishes backend status at wrapper+18, then synchronization clears. Backend22F94 returns1 for bounds rejection and2 for semaphore acquisition failure, without a read. After37430 returns it releases the semaphore at22FD4 and returns0. Resource47C6C preserves that status; identity25220 also leaves it available at25222. The six native tests show that existing callers do not reject those failures. app-08047c6c.asm (local-only reference: `builds/phase54-early-evidence-snapshot/app-08047c6c.asm`; not distributed), reader-boundaries.json (local-only reference: `builds/phase54-early-evidence-snapshot/reader-boundaries.json`; not distributed), [findings.md](<../phase31-storage-error-recovery/findings.md>).

| Completion obligation | Available internal source | Result |

|---|---|---|

| IRQ |QSPI573E0→22826 acknowledgesTCF/SMF and sets controller softwarebit0;5756E→57664 wakes Storage mask100 |PROVEN stock completion predicate, not a whole-buffer integrity guarantee |

| Request status |Wrapper+18 and R0 at25222/35EE6 |PROVEN statuses0/1/2 are directly inspectable; must reject nonzero |

| Requested bytes |Identity23; resource512; QSPI DLR is length−1; DMA2 stream7 NDTR/M0AR registers400264BC/C4 |PROVEN configured/requested counts are available; UNKNOWN generation-matched terminal invariant |

| DMA setup |1C072 returns0 even when EN is already1 and skips fresh address/count setup |PROVEN selected native Phase52 behavior; UNKNOWN real incidence/reachability for these boot reads |

| Error accounting |QSPI selected read uses TCIE, not TEIE; DMA ISR acknowledges TCIF7/FEIF7, no backend error unwind |PROVEN insufficient explicit per-request error result |

| Destination completeness |Buffer bytes can be observed internally; no authenticated source checksum supplied |UNKNOWN from wrapper return alone; source bytes/CRC cannot be guessed |

Sources: [findings.md](<../phase31-storage-error-recovery/findings.md>), DMA-setup-cases.json (local-only reference: `builds/phase52-read-authentication/DMA-setup-cases.json`; not distributed), [completion-signals.md](<../phase53-existing-read-final-decision/completion-signals.md>). Phase53 is reused as saved evidence only, not reopened.

**PROVEN:** TEF-only/missing completion in Phase31 leaves Storage waiting, semaphore held and request/buffer active. A post-return hook does not run in that state. Thus two post-read copy hooks alone cannot guarantee the requested literal FAILED state on every physical failure. EMPTY/partial-valid with no BOTH/export remains safe containment, but is not an implemented all-errors→FAILED contract. A bounded error observer would be additional, separately qualified behavior; it must not force release, retry or add a Storage request. Watchdog feeding by idle does not guarantee a bounded reboot. [findings.md](<../phase31-storage-error-recovery/findings.md>).

**STRONG INFERENCE:** a suitable internal attestation can combine request identity/source/destination/count, fresh setup, latched completion/error observations and quiescent DMA with expected remaining count, then publish validity after copy and appropriate memory ordering. Merely sampling NDTR0 or a controller bit later is insufficient if stale, cleared, reused or detached from the current request. Capture provenance before native acknowledgements destroy it; do not clear flags from the copy hook. Cache/coherency and CPU-visible destination freshness must follow the existing qualified platform evidence and an actual hook contract, not an assumed host pattern.

**UNKNOWN:** a minimal complete fence is not yet implemented or replay-qualified for either original boot read. No trustworthy-completion proof is claimed for arbitrary synthetic success returns. Required next completion experiment: execute the actual read/IRQ/backend return path for23 and512 bytes with fresh/stale DMA setup, short transfer, nonzero backend status, TEF and missing completion; require each validity commit to imply the full correct synthetic destination and current request provenance. Reuse Phase31/52 results for unchanged paths; do not fabricate authentic unit bytes or perform an extra raw read.
