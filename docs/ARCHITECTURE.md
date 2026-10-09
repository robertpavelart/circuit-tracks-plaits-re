# Architecture

## First-PoC concept

```text
stock request pass
  ↓
stock completion pass
  ↓
lookup / coefficient preparation
  ↓
stock combiner
  ↓
conditional dispatcher
  ├─ non-selected → stock path
  └─ selected bank0/slot0
       ↓
     load Plaits state
       ↓
     VariableSaw render
       ↓
     overwrite mono32 output only
       ↓
     save Plaits state
       ↓
     restore stock live state
       ↓
     JMP P:0x9D9
       ↓
     stock post-processing
```

## Constraints

- Do not skip request/completion machinery.
- Do not skip the stock combiner.
- Preserve auxiliary streams used by stock post modes.
- Leave natural `X:0x2C66` untouched.
- Preserve stock fallback for all non-selected paths.
- Keep the stock allocator for first PoC.

## Initial controls

- pitch: stock tracked pitch around `Y:0x12F`
- PW: fixed 0.5
- shape: fixed known value

Final knob routing is deferred.

## Long-term concept

1. MODEL
2. HARMONICS
3. TIMBRE
4. MORPH
5. stock cutoff
6. stock resonance
7. attack
8. sustain/release

Conceptual voice target only:
- Synth1: 1
- Synth2: 1
- MIDI1: 3–4
- MIDI2: 3–4

This is not yet a feasibility claim.
