# Project Status

## Current stage

**Phase 20C3 — P-backed persistent-state qualification (next / active research target).**

The runtime-snapshot branch is deferred for the first PoC. The current design executes inside the natural stock DSP runtime and replaces only the selected voice's final mono output.

No custom firmware has been flashed.

## Live-patch candidate

- Interception: `P:0x9B9` (conditional).
- Continuation: original `P:0x9D9`.
- Retain request/completion passes, worker/lookup behavior, phase/queue bookkeeping, six coefficient ramps, and the stock 32-word combiner.
- Replace only selected bank0/slot0 mono32.
- Leave `X:0x2C66` untouched.
- Test discriminator: `X:0xCC = 0`, `R4 = 0x5AB`.
- UI correspondence to Synth 1 remains a hypothesis.

## VariableSaw renderer

| Resource | Result |
|---|---:|
| Program | 442 P words |
| Persistent state | 7 words |
| Scratch | 3 X spill words + 16 working registers |
| Output | 32 Y words |
| LUT | 0 |
| Peak stack | 3 |

Integrated estimates:
- long-address template: 549 P words
- partial module: 713 P + 2 padding, excluding unresolved glue
- addressing delta: 587 / 673.37 / 945 cycles min / mean / max

## Timing

- reset-reachable tested max: 13,335 cycles/block
- reachable max + boundary allowance: 13,347
- derived upper: 13,379
- conditional block budget used by research model: 163,840 cycles

## Persistent-state blocker

No qualified 7-word persistent X block was found in the bounded candidate study.

Reasons:
- surviving stock writers
- later consumers
- SHI/service writes
- shared scratch reuse
- slot collision
- unresolved foreign writer domains

Do not reopen a broad X-memory search.

### Current fallback

Qualify seven mutable appended P words.

Preliminary calculated MOVEM traffic:
- min 3,855 cycles/block
- mean 4,168.23
- max 5,185

Not yet an integrated bound.

## Firmware / recovery

- Exact SYX round-trip established.
- No flash-ready modified firmware exists.
- Community research supports application base at `0x08010000` with a separate bootloader.
- Guaranteed USB-only recovery from a completely broken application is still not proven.

**Flashing readiness: NO.**

## Hardware rule

No opening, soldering, multimeter probing, JTAG/OnCE/SWD, or internal access.

Future device interaction: normal external interfaces only.

## Next gate

P-backed state is qualified only if:
1. runtime P writes are legal
2. seven words persist across blocks
3. no normal stock/service writer collides
4. no execution/fetch path reaches them
5. initialization is deterministic
6. wrapper remains bit-exact
7. cycle cost is bounded
8. image placement is structurally valid

After that: construct the first **offline executable patched DSP image** with dispatcher → Plaits → stock continuation.
