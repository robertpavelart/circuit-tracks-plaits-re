# Plaits integration research

Current target: four melodic Plaits tracks, default mono, shared model code with independent per-track state, MAX_TRACKS_PER_MODEL=2 and MAX_POLY_TRACKS=2 globally, with engine-specific admission limits and eventual24-model scope. This is a design, not a hardware-qualified implementation.

The current candidate is a temporary NOR diagnostic and contains no Plaits engine. Authentic82000 evidence is still missing; P:0282-0386 reclaim and final safe P/X/Y budgets remain unqualified/UNKNOWN. See ../docs/PLAITS_RESEARCH_STATE.md and ../docs/MEMORY_AND_RESOURCE_STATUS.md.

`poc/` and `seam/` retain project-authored historical experiments, including VariableSaw and later dual-replacement/Modal work. Their per-experiment claims are not current global status. Upstream source code is fetched locally, not vendored here; `upstream/source-manifest.json` records revision/hash metadata. Preserve MIT notices in poc/LICENSE and source headers.
