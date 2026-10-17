> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase20B7 — OnCE controller qualification

2026-10-07. **PLAUSIBLE TOOLCHAIN; NO QUALIFIED CONTROLLER/SOFTWARE PAIR.**
Documentation/source inspection only. No tools installed, built or launched;
no target interface opened. Preferred vendor qualification candidate is Symphony
Studio plus its documented DSP56724 OnCE command-converter class, without an
invented current SKU. Preferred auditable adaptation candidate is OpenOCD plus
an electrically qualified adapter; its present backend is not ready for this
two-TAP raw snapshot. Exact pair remains **UNRESOLVED**.

Canonical capability table: `builds/phase20b-tapqual/final-v2/controller-support.csv`.
It separately records breakpoint, raw registers, X/Y/P, hardware stack/loops,
pipeline, scripting, OS/availability and practicality for every candidate.

## Documented access relationship

**VERIFIED RM22 / FM7:** external JTAG shifts select ENABLE_ONCE in one chained
four-bit TAP and BYPASS in the other; OnCE command/data-register access permits
debug entry, comparator configuration and forced-instruction register/memory
transfers. TDI/TDO shift LSB first. This requires correct eight-bit IR and
companion BYPASS DR padding. Generic JTAG electrical ability alone is insufficient:
a DSP56k-specific OnCE protocol, dual-chain implementation, state-preserving
inspection and export are needed. SWD is not that protocol.

OnCE avoids firmware patches but is not passive or non-halting. Debug configuration
and forced instructions alter debug/register/pipeline state. A promise of literally
zero target writes would prohibit configuring a breakpoint or restoring disturbed
registers. The design contract is **no firmware or target-memory patch**, with all
transient debugger effects qualified and recorded. It is not authorization to act.

## F–G. Controller survey and preferred candidates

