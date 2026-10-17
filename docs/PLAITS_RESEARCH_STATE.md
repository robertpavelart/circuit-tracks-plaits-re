# Plaits research state — final pre-hardware review

**OPERATIONAL PREFLIGHT = UNQUALIFIED. POST-READY ALLOCATION CENSUS = UNQUALIFIED. USB STORAGE JOINT PATH = PASS.**

Current through 17 October 2026 (Europe/Moscow). The Phase63 artifact is a temporary NOR diagnostic, not Plaits firmware; it has not been hardware-tested. Phase67's FINAL PREFLIGHT CLOSURE = PASS remains valid only within its scoped model. No concrete offline firmware blocker has been demonstrated; the accepted residual software uncertainty is post-READY indirect allocation reachability with an eight-byte modeled heap gap. Tools remain locked. Risk acceptance is neither proof nor authorization to use them.

Evidence precedence: [final allocation decision](<research/final-indirect-resolution/findings.md>) controls the remaining software proof boundary; [USB joint-path closure](<research/final-two-check-closure/usb-joint-closure.md>) records 36 passing focused cases. [Phase67](<research/phase67-final-safety-disposition/findings.md>) retains its bounded configuration/query/authorization-to-capture-entry scope. The frozen [package audit](<research/final-hardware-test-package/final-cheap-checks.md>) preserves the earlier two-gap history, with a current supersession notice. No model PASS is physical proof.

Authentic NOR evidence and later initializer/reclaim/resource qualification remain future dependencies. Phase65 coefficients are synthetic. No current-unit capture, complete engine admission or final P/X/Y fit is claimed.

# First target: Modal / Resonator

**PROVEN:** source closure uses the revisions in PROJECT_OVERVIEW. Modal is registry model 20, `already_enveloped=true`, with original postprocessing MAIN gain−1 / AUX 0.8. **UNKNOWN:** complete native ModalEngine/Voice, final allocation, retained integration and total engine cost. An arithmetic probe is not a completed engine.

# Original 12→32 wrapper

**PROVEN in original-source host replay:** independently initialized original Voice objects compare continuous native 12 with a 32-frame FIFO adapter using strict floating arithmetic. Over 4096 Circuit blocks /131072 MAIN/AUX frame pairs /10923 native calls, output is bit-exact, all 112 named fields compare after each native call, and arena canaries remain intact. MAIN has 130794 nonzero samples; AUX 130348.

Calls repeat 3, 3, 2; FIFO remainders 4, 8, 0 frames. Controls are sampled at each native render's start (`generated/32`), including when that call crosses a Circuit boundary. The last call produces four lookahead frames. RNG is saved/restored per host instance. This proves the host scheduler contract, not a DSP FIFO/control port.

# Numeric progression

Initial signed 47 Q4.43 recurrence established wide fixed-point behavior. The later wide baseline worst path costs 762600 modeled cycles/block. **SUPERSEDED as best current kernel:** optimized D uses exact unsigned 24 coefficient mantissa plus signed exponent, split-word histories and 56-bit accumulator intermediates. History = signed 24 high × `2^24` + unsigned 24 low; coefficient = `M * 2^(-23-S)`. Exercised shifts−2…23 represent supplied binary32 coefficients exactly. Negative-shift partial-product truncation is explicitly modeled, bounded to three exercised history LSBs. Resonator histories use F36, excitation F26.

| Current D result | Value/scope |
|---|---|
| Isolated P bodies | 109 resonator + 111 excitation = 220 words |
| Active histories/voice | 100 X words: 48 resonator + 2 exciter histories, two words each |
| MAIN int16 primary error | Max 3; RMS 0.329192831 (rounded 0.329193) |
| AUX int16 primary error | Max 2; RMS 0.281588880 (rounded 0.281589) |
| Worst instructions/block | 72597 |
| Worst modeled filter cycles/block | 77697 |
| Two worst filter banks | 155394 modeled cycles before full-engine/retained work |

**PROVEN within probes:** primary 4096-block corpus and separate 4096-block decay tail execute the excitation SVF and all 24 resonant modes. Native histories match the independent integer model exactly; binary32 histories are not bit-exact. Primary replay includes 262152 exact mode checks and 524304 history comparisons with declared-range guards and canaries. Tail max MAIN/AUX error is 1/1.

220 P is the sum of independently assembled bodies, not a linked complete module. It excludes dispatch, caller saves, control smoothing, coefficients, excitation generation, limiter/postprocessing and native FIFO. Resident coefficients could add 200 X words/voice; the probe stages eight at a time with X 24 input/Y 24 output. Those are requirements/candidates, not admitted Circuit allocations. Integrated caller register/modifier preservation is **UNKNOWN**.

# Implications

All timing is **modeled DSP cycles**, not measured physical timing. Same-model max is two tracks, so four simultaneous Modal tracks are not required. The older four-Modal/seven-or-ten-voice workload projection is **SUPERSEDED as a requirement**; its arithmetic observations remain historical evidence. Two filters consume 155394 cycles before missing full-engine/retained work, against a conditional 163840 one-core allowance. Cross-core distribution requires proven scheduling/transport/state contracts; granular already uses core1.

**UNKNOWN:** full Modal CPU/state/P cost, active PCM drum/granular/capture worst-case interactions, full ABI and real Plaits track integration. Limited retained glitch/Master FX replay is not universal coverage. Per-engine polyphony must be determined empirically.

Evidence: [Modal port/host wrapper](<../notes/plaits-modal-dsp-port.md>), host verification (local-only reference: `builds/phase21-modal-plaits/host-result/verification.json`; not distributed), [numeric timing](<../notes/plaits-modal-numeric-timing.md>), [native optimization](<../notes/plaits-modal-native-optimization.md>), [four-track workload limits](<../notes/four-track-plaits-resource-architecture.md>).
