# Phase 19B-IRQ: interrupt contract at application handoff

2026-10-06. **UNRESOLVED: interrupt exclusion and deterministic handler-prefix
convergence. Original main instructions executed: 0. Original worker: 0.**
Offline analysis only. No hardware, transmissions, firmware changes, original/
changes, modified DSP execution, Plaits, or scheduler replay. Existing primary
manuals and byte-checked listings were reused; no ROM refetch or installation.

## Evidence and scope

DOCUMENTED device model is conditional on the candidate DSP56724/25 profile,
not physical part identification. References below use PDF page numbers:

- [DSP56724RM Rev.1](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf):
  tables 3-7/3-8 (register addresses), 5-6..5-9 (priority/vector sources),
  chapter 10 (SHI), chapter 13 (ICC), chapter 6 (DMA stall).
- [DSP56300FM Rev.5](https://www.nxp.com/docs/en/reference-manual/DSP56300FM.pdf):
  sections 2.3.2.3..2.3.2.9 (masks, arbitration, fast/long interrupt pipeline),
  2.3.3 (hardware reset), 5.4.4.4 (VBA), 10.5.4 (DMA controls).

Local PDFs retain their previously verified SHA256 identities. Selected page
text, exact original instruction witnesses, complete nonreserved device vector
catalogue for both images, source/enable/reset catalogue and blocked attempts
are exported in `builds/phase19b-irq/final/`. Text extraction is an aid; the
manuals remain authoritative. A documentation omission is not proof of an
arbitrary ROM write or of preservation.

## A. Pending-source catalogue

DOCUMENTED: the device has the following source groups. Actual presence at
handoff is UNRESOLVED; these are architectural candidates, not recovered ROM
history. Full flag, enable, reset, priority and relevance details are in
`interrupt-sources.json`; every nonreserved vector is in
`conditional-vectors.json`.

| Source | Flag/event and local enable | PIC/vector |
|---|---|---|
| SHI/SHI_1 | X:FFFF91 HCSR HTDE15/HTUE14, HRNE17/HRFF19/HROE20, HBER21; HTIE11, HRIE13:12, HBIE10 | IPRP SHL3:2; +40/+42/+44/+48/+4A/+4C |
| ICC maskable receive | Y:FFFFD3 MIF1/MIE0 reflect peer ICCR3 at Y:FFFFD6 | IPRP ICIL19:18; +2A |
| ICC ACK | Y:FFFFD5 ACK0, cleared through RACK1; no separate reviewed ACK enable | IPRP ICAL21:20; +2C |
| ICC NMI | Y:FFFFD8 IF1 reflects peer ICCR1; ICDR1 write requires DRE | Fixed IPL3; +28 |
| ESAI/2 | X:FFFFB3 SAISR and last-slot events; RCR at FFFFB7 / TCR at FFFFB5 enables20..23 | IPRP ESL1:0; +30..+3E |
| ESAI1/3 | Y:FFFF93 SAISR; Y:FFFF97 RCR / Y:FFFF95 TCR | IPRP ESL1/3 field11:10; +70..+7E |
| DMA0..7 | Block completion/core latch; DSTR at X:FFFFF4 is completion status; DCRn DIE22/DE23 | IPRC fields12..23, IPRC1 fields0..3; +18..+26 |
| TEC/TEC1 | TCSR0/1/2 X:FFFF8F/8B/87 TCF21/TOF20; TCIE2/TOIE1/TE0 | IPRP TAL9:8; +54..+5E |
| IRQA..D | Internal synchronized/edge detection latch or pin level; PIC controls enable/mode | IPRC fields0..11; +10..+16 |
| External NMI | Falling-edge event, no ordinary SR mask | Fixed IPL3; +0A |
| S/PDIF | X:FFFF64 SIS/SIC; X:FFFF63 SIE | IPRP Rx13:12 / Tx15:14; device vectors +80..+AA |
| ASRC | Y:FFFC08 ASRSTR; FFFC01 ASRIER, FFFC02 route mask | IPRP ASL17:16; +B0..+BE |
| EMC/ICC error | Y:FFFFC8 discriminator, ICC EF/EIE, EMC TESR/TEIR/TEDR | IPRP LIEL23:22; +FE |
| Always-on | Constant source, enabled through its priority field | IPRP1 STIL23:22; +FC |
| DMA stall | Contention count exceeds X:FFFFF8 DMAS; disabled when DMAS=0 | Fixed IPL3; +0E |
| Core exceptions | Stack error, illegal instruction, debug request, TRAP/TRAPcc | Fixed IPL3; +02/+04/+06/+08 |
| Reset/watchdog | Restart event, not an ordinary interrupt-prefix return | Boot-mode reset entry |

GPIO has no separately enumerated generic GPIO interrupt in table5-9; external
IRQ/NMI alternate functions must be considered separately. No pin was sampled.
Software illegal/TRAP exceptions require an instruction trigger; they are not
arbitrarily injected software requests. None has been produced by application
execution here. Prior ROM/pipeline state remains unestablished.

DOCUMENTED reset evidence: SHI enables clear; HTDE resets1, HRNE/HRFF/HROE/HTUE/
HBER reset0. ICCR3/4 and maskable data/ACK fields reset0; ICCR1/2 reset4 with
DRE1/IF0. ESAI interrupt enables and listed status bits reset0. Timer TCSR
resets0. DMA DCR bits clear on architectural reset. S/PDIF SIE resets0 but
SIS resets2. ASRIER/ASRIEM reset0. DMAS resets0. Exact EMC reset fields are
retained in page witnesses; no invented all-zero summary. WCR prose says resetF
while figure12-2 says allzeros: **UNRESOLVED documentation conflict**, no WDT
handoff seed. Reset observations are not actual application state.

## B–C. PIC and SR domains

DOCUMENTED register addresses: IPRC X:FFFFFF, IPRP X:FFFFFE, IPRC1 X:FFFFFB,
IPRP1 X:FFFFFA, separately instantiated per core. A defined two-bit priority
field encodes 00=disabled, 01=IPL0, 10=IPL1, 11=IPL2. These are encodings,
not raw priorities0..3. External IRQ's third bit selects level/negative edge.

Family hardware reset clears priority registers; the device extends the PIC
with C1/P1. Applying that architectural statement to the added priority
registers is an extension interpretation, not a separately reviewed per-bit
reset table. None is established preserved through either ROM exit.

DOCUMENTED SR.I is bits9:8. Reset sets both bits (I=3). I0 permits IPL0..3,
I1 permits IPL1..3, I2 permits IPL2..3, I3 permits IPL3 only. Numerically,
maskable priority >= I admits it; IPL3 is unmaskable. Actual handoff SR.I may
be any documented encoding; which are reachable through this ROM is unknown.
Both bits: **BLOCKING UNKNOWN**. Full SR is not demanded.

VERIFIED bootstrap bytes have no explicit SR.I, PIC or VBA write. They update
OMR bits7/22/21 and carry, then branch into ROM; this is not a hardware reset.
Main uses two ROM passes, worker one without shim. No recovered ROM write list
or re-entry preservation contract exists. No emulator default is evidence.

VERIFIED later main P:109 ORI03,MR masks IPL0..2, after the ICC readiness loop.
P:25EF writes IPRP=9 (ESAI IPL0, SHI IPL1; other fields disabled);
P:25F1 clears SR.I. These definitions cannot dominate P:0/100. No reviewed
direct IPRC/C1/P1/VBA write is visible in the listings; this is not an indirect
ROM write exclusion. **UNRESOLVED** handoff priority domain for each defined
field: disabled or IPL0/1/2, without proved independent reachability.

DOCUMENTED pipeline qualification: FM2.3.2.6 arbitrates after instruction
execution; interrupt instructions are fetched from two vector words while
normal PC is frozen. A fetched request is not necessarily cancelled by a later
disable. SHI enables have a one-instruction masking delay; SR mask changes
have pipeline timing obligations (FM2.3.2.9). The previous abstract eligibility
predicate is useful for small-field reasoning, **not proof of the exact first
fetch after a ROM branch**. No interrupt inhibit was inferred from a JMP.

## D–E. SHI completion and ICC ordering

DOCUMENTED mode0 (table5-5, PDF103): SPI slave, 24-bit word count, load/start
address, payload, then execution starts at load address. It gives no reviewed
exit promise for HRIE/HTIE/HBIE, PIC, SR.I, FIFO/error cleanup or pipeline drain.
Reading HRX clears HRNE only when FIFO becomes empty. HROE clearing requires
HCSR-with-error read followed by HRX read. Consuming the last counted program
word proves neither extra FIFO data absence nor that sequence. No separate
SPI final-transfer acknowledgement contract establishing interrupt exclusion
was recovered. Disabling SHI by HEN0 resets status/path but preserves control
bits; **UNRESOLVED** whether ROM does that at exit.

VERIFIED ARM upload order: shim channel0, main channel0, then worker channel1.
Worker P:105 defines R5=30002; P:107 writes shared X30000; P:109 writes ICDR3.
That publication cannot precede worker loading. Upload order alone gives no
certified relative-core execution timeline at main's exact first instruction:
no cycle schedule, documented main-start-to-worker-load bound or ROM peer
write exclusion is available. Thus distinguish:

- Before any peer write, under a proved preserved-reset contract: data/IF0,
  no maskable ICC request. This is a conditional statement, not a seed.
- Stale/ROM-created state: UNRESOLVED, including ICC NMI from ICDR1.
- Later actual worker publication: sets MIF; MIE/PIC/SR govern eligibility.
  It is a real original instruction path, not an executed event here.

No 30002 was pre-seeded. Data and interrupt eligibility are distinct. The
present limited ICC model does not certify every disabled/empty transfer case.

## F–I. Conditional forks and handlers

SYMBOLIC finite architectural control classes are exported: no admitted
request, SHI nonempty, other SHI, ICC/ACK, other maskable (including always-on),
IPL3, and restart. Each has a documented trigger and first vector formula.
Reserved HRIE10 and disabled PIC00 are not eligible cases. Highest IPL and
device tie priority determine arbitration among simultaneously admitted sources.

**These are conditional classes, not a proven set of legitimate stock ROM-exit
states.** Present evidence cannot enumerate that exact set. No speculative
pre-entry CPU fork was run or certified. Small-field tests cover16 PIC/SR
combinations, not arbitrary 24-bit register brute force.

VBA hardware reset0 does not prove VBA at handoff. Its low8 bits are fixed0;
upper16 remain unknown. Actual first vector fetch is P:(VBA | vector-offset),
with pipeline caveats. An exact handler PC is therefore conditional.

VERIFIED bytes **if VBA=0 and these P locations are mapped**:

- Main vector44 is a long JSR to156. P156/158/15A writes Y2000..2002 before
  startup initialization; P15C sets M0=FFFF; P15E consumes HRX. P15F branches
  on PDRC8. One branch loads inherited X10 into R0 at198, selects memory space
  via X11.bit15 at199, writes HRX to X/Y:(R0)+ at19D/19B, updates X10 at19E.
  Other paths alter X10/X11/X12, Y2003..2005, PDRC9 or HTX. X0/R0/M0 are
  restored at1AD..1B1; RTI at1B3 needs valid interrupt stack/SR. No explicit
  OMR write in the handler. Material effects and live inputs preclude a
  proved common-state convergence.
- Main vector3E JSR1B4: stack saves, Y writes using Y1A modifier and YFFE
  cursor, DMA DDR0/DSR1 writes at1BC/1BE, Y21/Y22/YFFE updates. RTI at1D8.
  Requires initialized rings/stack; materially changes RAM and DMA.
- All other nonreserved main vectors and all nonreserved worker vectors are
  two NOP words. Conditional fast entry has no explicit register/RAM stores
  and resumes interrupted PC without RTI. Core acknowledgement is not
  peripheral condition clearing. Persistent SHI/always-on/error levels can
  request again. Even harmless one-shot NOPs do not prove finite convergence
  across every permissible pending-source history.

DOCUMENTED long entry stacks PC/SR, clears LF/scaling/SA, raises SR interrupt
level to exclude same/lower priorities; RTI restores PC/SR. Fast NOP entry
does not create that stack save. Entry stack/mapping/pipeline are not seeded.
**UNRESOLVED** exclusion, exact first action, deterministic finite prefix,
return-to-P0 and persistent state equivalence at actual handoff.

## J–O. Execution gate and next step

| Gate question | Result |
|---|---|
| A First control flow known? | NOT-YET-DETERMINED |
| B Interrupt excluded or fully modeled? | NO |
| C SR/PIC evidence sufficient? | NO |
| D Pending sources bounded at handoff? | NOT-YET-DETERMINED; architectural catalogue is bounded |
| E Inherited loop state irrelevant/known? | NOT-YET-DETERMINED; deliberately deferred until IRQ resolution |
| F P:0 authentically executable under current evidence? | NOT-YET-DETERMINED; gate does not authorize execution |
| G P:100 authentically executable under current evidence? | NOT-YET-DETERMINED; gate does not authorize execution |

BLOCKING: effective admitted/fetched request state immediately after final
SHI ROM transfer, with SR.I/PIC/peripheral masks/pending and VBA provenance.
Counts remain main0 / worker0; no handler, GPIO startup instruction, ICC poll
or publication actually executed. Loop-control inheritance was not broadened.

Single best next step: obtain a matching authoritative **final SHI ROM exit
fragment or handoff guarantee** covering interrupt enables/priorities/SR.I,
pending or already fetched requests and VBA, including second-entry behavior.
A complete register dump is unnecessary. A proof of no IPL3 request plus
settled masking can suffice; alternatively a sourced exact deterministic
handler prefix may suffice. Current manuals alone do not supply either.

Reproduce using existing Python, with fresh output paths:

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_irq_handoff.py --output-dir builds/phase19b-irq/new-audit
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_irq_handoff.py --output-dir builds/phase19b-irq/new-repeat
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_irq_verify.py --first builds/phase19b-irq/new-audit --repeat builds/phase19b-irq/new-repeat --output-dir builds/phase19b-irq/new-checks
```

Canonical final/final-repeat and checks/reproducibility.json supersede the
earlier verified/ export (before corrected ESAI exception-enable bit20 and
expanded handler-effect evidence). Protected input and sealed-core guards
are checked; no synthetic success is called authentic stock execution.
