> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase49 — existing current-B1.3 geometry reader

**PROVEN:** the known hardware-tested CIRCUITS-HACKS rdiag ARM memory reader is absent from the exact published B1.3 dispatch hook. Reference release documentation explicitly says betas omit it. The original B1.3 prologue and stock dispatch are present; no literal rdiag signature occurs in the image (the latter is corroboration only). b13-inspection.json (local-only reference: `builds/phase49-existing-geometry-reader/b13-inspection.json`; not distributed); [b13-readonly-interfaces.md](<b13-readonly-interfaces.md>).

**STRONG INFERENCE:** none of the inspected, documented existing B1.3 interfaces supplies the required mounted internal filesystem record. Identity/mode/parameter/status and Components file reads do not constitute a geometry reader. USB capacity is fixed independent of BPB/window. **UNKNOWN:** universal absence of undocumented computed/virtual reader paths. Therefore this phase cannot qualify a safe installed read plan; it does not assert a fully enumerated negative theorem.

**PROVEN:** the needed46 bytes are three metadata spans, with a proven mounted-field layout; they are not a contiguous46-byte structure. Reserved sectors and cluster bounds are derived. BPB total sectors is absent and may only be a bounded range. Exact structure/lifetime/owner limits are recorded in [live-geometry-structure.md](<live-geometry-structure.md>).

**PROVEN:** an offline parser is complete. It accepted5 reference/model records and rejected24 bad/unsupported records; both target ranges lie outside normal writable domains in the reference snapshot. No result is relabeled as current-unit geometry. [geometry_parser.py](<../../../builds/phase49-existing-geometry-reader/geometry_parser.py>); parser-tests.json (local-only reference: `builds/phase49-existing-geometry-reader/parser-tests.json`; not distributed).

**UNKNOWN:** current-unit mounted geometry, coherent live status and a supported CURRENT B1.3 acquisition path. The earlier storage-preservation blocker remains. No new diagnostic, firmware, install plan, hardware access, MIDI port opening or transmission was performed. Historical Phase48/pinned-reference integrity is checked in validation.json (local-only reference: `builds/phase49-existing-geometry-reader/validation.json`; not distributed).

Stop at the existing-reader boundary. Ordered minimal future evidence options, without initiating any, are in [minimum-read-plan.md](<minimum-read-plan.md>); safety classification is in [readonly-safety.md](<readonly-safety.md>). Existing geometry/status evidence first; then already acquired host-readable internal-volume evidence; then availability of a historically tested diagnostic command; only last a separately authorized temporary diagnostic.

CURRENT-UNIT GEOMETRY READER = UNQUALIFIED
