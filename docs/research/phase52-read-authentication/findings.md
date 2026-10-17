> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase52 — read interleaving authentication

**Authentication answer: UNKNOWN.** The proposed finite read sequences have not qualified current-unit physical-read authentication. The single remaining ambiguity is whether native DMA/USB ownership and completion guarantee fresh, correctly addressed BPB bytes from the current command; repeated equality cannot establish that boundary by itself.

**PROVEN:**513 native coupled T2 prefix cases cover0..512. Every prefix shorter than512 is rejected;512 passes with all BPB bytes refreshed under the modeled contiguous-prefix assumption. The actual READ10 response remains4096 bytes, so this is not proof all4096 were refreshed. [partial-dma-exhaustive.md](<partial-dma-exhaustive.md>); authentication-experiment.json (local-only reference: `builds/phase52-read-authentication/authentication-experiment.json`; not distributed).

**PROVEN:** basic T1=T2 andT1!=C1 accepts a zero-returning control failure. A control header check rejects that case, but partial zero-tailed controls pass full-sector comparisons. Two-control/five-read sequence does not fix that. Immediate-control replay is rejected; an older valid target substituted twice at the physical-data seam passes. **UNKNOWN:** an actual native producer for that older-target replay; no incorrect physical-unit geometry is claimed. [control-sector-strategy.md](<control-sector-strategy.md>); [failure-semantics.md](<failure-semantics.md>).

**PROVEN:** new native DMA helper tests return0 without changing old address/count when EN is already1. This exposes the precise invariant still needed, not a hardware reproduction of a stale transfer. **STRONG INFERENCE:** a fault-free correctly serialized read could yield accurate geometry, and BPB/FAT/root checks offer corroboration. They remain secondary evidence. DMA-setup-cases.json (local-only reference: `builds/phase52-read-authentication/DMA-setup-cases.json`; not distributed); [cross-sector-consistency.md](<cross-sector-consistency.md>).

Seven requested reports and exact512-byte model transcripts are saved. Eighteen independent fault placements are tested; all six timeout/partial-timeout sequences stop without a subsequent request. Historical Phase51 and439 pinned reference sources are preserved; no hardware, MIDI, firmware generation/modification/transmission or new diagnostic occurred. Validation: validation.json (local-only reference: `builds/phase52-read-authentication/validation.json`; not distributed). No hardware plan is admitted: [authenticated-read-plan.md](<authenticated-read-plan.md>).

MSD PHYSICAL READ AUTHENTICATION = UNQUALIFIED
