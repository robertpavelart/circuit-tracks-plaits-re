> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase20B4 — event and retained-state admission

2026-10-07. **PARTIAL / no selected event / no replay.**
Reports under`builds/phase20b-projectassoc/final-v2/`:
`selected-event.json`, `macro-state.json`, `p657-material-inputs.csv`,
`y91-provenance.json`, `history-opportunity.json`, `qualification.json`.

**VERIFIED stored macro values, zero-based indices0..7:**
authored`[0,0,46,83,0,0,48,0]`;
cached`[0,126,11,84,51,58,73,0]`.
These are serialized values, not a selected event's active macro snapshot.
All four assignments per macro are exported. No neutral macro state is used.

**CALCULATED conditional common boundary:** complete original macro recompute
and callbacks using these stored values produce differentX2E8,X2EA,X3E7
transfers. The cached preset is materially different at that boundary.
There is no proof that a later original automation event converges its effective
controls to the authored context, and no proof that such convergence is
impossible for every cached event. Event-time equivalence is **INSUFFICIENT
EVIDENCE**. Overall qualification staysPARTIAL, with event-use admissionfalse.

## Y91 frontier

P657 structure is imported from20B3, not reanalysed. The20 modulation rows
are byte-identical in both patches. Row0[4,4,113,12],row2[7,0,68,12] retain
the same source/factor/destination literals. Complete stored-macro recompute
has zero corrections to row0/2 depth IDs60/68(hex): no selected macro destination
51/53. Their nominal signed depths49/4 therefore remain equal under that premise.

**CALCULATED conditional target words:** destination12 conversiontype2 selects
285EA TBB entry285F0→28640. The curve805A340[49]=75 and[4]=4 yields
X3D0=`31FFCE`,X3D2=`02AAA8` through original5555 multiplier/shift and upper24
transport. These are target values. Current smoothed amountsX2FE/X308 remain
**UNRESOLVED**, with1B89 prior-value/update-history dependence.

Source reads remain row0Y17C*Y17C and row2Y126*Y17D, withfactorY10.
Y17C is itself smoothed before use. P6ED also usesX2E9,Y131*X2EA,
Y135*X2EB and the accumulated route value. Cached macro differences affect
X3E7's target,X2EA and envelope parameters upstream of these source histories.
Equal row literals do not prove equalY91.

The exact preceding state still needed is:

* priorY17C, X5C3 and X40 at674; sourceY126 at its selected read;
* envelope/voice historiesY131/Y135 and their note/gate/velocity origin;
* priorX2FE/X308 and timing/count of smoothing updates;
* priorX2E9 and update history (its target addend is now fixed flash590C);
* selected playback pattern/event, macro automation ordering, allocation and
  material SR/OMR/AGU/stack context.

No numericalY91 is exported. The conditional zero-routing terms at8F/90
remain as previously bounded; their scalar contributions differ whenX2E8 differs.

## Event and history result

No exact pattern/step/note/velocity/gate/length/event has been qualified.
The first740-offset28-byte record is retained as raw candidate data; its record
geometry is supported, but musical meanings and playback choice are not assumed.
Logicalbank0 file-patch association does not prove physical voice slot0.

Project load is a promising bounded **parameter** origin. Its full-copy and
macro-only branches do not supply numerical DSP post histories. 3602A's zero
workspace is ARM correction state, notY5AB..5AE/5B7/5B8. Existing trigger reset
ranges still exclude those six words. No project-local bounded history origin
or preceding event sequence is admitted. Boot-zero substitution is refused.

All requested exports are present.31 focused/regression tests pass, including
4096 independent macro fixtures and repeated byte-identical exports. Firmware,
previous20B/20B2/20B3 reports and renderer baselines retain their hashes.
This is host-side static arithmetic/provenance validation, with0 stock CPU
instructions, no seam replay, no Plaits and no hardware access.

**Single best next step:** trace the original sequencer/automation consumer for
project0 group0 pattern0, establishing the event-routing chain and whether
automation replaces the differing load values before its first note. Do not
use this candidate for checkpoint reconstruction until that evidence qualifies.
# Phase20B5 continuation — current event gate (2026-10-07)

**PARTIAL; event admission NO. STATIC STRATEGY EXHAUSTED.** Cachedstep0
contains two occupied four-byte records51/18/0/106 and82/2/0/106. Original
3F350..384 and3F856..89C support stored key/duration/substep/level semantics,
not an exact first audible note/velocity/gate or allocatedDSP slot. Twelve
six-substep automation lanes,1D02A accessor and3FE24 pending processing are
recovered; playback application/notification order and prior values remain
unresolved. Lane2/8/9 have52/53/15 nonFF bytes; FF is not a default value.
See project0-first-note-context.md and project0-sequencer-ordering.md.
No event-time convergence or numericalY91/history origin is established.
0 stock instructions; no hardware, patching or Plaits. Earlier suggested
static association follow-ups below are superseded by static-checkpoint-limit.md.
