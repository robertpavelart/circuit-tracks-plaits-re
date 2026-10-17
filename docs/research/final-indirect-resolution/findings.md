> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Final indirect-call resolution

POST-READY ALLOCATION CENSUS: UNQUALIFIED

**UNKNOWN:** whether a reachable post-READY indirect callback can request more than the modeled remaining eight bytes. No such runtime allocation was proven, and absence was not proven. No concrete unsafe post-READY path is asserted. The previously qualified USB Storage joint path is preserved and was not revisited.

## What closed

**STRONG INFERENCE from normal stock publisher argument provenance:** the inner Content call at `08022E22` has seven recovered nonzero targets:

`0803A478, 0803C90C, 0803C968, 0803C978, 0803C9A8, 0803C9C8, 0803CC6A`.

`content-provenance.md` records the request field `+3C`, all three recovered descriptor assignment forms, queue copies, constructors, setters/publishers, caller arguments, target set limits and per-target allocation summaries. Four targets are SAFE with no allocation. Three still depend on slot0 virtual calls at **0803C91C / 0803C9C4**. Resolving the first indirect hop did not resolve the whole allocation chain.

Additional fixed sources were traced statically: RTC `200069F0 → 0801DA70`; event callback globals `200069E0/E8 → 08047828/08047830`; Content notification globals `200069B8/C0 → 0802D43C/0802D444`; callback `200069B0 → 08029A34`. These targets lead to their own explicitly retained downstream edges. Fixed first targets are not automatically labeled allocator-safe.

**PROVEN within the recovered direct publisher set:** all 17 callers of secondary timer registration `0803C432` supply fixed R3 callback values. Dispatcher `0803C42E` reads table `200065C4`, populated at `0803C442`. Source addresses/values for all 17 are in `resolution.json` under `secondary_timer_publishers`. This resolves that target-selection mechanism for the recovered publishers. It does not turn all timer object aliases into a complete lifetime proof.

## Complete ledger of the remaining proof boundaries encountered

`indirect-ledger.csv` records every encountered indirect site: callsite, pointer-producing instruction context, registration source where recovered, finite/partial targets, allocator reachability, maximum known request and classification. `resolution.json` retains 73 per-target summaries, including exact unresolved downstream sites. Explicit UNKNOWN fields mean unresolved, not zero. The full ledger is the requested list; selected mechanisms below explain why it still cannot qualify absence.

The expanded conservative traversal visits 32,266 instruction addresses and 260 indirect sites, with 233 unresolved target selections. The count increased because additional callback targets were followed. It is not evidence of 233 proven executable allocation hazards. Conditional BL forms are followed; stack epilogues `LDR PC,[SP],...` are recognized as returns rather than new callback registrations. Roots preserve Main, UI, Storage, Content, IRQ/class/BOT/SCSI and diagnostic coverage and add the recovered Content targets. Partial target sets are followed without excluding unknown alternatives.

| Exact unresolved mechanism | Source / registration evidence | Why maximum request remains UNKNOWN |
|---|---|---|
| `0803C91C` | Content target `0803C90C`; captured context references an object, whose first vtable slot is called | Complete owner/subobject constructor and alias binding is not established; no safe destructor assumption |
| `0803C9C4` | Common Content continuation of `0803C968/0803C9A8`; slot0 of object at context `+4` | Same type/alias boundary; descriptor callback resolution does not bound this second hop |
| `0801C8AE` | Subscriber registry slots `+8+4*i`; setters `080251E8` and inline `0805193C/0803CB42/080356B0` | Fixed registered targets are followed, but complete alias/writer closure of every reachable registry is not proven |
| `0801E51E`, `08023528` | Timer slot callback `+0C`; `0801E538` bulk slot copy and `0801E52C` exposes writable aliases | Saved three registries and fixed live setters enlarge the target set; saved values cannot exclude every later slot writer |
| `0801EB58` and object-method sites in the CSV | Parser object global, then slot0; other sites load a vtable from object/argument registers | No complete static constructor-to-use points-to relation for every receiver type. An observed vtable or a broad list of ROM code words is not a proven type bound |

**UNKNOWN:** complete possible targets at those unresolved sites and whether they reach `0801CFA4/0801D7D8`. The CSV gives the exact instruction-level sources at all the other encountered boundaries, rather than hiding them behind only these examples. The traversal reaches no allocator through the edges it resolves. Because unknown edges remain, that negative is explicitly not allocation-absence proof. No request size is invented from a startup observation. No unresolved request is labeled UNREACHABLE or SAFE-FAIL.

The static evidence recovered here does not close the constructor/alias relationships. This is not a claim that the frozen binary is fundamentally unanalyzable or that hardware execution could prove absence. It is a stop at an actual software points-to proof boundary within this task, not a new peripheral-model frontier. The task's exhaustive all-indirect-call requirement remains unmet; consequently PASS is withheld.

## Failure behavior

**PROVEN:** four new isolated native allocator ABI cases pass. Size8 succeeds with an eight-byte gap; size12 reaches rejection BKPT with unchanged cursor. Explicitly starting at the post-BKPT continuation returns `FFFFFFFF`, which the generic wrapper accepts as nonzero. Exact bytes bind the HardFault vector to a self-loop handler. Physical exception routing at BKPT remains UNKNOWN; no hardware or exception-routing model was introduced. See `failure-semantics.md` and `allocator-failure.json`.

Thus a future >8-byte path cannot be dismissed as safely failing. Conversely these isolated allocator inputs are not proof that such a path is post-READY reachable. SAFE classifications in the target summaries mean no allocator on their fully resolved graph, maximum0; UNKNOWN remains transitive where another callback is unresolved.

## Preservation and disposition

All evidence uses frozen candidate SHA-256 `edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9`. `validation.json` records package integrity and saved-result checks. Firmware, reference repository, candidate bytes, package files and live-tool locks are unchanged. No USB joint-path rerun, peripheral modeling, hardware access, MIDI access or transmission occurred. New native execution was limited to the isolated allocator ABI cases above.

The operational package is not updated or unlocked because the allocation census did not PASS. No firmware defect was established. Remaining work, if resumed, is specifically constructor/alias binding for `0803C91C/0803C9C4` and the registry/receiver sites enumerated in the CSV; repeating startup, enumeration or allocation observations would not close it.

POST-READY ALLOCATION CENSUS = UNQUALIFIED
