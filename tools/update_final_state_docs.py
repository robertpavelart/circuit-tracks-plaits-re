"""Documentation/state reconciliation only. No builders, transport or RE imports."""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[1]
O=R/'builds/final-pre-hardware-documentation'
O.mkdir(exist_ok=True)
P=R/'builds/final-hardware-test-package'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['README.md']+['docs/'+n for n in ('HANDOFF.md','CURRENT_STATUS.md','NEXT_STEPS.md','PROJECT_OVERVIEW.md','FINAL_PREFLASH_REVIEW.md','RESEARCH_TIMELINE.md','MEMORY_AND_RESOURCE_STATUS.md','REVERSE_ENGINEERING_STATE.md','PLAITS_RESEARCH_STATE.md','DOCUMENTATION_INDEX.md','CLAUDE_REVIEW_PACKAGE.md','CLAUDE_REVIEW_PROMPT.md','SNAPSHOT_CONSISTENCY_AUDIT.md','FINAL_DOCUMENTATION_AUDIT.md','HARDWARE_TEST_PREFLIGHT.txt')]+['notes/qspi82000-hardware-readiness.md','notes/fixed-nor-evidence-diagnostic.md','builds/final-hardware-test-package/README.txt','builds/final-hardware-test-package/final-cheap-checks.md','builds/final-hardware-test-package/HARDWARE_TEST_PREFLIGHT.txt','builds/final-hardware-test-package/HASHES.txt']
baseline={}
for name in names:
    src=R/name;dest=O/'before'/name
    if not dest.exists():
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(src.read_bytes())
    baseline[name]=sha(dest)
(O/'before/SUPERSEDED-SNAPSHOT.txt').write_text('HISTORICAL / SUPERSEDED documentation before this reconciliation. Banners, hashes and next steps in these preserved copies are not current authority. Read the project docs/CURRENT_STATUS.md. No candidate in this snapshot is enabled by these copies.\n')
protected={str(x.relative_to(R)):sha(x) for x in P.rglob('*') if x.is_file()}
for n in ('circuittracks-nor-defect-closure-development.bin','circuittracks-nor-defect-closure-development.syx'):
    x=R/'builds/phase63-defect-closure'/n;protected[str(x.relative_to(R))]=sha(x)
if not (O/'protected-before.json').exists():
    (O/'protected-before.json').write_text(json.dumps(protected,indent=2)+'\n')
