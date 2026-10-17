"""Persist narrow final triage; preserve all earlier reports and firmware."""
from pathlib import Path
import json,hashlib,ast
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def L(name):return f'[{name}](<{(OUT/name).as_posix()}>)'
def P(phase,name):return f'[{name}](<{(ROOT/"builds"/phase/name).as_posix()}>)'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    text=f'''# Final triage — only the three requested categories

This refines the named Phase60 UNKNOWN paths; it does not replace whole-project admission with a universal proof. All addresses are pinned Phase44 corrected research-image addresses. No reference/image modifications, firmware generation or hardware/MIDI access occurred.

## A–E answers

|Item / classification|A: NOR program/erase?|B: filesystem persistence?|C:82000..821FF alteration before capture?|D: adapted12-byte overwrite?|E: reachable boot→snapshot→authorization?|
|---|---|---|---|---|---|
|TIM2 channel4→1EEB0→display DMA — **SAFE / IRRELEVANT**|No|No|No|No, with normal initialized display objects/buffers|Conditional: compare interrupt plus pending display row/frame; yes as display refresh becomes active|
|RTC223B0→1DA70→1DAE0 — **SAFE / IRRELEVANT**|No|No|No|No|Conditional:22308 has armed the alarm after power-button hold; alarm expiry can occur during a sufficiently long window|
|Legacy five-owner group — **REAL BLOCKER** (schema integration)|No: raw helper submits fixed-address reads, not programs/erases|No|No|Old code writes overlapping bytes as listed below; correctly early-reserved first-epoch geometry is guarded against preauthorization entry. Coordinated replacement remains required|Getter/SysTick callable in window; old start only on matching host packet; raw/completion only after old admission. New control makes old admission fail closed|

## Display trace, stopped at non-storage leaves

1EEB0 takes display context200007FC, consumes its row-tick byte+18, advances modulo64 scan index and double-buffer/frame counters.1B130 writesGPIOBSRR;25B10→3AD16/3AD4E selects display GPIO row and advances selector.1EF8A→1C270 sets DMA memory pointer from the display frame data.1EF92→25AE8(argument1) stops the display timer via2446A and starts the configured SPI DMA via3783A→1C142.1EFA2→25B26 programs the next timer compare and restarts timer via3ADBC→2445C. DMA completion3784E/37852 only updates the display's bounded pending counters. No filesystem, Storage queue, NOR primitive, diagnostic admission or private-record pointer occurs in this chain. Valid initialized display pointers are the premise; arbitrary RAM corruption is not introduced as a new scope. Evidence: {L('app-0801eeb0.asm')}, {L('app-08025b10.asm')}, {L('app-0803ad16.asm')}, {L('app-0801c270.asm')}, {L('app-0803783a.asm')}, {L('app-0801c1d4.asm')}, {L('app-0803adbc.asm')}.

Display receive completion1EFA8 consumes its own buffer-pending count, toggles its double buffer at+5C, sets the next receive-DMA memory pointer through1C270, then tail-calls1BA12 on display context+18. This completion path also contains no storage callback. {L('app-0801efa8.asm')}, {L('app-0801f02a.asm')}.

## RTC trace, stopped at GPIO/watchdog leaves

223B0 first disables/acknowledges alarm through2238C and calls the registered200069F0 callback. In this path that is1DA70, installed by1DA24→22308.1DA70 acknowledges its EXTI source and checks20006A46 bit0; if no longer held it returns. If held it explicitly setsR0=0 before branching to1DAE0. Therefore the optionalR0!=0 brightness/fade loop at1DAF8..1DB14 is **not on this RTC edge**.22420(R1=0) skips224A8 callback work and changes only RAM flagbit0;22408 changes RAM flagbit2. Remaining calls configure/clear GPIO, then disable interrupts and feed watchdog forever. This is power-latch shutdown/halt behavior, not a persistence callback, and it need not return to finish boot. No NOR/FS/private-state operation occurs. Evidence: {P('phase60-irq-liveness-final','app-080223b0.asm')}, {P('phase60-irq-liveness-final','app-0801da24.asm')}, {L('app-0802238c.asm')}, {L('app-0801dae0.asm')}, {L('app-08022408.asm')}, {L('app-0801afbc.asm')}, {L('app-0801b130.asm')}, {L('app-0801eb1e.asm')}.

## Exact legacy writes, guards and replacements

Private record baseS=20044D70; offsets below are bytes.

|Owner|Exact stores / values|When / guards|Required adaptation preserving diagnostic behavior|
|---|---|---|---|
|6B6CC getter|6B708:S+4..7=0;6B70A:S+8..11=0;6B714:S+0..3=4E4F5234 (little endian34 52 4F 4E)|Only lazy reservation when allocator limitE58 and cursor<=D70. Already-reservedD70 takes6B71A magic check; new control11/12 fails and returns0 at6B744, without writing|Move one-time initialization before publication; never clear a committed record; preserve independent MasterFX getter/initialization atD7C via5DC06, and its pointer-return ABI|
|6B748 timeout|6B794:S+4=3|Only reservedD70, old magic, oldACTIVE byte1, elapsed>=5000|Read new control/ACTIVE and writeFAILED to control32 only. Preserve wrap arithmetic, quarantine/retained ownership, no forced cleanup/retry|
|6B798 admission|6B820:S+4=1;6B824:S+5=session;6B830:S+8..11=start tick|Valid232-byte legacy command, getter returns nonzero, old statebyte0; then6B838 callsraw6B850|Validate geometry/epoch/host authorization first; atomically overlay payload and publishACTIVE. Preserve one-shot rejection and packet/buffer validation|
|6B850 raw|6B8DA:S+6=chunk;6B8DE:S+7=1(read);6B924:S+7=2(reply);6B9FE:S+4=3(failed unless oldSUCCESS);6BA02:S+7=0(cleanup)|Entered from admitted legacy start; oldACTIVE checks before reads/replies; cleanup on exit. Raw inputs are fixed81000/23 and82000+64*n/64 through47C6C|Allow transport-field writes only after adapted authorization; check new epoch/lifecycle at submit and callback boundaries. Keep read-only targets, bounded buffers and no retry. Do not infer unsafe failure cleanup is solved by moving fields|
|6BC46 corrected terminal|S+4=2|Raw final transmit succeeded;6BC30 masks IRQs and checks oldACTIVE byte1 before6BC46; old6B9EC is bypassed|Use atomic ACTIVE→SUCCESS on control32; FAILED remains absorbing. No geometry write before authorization|

All five can be adapted without changing required read-only/one-shot/timeout/quarantine semantics, but **all interpretations and writes must move together**. Adapting only the getter to accept the new schema while leaving old admission/raw stores would remove an existing fail-closed guard and is not acceptable. This is a concrete implementation constraint, not an unknown storage producer. Evidence: {L('app-0806b6cc.asm')}, {L('app-0806b798.asm')}, {L('app-0806b850.asm')}, {L('app-0806bc30.asm')}, {L('app-08047c6c.asm')}, {L('app-0805dc06.asm')}, {P('phase57-first-mount-provenance','ownership.json')}.

## New targeted guard evidence

Fifteen native runs test getter, timeout and a fully valid legacy-start packet against BOOT0/MOUNTING16/VALID11/EXPORTED12/FAILED15, with early allocator limitD70 and geometry payload starting01 (so an accidentally unguarded legacyACTIVE test would matter). Every record remains byte-identical, with0 private write intents and0 raw/read/program/erase entries. Getter returns0; admission exits atB808/B842 beforeB820. No whole-boot or historical test is rerun. {L('legacy_guards.py')}, {L('legacy-guard-tests.json')}.

The preserved Phase56 overwrite case used old unreserved limitE58. It proves the need for initialization ordering, **not corruption of a correctly reserved/committed adapted record**. The old timeout collision likewise required old magic/ACTIVE interpretation. These distinctions prevent using invalid mixed states as a new preauthorization counterexample. {P('phase56-geometry-snapshot-lifecycle','liveness-tests.json')}.

## 1. REAL BLOCKERS BEFORE FLASHING

Coordinated native integration/independent validation of the five legacy owners is still required: getter ABI and separateMasterFX state; new timeout control field; geometry-gated admission; raw transport lifecycle; atomic terminal state. Existing fragments qualify owner semantics only, not their installed call sites. These are candidate construction/validation tasks, not a reason to expand reverse-engineering scope.

## 2. MODEL-ONLY UNKNOWNS

Exact display/RTC interrupt timing and unexercised scheduling combinations remain incompletely modeled, but their traced operations expose no storage or private-record writer. No unresolved corruption mechanism remains in these two paths under normal initialized-object assumptions.

## 3. SAFE / IRRELEVANT PATHS

TIM2 channel4/display DMA and the specified RTC alarm callback chain, for NOR/FS/geometry preservation. RTC can stop normal execution; that is not evidence of a NOR or geometry write.

Is there still a concrete software path that can plausibly corrupt82000 or the geometry state before authorization?

**NO**

This answer is restricted to the three requested categories and the required early-reserved, first-epoch adapted layout. It does not approve the unwired historical image as a final candidate. Further proof work on these display/RTC paths has diminishing returns. The next step may be final candidate construction, including coordinated owner integration, plus independent validation. No firmware was generated and no hardware was accessed.
'''
    (OUT/'findings.md').write_text(text,encoding='utf8')
    preserved={}
    for phase in ('phase60-irq-liveness-final','phase59-scheduler-first-mount-order','phase57-first-mount-provenance','phase56-geometry-snapshot-lifecycle'):
        folder=ROOT/'builds'/phase;count=0
        for line in (folder/'SHA256SUMS.txt').read_text().splitlines():
            h,n=line.split('  ',1);assert sha(folder/n)==h,(phase,n);count+=1
        preserved[phase]=count
    tests=json.loads((OUT/'legacy-guard-tests.json').read_text());assert tests['passed'] and len(tests['cases'])==15
    sources=json.loads((ROOT/'builds/phase42-exact-rdiag-integration/inputs.json').read_text())['sources']
    for x in sources:assert sha(Path(x['path']))==x['sha256']
    for p in OUT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'))
    assert not list(OUT.glob('*.bin')) and not list(OUT.glob('*.syx'))
    r=dict(scope='Only TIM2/display, specified RTC alarm and five legacy owners',classifications={'display':'SAFE / IRRELEVANT','RTC':'SAFE / IRRELEVANT','legacy_owners':'REAL BLOCKER'},new_native_guard_cases=15,prior_files_unchanged=preserved,pinned_sources_unchanged=len(sources),hardware_access=False,MIDI_ports_opened=0,firmware_generated=False,firmware_transmitted=False,concrete_preauthorization_corruption_path='NO under required early-reserved first-epoch layout in these three categories',final_candidate_qualified=False)
    (OUT/'validation.json').write_text(json.dumps(r,indent=2)+'\n')
    (OUT/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'))
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
