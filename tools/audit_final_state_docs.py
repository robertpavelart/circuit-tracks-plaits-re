"""Offline documentation/link/hash checks only. No experimental or live imports."""
from pathlib import Path
import hashlib,json,re,csv,subprocess
from urllib.parse import unquote
R=Path(__file__).resolve().parents[1];O=R/'builds/final-pre-hardware-documentation';P=R/'builds/final-hardware-test-package'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def link(p,label=None):return f'[{label or Path(p).name}](<C:/Proj SSD/CODEX/CIRCUIT/{p}>)'
before=json.loads((O/'protected-before.json').read_text())
docs_before=json.loads((O/'documentation-before.json').read_text())
package_allowed={'README.txt','final-cheap-checks.md','HARDWARE_TEST_PREFLIGHT.txt','HASHES.txt'}
expected={
 'circuittracks-nor-defect-closure-development.syx':(569229,'9b420521a366c65c13fb871778fdbab612ca126cbb4ad60d0fd5bc12ecd253da'),
 'circuittracks-nor-defect-closure-development.bin':(413952,'edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9'),
 'circuittracks-B1.3-manifest-matched.syx':(598489,'6f07376b5983a5e0350d4883ae9ed57a69bc735320afde9f43ca75017b8e8736'),
 'circuittracks-firmware-4486-STOCK.syx':(432961,'bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd'),
 'live_host.py':(None,'9b8a7d3d088cdffe21257824cb16db602659d678d240e7266f468e92c3ae9dc9'),
 'ct_uploader-final-offline-locked.html':(None,'bf1ef00dbca9c3715932235249fcc8ba0a71d6f2f989c047aa8caf66b85e17a5')}
identities=[]
for name,(size,digest) in expected.items():
    f=P/name
    assert sha(f)==digest,name
    assert size is None or f.stat().st_size==size,name
    identities.append(dict(file=name,bytes=f.stat().st_size,sha256=digest))
central=(R/'docs/CURRENT_STATUS.md').read_text(encoding='utf-8')
for size,digest in expected.values():assert digest in central,digest
identity=json.loads((R/'builds/phase63-defect-closure/development-identity.json').read_text())
assert identity['CRC']=='1BB21302' and identity['CRC'] in central
assert json.loads((P/'operational-gate.json').read_text())['live_enabled'] is False
assert re.search(r'PREFLIGHT_QUALIFIED\s*=\s*false', (P/'ct_uploader-final-offline-locked.html').read_text(encoding='utf-8'))
assert sha(P/'recovery-status.txt')=='169f295e37fc8b39d51ec5e38a54d2d341d52cd7b2bca7b8d762ff6ff019008d'
# Preserve names/order/comment formatting; change only digests of updated docs.
m=P/'HASHES.txt';raw=m.read_bytes()
for line in raw.decode('utf-8').splitlines():
    if not line or line.startswith('#'):continue
    digest,name=line.split('  ',1)
    f=(P/name).resolve();assert f.is_relative_to(P.resolve())
    actual=sha(f)
    if actual!=digest:
        assert name in package_allowed,name
        raw=raw.replace((digest+'  '+name).encode(),(actual+'  '+name).encode())
m.write_bytes(raw)
count=0
for line in m.read_text().splitlines():
    if not line or line.startswith('#'):continue
    digest,name=line.split('  ',1);assert sha(P/name)==digest,name;count+=1
assert count==633
changed_package=[]
for name,digest in before.items():
    if sha(R/name)!=digest:
        name=Path(name).as_posix()
        assert name.startswith('builds/final-hardware-test-package/')
        assert Path(name).name in package_allowed,name
        changed_package.append(name)
assert set(changed_package)=={'builds/final-hardware-test-package/'+n for n in package_allowed}

