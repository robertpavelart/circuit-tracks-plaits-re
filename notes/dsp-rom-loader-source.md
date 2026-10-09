# Phase 19B-ROM — source recovery and exit-state decision

2026-10-06. **ROM source was not recovered. Authentic stock execution remains
blocked; main/worker/bootstrap executed instruction counts are0.** Public
source discovery and official manual comparison are complete for this phase;
the primary goal of proving the ROM exit state has not been achieved.
No hardware, transmissions, flashing, firmware modifications or Plaits work.

The historical [NXP discussion](https://community.nxp.com/t5/Other-NXP-Products/DSP56725-bootloader/td-p/217563)
contains a2011-06-25 contributor report of two support-supplied DSP56721 source
attachments and a2011-06-29 report comparing a support-supplied56725 file.
These remain **UNRESOLVED source leads**, not vendor-authenticated code or a
ROM-revision equivalence guarantee. Source filenames, revision/date and hashes
are unknown because the attachments have not been obtained.

This phase materially improves the recovery record: the live public thread is
accessible through the normal in-app browser. A read-only DOM link inventory
shows no attachment/download/ASM/TXT/ZIP links. The public attachment API returns
HTTP403 to the CLI and is blocked by the browser backend. No login, CAPTCHA,
permission/security change, private-state inspection or access bypass was used.
Current-thread archive index returned an empty result and availability API no
snapshot. Targeted old community.freescale.com/forums.freescale.com archive
queries timed out. **These are retrieval limitations, not proof that the files
no longer exist.** No support or contributor message was sent.

**DOCUMENTED newly archived primary source:**

| Filename | Revision/date | Target | Kind |
|---|---|---|---|
|DSP56720RM.pdf|Rev1.1,02/2008|DSP56720/21|Official reference manual; not boot-ROM source|
|DSP56724RM.pdf|Rev1,02/2009|DSP56724/25|Existing official reference manual reused|

[DSP56720RM](https://www.nxp.com/docs/en/reference-manual/DSP56720RM.pdf) and
[DSP56724RM](https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf).
Original PDFs, selected-page witnesses and hashes are retained. No upstream core,
existing firmware or existing manual was refetched. The new manual download
installs no tools. No unrelated DSP563xx loader was substituted.

| Applicability portion | Classification | Evidence boundary |
|---|---|---|
|Core ISA|COMPATIBLE|Both document DSP56300 cores; not identical chip/ROM|
|SHI mapping|IDENTICAL|ReviewedXFFFF90 HCKR,91HCSR,92HSAR,93HTX,94HRX addresses|
|ICC|COMPATIBLE|Reviewed peerICDR3/ICDR4 pairing and flag/ACK mechanisms|
|PCRG/PRRG|IDENTICAL|ReviewedYFFFFFA/F9 mapping andreset1E1 diagrams|
|Mode0 boot protocol/OMR controls|COMPATIBLE|SPI slave24,count/load/Pwords; MS/MSW controls|
|RAM maps|DEVICE-SPECIFIC|56721 mode110 P6000/X9000/Y8000;56724 core0 P4000/X6000/Y4000;core1 P2000/X2000/Y2000|
|Additional host boot modes|DEVICE-SPECIFIC|56720/21 HDI24 paths must not be transplanted|
|ActualROMcode/exit and conditional assembly|UNRESOLVED|Missing source/binary; no directives or terminal instruction block inspected|

These classifications apply to the reviewed **documentation portions**, not to
an obtained DSP56721 source file. No full-source IDENTICAL/COMPATIBLE verdict can
be issued. Differences in private capacity/core maps alone require review of
every ROM scratch/destination access when source becomes available.

**VERIFIED original shim comparison:** its seven instructions setOMR7/22,
clear21, and jumpFFFFFE. It is a memory-mode setter plus ROM re-entry shim; it
contains no SHI receive loop or exit implementation. Under the candidate56724
core0 map, the main2A5E-word image exceeds defaultP1000 but fits mode110P4000.
This corroborates a reason for the mode-setting shim; it does not prove ROM
preserves the mode or identify the actual silicon. Side-by-side ROM disassembly
cannot be produced without authentic ROM code. `stock-witnesses.json` records
the immutable shim/main/worker bytes and that explicit limitation.

**Exact ROM exit flow: UNRESOLVED.** The documented abstract contract is to
receive count/start/Pwords, then enter that start address. It provides no exact
exitPC/opcodes/clobber list. The same load/output contract can coexist with
different register/peripheral residue; uniquely reconstructing a faithful ROM
from the packet format is therefore not supported. No invented ROM assembly,
binary or executable replacement was generated or run.

`main-handoff.json` and `worker-handoff.json` export every requested state group
with provenance and classification. PC0 is the only eligible exact assignment.
SR/OMR/control state, PCRG/PRRG and peripheral/interrupt residue remain null.
Scratch values are unspecified; reviewed application first definitions are
recorded separately. MainSP/SC=0 at107/108 andR0=2028 at10B are application
definitions, not incoming seeds. WorkerR5=30002 at105 likewise is not preseeded.
No additional field is claimed unchanged from reset through uninspected ROM.

**Core asymmetry:** main has two ROM passes separated by the uploaded shim;
worker has one pass and receives no uploaded shim. Do not copy main's pre-ROM
OMR mask or a hypothetical full exit snapshot into worker. Originalworker100
writes0 toHCSR, disabling SHI controlHEN; this does not establish the full
post-write statusword aszero or justify its inherited interrupt/GPIO state.

**Timeline:** verified ARM upload calls29284shim,29294main,292A6worker.
Documented record completion starts each program at itsP0; the final handoff
instructions and exact clock delay remain unknown. Main can reach its poll
before workerpublication under this ordering, so30002 must not be preseeded.
For a bounded readiness rendezvous, deterministic staged execution could be
adequate *once* both handoffs and reached peripherals are qualified: preserve
causal order, run the real original worker, connect actualICDR3→ICDR4 and log
flags/ACK. This is **HYPOTHESIS/design**, not a physical timing model or tested
execution. Full simultaneous audio scheduling is not needed or authorized here.

| First-execution gate | Result |
|---|---|
|Main100 entry established|NOT-YET-DETERMINED|
|Workerentry established|NOT-YET-DETERMINED|
|FaithfulBCLR/BSET with actualhandoff inputs|NO|
|QualifiedoriginalICC execution model|NO; staticproducerprovenance remainsVERIFIED|
|Allliveearlyunknownsresolved/irrelevant|NO|
|Authenticfirstexecutionjustified|NO|
|Originalinstructionsactuallyexecuted|0|
|Resume19B2|NO|

Runtimebranch/token/ACK validation is **NOT REACHED**. No CPU/core is instantiated
by the new audit; both manifests set execution_allowed=false and limit0. Main
and worker remain immutable files used for static witness checks only. No
patched or modified DSP image was executed, no completion fabricated, and no
phase19C/scheduler/Plaits follows.

**Single best next step:** obtain offline copies of the two historical
support-supplied source attachments, or an authentic matching ROM listing.
Validate target/revision and conditional paths, then trace the actual SHI exits.
Further inference from the boot packet alone cannot close this blocker.
Contacting support/contributors would require the user's explicit instruction;
none was sent. No hardware ROM read is proposed.

Reproduction (reuse existing local sources; fresh outputs):

```powershell
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_rom_exit_audit.py --output-dir builds/phase19b-rom/new-audit
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_rom_exit_audit.py --output-dir builds/phase19b-rom/new-repeat
& 'C:/Users/rober/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B tools/ct_rom_verify.py --first builds/phase19b-rom/new-audit --repeat builds/phase19b-rom/new-repeat --output-dir builds/phase19b-rom/new-checks
```

Canonical evidence: `builds/phase19b-rom/final/` and `final-repeat/`.
Recovery request/response logs are inpublic-fetch/ andhistorical-fetch/;
source catalog, applicability, abstract exit-flow limitations, two handoff
manifests, peripheral exit unknowns, timeline, gate answers and integrity hashes
are exported. Network discovery tools are separate from the offline audit:
ct_rom_public_fetch.py /ct_rom_archive_fetch.py; neither executes downloadedcode.

**TESTED:**13 final/repeat static reports are byte-identical; both handoff
manifests preserve provenance/null unknowns and closed execution gates. Protected
SYX/BIN hashes and allten extraction hashes match; unchanged19A203-file core and
harness source guard passes. `builds/phase19b-rom/checks/reproducibility.json`
records these results. They are static evidence tests, not stock/ROM execution.
