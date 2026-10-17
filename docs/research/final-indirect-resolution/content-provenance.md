> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Content completion pointer provenance

**STRONG INFERENCE — finite target set for the identified normal stock request publishers:**

`0803A478, 0803C90C, 0803C968, 0803C978, 0803C9A8, 0803C9C8, 0803CC6A`.

These are instruction addresses. Stored pointers have Thumb bit 0 set. Zero means no asynchronous callback publication; it is not a target of `08022E22`. This bounds the recovered descriptor types, not arbitrary corrupted descriptors or an unproved whole-program alias universe.

## Storage and copies

**PROVEN by exact instructions:** request records are 72 bytes. Operation is at `+00`; identity/reference data starts at `+04`; payload occupies `+10..+3B`; callback is at `+3C`, context at `+40`, optional result pointer at `+44`.

| Assignment / copy | Source |
|---|---|
| `0803CA7A: STR R2,[SP,#48]` with descriptor base `SP+0C` | `0803CA52` entry R3, saved at `SP+48`: callback field `+3C` |
| `080499D8: STR R5,[R4,#3C]` | `080499B4` loads stacked callback; sole direct constructor caller `0803CAD2` in `0803CAA4`, which saved entry R3 at `SP+30` |
| `08049A0E: STR R2,[R0,#3C]` | `080499EC` loads stacked callback; sole direct caller `0803CAFE` in `0803CADE`, which saved entry R2 at `SP+04` |
| Queue enqueue `08022A5C → 08036708 → 08022190` | Copies complete 72-byte descriptor into the Content queue; no new function-pointer selection |
| Consumer `08022AE4`, e.g. `08022B7A / 08022BE0 / 08022CA6` | Reads dequeued descriptor `+3C`, skips completion publication if zero |
| Six completion publishers to `08037310` | Copy callback into completion payload first word, context into its final word; install outer thunk `08022E09` |
| Main queue `0801CFF4`, `BLX R6` at `0801D010` | Calls outer thunk on payload |
| `08022E0A: LDR R4,[R0]`, `08022E22: BLX R4` | Calls copied inner callback, with payload arguments and stacked context |

The two constructors copy or clear payload through `+3B`, then explicitly assign `+3C`; payload copying is not another callback setter. The generic callback dispatcher has no target whitelist. Thus the finite set comes from publisher argument provenance, not from the dispatcher validating an address. No constructor or setter accepts a function pointer from the diagnostic wire protocol in the recovered paths.

The six Main completion publication calls are `08022BB8`, `08022C30`, `08022C9C`, `08022CE4`, `08022D48`, `08022DAC`. Exact listings and candidate xrefs are in this folder and the preserved `final-two-check-closure` folder.

## Publisher argument closure

| Request publisher | Callback provenance under the recovered callers |
|---|---|
| `0803CA52` | Sole direct call `0803CC0C`; read/write wrappers `0803CBD6/0803CBF0/0803CC16` supply stacked callback. Most callsites explicitly supply zero; `0803C904` supplies `0803C90D`; `0803C95E` supplies `0803C969`; `0803A3DE` supplies `0803A479` |
| `0803CAA4` | Only direct callers `0803CCC6` and `0803CD36`. First installs `0803CC6B`; latter forwards `0803CCFA` entry R3. Its only direct callers `08039E40/08039F1C` set R3=0 |
| `0803CADE` | `0803CB5C/0803CB92/0803CBC0` use zero callbacks. `0803CC62` forwards callback argument from `0803CC34/0803CC54` (original R1, not original R2) |
| `0803CC34` callers | `08039828/08039B58/08039B94/0803C984` set callback zero; `0803C9A2` installs `0803C9A9` |
| `0803CC54` callers | `08039A5E/08039A74/0803C942/0803C992` use zero; common call `0803C9B4` receives `0803C979` from `0803C970` or `0803C9C9` from `0803C9B0` |

The request constructor/publisher API entries have no raw absolute Thumb-pointer occurrences in the frozen image in the saved xref scans. The immediate-call candidate index and verified caller listings support these sets. They do not constitute a proof against every possible computed entry, alias write, or future execution root. The whole census therefore remains incomplete; the normal-publisher set is stronger evidence than saved dynamic values alone, but is not presented as universal pointer-integrity proof.

## Allocation summaries

| Target | Classification | Allocator/request-size conclusion |
|---|---|---|
| `0803A478 → 08026D34` | SAFE | Fixed counter/state writes; no allocation, maximum 0 |
| `0803C978` | SAFE | `BX LR`; no allocation, maximum 0 |
| `0803C9C8` | SAFE | `BX LR`; no allocation, maximum 0 |
| `0803CC6A` | SAFE | Result/status stores; no allocation, maximum 0 |
| `0803C90C` | UNKNOWN | `0803C91C` calls slot0 of the object obtained through stacked context: `R2=[SP+0C]; R0=[R2]; R2=[R0]; R4=[R2]` |
| `0803C968` | UNKNOWN | Falls through common body `0803C9B4`; `0803C9C4` calls slot0 of `[context+4]`. Context captured from `[SP+14]` at `0803C96C` |
| `0803C9A8` | UNKNOWN | Same common `0803C9B4 → 0803C9C4` virtual continuation |

**UNKNOWN:** complete constructor-to-use object/type and alias bindings for those two slot0 calls. Examples of normal publishers are `0802F8DC`, `0802FB3E`, `08030688`, `08030FCA` (read completion) and `0802FC06`, `0802FC7A`, `0802FE88`, `08030F6C` (write completion). They capture pointers into their owning objects, not a function pointer supplied as MIDI data. The owner has further mutable fields and virtual subobjects; identifying it merely by an observed RAM vtable, or assuming slot0 is a harmless destructor, would not prove allocation absence.

No direct/bounded-edge allocator endpoint was found in these target summaries. The unresolved virtual edges make their maximum transitive allocation request UNKNOWN. Resolving the outer seven targets therefore does not by itself close `08022E22`'s allocation safety.