# Build current human audit, retaining the old identity table as historical only.
old=(O/'before/docs/FINAL_DOCUMENTATION_AUDIT.md').read_text()
hist=[line for line in old.splitlines() if line.startswith('| phase')]
updated=[name for name,digest in docs_before.items() if (R/name).is_file() and sha(R/name)!=digest]
if 'docs/FINAL_DOCUMENTATION_AUDIT.md' not in updated:updated.append('docs/FINAL_DOCUMENTATION_AUDIT.md')
report=f'''# Final documentation audit — final pre-hardware review

**OPERATIONAL PREFLIGHT = UNQUALIFIED. POST-READY ALLOCATION CENSUS = UNQUALIFIED. USB STORAGE JOINT PATH = PASS.**

17 October 2026 (Europe/Moscow). Documentation/state cleanup only: no reverse engineering, experimental runner, firmware build, host/uploader execution, hardware access, MIDI access or transmission. No live lock was changed. Candidate firmware is a temporary NOR diagnostic, not Plaits; it has not been hardware-tested. Phase67 FINAL PREFLIGHT CLOSURE = PASS remains scoped model evidence.

## Files updated

'''+ '\n'.join('- '+link(n) for n in sorted(updated))+f'''

Documentation-only helpers: {link('tools/update_final_state_docs.py')} and {link('tools/audit_final_state_docs.py')}. Evidence/state receipts are under {link('builds/final-pre-hardware-documentation')}; preserved before-copies are explicitly historical / SUPERSEDED, not a second current state. Historical note bodies and the original cheap-check audit body are retained beneath current/supersession notices. The old readiness note's legacy byte encoding is preserved with its historical body.

## Files left unchanged

Exact candidate SYX/BIN in both Phase63 and package, both rollback SYXs, live_host.py, uploader HTML, transport/codecs, operational-gate.json, recovery-status.txt and all other package content except README.txt, final-cheap-checks.md, HARDWARE_TEST_PREFLIGHT.txt and their HASHES.txt digests. All other historical phase evidence, runners, reference/pinned sources, firmware and Plaits PoCs remain unchanged by this task. No evidence was deleted. The earlier circuit-tracks-plaits-re source snapshot remains historical; its README/status/roadmap are not current release authority.

## Stale references found and contradictions resolved

- Root landing page and current overview/review/index/audit pages previously led with Phase67 PASS as current authority and hardware/model-only risk. They now retain that scoped result while naming the later allocation SOFTWARE UNKNOWN and operational UNQUALIFIED.
- HANDOFF/CURRENT_STATUS/NEXT_STEPS previously carried two competing status layers and listed both cheap-check gaps unresolved. They now record USB joint-path PASS (36 cases), with only the allocation proof open.
- Review prompts treated independent review as pending. The user-reported favorable Claude conclusion and accepted soft-brick/recovery risk are recorded; a separately reviewed operational release is next. No external review or message was initiated.
- Recovery entry/exit is now expressly user-reported physical evidence with no rehearsal transmission. Enumeration, handshake, both recovery flashes and non-booting-candidate recovery remain unproven; recovery is not guaranteed.
- Frozen package README/checklist and original cheap-check decision were stale. Current notices/checklist/README are corrected; the original audit remains historical. Package HASHES.txt was updated for documentation only.
- Memory/Plaits pages retain numerical/design evidence but no longer imply diagnostic PASS qualifies final resources. Authentic82000 is missing; P0282-0386 and final P/X/Y remain unqualified/UNKNOWN.
- Old hashes were searched across repository documentation. Preserved phase reports/source snapshots are historical evidence, not eligible candidates; current-page occurrences appear only in the historical table below. Machine inventory: stale-references.json. No historical evidence was rewritten to erase a prior result.

## HISTORICAL / FAILED / SUPERSEDED identities — DO NOT FLASH

All entries below are historical / SUPERSEDED, not current candidates. Phase61 and original Phase62 specifically FAILED later qualification. Keeping their hashes prevents accidental substitution.

| Historical evidence directory | Superseded artifact | Historical SHA-256 |
|---|---|---|
'''+ '\n'.join(hist)+f'''

## Current candidate identity

Phase63 N63DEV: SYX 569229 bytes, SHA-256 `9b420521a366c65c13fb871778fdbab612ca126cbb4ad60d0fd5bc12ecd253da`; BIN 413952 bytes, SHA-256 `edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9`. CRC-32/MPEG-2 `1BB21302`; application `0x08010000..0x08075100` end-exclusive. CRC is referenced from saved identity evidence, not a newly run decoder/build. Full rollback/tool identities: {link('docs/CURRENT_STATUS.md')}.

## Current preflight status and next step

No concrete offline firmware blocker demonstrated. Accepted residual SOFTWARE uncertainty: unresolved post-READY indirect/virtual allocation reachability, especially 0803C91C/0803C9C4 and registry/object methods, with 8 bytes modeled gap. No actual >8-byte post-READY allocation found; absence NOT proven. Allocator rejection reaches BKPT; artificially continuing returns FFFFFFFF accepted by generic wrapper; physical routing UNKNOWN. USB joint path PASS is preserved within its 36-case declared scope, not physical proof.

Reported independent review: REASONABLE TO PROCEED WITH CONTROLLED HARDWARE TEST, subject to accepted residual risk. User accepts possible soft brick requiring recovery provided bootloader remains accessible; this does not guarantee recovery, close the census or authorize hardware. Next: separately reviewed operational-release preparation/new tool hashes, actual-machine hash verification and Windows/MSD policy, then an explicitly authorized controlled test. Geometry first, host validation of82000 safety, exact epoch/session authorization, one fixed capture, restore B1.3 on success. H4 remains FAILED (H4 = FAIL): discard/no retry/no second diagnostic or Storage request/full physical power OFF/USB unplugged/end session.

## Verification and Git hygiene

Read-only artifact hashing confirms candidate/rollback/tool identities and all 633 package manifest entries. Only four package documentation/manifest files changed; recovery-status.txt retains SHA-256 `169f295e37fc8b39d51ec5e38a54d2d341d52cd7b2bca7b8d762ff6ff019008d`. No old test suite was rerun. The machine audit records internal links, status assertions, stale hash inventory, exact preserved hashes and changed files in {link('builds/final-pre-hardware-documentation/audit.json')}.

Earlier saved hash receipts describe their own packaging snapshots; the updated package HASHES.txt controls current documentation bytes. Candidate/tool/rollback identities and the saved experiment results were not changed by documentation supersession.

[[VERIFICATION_RESULTS]]

Neither the project root nor the earlier source snapshot contains Git metadata in this working copy. No staging/commit/push occurred and no history was rewritten. Existing snapshot .gitignore already excludes Python caches, editor artifacts and generated builds/binaries; it was left unchanged. No root .gitignore was added without a Git checkout. Do not stage historical/proprietary artifacts or documentation-before copies indiscriminately when preparing a future commit. Documentation helpers ran with Python -B.

## Proposed commit — not executed

`docs: update project state through final pre-hardware review`

- document Phase63 identity and Phase61/62 supersession;
- record actual defect closures and Phase64-67 scoped modeling;
- record final USB joint-path PASS and unresolved allocation proof;
- reconcile rollback/recovery/locked-tool status and accepted soft-brick risk;
- clarify separately reviewed release preparation and future controlled-test sequence.

REPOSITORY STATE = CURRENT THROUGH FINAL PRE-HARDWARE REVIEW
'''
(R/'docs/FINAL_DOCUMENTATION_AUDIT.md').write_text(report,encoding='utf-8')
current=[R/'README.md']+sorted((R/'docs').glob('*.md'))
if not (O/'audit.json').exists():
    (O/'audit.json').write_text('{"status":"pending documentation checks"}\n')
