> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase53 — final existing-B1.3 decision

**PROVEN NO.** Under the user's decision definition, the inspected existing normal B1.3 interfaces cannot establish filesystem-geometry physical-read authenticity sufficiently for the preflash preservation decision. This existing-MSD authentication branch is closed; no further READ10 repetition/control scheme is proposed.

**PROVEN:** B1.3 exposes the correct physical storage path: mode1 USB LBA40hex→D4000. **PROVEN:** it discards lower-read failure information. **PROVEN:** low LBAs00..3F are all NOR-backed, generated SCSI responses supply at most36 bytes, and the only full deterministic clear supplies zeroes that the target itself reapplies. **PROVEN:** no independent completion signal is exported by the inspected supported SCSI/status interfaces. Therefore neither candidate mechanism A nor B closes the missing authenticity contract. [buffer-producers.md](<buffer-producers.md>); [synthetic-msd-sectors.md](<synthetic-msd-sectors.md>); [deterministic-poison-analysis.md](<deterministic-poison-analysis.md>); [completion-signals.md](<completion-signals.md>).

This is a decision about **sufficiency of the existing interfaces**, not a claim that a real BPB was corrupted or a universal impossibility theorem about undocumented/memory-corrupt execution. Native/data-flow closure covers the registered MSD dispatcher, initialized callbacks and the supported protocol inventory. Raw scan limitations and unknown physical fault incidence are retained. There is no specific existing usable mechanism pending that would justify another UNQUALIFIED iteration.

Current-unit geometry consequently remains unqualified through existing B1.3 MSD alone. Reference geometry, valid-looking BPBs, matching repeated reads or an internal DMA flag must not be promoted into authenticated current-unit evidence. Earlier bounded mapping and parser results remain valid in their own scopes.

Conceptual next options only:

| Option | Consequence |

|---|---|

|A — explicitly accept geometry preservation as hardware-only uncertainty |Requires an explicit user decision to accept the remaining uncertainty. It does not turn the offline evidence gate into PASS, authenticate geometry or authorize a firmware/hardware action. |

|B — separate minimal read-only diagnostic with correct success/failure propagation |Could expose the missing contract, but must preserve source/address/count provenance and report physical completion/errors correctly. Merely forwarding22F94's normal0 or adding a payload CRC is insufficient where the underlying DMA/wait contract remains unqualified. Existing TEF quarantine/no-retry limits still apply. Separate design, validation and authorization would be needed. No diagnostic is designed, generated, installed or transmitted here. |

Neither option is selected or executed in Phase53. This report does not promote any historical firmware candidate or recommend hardware action.
