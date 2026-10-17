> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase 19B-HANDOFF — minimum state and execution decision

2026-10-06. **Execution remains blocked. Original main/worker/bootstrap
instructions executed:0.** This phase establishes additional static contracts;
it does not resume19B2 or start19C/scheduler/audio replay.

| Main P | Original word(s) | Reads → definitions/accesses |
|---|---|---|
|100|0ABA4D|Read PCRG(YFFFFFA); C=oldbit13; writePCRG withbit13 cleared|
|101|0AB96D|Read PRRG(YFFFFF9); C=oldbit13; writePRRG withbit13 set|
|102|5EF000 FFFFD4|Read peer ICC data; defineA; associated ICC acknowledge/flag effects|
|104|0140C5 030002|ReadA; compare immediate30002; update compare flags, preserveA|
|106|0E2102|ReadZ: Z0→102, Z1→107|

There are five instructions and seven words.100/101 use short direct peripheral
addressing,102 an absolute Y address,104 an immediate operand,106 a direct branch.
All fetches use loadedP. No explicit R/N/M addressing, stack push/pop, X RAM
access or Y RAM access occurs in this prefix. SP/SC are explicitly initialized
at107/108 before10F's JSR. R0 is initialized10B before10D. PriorA is unnecessary
once102 performs the transfer; the actual transfer/compare mode must be correct.
No complete incoming accumulator/AGU/stack numeric snapshot is required simply
because those registers exist. Implicit inherited loop/interrupt state still
must be established.

