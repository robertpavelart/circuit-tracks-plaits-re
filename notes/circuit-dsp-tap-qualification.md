> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase20B7 — Circuit Tracks DSP TAP qualification

2026-10-07. **DESIGN / DOCUMENTATION ONLY.** No board access, measurements,
debug commands, tool installation, firmware changes or snapshot acquisition.
Canonical reports: `builds/phase20b-tapqual/final-v2/`; verification:
`builds/phase20b-tapqual/checks-v2/`. Public documentary sources are archived in
`builds/phase20b-tapqual/sources/`, with retrieval URLs, SHA256 and limitations.

**Result: READY-FOR-PIN-VERIFICATION, CONDITIONAL on the actual board.** A visible
candidate footprint justifies a later limited identification/continuity session.
It does not establish exposed TAP connectivity, an electrically qualified
controller, or permission to attach anything. Tool status: **PLAUSIBLE TOOLCHAIN**.
External OnCE remains the first candidate; hook fallback is not promoted.

## A. Identity

**STRONGLY SUPPORTED, photographed board only:** DSPB56724AG, 144-pin LQFP.
The primary board investigator's component list identifies that part and the
under-shield close-up marking appears consistent. This improves the previous
firmware-family inference; it does not establish the user's actual part, board
revision, silicon mask or debug/security state. The bottom photograph reads
“Circuit Rhythm/Tracks MAIN BOARD V3.2 FP002099-01”, with 2020 Novation/Focusrite
marking. The STM32 photograph clearly shows STM32F745VEH6.