**VERIFIED official product documentation:**
[NXP Symphony Studio](https://www.nxp.com/products/processors-and-microcontrollers/additional-mpu-mcus-architectures/digital-signal-processors/symphony-studio-development-tools:SYMPH_STUDIO)
explicitly supports DSP56724/DSP56725, a custom GDB and parallel/USB command
converters. Legacy1.1.0 is dated2008 and listed as a54.35MB account-gated ZIP;
it was not downloaded. Modern Windows driver compatibility, obtainable converter
model, complete raw-pipeline export and stack-frame walk remain **UNRESOLVED**.
This is the best exact-device vendor support evidence, not a qualified purchase.

[DSPAUDIOEVM guide](https://www.nxp.com/docs/en/user-guide/DSP56720DBUG.pdf)
Rev4 Sec1.2.1 documents an embedded parallel OnCE command converter and external
OnCE header for DSP56724/25-capable daughterboards. Sec1.2.2 describes SDI USB/RS232
SPI/I2C real-time debug, a different path. Do not confuse SDI USB with an OnCE USB
converter, use EVM P2 pinout as Circuit wiring, or assume an EVM can serve as an
external controller without routing support.

**VERIFIED current official source:** OpenOCD DSP563xx backend pinned at
`8da0578d7bce3e134821ccf10911182788debc32` (2026-10-04 commit), four GPL source files
archived unmodified. [Core backend](https://github.com/openocd-org/openocd/blob/8da0578d7bce3e134821ccf10911182788debc32/src/target/dsp563xx.c),
[OnCE transport](https://github.com/openocd-org/openocd/blob/8da0578d7bce3e134821ccf10911182788debc32/src/target/dsp563xx_once.c).
No local executable was found via command discovery; nothing installed or compiled.

**VERIFIED source-level capabilities and blockers (not hardware tests):**

- once.c42/76 use `jtag_add_plain_dr_scan` / `jtag_add_plain_ir_scan` with only the
  supplied lengths, without inserting the other TAP's IR/DR padding. Merely declaring
  two TAPs is not demonstrated sufficient. DSP56724-specific chain qualification
  or host-side adaptation is required.
- c912 rejects a TAP without IDCODE; device JTAG0 legitimately lacks IDCODE.
  Exact dual-TAP examination is unqualified.
- c136 caches25 OnCE registers, including PIL/PDB/PAB and12 flow entries, in a
  static global array. Per-core isolation and raw export must be audited; this is
  not a claim a specific multicore failure was observed.
- c947–1021 saves OnCE latches before injected inspection, but automatically clears
  SR.SA/SC when set, sets N0/N1=0 and M0/M1=FFFFFF, and marks original cached values
  dirty. Export must retain pre-change cached state, not the altered physical
  registers or defaults. Poll/examine paths also clear comparator configuration.
- c830 saves54 core registers, including accumulator slices, SP/SC/LA/LC/EP/SZ.
  SSH handling saves/restores controls around top-register inspection; no complete
  active indexed hardware-stack export is established. Top SSH/SSL is insufficient.
- PC read c560 onward uses PAB/flow heuristics with TODOs. GUI/GDB PC cannot replace
  raw boundary evidence. Required OnCE registers are not the ordinary54-reg file.
- X/Y/P reads are supported, temporarily using R0/R1, exporting32-bit containers
  masked24. Canonical three-byte MSB-first DSP words need explicit conversion.
- c2063 routes program breakpoints to a hardware P-memory read/equality comparator;
  the backend exposes one hardware breakpoint/watchpoint resource. No P patch is
  inherent in that route. Actual device comparator support still needs qualification.

Source line anchors and hashes are exported in evidence/source-locators.json and
validation.json. No adaptation, configuration file or capture utility implemented.

**VERIFIED family-level commercial evidence:**
[TRACE32 DSP56k manual](https://www2.lauterbach.com/pdf/debugger_56000.pdf), 2026,
documents chain padding, attach versus reset-start, on-chip comparator facilities
and PRACTICE scripting. Its CPU list does not include56724/25. Default program
breakpoints are **software memory patches** (PDF14); future qualification must
explicitly select hardware comparator mode. PDF19 warns LA7701 lacks multicore
support. DE defaults, COP/watchdog settings and stepping options can change target
behavior; no distinct external DE pin is established for this package. Exact
DSP56724 controller/adapter support and complete raw stack/pipeline export remain
**UNRESOLVED**. Current generic DSP56303 product support and legacy LA7735 catalog
names do not prove a suitable present-day3.3V DSP56724 pair.

**VERIFIED legacy family evidence:**
[Suite56 tool manual](https://www.nxp.com/docs/en/supporting-information/DSPS56TOOLSUM.pdf)
Release6.3 (2000) advertises ads56300 hardware debugging and batch command files
with parallel command converter. Modern OS/drivers, availability and dual56724
support remain unqualified. CodeWarrior56800/E or DSC support does not prove
DSP56300 support; “USB TAP” branding does not identify the required protocol.

**UNRESOLVED support:** reviewed [P&E manuals](https://www.pemicro.com/manuals/)
and [SEGGER supported CPUs](https://www.segger.com/products/debug-probes/j-link/technology/cpus-and-devices/overview-of-supported-cpus-and-devices/)
contain no positive DSP56300/DSP56724 evidence used here. This is not proof those
vendors can never supply support. Generic FTDI/MPSSE can supply a JTAG bit engine
only with a correct qualified backend/adapter. Project emulators/disassemblers
do not supply a physical raw OnCE capture pipeline.

Retrieval limits: direct NXP EC/EVM/Suite56 downloads returned404; their official
web-cached text was consulted, not archived as complete local PDFs. Full pinned
RM/FM, TRACE32 PDF, OpenOCD source and board photos are available locally. Report
evidence/web-evidence.json distinguishes these cases. No large download was made.

## M–O. Tooling and fallback decision

**PLAUSIBLE TOOLCHAIN**. No exact currently usable pair meets electrical,
no-reset/no-auto-patch, two-TAP, raw latch/register/full-stack and coherence gates.
Machine-readable scripts outrank GUI transcription, but “GDB available” is not
a complete raw-state export guarantee. All candidates' connection-qualified
flags remain false. No purchase, installation, experiment or vendor message.

External OnCE remains preferred **CONDITIONALLY**, because exact-device vendor
support and an auditable family backend make it realistic to qualify. It has not
been demonstrated impractical. DSP hook + readback **does not become preferred**;
no further hook design or assembly. Flashing remains unjustified.
