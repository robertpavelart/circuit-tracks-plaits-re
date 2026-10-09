# Phase 6 — static DSP resource audit, build 4486

**Current Phase 6C criterion:** INIT-TOUCHED and RUNTIME-OWNED are separate.
Startup clear does not disqualify later allocation. See
[dsp-runtime-ownership.md](dsp-runtime-ownership.md): normal destination
constants and selected intervals are bounded, computed/ancestry exclusions
are incomplete, and no RAM allocation is VERIFIED AVAILABLE AFTER INIT.
Reading Plaits solely to compare resource needs is ready; safe fit and
implementation remain NOT-YET-DETERMINED. Earlier blanket comparison and
initialization-disqualification gates below are superseded.

**Phase 6B update:** [dsp-memory-ownership.md](dsp-memory-ownership.md)
proves startup writes across both candidate X/Y ranges. They fail the strict
no-initialization-use availability criterion; persistent runtime ownership is
still unresolved. It also adds the X:2C66 prefetch/readability obligation,
reviewed affine intervals, worker/private-memory correlation, clobber table
and extension mechanics. Largest VERIFIED AVAILABLE X/Y allocation remains
zero proved words. Current next step is normal host destination-range closure.

All ranges are half-open and all DSP addresses/counts are **24-bit words**,
unless stated otherwise. This audit executes analysis scripts only. No hardware,
firmware execution, patching, installation or Plaits compilation was performed.

**Result: NOT-YET-DETERMINED for a resource-qualified Plaits comparison.**
The firmware supplies useful conditional limits, but no safe persistent RAM
allocation or finite voice execution-time headroom has been proved. The mono
seam is a scratch-buffer boundary with outstanding state obligations.

## Evidence and reproduction

`tools/ct_resource_audit.py --output-dir builds/phase6-audit` produces
`audit.json`, `memory-map.csv`, `access-inventory.csv`, `candidate-code.asm`.
See `tools/PHASE6.md` for the Python executable and fresh-directory repeat.
Canonical DSP listings are `builds/phase3-selection0-channel{0,1}.asm`;
each listed instruction's encoded bytes are checked against the extracted
payload. ARM evidence is in `builds/phase6-arm-rcc-init.asm`,
`phase6-arm-system-init.asm`, `phase6-arm-clock-functions.asm` and
`phase3-arm-transport.asm`, also byte-checked. Existing reconstruction,
descriptor and output-contract reports are prerequisites, not runtime snapshots.

