> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

> Candidate in this historical report: FAILED / SUPERSEDED / DO NOT FLASH.

# Exact 12-byte schema and ownership

**PROVEN:** recordS=20044D70..20044D7B. MasterFX retains20044D7C..20044E57. Early constructor hook reserves both by moving heap limit20044E58→20044D70 before native constructors; the additional diagnostic capacity over existing MasterFX is exactly12 bytes. No extra persistent allocation is introduced. Native constructors and the installed first-mount path execute in the new image.

|Byte/bit|Meaning before authorization|Meaning after authorization|Writers / readers|

|---|---|---|---|

|S+0 bits0..2|BOOT0,VALID1,EXPORTED2,MOUNTING6; FAILED5|ACTIVE3,SUCCESS4,FAILED5|init/begin/snapshot/export/authorize/watch/invalidate/complete/fail; all lifecycle readers|

|S+0 bit3|unexpected-event terminal flag|same|invalidation hooks only; admission rejects it|

|S+0 bit4 throughS+3 bit0 (21 bits)|strict first-mount epoch:0 before first mount,1 thereafter|epoch1 retained|begin, terminal phase writes; authorization checks epoch1|

|S+3 bits1..7 (control bits25..31)|exported host session1..127 only in EXPORTED;0 otherwise|0; session is copied to payload|export writes; authorization compares exact session-bound control word|

|S+4..S+11|geometry64: bits0..12=fat;13..25=fatsz;26..38=data;39..51=entries;52..54=log2(cluster sectors);55=nfats−1;56=type−1;57..63=0|overlay described below|snapshot commits; export/auth read. No overlay at export|

|S+4|geometry byte0|fixed target mask2=coefficients,3=identity+coefficients|authorize writes; raw derives fixed address/total only|

|S+5|geometry byte1|session1..127|authorize writes; raw reads|

|S+6|geometry byte2|global chunk0(identity) or1..8(coefficients)|raw writes only whileACTIVE|

|S+7|geometry byte3|owner0(initial),1(read),2(reply); retained on failure|authorize clears as part of word store; raw sets; complete clears only on successful ACTIVE→SUCCESS|

|S+8..11|geometry bytes4..7|start tick32|authorize writes; watch reads unsigned elapsed|

This intentionally replaces the earlier conceptual28-bit epoch with21 bits plus7 export-session bits. The candidate permits **only epoch1**, never recertifies a later mount, and does not claim a globally unique token across power cycles. Host session is a transaction identifier, not cryptographic authentication.

Legal path: BOOT0→MOUNTING16→VALID11→EXPORTED(session<<25|12)→ACTIVE13→SUCCESS14. ACTIVE→FAILED15 on timeout/read/send failure. Unexpected drive0 mount/binding/stride events→unexpectedFAILED1D. SUCCESS/FAILED reject new capture. Completion requires exact13 under PRIMASK and cannot replace15/1D. Geometry overlay occurs only after matching epoch, both geometry words, export session and allowed target mask. Geometry remains immutable during export and waiting.

Snapshot accepts only fixedD4000 base/4096 stride+BPS, drive0/FAT12/16, current disk0 wrapper and registeredFS, representable scalars, valid factors and root relationship. Host independently validates domain bounds/FAT capacity/classification and computes both target intersections. Device snapshot is a bounded representation check, not a substitute for host domain validation. A successful RAM-only export implies a committed first snapshot. Native commit writes both payload words before validity publication, with interrupts masked and a barrier; no allocator/Storage/NOR/FS call exists in it.

Expected first-mount stride4096 publication is allowed only duringMOUNTING. Later stride/binding changes and slow remount invalidate, including changes to an otherwise numerically identical geometry. Registration checks the actual expected outer return address0801AE07. Cached normal file operations do not create a new snapshot. The hook at0801AE06 reconstructs the overwritten MOVS/IT outcomes before the original0801AE14 tail.

Preauthorization host timeout is10 seconds and consumes the host session without sending another command; it is not a device-side Storage cancellation. Device timeout applies only toACTIVE at5000 ticks, including wrapping tick arithmetic. H4 remains FAIL for in-session recovery: pending Storage/semaphore/buffer ownership is never forcibly released.

## Fixed command grammar

Commands are exactly232 bytes, USB port0, F0 7D 43 54 prefix, session1..127 and finalF7. Command0E is geometry export with bytes6..230 zero. Command0F has byte6 mask2/3, bytes7..14 epoch32 as8 MSB-first nibbles,15..22 low geometry word as8 nibbles,23..30 high word as8 nibbles,31..230 zero. Old0D start is rejected. No address/length is accepted from the host.

Geometry reply is39 bytes: F0 7D CT 4E session, epoch32/low32/high32 encoded as24 nibbles, MPEG-2 CRC32 over bytes4..29 as8 nibbles, F7. Raw replies retain4D framing and per-packet+whole-transfer CRCs. Coeff-only skips identity globalindex0: indices1..8 then completion9,total512,completionbase82000. Explicit mask3 sends index0 identity23 plus1..8 coefficients, completion9,total535,completionbase81000. Raw target derivation is fixed81000/23 or82000+64*(index−1)/64. Identity is an independent explicit host option with its own mapping-intersection check; it is not silently enabled by coefficient permission.

The512-byte capture requires8 ordered64-byte chunks, exact addresses/indices/lengths, valid packet CRCs and exactly one valid completion with full CRC. The host buffers in memory; an explicit end-of-stream boundary validates duplicates/trailing packets before publication. A production transport adapter must drive the monotonic deadline and that boundary; this phase exercises injected transport only and opens no ports. All output files are fsynced in a fresh sibling staging directory, then published by one directory rename. Existing capture directories are never replaced. Failures discard reconstruction; no automatic retry or cleanup/storage command is sent. Optional identity and coefficients publish together. All included sample output is clearly marked SYNTHETIC.
