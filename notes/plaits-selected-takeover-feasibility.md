> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase20C6 — selected-generator takeover feasibility

2026-10-07. **UNRESOLVED takeover ownership; comparison SELECT-A.** This is a
bounded selected-object/dependency study, not another global writer audit or
proof that takeover can never work. No code/math/firmware changes or DSP execution.

## Seven-word candidate result

Nominal selected objects: descriptor X[EB,F3), event/coefficient X[57A,5C4),
control Y[11F,17F), sample Y[59F,5C7), nominal kernel X[1960,196C) and reset
mirror Y[1960,196C). Kernel calculations extend beyond the nominal pointer:
P3B5 N2=90hex;3BB advances R2=kernel+90hex;3BF reads kernel+120hex;
3C2 writes a data-dependent number of coefficient words. P97B reads kernel+
144decimal. For slot0, current coefficients begin X19F0, source X1A80;
lane bases advance4. Their exact complete runtime extents are UNRESOLVED.

The export labels each nominal/scoped word and preserves UNKNOWN semantics.
GENERATOR-ONLY describes local use, not producer closure, selected exclusivity
or freedom from auxiliary dependencies. Active post, allocator, mailbox,
timestamp and ramp words cannot be surrendered merely because they are nearby.

**84 selected generator-associated candidates,0 qualified.** First7 X[57B,582)
are lane0's active record prefix. Replacing them requires suppressing preparation
and consumers in both passes, then obtaining original lane0's auxiliary input
another way. No such equivalent source is established.

## Smallest retained sub-generator currently supported

VERIFIED combiner:

- P9C8: A receives lane0*c0.
- P9C9: B receives lane1*c1.
- P9CA: parallel store sends the *pre-add* A to X2C02; A then adds B.
- P9CD: X2C24 receives that first-two-lane sum.
- Remaining body forms mono from further lane/coefficient/nonlinear terms.

Thus exact original auxiliary0 needs original lane0; auxiliary1 also needs
lane1. Their two request/lookup/completion sources must remain unless a new
equivalent producer is proved. Synth terminology and independent side-stream
semantics are not inferred beyond these calculations.

Natural X2C66 depends on phase generation outside the combiner. On the selected
three-lookup-lane witness it is the most recent applicable lane/repeat phase
store, reaching2C66 at sample16 of the interleaved tracks. The final mono32
store ends before2C66. Other classes can leave different natural history, so a
universal guard value or simplified all-mode producer was not invented.

**CONDITIONAL thinning:** retain complete lanes0/1 for auxiliaries and a third-
lane phase/guard slice. Lane2's record starts X597. Fields2..9 feed the inspected
repeat/selector/flags/product/phase/base/correction path (7C8,7D0..7E9). Fields
0,1,10..13 might be omitted by a correctly rewritten phase-only path:
X597,598,5A1,5A2,5A3,5A4 — six record words. Alternate classes, preparation/reset,
loop/cursor progression and external writers remain unclosed. This is not a
maximum reclaimability theorem. A seventh kernel word needs its own dynamic
writer/reader and other-slot proof. The nominal12-word stride is insufficient.

Feeding new Plaits-derived lane/auxiliary values is conceivable but changes
the selected auxiliary contract. It needs explicit guard/post/normalization
validation; it is not established by bit-exact standalone mono output. No zeros,
duplicated mono or fabricated guard were admitted as a shortcut.

## Scheduling and local-protection limits

Both77F entries have distinct pass semantics. Request publication sets pending
bits and queues addresses; completion clears scratch, consumes worker results
and commits selected phase. Some alternate phase paths commit during request.
The79B outer loop,7C8 inner count,979..99D cursor correction, request exit9A4,
completion ramps9A5..9B8 and Y7/R4 post cursors need exact retained effects.
Three gate anchors387/79D/9B9 do not form a complete finite patch specification.

A gate at early77F can inspect incoming Q and descriptor bank, subject to exact
ABI/flags proof. The late R4=5AB discriminator cannot be used there unchanged:
early R4 points to sample S=59F. Both passes and nonselected fallback must be
covered. Skipping everything is not a scheduling/auxiliary preservation proof.

Even after selected writers are disabled, arbitrary service/cache/paged writes
to reclaimed history cannot be tolerated while promising exact cross-block
state. Ignoring a write semantically is not ignoring its memory mutation;
overwriting it with a new seed loses phase/history continuity. SHI must guard
actual per-word addresses. Table-driven RMW must avoid the protected read as
well as commit. DMA/foreign write domains and safe appended code/save storage
are still needed. No material whole-policy reduction for B has been proved.

The existing stock trigger resets phases and envelope/filter subsets; it does
not initialize the seven Plaits values. Reusing it as a no-flag initialization
event would need a defined one-time ownership transfer and subsequent producer
exclusion. Reinitializing on every note is a new lifecycle contract. Frequency0
can only be a sentinel after an owned clear is proved, not arbitrary RAM or
service writes. No additional flag was silently introduced.

## Register and readiness result

At the comparable retained-combiner return9D9, A and B have the same post
continuation. Explicit liveness checks find R0 redefined, R4 live, A locally
redefined9DD, and incoming A slices visible to IRQ save168/16A/16C. Remaining
caller/all-mode deadness is not closed. Retain26 raw saved words; no smaller
B set or minimum universal set was established. An earlier takeover entry is
a different unqualified ABI, not permission to import the same liveness result.

B's high-X renderer is cheaper than P-state, but the required local bypass/
auxiliary/guard/scheduling/foreign-protection implementation is unknown. Its
740P comparable constituent subtotal and8461.54 mean/14341 max-style partial
wrapper projection exclude these costs and retained/removed stock work. They
cannot establish total size, deadline or superior containment. A wrong shared
gate, invalid count/pointer interpretation or queue mismatch can escape the
selected path. No locality guarantee follows from intent.

**B is not selected now. A is preferred conditionally** because the current
verified auxiliary/guard/post contract can be retained unchanged. This is not
a universal impossibility result for B. Detailed component comparison and
next-phase gate: `plaits-architecture-selection.md`. Offline patched image NO;
flashing NO; device stays unopened; no next-phase implementation.