link_rows=[];broken=[]
inputs=[(f,f.read_text(encoding='utf-8')) for f in current]
for name,marker in [('notes/qspi82000-hardware-readiness.md','## Historical Phase28'),('notes/fixed-nor-evidence-diagnostic.md','# Fixed NOR evidence diagnostic'),('builds/final-hardware-test-package/final-cheap-checks.md','## Historical original cheap-check audit')]:
    f=R/name;text=f.read_bytes().decode('utf-8',errors='surrogateescape').split(marker,1)[0]
    inputs.append((f,text))
for f,text in inputs:
    for match in re.finditer(r'\[[^\]]*\]\((<[^>]+>|[^\s)]+)(?:\s+"[^"]*")?\)',text):
        target=match.group(1).strip('<>')
        if re.match(r'^(https?://|mailto:|app:|codex:|#)',target):continue
        target=unquote(target.split('#',1)[0])
        dest=Path(target) if re.match(r'^[A-Za-z]:[/\\]',target) else f.parent/target
        good=dest.exists();row=dict(file=str(f.relative_to(R)),line=text.count('\n',0,match.start())+1,target=target,exists=good)
        link_rows.append(row)
        if not good:broken.append(row)
    if f in current:
        assert 'OPERATIONAL PREFLIGHT = UNQUALIFIED' in text,f
        assert 'POST-READY ALLOCATION CENSUS = UNQUALIFIED' in text,f
        assert 'USB STORAGE JOINT PATH = PASS' in text,f
        assert not re.search(r'\bSAFE TO FLASH\b',text,re.I),f
