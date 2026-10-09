# Phase 17 — Circuit Tracks board observation access

2026-10-06. Public-document/source research only; no hardware/disassembly of a
unit, continuity measurements, port enumeration, JTAG/SWD/analyzer connection.
No probing recommendation or wiring recipe is authorized by this assessment.

## Sources and exact silicon conflict

**SOURCE-DERIVED first-party board research:** the public
[CircuitTracksReverseEngineering README](https://github.com/userx14/CircuitTracksReverseEngineering)
lists DSPB56724AG under the RF shield, SDRAM IS42S16160G and anLVT573 latch.
It reports aTC2050-compatible debug header and links aJ3 photograph plus
debugHeader.svg. SPI2 MCU signals are reported asPC1MOSI,PC2MISO,PD3SCK.
These are public author's board assignments, not verified pad continuity or
a complete DSP netlist for the user's unit.

A [teardown discussion](https://www.reddit.com/r/novationcircuit/comments/1g6r35j/)
reports Tracks/Rhythm mainboardV3.2 and later lists DSPB56725AG. That conflicts
with the repository. Manufacturer Table19 identifies56724AG and56725AF;
the reported56725AG spelling is not corroborated by that table. Possible typo
or board variation remains **UNRESOLVED**, not an assumed revision change.
[NXP DSP56724EC](https://www.nxp.com/docs/en/data-sheet/DSP56724EC.pdf).

**STRONG HYPOTHESIS:**56724AG fits the repository marking/SDRAM/latch and existing
firmware external-memory use better. Exact unit model/package/marking and mask
are not VERIFIED. Both candidates shareDSP56300 OnCE, so the debug gate does
not depend on resolving that conflict first.

## Access ledger

| Item | Evidence/status | Limit |
|---|---|---|
|STM32 debug header|SOURCE-DERIVED publicTC2050-compatible header report/J3 photo reference; gist mentionsstlink pinout|Exact numbered pin signals, orientation, electrical ratings and board revision UNRESOLVED|
|DSP JTAG/OnCE pads|UNRESOLVED|No documented pad-to-TDI/TDO/TCK/TMS/TRST mapping recovered|
|STM32 SWD/SWO|UNRESOLVED exact pads|STM32 silicon capability or programmer name does not prove board route or DSP access|
|Manufacturing/test points|UNRESOLVED net functions|Pad shape/labels alone not functional proof|
|SPI2 link|VERIFIED firmwareSPI2/SHI; SOURCE-DERIVED MCU signals above|Physical safe analyzer access points and chip-select/commandlane continuity UNRESOLVED|
|ESAI/codec link|VERIFIED firmwareESAI processing; SOURCE-DERIVED AK4556VT board component report|Exact lines/slots/pads/voltage/loading UNRESOLVED|
|ICC/shared memory|SOURCE-DERIVED internal candidate-silicon modules|Not an externally routed bus inferred from dual endpoints|
|External SDRAM/EMC|SOURCE-DERIVED boardSDRAM/latch report and firmware external domains|Does not expose private low/highX accesses or on-chipICC traffic|
|GPIO lane/select/handshake|VERIFIED firmwareGPIO transport controls|Exact manufacturing-pad assignments UNRESOLVED|
|Public schematic|UNRESOLVED; none established in reviewed sources|No complete authoritative Tracks netlist located; not claim none exists|

Public references, not inspected images:

- [J3 photograph](https://github.com/userx14/CircuitTracksReverseEngineering/blob/master/Documentation/Mainboard-Photos/j3_debug_port.png)
- [Debug header diagram](https://github.com/userx14/CircuitTracksReverseEngineering/blob/master/Documentation/Diagrams/debugHeader.svg)

README retrieval succeeded; directory/image/diagram retrieval throughweb failed.
Shell network retrieval was denied by the sandbox; no escalation, download,
adapter or hardware action followed. Thus no imagined pin numbers or visual
confirmation. Research may later resolve the public files without hardware.

## Passive signal limits

Future SPI/ESAI/GPIO capture could correlate existinghost commands and audio
outputs only after route, voltage, input-only loading and loss-free timing are
qualified. SPI needswidth/commandlane context. No active5E/identity query should
be inserted into an allegedly passive capture. No guaranteed zero electrical
disturbance from a logic analyzer is claimed.

SPI traffic cannot prove absence of internalDSP-only writes. ESAI gives audio
behavior, not privateRAM data. GPIO gives timing context. On-chipICC/shared
memory is not an exposed board bus. Boundaryscan JTAG samples externalpins,
and EXTEST/CLAMP/HIZ can actively alter them; not a compliantRAM observer.

**Gate:** board access to a qualifying passive DSP state facility remains
NOT-YET-DETERMINED. Keephardware disconnected. See
[dsp-debug-observation.md](dsp-debug-observation.md) for the offline alternative.
