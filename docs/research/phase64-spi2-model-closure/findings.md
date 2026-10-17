> Saved phase-scoped evidence; original next-step instructions are historical. [Current project state](../../CURRENT_STATUS.md).

# Phase64 — SPI2 offline model closure

**FINAL PREFLIGHT CLOSURE = UNQUALIFIED.** The original zero-SR blocker is resolved in a bounded SPI2 register subset. Full startup still requires faithful16-bit SHI/DMA recipient handling and the resource-backed DSP table job; startup-to-capture and complete postboot allocation coverage remain incomplete. No new firmware defect is demonstrated. No candidate was modified or generated; no hardware, MIDI port or firmware transmission was used.

| Requested result | Conclusion | Confidence |

|---|---|---|

|1 Register identification|SPI2_SR, offset08/reset0002; status/FIFO and error-clear semantics documented|PROVEN vendor definitions|

|2 Accessors / stop cause|31 observed PC/access combinations, exact function listings; zero-shadow SR prevented TX/RX progress|PROVEN within traced prefix; post-frontier closure UNKNOWN|

|3 Device role|DSP bootstrap and SHI control/readback link, established on both ARM and DSP code|PROVEN functional role; exact board nets UNKNOWN|

|4 Minimal normal model|CR/mode setup, byte FIFO, TXE/RXNE, delayed transfer and DR side effects; boot-ready and four exact job contracts|PROVEN bounded tests; complete normal-boot peer model UNKNOWN|

|5 Negative sanity|Normal/delayed exact output; absent completion/disabled SPI block at3798A; eleven peer checks|PROVEN|

|6 Startup continuity|Same-state NOR/SD/geometry prefix advances past four procedural DSP jobs; stops at width command200100|PROVEN prefix; complete path UNKNOWN|

|7 Postboot allocation|176 prefix requests enumerated; later lifetime not reached|PROVEN prefix; complete audit UNKNOWN|

|8 Failure classification|A: missing16-bit SHI/DMA recipient and subsequent table-job model, not demonstrated candidate defect|PROVEN explicit model refusal; future full behavior UNKNOWN|

|9 Final reassessment|No PASS: continuity and allocation gates still open; old passing suites retained without unnecessary reruns|UNKNOWN overall|

The exact remaining mechanism begins at **SHI width command200100**, emitted by ARM295E4/29600 and consumed through DSP113→12D. It precedes the16-bit coefficient DMA upload and Y:$2C selector0 job0D1000. A model that merely acknowledges DMA and returns800000 would omit the actual recipient/work. The four procedural jobs are now independently completed; their earlier32-step probe did not establish a hang. No Phase63 change is justified by this model gap.

Reports: [register-model.md](<register-model.md>), [accessors.md](<accessors.md>), [device-role.md](<device-role.md>), [negative-tests.md](<negative-tests.md>), [continuity-allocation.md](<continuity-allocation.md>). Machine-readable gates: preflight-verdict.json (local-only reference: `builds/phase64-spi2-model-closure/preflight-verdict.json`; not distributed). The final geometry record is `110000000180003480908f01`.

The **smallest next experiment** is to carry the first actual200100 width command and the following DMA TX buffer into an explicit16-bit SHI recipient, preserving byte order and data-word shift, then execute the unchanged DSP selector0 job with that exact modeled upload. Keep its actual continuation until native1DA8 completion and continue the same ARM instance. Record the inherited NOR payload's synthetic provenance separately; it cannot authenticate current-unit coefficients. Do not force mailbox values, skip read loops, substitute a running fixture, modify candidate firmware, or reopen NOR mutation research.

Remaining hardware-only unknowns are real heap/stack margin, physical bus/clock/error timing, ADC/calibration values and live USB/host interoperability. These are separate from the remaining **offline** DSP-peer/continuity/allocation gaps. H4's already proven lack of bounded unwind is not relabeled unknown; the existing quarantine/power-cycle containment policy still applies.

**PROVEN preservation:** all199 Phase63 manifest files verify unchanged, including its candidate, old test evidence, locked host/uploader and its UNQUALIFIED verdict. BIN SHA `edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9`; SYX SHA9b420521a366c65c13fb871778fdbab612ca126cbb4ad60d0fd5bc12ecd253da. The inspected SPI2/DSP-host code also equals clean SC35D8. No install/rollback,28-native,31-DMA or32-host tests were repeated because their image and scope are unchanged. See identity-preservation.json (local-only reference: `builds/phase64-spi2-model-closure/identity-preservation.json`; not distributed).

FINAL PREFLIGHT CLOSURE = UNQUALIFIED
