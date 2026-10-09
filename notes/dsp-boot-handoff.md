# Phase 19B — reset and boot handoff

2026-10-06. Offline immutable loading only. No hardware, transmission, debugger,
flashing, patch, modified DSP image, worker execution or Plaits work.

**VERIFIED:** the previously recovered ARM uploader 0x08029260 sends bootstrap
through 0x08029200 to endpoint 0, then Selection-0/channel-0, then channel-1.
See `firmware-map.md` and `firmware/dsp/build-4486/manifest.json`; no new upload
was performed. The bootstrap's eight words are inspected statically only.

Its P:0..4 sequence reads OMR into X0, sets bits 7 and 22, clears bit 21 and
writes OMR. P:6 jumps to P:0xFFFFFE. Thus the established state transition is
bootstrap → ROM re-entry → stock payload entry, rather than a direct chip reset
into the payload. **SOURCE-DERIVED** SHI boot contract: two metadata words
(count, destination), followed by contiguous PRAM words; execution starts at the
load address. Here that address is P:0, whose original instruction jumps to
P:0x100. The ROM's complete register/peripheral handoff is **UNRESOLVED**.
[NXP DSP56724RM, tables 5-3 and 5-5](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf#page=102).

The classification is **B following C**: SHI/ROM handoff after the uploaded
bootstrap. Exact ROM implementation/revision, mode pins, physical core identity
and complete handoff state are not established. Bootstrap-established OMR bits
are evidence about the pre-ROM state; preserving every bit across ROM must not
be assumed. No ROM or bootstrap code was loaded/executed in this phase.

| State | Documented chip reset | Implementation probe | Stock handoff |
|---|---|---|---|
|PC|SHI mode reset entry 0xFFFFFE|0|Load/start address 0, conditional documented boot contract|
|SR|0xC00300, device figure 5-2|0xC00300 at constructor|UNRESOLVED; especially LF/FV, modes, interrupt state|
|OMR|0x000300 plus mode-pin nibble, figure 5-1|0|UNRESOLVED after ROM; bootstrap formula `(old \| 0x400080) & ~0x200000`|
|SP/SC|0/0|0/0|UNRESOLVED incoming; firmware P:107/108 writes zero before first JSR|
|SSH/SSL, 16 stack entries|No content reset value established|All implementation cells zero|UNRESOLVED; empty stack does not prove zero contents|
|R0..7|Numeric reset unspecified in reviewed sections|All zero, explicitly in resetHW|UNRESOLVED; R0 set at 10B before 10D|
|N0..7|Numeric reset unspecified in reviewed sections|All zero, explicitly in resetHW|UNRESOLVED until first-use audit reaches them|
|M0..7|FFFFFF each|FFFFFF each|UNRESOLVED incoming; stock 2779..2781 sets 00FFFF before clear|
|A/B, X0/X1, Y0/Y1|Numeric reset not established|Constructor zero|UNRESOLVED scratch; no zero seeding|
|LA/LC|Numeric reset not established|Constructor zero|UNRESOLVED; implicit loop behavior depends on SR|
|VBA|0|0|UNRESOLVED after ROM; vector locations alone do not prove VBA|
|SZ|Not initialized by hardware reset|BADBAD sentinel|UNRESOLVED, not a hardware value|
|EP|Not initialized by hardware reset|Constructor zero|UNRESOLVED|

Reset references: [DSP56300FM §2.3.3, §4.3, §5.4](https://www.nxp.com/docs/en/reference-manual/DSP56300FM.pdf#page=44)
and [DSP56724RM figures 5-1/5-2](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf#page=97).
Archived original manuals, hashes, selected text/layout pages and page indices
are under `builds/phase19b/documentation/verified/`. Layout/text extraction has
font warnings; the PDFs remain the authority. Regional/older family manuals
must not override this device's register diagrams. In particular its SR bits
14..12/19 are reserved and bit 18 is EMA; this is not identical to every classic
DSP56300 peripheral/mode profile in the library.

**EMULATOR VERIFIED:** the separate constructor-only probe has no stock program,
no executed instructions, and accepts only the reset routine's two explicit
zero priority writes at X:FFFFFE/FFFFFF. It supplies no GPIO/ICC/SHI behavior.
The probe is never used as stock CPU state. Its JSON is exported in each run.

**MISMATCH for a DSP56724-compatible reset profile:** library PC=0 versus chip
SHI reset entry FFFFFE, and OMR CDP=0 versus documented CDP=3. PC=0 is appropriate
as a boot-record entry address only with a justified post-load profile; it does
not repair the other differences. No stock execution mismatch was observed,
because no stock execution occurred. Library resetHW also clears only low four
CCR bits explicitly; the fresh constructor's other CCR bits happen to be zero.
This probe does not certify resetting an arbitrary warmed CPU.

**Execution gate CLOSED:** before even P:0, establish the live post-ROM control
state (particularly inactive loops, relevant modes and pending interrupts).
Before P:100, establish actual GPIO register handoff and a faithful read/modify/
write contract. Before P:102, establish the ICC peer publication contract.
Unused scratch may remain explicitly unknown if a later interpreter tracks
live operands; this phase has not implemented that stock operand tracker.
Neither guessing all registers nor demanding irrelevant scratch be zero is a
valid substitute. Do not seed SR/OMR from the implementation probe.

**Single best next step:** recover the minimum documented ROM handoff contract
needed through P:100..106, including GPIO and the first ICC publication, before
enabling any stock execution. No hardware observation is requested or performed.

## Phase19B-HANDOFF result — 2026-10-06

See `dsp-rom-handoff.md`, `dsp-bootstrap-analysis.md`, `dsp-icc-startup.md`.
The seven-instruction bootstrap only explicitly modifies X0/OMR/C and PC;
it supplies no GPIO/ICC initialization and does not establish whole SR after
the second ROM pass. GPIO control/direction reset words are1E1, but their
post-ROM words remain unknown. These reads are configuration latches, not
external pin-level reads. Numeric board pin values are unnecessary for this
prefix and were not invented.

Worker30002 is now traced as initial shared-queue cursor/progress publication;
main102..106 uses its initial equality for readiness. ICC reads have documented
flag/acknowledgement effects, so a constant response is not a sufficient model.
Upload order is channel0 beforechannel1, but first-read timing remains unknown.
Explicit100..106 operands do not use stack/AGU; inherited loop/IRQ state is still
unproved. Thus no defensible prefix was enabled:0 original instructions.

The future manifest has only an eligible PC0 assignment; all other numeric
handoff values remain null with provenance. New harness gate inspection refuses
defaults/preseeded tokens or execution enable, without constructing a CPU.
No global emulator defaults or firmware images were changed.

Best next step is now specific: obtain a matching authentic DSP56724/25 ROM
loader source/listing and statically trace SHI reset/re-entry exits. Public forum
attachment lead is recorded but not retrieved/verified. No support message was
sent. Do not resume19B2 or proceed19C automatically.