Primary register/memory references:
[NXP DSP56724 Reference Manual](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf)
(memory-mode tables 3-3/3-4, PLL chapter 7, ESAI chapter 9) and
[ST RM0385](https://www.st.com/resource/en/reference_manual/rm0385-stm32f75xxx-and-stm32f74xxx-advanced-armbased-32bit-mcus-stmicroelectronics.pdf)
(RCC_CFGR MCO1 fields). DSP56724/core assignment and physical board wiring
remain conditional; family ISA decoding alone does not identify the exact part.

## A–C. Clock, audio rate and period

**VERIFIED register programming:** P:10B/10D loads 0x002028 into X:FFFF7D.
Under the documented DSP56724 map this is PCTL: PEN=1, NR=1, NF=41,
NO=1, DF=0. Thus Fsys=41×EXTAL. No second direct PCTL write appears in
the normal program inventory; indirect host writes and boot-ROM effects are
not excluded. SHI is an SPI slave clocked by ARM SPI2; its serial clock is
independent of the audio frame clock. HCSR word-width changes and HCKR=3
do not establish an audio rate.

**VERIFIED ARM programming:** 0x0801B1E8..0x0801B1F4 clears CFGR mask
0x07600000 and sets 0x06400000 at RCC+8 (RCC=0x40023800). On STM32F745
this selects MCO1=HSE/4. Firmware clock getter 0x0801BCCA..0x0801BCE4
uses HSE=24,000,000, from literal 0x0801BD3C. The firmware's MCO1 model
is therefore 6 MHz. **HYPOTHESIS:** MCO1/PA8 is wired to DSP EXTAL and
the physical oscillator matches that assumption; neither is proved here.
That model yields a 246 MHz DSP core. A LE16 constant at ARM 0x0805BCD0
is **VERIFIED 48047** and corroborates the rounded model audio rate; it
does not independently prove oscillator frequency or wiring.

| Register programming | Decoded configuration under DSP56724 map |
|---|---|
| P:2A3F, TCCR X:FFFFB6 = ECC309 | PM=9, PSR=1, DC=1, FP=3; TX clock/frame pins outputs |
| P:2A50, TCR X:FFFFB5 = 817D10 | 24-bit data in 32-bit slots; network mode; only TE4 enabled |
| P:2A43, RCCR X:FFFFB8 = 0CC30A | RX divider fields present, superseded by synchronous TX clocking |
| P:2A52, RCR X:FFFFB7 = 017D01 | 24-bit data in 32-bit slots; only RE0 enabled |
| P:2A47, SAICR X:FFFFB4 = 40 | SYN=1: RX uses TX clocks |

**VERIFIED field arithmetic, conditional clock routing:** PSR=1 bypasses
the fixed divide-by-eight stage. Bit clock = Fsys/[2×10×4] = Fsys/80.
Two 32-bit time slots give frame rate = Fsys/5120. One TX data line and
one RX data line each carry two slots, not six active serial channels.
PDRH X:FFFF98 ETI0/ETO0 reset to zero in the manual, selecting Fsys;
no direct normal/worker write was found. Unreviewed indirect writes, ROM
initialization and actual device identity prevent an unconditional clock proof.

**HYPOTHESIS nominal physical model:** bit clock 3.075 MHz, frame rate
48,046.875 Hz, 32-frame period 0.666016 ms. The architectural ratio gives
**5,120 Fsys cycles/frame and 163,840 cycles/32 frames**, provided the
documented source/dividers remain selected. This is the total sustained
service period, not an available voice budget. Effective physical rate,
per-voice cycles, memory stalls and headroom are **UNRESOLVED**.

## D. One service-period timeline and deadline

The following ordering is **VERIFIED** in the selected normal program;
elapsed durations and maximum waits are **UNRESOLVED**.

| Stage | Instruction evidence | Work / synchronization |
|---|---|---|
| Main loop | P:113, P:1C53, P:1FD1 | Host/table-job service before audio; X:13 gates audio service |
| Audio readiness | P:1D9 | D=(Y:FFE−Y:FFD)&3FF must reach 300 hex |
| Prepare | P:1EF..1F5 | Timing hook P:1C01; P:140 block constants; P:19F3 control; P:759 clears sums and resets worker queue through handshake |
| Request | P:1FC→198D→281 | Descriptor pass; twelve normal contexts plus two other entries, lifecycle-dependent work |
| Worker | worker P:120..126 | Concurrent address fetch/result replacement; completion mailbox/ICC polling |
| Completion | P:1FE→19BF→77F | Clear pass bit 23; completion bitmap bits 0..11 drive selected voice processing |
| Mono consumer | P:9DD..A94 | Per selected voice: post/filter processing then gain/group accumulation before scratch reuse |
| Group processing | P:200..22A | Bank-specific work; global scratch also reused |
| Converge/effects | P:242..24E, P:260→CB8 | Bank streams meet; retained downstream processing |
| Output | P:274→21C4, P:27B | Write two X-ring words/frame; advance Y:FFD by 64 words for N=32 |
| Optional work | P:277 | Additional output-region processing on selected state |
| Interrupt, interleaved | vector P:3E→1B4 | ESAI last-slot ISR, DMA rearm, two ring-word transfers/frame; Y:FFE advances by two |

**VERIFIED ring topology:** X:[1000,1400) output and Y:[1000,1400)
input, each 1024 words = 512 two-slot frames. P:1C7..1CA accesses two
words and wraps modulo 3FF. DMA channel addresses are rearmed at
P:1BC/1BE to staging words X:21/Y:29; configured peripheral endpoints
are TX4/RX0. The cadence here is ESAI last-slot/frame service, not a
proved DMA half/full interrupt. Exact DMA burst/cycle arbitration is unresolved.

At D=300 hex, input lag is 384 frames and output ring wrap lead is
128 frames. This describes pointer geometry at that occupancy only;
it is not a guaranteed four-block execution allowance. IRQs continue,
entry occupancy can be higher, and no complete overrun proof exists.
Generation must precede same-slot P:9DD; all output processing must
finish before the ISR reads that output-ring region. Worker completion
is an intermediate dependency for lookup modes, not the audio deadline.
SHI ISR register save area Y:[2000,2006) and ESAI ISR state must survive
preemption. Mailbox/queue wait iterations cannot be finitely timed here.

## E. X:2C46 ownership and lifetime

**VERIFIED:** this is shared scratch, reused across successive slots and
global processing. It is not per-voice storage and no dedicated double-buffer
partner was established. Startup X clear initializes it. Its contents must
survive P:9DD through the selected post path and P:A94 accumulation, not
merely the first read at 9DD. Earlier phase/index work also reuses the range.

The inventory finds **26 immediate base references**. Bounded pointer review
gives the following access families; these are not a complete points-to proof
for every computed/host-supplied address.

| Base-reference PCs / reviewed body | Role |
|---|---|
| 7EC,7FA; phase loop 7F1..7F3 | Phase/index scratch writer and reuse |
| 81F,87A | Phase/weight scratch readers |
| 9BD; 9C8..9D8 | Three-lane combination writes mono block |
| 9EC,9F0→9FD | Selected read/modify helper |
| A19→BDD, A23 | Post-path input reader and returned-result copy writer |
| A2B,A39,A3F,A71 | Alternative post branches: read/transform/recombine |
| A80; A8D..A94 | Final per-voice gain/mix reader |
| F4F,F59,F65,F73 | Global channel copy/transform: writers and readers through F7A |
| FFD..1003 | Global/group gain-ramp scratch writer |
| 1434..1465 | Global mix input reader (2C46 or 2C8A selected) |
| 1ECC..1ED6 | Table/work-generation writer |
| 1FC6..1FCD | Y:840-bank stream copy writer |
| 20F8..2110,211D→AA8 | Global processor writer, then transform consumer |
| 21B2..21C1 | Global buffer read/modify |

**VERIFIED reviewed ISR accesses:** ring/staging/state, with no direct
2C46 reference. **UNRESOLVED universal asynchronous exclusion:** worker
fetches arbitrary queued X addresses and host protocol writes addressed
memory. No fixed worker reference to 2C46 exists, and selected stock
wave requests use external table addresses; this does not prove every
possible request avoids scratch. An alternative producer must respect
the synchronous lifetime and restore live state. A safe producer ABI is
not proved solely by finding a writable destination.

## F–H. P/X/Y inventory and storage candidates

**VERIFIED load:** normal channel-zero boot record writes every P word in
[0,2A5E): 10,846 payload words; highest loaded address 2A5D. The stream
contains two additional header words. Code and constants are mixed; linear
disassembly of table words is not executable-code proof. No gap exists in
the *load record*, and zero runs are not free storage. Candidate CFG has
6,106 decoded instruction rows, unresolved indirect transfers and reviewed
dispatch seeds. It cannot establish dead code or maximum reachable PC.
Selection 1 diagnostic images are distinct loads, not deletable normal code.

**VERIFIED bootstrap bits:** MS=1, MSW1=1, MSW0=0, followed by ROM jump
P:FFFFFE. **Conditional DSP56724 map:** core0 P=16K, X=24K, Y=16K
words; core1 P/X/Y=8K each. Normal payload exceeding 8K corroborates,
but does not itself identify, the proposed channel-zero/core0 assignment.
Startup clears X/Y through 6000; Y:[4000,6000) is outside conditional
core0 Y RAM and must not be advertised as storage.

| Space/range | Established use / audit status |
|---|---|
| P:[0,100) | Loaded vector/reserved area |
| P:[100,2A5E) | Mixed reachable code, tables, templates, indirect targets |
| X:[0,EB), Y:[0,11F) | Global control/protocol/constants; field meanings partial |
| X:[EB,15B) | Twelve eight-word normal descriptors plus two other entries |
| X:[57A,8F2) | Twelve 4A-word event/coefficient contexts |
| Y control starts 11F+60*i | Twelve control/secondary regions; ownership overlap needs field-level bounds |
| Y:[59F,77F) | Twelve 28-word sample/post contexts |
| X:[C00,1000),[2800,2C00) | Host/table staging and backup |
| X/Y:[1000,1400) | Separate output/input ring memory |
| X:[1400,1600),[2400,2800) | Scratch/table generation work |
| X:[1600,1940) | 832 uploaded filter-coefficient words |
| X kernels 1960+C*i; template 1A80 | Per-slot kernels; surrounding global/state span not wholly classified |
| X:[2000,2200),[2200,2400) | 512-word frequency / normalization tables |
| X:[2C00,2DF0), Y:[A01,A61) | Shared voice/audio/filter work; 96-word lane scratch in Y |
| X:[2DF0,2F30) and following globals | Group sums/output/global state; full computed extents unresolved |
| Y:[E30,F3F),[F3F,1000) | Copied constants followed by ISR/effects/ring state |
| Y:[2000,2006) | SHI ISR saved registers |
| Other X/Y ranges | See CSV ledger; classified use is coarse/overlapping, not a proven partition |
| Shared:[30000,38000) | 32K words; P/X/Y accesses alias the same physical memory |
| External ≥40000 | Sample/table access verified; physical capacity/wait states unresolved |
| Hardware stack | DSP architectural return stack; not an identified reclaimable X/Y allocation |

Candidate ranges (none is **VERIFIED AVAILABLE**):

| Range | Words | Status / constraint |
|---|---:|---|
| P:[2A5E,4000) | 5,538 | POTENTIALLY AVAILABLE under conditional part/core/mode; 16,614 packed bytes |
| X:[4000,6000) | 8,192 | POTENTIALLY AVAILABLE; computed/host access non-alias proof missing |
| Y:[3000,4000) | 4,096 | POTENTIALLY AVAILABLE; effects/indirect upper extents missing |
| Shared:[34003,38000) | 16,381 | POTENTIALLY AVAILABLE; queue/service extents and aliasing unresolved |

No additional persistent state words are proved available. The shared queue
reservation [30002,34000) is conservative, not a validated capacity limit.
External space is not free/on-chip RAM by implication. Broad ledger ranges
denote reviewed activity; they do not claim every word is occupied or all
unlisted words unused. Audit inventories include indirect operands expressly
to expose this limitation.

**VERIFIED loader mechanics:** ARM 08029200 reads stream count bytes 1/2
(16-bit count), includes two header words, chunks up to 170 words. A 4000-word
program fits that counter format in principle. **UNRESOLVED deployable extension:**
normal channel-one stream immediately follows at ARM offset 8110, so extending
the first record requires layout/metadata changes; no contiguous append space
in the ARM image or relocation-safe extension has been established. No patch
was attempted. No normal dead region is declared reclaimable.

## I. Worker dependency

**VERIFIED lookup protocol:** producer queues one X-space address per word
in shared memory starting 30002. Worker P:120..126 reads it, fetches X at
that address, and replaces the queue word with the result. Consumer reads
through the Y alias of the same shared physical memory. Selected three-lane
profile: 192 requests/voice/block, six worker instructions/fetch, subtotal
1,152; counts vary with modes and repeats. ICC reset/completion handshakes
and polling contribute unbounded-from-this-analysis overhead. No proven
maximum outstanding requests, capacity check or backpressure bound exists.

**VERIFIED request-free stock path:** P:7A7..7C2, mode<8, distinguishes
request/completion using bit23 and supplies lane samples from cached X:2D70
on completion at P:7BA/7BB without P:775 lookup submission. Thus individual
voices need not request the worker. **HYPOTHESIS option A:** a local generator
can follow that scheduling pattern while other paths retain worker service.
This does not justify removing global P:759 handshake or worker program.
**UNRESOLVED options B/C:** reuse for different work or change both programs
needs a new protocol/capacity proof. None is implemented.

## J. Corrected static cost and scaling

**Correction to Phase 5:** loops P:810..816 and P:83D..846 use X:3C=31,
not X:3D=15. Their contributions are 558 and 837 instructions respectively,
instead of 270 and 405. Selected major-loop subtotal is **4,355**, replacing
3,635. Old phase-5 saved reports are preserved as superseded evidence;
`builds/phase6-corrected-contract` is the corrected export.

| Selected major loops | Issued instructions/block/voice |
|---|---:|
| Phase progression, both passes | 384 |
| First address interpolation / second result arithmetic | 558 / 837 |
| Absolute-value loop | 240 |
| Six coefficient ramps / lane combination | 384 / 544 |
| AA8 ramp / normalization | 64 / 704 |
| BDD scale / recursive filtering | 64 / 320 |
| Final group gain accumulation | 256 |
| Total | 4,355 |

Hardware DO repeats are expanded; extension words do not count as extra
instructions and parallel moves stay part of one issued instruction. Calls,
setup, control preparation and other loops are excluded. This is a verified
subtotal for the stated branch/profile, not a minimum for all patches or a
complete worst case. Even assuming ideal one-cycle issue would not convert
it into a measured cost; multicycle operations, external-memory waits,
pipeline, IRQs, SHI traffic and synchronization require separate timing proof.

| Active voices, selected profile | Channel-zero subtotal | Worker fetch subtotal | HYPOTHESIS selected voice generation/post range |
|---:|---:|---:|---:|
| 1 | 4,355 | 1,152 | 5,000–7,000 issued instructions |
| 6 | 26,130 | 6,912 | 30,000–42,000 |
| 12 | 52,260 | 13,824 | 60,000–84,000 |

The rough range is an allowance for selected local setup, not an independently
bounded timing measurement. Request/worker work can overlap, so subtotals
must not be added as serial wall-clock cycles. Per-slot lifecycle/control
scales with contexts even when a voice skips generation; bank processing
scales with bank activity, and host/ring/ISR/synchronization/global output
remain block overhead. Mode/repeat-dependent costs can exceed this profile.
**UNRESOLVED:** finite maximum total cost or available generator headroom.

## K. Formal theoretical mono-seam ABI

Scope: selected normal branch, slot i∈[0,12), E=57A+4A*i,
S=59F+28*i, control C=11F+60*i. This is an obligation ledger, not a safe
drop-in design. General branch clobber proof is unfinished.

| Contract item | Status and obligation |
|---|---|
| Invocation | VERIFIED request/completion passes precede per-slot consumer; output required once for the selected serviced block before P:9DD |
| Pitch input | VERIFIED C+10/C+3A current/target note and prepared Q+9+14*j increments; masked phase arithmetic. UNRESOLVED universal frequency unit/calibration and alternative mapping |
| Gate/lifecycle | VERIFIED C+3 flags and descriptor/bitmap lifecycle; preserve activation/release bookkeeping. Exact substitute generator gate ABI UNRESOLVED |
| Level | VERIFIED C+11 envelope, squared event/sensitivity path to target, patch-derived gain ramp E+42/+43; not all coefficients mean velocity |
| Patch/modulation | VERIFIED X:CC bank, banked parameters and prepared coefficients; UNRESOLVED complete mandatory parameter inputs for all modes |
| Persistent pointers | VERIFIED r0=E+0x31 in X, r4=S+0xC in Y (slot0 both 5AB); context X:2C and stock pointed-to states valid |
| Destination/length | VERIFIED X:[2C46,2C66), 32 mono words |
| Numeric output | VERIFIED signed 24-bit stored words, stock limiter/scaling behavior; HYPOTHESIS nominal Q1.23; absolute safe amplitude/headroom UNRESOLVED |
| Output deadline | VERIFIED before same-slot post-processing; block output before ring ISR consumer. Finite spare cycles UNRESOLVED |
| Phase and state effects | VERIFIED stock phase commit differs between request/completion paths and retained downstream states evolve; required substitute phase/state compatibility for all callers UNRESOLVED |
| Retained stock fields | VERIFIED keep envelope/note-follow/filter/gain/lifecycle state; no entire 28-word sample context reclaim |
| Scheduler | VERIFIED retain pass-bit23/completion bitmap/active descriptor logic; no stale queue entries or double updates |
| Worker/mailbox | VERIFIED global queue reset/completion protocol remains; request-free branch exists. Replacement compatibility UNRESOLVED |
| Forbidden memory clobbers | VERIFIED preserve other slots, group sums, stock tables, ring/staging/ISR state, queue/ICC/host metadata and code. Complete computed boundary/clobber set UNRESOLVED |
| Forbidden register effects | VERIFIED preserve live r0/r4, X:CC/current context, SR/MR scaling/rounding and caller stack semantics. Full accumulator/r0..r7/n/m/loop live set across modes UNRESOLVED |
| Scratch lifetime | VERIFIED buffer cannot be overwritten until selected consumer/gain/mix finishes; cannot retain generator state there |

P:9DD-selected BDD path consumes seven coefficient words; P:A1F skips
eight more before gain header/delta/current. The stock current gain reads
old gain while advancing the new ramp, then ASR4/MAC/ASL4 mixes into bank
sum. This is why amplitude and instruction parallelism are ABI obligations.
See `voice-output-contract.md` for exact producer/read PCs and finite-width
details. All unsupported input semantics and forbidden sets stay unresolved.

## L–N. Feasibility gate, blockers and next step

| Gate | Answer |
|---|---|
| A: enough known program memory? | NOT-YET-DETERMINED. Conditional 5,538-word tail; no generator requirement or deployable extension proof |
| B: enough known X/Y state RAM? | NOT-YET-DETERMINED. Zero words proved safely available; candidates only |
| C: provable execution-time budget? | NOT-YET-DETERMINED for voices. Nominal total 163,840 cycles/period conditional; no finite spare-budget bound |
| D: worker bypass without breaking invariants? | NOT-YET-DETERMINED for a replacement. Stock request-free path proves it is possible for some voices, not all global worker removal |
| E: writable seam without mandatory generator side effects? | NOT-YET-DETERMINED. Stock scratch writes proved; lifecycle/phase/clobber/scaling obligations remain |
| F: ready for a resource-qualified Plaits architecture comparison? | NOT-YET-DETERMINED. Conditional estimates can be recorded; hard fit cannot yet be decided |

Blockers: actual part/core/mode and clock wiring; indirect-memory ownership
and queue bounds; all-mode live/clobber and phase side effects; sample
normalization; worst-case total cycles including interrupts/external stalls.
No conclusion about Plaits fit follows from raw MIPS or unloaded words.

**Single best next step:** perform bounded points-to analysis of normal and
worker computed X/Y accesses, including host/table jobs, against candidate
X:[4000,6000) and Y:[3000,4000). Establish a proved non-aliasing persistent
state region (or disqualify these candidates). This resolves the immediate
state-memory blocker before any replacement design or implementation.
