> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase56 — generation and volatile admission model

**STRONG INFERENCE:** reuse12 bytes as control32+payload64. Control holds phase3 bits, sticky history bit and28-bit mount generation. Phases:EMPTY,VALID,EXPORTED,ACTIVE,SUCCESS,FAILED,INVALID,UNSUPPORTED. Do not wrap the generation: exhaustion gives terminal FAILED. Reset also invalidates the transport session;28 bits alone is not a cross-boot token. A fresh host session must re-export geometry after every connection/boot boundary.

At initial normalized mount event:invalidate, generationG; collect/check/pack8 bytes; compare sameG and publishVALID last. Export returns exact scalars, generation and frame CRC; records are immutable through decision. Authorization is explicit, scoped to fixed target mask1(identity),2(coefficients),3(both), and carries the exported generation plus record digest and current host transaction token. Reject unsupported masks/addresses, nonEXPORTED state, stale generation/digest, history taint or failed ownership.

At accepted authorization, atomically transitionEXPORTED→ACTIVE before any raw read/queue submit. The8 payload bytes may then become target/session/chunk/owner/start-tick bookkeeping; geometry is no longer exportable. Timeout/success/failed terminal publication must preserve the old one-shot ownership/quarantine semantics under this new encoding. A remount writer that loses the admission race must be rejected/deferred **before** it changes geometry or initiates persistence; it cannot merely increment a generation after the raw operation is queued.

**PROVEN in abstract model:**7 scenarios and4 event insertion positions reject stale generation/digest, keep identity authorization separate, fail closed on generation exhaustion and serialize ACTIVE versus geometry mutation under the stated interception assumptions. [lifecycle.py](<../../../builds/phase56-geometry-snapshot-lifecycle/lifecycle.py>), lifecycle-tests.json (local-only reference: `builds/phase56-geometry-snapshot-lifecycle/lifecycle-tests.json`; not distributed). It is not native queued I/O proof; no real read occurs.

## Historical preservation correction

**PROVEN logical counterexample:** epochG1 may have unsafe geometry and mutate82000 before the host decides; a subsequentG2 safe mount and perfectly matchingG2 authorization cannot recover original coefficients. Fresh generation prevents using a stale *current* layout, but does not prove the evidence survived *earlier* layouts. This is a reasoning counterexample, not an induced normal firmware overwrite.

**STRONG INFERENCE — smallest conservative repair:** any post-initial geometry-changing event sets a sticky unqualified-history bit for the rest of the boot. Successful new mount may capture new bytes, increment generation and set current geometryVALID, as requested, but **raw_capture_allowed remains false** because earlier-history preservation is not certified. New geometry may still be exported for diagnosis. Clearing the bit on a successful remount would be unsound. Supporting safe raw admission after multiple epochs would require a qualified cumulative history proof or prevention of persistence under every unapproved epoch; neither is implemented.

Nested registration/stride-query/parse events within one initial mount transaction must be normalized so they do not falsely indicate an earlier usable filesystem epoch. **UNKNOWN:** native event normalization and every required pre-mutation hook. Even a conservative policy that rejects every later event must be placed before every actual changer. It cannot be certified from the abstract state model alone.
