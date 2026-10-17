> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase52 — authenticated hardware plan withheld

**Authentication answer: UNKNOWN.** Single remaining ambiguity: no qualified current-command DMA/USB ownership-and-source invariant proves that an accepted512-byte BPB came from the intended current NOR read rather than a late/old operation or replay. The restricted contiguous-prefix/zero-clear model passes the required target freshness check; actual native reachability of broader stale-completion/replay outcomes is not established. More equality-only controls do not prove that invariant.

**PROVEN:** T→C→T is insufficient to detect every modeled control failure. T→A→T→B→T still accepts byte-identical partial controls. **PROVEN:** within the tested prefix model, no n<512 target result passes; n512 is fully refreshed metadata but incomplete4096-byte physical block. These distinct findings must not be collapsed into either 'all partial reads pass' or 'physical authentication proven'. [partial-dma-exhaustive.md](<partial-dma-exhaustive.md>); [control-sector-strategy.md](<control-sector-strategy.md>).

Because the requested answer is not PROVEN YES, no future hardware procedure is qualified or issued. There is no acquisition script, port operation, device enumeration, firmware action, filesystem mount/repair or new binary. Model addresses64/65/73 are evidence fixtures, not an instruction to read those LBAs on the unit. Existing Phase51 acceptance boundary remains INVALID on structural failure, otherwise UNQUALIFIED for physical authentication. [acceptance_gate.py](<../../../builds/phase51-msd-read-safety/acceptance_gate.py>).

Smallest next offline question: establish or reject the existing37430/37596/IRQ-to-DMA ordering invariant that EN is clear before1C072, all BPB-bearing bytes correspond to this read, and USB consumes the buffer before reuse. The native EN1-skip behavior is now explicit. This requires closing the actual completion boundary rather than adding more control reads or another firmware diagnostic. No new experiment is started here.
