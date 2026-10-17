"""Report admission failure separately from the valid pinned-host FIFO result."""
import csv, hashlib, json, math, re, statistics, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'builds/phase20f-va-vpre-admission'
UP=ROOT/'plaits/upstream'
REF=Path(r'C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main')
def link(p,symbol=None):
    line=next((i for i,s in enumerate(p.read_text(encoding='utf-8').splitlines(),1) if symbol and symbol in s),1)
    return f'[{p.name}'+(f' — {symbol}' if symbol else '')+f'](<{p.as_posix()}:{line}>)'
def main():
    placement=json.loads((OUT/'placement.json').read_text())
    native=json.loads((OUT/'run-v1/native.json').read_text())
    oracle=json.loads((OUT/'oracle-v1/verification.json').read_text())
    rows=list(csv.DictReader((OUT/'run-v1/blocks.csv').open()))
    assert len(rows)==4096
    assert all(r['restored_equal']=='1' and r['caller_and_stack']=='1' and r['canaries']=='1' and r['mixer_same_instruction_path']=='1' for r in rows)
    assert all(r['state_equal']=='0' and r['output_equal']=='0' for r in rows)
    orows=list(csv.DictReader((OUT/'oracle-v1/blocks.csv').open()))
    assert len(orows)==4096
    assert [(int(r['renders']),int(r['fifo_remainder'])) for r in orows[:6]]==[(3,4),(3,8),(2,0)]*2
    timing={}
    for key in ('original_instructions','reduced_instructions','original_nominal_cycles','reduced_nominal_cycles','original_vpre_cycles','reduced_vpre_cycles'):
        vals=[int(r[key]) for r in rows]
        i=max(range(len(vals)),key=vals.__getitem__)
        timing[key]=dict(min=min(vals),mean=statistics.mean(vals),max=max(vals),worst_block=i)
    raw=(OUT/'run-v1/midi2.i32').read_bytes();vals=struct.unpack('<'+'i'*(len(raw)//4),raw)
    assert len(vals)==4096*32*3
    assert all(vals[i]==vals[i+2] for i in range(0,len(vals),3))
    errors=[vals[i+1]-vals[i] for i in range(0,len(vals),3)]
    regression_error=dict(max_abs=max(abs(e) for e in errors),rms=math.sqrt(sum(e*e for e in errors)/len(errors)),dc=statistics.mean(errors),units='signed24 MIDI2 ring words; reduced-deletion failure, not Plaits error')
    # Trace-level mixer arithmetic verification, independent of the DSP opcodes.
    # All fixture strip coefficients are 0x100000, and stock synth stems are zero.
    mixer_checks=0
    for name in ('original','reduced','restored'):
        ring=[0]*64;pending={}
        with (OUT/f'run-v1/{name}/access.csv').open() as f:
            for r in csv.DictReader(f):
                b=int(r['block']);phase=int(r['phase']);ad=int(r['address'],16);value=int(r['value'],16)
                if r['space']!='Y' or r['write']!='1':continue
                if phase==1 and 0x1000<=ad<0x1040:pending[(b,ad-0x1000)]=value
                if phase==2 and 0x800<=ad<0x840:
                    j=ad-0x800;frame=j//2
                    def s24(v):return v-0x1000000 if v&0x800000 else v
                    left=s24(pending.get((b,2*frame),(0x111*(2*frame)+b)&0xffffff))
                    right=s24(pending.get((b,2*frame+1),(0x111*(2*frame+1)+b)&0xffffff))
                    # Sign inversion by stock output move; accumulator conversion
                    # floors the positive half-sum before negation in this sequence.
                    actual=s24(value)
                    # Accepted only after reproducing the sealed accumulator rule.
                    expected=-(left+right)//2
                    if actual!=expected:
                        raise AssertionError(('Stock mixer oracle',name,b,j,actual,expected,left,right))
                    mixer_checks+=1
    before=json.loads((ROOT/'builds/phase20e-full-plaits-audit/source-inventory.json').read_text())['reference_before']
    after={str(p.relative_to(REF)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in REF.rglob('*') if p.is_file() and '.git' not in p.parts}
    assert before==after
    manifest=json.loads((UP/'source-manifest.json').read_text())
    for f in manifest['files']:assert hashlib.sha256((UP/f['path']).read_bytes()).hexdigest()==f['sha256']
    protected=json.loads((ROOT/'builds/phase20d-midi-vpre/fixture/preparation.json').read_text())['protected']
    for p,h in protected.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
    provenance_files=list((ROOT/'plaits/poc/va_vpre').glob('*'))+[ROOT/'plaits/poc/midi_vpre/runner.cpp',ROOT/'builds/phase19a/core-build/replay_core.lib',ROOT/'builds/phase19a/core-build/upstream/asmjit/asmjit.lib']
    source_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in provenance_files if p.is_file()}
    result=dict(verdict='UNQUALIFIED',admission='FAIL: reduced-layout deletion breaks unchanged MIDI2',placement=placement,native=native,host_FIFO=oracle,
        baseline_comparison_timing=timing,reduced_MIDI2_error=regression_error,independent_stock_mixer_samples_verified=mixer_checks,
        protected_reference_files=len(after),protected_pinned_files=len(manifest['files']),DSP_engine_implemented=False,
        new_DSP_engine_P_words=0,new_DSP_tables_P_words=0,qualified_Plaits_state_words=None,full_Plaits_cycles=None,ARM_vs_DSP_error=None,source_and_library_hashes=source_hashes)
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    U=lambda p,s=None:link(UP/p,s)
    R=lambda p,s=None:link(REF/p,s)
    L=lambda p:link(ROOT/p)
    report=f'''# Phase20F — pinned VA_VARIANT=2 at MIDI vpre: admission failure

2026-10-15. **ONE COMPLETE PLAITS ENGINE: UNQUALIFIED. Placement/regression admission: FAIL.** No complete DSP VA+Voice implementation was built or claimed. The required reduced layout deletes code used by the unchanged MIDI2 regression track. I corrected the prior recommendation instead of retaining its invalid budget or weakening MIDI2 tests.

**PROVEN:** original B1.3 core0 occupies `[0000,3FED)`, 16,365 P words, leaving19 below4000. The Phase20E 1,196-word budget =19 existing tail +1,177 words removed from a shared two-track renderer/control module. This is a conditional budget for replacing BOTH original MIDI engines. It is not1,196 words available beside an unchanged MIDI2 engine.

The deleted code is shared, not two separately duplicated engines:

| Original P range | Words | Needed by unchanged MIDI2 |
|---|---:|---|
| `[36AD,3876)` | 457 | Pitch, shape, morph and dual control |
| `[3999,3B82)` | 489 | Single/dual oscillators, interactions and VA noise |
| `[3D9E,3E1F)` | 129 | TINC pitch table |
| Scattered VA-drum control changes | 102 net | Original VA envelope/filter/noise behavior |
| Total restoration charge | **1,177** | Restoring the original shared module leaves **19** words |

{R('tools/vcf21_dsp.py','def code')}; {R('tools/vcf21_dsp.py','L("vp_loop")')}; {R('tools/vcf21_dsp.py','control("vc_")')}; {R('tools/vcf21_dsp.py','def channel')}; {L('plaits/poc/full_audit/reclaim.py')}. **UNKNOWN:** whether an additional semantics-preserving refactor could reclaim space while retaining MIDI2; the current deletion does not do that. Even retaining only legacy oscillator control/render/TINC would charge1,075 words and leave121, while dropping VA control would change MIDI2's engine capabilities. The existing sealed VariableSaw primitive alone is523P in the previous short-target fixture, exceeding either19 or121 before the other three oscillators/LPG/glue. This is a size comparison for existing code, not a mathematical lower bound on every future implementation.

## Actual DSP admission test

**PROVEN:** executed4,096 consecutive32-sample blocks for three machines: original B1.3; the actual source-reduced shared module; and restored original code. MIDI1 was disabled to isolate MIDI2. Identical MIDI2 mailbox words exercised notes/gates/retrigger, oscillator shape/PW, single/dual and VA modes, with reference-style latest-value coalescing/2ms scheduling. All active DSP bytes came from original B1.3 or the byte-verified source assembler. No host callback rendered or replaced audio.

- Reduced layout: MIDI2 state mismatch **{native['midi2_state_mismatch_blocks']} /4096**, output mismatch **{native['midi2_output_mismatch_blocks']} /4096**. First mismatch block0, sample0. These failures are preserved in `blocks.csv`; they are the reason admission fails.
- Original MIDI2 executed **{native['midi2_control_island_instructions']:,}** instructions in the deleted control island and **{native['midi2_renderer_island_instructions']:,}** in the deleted renderer island. Those are issued instructions, not cycles or P sizes.
- Restored original code: all4,096 MIDI2 state/output blocks exact to the original; mixed output exact as well. State comparison covers240 cells across VB, OSC1, OSC2, second-filter-stage and FX records. It is an offline fixture regression, not full-device verification.
- Caller register/modifier/LA/LC/OMR/SP/SC checks and fixture ring/mixer/stem/gain canaries pass after every vpre/mixer call. X/Y writes traced; P runtime writes rejected. No private Plaits DSP allocations exist, so these checks cannot qualify a future engine workspace or its ABI.
- The stock strip mixer executed identical instruction paths; independently checked **{mixer_checks:,}** output samples against its accumulator arithmetic. Different reduced-layout audio produces different mixed samples; that is expected and does not excuse MIDI2 regression.

Evidence: {L('builds/phase20f-va-vpre-admission/verification.json')}, {L('builds/phase20f-va-vpre-admission/run-v1/blocks.csv')}, {L('builds/phase20f-va-vpre-admission/run-v1/native.json')}, per-machine `access.csv`, `pc.u16`, `executed.asm`; harness {L('plaits/poc/va_vpre/admission.cpp')} and {L('plaits/poc/va_vpre/admission.py')}.

The reduced fixture keeps the sampler tail at its original P addresses, puts zeros only in the deleted module's gap, repairs the external P:D22 vret operand, and uses only a3-word call/stop stub atP:[3FF0,3FF3) inside the old19-word tail. There are **no P:0400/P:0800 stock-synth overlays**. All other stock words below2A5E are equal apart from that explicit vret operand; all sampler-tail words are equal. Full ARM relinking/boot/core1/concurrent operation is UNKNOWN. Raw `.be24` fixtures are DSP-only programs, not application BIN/SYX firmware containers.

## Exact selected original behavior

**PROVEN source structure:** MODEL=8, `VirtualAnalogEngine`, active `VA_VARIANT=2`. {U('plaits/dsp/engine/virtual_analog_engine.h','VA_VARIANT')}; {U('plaits/dsp/engine/virtual_analog_engine.cc','void VirtualAnalogEngine::Render')}.

- Engine pitch: `NoteToFrequency` plus HARMONICS detuning intervals; cycles/sample normalized using upstream corrected47,872.34Hz constant. {U('plaits/dsp/engine/engine.h','inline float NoteToFrequency')}.
- Engine HARMONICS sets detuning; TIMBRE sets sync amount/square PWM and gain; MORPH sets variable-shape/PW, saw shape/gain. Preserve all clamps/normalization and two gain interpolators.
- AUX: primary and auxiliary monster-sync `VariableShapeOscillator` renders, differenced at0.5 gain. MAIN: synced variable square plus VariableSaw, mixed with interpolated normalized gains. Three distinct VariableShape instances plus one VariableSaw; sealed VariableSaw alone is not this engine.
- `Init` initializes the four oscillators/two gain histories and a24-float temp arena; `Reset` is empty. Model-switch Voice behavior therefore differs from calling Init/reset-all. {U('plaits/dsp/engine/virtual_analog_engine.cc','void VirtualAnalogEngine::Init')}.
- Trigger/accent are not directly read by this VA engine. Original Voice owns delayed0.3/0.1 trigger hysteresis, internal decay/LPG, note averaging, patched-source choices and nonlinear modulation amount curves/clamps. LEVEL compression sets accent and may drive LPG; unpatched default accent0.8 does not become an automatic VA amplitude multiplier.
- VA metadata: already_enveloped=false, MAIN/AUX gain0.8. Voice may bypass LPG when neither trigger nor level is patched; otherwise it processes both channels with independent LPG filter/gain histories. Positive VA gain does not execute limiter audio processing, though limiter state initialization/reset remains in the original wrapper. Output polarity and16-bit clipping are preserved in the host reference.

{U('plaits/dsp/voice.cc','void Voice::Init')}; {U('plaits/dsp/voice.cc','void Voice::Render')}; {U('plaits/dsp/voice.h','ApplyModulations')}; {U('plaits/dsp/envelope.h','class LPGEnvelope')}; {U('plaits/dsp/fx/low_pass_gate.h','class LowPassGate')}. Module ADC/DAC/calibration/UI/flash mechanisms are excluded. The TEST host UserData accessor supplies null custom data; no save/programming function is called.

## Implemented 12-to-32 scheduler and pinned host oracle

**PROVEN host-only:** two independent original `Voice` instances, fixed MODEL=8. Reference A renders a natural sequence of full12-sample blocks. Adapter B requests32 samples, consumes FIFO remainder and renders complete12-sample blocks only. Over three Circuit blocks the pattern is **3/3/2 renders**, with FIFO remainder **4/8/0**. No12+12+8 truncation, array-cap enlargement, oscillator arithmetic changes or envelope coefficient changes.

Completed4,096 Circuit blocks =131,072 MAIN/AUX sample pairs, **10,923** original render calls, including deferred Init reset, note on/off/retrigger, pitch/HARMONICS/TIMBRE/MORPH/LEVEL sweeps and internal/external modulation, ping/level-driven/bypass LPG modes. Output max absolute/RMS/DC difference between A and B is **0 signed16 units**. **{oracle['state_fields_compared_per_render']}** named persistent scalar/filter/envelope/trigger-delay fields match bit-for-bit after each internal render; host arena canaries pass. This comparison verifies FIFO scheduling against the same pinned host implementation, **not an independent fixed-point arithmetic oracle or ARM-vs-DSP equality**.

Control/reset selection uses internal-render start sample `s`: Circuit control index `floor(s/32)`. Already-prefetched4/8 samples retain earlier controls; new changes become visible at the next12-sample boundary (0..11 samples later). Trigger delay remains five original control calls,60 samples, followed by the original hysteresis. The adapter does not split or reset oscillator state across FIFO extraction. Final four lookahead samples are retained. Host replay uses identical clocks/staging in A and B. None of this proves actual ARM mailbox scheduling or audio-rate CV transport. `controls.tsv` is the host oracle stream; `cases.tsv` is the separate MIDI2 admission stream. No DSP Plaits candidate exists to feed the host stream to.

Fidelity: **BIT-EXACT** for host FIFO output and the named host state fields versus natural pinned-host rendering; **UNKNOWN** for a DSP fixed-point conversion. **STRONG INFERENCE:** the scheduling preserves the original discrete algorithm/control cadence. Playback on the conditional Circuit48,046.875Hz rate without retiming would shift original corrected-rate pitch approximately+6.30 cents and rescale durations. No rate correction was silently inserted. A faithful Circuit port must explicitly qualify sample-rate/parameter semantics; same sample sequence alone is not identical physical-time pitch.

Host source {L('plaits/poc/va_vpre/oracle.cpp')}; result {L('builds/phase20f-va-vpre-admission/oracle-v1/verification.json')}; blocks/raw pairs in `oracle-v1/`. Build uses pinned engine object files from Phase20E plus actual `voice.cc`, MSVC strict float and the already documented host-only compatibility overlay. Private-member exposure is instrumentation only. No other engine is rendered or ported.

## Memory and nominal timing

New shared DSP engine code **0P**, immutable DSP tables **0P**: not implemented after admission failure. Restoring unchanged legacy MIDI2 charges1,177 of the purported1,196 free words, leaving **19P** before any new engine/glue. The admission caller stub temporarily uses3 of those19; that is test infrastructure, not production engine cost.

Persistent/temporary X, Y and external/shared Plaits allocations: **not allocated, costs UNKNOWN**. Logical upstream active-state census:39 VA oscillator/gain cells plus35 tracked Voice/LPG/filter/trigger metadata =74 tracked scalar fields, before Patch/Modulations/control staging, buffers and caller saves. This is source/host accounting, not a fixed-point layout. Original temp24 floats, MAIN/AUX24 each; FIFO adapter holds up to44 frames transiently before extracting32, with up to8 frames left at completed blocks. The host full Voice also embeds inactive engine objects/16KiB arena because it is the actual pinned wrapper. Those inactive objects are not a proposed fixed-engine DSP allocation. No claim of X/Y address ownership or canary-qualified DSP workspace is made.

Nominal DSP comparison below is **original versus stripped legacy path**, including vpre + original strip mixer + equal caller-stub overhead. It is not complete Plaits timing. calcCycles excludes interlocks/IRQ/DMA/external waits; issued counts remain separate.

| Fixture path | Instructions/block min / mean / max | Nominal cycles/block min / mean / max |
|---|---|---|
| Original B1.3 MIDI2 | {timing['original_instructions']['min']} / {timing['original_instructions']['mean']:.4f} / {timing['original_instructions']['max']} | {timing['original_nominal_cycles']['min']} / {timing['original_nominal_cycles']['mean']:.4f} / {timing['original_nominal_cycles']['max']} |
| Reduced module, MIDI2 broken | {timing['reduced_instructions']['min']} / {timing['reduced_instructions']['mean']:.4f} / {timing['reduced_instructions']['max']} | {timing['reduced_nominal_cycles']['min']} / {timing['reduced_nominal_cycles']['mean']:.4f} / {timing['reduced_nominal_cycles']['max']} |

Worst original observed total at block{timing['original_nominal_cycles']['worst_block']}; worst reduced at block{timing['reduced_nominal_cycles']['worst_block']}. Renderer-only, wrapper-only and complete Plaits worst cycles **UNKNOWN**. Host execution time is not substituted. Reduced-path savings measure removal of MIDI2 synthesis and are not available while MIDI2 must remain unchanged.

## P1–P9 gates

| Gate | Result | Confidence/scope |
|---|---|---|
| P1 complete engine fits real budget | **Admission FAIL; engine fit UNKNOWN** | PROVEN1,196 assumption removes MIDI2; restored original leaves19, not a valid1196 budget beside MIDI2 |
| P2 bounded private persistent state | UNKNOWN | No DSP engine allocation admitted |
| P3 original32-sample adaptation | PASS host scheduler; DSP UNKNOWN | PROVEN full12 renders/FIFO preserve131072 output pairs and named state; rate semantics remain explicit |
| P4 quantified DSP numerical error | UNKNOWN | Host-FIFO error0; no DSP-vs-pinned candidate comparison |
| P5 vpre ABI | PASS admission fixture; Plaits UNKNOWN | Registers/modifiers/stack checked4096 times per machine; no Plaits adapter tested |
| P6 MIDI2 unchanged | **FAIL reduced layout; PASS restored** | PROVEN4096 mismatches versus4096 exact restored blocks |
| P7 stock mixing | PASS fixture arithmetic/path; complete integration UNKNOWN | PROVEN independent mixer oracle and restored output; silent synthetic stock synth stems |
| P8 worst complete modeled cycles | UNKNOWN | Only legacy original/reduced counts above were measured |
| P9 second shared-code instance plausible | UNKNOWN | No completed, placed/timed first engine; do not infer from VariableSaw alone |

Exact blockers: the contradictory deletion/MIDI2 requirement; then missing complete VariableShape/VA and Voice/LPG fixed-point port, qualified private state/save/output/FIFO layout, DSP arithmetic oracle/error acceptance bounds, full integration/register/stock-feature regression and target timing. No additional engine or second instance was attempted. This admission rejection is not proof that future code refactoring/placement cannot succeed.

**Next necessary technical step:** prove a genuine P allocation that retains the original shared MIDI2 code (or a separately proven exact legacy-preserving refactor). Only then can a complete engine implementation use an admitted budget. No permission was inferred to drop MIDI2, occupy stock-synth P, delete unrelated features or increase the budget.

Verified unchanged: **{len(after)} reference files**, **{len(manifest['files'])} pinned source files**. No hardware, firmware container, flash-ready artifact or reference-repository edit. Sources and retained output hashes are in `verification.json`/`hashes.json`.
'''
    report=report.replace('up to44 frames transiently','up to40 frames transiently')
    (ROOT/'notes/plaits-va-vpre-admission.md').write_text(report,encoding='utf-8')
    files=[p for p in OUT.rglob('*') if p.is_file() and p.name!='hashes.json']
    hashes={str(p.relative_to(OUT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    (OUT/'hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
    print(json.dumps(dict(verdict=result['verdict'],admission=result['admission'],mixer_checks=mixer_checks,timing=timing),indent=2))
if __name__=='__main__': main()
