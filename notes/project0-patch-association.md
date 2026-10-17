> Research/design evidence with its original experimental scope. Historical blockers and next steps below are not current project instructions; see [current state](../docs/CURRENT_STATUS.md).

# Phase20B4 — cached project0 patch association

2026-10-07. **PARTIAL association; event use not admitted.** Canonical reports:
`builds/phase20b-projectassoc/final-v2/patch-identity.json`,
`event-bank-slot-chain.json`, `qualification.json`.

**VERIFIED:** unchanged cached archive member`projects/project_0.ncs` is160780
bytes. Header signatureUSER, declared size160780, name`User Session`.
The first embedded340-byte synth patch is at158996=26D14(hex); second at
159336=26E68(hex). Installed Components migration copies680 bytes to158996.
Association is established through original load/view code, not the patch name.

Original project object holds the file buffer atobject+14(hex). EEFE is a
project-load/apply routine. Relevant identity/control steps:

* AF66 returns `base+CD64+8*i` for synth indices0/1. Cached records at
  52580/52588 contain `[0,0,0,0,0,0,0,0]` and`[32,0,0,0,0,0,0,0]`.
* F146..19C reads byte0, compares it to retained runtime property10(decimal)
  and produces the two branch flags atSP/SP+1. The saved property/state,
  enabling mode and actual branch are not recovered as a runtime snapshot.
* F442 selects the parameter view atobject+6C+344 and F448 forms source
  `filebase+26D14`. 3BE60 maps logicalbank0 to this same+344 view.
* F4AC selects+348 and F4B2 forms `filebase+26E68`; logicalbank1 uses that view.

**VERIFIED:** first embedded patch→logical parameterbank0; second→bank1.
The literal0/32 identifier bytes are exported. Their exact native pack/patch-slot
numbering is **UNRESOLVED**. Archivepatch slot0, logicalparameterbank0 and
allocated DSPvoiceslot0 are separate identities. Physical selected pack is not
inferred from archive name, historical metadata or these identifier bytes.

## Two original load branches

F438 tests flag0. Nonzero reaches virtual+12 atF450; bank view3BBE2 copies
340 bytes to the current backing patch. This admits the cached contents as
source bytes, not an executed runtime load.

The alternate F454..49C path reads the same embedded patch via descriptor
offsets and invokes the setter for IDsAE+11(hex)*m, m0..7, then ID5.
Those are the eight stored macro values and keyboard octave. The second bank
has the analogous F4BA..502 branch. A matching retained identifier is not a
proof that all embedded values are ignored or materially identical.

**TESTED serialized reconstruction / CONDITIONAL setter application:** starting
with the exact authored bank0 patch, overlaying these eight macro-value bytes
and keyboard byte35 produces the cached340-byte patch byte-for-byte: exactly
the seven discrepancies occur in that update set. Descriptor types/ranges
accept the recovered byte values. This does not claim arbitrary setter/callback
side effects, scheduler timing or preservation of a real runtime snapshot.

Thus neither branch restores the authored macro context under this bounded
binding. After complete original macro recompute, stored cached values yield
different corrected controls. See rudi-saw-poly-differences.md. The earlier
prepared selectors0/1 and offsets5/5 remain identical expected fields; they
cannot establish equivalence of all generator/filter inputs.

## Pattern data versus event association

**VERIFIED original layout:** AF46 computes
`filebase+6540*track+2E4` for the first two track groups. ADB2..AE12 initializes
eightCA8-stride pattern records per group; B03E..B0BE initializes32 records
with1C-byte step stride. Installed migration independently uses3240-byte
pattern stride. Pattern-group0 starts740; group1 starts26660.

This proves file geometry and a logicalbank0 patch source. It does not yet
connect a selected playback pattern/note to that parameter bank or a concrete
voice allocation. The first28 raw bytes are exported as an **unqualified layout
candidate**, without fabricated note/velocity/gate names. Original keyboard,
automation, probability/gate and note-field consumers have not been closed.
The previous direct caller2AB48 is a separate FF/0/96 event, not proof that the
first project record is a normal Synth1 note. No indirect callback is guessed.

The full chain event→track→synth→native pack/patch-slot→logicalbank→voiceslot
therefore remains **PARTIAL**. No exact event is admitted, regardless of the
same patch name. No DSP execution, Components launch, refetch or firmware edits.

Reproduce with fresh directories using plaits/seam/projectassoc/README.md.
Original sources, prior reports and renderer baselines are hash guarded;
focused original ARM windows under`evidence/` are byte checked. Linear listing
data/literals are not treated as executable code.
# Phase20B5 continuation — current disposition (2026-10-07)

**PARTIAL / STATIC STRATEGY EXHAUSTED.** Earlier20B4 load-boundary arithmetic
and seven-byte proof remain unchanged; they do not establish event-time patch
identity. AF46 literalgroup0 reaches2E2D8's first3F1F0 child+48 through
1FD34/2E35C. Full-copy/macro-only branch at actual playback remains unresolved,
as does complete physical track/bank/voice routing. Recording/automation
notifications cannot prove audible application order. Current report:
project0-sequencer-ordering.md; builds/phase20b-sequence/final/.
Stored context remains MATERIALLY DIFFERENT; runtime INSUFFICIENT EVIDENCE.
No event/checkpoint admitted. Static follow-up recommendations below are historical;
the current next step is a separately authorized coherent9D9 snapshot decision,
as specified in static-checkpoint-limit.md. No snapshot acquired or stock execution.
