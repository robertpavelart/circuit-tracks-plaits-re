> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Separate preservation gates

No authentic23/512-byte NOR payload was obtained. All new tests use synthetic data or intercepted Storage submission, and none accessed a device. All intervals below are half-open NOR byte offsets.

| Question | Identity[81000,81017) | Coefficients[82000,82200) |
|---|---|---|
| Boot/application read | Boot05D98→Storage read23; app2520C counterpart | App35E28→47C6C→24130 reads512 into20005148, then DSP upload |
| Specific writer | Boot05DB4/app25228 write23 and erase[81000,82000) | Resource selector2 update begins82000; generic mapped/whole-array writers also exist |
| Sector erase exposure | Own identity setter; whole-chip erase; whole-array MSD; mapped-write bound failure | Selector2; whole-chip erase; whole-array MSD; mapped-write bound failure. Identity-sector erase ends exactly at82000. |
| Chosen completed installation | **PROVEN scoped:** zero program/erase overlaps | **PROVEN scoped:** zero program/erase overlaps |
| Metadata adjacency |[80000,81000) erase is adjacent, gap0; write[80000,80017) gap4073 | Metadata erase gap4096; write gap8169 |
| First ordinary boot | Constructor reads and normalizes RAM; complete producer exclusion **UNKNOWN** | Known initializer read-only; complete mode/filesystem producer exclusion **UNKNOWN** |
| Normal idle | No spontaneous identity edit proved; callback/other-writer exclusion incomplete | Default storage windows safe, but complete mode and filesystem bounds **UNKNOWN** |
| Retained custom behavior | Custom resync narrowed to RAM/DSP; stock persistence still must be bounded | Same; do not assume every save is SD |
| Recovery | Identity-edit callback can rewrite record; factory erase can erase array | Factory erase/resource update can alter payload; selected official/candidate intake does not |
| Fixed diagnostic | Fresh raw read, no normalization or write | Eight64-byte raw reads, no write |
| Pre-experiment equality through full planned sequence | **UNKNOWN** | **UNKNOWN**, with stronger conditional preservation evidence |

## Critical82000 authenticity question

“If corrected diagnostic is installed over B1.3 and cold-boots before capture, can a reachable path have modified82000–821FF?”

**UNKNOWN for the complete intended ordinary-boot/background schedule.** No actual overwrite during that schedule has been demonstrated. Two exact unclosed obligations prevent answering NO:

1. USB MSD callback2000379C→08057EF4. Native mode3 maps block82 to82000 and requests4096-byte erase/program. Initialized mode1 maps above94000, but the complete mode invariant over24918/2492E, delayed callback248B4 and38C54 is not proved.
2. Disk0 file-write mapper0801AF1E. Valid NOR filesystem LBAs map aboveD4000. Out-of-range LBAFFFAE wraps to82000; all accepted filesystem/restoration/flush producers must be shown to bound LBA/count and preserve binding. Native mapper tests alone do not prove those values are reachable from a valid filesystem.

**PROVEN conditional YES:** deliberately selected resource-update, chip-erase or whole-array-MSD paths can alter82000 before capture. These are not part of the prescribed fixed update/capture command stream. If any actually ran, a later capture is the modified post-write resource; it cannot be certified as original coefficients. Whether it still serves initializer qualification depends on that writer's payload/provenance and the actual expected application resource version; this is **UNKNOWN**, not an automatic acceptance of arbitrary post-write bytes.

**STRONG INFERENCE:** completed selector0 update plus the known read-only initializer and fixed capture preserve the coefficient prefix if all other mutators are excluded. This conditional argument is stronger than identity's because identity setters cannot touch it. It does not satisfy the required exhaustive gate.

## Identity81000 gate

**PROVEN:** boot05DB0 and app25224 zero byte14 in RAM after reading; they do not themselves write NOR. A raw diagnostic therefore avoids cache normalization. Identity setters later write the whole23-byte cache with erase-first, including the normalized byte14. Boot/app edit admission differs; application requires an invalid old identity, while boot does not impose that same check. Both require their actual edit command predicates.

In addition to those dedicated setters, whole-array MSD block81 and mapped LBAFFFAD can address the identity sector under the conditions above. Complete pre-experiment identity equality is therefore **UNKNOWN**. Its separate semantic/provenance uncertainty need not by itself block82000; the shared MSD/file-mapping obligations genuinely affect both.

Evidence: [expanded graph](<nor-mutation-callgraph.md>), [background analysis](<background-write-analysis.md>), MSD results (local-only reference: `builds/phase45-nor-mutation-closure/msd-writer-review.json`; not distributed), mapped-write results (local-only reference: `builds/phase45-nor-mutation-closure/mapped-write-review.json`; not distributed), completed selected update dependencies (local-only reference: `builds/phase45-nor-mutation-closure/update-dependency-review.json`; not distributed), [Phase44 preservation](<../phase44-preflash-redteam-closure/evidence-preservation.md>).
