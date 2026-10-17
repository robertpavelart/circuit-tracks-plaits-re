"""Record mandatory reservation-defect stop; no further preflight experiments."""
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase61-final-geometry-gated-candidate'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def link(p,label=None):return '['+(label or Path(p).name)+'](<'+(R/p).as_posix()+'>)'
def here(n):return link('builds/phase62-final-preflight/'+n)
def write(n,s):(O/n).write_text(s.strip()+'\n',encoding='utf8')
def main():
 c=json.loads((O/'correction-identity.json').read_text());old=json.loads((O/'original-reservation-tests.json').read_text());new=json.loads((O/'corrected-reservation-tests.json').read_text());native=json.loads((O/'native-tests.json').read_text())
 assert not old['passed'] and new['passed'] and len(new['cases'])==7 and native['all_passed']
 protected=0
 for line in (P/'SHA256SUMS.txt').read_text().splitlines():
  h,n=line.split('  ',1);assert sha(P/n)==h,n;protected+=1
 identity=f'''| Corrected, UNQUALIFIED artifact | Bytes | SHA-256 |
|---|---:|---|
| {c['candidate']}.syx | {c['SYX_bytes']} | `{c['SYX_sha256']}` |
| {c['candidate']}.bin | {c['BIN_bytes']} | `{c['BIN_sha256']}` |

CRC-32/MPEG-2 **{c['CRC']}**; marker **N62RSV**; exclusive app end **0x08075100**; image headroom **44800 bytes**. These are not hardware RAM measurements.
'''
 for ext,key in (('bin','BIN_sha256'),('syx','SYX_sha256')):assert sha(O/(c['candidate']+'.'+ext))==c[key]
 write('reservation-negative-test.md',f'''# Reservation-negative test — reproduced failure and focused correction

**PROVEN:** exact original Phase61 SYX decodes to BIN SHA-256`af5b62e371c1f9e6972b573e766088e54da6fadfcba911e62f25bd0edb0c763f`. Its hook at0801AE06 enters snapshot0806D500, which checks control16 (MOUNTING) but not allocator ownership. At limit20044E58 (not reduced), cursor20044D68, and record`16000000A5A5A5A5A5A5A5A5`, valid synthetic mounted metadata causes:

| Store PC | Address | Value |
|---|---|---|
|0806D686|20044D74|34008001|
|0806D688|20044D78|018F9080|
|0806D690|20044D70|00000011 (VALID)|

Output record:`110000000180003480908F01`. It wrongly writes all12 bytes and publishes validity without a reservation. The wrong-limit and overlapping-cursor variants also reproduce the missing check. This is an adversarial native entry-state counterexample, **not** evidence that ordinary hardware boot has already encountered that state. Native initialization normally reserves earlier; that does not satisfy the specifically requested defensive negative gate.

**PROVEN correction:** at0806D510, branch to a36-byte leaf guard at0806D800. Before any record access, require `[20002B44]==20044D70` and `[20002B48]<=20044D70`. Failure takes the existing restore tail0806D698, preserving the caller and making zero record reads/stores in the guarded snapshot path. Success setsR4 to the record base and resumes0806D518. The existing PRIMASK-masked save/restore envelope surrounds the guard; it adds no stack frame. No schema, raw-read protocol, transport or allocation architecture changes.

The corrected full7-case matrix passes: absent zero, absent garbage, absent partial MOUNTING, absent reservation with cursor beyond the record, wrong limit, reserved limit with cursor overlap, and correctly reserved positive first mount. Every negative case has0 private-record write intents, byte-identical input/output, geometry_valid=false, allocator unchanged and neighbor guards preserved. The positive case writes geometry and VALID normally. All cases execute the installed0801AE06 hook and original0801AE14 mount return tail; the stock logging sink alone is modeled. ReturnSP is callerSP+16 after the original frame pop. This proves safe bounded continuation through that tail, **not a complete boot-to-USB replay**.

The corrected bytes also pass the existing28 native boundary regressions, emitted to this Phase62 directory. No old result file was overwritten. The new candidate changed42 bytes:4 differing marker bytes,4-byte guard branch and34 differing bytes in a36-byte formerlyFF gap. Serialization was independently decoded/CRC-checked and BIN equality verified. It has **not** passed full new-image startup/coupled/install/rollback qualification.

Fixture correction disclosed: an initial corrected-image run replaced code after the old fixture had executed it, leaving Unicorn translated code cached. That result is retained as `corrected-reservation-tests-before-fixture-cache-fix.json` and is invalidated as corrected-code evidence. The runner now installs selected bytes before the fixture executes any instruction. The original Phase61 failure remains valid and reproduces with this corrected fixture ordering. Initial six-case evidence is also preserved separately.

Evidence: {here('reservation_negative_test.py')}, {here('original-reservation-tests.json')}, {here('corrected-reservation-tests.json')}, {here('native-tests.json')}, {here('reservation-guard.asm')}, {here('fix_reservation_guard.py')}, {here('correction-identity.json')}.

**PROVEN stop rule:** the requested negative gate failed on Phase61, so only this issue was fixed; the remaining preflight work was not started.
''')
 write('findings.md',f'''# Phase62 final preflight — stopped at the mandatory first gate

**FINAL PREFLIGHT CLOSURE = UNQUALIFIED. DO NOT FLASH EITHER IMAGE.**

The user's section1 says: “If the current code does not fail closed: STOP and fix only this issue.” The exact Phase61 image failed that gate. This phase therefore fixes only reservation-before-snapshot handling and stops; it does not claim to complete the live-host, provisioning or other requested preflight checks.

## Demonstrated defect and correction

**PROVEN:** with an unreduced heap limit and partial MOUNTING16 record, snapshot0806D500 writes private geometry at0806D686/688 and VALID at0806D690. Correctly reserved ordinary positive cases do not refute the missing defensive guard. Full reproduction and limits: {here('reservation-negative-test.md')}.

**PROVEN:** the minimal new guard checks heap limit and cursor before touching the record. Corrected7-case reservation matrix and28-case native regression pass. A separately named image was generated because this is a concrete firmware defect. It changes42 bytes; architecture, schema, transport, stack-local buffer and fixed read targets remain unchanged. The distinct N62RSV compared-header marker prevents equality with the old marker, but no new-image install/no-op replay has yet been performed.

## Corrected identity — NOT QUALIFIED

{identity}
Independent serialization round-trip/CRC/BIN equality and exact three-area diff are recorded in {here('correction-identity.json')}. A source checkpoint plus the failed-fixture artifact are preserved for audit. None is a final hardware-test approval.

## Phase61 designation withdrawn

Old Phase61 SYX`fe36e18bc83448b0e25cc21b8323e0e64e153f6e04abc042546f4a20e83731d3` and BIN`af5b62e371c1f9e6972b573e766088e54da6fadfcba911e62f25bd0edb0c763f` are **SUPERSEDED — DO NOT FLASH**. Their cryptographic hashes and historical results remain unchanged; their hardware-test eligibility is withdrawn by the new counterexample. This is not a claim that stored hashes stopped matching. All{protected} Phase61 checksum-manifest entries still verify; no Phase61 package/source/candidate file was edited. Current documentation carries this superseding status above the historical Phase61 text.

## REAL BLOCKERS REMAINING

| Item | Current state |
|---|---|
| Reservation-negative guard | PROVEN narrow correction passes; original Phase61 fails. Full new-image qualification remains pending. |
| Final runnable Windows host and mocked pre/post-send policy | Not implemented here because the mandatory stop rule fired. Existing Phase61 host library is not a final live CLI. |
| Pinned/provisioned rollback chain, including exact uploader | Not provisioned here; old B1.3 rollback replay used an in-memory stream. No new provisioning claim. |
| Startup→coupled exact-state continuity | Not executed here; no substitution of old exported-geometry fixture as continuity proof. |
| Corrected candidate full validation | New bytes invalidate automatic transfer of Phase61 whole-image startup/install/rollback admission; only focused serialization, diff and native tests were rerun. |

## CHEAP CHECKS REMAINING

Sections2–13 remain pending under the stop rule: exact startup/register/RAM seam and milestone records; final-image Main/Storage stack paths and DMA lifetime; heap cursor provenance/exhaustion; direct B1.3 updater/selector confirmation; Windows writable-MSD/automount exposure; cold/software/watchdog/power-removal record lifecycle; stage timeout ordering/pre-send versus post-send markers; mount NOT_READY/INVALID/FAILED distinctions; final live host/mock suite; rollback provenance/provisioning; recovery-rehearsal evidence reconciliation. Existing older tests remain evidence in their stated scope, not answers to these unexecuted questions.

No placeholder live_host.py or mock PASS report is created. Those would imply completion of work explicitly stopped at section1. The final preflight report/checklist identifies every withheld item instead.

## HARDWARE-ONLY UNKNOWNS

Physical boot, timing, USB/Storage/DMA completion, actual geometry/data, RAM margin, hardware faults and exact-candidate recovery/rollback remain untested. No hardware or MIDI ports were accessed; no firmware was transmitted. Ordinary occurrence of the adversarial reservation state is not asserted as proven.

## CONTROLLED RISKS

H4 remains FAIL: any raw capture failure discards partial evidence, burns the attempted session, forbids retry/second Storage request or forced semaphore release, and requires a **full physical power cycle**, not software/watchdog reset or a new process. The corrected guard does not solve H4. Recovery entry/exit has only the prior user-reported scope; no handshake/rollback test is newly claimed.

STOP after the focused correction. Await direction before resuming the remaining Phase62 work. No qualified current hardware-test candidate is designated.

FINAL PREFLIGHT CLOSURE = UNQUALIFIED
''')
 write('README.md',f'''# Phase62 — reservation correction only

**UNQUALIFIED — DO NOT FLASH.** Mandatory section1 counterexample triggered “STOP and fix only this issue.” See {here('findings.md')} and {here('reservation-negative-test.md')}.

{identity}
Corrected7-case reservation gate and28 native cases pass. Serialization/diff are checked, but continuity/stack/heap/MSD/reset/live-host/rollback provisioning and full corrected-image qualification are not completed. Historical Phase61 hardware designation is withdrawn; its files remain untouched. There is no final live host utility in this stopped package.
''')
 write('PRE-FLASH-CHECKLIST.txt','''DO NOT FLASH — PHASE62 IS UNQUALIFIED

[x] Reproduce original reservation-negative failure from exact Phase61 SYX.
[x] Fix only missing snapshot reservation/cursor guard.
[x] Preserve original Phase61 bytes and historical evidence.
[x] Distinct unqualified corrected BIN/SYX identity, serialization and exact diff.
[x] Corrected reservation matrix and native boundary regression.
[ ] Remaining sections2–13: explicitly NOT COMPLETED due mandatory section1 stop.
[ ] Final runnable host, durable marker, mock suite and stage/end-stream policy.
[ ] Exact startup-to-coupled continuity, final stack/DMA and heap audit.
[ ] B1.3 updater/selector direct confirmation, MSD/reset/mount-state checks.
[ ] Provisioned/pinned rollback SYXs and exact uploader/provenance.
[ ] Full independent qualification and install/rollback replay for corrected bytes.
[ ] Independent review and explicit user hardware-test decision.

No hardware access, MIDI port opening or transmission is authorized here.
H4: NO RETRY / NO SECOND STORAGE REQUEST / DISCARD PARTIAL EVIDENCE /
FULL PHYSICAL POWER CYCLE REQUIRED AFTER CAPTURE FAILURE.
Software/watchdog reset is not a substitute for that policy.
''')
 # Preserve current docs before adding a decisive superseding banner. Never
 # modify the immutable Phase61 package to retroactively rewrite its evidence.
 archive=O/'documentation-before';archive.mkdir(exist_ok=True)
 banner=f'''# Phase62 supersession — DO NOT FLASH

**FINAL PREFLIGHT CLOSURE = UNQUALIFIED. Phase61 hardware-test eligibility is withdrawn.** Its exact serialized image failed the required reservation-negative test: an unreserved partial MOUNTING record was written and marked VALID. A minimal separately named guard correction passes focused tests, but is **UNQUALIFIED — DO NOT FLASH**. The mandatory instruction was to stop and fix only this issue; final live-host/provisioning/continuity and remaining checks are pending.

Current authority: {here('findings.md')}. No current qualified hardware-test candidate is designated. Historical Phase61 PASS/“eligible” wording below is superseded for hardware use; its narrow recorded results remain evidence. No hardware/MIDI access or transmission occurred. H4 still requires full physical power cycling after a failed capture.

---

## Historical Phase61 documentation snapshot below

'''
 for p in list((R/'docs').glob('*.md'))+[R/'README.md']:
  relative=p.relative_to(R).as_posix();copy=archive/relative.replace('/','__')
  if not copy.exists():copy.write_bytes(p.read_bytes())
  text=p.read_text(encoding='utf8')
  if not text.startswith('# Phase62 supersession'):p.write_text(banner+text,encoding='utf8')
 # All original package evidence remains authenticated after doc updates.
 for line in (P/'SHA256SUMS.txt').read_text().splitlines():
  h,n=line.split('  ',1);assert sha(P/n)==h,n
 result=dict(confidence='PROVEN',scope='Mandatory section1 stop and reservation correction only',original_reservation_gate=False,corrected_reservation_gate=True,reservation_cases=7,corrected_native_cases=28,corrected_BIN_sha256=c['BIN_sha256'],corrected_SYX_sha256=c['SYX_sha256'],Phase61_manifest_entries_preserved=protected,full_preflight_completed=False,live_host_created=False,rollback_provisioned=False,hardware_access=False,MIDI_ports_opened=0,firmware_transmitted=False,verdict='UNQUALIFIED')
 (O/'stop-validation.json').write_text(json.dumps(result,indent=2)+'\n')
 files=sorted(p for p in O.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt')
 (O/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+p.relative_to(O).as_posix()+'\n' for p in files))
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
