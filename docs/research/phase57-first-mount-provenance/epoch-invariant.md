> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase57 — strict first-mount invariant

**STRONG INFERENCE — proposed policy:** initialize BOOT_EPOCH_STARTED before any relevant application constructor or task can invoke filesystem code. Only the expected first NOR mount root may moveBOOT/epoch0→MOUNTING/epoch1. Nested registration/stride-query/parse operations belonging to that same initial native call must be normalized, using actual caller/task provenance; another root, early unmount or unexpected mount sequence quarantines.

At complete successful return1AE06, require MOUNTING/epoch1, expected registered FS/binding and no unexpected-event bit. Copy canonical geometry and publishVALID last. Invalid parse/unsupported bounds/changed epoch gives no valid snapshot. No later successful mount may become an admitted replacement epoch; later geometry changes invalidate authorization and set terminal quarantine for this boot. This stricter policy intentionally avoids certifying a safeG2 after unknownG1 history.

HOST:request fixed geometry-only response→independently validate exact8 bytes/mapping/code/session→explicitly authorize target mask and exactepoch/digest. DEVICE:atomically compare epoch1/EXPORTED/unexpected=false, claimACTIVE, then submit only authorized fixed read(s). Geometry export alone never captures NOR; missing/invalid snapshot never starts a request.

If a geometry-changing event races admission, invalidation wins with0 new submits, or ACTIVE wins and the changer must refuse/defer **before** mutation. A queued/active read cannot be safely canceled by clearing a flag; existing H4 quarantine remains. Old host tokens cannot rearm after failure, reset or remount. Cross-boot transport session freshness also requires integration; a volatile epoch1 value alone repeats every boot.

**PROVEN abstract tests:**13 cases in epoch-model-tests.json (local-only reference: `builds/phase57-first-mount-provenance/epoch-model-tests.json`; not distributed) preserve deadline4999/5000,32-bit tick wrap, FAILED over late success, reservation refusal, duplicate rejection and identity/coefficient target separation. There is no new capture after an unexpected earlier or later mount event. All native event interception, first-root identity and queue-admission atomicity remain **UNKNOWN**.

## Primary question

Can the first accepted geometry snapshot be considered valid evidence about whether82000 was preserved since the beginning of this candidate boot?

**UNKNOWN.** The policy would establish that conclusion only after earlier mutation exclusion and complete guard placement are proved. Concrete unresolved operations are bootloader81000-read completion/consumer control beginning051C2, the10 global constructor subgraphs dispatched by5B978, and pre-Main Content/UI queue/callback ordering (22ACC/22AE4,1D680/1E4BE) before1D4C0. No actual earlier mounted epoch or82000 mutation has been demonstrated. An exactly matching later epoch number cannot substitute for that missing history.

## Independent target gates

|Target |Intended raw admission |Current status |

|---|---|---|

|82000..821FF |First-epoch validated mapping, no pre-snapshot target mutation, same epoch/session, no bypass writer |UNKNOWN; disabled |

|81000..81016 |Shared prerequisites plus distinct identity-history authorization |UNKNOWN; independently disabled |

Identity erase[81000,82000) does not touch82000. Coefficient-only target mask2 does not require identity predicate; existing combined command must be adapted/tested before such a mask is usable. Required coefficient bytes still come from a later fixed physical read, not from geometry. No arbitrary address is accepted and no hardware action occurs.