Sources: [board investigator repository](https://github.com/userx14/CircuitTracksReverseEngineering),
archived README line6 and photos with Git blob hashes in photo-retrieval.json.
**VERIFIED documentation / CONDITIONAL device applicability:** NXP EC Table19
specifies DSPB56724AG as 144-LQFP, 20×20mm, 0.5mm pitch; DSP56725 is documented
as 80-LQFP, 14×14mm, 0.65mm pitch. Package pins for both are exported to avoid
substituting a family or EVM connector pinout for a board net.
[NXP datasheet](https://www.nxp.com/docs/en/data-sheet/DSP56724EC.pdf).

**VERIFIED pinned RM Chapters3/22:** two DSP56300 cores, each with OnCE;
external TDI → JTAG1/core1 → JTAG0/core0 → external TDO. Each instruction
register is four bits; a complete IR update shifts eight bits. JTAG1 supports
IDCODE; JTAG0 does not. Documented JTAG1 ID is 0x01ED001D; that does not identify
which core runs selection0/channel0. Coupled debug entry is configurable.
No external core-selection pin is established; selection uses the chained IRs.
Firmware upload endpoint/channel labels must not be equated with physical cores.

## B. Candidate package pins

**VERIFIED documentation, CONDITIONAL actual unit:** RM PDF48/49 Figures2-1/2-2,
PDF74 Table2-21; EC pin diagrams corroborate. These are package pins, not a
header wiring diagram. Complete signals/power lists are in tap-pins.csv.

|Signal|DSP56724 144-LQFP|DSP56725 80-LQFP|Direction/reset/pull|
|---|---:|---:|---|
|TMS|101|55|input at reset, internal pull-up|
|TCK|102|56|input at reset, internal pull-up|
|TDI|103|57|input at reset, internal pull-up|
|TDO|104|58|output, tri-state at reset; driven Shift-IR/DR; no pull specified|
|RESET|111|63|active-low Schmitt input, internal pull-up; resets both cores|
|PINIT/NMI|105|59|input/pull-up; PLL initialization at reset, then negative-edge NMI|
|SCAN|144|80|manufacturing-test input/internal pull-down; normal low|
|Nearby IO_VDD example|107|49|nominal3.3V I/O supply; actual net/Vref unmeasured|
|Nearby IO_GND example|108|50|actual board ground must be identified|

**VERIFIED package documentation:** no distinct external TRST, DE/debug-ACK,
DEBUG_REQUEST or TAP-select pin is listed. RM22 shows TRST inside the controller
and describes its reset source as on-chip POR; this is not permission to assign
TRST to an unknown pad. SCAN, PINIT/NMI and MODA/B/C/D boot pins are not substitutes.
RESET release latches boot modes; resetting destroys the desired natural epoch.

## C–D. Board exposure and header discrimination

**VERIFIED visible image observation:** J3 has ten gold pads/alignment holes and
Programming Debug silkscreen. The investigator's debugHeader.svg labels SWDIO,
SWCLK and GND. Other labels include resistor nodes to 3.3V/Vreg and explicitly
uncertain SWO/reset. **STRONGLY SUPPORTED:** this is an STM32 SWD header.
Neither the physical footprint nor a resistor label proves a DSP connection or
safe direct voltage-reference pin. Actual continuity remains unmeasured.

**VERIFIED visible image observation:** a separate six-through-hole-pad footprint
beside the DSP is visible in the under-shield close-up, with one end square.
**UNRESOLVED:** function, orientation, nets and exact connector label. Six pads
could accommodate four TAP signals plus reference/ground, but count and location
do not prove that allocation. No package-to-pad continuity can be traced from the
available imagery. Hidden PCB layers and package/shield occlusion are not inferred.
Routing result is **E: impossible to determine from available imagery**.

Discriminators for a future separately authorized identification session: net
continuity to candidate DSP pins101–104 versus MCU SWDIO/SWCLK, actual I/O
reference/ground, orientation, pulls and any conflicting factory-test net.
No pin-to-header mapping is supplied here. Sources: board-evidence.csv and
header-comparison.csv. Prior local project materials inspected were manuals,
analysis reports and generated images; no schematic was established. Public
photo evidence is now archived. This is a bounded evidence review, not a claim
that no other service/PCB material exists.

## E. Electrical gate

**VERIFIED device specifications / actual board UNRESOLVED:** nominal IO_VDD3.3V
(EC operating range3.14–3.45V). Core power is a separate domain and cannot serve
as JTAG Vref. Require actual board ground and I/O-reference identification,
controller-level compatibility, isolation against probe power/back-power,
orientation, pulls/loading, and qualified power/connection sequencing. Target
power must come from its normal supply; probe target-power output disabled.

EC specifies VIH maximum VIO+2 and absolute VIN maximum5.5V. Consequently the
documentation does **not** support a categorical claim that silicon excludes all
5V tolerance. These limits also do not authorize a 5V adapter or drive on the
unknown board network. Use an actual target-referenced, compatible controller.

EC Table13: TCK maximum min(10MHz,Fsys/3), minimum cycle100ns and high/low pulse50ns;
rise/fall≤3ns; TMS/TDI setup5ns, hold25ns; TDO valid≤44ns. No board-safe initial
clock has been selected: actual clock/loading/adapter timing remains unknown.

**Minimum future qualification checklist, not instructions to act now:** actual
part/package/board orientation; powered-off net/ground continuity; subsequently
authorized Vref measurement; adapter input/output/power compatibility; reset and
TAP topology; clock/pull constraints; and controller startup review proving no
automatic reset, P-memory software breakpoints, target initialization, watchdog,
clock/PLL or cache writes. DSP lock/access state remains unknown; MCU option bytes
do not answer DSP security. Refuse connection if voltage, ground, TAP identity,
electrical compatibility, reset consequences or automatic target writes are unknown.

## L–S. Physical decision

**READY-FOR-PIN-VERIFICATION:** only a candidate footprint on a public revision is
supported. No exposed DSP TAP has been verified on the actual unit. A future
limited powered-off board identity/continuity session is justified in principle,
and requires separate authorization. **Probe attachment justified now: NO.**
**Flashing justified: NO.** Neither physical action is requested or authorized
by this report. No hook, RAM allocation, patch, firmware getter, or board command
was created or performed.

**Single best next step:** separately authorize a limited powered-off inspection
and continuity identification on the actual board to determine whether the
six-pad candidate reaches DSP TCK/TMS/TDI/TDO and valid reference/ground. No probe
attachment until both physical and controller gates close. See controller and
coherence notes for the independent remaining gates.
