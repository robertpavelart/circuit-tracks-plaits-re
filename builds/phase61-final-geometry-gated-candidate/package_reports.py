"""Package already-validated bytes and update current documentation only.
Historical research/candidate files and pinned sources are never modified.
"""
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[1]
def link(name):return f'[\u200b{name}](<C:/Proj SSD/CODEX/CIRCUIT/builds/{O.name}/{name}>)'.replace('\u200b','')
def main():
 v=json.loads((O/'final-validation.json').read_text());assert v['verdict']=='PASS'
 name=v['candidate'];old=R/'builds/phase43-hardware-test-candidate';meta=json.loads((O/'construction.json').read_text())
 for ext,key in (('bin','BIN_sha256'),('syx','SYX_sha256')):assert hashlib.sha256((O/(name+'.'+ext)).read_bytes()).hexdigest()==v[key]
 identity=f'''|Artifact|Bytes|SHA-256|
|---|---:|---|
|{name}.syx|{v['SYX_bytes']}|`{v['SYX_sha256']}`|
|{name}.bin|{v['BIN_bytes']}|`{v['BIN_sha256']}`|

CRC-32/MPEG-2: **{v['CRC']}**. Application `[08010000,08075100)`; exclusive end **08075100**; image headroom **44,800 bytes** to08080000. Protocol product64/version572; distinct compared-header marker **N61GEO**. InitialSP20050000/reset0805C00D are unchanged. No Plaits code is present.
'''
 schema='''# Exact 12-byte schema and ownership

**PROVEN:** recordS=20044D70..20044D7B. MasterFX retains20044D7C..20044E57. Early constructor hook reserves both by moving heap limit20044E58→20044D70 before native constructors; the additional diagnostic capacity over existing MasterFX is exactly12 bytes. No extra persistent allocation is introduced. Native constructors and the installed first-mount path execute in the new image.

|Byte/bit|Meaning before authorization|Meaning after authorization|Writers / readers|
|---|---|---|---|
|S+0 bits0..2|BOOT0,VALID1,EXPORTED2,MOUNTING6; FAILED5|ACTIVE3,SUCCESS4,FAILED5|init/begin/snapshot/export/authorize/watch/invalidate/complete/fail; all lifecycle readers|
|S+0 bit3|unexpected-event terminal flag|same|invalidation hooks only; admission rejects it|
|S+0 bit4 throughS+3 bit0 (21 bits)|strict first-mount epoch:0 before first mount,1 thereafter|epoch1 retained|begin, terminal phase writes; authorization checks epoch1|
|S+3 bits1..7 (control bits25..31)|exported host session1..127 only in EXPORTED;0 otherwise|0; session is copied to payload|export writes; authorization compares exact session-bound control word|
|S+4..S+11|geometry64: bits0..12=fat;13..25=fatsz;26..38=data;39..51=entries;52..54=log2(cluster sectors);55=nfats−1;56=type−1;57..63=0|overlay described below|snapshot commits; export/auth read. No overlay at export|
|S+4|geometry byte0|fixed target mask2=coefficients,3=identity+coefficients|authorize writes; raw derives fixed address/total only|
|S+5|geometry byte1|session1..127|authorize writes; raw reads|
|S+6|geometry byte2|global chunk0(identity) or1..8(coefficients)|raw writes only whileACTIVE|
|S+7|geometry byte3|owner0(initial),1(read),2(reply); retained on failure|authorize clears as part of word store; raw sets; complete clears only on successful ACTIVE→SUCCESS|
|S+8..11|geometry bytes4..7|start tick32|authorize writes; watch reads unsigned elapsed|

This intentionally replaces the earlier conceptual28-bit epoch with21 bits plus7 export-session bits. The candidate permits **only epoch1**, never recertifies a later mount, and does not claim a globally unique token across power cycles. Host session is a transaction identifier, not cryptographic authentication.

Legal path: BOOT0→MOUNTING16→VALID11→EXPORTED(session<<25|12)→ACTIVE13→SUCCESS14. ACTIVE→FAILED15 on timeout/read/send failure. Unexpected drive0 mount/binding/stride events→unexpectedFAILED1D. SUCCESS/FAILED reject new capture. Completion requires exact13 under PRIMASK and cannot replace15/1D. Geometry overlay occurs only after matching epoch, both geometry words, export session and allowed target mask. Geometry remains immutable during export and waiting.

Snapshot accepts only fixedD4000 base/4096 stride+BPS, drive0/FAT12/16, current disk0 wrapper and registeredFS, representable scalars, valid factors and root relationship. Host independently validates domain bounds/FAT capacity/classification and computes both target intersections. Device snapshot is a bounded representation check, not a substitute for host domain validation. A successful RAM-only export implies a committed first snapshot. Native commit writes both payload words before validity publication, with interrupts masked and a barrier; no allocator/Storage/NOR/FS call exists in it.

Expected first-mount stride4096 publication is allowed only duringMOUNTING. Later stride/binding changes and slow remount invalidate, including changes to an otherwise numerically identical geometry. Registration checks the actual expected outer return address0801AE07. Cached normal file operations do not create a new snapshot. The hook at0801AE06 reconstructs the overwritten MOVS/IT outcomes before the original0801AE14 tail.

Preauthorization host timeout is10 seconds and consumes the host session without sending another command; it is not a device-side Storage cancellation. Device timeout applies only toACTIVE at5000 ticks, including wrapping tick arithmetic. H4 remains FAIL for in-session recovery: pending Storage/semaphore/buffer ownership is never forcibly released.
'''
 (O/'schema-and-protocol.md').write_text(schema+'''
## Fixed command grammar

Commands are exactly232 bytes, USB port0, F0 7D 43 54 prefix, session1..127 and finalF7. Command0E is geometry export with bytes6..230 zero. Command0F has byte6 mask2/3, bytes7..14 epoch32 as8 MSB-first nibbles,15..22 low geometry word as8 nibbles,23..30 high word as8 nibbles,31..230 zero. Old0D start is rejected. No address/length is accepted from the host.

Geometry reply is39 bytes: F0 7D CT 4E session, epoch32/low32/high32 encoded as24 nibbles, MPEG-2 CRC32 over bytes4..29 as8 nibbles, F7. Raw replies retain4D framing and per-packet+whole-transfer CRCs. Coeff-only skips identity globalindex0: indices1..8 then completion9,total512,completionbase82000. Explicit mask3 sends index0 identity23 plus1..8 coefficients, completion9,total535,completionbase81000. Raw target derivation is fixed81000/23 or82000+64*(index−1)/64. Identity is an independent explicit host option with its own mapping-intersection check; it is not silently enabled by coefficient permission.

The512-byte capture requires8 ordered64-byte chunks, exact addresses/indices/lengths, valid packet CRCs and exactly one valid completion with full CRC. The host buffers in memory; an explicit end-of-stream boundary validates duplicates/trailing packets before publication. A production transport adapter must drive the monotonic deadline and that boundary; this phase exercises injected transport only and opens no ports. All output files are fsynced in a fresh sibling staging directory, then published by one directory rename. Existing capture directories are never replaced. Failures discard reconstruction; no automatic retry or cleanup/storage command is sent. Optional identity and coefficients publish together. All included sample output is clearly marked SYNTHETIC.
''',encoding='utf8')
 trows=[]
 for t in v['transitions']:
  trows.append(f"|{t['transition']}|PASS; exact image installed|No|`{t['external_erase_ranges']}`|`{t['external_program_ranges']}`|0 /0|")
 findings=f'''# Phase61 final candidate qualification

**PROVEN — FINAL PRE-FLASH HARDWARE-TEST CANDIDATE. NOT YET HARDWARE-TESTED.** Offline qualification is complete for the constructed candidate below. No hardware, MIDI port, firmware transmission or reference-source modification occurred. Work resumed from saved Phase61 results; the binary was not rebuilt during final packaging.

{identity}
## Integrated behavior

**PROVEN:** all five legacy entries are redirected together:0806B6CC getter preserves MasterFX ABI;0806B748 invokes retained clock update then lifecycle-only timeout;0806B798 dispatches geometry/auth while rejecting old start;0806B850 uses stack-local raw buffering and authorized transport fields;0806BC46 redirects to masked ACTIVE→SUCCESS. Old diagnostic bodies in6B6CC..6BC8C are cleared except explicit redirects, preventing mixed-schema stores. Native helpers and original call-site trampolines are hash-bound in construction.json and independently reviewed full M-class listings.

**PROVEN:** installed constructor initialization plus actual first-mount snapshot at0801AE06 passes the59548-instruction native startup replay under the already-declared Phase59 peripheral completion/RTOS models. The valid compact snapshot is0180003480908F01. The runner now stops at0801AE14 after the installed hook; its reportedR0 at that tail is a reconstructed logging-string pointer, not the mount status. The original stock mount returned0 before the hook. First-mount stride4096 publication is permitted only during that mount; subsequent changes invalidate.

**PROVEN:**28 native boundary cases pass: initialization/constructors, first snapshot, export, invalid binding, remount/binding/stride/earlier registration invalidation, correct/wrong epoch, geometry/session mismatch, malformed/arbitrary payload, unauthenticated raw, duplicates, parser overwrite, both fixed-read modes, chunk0/4/7 read errors and timeouts, native wrapping timeout, disconnect, absorbingFAILED, repeated terminal requests, supported register/APSR/PRIMASK preservation and getter ABI. Native boundary tests explicitly model read completion and USB output; they do not claim physical DMA execution.

**PROVEN:** the coupled Main/parser→Storage worker→QSPI IRQ→USB-ring/completion replay passes with the final bytes for explicit identity+coefficients.9 reads/10 frames are reconstructed exactly; native Main returns, semaphore is free, queue/pending/sync are zero. It records345 guard checks and8 callee-saved register checks; minimumSP Main200080FC/Storage20009174/IRQ2004FFF0, with2460/1068/4076 bytes respectively to lower guards. Coeff-only exact output is separately covered by the native boundary suite. The coupled case uses a prequalified exported-geometry fixture; it is not one uninterrupted electrical reset-to-USB capture.

**PROVEN:**19 deterministic host cases pass, including14 required stream patterns, geometry silence/malformed/CRC cases, explicitly optional identity, and injected second-file IO failure. Timeout is10 seconds per host stage using a monotonic clock model. Failure creates no accepted capture directory, no retry, no second diagnostic request, and no storage cleanup command. Host requests are one geometry request and, only after validation, one authorization request. The two-request workflow is not a retry. Failure reports CAPTURE FAILED / DO NOT RETRY / POWER-CYCLE DEVICE BEFORE ANOTHER ATTEMPT.

## File-first and diff review

**PROVEN:** independent SYX decoder checks product64/protocol572, ordering/framing/nibbles/padding/image bounds and bitwise MPEG-2 CRC, then matches BIN. Four malformed serialized files are rejected. Exact structural reconstruction independently accounts for39469 changed/added bytes against clean pinnedSC35D8: explicit hooks/marker, cleared obsolete diagnostic pool, appended native helpers/trampolines and explicitFF alignment/reserved gaps. {link('classified-diff.json')} gives every exact span and category;0 unexplained bytes. Unused appended gaps are requiredFF, not counted as executable code. Existing DSP bytes remain unchanged fromSC35D8; cleanSC35D8's inherited changes versus official4486 remain inherited reference behavior, not Plaits changes.

**PROVEN:** the generated code's only direct calls below appended code are retained clock599B8, fixed read wrapper47C6C, USB route20C90, USB service35A50 and scheduler yield1BE60. Reviewed getter/trampolines have explicit original return/initialization tails. There is no diagnostic NOR write/erase entry or host-address decoding command. Fixed raw address-load pairs are81000 and82000. The full native raw loop and failure tests bind lengths and prevent unauthenticated/second reads. Bootloader/option bytes are outside the app image; exact update replay independently verifies bootloader equality.

## Exact installation and rollback

|Transition|Native result|Silent no-op?|External erase ranges (half-open)|External program ranges|81000 /82000 write-or-erase overlaps|
|---|---|---|---|---|---|
{chr(10).join(trows)}

**PROVEN:** all three saved native replays install their exact incoming image and leave bootloader64KiB byte-identical. N61GEO differs within the38 compared header bytes, so B1.3→candidate is not suppressed by header equality. Both rollbacks also execute actual installation. Candidate staging erases[0,66000), programs[0,65100); metadata erases[80000,81000), programs[80000,80017). Metadata erase ends exactly at81000; it does not include it. Both target sentinels remain exact. Internal erases stay within application08010000..08080000; candidate programming ends08075100. These are native address/state-machine replays with modeled flash/NOR completion, not tested physical installation or recovery.

## Remaining status

|Classification|Result / limit|
|---|---|
|PROVEN|No remaining known offline software blocker in the integrated candidate and required saved validation gates; historical Phase43/44 bytes and349 files across6 checked historical manifests are preserved;439 pinned sources remain identical.|
|PROVEN|H4 in-session Storage recovery remains FAIL by design. Any TEF/missing completion/timeout/disconnect/malformed capture requires no retry and full power cycle. No forced semaphore unwind exists or is attempted.|
|STRONG INFERENCE|Under admitted ordinary boot/task/control paths and successfully validated current geometry, no concrete preauthorization82000 corruption path remains. This reuses the completed Phase45–60 producer/mapping/IRQ triage, not merely the new no-write replay. Identity mapping and explicit permission remain separate; no authentic bytes have yet been acquired.|
|HARDWARE-ONLY UNKNOWN|Physical USB/DMA/NOR completion and electrical timing, real device geometry/target contents, physical SRAM/stack behavior, and successful hardware installation/rollback of this exact candidate. User-reported recovery entry/exit is not proof of rollback flashing. Offline replay is not a risk-free guarantee.|

Evidence: {link('final-validation.json')}, {link('file-validation.json')}, {link('construction.json')}, {link('native-tests.json')}, {link('candidate-startup.json')}, {link('coupled-tests.json')}, {link('host-tests.json')}, {link('schema-and-protocol.md')}, {link('b13-to-candidate-summary.json')}, {link('candidate-to-official-summary.json')}, {link('candidate-to-b13-summary.json')}.

Construction metadata erratum: its historical `name` field says snapshot_return because a loop reused that Python variable. The filenames, all bytes, hashes, CRC and native replay identities are correct; final-validation.json is the authoritative final candidate identity. This packaging fixes no firmware bytes. Earlier truncated .asm checkpoint views are preserved; `reviewed-components-*.asm` and `reviewed-trampolines-*.asm` decode every byte in M-class mode and are the complete review listings.

STOP. Await explicit user decision. No hardware action is authorized by this report.

FINAL HARDWARE-TEST CANDIDATE = PASS
'''
 # Count historical files from the actual validated manifests, not prose estimates.
 findings=findings.replace('349 files',str(sum(v['historical_manifests_preserved'].values()))+' files')
 (O/'findings.md').write_text(findings,encoding='utf8')
 (O/'README.md').write_text(f'''# Phase61 candidate — offline qualification complete

**FINAL PRE-FLASH HARDWARE-TEST CANDIDATE — NOT YET HARDWARE-TESTED.**

{identity}
Only this exact Phase61 pair is designated. All older diagnostic candidates/fragments are **SUPERSEDED — DO NOT FLASH**. This does not supersede official stock rollback firmware. Historical candidate files and reports remain unchanged as evidence.

Read {link('findings.md')} and {link('schema-and-protocol.md')}. Detailed exact diffs and all three install/rollback summaries are local. SHA256SUMS.txt authenticates this package. The host.py module implements the geometry/authorization/one-shot receiver with injected transport; it opens no ports. Tests and sample outputs are synthetic. Old Phase43/44 host tools use incompatible0D start and must not be used with this candidate.

H4 remains FAIL for in-session recovery. After any failed or uncertain attempt: **CAPTURE FAILED — DO NOT RETRY — POWER-CYCLE DEVICE BEFORE ANOTHER ATTEMPT**. No forced storage cleanup or retry is permitted. A new Python Session object alone is not evidence of a physical power cycle.

No installation or capture command is run or authorized here. STOP and await explicit user decision. Physical installation, capture and rollback remain untested.
''',encoding='utf8')
 superseded='''# Diagnostic candidate supersession

**PROVEN current designation:** only the exact Phase61 pair in final-validation.json is the FINAL PRE-FLASH HARDWARE-TEST CANDIDATE, NOT YET HARDWARE-TESTED.

**SUPERSEDED — DO NOT FLASH:** ALL older diagnostic firmware, internal images and fragments in Phase27 throughPhase60, including Phase41/42 internal builds, Phase43 `circuittracks-4486-nor-evidence-test.bin/.syx`, Phase43 `independently-decoded.bin`, and Phase44 `circuittracks-4486-nor-evidence-atomic-test.bin/.syx`. Old historical PASS statements and hardware-test instructions do not designate those artifacts for current use. Synthetic transcripts/data are not firmware or authentic device evidence. CleanSC35D8 and official4486 inputs are construction/rollback inputs, not the new diagnostic candidate.

Historical files are intentionally preserved byte-for-byte. This central supersession applies even when an old directory README is opened independently. Only final-validation.json identifies the current candidate. Official stock rollback firmware is not superseded. No hardware action is authorized by supersession.
'''
 (O/'SUPERSESSION.md').write_text(superseded,encoding='utf8')
 docs={
 'docs/CURRENT_STATUS.md':f'''# Current project status — 2026-10-16

**PROVEN: Phase61 FINAL HARDWARE-TEST CANDIDATE = PASS offline. NOT YET HARDWARE-TESTED.**

{identity}
{link('findings.md')} is the current decision point. The five legacy owners, first-mount geometry snapshot, RAM-only export, same-epoch/session authorization, fixed reads, timeout/one-shot containment and atomic completion are integrated.28 native boundary cases,19 host cases, installed startup and coupled replay pass. Independent file-first decode and all three exact install/rollback replays pass; no silent no-op, bootloader change or target NOR overlap occurs in those models.

All older diagnostic candidates are **SUPERSEDED — DO NOT FLASH**; see {link('SUPERSESSION.md')}. H4 remains FAIL for in-session recovery. On capture failure, no retry/second storage request and a full power cycle are required. This candidate contains no Plaits and does not qualify the four-track DSP architecture.

**HARDWARE-ONLY UNKNOWN:** real geometry/target bytes, physical timing/USB/DMA/NOR behavior and installation/rollback of this exact candidate. No hardware/MIDI access or transmission occurred. STOP; await explicit user decision. Prior current-status text is archived in the Phase61 documentation-before directory.
''',
 'docs/HANDOFF.md':f'''# Current handoff — Phase61

**FINAL PRE-FLASH HARDWARE-TEST CANDIDATE — NOT YET HARDWARE-TESTED.** Offline verdictPASS. Do not restart Phase61 construction or rerun completed transitions without an invalidating change.

Read {link('findings.md')}, {link('README.md')}, {link('final-validation.json')} and {link('schema-and-protocol.md')}. Current identity:

{identity}
All three native update replays completed: B1.3→candidate, candidate→official4486, candidate→B1.3. Each installs exactly, avoids silent no-op, preserves bootloader and excludes both target NOR intervals.28 native boundary cases,19 host cases, startup and coupled raw path pass. Exact diff spans and full M-class listings are packaged. Older truncated listings are historical; construction.json has a harmless name-field erratum documented in findings.

All pre-Phase61 diagnostic candidates are **SUPERSEDED — DO NOT FLASH**. Historical firmware/evidence/reference sources remain unchanged. Old0D host receivers are incompatible. H4 is still FAIL; no in-session recovery/retry/forced semaphore release. All host test artifacts are synthetic, not acquired NOR bytes. User-reported recovery entry/exit does not establish physical rollback flashing.

STOP and await explicit user decision. No hardware, MIDI opening or firmware transmission is authorized. Previous handoff text is archived under Phase61 documentation-before.
''',
 'docs/NEXT_STEPS.md':f'''# Current decision point — Phase61

**PROVEN: FINAL HARDWARE-TEST CANDIDATE = PASS offline. NOT YET HARDWARE-TESTED.**

STOP. Await explicit user decision before any hardware access, MIDI opening or firmware transmission. Construction and requested offline validation are complete; do not restart the research branch or port Plaits as a continuation of this task.

Current candidate identity and limits: {link('findings.md')}. All older diagnostic candidates are **SUPERSEDED — DO NOT FLASH** ({link('SUPERSESSION.md')}). The new host library uses geometry0E then same-epoch authorization0F, not old0D start. It has no automatic retry. All physical action requires a separately chosen session; no command is provided or executed here.

**HARDWARE-ONLY UNKNOWN:** real-device installation/rollback, actual target bytes and physical transport/DMA timing. H4 remains FAIL for in-session storage recovery; after failure, discard partial evidence, do not retry or issue another storage request, and require a full power cycle. No Plaits hardware firmware exists in this package.
''',
 'README.md':f'''# Circuit Tracks / Plaits research

**Current: Phase61 FINAL HARDWARE-TEST CANDIDATE = PASS offline — NOT YET HARDWARE-TESTED.** {link('findings.md')} records the exact candidate, independent validation and three completed native install/rollback replays.

All older diagnostic candidates are **SUPERSEDED — DO NOT FLASH**; {link('SUPERSESSION.md')} is authoritative. No hardware, MIDI port or firmware transmission occurred. Await explicit user decision before any hardware action. H4 remains FAIL for in-session recovery: failed capture requires no retry and a full power cycle.

This project studies Circuit Tracks DSP resources and Plaits integration. The Phase61 candidate is a fixed read-only NOR evidence diagnostic and contains no Plaits. Four-track Plaits resource architecture remains unqualified; synthetic test payloads are not current-unit evidence.

- [Current status](<C:/Proj SSD/CODEX/CIRCUIT/docs/CURRENT_STATUS.md>)
- [Handoff](<C:/Proj SSD/CODEX/CIRCUIT/docs/HANDOFF.md>)
- [Next steps](<C:/Proj SSD/CODEX/CIRCUIT/docs/NEXT_STEPS.md>)
- [Documentation index](<C:/Proj SSD/CODEX/CIRCUIT/docs/DOCUMENTATION_INDEX.md>)
- [Phase61 candidate package](<C:/Proj SSD/CODEX/CIRCUIT/builds/{O.name}/README.md>)

Previous root/current-status/handoff/next-step text is preserved in Phase61 `documentation-before/`. Other research documents retain their historical scope and do not override the current candidate designation.
'''}
 archive=O/'documentation-before';archive.mkdir(exist_ok=True)
 for relative,text in docs.items():
  p=R/relative;copy=archive/relative.replace('/','__')
  if not copy.exists():copy.write_bytes(p.read_bytes())
  p.write_text(text,encoding='utf8')
 (O/'checksums.json').write_text(json.dumps({k:v[k] for k in ('candidate','SYX_bytes','SYX_sha256','BIN_bytes','BIN_sha256','CRC','application_end_exclusive','headroom_bytes')},indent=2)+'\n')
 # Never include the checksum file itself in its own manifest.
 files=sorted(p for p in O.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt')
 (O/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(O).as_posix()+'\n' for p in files))
 print('Packaged',len(files),'files; candidate bytes unchanged; STOP')
if __name__=='__main__':main()
