> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase57 — installation boot versus later cold boot

No new candidate exists. “Candidate” below refers to the historical corrected research image inspected read-only. A future first-mount adaptation would require a new offline qualification; these saved traces are not automatically its admission.

|Question |A: first boot after completed installation |B: later cold boot already installed |

|---|---|---|

|Prior staging |PROVEN named selector0 transfer overwrites all staged/metadata bytes subsequently read in saved model |Metadata/staging state inherited from previous successful boot; exact actual contents UNKNOWN |

|External update writes |PROVEN staged[0,5C000), metadata[80000,81000); neither target overlaps |No completed new upload assumed; do not automatically infer external metadata cleanup |

|Boot metadata handling |03B2A reads80000;03B9A checks selector/size/CRC/header |Same native validator; matching38-byte header can skip internal install |

|Stale but valid staged image |Selected completed transition does not depend on prior array bytes |Can be evaluated on boot. Compatible different compared header can reinstall internal image; equal header skips. This is a code capability, not a demonstrated rollback on this unit. |

|Evidence-sector mutation by reviewed installer |PROVEN absent in selected trace |STRONG INFERENCE same raw-read/internal-program structure; full boot dispatch closure UNKNOWN |

|Application pre-mount cleanup |PROVEN Main settings cleanup is later than intended NOR mount hook |Same Main order; all-task constructor/deferred closure UNKNOWN |

|Filesystem initialization before geometry |Reviewed mount reads/parses, not format; saved native8 cases add no writes |Same; actual-unit first-epoch provenance still UNKNOWN |

|Complete reset→accepted snapshot |UNKNOWN, authentic read boundary and startup/liveness gates remain |UNKNOWN, plus actual persisted metadata state is not newly acquired |

**PROVEN:** named updater/no-op/rollback results are preserved, not rerun.03BE4..03BF6 compares38 bytes at app+1C8..1ED; equal headers skip, different compatible headers install. A changed header is not a rule requiring a numerically higher build.80000 metadata is not relocated to81000. No automatic metadata-clear erase is proved merely because installation succeeds. [update-noop-review.md](<../phase45-nor-mutation-closure/update-noop-review.md>), [b13-updater-replay.md](<../phase44-preflash-redteam-closure/b13-updater-replay.md>), boot-08003b9a.asm (local-only reference: `builds/phase57-first-mount-provenance/boot-08003b9a.asm`; not distributed).

**UNKNOWN:** interrupted/power-cut uploads and arbitrary prior command histories are outside this normal completed-install sequence, not newly introduced attack scenarios. No safe physical recovery/rollback guarantee follows from the snapshot design, and no firmware transfer or restore is performed.