def L(path,label=None):return f'[{label or Path(path).name}](<C:/Proj SSD/CODEX/CIRCUIT/{path}>)'
def W(name,text):(R/name).write_bytes((text.rstrip()+'\n').encode('utf-8',errors='surrogateescape'))
def old(name):return (O/'before'/name).read_bytes().decode('utf-8',errors='surrogateescape')
status='''**OPERATIONAL PREFLIGHT = UNQUALIFIED. POST-READY ALLOCATION CENSUS = UNQUALIFIED. USB STORAGE JOINT PATH = PASS.**

Current through 17 October 2026 (Europe/Moscow). The Phase63 artifact is a temporary NOR diagnostic, not Plaits firmware; it has not been hardware-tested. Phase67's FINAL PREFLIGHT CLOSURE = PASS remains valid only within its scoped model. No concrete offline firmware blocker has been demonstrated; the accepted residual software uncertainty is post-READY indirect allocation reachability with an eight-byte modeled heap gap. Tools remain locked. Risk acceptance is neither proof nor authorization to use them.
'''
limits='''**H4 remains FAILED (H4 = FAIL) for bounded in-session recovery.** On any failed or uncertain raw capture: discard all partial evidence; DO NOT RETRY; send no second diagnostic/Storage request or cleanup command; full physical power OFF, USB unplugged, session ends. No forced semaphore release. A reset, new process, session identifier or deleted attempt marker is not a power-cycle substitute.
'''
authority=f'''Evidence precedence: {L('builds/final-indirect-resolution/findings.md','final allocation decision')} controls the remaining software proof boundary; {L('builds/final-two-check-closure/usb-joint-closure.md','USB joint-path closure')} records 36 passing focused cases. {L('builds/phase67-final-safety-disposition/findings.md','Phase67')} retains its bounded configuration/query/authorization-to-capture-entry scope. The frozen {L('builds/final-hardware-test-package/final-cheap-checks.md','package audit')} preserves the earlier two-gap history, with a current supersession notice. No model PASS is physical proof.
'''
candidate=f'''| Artifact | Bytes | SHA-256 |
|---|---:|---|
| {L('builds/final-hardware-test-package/circuittracks-nor-defect-closure-development.syx')} | 569229 | `9b420521a366c65c13fb871778fdbab612ca126cbb4ad60d0fd5bc12ecd253da` |
| {L('builds/final-hardware-test-package/circuittracks-nor-defect-closure-development.bin')} | 413952 | `edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9` |

CRC-32/MPEG-2: **1BB21302**. Marker: **N63DEV**. Application: **0x08010000 .. 0x08075100**, end-exclusive. The Phase63 originals and package copies have the same bytes; no later candidate was generated. Phase61 and the original Phase62 candidates are **FAILED / SUPERSEDED / DO NOT FLASH**; Phase43 is historical / SUPERSEDED / DO NOT FLASH.
'''
recovery=f'''## Recovery and accepted risk

**PROVEN — by user report on the physical unit:** recovery/bootloader mode can be entered; full power cycling exits recovery; B1.3 boots normally afterward; no firmware was transmitted during that rehearsal. This does not mean the diagnostic candidate was tested.

**UNKNOWN / NOT PROVEN:** recovery-mode host enumeration, uploader handshake in recovery, actual recovery flashing of B1.3 or official 4486, recovery from a non-booting diagnostic candidate, and guaranteed recovery. Physical candidate-specific recovery is **HARDWARE-ONLY UNKNOWN**.

**STRONG INFERENCE from the saved offline scope:** no concrete bootloader-loss path has been identified. **PROVEN in modeled install/rollback operations:** bootloader lies outside application erase/program ranges and remains unchanged. This is narrower than physical recovery success.

The user explicitly accepts the possibility of a soft brick requiring recovery, provided the bootloader remains accessible. Recovery success is not guaranteed. Acceptance does not convert UNKNOWN into PROVEN, close the allocation census, enable tools or authorize hardware action in this documentation task. See {L('builds/final-hardware-test-package/recovery-status.txt')}.
'''
tools=f'''## Operational tools — LOCKED

| Tool | Exact identity | Lock |
|---|---|---|
| {L('builds/final-hardware-test-package/live_host.py')} | Version `1.0.0-phase68-locked`; SHA-256 `9b8a7d3d088cdffe21257824cb16db602659d678d240e7266f468e92c3ae9dc9` | `live_enabled=false` |
| {L('builds/final-hardware-test-package/ct_uploader-final-offline-locked.html')} | SHA-256 `bf1ef00dbca9c3715932235249fcc8ba0a71d6f2f989c047aa8caf66b85e17a5` | `PREFLIGHT_QUALIFIED=false` |

PROVEN in saved mocks: 32 host cases pass. No live host or uploader operation was run for this update. The same exact frozen uploader is intended for candidate install and both rollback files. Do not manually toggle locks. A separately reviewed operational release with new hashes is required before hardware use; the current locked package is not that release.
'''
rollback=f'''## Rollback artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| {L('builds/final-hardware-test-package/circuittracks-B1.3-manifest-matched.syx')} | 598489 | `6f07376b5983a5e0350d4883ae9ed57a69bc735320afde9f43ca75017b8e8736` |
| {L('builds/final-hardware-test-package/circuittracks-firmware-4486-STOCK.syx')} | 432961 | `bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd` |

PROVEN: local byte identities. UNKNOWN: independent authentication of the local 4486 artifact against a fresh Novation-origin download. Modeled exact install/rollback, no silent no-op, bootloader equality and no target write/erase overlap do not prove physical rollback. See {L('builds/phase63-defect-closure/install-validation.json')}.
'''
allocation=f'''## Primary accepted residual SOFTWARE uncertainty

**POST-READY ALLOCATION CENSUS = UNQUALIFIED.** Static analysis did not exhaustively resolve indirect/virtual targets, including **0x0803C91C**, **0x0803C9C4**, and registry/object-method sites. No actual post-READY allocation >8 bytes was found; its absence is NOT proven. The modeled heap cursor is `20044D68`, cap `20044D70`: eight bytes, not physical stack margin or replenished per-request capacity.

The recovered normal-publisher set for `08022E22` has seven targets. Four are allocator-free; three lead to unresolved virtual continuations. The expanded ledger covers 260 encountered indirect sites, 233 unresolved, and 73 target summaries. These are conservative traversal counts, not 233 proven allocation hazards or an exhaustive complete graph.

PROVEN in four isolated allocator ABI cases: rejection reaches BKPT; if execution is artificially continued after BKPT, R0=`FFFFFFFF`, accepted by the generic wrapper as nonzero. Physical exception routing remains UNKNOWN. Safe failure cannot be assumed. These isolated inputs do not prove a post-READY occurrence. See {L('builds/final-indirect-resolution/findings.md')}, {L('builds/final-indirect-resolution/indirect-ledger.csv')}, and {L('builds/final-indirect-resolution/failure-semantics.md')}.
'''
defects=f'''## CLOSED — known defects and focused synchronization check

| Item | Closure and scope |
|---|---|
| Phase61 reservation bug: VALID could publish into unreserved memory | Reservation guard added in Phase62, retained with seven Phase63 regressions. Phase61 FAILED / SUPERSEDED |
| SD mount invalidated retained NOR geometry | Phase63 separates NOR binding/epoch semantics; SD/NOR native tests pass |
| NOT_READY / INVALID / FAILED status ambiguity | Explicit 39-byte CRC-protected status protocol and matching host handling |
| DMA still referenced former Main stack storage after return | Ownership fence before CPU use and common return; 31 saved DMA cases and later focused joint cases pass in their scopes; no forced unwind |
| Late SUCCESS overwrote failure/quarantine | Absorbing failure/atomic terminal handling fixed earlier and retained |
| USB Storage / diagnostic joint path | **USB STORAGE JOINT PATH = PASS**: 36 focused cases, both request orders, failure/late completion, disconnect/remount and resets; declared native/model seams |

Evidence: {L('builds/phase63-defect-closure/findings.md')}, {L('builds/phase63-defect-closure/sd-mount-fix.md')}, {L('builds/phase63-defect-closure/status-protocol.md')}, {L('builds/phase63-defect-closure/buffer-ownership.md')}, {L('builds/final-two-check-closure/usb-joint-closure.md')} and {L('builds/final-two-check-closure/joint-results.json')}.

Saved Phase63 results: 7 reservation, 28 native, 13 status/mount, 31 DMA, 32 host containment and 3 install/rollback transitions. None was rerun for this documentation update. CLOSED refers to demonstrated defects and stated regression scopes, not guaranteed physical behavior.
'''
models=f'''## Model-coverage history — scoped evidence

Phase64 closed narrow SPI2 startup modeling. Phase65 closed 16-bit SHI coefficient-transfer framing (144 uploads; 148 jobs posted; 147 idle completions observed), using synthetic coefficients. Phase66 reached USB controller READY with geometry intact and 3,186 allocator returns across two layers, without observed allocation failures or diagnostic-owned overlap. Phase67's bounded boot-SRAM fixture reached configuration/query/authorization and capture entry with zero new allocations and preserved geometry. It stopped at raw entry and is not uninterrupted reset-to-capture or real USB enumeration proof.

Further peripheral emulation has diminishing safety value; no SPI2/SHI/USB/DWT continuation or endless reverse-engineering loop is the current next step. The allocation proof boundary remains SOFTWARE UNKNOWN, distinct from HARDWARE-ONLY UNKNOWN timing, physical stack margin, current-unit bytes, completion behavior and candidate-specific recovery.
'''
windows=f'''## Windows / MSD — prepared, not physically applied or tested

Automount control alone is NOT sufficient isolation. Removable-storage access denial policy is prepared in {L('builds/final-hardware-test-package/windows-msd-policy.txt')}; applicability/enforcement with this unit remains HARDWARE-ONLY UNKNOWN. No scan/repair, format, Explorer browsing, SD changes or filesystem utilities. Close Components, DAWs and other MIDI users. Unexpected mounted volume or storage access means STOP. No OS policy was changed here.
'''
nextsteps='''1. Keep repository documentation current and operational tools locked.
2. Prepare a **separately reviewed operational release**, with new exact tool hashes and explicit treatment of the accepted allocation uncertainty; do not manually toggle the frozen locks.
3. In a future explicitly authorized session, verify all hashes on the actual sending machine and apply/verify Windows/MSD policy before connection. Stop if isolation cannot be established.
4. Conduct the controlled hardware test only under that separately reviewed release and explicit user decision.
5. Query geometry first; independently validate the retained geometry and `$82000` safety on the host.
6. Authorize only the exact validated epoch/geometry/session; exactly one fixed capture. Optional `$81000` identity requires separate target authorization.
7. On success, validate/hash/archive complete evidence and restore B1.3 using the agreed rollback plan.
8. On any failure, discard partial evidence, no retry or second diagnostic/Storage request, full physical power OFF, USB unplugged, session ends.
'''
review='''The independent Claude review is **reported by the user** as: **REASONABLE TO PROCEED WITH CONTROLLED HARDWARE TEST**, subject to explicitly accepted residual risk. The reported review found no concrete offline firmware blocker or bootloader-loss path and recognized the actual defect fixes. This records the supplied review conclusion, not a new independent review in this task. Later allocation findings remain SOFTWARE UNKNOWN even though earlier review emphasized hardware/model uncertainty. Neither favorable review nor accepted soft-brick risk changes OPERATIONAL PREFLIGHT = UNQUALIFIED or enables tools.
'''
W('README.md',f'''# Circuit Tracks / Plaits research

## Status — October 2026

| Question | Current state |
|---|---|
| Long-term goal | Four melodic Plaits tracks on Circuit Tracks, retaining useful sequencer, drums, mixer, FX and project workflow where feasible |
| Current artifact | Temporary NOR diagnostic firmware, **not Plaits** |
| Candidate hardware-tested | **NO**; only user-reported recovery entry/exit rehearsal |
| Known offline firmware blockers | None demonstrated |
| Operational release | **NOT YET ENABLED**; host and uploader LOCKED |
| Residual software uncertainty | Post-READY indirect allocation reachability with only eight bytes modeled heap gap |
| Recovery | Bootloader entry/exit physically rehearsed; recovery flashing not tested or guaranteed |
| Next step | Separately reviewed operational release → controlled hardware test preparation |

{status}
{review}
Start with {L('docs/HANDOFF.md')}, {L('docs/CURRENT_STATUS.md')} (exact candidate/tool/rollback identities), {L('docs/NEXT_STEPS.md')} and {L('docs/DOCUMENTATION_INDEX.md')}.

{limits}
Authentic `$82000-$821FF` coefficients have not been captured. P:`$0282-$0386` reclaim is not finally qualified; final safe P/X/Y budget remains UNKNOWN. Future four-track design shares model code and keeps independent track state; default mono, `MAX_TRACKS_PER_MODEL = 2`, `MAX_POLY_TRACKS = 2`, engine-specific polyphony, eventual 24 engines.

Historical build/evidence directories and the earlier `circuit-tracks-plaits-re/` source snapshot are preserved, not current operational instructions. Phase61/original Phase62 are FAILED / SUPERSEDED / DO NOT FLASH; Phase43 is SUPERSEDED. See {L('docs/FINAL_DOCUMENTATION_AUDIT.md')} for supersession and this update's audit.
''')
W('docs/CURRENT_STATUS.md',f'''# Current authoritative project state

{status}
{authority}
## Current candidate — temporary NOR diagnostic

{candidate}
{allocation}
{defects}
{models}
## Independent review and user decision

{review}
{recovery}
{rollback}
{tools}
{limits}
{windows}
## Plaits dependency and current stop point

Authentic `$82000-$821FF` coefficients have NOT been captured. P:`$0282-$0386` (261 words) is not finally qualified; final safe P/X/Y capacity and complete Plaits hardware integration remain UNKNOWN. Synthetic inputs do not qualify physical provenance. The diagnostic exists to obtain that evidence; it is not an engine release.

{nextsteps}
No hardware, MIDI or transmission is authorized by this documentation update. See {L('docs/FINAL_DOCUMENTATION_AUDIT.md')}.
''')
W('docs/HANDOFF.md',f'''# Handoff — final pre-hardware review

{status}
{authority}
## Resume point

{review}
No further reverse engineering or peripheral modeling is the default continuation. Preserve the accepted allocation uncertainty explicitly; prepare a separately reviewed operational release before any later hardware session. Current candidate/tool identities: {L('docs/CURRENT_STATUS.md')}. Phase61/original Phase62 remain FAILED / SUPERSEDED / DO NOT FLASH; no candidate bytes were changed by this state update.

{defects}
{allocation}
## Diagnostic architecture

Reserved record `$20044D70-$20044D7B`; adjacent Master FX begins `$20044D7C`. First-mount geometry/lifecycle → RAM-only 0E export → independent host validation → exact first-epoch/geometry/session 0F authorization → fixed read. Required target `$82000-$821FF` is 512 bytes in eight ordered 64-byte chunks; optional `$81000-$81016` is 23 bytes separately authorized. There is no host-selected address/length. A dedicated Main stack frame remains owned until DMA/request/backend release. Epoch/session binding is not cryptographic or globally unique across power cycles.

{limits}
{recovery}
## Next steps, not actions authorized here

{nextsteps}
Read {L('docs/FINAL_PREFLASH_REVIEW.md')}, {L('docs/CLAUDE_REVIEW_PACKAGE.md')} and {L('docs/MEMORY_AND_RESOURCE_STATUS.md')}. Four-track Plaits remains a future design; authentic target bytes and final resource budgets are still missing.
''')
W('docs/NEXT_STEPS.md',f'''# Next steps — decision boundary

{status}
{review}
## Future sequence

{nextsteps}
{limits}
{windows}
Do not continue infinite offline investigation, port Plaits, regenerate a diagnostic image, silently relabel the allocation census PASS, or enable the frozen live tools. The accepted residual SOFTWARE UNKNOWN is documented in {L('docs/CURRENT_STATUS.md')} and {L('builds/final-indirect-resolution/findings.md')}. Hardware behavior and candidate-specific recovery remain HARDWARE-ONLY UNKNOWN. Existing recovery rehearsal is not a tested recovery flash. This task stops at documentation; preparation/review and any hardware action require the separately defined future scope.
''')
# Preserve the established design/numeric/provenance bodies, removing obsolete
# current-status prefixes instead of layering contradictory current banners.
for name,marker,title in [
 ('docs/PROJECT_OVERVIEW.md','# Project goal','Project overview'),
 ('docs/MEMORY_AND_RESOURCE_STATUS.md','# Historical Layout A','Memory and resource status'),
 ('docs/PLAITS_RESEARCH_STATE.md','# First target: Modal / Resonator','Plaits research state'),
 ('docs/REVERSE_ENGINEERING_STATE.md','# Stock ARM','Reverse-engineering state')]:
    body=old(name).split(marker,1)[1]
    body=marker+body
    body=body.replace('## Current corrected diagnostic','## Current corrected diagnostic — scoped evidence')
    body=body.replace('**STRONG INFERENCE:** Scales + Preset + Note at power-on enters bootloader/recovery, supported by reference bootloader analysis and reported uploader hardware tests. Official 4486 is the intended stock application rollback. **UNKNOWN:** recovery of this exact candidate from a non-booting application on this unit. Do not call recovery guaranteed; bootloader preservation is narrower than recovery success.', 'PROVEN by user report: recovery entry/exit and normal B1.3 boot afterward were physically rehearsed without transmission. Recovery enumeration, handshake and actual recovery flashes remain UNKNOWN. See CURRENT_STATUS.md for the accepted risk and exact limits; recovery is not guaranteed.')
    body=body.replace('Its original development metadata and uploader locks remain unchanged.','Its original development metadata and uploader locks remain unchanged.')
    body=body.replace('next action is independent final review, then an explicit controlled hardware-test decision, not another resource port.', 'next action is separately reviewed operational-release preparation under the accepted residual risk, not another resource port.')
    body=body.replace('Phase67 scoped preflight is complete. Earlier geometry/preservation investigations explain the gate, rather than pending automatic research.', 'Phase67 scoped preflight is complete; the later operational allocation census remains UNQUALIFIED. Earlier geometry/preservation investigations explain the gate, rather than pending automatic research.')
    prefix=f'# {title} — final pre-hardware review\n\n{status}\n{authority}\n'
    if 'MEMORY_' in name:prefix+=allocation+'\nAuthentic `$82000` data is not captured. P:`$0282-$0386` remains not finally qualified (261 candidate words, zero newly safe words); final safe DSP P/X/Y budget is UNKNOWN. Physical stack margin is HARDWARE-ONLY UNKNOWN.\n\n'
    if 'PROJECT_' in name:prefix+='The long-term design below is retained. Current firmware is a temporary evidence diagnostic, not an implemented Plaits product. User risk acceptance and the reported favorable review do not change the allocation census or unlock tools.\n\n'
    if 'PLAITS_' in name:prefix+='Authentic NOR evidence and later initializer/reclaim/resource qualification remain future dependencies. Phase65 coefficients are synthetic. No current-unit capture, complete engine admission or final P/X/Y fit is claimed.\n\n'
    W(name,prefix+body)
