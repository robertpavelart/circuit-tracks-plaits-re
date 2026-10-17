> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase51 — stale, zero and partial data

**PROVEN:** READ10 uses40024000..40024FFF. Native57E88→1A7E4 clears the requested4096 bytes before any queue wait or physical read. Both an A5 poison fill and a previous complete valid BPB were seeded as prior contents in each case. Native early failures1/2 return a full all-zero sector, never those old contents. The lower backend alone leaves its destination unchanged on those early failures; the MSD caller's earlier clear makes that unchanged destination zero. b13-0801a7e4.asm (local-only reference: `builds/phase51-msd-read-safety/b13-0801a7e4.asm`; not distributed); b13-08057e30.asm (local-only reference: `builds/phase50-msd-readonly-geometry/b13-08057e30.asm`; not distributed); [read_cases.py](<../../../builds/phase51-msd-read-safety/read_cases.py>); read-cases.json (local-only reference: `builds/phase51-msd-read-safety/read-cases.json`; not distributed).

| New coupled cases (two priors each) | Returned data | Parser | Confidence/scope |

|---|---|---|---|

|Normal read model |4096-byte model BPB |passes structure |**PROVEN** native upper path; DMA bytes modeled |

|Native busy2 |4096 zero bytes, GOOD CSW |rejects signature |**PROVEN** native backend failure propagation |

|Native bounds1 |4096 zero bytes, GOOD CSW |rejects signature |**PROVEN** with capacity-mismatch fixture |

|Hypothetical128-byte DMA then completion-return |prefix plus cleared tail; no55AA |rejects signature |**PROVEN** model behavior; **UNKNOWN** silicon reachability |

|Hypothetical512-byte DMA then completion-return |complete BPB/signature, cleared tail |passes structure |**PROVEN** model ambiguity; **UNKNOWN** silicon reachability |

In the512-byte model the remaining3584 bytes of the normal test sector are zero, so a partial DMA and full transfer produce **identical returned4096 bytes and hash**. This is not a demonstrated incorrect BPB, nor a parser bug. It proves byte-only checks cannot attest the full physical transaction's completion. If all geometry-bearing bytes really came from the correct NOR address, those bytes can still describe correct geometry. Establishing that condition under physical faults remains **UNKNOWN**.

**PROVEN:** no previous-sector/unrelated-RAM contamination survives normal clearing in the tested sequence. **UNKNOWN:** concurrent buffer reuse, DMA writes after a failed/hung read, or physical corruption; these were not fabricated as observed failures. A hung TEF read may partially alter the buffer but does not reach ordinary USB data-send in the prior tested wait model. Do not re-use that active session.

**PROVEN:** existing Phase50 parser rejects zeroes, missing signature, wrong length and inconsistent geometry. New [acceptance_gate.py](<../../../builds/phase51-msd-read-safety/acceptance_gate.py>) preserves that structural rejection and labels every structurally valid candidate UNQUALIFIED for physical completion, rather than promoting a plausible sector into authenticated evidence. It cannot distinguish byte-identical partial/full histories; no parser can do so from those bytes alone. No firmware or historical parser is changed.