**DOCUMENTED GPIO identity:** candidate DSP56724/25 YFFFFFA is PCRG; YFFFFF9
is PRRG. Both reset to0001E1, withbit13 reset0. Defined low-word R/W bit mask is
3CFFEF; blank/reserved positions are excluded. PCRG/PRRG reads access control
latches, not external pin samples. No read-clear behavior is described for these
configuration registers. Writes jointly select disconnected/input/output/
alternate-function operation. After100/101, bit13 selects output irrespective
of its old configuration. Its data-latch/output pin level remains unknown.
The actual pin sampling register is PDRG atYFFFFF8, not read by100..106.
[DSP56724RM §8.2.5, tables8-10/8-11](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf#page=143).

**Boundary of that proof:** reset latch words are not post-ROM values. No
authentic matching ROM write-path exclusion was recovered, so ROM modification
of PCRG/PRRG remains **UNRESOLVED**. ARM GPIO object configuration/polling does
not establish DSP latch contents or a physical G13-to-ARM signal mapping.
External pin levels are **BOARD-DEPENDENT / UNRESOLVED**, but are not numeric
inputs to the two configuration-register reads. No board pin level was guessed.

The minimum missing inputs are live control/mode/interrupt state and the GPIO
latches. For straight-line execution establish inactive inherited hardware-loop
state, compatible 24-bit transfer/addressing/compare behavior, valid P/peripheral
mapping, and controlled interrupt delivery at every boundary. If LF is known
inactive, unknown LA/LC and stack cells need not be invented. A partial known-bit
contract could suffice with qualified unknown-value tracking; the existing
synthetic harness has not established this for stock registers/peripherals.
No full SR/OMR literal may be set merely to satisfy the interpreter API.

| State | Actual evidence | Application classification |
|---|---|---|
|PC|Boot record load/start0; original JMP100|DOCUMENTED HANDOFF VALUE0;100 derived by static control flow|
|SR|Device resetC00300; bootstrap changesC only|BLOCKING UNKNOWN after second ROM; reset preservation unproven|
|OMR|Device reset300+pin nibble; bootstrap sets7/22,clears21|MODIFIED BY BOOTSTRAP before ROM; BLOCKING UNKNOWN at actual handoff|
|SP/SC|Reset0; stock107/108=0|FIRMWARE INITIALIZES BEFORE USE for first explicit call; implicitIRQ/loop preconditions unproven|
|SSH/SSL/SZ/EP|No established incoming contents; SZ/EP not reset initialized|UNKNOWN BUT UNUSED on explicit five-instruction path; IRQ/loop conditions apply|
|R0..7/N0..7/M0..7|ResetM=FFFFFF; no numericR/N guarantee; explicitR0/clearM setup later|UNKNOWN BUT UNUSED on explicit100..106; only reviewed later initialization certified|
|A/B/input registers|102 definesA before104; bootstrap definesX0, thenROM runs|UNKNOWN BUT UNUSED until dominated definition in this prefix|
|LA/LC|No numeric incoming values established|BLOCKING UNKNOWN conditionally on loop control; unused ifLF inactive is proven|
|VBA/priorities/masks/pending IRQ|Reset facts are documented, ROM effects unproved|BLOCKING UNKNOWN unless delivery is proven irrelevant for prefix|
|SHI|Boot mode0 SPI slave24 documented|Full application register/mask/FIFO handoff UNKNOWN; not required as explicit100..106 operand|
|PCRG/PRRG|Reset1E1, readable configuration latches|BLOCKING UNKNOWN handoff values|
|ICDR4|Reset0; peer worker publishes30002 later|BLOCKING UNKNOWN first-read state/timing; producer provenance VERIFIED|

**No additional register is claimed PRESERVED FROM RESET at application handoff.**
The bootstrap leaves most registers untouched explicitly, but two ROM passes
intervene. Reset-state evidence, bootstrap-local preservation and actual
application-state guarantees are distinct. See `dsp-bootstrap-analysis.md` and
`dsp-icc-startup.md` for their complete boundaries.

**PC/OMR discrepancy:** documented chip SHI reset entersFFFFFE with OMR priority
bitsCDP=3; library constructor usesPC0/OMR0. ApplicationPC0 is separately
justified by count/load boot semantics, not by the constructor. Bootstrap and
ROM residue cannot be inferred from either reset profile. No emulator defaults
were changed. `emulator/stock/handoff_gate.py` inspects the explicit manifest;
onlyPC0 has an eligible numeric assignment. Unknowns remain null and an execution
enable is rejected. It neither constructs nor executes a CPU.

**ROM-source search result:** the existing NXP manual documents loading and
entry, but supplies no complete reviewed application register contract. Targeted
search found a [public NXP forum lead](https://community.nxp.com/t5/Other-NXP-Products/DSP56725-bootloader/td-p/217563)
reporting support-supplied DSP56721 code and a comparison for56725. This is a
discovery lead, not authoritative source or compatibility proof. Attachments
could not be retrieved: web opens failed, direct public page returned403.
No login, access bypass or support message was attempted. A different-family
bootstrap listing cannot certify this device. Existing interpreter has no
verified matching ROM implementation; no ROM was loaded/run or emulated here.

| Phase19B2 gate | Answer | Scope |
|---|---|---|
|A P100 entry defensible?|NOT-YET-DETERMINED|Live handoff not established|
|B GPIO sufficiently modeled?|NO|Semantics documented; no qualified implementation/handoff inputs|
|C30002 provenance proven?|YES|Verified bytes plus conditional documented device ICC pairing|
|D ordering proven?|YES|ARM upload order; exact first-read/peer-publication interleaving unresolved|
|E SR/OMR sufficient?|NOT-YET-DETERMINED|No justified live-state/known-bit contract|
|F stack/AGU sufficient?|NOT-YET-DETERMINED|No explicit uses here, but inherited IRQ/loop uses not excluded|
|G one instruction may now execute without guess?|NO|Current contract cannot enable execution; not a permanent impossibility claim|
|H reach X/Y clear?|NO|Current gate closed; later dependencies also remain|

**Longest defensible executable prefix:0 instructions**, stopping beforeP0
(or before100 for the requested startup-entry profile). No invented GPIO value,
constant ICC stub, forced PC advance, worker-from105 entry or modified image was
used. Stock/worker micro-execution logs are empty by design; they are not tested
runtime traces. Conditional token provenance is established, but handoff safety
is not. Do not resume controlled startup yet.

**Single best next step:** acquire an authentic matching DSP56724/56725 ROM
loader source/listing, then statically trace reset and re-entry SHI exits for
SR/OMR/IRQ and PCRG/PRRG. This is a finite targeted provenance check, not another
generic alias census. No communication with NXP or anyone else is authorized
by this note or performed. Subsequent stock execution requires a separately
accepted sufficient contract; no19C follows automatically.

Reproduction (fresh output required):

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_handoff_contract.py --output-dir builds/phase19b-handoff/new-audit
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_handoff_contract.py --output-dir builds/phase19b-handoff/new-repeat
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B emulator/stock/handoff_gate.py builds/phase19b-handoff/new-audit/handoff-manifest.json
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_handoff_verify.py --first builds/phase19b-handoff/new-audit --repeat builds/phase19b-handoff/new-repeat --output-dir builds/phase19b-handoff/new-checks
```

Canonical evidence `builds/phase19b-handoff/final/` and `final-repeat/` includes
byte-checked original bootstrap/main/worker decoding, ARM instruction witnesses,
provenance manifest, GPIO/ICC contracts, primary manual pages/hashes and gate
answers. No firmware inputs or19A/19B implementation defaults were modified.

**TESTED:**14 static reports match byte-for-byte between final andfinal-repeat.
Four guessed-state/forced-enable refusals pass. Allten original extraction-pair
hashes match and the unchanged203-file19A source/harness guard passes.
Evidence: `builds/phase19b-handoff/checks/reproducibility.json`.

## Phase19B-ROM follow-up — 2026-10-06

See `dsp-rom-loader-source.md`. The public thread is now readable in the normal
browser, but exposes no source attachment links; publicAPI is unavailable and
archival attempts did not recover code. An official56720/21 manual was archived
and compared with the existing56724/25 manual. ISA/register-address compatibility
does not establish identical ROM exits; RAM maps and host-mode coverage differ.

Exact exit instructions/state remainUNRESOLVED. Separate main/worker manifests
under `builds/phase19b-rom/final/` retain null unknowns; only post-loadPC0 is
eligible. Main has twoROMpasses plus uploadedshim; worker has one and no shim.
No original instructions executed; no controlledstartup resumed. The specific
next prerequisite is offline historicalsource attachments or authenticROMlisting.

## Phase 19B-SYMBOLIC — narrower requirement

Full register/latch words are no longer blanket prerequisites. Partial BCLR/BSET
transfers preserve unrelated unknowns, and unused stack/AGU values need no seeds.
The first material unknown is interrupt eligibility at application entry:
inherited request state, PIC priority and SR.I can select the next original
instruction or handler delivery. No event injection does not establish absence
of an inherited request. Both original attempts stop before P:0, count0.

See `dsp-symbolic-handoff.md` and `dsp-partial-state-model.md`. A narrowly sourced
interrupt-exclusion/partial-mask contract could suffice; a full ROM listing is
not the uniquely necessary artifact. No concrete defaults were assigned.

## Phase 19B-IRQ — 2026-10-06

**UNRESOLVED interrupt-exclusion/convergence contract; original main0 / worker0.**
See `notes/dsp-interrupt-handoff.md` and `builds/phase19b-irq/final/`.

DOCUMENTED: PIC field00 is disabled,01/10/11 select IPL0/1/2; SR.I is bits9:8.
The always-on source at VBA+FC needs no external event when enabled. ICC NMI
and DMA-stall are IPL3 sources; ordinary mask3 alone cannot exclude them.
The SHI mode0 description specifies loading/entry, not a reviewed SR/PIC/FIFO
cleanup or interrupt-pipeline contract. No post-ROM reset value was promoted.

VERIFIED conditional on VBA0: main vector44 JSR156 writes Y2000..2002 and can
write HRX through inherited X10 to X/Y RAM; main vector3E JSR1B4 writes RAM/DMA.
Other nonreserved main vectors and every nonreserved worker vector are NOP/NOP.
Fast NOPs do not prove persistent peripheral requests clear or finite convergence.
VBA0 itself is not established after ROM. Upload order does not prove the exact
cross-core entry/publication interleaving. No 30002 was seeded.

SYMBOLIC source/vector classes are conditional architecture classes, not verified
reachable ROM exits. Exact first fetch also depends on pending/already fetched
interrupts and documented pipeline timing. The abstract field predicate alone
is insufficient. Loop inheritance remains deferred because IRQ resolution failed.
No stock or handler instructions executed; no scheduler replay enabled.

TESTED:16 canonical files match final/final-repeat;24 existing partial-state
checks pass;16 PIC/SR predicate cases pass; protected SYX/BIN and all ten DSP
extraction hashes match; sealed203-file concrete-core/harness guard passes.
Evidence: builds/phase19b-irq/checks/reproducibility.json.

The next prerequisite is a matching authoritative final SHI ROM-exit fragment
or handoff guarantee covering effective interrupt state/pipeline and VBA,
including second ROM entry. A full register dump is not required. Previous
phase gates and X35F/high-X ownership verdicts remain unchanged.