# Search all local first-party documentation, including immutable historical
# evidence; classify history rather than mutating old reports or embedded hashes.
old_hashes={'phase61_FAILED_SUPERSEDED':'fe36e18bc83448b0e25cc21b8323e0e64e153f6e04abc042546f4a20e83731d3','phase43_SUPERSEDED':'59be0e5733c70783c278ff5f89e575d77eef4dd3f6389841eac4a488111df32b'}
stale=[]
inventory=subprocess.run(['rg','--files','--hidden','-g','*.md','-g','*.txt','-g','!**/vendor/**','-g','!**/upstream/**','-g','!**/.git/**','-g','!**/__pycache__/**'],cwd=R,capture_output=True,text=True,check=True)
for filename in inventory.stdout.splitlines():
    f=R/filename
    if not f.is_file() or f.suffix.lower() not in ('.md','.txt'):continue
    rel=f.relative_to(R)
    if any(x in rel.parts for x in ('vendor','upstream','.git','__pycache__')):continue
    if f.stat().st_size>5_000_000:continue
    text=f.read_bytes().decode('utf-8',errors='replace')
    for number,line in enumerate(text.splitlines(),1):
        for kind,digest in old_hashes.items():
            if digest not in line:continue
            category='historical evidence/source snapshot'
            if f in current:
                assert f.name=='FINAL_DOCUMENTATION_AUDIT.md',(str(rel),number)
                assert '## HISTORICAL / FAILED / SUPERSEDED' in text
                category='explicit historical/superseded identity table'
            stale.append(dict(file=str(rel),line=number,identity=kind,classification=category,text=line))
result=dict(date='2026-10-17',timezone='Europe/Moscow',documentation_only=True,
    current_pages=len(current),additional_current_notices=3,local_links_checked=len(link_rows),broken_links=broken,
    status_language_consistent=True,stale_hash_occurrences=len(stale),
    stale_current_eligible_candidates=0,package_files_verified=count,package_total_files=sum(f.is_file() for f in P.rglob('*')),
    changed_package_files=changed_package,identities=identities,
    candidate_tool_rollback_bytes_unchanged=True,recovery_sha256=sha(P/'recovery-status.txt'),
    live_enabled=False,PREFLIGHT_QUALIFIED=False,allocation_census='UNQUALIFIED',USB_joint_path='PASS',operational_preflight='UNQUALIFIED',
    no_git_metadata=True,gitignore_changed=False,staged=False,committed=False,pushed=False,
    experiments_run=False,hardware_access=False,MIDI_access=False,transmission=False)
(O/'local-links.json').write_text(json.dumps(link_rows,indent=2)+'\n')
(O/'stale-references.json').write_text(json.dumps(stale,indent=2)+'\n')
(O/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
assert not broken,broken
auditfile=R/'docs/FINAL_DOCUMENTATION_AUDIT.md'
text=auditfile.read_text(encoding='utf-8').replace('[[VERIFICATION_RESULTS]]',f'Verification results: **{len(link_rows)} local link occurrences, zero broken**, across {len(current)} current pages and 3 current notices; **{count} package manifest entries verified**; {len(stale)} old-hash occurrences classified as historical, zero current eligible historical candidates. Current status-language assertions and exact candidate/rollback/tool reference checks pass. These are documentation/hash checks, not new firmware or hardware experiments.')
auditfile.write_text(text,encoding='utf-8')
updated=sorted(name for name,digest in docs_before.items() if sha(R/name)!=digest)
(O/'updated-files.json').write_text(json.dumps(updated,indent=2)+'\n')
receipts=[p for p in O.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt']
(O/'SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.relative_to(O).as_posix()}\n' for p in sorted(receipts)))
print(json.dumps(result,indent=2))
