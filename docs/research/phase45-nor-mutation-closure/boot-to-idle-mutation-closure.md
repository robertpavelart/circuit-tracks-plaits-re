> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Boot-to-idle closure

**UNKNOWN — required complete closure has not been established.** This report distinguishes qualified prefixes/selected transfers from a proof of all reachable producers. It does not present a no-observed-write replay as the requested result.

## Preserved boot evidence

**PROVEN scoped:** the authentic boot prefix reaches Main03A10→05D98, submitting a23-byte81000 read through the real queue/Storage worker/DMA. The prefix stops at051C2 with that read active; authentic payload completion is not supplied. First SVC, Idle→Main PendSV and native SysTick/Storage transitions were qualified in their earlier scopes. Complete application USB/project-restoration idle was not reached by those proofs. See [Phase38 findings](<../phase38-nor81000/findings.md>), [Phase37 findings](<../phase37-systick/findings.md>), [Phase39 boundary](<../phase39-nor81000-symbolic/findings.md>).

The corrected diagnostic changes only its marker and terminal commit. Bootloader bytes remain the authenticated original. That supports reuse of unchanged prefix analysis; it does not transform a blocked prefix into completed corrected-candidate cold boot.

## Producer obligations by stage

| Stage | Established path / effect | Remaining obligation |
|---|---|---|
| Boot storage initialization | NOR mode/status/identity setup; read81000 | All mode/config descriptor clients and completion observers, not just array-write calls |
| Identity constructor | Read23 bytes then zero **RAM** byte14; register edit callback | Callback inputs/dispatch throughout boot/recovery; no proof that registration itself writes NOR |
| Metadata/ordinary installer |03B2A reads80000;03B9A validates staged image, compares header, installs internally | Selected image footprints proved; arbitrary prior metadata/fault histories are not the chosen completed transition |
| Recovery selection |03B66/03AB0 key path; own boot intake | Physical entry/exit is user-reported; not rollback flashing proof |
| Application constructors/tasks | NOR wrapper20006968 and SD wrapper2000696C created by1E3A8; Storage5767C services both queues | Task creation is not full task/callback root enumeration |
| USB initialization/timers | Mode1 initialized; callback pointers in compressed RAM;248CE schedules150-tick reconfiguration callback | Prove all mode-selection writes and ordering through248B4/24918/38C54 before capture |
| Project/session restore | Copies/applies state; persist19 schedules RESYNC | Follow any stock file/flush producer and its filesystem/backend bounds |
| Deferred service | Actual SC35D8 persist19 resync is RAM/DSP work | Must not assume later B1.3 autosave code is inherited |
| Idle before capture | Diagnostic remains dormant in bounded20-tick model | No universal proof for delayed callbacks, filesystem jobs or USB MSD traffic |

## Why the next missing proof is concrete

The new native mass-storage review demonstrates a writer at57EF4, referenced by initialized RAM2000379C. Default mode1 maps above94000; whole-array mode3 can target both evidence sectors. Setter2492E and delayed callback248B4 are actual roots to review. Absence of a command in one transfer trace cannot prove their mode invariant over ordinary boot/background operation.

Disk persistence has an independent obligation: disk-write1A7AC selects the NOR logical device for drive0, and mapper1AF1E has no own LBA-range check. Valid LBAs stay aboveD4000; out-of-range32-bit arithmetic can wrap. The accepted filesystem metadata/allocation/flush constraints supplying that LBA/count have not been exhaustively proved. This is not a claim that a normal filesystem generated the adversarial test values.

## Test-state boundary

The intended sequence is a completed selector0 B1.3→corrected update, ordinary successful cold boot, no factory/resource/mode-changing commands, and a later single diagnostic request. Even under that restricted input policy, missing mode/callback and filesystem producer proofs prevent claiming that **all** reachable mutation producers are enumerated and safe. Missing authentic NOR values cannot be silently replaced with zeros to advance boot.

**Smallest remaining offline work:** close the mode invariant through the delayed USB callback and complete the upstream LBA/count proof for1AF1E across project/settings restoration and any automatic file flush. If either admits a target write under the actual state, identify its data/provenance effect before acquisition. Otherwise record the complete exclusion graph. Full candidate qualification stays gated.

Evidence: [expanded graph](<nor-mutation-callgraph.md>), MSD results (local-only reference: `builds/phase45-nor-mutation-closure/msd-writer-review.json`; not distributed), mapped-write results (local-only reference: `builds/phase45-nor-mutation-closure/mapped-write-review.json`; not distributed).
