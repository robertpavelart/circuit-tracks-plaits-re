# Project overview — final pre-hardware review

**OPERATIONAL PREFLIGHT = UNQUALIFIED. POST-READY ALLOCATION CENSUS = UNQUALIFIED. USB STORAGE JOINT PATH = PASS.**

Current through 17 October 2026 (Europe/Moscow). The Phase63 artifact is a temporary NOR diagnostic, not Plaits firmware; it has not been hardware-tested. Phase67's FINAL PREFLIGHT CLOSURE = PASS remains valid only within its scoped model. No concrete offline firmware blocker has been demonstrated; the accepted residual software uncertainty is post-READY indirect allocation reachability with an eight-byte modeled heap gap. Tools remain locked. Risk acceptance is neither proof nor authorization to use them.

Evidence precedence: [final allocation decision](<research/final-indirect-resolution/findings.md>) controls the remaining software proof boundary; [USB joint-path closure](<research/final-two-check-closure/usb-joint-closure.md>) records 36 passing focused cases. [Phase67](<research/phase67-final-safety-disposition/findings.md>) retains its bounded configuration/query/authorization-to-capture-entry scope. The frozen [package audit](<research/final-hardware-test-package/final-cheap-checks.md>) preserves the earlier two-gap history, with a current supersession notice. No model PASS is physical proof.

The long-term design below is retained. Current firmware is a temporary evidence diagnostic, not an implemented Plaits product. User risk acceptance and the reported favorable review do not change the allocation census or unlock tools.

# Project goal

The final design is custom Circuit Tracks application firmware with Track 1 = Plaits, Track 2 = Plaits, Track 3 = Plaits and Track 4 = Plaits. Stock Synth1/Synth2 generation is eventually removed from the custom application. Restoring official Novation application firmware restores those original engines because they are contained in that image. The bootloader is never to be modified.

**UNKNOWN:** complete four-track implementation, final memory fit and runtime admission. This document records intended design, not implemented functionality. The unchanged Phase63 candidate is the temporary diagnostic reviewed through Phase67; no hardware test occurred. Exact current identity and tooling locks are in CURRENT_STATUS.md.

# Final voice architecture — design

Four melodic tracks default to mono. `MAX_TRACKS_PER_MODEL = 2` and `MAX_POLY_TRACKS = 2`. Each engine's maximum polyphony must follow actual CPU/state cost: light engines may potentially reach Poly4; heavy engines may require mono or Poly2. Share model code and immutable resources where possible, with independent per-track/per-voice mutable state. The conceptual upper bound is not a guaranteed runtime configuration. Two tracks using a model may still exceed two voices if polyphony is admitted; those costs remain **UNKNOWN**.

# Pinned Plaits source

**PROVEN:** eurorack revision `08460a69a7e1f7a81c5a2abcc7189c9a6b7208d4`; stmlib revision `e3bd7c9cc00e4364166f9905c0509b6ffd0535ec`. The pinned source has 24 model slots. An explicit UI-pad → engine-enum mapping is required; registry order must not be assumed to equal UI order. Modal is internal registry model 20, not necessarily pad 20.

# Intended 4×8 Preset UI — design

Pad numbers are 1-based. This is agreed design, not a completed UI.

| Pads | Page 1 | Page 2 |
|---|---|---|
| 1–8 | Original first eight models; green | Extra/new eight models; yellow |
| 9–16 | Original second eight models; pink | Completely inactive |
| 17–24 | Preset slots | Same presets |
| 25–27 | Extra control pages | Same control pages |
| 28 | Bank toggle | Return to page 1 |
| 29–32 | Mono / Poly2 / Poly3 / Poly4 | Same polyphony controls |

When a model is assigned to two tracks, its pad becomes unavailable on the remaining tracks. Preserve green/pink/yellow family colors. Polyphony controls must respect eventual engine admission limits.

# Parameter-page concept — design

| Knob | MAIN | VOICE | MOD | TRACK |
|---:|---|---|---|---|
| 1 | Frequency/Tune | Root octave | LFO rate | MAIN/AUX balance |
| 2 | Harmonics | Fine tune | LFO shape | Stereo width |
| 3 | Timbre | Glide | LFO → Pitch | Pre-filter drive |
| 4 | Morph | Pitch-bend range | LFO → Harmonics | Filter type |
| 5 | Envelope/FM → pitch amount | Internal envelope decay | LFO → Timbre | Cutoff |
| 6 | Envelope → Timbre | LPG response | LFO → Morph | Resonance |
| 7 | Envelope → Morph | LPG decay/ringing | Velocity → Timbre | Reverb send |
| 8 | Level/Accent/Velocity context | Retrigger/legato | Velocity → Morph | Delay send |

Engine-specific parameter semantics must still be verified directly against pinned Plaits source before final implementation. The UI/page requirements above are recorded from the current snapshot request.

Evidence: [four-track resource architecture](<../notes/four-track-plaits-resource-architecture.md>), [Modal source closure](<../notes/plaits-modal-dsp-port.md>).

# WHY THE DIAGNOSTIC EXISTS

Authentic$82000–$821FF data is needed for initializer replay and resource-reclaim qualification, including P:$0282–$0386. The diagnostic is temporary. Its geometry gate avoids trusting unknown current-unit filesystem geometry: the host validates the retained first-mount mapping before authorizing a fixed read for the same epoch. Successful authenticated capture is a prerequisite for resuming blocked resource work; it does not itself qualify reclaim or implement Plaits. Optional$81000 is separately authorized.

The long-term goal remains4 Plaits tracks, `MAX_TRACKS_PER_MODEL = 2`, `MAX_POLY_TRACKS = 2`, and engine-dependent polyphony. These are future design goals, not diagnostic features. See [CURRENT_STATUS.md](<CURRENT_STATUS.md>).
