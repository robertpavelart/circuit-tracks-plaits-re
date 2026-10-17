> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase20C5 — state guards and failure containment

2026-10-07. **PARTIAL / design only.** Chosen numeric object P:[3FF0,3FF7);
same future policy must protect code, temporary frames, shadow and fault latch.
No guard encoding, modified payload or runtime ownership proof is supplied.
See `plaits-enforced-state.md` for object layout, costs and reproduction.

## P204B: enforce at the actual commit

**VERIFIED original instructions**, byte-checked export `evidence/P202B-P2071.asm`:

|PC|Operation|Meaning supported by data flow|
|---|---|---|
|202B/C|MOVE #967,R1|Two-word whole-function entry; clean future long-JMP window|
|203A|MOVE X:(R0)+,X1|Single count from X35F|
|203B..203F|First fields and Y prefetch|Do not skip initialization/prefetch|
|2040|DO X1,204C|Loop endpoint LA=204B; one latched count, not count per record|
|2042|MOVE Y:(R6+N6),Y1|Source lookup|
|2043|MPY Y1,Y0,A X:(R0)+,R4|Destination from X[364+5*k]|
|2044..2047|Following pointer fields and product|Record advances, next source pointers|
|2048|MOVE X:(R4),B A,Y1|Read destination plus product transfer|
|2049|MAC X0,Y1,B X:(R0)+,X0|Read/modify accumulator, prefetch next coefficient|
|204A|MOVE Y:(R5+N5),Y0|Next-source prefetch|
|204B|MOVE B,X:(R4)|Destination commit; hardware-loop endpoint|
|204C..2054|Post-loop setters|Must remain|
|2055 /2057|MOVE X:(R0)+,B Y:(R4),Y0 / TFR Y0,A X15,Y1|Tail redefines A/Y1 before later consumption|
|2070|RTS|Whole helper is70P words, [202B,2071)|

No recovered normal positive-count/destination/value bound was added. X35F is
latched into LC; writing it zero cannot disable one current record or update
the current LC. “Zero count for conflicting record” is not the schema.

Chosen A: X3FF0 is not P3FF0 under fixed Harvard mapping. Testing integer R4
against3FF0 would block unrelated X memory and fail to close the real DMA route.
Retain ordinary X RMW. Classify actual X control/peripheral destinations and
mediate DMA/mode/control commits; this denies the mechanism capable of creating
P writes. Policy covers code and every new P object, not only seven state words.

**CONDITIONAL future template:** replace complete202B entry with a jump to a
guarded clone, not a long jump at one-word LA204B. At the final store, A/Y1 are
locally dead until their next definitions. Save SR in Y1, copy R4 to A, AND/CMP
raw top12 againstFFF000, branch to control admission, restore SR, perform original
MOVE B,X:(R4). Leave X1 intact. Common five-NOP tail moves DO LA away from long
JMP/JSR/MOVEM hazards. The slow validator must reproduce original56-to24 limiting
and sticky CCR effects; B1 alone is not necessarily the bus value.

**CALCULATED unassembled:**20 words replace original1 =>+19, full clone89P;
fast+21 per record, slow+19+U_validator, entry+4. Local deadness is not proof of
complete IRQ/CCR/caller ABI. FM PDF438/439 bans relevant instructions at/near
DO LA; retargeting and five-NOP tail still need actual assembler/ISA qualification.

Alternative B reclaims X:[57B,582): guard before2048's read, not only write,
and skip matching read/MAC/commit while retaining2049 next-coefficient and204A
source prefetch plus loop progression. No count or unrelated-record naming.
Second-choice redirect requires a newly owned seeded sink, not “harmless scratch”.
Preparation-time rewriting ranks below commit mediation: producer/order unknown,
later table mutation is a TOCTOU risk. Global count-zero is rejected.

## DMA admission, eight channels and startup

**VERIFIED:** there is no recovered centralized stock admission trap. Proposed
central nonblocking validator needs distributed commit adapters or proved
exemptions. X DMA registers are FFFFEC-4*c +{0:DCR,1:DCO,2:DDR,3:DSR}, c0..7;
DOR and mode/PIC/control roots are additional protected control state.

For the first PoC, **CONDITIONAL policy** denies all stock DMA P destinations
and P sources during the ownership epoch. This protects new code/data and prevents
stock consuming the object. It is deliberately stricter than a seven-word
destination interval check; P-copy/overlay features are accounted as denied.
Reserved space encodings and unknown modes/endpoints fail admission.

|Channel|Recovered profile retained|Admission rule|
|---|---|---|
|0|DCR285AC4(+DE),DSRFFFFA8,DCO2,DDSY/DRS11; ISR DDR0=29|Pin exact certified profile/rearm; no arbitrary live changes|
|1|DCR286251(+DE),DDRFFFFA4,DCO2,DSSY/DDSX/DRS12; ISR DSR1=21|Same; preserve original audio transfer|
|2..7|Post-ROM live configuration UNRESOLVED|Inspect/admit complete safe X/Y configuration; do not blanket-disable or assume reset|

Enabled configurations are immutable except certified audio rearm and DE clear.
To reconfigure, require certified DE0+DTD1, validate the complete proposed DE0
configuration and enable as one serialized transaction. NOT_READY returns without
changes, not an unbounded runtime polling loop. Maskable configuration writers
need serialization and their own P30 save frame; renderer P26 must not be shared.
NMI/IRQ/FIFO latency and complete store-coverage protocols remain unqualified.

