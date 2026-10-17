> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Exact-image continuous prefix and allocation status

**PROVEN:** the same Unicorn instance executes the unchanged Phase63 image throughout the observed startup. Initial SRAM is freshly zeroed plus authenticated initializer bytes, with inherited reset-clock/constructor/RTOS entry and peripheral-completion models. This reuses the prior qualified starting boundary; it does not reexecute every decompressor instruction or claim a new complete hardware reset proof. There is no running-RAM/geometry/task fixture substituted after mount or at the SPI seam. The independent helper-test RAM is never used here.

| Recorded milestone |12-byte lifecycle record |

|---|---|

|reset prefix before constructors|`000000000000000000000000`|

|constructors complete|`000000000000000000000000`|

|first scheduler architectural launch boundary|`000000000000000000000000`|

|mount return 0x20000aa0|`110000000180003480908f01`|

|mount return 0x20001af4|`110000000180003480908f01`|

|mount return 0x20000aa0|`110000000180003480908f01`|

|Current DSP task frontier|`110000000180003480908f01`|

|USB-ready|UNKNOWN — not reached|

|Geometry query|UNKNOWN — not reached|

|Authorization|UNKNOWN — not reached|

|Raw capture start|UNKNOWN — not reached|

**PROVEN:** 1,212,601 native instructions;24,064 SPI status reads;9,024 transmitted polled bytes. These are model counts, not timing/feasibility measurements. Final heap cursor0x2000fe58, cap0x20044d70; the geometry record remains valid through NOR, SD and the later unchanged NOR mount.

The old cumulative10,000-PC-visit guard falsely stopped finite repeated GPIO/SPI operations during table upload. The new guard requires absence of byte-transfer progress for20,000 instructions before treating a heavily visited PC as stalled. Native chunk/exception bounds remain; missing receive completion cannot fake byte progress. This changes only replay termination policy, not firmware or readiness.

The inherited result field `private_unchanged=false` compares the final record with its initial all-zero marker. The actual snapshot intentionally changes it to11 plus geometry. It is not a failed memory-canary assertion; all record milestones are printed above. Full lifetime preservation is still unqualified.

**PROVEN:** boot-ready Y2B and initial mailbox idle responses now travel through actual SPI DR FIFO reads. No native read helper is replaced. SHI command/data selection is observed through native29190/291A2 and291B8 helpers; the protocol commits each word only after its third modeled byte completes. The XFFF request hook logs intent only; it cannot make DSP ready before the wire word commits. Each of the four exact ordered jobs returns its posted busy word before the independently supported idle result. **STRONG INFERENCE:** this finite busy→complete stutter is a valid progress abstraction for these observed mailbox values; it is not cycle-accurate processor-pair scheduling or a full DSP-state comparison.

**PROVEN model frontier:** native295E4 sends width-control bytes20/01/00 at29600. `BootPeer.commit` deliberately raises UnknownPeerRead at native37986 after the third byte, because the peer's16-bit SHI receive/DMA semantics and subsequent resource-backed selector0 job are not modeled. DSP main-loop113→12D is the width producer; HCSR10A5 selects16-bit words. ARM35ECE..35EF4 subsequently uploads16-bit coefficients;35F04 posts selector0 (first word0D1000). See the existing [command map](<../../../notes/dsp-command-map.md>) and Phase24 evidence (local-only reference: `builds/phase24-init-transition/four-job-baseline-result.json`; not distributed). Full normal boot remains **UNKNOWN**. This is a model refusal, not a firmware crash or unchanged-SR wait.

An exploratory pass that ignored the width command reached selector0 and refused completion there. That pass is not admitted as a qualified continuity prefix: ignoring width and bulk-recipient updates cannot prove the coefficient upload. The final runner stops at the earlier, exact unsupported transition instead.

**PROVEN:** 176 allocation requests and their actual caller sites are enumerated in allocation-prefix.json (local-only reference: `builds/phase64-spi2-model-closure/allocation-prefix.json`; not distributed). No additional Main heap allocation occurs across the newly modeled SPI prefix. Native allocator cap remains44D70 and observed record writes are only the intended lifecycle/snapshot operations. Ordinary bounded-allocator exclusion and raw-stack ownership remain supported by unchanged Phase63 tests, not rerun here.

**UNKNOWN:** complete postboot filesystem/transport/diagnostic allocation enumeration, postboot stack peak and absence of overlap across the *remaining* lifetime. The raw buffer has not yet been created in this continuous path, and no host transport session has begun. Do not infer complete coverage from176 prefix requests or a stopped cursor. No new fixed ARM RAM allocation is introduced by the Python peripheral/DSP-peer model.

Inherited synthetic models are explicit: FAT16 BPB/NOR payloads, JEDEC identity, absent SD completion, ADC1024 and factory calibration1500, clocks, DMA events and architectural exception delivery. These are not measurements of this unit. Real hardware memory margin and peripheral/USB timing remain hardware-only unknowns.
