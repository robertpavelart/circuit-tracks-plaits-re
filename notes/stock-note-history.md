> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase20B3 — exact-patch note/history frontier

2026-10-07. **UNRESOLVED event; numerical replay REFUSED.** Bank0/slot0
is the prior bounded source binding, not a recovered allocation outcome.
Evidence: `builds/phase20b-inputrec/final-v3/selected-note-event.json`.

**VERIFIED:** the same cached archive contains four160780-byte project files.
Installed Components conversion code places two340-byte synth patch views
starting158996 (the680-byte copy witness is exported). Project0 has the
same16-byte `Rudi saw poly` name at158996. Its340-byte record differs from
the already selected standalone patch at offsets:

`35,221,238,255,272,289,306`.

The selected/project values respectively are:
`63/64,0/126,46/11,83/84,0/51,0/58,48/73`.
Installed patch mapping places macro slots at204 with17-byte stride;
six of these differences are macro-record words. A same-name record is not
silently substituted. An exact340-byte selected-patch search finds no match
in any of the four cached projects. This is a **TESTED byte comparison**, not
proof that no semantically equivalent event could exist. Equivalence, track/
bank association, sequencing and prior active corrections remain unresolved.

The project files are preset/sequence data, not DSP register/history traces.
No project notes are claimed decoded from guessed format fields, and no
literal note, velocity or middle C is manufactured.

**VERIFIED original event path**, retained from Phase4:
497CA nonzero note-associated level→21DD4→21D86→219E8 allocation→21246
event publication. Bank0 allocation considers slots0..5; it does not promise
slot0. Selection depends on lifecycle/state and DSP readback. Staged note and
level resideT+A/T+B;S+2 receives level²>>7;S+9 receives adjusted note.
Y159 target,Y12F tracked state,Y15C seed and mailboxX57A have original
instruction-backed producers. Their selected numerical values are **UNRESOLVED**.

The trigger word can select distinct reset/update actions. Trigger32C..33E
does not initialize all post histories. The trigger path calls657 at33F,
then later37A→4D5→37C calls657 **again** before37E→387. Starting from the
second657 without its first call/history is not a natural event replay.

`selected-note-event.json` keeps note, velocity, pitch, flags, gate and event
null. `history-initialization.json` admits no origin. No full authentic boot
is requested as a shortcut. The best next source investigation is to qualify
project0's original event-to-bank association and the seven patch differences
for material equivalence, including macro correction state, before selecting
any numerical event/checkpoint. If that cannot supply the required context,
explicitly retain the missing-evidence result; do not default the runtime.

## Phase20B4 association result

The seven fields are now identified:keyboardOctave plus six stored macro
values, not changed assignment records. Original project loader ties the first
embedded patch at26D14 tologicalbank0 view+344. Identity records have literal
byte0 values0/32; native pack/patch-slot numbering remains unresolved.
Both full-copy and retained-identity macro-only paths can import the seven
differences. Conditional stored-value macro recompute proves differing controls.

No selected event is qualified. Original pattern/step geometry is recovered,
but playback selection, note-field/automation consumer, event-to-track route and
physicalslot0 allocation remain open. Cached event-time material equivalence is
INSUFFICIENT EVIDENCE; no note, velocity, gate or default macro is invented.
Next frontier:project0 group0 pattern0 original sequencer/automation consumer.
See project0-patch-association.md,project0-event-context.md andfinal-v2 reports.
# Phase20B5 continuation — allocation remains unresolved (2026-10-07)

**PARTIAL / STATIC CHECKPOINT RECONSTRUCTION EXHAUSTED.** Serialized first
occupied step0 and original note recording/state consumers are source-backed;
the sound-dispatch/allocator chain for that event is not complete. Packed
recording state is not DSP voice allocation. No slot0 is forced, no allocator
occupancy/age/release/steal state invented. Y91 retains envelope/modulation/
smoothing dependencies documented by20B3/4. New context and minimum observation
specification:project0-first-note-context.md,static-checkpoint-limit.md;
builds/phase20b-sequence/final/voice-allocation.json. No stock CPU execution.
Earlier static-next-step text below is historical; no similar broad phase recommended.
