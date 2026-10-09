# Circuit Tracks Plaits RE

Experimental reverse-engineering and DSP integration research for running a Mutable Instruments Plaits-derived synthesis engine inside a Novation Circuit Tracks.

> **Current status:** research / offline integration design only. No flash-ready custom firmware has been produced.

## Project goal

Long-term target:

- Synth 1 / Synth 2 can use a Plaits-derived engine.
- MIDI 1 / MIDI 2 may eventually host internal polyphonic voices if CPU/memory allow.
- Retain stock Circuit post-processing where practical.
- Preserve a safe path back to original firmware.
- No opening, soldering, probing, or hardware debugger access.

First milestone:

**One mono VariableSaw/Plaits-derived voice on one selected stock synth path, while the rest of the machine stays stock.**

## Current architecture candidate

```text
stock request/completion machinery
        ↓
stock lookup / coefficient ramps
        ↓
stock 32-word combiner
        ↓
candidate interception P:0x9B9
        ↓
Plaits-derived mono32 replacement
        ↓
restore required live state
        ↓
original P:0x9D9
        ↓
stock post-processing
```

## Already demonstrated

- Exact Circuit firmware SYX → BIN → SYX round-trip.
- DSP payload extraction and mapping.
- Bounded execution of original DSP code in a DSP56300 emulator.
- Standalone fixed-point VariableSaw-derived renderer as real DSP56300 code.
- Bit-exact output against an independent integer oracle.
- Native DIV optimization.
- Register/scratch optimization.
- Tightened reachable timing bound.
- Candidate stock seam and software-only live-patch architecture.

## Current blocker

The 7-word persistent VariableSaw state cannot yet be placed in a proven-safe X-memory region under the retained-stock design.

Next research target: qualify a **mutable P-memory-backed 7-word state object** and bound its MOVEM cost.

See [docs/STATUS.md](docs/STATUS.md).

## Repository policy

Do not commit proprietary Novation firmware, extracted DSP payloads, vendor PDFs, user projects, sample packs, or device dumps.

See [docs/REPOSITORY_POLICY.md](docs/REPOSITORY_POLICY.md).

## Device safety rule

This project has a hard constraint: the Circuit Tracks is not opened or physically probed.

Future hardware interaction, if reached, should use normal external interfaces only. No modified firmware should be sent to hardware until the recovery / rollback path is independently qualified.

## Disclaimer

Unofficial research project. Not affiliated with or endorsed by Novation, Focusrite, Mutable Instruments, NXP, or upstream community projects.