timeline=old('docs/RESEARCH_TIMELINE.md').split('# Research milestones',1)[1]
timeline=timeline.replace('Phase67 is current safety authority; Phase63 bytes are unchanged.', 'Phase67 retains its scoped model result; later final allocation/joint-path decisions control current operational status. Phase63 bytes are unchanged.')
timeline=timeline.replace('| Phase67 — CURRENT |','| Phase67 — scoped model |')
timeline=timeline.replace('Next action is independent final review, then explicit user decision; no automatic hardware access or further research.', 'Next action is separately reviewed operational-release preparation; no automatic hardware action or further research.')
W('docs/RESEARCH_TIMELINE.md',f'''# Research timeline — final pre-hardware review

{status}
## Latest recorded decisions

| Event | Current interpretation |
|---|---|
| Independent Claude review, user-reported | REASONABLE TO PROCEED WITH CONTROLLED HARDWARE TEST, subject to accepted residual risk; not physical proof |
| Frozen operational package | Exact Phase63 candidate and rollback identities, locked host/uploader; no operational release enabled |
| Final two-check closure | USB STORAGE JOINT PATH = PASS, 36 focused cases; allocation remained UNQUALIFIED |
| Final indirect resolution | Seven normal Content targets recovered; remaining virtual/registry targets, including 0803C91C/0803C9C4, not exhaustively bound. No actual >8-byte post-READY allocation found; absence not proven |
| Recovery packaging correction | recovery-status.txt clarified; SHA-256 169f295e37fc8b39d51ec5e38a54d2d341d52cd7b2bca7b8d762ff6ff019008d; 633 manifest-listed files verified |
| Current user decision | Soft-brick/recovery risk accepted without guarantee; tools stay locked pending separately reviewed release |

{authority}
## Historical research milestones
{timeline}
''')
W('docs/FINAL_PREFLASH_REVIEW.md',f'''# Final pre-hardware review — current decision record

{status}
{review}
## Evidence and candidate precedence

{authority}
{candidate}
{defects}
{allocation}
{models}
{recovery}
{tools}
{rollback}
{limits}
{windows}
## Separately reviewed operational release

Any release review must preserve these exact candidate bytes, keep the accepted allocation uncertainty explicit, bind new enabled tool hashes separately, and check recovery/rollback limits and host policy on the sending machine. Favorable review is not a guarantee or permission to toggle the frozen locks. No new firmware defect was demonstrated; further peripheral emulation has diminishing safety value. The current next step is release preparation/review, not a new reverse-engineering phase or an automatic hardware action. See {L('docs/NEXT_STEPS.md')}.
''')
W('docs/CLAUDE_REVIEW_PACKAGE.md',f'''# Independent review record and operational-release evidence map

{status}
{review}
This is a local evidence map; no external message or upload was sent. The supplied Claude verdict is recorded, not rerun. Any future operational-release review must account for the later allocation decision rather than assuming all residual uncertainty is hardware-only.

## Read in order

1. {L('docs/CURRENT_STATUS.md')} — identities, accepted risk, current gates.
2. {L('docs/FINAL_PREFLASH_REVIEW.md')} — fixed defects and decision limits.
3. {L('builds/final-indirect-resolution/findings.md')} and {L('builds/final-indirect-resolution/indirect-ledger.csv')} — remaining SOFTWARE UNKNOWN.
4. {L('builds/final-two-check-closure/usb-joint-closure.md')} and {L('builds/final-two-check-closure/joint-results.json')} — 36-case scoped PASS.
5. {L('builds/phase67-final-safety-disposition/findings.md')} and {L('builds/phase67-final-safety-disposition/callback-results.json')} — bounded fixture.
6. {L('builds/phase63-defect-closure/findings.md')}, {L('builds/phase63-defect-closure/sd-mount-fix.md')}, {L('builds/phase63-defect-closure/status-protocol.md')}, {L('builds/phase63-defect-closure/buffer-ownership.md')} — actual closures.
7. {L('builds/phase62-final-preflight/findings.md')} — historical FAILED / SUPERSEDED counterexamples, not a current candidate.
8. {L('builds/final-hardware-test-package/README.txt')}, {L('builds/final-hardware-test-package/HASHES.txt')}, {L('builds/final-hardware-test-package/recovery-status.txt')}, {L('builds/final-hardware-test-package/host-tool-identity.txt')}, {L('builds/final-hardware-test-package/uploader-identity.txt')} — frozen locks/identities.
9. {L('builds/phase63-defect-closure/install-validation.json')} and {L('builds/final-hardware-test-package/rollback-manifest.txt')} — scoped update/rollback evidence and provenance limits.
10. {L('docs/FINAL_DOCUMENTATION_AUDIT.md')} and {L('docs/CLAUDE_REVIEW_PROMPT.md')} — state audit and future release-review checklist.

Model history: {L('builds/phase64-spi2-model-closure/findings.md')}, {L('builds/phase65-shi-model-closure/findings.md')}, {L('builds/phase66-usb-safety-classification/findings.md')}. Numeric/resource history: {L('docs/MEMORY_AND_RESOURCE_STATUS.md')} and {L('docs/PLAITS_RESEARCH_STATE.md')}. Do not run experimental builders or old tests to assemble this map; actual listings, saved JSON and declared seams remain the underlying evidence.
''')
W('docs/CLAUDE_REVIEW_PROMPT.md',f'''# Future operational-release review checklist

{status}
{review}
The independent firmware review is already reported favorable. This checklist concerns a separately proposed operational release; it is not a request for another broad reverse-engineering phase and does not authorize sending a message or operating hardware.

1. Compare the proposed release against {L('docs/CURRENT_STATUS.md')} and its exact unchanged candidate identity.
2. Carry forward POST-READY ALLOCATION CENSUS = UNQUALIFIED and the accepted eight-byte-gap risk. Do not substitute zero observed allocations for absence proof.
3. Preserve USB STORAGE JOINT PATH = PASS within the documented 36-case scope and actual fixed reservation/geometry/status/DMA/late-success defects.
4. Review enabled tool changes and new hashes separately. Do not hand-toggle the frozen live locks or imply this documentation update enabled them.
5. Verify host-only validation, same-epoch authorization, exactly one fixed capture, atomic evidence acceptance and H4 discard/no-retry/full-power-off rules.
6. Distinguish user-reported physical recovery entry/exit from untested recovery enumeration, handshake, flashing and candidate-specific recovery. No guaranteed recovery or numerical brick-risk claim.
7. Retain Windows/MSD deny-access requirements and the fact they have not been physically applied/tested with the unit. Unexpected storage access means STOP.
8. Do not promote historical Phase43/61/62 identities or infer final Plaits resource qualification from diagnostic/model success.

Use PROVEN, STRONG INFERENCE, UNKNOWN, FAILED, SUPERSEDED and HARDWARE-ONLY UNKNOWN consistently. Review exact files and saved results. No hardware, MIDI, transmission, firmware regeneration or infinite peripheral modeling is requested. See {L('docs/CLAUDE_REVIEW_PACKAGE.md')}.
''')
indexfiles=['HANDOFF.md','CURRENT_STATUS.md','NEXT_STEPS.md','PROJECT_OVERVIEW.md','FINAL_PREFLASH_REVIEW.md','MEMORY_AND_RESOURCE_STATUS.md','REVERSE_ENGINEERING_STATE.md','PLAITS_RESEARCH_STATE.md','RESEARCH_TIMELINE.md','CLAUDE_REVIEW_PACKAGE.md','CLAUDE_REVIEW_PROMPT.md','SNAPSHOT_CONSISTENCY_AUDIT.md','FINAL_DOCUMENTATION_AUDIT.md','HARDWARE_TEST_PREFLIGHT.txt']
W('docs/DOCUMENTATION_INDEX.md',f'''# Documentation index — final pre-hardware review

{status}
'''+ '\n'.join(f'- {L("docs/"+n)}' for n in indexfiles)+f'''

## Evidence precedence and labels

{authority}
Current central authority is {L('docs/CURRENT_STATUS.md')}, reconciled with the latest user-supplied state and saved final closure evidence. Historical reports remain intact. The old package two-gap text is retained as a dated audit body with a supersession notice; only the allocation gap remains open. Phase61/original Phase62 are FAILED / SUPERSEDED / DO NOT FLASH; Phase43 is SUPERSEDED. The earlier `circuit-tracks-plaits-re/` tree is a historical source snapshot, not a second current release.

PROVEN means the stated artifact/code/model scope, or expressly attributed user physical report. STRONG INFERENCE means supported interpretation. UNKNOWN means not established; HARDWARE-ONLY UNKNOWN identifies unresolved physical behavior, not the software allocation proof gap. FAILED records a failed gate/test; SUPERSEDED prevents historical candidates/instructions from being treated as current. Accepted risk does not alter any label.

Current package: {L('builds/final-hardware-test-package/README.txt')}. Packaging recovery record: {L('builds/final-hardware-test-package/recovery-status.txt')}. This update's machine audit: {L('builds/final-pre-hardware-documentation/audit.json')}.
''')
W('docs/SNAPSHOT_CONSISTENCY_AUDIT.md',f'''# State consistency — final pre-hardware review

{status}
| Former contradiction | Current resolution |
|---|---|
| Phase67 PASS implies overall release PASS / all residual risk hardware-only | Phase67 scoped PASS retained; later all-root allocation census remains SOFTWARE UNKNOWN; operational preflight UNQUALIFIED |
| Both final cheap checks remain open | USB joint path PASS, 36 focused cases; allocation alone remains open |
| No actual >8-byte post-READY allocation found means none exists | Absence NOT proven; unresolved virtual/registry targets and eight-byte modeled gap retained |
| Allocation failure is safely NULL | Rejection reaches BKPT; artificial continuation returns FFFFFFFF, generic wrapper accepts it; physical routing UNKNOWN |
| Recovery entry rehearsal proves recovery flash | User-reported entry/exit/B1.3 boot with no transmission; enumeration/handshake/recovery flashing unproven |
| Accepted soft-brick risk closes an evidence gate or enables tools | Risk acceptance recorded separately; locks unchanged; new operational release requires separate review/hashes |
| Phase61/62 or Phase43 historical candidate remains current | Explicit FAILED/SUPERSEDED labels; only unchanged Phase63 identity current |
| A temporary diagnostic is Plaits firmware | No Plaits in candidate; authentic82000 missing; P0282 reclaim and final P/X/Y remain unqualified |
| Windows automount disable alone isolates storage | Deny-access policy prepared; physical enforcement untested; unexpected volume/storage access STOP |
| Model success repairs bounded unwind | H4 remains FAIL: discard/no retry/full physical power OFF/USB unplugged/session ends |

No candidate/tool bytes or historical experiment results were changed. Current identities and evidence: {L('docs/CURRENT_STATUS.md')}; final audit: {L('docs/FINAL_DOCUMENTATION_AUDIT.md')}.
''')
preflight='''HARDWARE TEST PREFLIGHT — PREPARATION ONLY / NOT AN ENABLED RELEASE
OPERATIONAL PREFLIGHT = UNQUALIFIED
POST-READY ALLOCATION CENSUS = UNQUALIFIED
USB STORAGE JOINT PATH = PASS (36 focused offline cases)

No candidate hardware test has occurred. Risk of a soft brick requiring recovery
is accepted by the user, provided bootloader access remains; recovery is not guaranteed.
The allocation proof remains incomplete; acceptance is not proof or a tool unlock.
Host and uploader remain LOCKED. A separately reviewed operational release with
new hashes and explicit treatment of residual risk precedes any hardware use.

FUTURE EXPLICITLY AUTHORIZED SESSION ONLY
[ ] Verify every package hash on actual sending machine; verify candidate/rollback/tool identities.
[ ] Recovery entry/exit rehearsal is user-proven; recovery enumeration, handshake,
    B1.3/4486 recovery flashing and non-booting-candidate recovery remain unproven.
[ ] Apply/verify prepared Windows removable-storage deny-access policy before
    connection. Automount alone is insufficient. Policy has not been physically
    applied/tested with this unit. Unexpected mounted volume/storage access: STOP.
[ ] Close Components, DAWs and other MIDI users. No Explorer browsing, scan/repair,
    format, filesystem utilities or SD changes.
[ ] Install only under separately reviewed operational release and explicit decision.
[ ] Geometry query first; independently validate retained geometry and $82000 safety.
[ ] Authorize only exact validated epoch/geometry/session; exactly one fixed capture.
    Optional $81000 requires separate target authorization. No retries/reconnect bypass.
[ ] SUCCESS: accept only complete validated evidence, hash/archive provenance,
    then restore B1.3 using agreed rollback plan.
[ ] FAILURE/UNCERTAINTY: discard partial evidence; no retry, no second diagnostic/
    Storage request, no forced cleanup; full physical power OFF, USB unplugged,
    session ends. Do not delete/reuse attempt marker. H4 remains FAIL.

This documentation task performs no hardware action, OS-policy change or transmission.
Current authority: docs/CURRENT_STATUS.md and docs/NEXT_STEPS.md in project root.
'''
W('docs/HARDWARE_TEST_PREFLIGHT.txt',preflight)
W('builds/final-hardware-test-package/HARDWARE_TEST_PREFLIGHT.txt',preflight)
W('builds/final-hardware-test-package/README.txt','''FINAL HARDWARE TEST PACKAGE — FROZEN / LIVE TOOLS LOCKED
OPERATIONAL PREFLIGHT = UNQUALIFIED
POST-READY ALLOCATION CENSUS = UNQUALIFIED
USB STORAGE JOINT PATH = PASS (36 focused offline cases)

Current through final pre-hardware review, 17 October 2026. Temporary NOR diagnostic,
NOT Plaits firmware; no candidate hardware test has occurred. No concrete offline
firmware blocker demonstrated. Residual SOFTWARE uncertainty: post-READY indirect
allocation reachability with 8 bytes modeled heap gap; no actual >8-byte allocation
found, absence NOT proven. Remaining physical behavior/recovery stays UNKNOWN.

Read project docs/CURRENT_STATUS.md and builds/final-indirect-resolution/findings.md.
final-cheap-checks.md preserves the older two-gap audit beneath a current notice;
builds/final-two-check-closure/usb-joint-closure.md supersedes its concurrency UNKNOWN.

The user accepts soft-brick/recovery risk, provided bootloader remains accessible.
Recovery is NOT guaranteed. Favorable independent review and acceptance do not
close the allocation proof, authorize hardware or enable live tools. Host/uploader
remain LOCKED. Separately reviewed operational release with new hashes required;
do not manually toggle frozen locks. Candidate and tool bytes are unchanged.

Files: candidate-identity.txt, host-tool-identity.txt, uploader-identity.txt,
rollback-manifest.txt, windows-msd-policy.txt, recovery-status.txt,
HARDWARE_TEST_PREFLIGHT.txt, final-cheap-checks.md, HASHES.txt, verify_hashes.py.
All 633 manifest-listed files must verify on the actual sending machine. HASHES.txt
itself is not self-hashed. Recovery rehearsal is entry/exit/B1.3 boot only, no send;
recovery enumeration, handshake and flashes remain unproven.

Future authorized plan: validate geometry first, exact epoch/session authorization,
one fixed capture, restore B1.3 on success. H4 FAIL: failure means discard/no retry,
no second diagnostic/Storage request, full physical power OFF/USB unplugged/end session.
Windows automount alone is insufficient; deny-access policy prepared, not physically
applied/tested. Unexpected mounted volume/storage access means STOP.

This package update changed documentation/hashes only. No hardware or MIDI action.
''')
cheap=old('builds/final-hardware-test-package/final-cheap-checks.md')
W('builds/final-hardware-test-package/final-cheap-checks.md',f'''# Current supersession notice — final pre-hardware review

{status}
{authority.replace('The frozen '+L('builds/final-hardware-test-package/final-cheap-checks.md','package audit')+' preserves the earlier two-gap history, with a current supersession notice.','The original audit body below preserves the earlier two-gap checkpoint.')}
Only the allocation proof remains incomplete; no actual >8-byte post-READY allocation was found, absence not proven. User risk acceptance and reported favorable Claude review do not enable tools or convert UNKNOWN to PROVEN. No candidate hardware test has occurred. Exact identities/accepted risk/next step: {L('docs/CURRENT_STATUS.md')}, {L('docs/NEXT_STEPS.md')}. No further peripheral emulation is requested.

## Historical original cheap-check audit — superseded status/next steps

The body below is preserved verbatim as historical evidence. Its concurrency UNKNOWN, two-gap decision and earlier recovery wording are superseded by the current notice, final joint closure and recovery-status.txt. It is not a competing current verdict. Candidate/tool byte accounts remain applicable.

{cheap}
''')
readiness=old('notes/qspi82000-hardware-readiness.md')
historical=readiness.split('## Historical Phase28–66 readiness entries below — superseded status/next steps',1)[1]
W('notes/qspi82000-hardware-readiness.md',f'''# Current readiness — final pre-hardware review

{status}
{authority}
Current risk acceptance, recovery limits, exact identities and future release preparation: {L('docs/CURRENT_STATUS.md')}. No authentic target capture has occurred; no new peripheral modeling or hardware action is requested.

{limits}
## Historical Phase28–66 readiness entries below — superseded status/next steps
{historical}
''')
fixed=old('notes/fixed-nor-evidence-diagnostic.md')
fixed=fixed.replace('Current authority: '+L('builds/phase67-final-safety-disposition/findings.md','Phase67 findings')+'; exact review identity and tooling locks:', 'Current authority: '+L('docs/CURRENT_STATUS.md')+'; exact review identity and tooling locks:')
W('notes/fixed-nor-evidence-diagnostic.md',fixed)
(O/'documentation-before.json').write_text(json.dumps(baseline,indent=2)+'\n')
(O/'update-files.json').write_text(json.dumps(names,indent=2)+'\n')
print('Current documentation written; audit report/manifest finalization remain.')
