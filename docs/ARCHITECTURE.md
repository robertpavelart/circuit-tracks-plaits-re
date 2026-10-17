# Architecture

## Current long-term target

The active design target is a four-track Plaits architecture inside Circuit Tracks.

The previous single selected stock-synth / VariableSaw interception design was an important proof-of-concept path, but it is no longer the current architectural target.

Current high-level goal:

```text

Circuit sequencing / track workflow

        ↓

four melodic track front ends

        ↓

Plaits-derived engine selection

        ↓

shared model code

        ↓

independent per-track state

        ↓

existing Circuit mixing / effects / output path where feasible

```

## Track policy

Current planning constraints:

- four melodic Plaits tracks;

- default mono;

- `MAX_TRACKS_PER_MODEL = 2`;

- `MAX_POLY_TRACKS = 2` globally;

- model-specific polyphony limits;

- shared model implementation with independent state per track.

These are architecture constraints, not yet a final hardware-qualified performance guarantee.

## Plaits model scope

The long-term target remains the full Plaits model set, subject to final memory and CPU qualification.

The exact UI mapping and per-engine polyphony policy remain implementation work.

## Current firmware is diagnostic-only

The current Phase63 `N63DEV` candidate does **not** contain Plaits.

Its purpose is to obtain authentic NOR/QSPI evidence from `$82000` needed for final resource qualification.

Therefore the current architecture work is temporarily gated by evidence acquisition rather than synth-engine integration.

## Memory/resource dependency

Authentic `$82000` coefficient data has not yet been captured.

Until it is:

- reclaim of `P:$0282-$0386` is not finally qualified;

- the safe final P/X/Y budget remains **UNKNOWN**;

- the final placement strategy for all Plaits resources remains open.

## Audio/DSP constraints already established

Research to date establishes several important constraints:

- Circuit audio processing uses 32-frame blocks;

- Plaits voice rendering naturally uses 12-sample blocks;

- an exact 12→32 FIFO wrapper has been demonstrated in offline work;

- CPU budget is a primary limiting resource;

- some Plaits engines have additional state/resource costs that must be accounted for separately.

The final architecture must respect real hardware timing, not only offline model feasibility.

## Stock behavior retention

Where feasible, retain:

- Circuit sequencing workflow;

- drums;

- mixer;

- effects;

- project behavior;

- rollback path.

Exact retention boundaries remain implementation-dependent.

## Historical first-PoC design

Earlier work explored a conditional interception around stock DSP flow, replacing one selected mono path with a VariableSaw/Plaits-derived renderer while retaining stock request/completion and post-processing.

That design remains useful historical evidence, but it is **not** the current project target.

See `docs/STATUS.md` and `docs/ROADMAP.md` for the active state.

Current detailed authority: [CURRENT_STATUS.md](CURRENT_STATUS.md).