**VERIFIED pinned FM, PDF195/203..205:** DE clear may finish a captured/current
word. DACT bit8 is active status, DCH11:9 channel; external-bus transition can
show spurious active/channel0. DTD becomes set on termination/last transfer; word
mode DE clear can await a captured trigger, and continuous infinite transfers
need not terminate while enabled. Therefore DE=0 alone is insufficient.
Require all eight DE0, all eight DTD1 and DACT0 after the ordered shutdown,
with a startup timeout/refusal budget. Initialize P objects only after old pending
writes are finished. **VERIFIED RM PDF115** adds DTD6/7 at DSTR bits6/7 to the
family manual's six-channel status definition. Its DCH[10:9]/DCH[2:0] description
is inconsistent; the policy does not use the active-channel field as a quiescence
witness. Compatible hardware/handoff ordering remains a proof gate.

**Important primary-source restriction (FM PDF205 section10.6 restriction3):**
DMA accesses to internal peripheral I/O are limited to transmit/receive data
registers. DMA-to-DMA-control is not a supported generic route under that
documented compatible profile. Earlier generic concerns must not be presented as
a verified DMA ability. CPU indirect writes to DMA/control registers remain the
actual unclosed configuration route. Admission still rejects undocumented I/O
endpoints rather than depending on undefined behavior.

Initial trust is independent: an unknown enabled P-DMA at ROM exit might damage
the initializer/guard code before it quiesces. A validated surviving entry and
handoff contract is needed; software cannot retroactively certify corrupted
enforcement code. No initialized constructor/reset register state is assumed.

## SHI protection per actual word

**VERIFIED:** the data-lane branch at15F reaches198 directly, bypassing168..16C
accumulator saving. The commit is19D `MOVE X0,X:(R0)+`, then19E stores updated
R0 toX10. Guarding requested ARM addresses, page setup or cached start addresses
does not cover each actual destination. The preferred clone is198..19F (8P),
with clean198 one-word +199 two-word entry window.

Chosen A checks actual X control roots after bank/address decoding. Ordinary
private X/Y stores cannot touch private P state under the admitted mapping;
X and Y at the same numeric address must remain distinct. For alternative B,
test only actual X[57B,582), with its correct AGU address/advance.

Simple unindexed R0 classifier can use12 JCLR bit tests on23..12 without A/B
clobber; low RAM exits on bit23 at4 modeled cycles. False conditional branches
add1 (FM PDF437): all12 misses cost60; a final clear costs59. **Unassembled
template** partial size37P: relocated original8+1 long-branch relaxation,
24 tests+2 slowcall+2 routing. Actual denied advance/error adapter costs extra.

Each word is tested, including paged/cached/wrapped and width-dependent
continuations. Denial must consume exactly one host word, advance the original
cursor exactly once with original modifier semantics, storeX10, and report
denial. Existing status2 success may not claim a blocked write succeeded.
Separate P1 diagnostic fault latch and a symbolic read-only guard-status adapter
are budgeted; no opcode number invented and no packets constructed. Nonconflicting
services remain available, subject to unqualified timing/backpressure.

## Complete mediation and execution boundaries

The original listing yields **344 decoded indirect X/L store-component
candidates** outside known copied-data regions. They are a finite obligation
list, not a registry of344 proved-normal writers or a full reachability proof.
Control-flow, single-component, parallel and RMW instructions must be classified
against actual effective addresses. Comparing Rn before predecrement/index/modulo
calculation is insufficient. L moves require separate X/Y destination components.

A finite certificate must assign each candidate a proved domain exemption or
exact adapter. Direct register stores, mode changes, all new P-owner reads/writes,
DMA reconfiguration and control-flow access to data/initializer/ROM require
coverage too. Reject illegal jump/call/return into owner-store gadgets; a PC
allowlist without caller/control capability cannot certify ownership. Existing
indirect DB6/DBD/DC5/DCD/DEC/DF9/19AC and RTS/RTI remain residuals.

The provisional P32 typed shadow is a design allocation, not an implemented
control-flow stack. It must account for DO/call/IRQ/data frames and current
headroom; immutable code, legal return labels, INIT/ROM exclusion and async
serialization are unproved. Only owners may read/write the explicit P objects;
stock table-source reads cannot accidentally interpret them.

## Failure containment and gates

|Failure|Required response|Remaining gate|
|---|---|---|
|Startup/profile/quiescence/trust unknown|Do not publish owned epoch|Entry guarantee, bounded barrier and actual mode|
|Conflicting record commit|Skip just conflicting side effect; retain prefetch/DO progression|Exact CCR/limiting/liveout and record coverage|
|Conflicting SHI word|Consume/advance once, deny, latch/report fault|Cursor/error ABI and latency|
|Unsafe DMA request|Reject; leave previously admitted config intact|Transaction/coverage/IRQ serialization|
|Mapping/code/CFI ownership lost|Stop selected rendering until reload; no live stock takeback|Safe mute and auxiliary/post contract not yet qualified|

No silent corruption, invented sink or global service-disable solution.
Zeroing mono alone is not a qualified mute because auxiliary streams can
contribute downstream. Runtime silence/denial adapters require their own finite
ABI. External-interface recovery/rollback remains separate; no debug-probe
dependence. **Offline patched image NO; hardware flash NO.**
