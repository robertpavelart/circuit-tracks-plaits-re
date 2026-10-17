> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Post-READY allocation check

POST-READY ALLOCATION CENSUS: UNQUALIFIED

**UNKNOWN — conclusion D: unresolved indirect targets prevent proof.** No post-READY request larger than eight bytes was established by this traversal. Its absence was not established either. The modeled remaining eight bytes are not a qualified physical heap margin.

## Exact inputs and method

The frozen package BIN has SHA-256 `edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9`. `byte_audit.py` reads these bytes and the saved Phase66 `frontier-sram.bin`; it does not run a builder. `reachability.py` produces `reachability.json` and `indirect-sources.tsv`.

**PROVEN within this traversal:** 78 roots, 25,033 instruction addresses, 18 locally bounded TBB/TBH switches, 206 encountered indirect sites. Seventeen indirect sites have selected fixed-object target sets; 189 remain UNKNOWN. Each encountered indirect site has its pointer-producing instruction context or an explicit source explanation, and its bounded target set where established, in the TSV/JSON. This is an incomplete reachability census, not a complete control-flow graph. Numbers count instructions/sites, not functions or allocations. The linear disassembly evidence files can include data after function returns; that data is not automatically an executable edge.

Roots cover the Main post-READY loop `0801D5A4`, UI `0801D696`, Storage `0805769C`, Content `08022AD0`, Idle hook `0801D760`, parser `0801EB30`, deferred consumer `0801CFF4`, diagnostic `0806F900`, BOT service `0801F37C`, application IRQ vectors, initialized USB child-class tables `0805A444/0805A480`, port table `0805B60C`, SCSI table `20003788`, SD/NOR tables `0805B180/0805B1AC`, and saved Main/UI timer callbacks. Saved registrations seed coverage; they do not prove all future registration writers or task creators are bounded. Conditional paths are retained. Unknown indirect edges stop proof rather than being assumed harmless.

Targets include `0801CFA4`, `0801D7D8` and aliases/wrappers `0801D7D0`, `0801D808`, `08037380`. No allocator endpoint was reached through the edges whose targets were resolved. Thus the proven-reachable allocation table is empty; there is no justified request-size/caller chain to invent. `allocation_endpoints` explicitly remains incomplete.

## Narrowed software proof boundaries

| Pointer source / exact site | Established target information | Context and relevant windows | Remaining allocation question |
|---|---|---|---|
| Main queue consumer `0801D010`, record first word | Six direct Content publishers of `08037310` install outer thunk `08022E09` | Main; may run between query/authorization/capture commands; Main does not dispatch it inside its suspended raw-read frame | Outer target resolved; inner target below is not |
| Forwarding thunk `08022E08`, `LDR R4,[R0]`; `BLX R4` at `08022E22` | Inner callback comes from the queued Content completion payload; producer request descriptor callback at offset `+3C` | Content produces, Main consumes; query/authorization intervals possible; not nested Main processing during raw suspension | Complete producer/target set, downstream caller chains and sizes UNKNOWN |
| Event subscriber dispatcher `0801C894`, `BLX` at `0801C8AE` | Function/context slots in subscriber object, populated by `080251E8`; saved Main/UI registrations are finite | Main/UI event processing; UI can continue while Main raw read waits | Lifetime registration writer/type closure and downstream allocations UNKNOWN |
| Timer dispatcher `0801E4BE`, `BLX` at `0801E51E` | 28-byte slot, callback `+0C`, context `+10`; registration via `0801E538` | Main/UI timer owners; UI may run while capture pending | Saved timer values alone do not bound every later registration or allocation size |
| UI global callback `200069A8`, `BLX` at `08035698` | Setter `080356B0`, initialized by `08020906` to `0802096D` | UI | This outer target is resolved; downstream unresolved sites remain explicit |

`08037310` copies a 30-byte payload beside the callback word into a 34-byte Main queue record. Its six direct Content callers are `08022BB8`, `08022C30`, `08022C9C`, `08022CE4`, `08022D48`, `08022DAC`. Resolving the outer callback does not resolve `08022E22`. See `08037310.asm`, `08022acc.asm`, `08022e08.asm`, `0801cff4.asm`, `0801e4be.asm`, `08035680.asm`, and `service-xrefs.json`.

**UNKNOWN:** for targets behind these unresolved edges, request size, allocation caller chain, and occurrence after READY/during geometry query/during authorization/during pending capture cannot all be supplied. Main serialization limits the last window for Main callbacks; it does not close UI/Content callback targets. This is relevant software uncertainty, not host-enumeration timing or an unrelated peripheral-model frontier. It is not evidence that 189 different runtime allocation risks exist.

## Exhaustion is not a safe fallback

**PROVEN by frozen bytes and preserved prior disassembly:** `0801D7D8` rounds the request to four bytes and compares it against cap/cursor `20002B44/20002B48`. Exhaustion executes `BKPT #1` at `0801D7F4`; if resumed it returns `FFFFFFFF` via `0801D800..0801D804`. Generic wrapper `0801CFA4` tests nonzero at `0801CFB2`, accepting that value. The construction call at `0801CFDC` requests 12 bytes and checks only zero. That construction call is not proven reachable after READY. This prevents substituting conclusion B without caller-specific evidence.

Smallest remaining work: bound the nested Content completion callback producers feeding `08022E22`, then the live subscriber/timer registration writers reached from those producers, and resolve any allocator argument/failure handling on those paths. Do not repeat startup or add a peripheral model. This report does not claim that resolving just one callback closes all 189 unknown sites.
