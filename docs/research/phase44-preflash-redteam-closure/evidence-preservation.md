> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: SUPERSEDED / DO NOT FLASH.

# Original-evidence value after candidate installation

The two requested regions have different preservation evidence. “PROVEN” below is scoped to exact code/recorded offline paths, not physical NOR history or an unseen cold-boot suffix. [Static census](<nor-write-erase-census.md>) and its authenticated byte listings establish available mutation mechanisms. The Phase44 exact B1.3/rollback/recovery reports must be read alongside this note; Phase43 selected replay alone does not establish B1.3 update compatibility.

**PROVEN:** the Phase44 B1.3→original candidate summary (local-only reference: `builds/phase44-preflash-redteam-closure/b13-to-candidate-summary.json`; not distributed) now authenticates selector 0 base 0 capacity `$80000`, metadata program `[$80000,$80017)`/erase `[$80000,$81000)`, staged hash equal to original candidate, and actual native installer entry. Both targets have zero direct program/erase overlap in that selected exact-B1.3 model. This closes the previous *updater-image identity* gap for that transfer, not complete cold-boot producer closure.

**PROVEN:** the static listings here identify the original Phase43 BIN hash. Phase44's separately proven SUCCESS/quarantine race requires a minimal candidate correction; mutation-body equality for a corrected candidate must be established separately before reusing these bounds for that new artifact. No unchanged original artifact should be described as the corrected test candidate.

## Identity/settings: `[$81000,$81017)` — 23 bytes

**PROVEN:** ordinary identity load `$08005D98` reads 23 bytes into `$2000546C`, then `$08005DB0` zeroes **RAM** byte 14. Application equivalent `$0802520C` reads into `$20006868` and `$08025224` zeroes RAM byte 14. These stores do not rewrite external NOR. The diagnostic reads the physical NOR region afresh; it does not dump that normalized cache.

**PROVEN:** mutation is supported: boot setter `$08005DB4` and app setter `$08025228` write the full 23-byte cached record with erase-first=1. Their fixed erase sector is `[$81000,$82000)`. The first 14 bytes may be changed by the native identity SysEx command; cache byte 14 is then zero, so a setter can erase an originally nonzero physical byte 14. App `$080252F8` restricts mutation to a valid new 14-character identity when the old cached identity is invalid; the boot handler has a different, less restrictive predicate. Do not assume identical setter admission rules across images.

**PROVEN in Phase43 selected update model:** metadata program `[$80000,$80017)` and erase `[$80000,$81000)` do not overlap this region; the nearest erase is adjacent, gap 0. The closest program ends 4073 bytes before it. Diagnostic operation 1 reads do not mutate it. This is not a whole-boot mutation census.

**STRONG INFERENCE:** absent a setter invocation, chip erase, or another generic storage mutation, a post-install raw capture represents the pre-experiment physical 23 bytes. **UNKNOWN:** unconditional identity preservation through all first-boot, maintenance, B1.3 persistent and recovery conditions. It must be archived as “post-candidate-install raw capture,” with transfer/build hashes and timing/context, not labelled an independently proven untouched pre-experiment identity dump.

## DSP coefficient resource: `[$82000,$82200)` — 512 bytes

**PROVEN:** this is separate from identity and update metadata sectors. Identity erase ends at `$82000`, with no overlapping byte. Normal app staging selector 0 has capacity `$80000`, while selector 2 starts `$82000` with capacity `$12000`. The actual Phase43 candidate selected-update replay records no writes/erases to the target; nearest write `[$80000,$80017)` is 8169 bytes away, nearest erase `[$80000,$81000)` has 4096-byte gap. Exact B1.3 transfer results are separately required, not inferred from this earlier run.

**PROVEN:** known table initialization consumes the resource read-only: `$08035E28→$08047C6C→$08024130` reads 512 bytes at `$82000` into `$20005148`, then `$08035EEE→$0802968E→$0803BA78` transmits 256 16-bit values to DSP X:`$0C00–$0CFF`. This is the missing authentic input to the stock DSP initializer/reclaim study ([provenance qualification](<../../../notes/p0282-0386-reclaim-qualification.md>)). It is not an identity record and not DSP external SDRAM.

**PROVEN:** the diagnostic adds no mutation; its eight 64-byte reads reconstruct exactly the resource prefix only after complete validation. Native stock facilities *can* destroy it: selector 2 resource update is directed to its containing bundle; whole-chip erase is reachable from stock command `$77` plus two `$CF525EB4` arguments in boot recovery and both applications. The exact capture request does not call these paths.

**STRONG INFERENCE:** preservation of these 512 bytes is stronger than identity preservation for the intended normal app install/capture sequence: identity setters cannot overlap it; the traced initializer only reads it; fixed capture only reads it; normal selector 0 updater footprints stop below metadata/identity/resource boundaries. Thus an authenticated post-install capture is useful evidence for the coefficient payload, with its post-install provenance stated.

**UNKNOWN:** no fresh physical pre-install hash exists, and the complete boot/persistent client graph is not closed by static direct-call scans. Therefore byte equality to the pre-experiment physical content is not unconditional PROVEN. Neither absence of a background write in a bounded replay nor hardware-tested transport proves global original-evidence preservation. The critical remaining offline proof is the normal boot-to-capture mutating-request address closure; do not silently merge that with transfer-only zero-overlap.

**UNKNOWN — offline blocker:** the unclosed normal boot/persistent producer predicates are an E 2/E 3 original-evidence preservation issue, not merely an acceptable hardware-only timing unknown. A complete “every reachable mutation callsite” claim and unconditional preservation admission are not justified by this census. Fixing the terminal-state race does not close this independent gap.

## Interpretation and stop conditions

**PROVEN:** genuine successful capture must produce both exact-length files atomically, 535 bytes total, with hashes and candidate/transfer provenance. Synthetic fixtures are not original device bytes. Any TEF/timeout/malformed stream must discard all partial output, keep the post-send marker burned, and require full power cycle; H4 remains FAIL for in-session unwind.

**UNKNOWN:** full physical cold-boot behavior, device-specific storage history, supply interruption and NOR identity. No hardware was accessed and no guarantee of permanent recoverability follows from this audit. A successful post-install 512-byte capture can resolve the missing initializer input only after authentication and offline replay; it does not itself qualify P-memory reclamation or authorize a Plaits port.
