# Safety

## Physical device

Hard project rule: **do not open or physically probe the Circuit Tracks**.

No soldering, continuity probing, JTAG/OnCE/SWD, test-pad access, or internal wiring.

## Flashing gate

No modified firmware should be sent to hardware until:
1. offline DSP integration passes
2. firmware container checks pass
3. update protocol is understood
4. rollback/recovery is proven
5. original firmware is preserved
6. a broken DSP payload cannot strand the unit without USB recovery

## Evidence labels

Use consistently:

VERIFIED / TESTED / MEASURED / CALCULATED / BOUNDED-PROOF / CONDITIONAL / HYPOTHESIS / UNRESOLVED
