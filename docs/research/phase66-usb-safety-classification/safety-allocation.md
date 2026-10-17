> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Safety relevance and allocation results

The conclusions below concern the normal offline startup workload, with inherited synthetic storage/ADC/clock inputs. They do not describe arbitrary later USB commands.

| Resource | Observed effect / boundary | Confidence |

|---|---|---|

|Diagnostic-owned RAM|USB init writes its own handle/endpoint metadata and temporary stack. All3,186 observed allocation returns end at or below20044D70 and none intersects the reserved record.|PROVEN within traced prefix|

|12-byte lifecycle/geometry|Remains `110000000180003480908f01`; no USB-driver PC writes it.|PROVEN|

|Raw capture buffer|No raw frame exists yet. USB init's temporary stack use is not concurrent with a live capture frame.|PROVEN absence; future lifetime UNKNOWN here|

|External NOR program/erase|No mutation primitive is entered after USB initialization starts in this workload; local USB init contains register/metadata operations.|PROVEN observed path; arbitrary later commands outside scope|

|Authorization epoch/session|No diagnostic request is injected, no session is authorized, and record11 persists. No USB-init write advances the epoch/session.|PROVEN|

|Bootloader/rollback|Candidate bytes and prior install/rollback evidence are unchanged; the modeled register sequence does not program internal flash.|PROVEN scoped preservation; physical rollback UNKNOWN|

**PROVEN USB initialization state:** the live PCD handle at `$20004D44` has six endpoints and state1 (driver READY). Its native DMA-enable field is0 at handle+`$10`; this offset follows the actual by-value ABI and conditional branch at `08048226`, not an assumed modern struct layout. GAHBCFG ends at1, so GINT is enabled and DMAEN is clear. No endpoint-DMA register is programmed in the observed USB initialization. PCD READY is **not** `USBD_STATE_CONFIGURED=3`; no host configuration event was modeled.

**PROVEN allocation evidence:** allocation-returns.json (local-only reference: `builds/phase66-usb-safety-classification/allocation-returns.json`; not distributed) tracks entry size, caller return PC, SP/TCB, pointer and end extent for1,582 generic requests and1,604 underlying bounded bump calls. All3,186 calls return; there are no positive-size failure returns, pending returns, arithmetic-wrap extents or overlaps with `20044D70,20044D7C)`. The generic/bump counts are two layers of the allocator, not3,186 distinct independent objects. Observation begins at runtime-hook installation after constructors; the constructor reservation evidence remains separately preserved.

The cursor is `$20044D68`, eight bytes below the cap. This is the observed bump frontier, not a physical RAM/stack margin measurement or proof that all future requests can succeed. A large160,784-byte allocation is explicitly recorded at2001183C–20038C4C; no inference about its ownership/free capacity is needed for the overlap check. The earlier concern that the next fault might mean allocation failure is **rejected**: every observed allocator call returned normally and the fault address is DWT, not heap RAM. See [analysis.json (local-only reference: `builds/phase66-usb-safety-classification/analysis.json`; not distributed) and fault-and-R9.json (local-only reference: `builds/phase66-usb-safety-classification/fault-and-R9.json`; not distributed).

**UNKNOWN:** allocations caused by future host enumeration, runtime reconfiguration or actual capture entry have not been executed. No claim is made that zero observed overlap proves the entire future lifetime. The prior Phase63 stack-buffer/DMA fence and host containment tests remain scoped evidence; no prepared fixture replaces this continuous run.
