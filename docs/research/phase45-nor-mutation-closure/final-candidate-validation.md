> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Final-candidate validation gate

**UNKNOWN — Phase45 final admission is withheld.** Section9 of the request permits full corrected-candidate validation only after the preceding preservation/reachability gates pass. Those gates have not passed. No Phase45 final hardware candidate is designated, no new candidate is generated, and the old Phase43 candidate is not modified.

## Existing evidence retained, not relabelled

**PROVEN in recorded offline scopes:** Phase44 already independently decoded the produced corrected SYX, checked framing/product/block count/size/MPEG-2 CRC/BIN equality and bounds; compared its limited byte changes; ran actual B1.3 update, both rollbacks and bootloader-owned recovery; swept fixed diagnostic admission and arbitrary-address rejection; and exercised native capture/host acceptance. Phase45's saved independent atomicity review separately decoded actual disk SYX without the patch emitter and classified every differing byte.

Those results remain valid evidence unless invalidated. They are not a new complete Phase45 qualification, nor proof that all ordinary boot/background writers are excluded. Repeating them would not close the new MSD-mode/filesystem obligations, so completed tests were not restarted.

| Required item | Strongest current status |
|---|---|
| Framing/product/block sequence/size/CRC/decoded BIN | Existing Phase44 qualification plus independent Phase45 file review, **PROVEN scoped** |
| Bounds/bootloader/options/DSP delta | Existing limited diff and application-only installation proof; no new candidate delta |
| Fixed-address/read-only command/no arbitrary host address | Existing final-SYX native admission/Storage tests, **PROVEN scoped** |
| Exact install/B1.3 updater/rollbacks/own recovery | Existing selected native traces and saved dependency review, **PROVEN scoped** |
| Whole boot/background target preservation |**UNKNOWN**, not completed by the above |
| Final pre-flash designation |Withheld pending complete offline closure |

## Historical identity versus a final designation

OLD PHASE43 CANDIDATE: **SUPERSEDED — DO NOT FLASH**. Preserve it as evidence; do not delete/overwrite it.

The separately corrected `N44ATM` artifact remains an **offline research candidate**, not the FINAL PRE-FLASH HARDWARE-TEST CANDIDATE. Its reproducibility identity remains in Phase44 atomic-candidate-identity.json (local-only reference: `builds/phase44-preflash-redteam-closure/atomic-candidate-identity.json`; not distributed). No old hash is reused for it. No new final-candidate identity is issued in Phase45 because the conditional designation gate is not satisfied.

Image length/headroom remain the previously established375948 bytes /82804 bytes; logical application end0806BC8C. Actual fresh-boot RAM headroom and physical recovery remain distinct questions. Only bootloader entry/exit has now been manually reported by the user, not rollback flashing.

After the reachability gates pass, perform the requested file-first full admission using the exact produced corrected SYX and retain a separate final validation record. Until then, updating a README to imply hardware readiness would be false.

Evidence: Phase44 validation (local-only reference: `builds/phase44-preflash-redteam-closure/validation.json`; not distributed), independent persisted review (local-only reference: `builds/phase45-nor-mutation-closure/independent-atomicity-review.json`; not distributed), [preservation gates](<target-preservation.md>).
