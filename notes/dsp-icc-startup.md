# Phase 19B-HANDOFF — peer readiness and progress publication

2026-10-06. **VERIFIED stock data flow / DOCUMENTED conditional device map.**
Worker was read and decoded for static analysis only; not emulator-loaded or
executed. Its original SHA256 is
`adf8da1b2b889d069eb52935dbdc4ce9092210d29df719937ca5ac5f62dfa91a`.
Boot count364, load0; payload1092 bytes, P[0,16C), entryP0→P100.

| Worker P | Original words | Operation |
|---|---|---|
|0|0AF080 000100|JMP100|
|100|07F411 000000|MOVEP #0,X:FFFF91|
|102|013F09|BCLR #9,X:FFFFBF|
|103|013E29|BSET #9,X:FFFFBE|
|104|013D29|BSET #9,X:FFFFBD|
|105|65F400 030002|R5=030002|
|107|657000 030000|X:30000=R5|
|109|6D7000 FFFFD7|Y:FFFFD7=R5|
|10B|05F425 00FFFF|M5=00FFFF|

**VERIFIED role of30002:** an initial cursor address, not an arbitrary command
ID. Later worker117 reads the shared tail X30000;11A subtracts R5. Worker120
reads X:(R5) intoR0;125 reads X:(R0);126 replaces X:(R5)+ with that result.
121/128 republish R5 via the same YFFFFD7. Main779 reads YFFFFD4 and compares
the progress against expected count/cursor state at775..77D. Main initial
102/104/106 polls for equality30002. The initial pointer publication therefore
also acts as a readiness rendezvous. No synth/audio semantic inference follows
from this constant alone.

**DOCUMENTED device wiring inside ICC:** each core's write-only ICDR3 at
YFFFFD7 is reflected in the other core's read-only ICDR4 atYFFFFD4. This directly
matches worker109 and main102. Reset data is0, not30002. Read service clears the
corresponding interrupt flag; acknowledgement of a maskable transfer sets ACK
to inform the sender. IRQ enable, priority and masks matter even if firmware
polls rather than enters an ISR. Exact empty/disabled-transfer ACK behavior
is not fully established by the reviewed text; do not invent those transitions.
[DSP56724RM §13.1.2, §13.2.2.5–10](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf#page=251).

**VERIFIED upload ordering:** ARM08029294 sends channel0 first;080292A6 sends
channel1 second. Each SHI record's documented completion starts that program at
P0. Classification **B: main upload/start contract before worker**, with explicit
ICC synchronization. Both can then run concurrently. Exact first main102 versus
worker109 interleaving is **UNRESOLVED**; upload order cannot establish that30002
is already present on the first read. Main waits at102..106, not at100. It can
execute earlier instructions before publication only if its own handoff is
defensible; it cannot exit this poll before matching the peer pointer.

Minimum future contract, **specification only**:

1. Separate private P/X/Y for both logical program roles; explicit common
   storage for sharedX30000. Do not alias equal private X/Y addresses.
2. Initial ICDR3/4 reset data0 only at a documented chip reset boundary.
   Application handoff values remain unknown until ROM/peer ordering is proven.
3. Original worker105 definesR5;107 publishes shared tail;109 publishes ICDR3.
   Preserve this ordering and produce mainICDR4 from the peer write, not a timer
   stub, forced value or initialization seed.
4. Main102 reads and acknowledges the ICC transfer with documented flag/ACK
   behavior;104/106 compare/poll. Repeated data reads are not a one-shot command
   dequeue. Log data and all reached control side effects.
5. Establish ICCR3.MIE, PIC priority, SR masks and pending state before injecting
   any interrupt. No interrupts/events were injected here.
6. Stop before any subsequent worker handshake or queue operation not covered by
   a separately justified contract; do not implement a broad worker.

**Worker gate CLOSED:** before109, worker100 and102..104 already access
unmodeled X peripherals, and its inherited loop/interrupt/mode state is not
proven. R5 itself is explicitly initialized before publication and no R/N/M
indirect addressing is needed for107/109. That local fact does not justify
recursively guessing the worker's startup state or executing it from105.
Physical channel-to-core numbering remains **UNRESOLVED**, though complementary
program roles and documented peer-register pairing are corroborated.

Evidence: `icc-contract.json`, `selection0-channel1.asm`, `arm-ordering.json`
under `builds/phase19b-handoff/final/`. No worker completion was fabricated.

## Phase19B-ROM exit/timeline status — 2026-10-06

Official56720/21 comparison corroborates the reviewed ICCpairing; actual ROMICC
residue remainsunknown. Laterworker30002 publication is not a ROMexit field.
Worker receives no uploadedshim, unlike main; two separate handoff manifests
remainblocked. Worker100 explicitly writes0 toXFFFF91HCSR (HENdisabled), but
this does not make allstatus/FIFO/interruptstate known or qualify its GPIOreads.

Deterministic staged original execution could cover a bounded startup rendezvous
after both state/peripheral gates pass. It must log the realworkerwrite and
mainpoll/ACK, preserve ordering/private/shared state, and make no unproven clock
claim. This remainsHYPOTHESIS/design; no worker ran and no30002 waspreseeded.
