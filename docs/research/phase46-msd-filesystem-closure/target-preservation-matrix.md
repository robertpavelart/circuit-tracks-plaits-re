> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase46 — separate target decisions

Rows concern the restricted T0–T7 sequence in [boot-to-capture-mutation-timeline.md](<boot-to-capture-mutation-timeline.md>). `NO WRITE PATH` is scoped to the specified producer, not every concurrently running task. `UNKNOWN` means its complete target exclusion has not been proved. No target-changing ordinary-boot execution was demonstrated. Conditional capabilities outside this window are listed separately.

## A — identity `[81000,81017)`

| Stage | Classification | Confidence / exact reason |
|---|---|---|
|Installation |NO WRITE PATH |PROVEN in saved chosen transition: highest metadata erase ends exactly81000. |
|Bootloader |UNKNOWN |Registered setter05DB4 does write this sector, but needs explicit identity-edit input excluded by policy. Known read/constructor does not write it; full boot scheduling/client exclusion is not a new whole-boot proof. |
|Cold boot |UNKNOWN |Repeats application filesystem startup; wrap protection not globally enforced. |
|Application startup |UNKNOWN |2CFB8→2D060 invalid nonempty type0 record can request deletion+sync; actual FAT destinations not qualified. |
|Idle |UNKNOWN |Settings subscriber2D278 may invoke save2D2AC and cache sync; real dirty/allocation predicates unclosed. |
|USB enumeration |NO WRITE PATH |STRONG INFERENCE for ordinary control enumeration from reviewed descriptor/class routes; filesystem concurrency remains in its own rows. |
|MSD |UNKNOWN |PROVEN ordinary initialized WRITE10 rejects via57E48; full malformed-BOT continuation/CBW state invariant not exhaustively established. Direct lower mode3 callback can reach81000. |
|Filesystem |UNKNOWN |Accepted synthetic FAT32 + native f_write can emitFFFAD, which native drive0 mapper wraps to81000. Actual unit metadata/path not demonstrated. |
|Background persistence |UNKNOWN |Known custom persist19 resync is RAM/DSP; stock settings/cache producer destination proof incomplete. |
|Diagnostic command |NO WRITE PATH |PROVEN scoped fixed READ path; RAM byte14 normalization is not evidence-sector modification. |

**Final identity preservation: UNKNOWN.** Explicit identity setter is an additional target-specific capability, not an asserted automatic writer. Registration, cached identity validity and USB serial formatting do not by themselves prove physical overwrite.

## B — coefficient prefix `[82000,82200)`

| Stage | Classification | Confidence / exact reason |
|---|---|---|
|Installation |NO WRITE PATH |PROVEN in saved chosen selector0 transition; staging and80000 metadata erase/program exclude82000. |
|Bootloader |UNKNOWN |Reviewed named update/identity paths exclude82000; complete ordinary-boot computed-client closure remains weaker than a whole-boot theorem. No identity-only uncertainty is used as the critical blocker. |
|Cold boot |UNKNOWN |Repeats unqualified filesystem startup/mount/cleanup. |
|Application startup |UNKNOWN |Automatic settings cleanup can reach internal FAT mutation; accepted volume geometry need not be physically bounded. |
|Idle |UNKNOWN |Actual settings dirty/subscriber/cache/restore destination state unclosed. |
|USB enumeration |NO WRITE PATH |STRONG INFERENCE for ordinary enumeration; no reviewed class setup directly programs the target. Concurrent filesystem routes classified separately. |
|MSD |UNKNOWN |PROVEN state0 WRITE10 protection; full hostile-BOT invariant incomplete. Mode3 lower callback can address82000 directly, default mode's physical out-of-array behavior not assumed. |
|Filesystem |UNKNOWN |Accepted synthetic geometry + native f_write emitsFFFAE; native mapper wraps to82000. No actual unit allocation or automatic overwrite demonstrated. |
|Background persistence |UNKNOWN |Stock file mutation producers are not globally excluded; custom SC35D8 RAM/DSP resync alone has no such write. |
|Diagnostic command |NO WRITE PATH |PROVEN scoped fixed raw READ only; failure containment does not repair earlier mutation. |

**Final coefficient preservation: UNKNOWN.**

**Before the first diagnostic capture request, can any reachable path in the planned sequence write or erase any byte of82000–821FF? UNKNOWN.** The concrete unresolved chain is:

`0801FAD4 → settings constructor0802CFB8 → startup0802D060 → conditional DELETE0803C97A/op5 + flush0803CC54 → Storage content worker → internal volume/file/FAT mutation → disk0801A7AC → NOR mapper0801AF1E → WRITE24164 → worker/backend → program/erase`.

Also retain settings subscriber`0802D278 → changed predicate0802D300 → save0802D2AC → 0803C920/op7 + flush` and filesystem cache/directory/FSInfo destinations`0801859A/08018612/0801A010`. The missing facts are accepted actual mounted geometry/allocations and complete startup/dirty predicates, not an unresolved name for the physical medium. Drive0's physical NOR binding is proved.

**PROVEN conditional WRITE PATH outside ordinary input policy:** whole-NOR lower MSD callback, explicit resource update selectors and factory erase can affect both targets. Identity setter writes23 bytes81000 and erases`[81000,82000)` only; that identity-specific capability does not overlap coefficient prefix82000. If coefficients were actually overwritten, their bytes cannot automatically count as original evidence; payload provenance would need separate proof.

Evidence: [filesystem chain and countermodel](<filesystem-lba-binding.md>), [persistence roots](<persistence-routes.md>), [MSD admission](<msd-reachability.md>), native cases (local-only reference: `builds/phase46-msd-filesystem-closure/native-cases.json`; not distributed), [Phase45 preserved installation evidence](<../phase45-nor-mutation-closure/update-noop-review.md>), identity setter listing (local-only reference: `builds/phase46-msd-filesystem-closure/app-08025228.asm`; not distributed).
