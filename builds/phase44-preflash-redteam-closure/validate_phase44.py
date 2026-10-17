"""Read/hash/consistency validation only; no emulator or live transport import."""
from pathlib import Path
import hashlib,json,re,ast
O=Path(__file__).resolve().parent;R=O.parents[1]
S=R/'builds/phase43-hardware-test-candidate';P=R/'builds/phase42-exact-rdiag-integration'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
 checked=[]
 for base in (P,S):
  v=load(base/'validation.json')
  for name,h in v['evidence_sha256'].items():
   p=base/name;assert digest(p)==h,(p,'original evidence changed');checked.append(str(p))
  for name,h in v.get('notes_sha256',{}).items():
   p=Path(name);assert digest(p)==h,p;checked.append(str(p))
 v=load(S/'validation.json');assert digest(S/'SHA256SUMS.txt')==v['SHA256SUMS_sha256']
 sources=load(P/'inputs.json')['sources']
 for row in sources:
  for path in (Path(row['path']),Path(row['local']),S/'source'/Path(row['local']).relative_to(P/'source')):
   assert digest(path)==row['sha256'],path;checked.append(str(path))
 identity=load(O/'atomic-candidate-identity.json')
 for suffix,size,key in (('bin',375948,'BIN_sha256'),('syx',517001,'SYX_sha256')):
  p=O/('circuittracks-4486-nor-evidence-atomic-test.'+suffix)
  assert p.stat().st_size==size and digest(p)==identity[key]
 original=(S/'circuittracks-4486-nor-evidence-test.bin').read_bytes()
 corrected=(O/'circuittracks-4486-nor-evidence-atomic-test.bin').read_bytes()
 diff=[i for i,(a,b) in enumerate(zip(original,corrected)) if a!=b]
 assert len(diff)==39 and len(original)==len(corrected)
 assert all(0x1e8<=i<0x1ee or 0x5b9dc<=i<0x5b9e0 or 0x5bc30<=i<0x5bc50 for i in diff)
 assert corrected[0x1e8:0x1ee]==b'N44ATM'
 assert corrected[0x1f0:0x855a]==original[0x1f0:0x855a]
 transitions=[]
 for prefix in ('','atomic-'):
  for name in ('b13-to-candidate','candidate-to-official','candidate-to-b13'):
   d=load(O/(prefix+name+'-summary.json'))
   assert d['accepted'] and d['actual_install_performed'] and not d['silent_noop']
   assert d['staged_image_sha256']==d['final_installed_sha256']==d['incoming_image_sha256']
   assert all(p['writes']==0 and p['erase_overlaps']==0 and p['sentinel_unchanged'] for p in d['preservation'].values())
   transitions.append(prefix+name)
 supplement=load(O/'atomic-supplement.json')
 assert supplement['SYX_sha256']==identity['SYX_sha256'] and supplement['final_installed_sha256']==identity['BIN_sha256']
 assert supplement['native_USB_to_revised_host']['status']=='SUCCESS' and supplement['requests']==1
 assert load(O/'success-atomicity.json')['quarantine_overwrite_reproduced']
 assert load(O/'header-noop-control.json')['changed_code_equal_header']['silent_noop']
 assert load(O/'native-results.json')['case_count']==25
 assert load(O/'host-presend-tests.json')['case_count']==17
 assert load(O/'capture-tool-tests.json')['case_count']==25
 assert len(load(O/'recovery-results.json')['matrix'])==10
 assert not (O/'NOR-CAPTURE-ATTEMPT.json').exists() and not (S/'NOR-CAPTURE-ATTEMPT.json').exists()
 missing=[];links=0
 for p in [*O.glob('*.md'),R/'README.md',*list((R/'docs').glob('*.md'))]:
  s=p.read_text(encoding='utf-8')
  for target in re.findall(r'\]\(<([^>]+)>\)',s):
   links+=1
   if not Path(target).exists():missing.append([str(p),target])
 assert not missing,missing
 for p in O.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
 evidence={p.name:digest(p) for p in sorted(O.iterdir()) if p.is_file() and p.name not in ('validation.json','SHA256SUMS.txt')}
 result=dict(confidence='PROVEN',verdict='UNQUALIFIED',scope='Phase44 completed selected native/offline tests; global normal boot/persistent-writer exclusion remains UNKNOWN',
  candidate=identity,original_phase42_phase43_evidence_and_source_checks=len(checked),unique_preserved_inputs=len(set(checked)),
  original_artifacts_unchanged=True,reference_source_files_checked=len(sources),all_six_transitions=transitions,
  atomicity_original_failure_preserved=True,corrected_native_cases=25,host_inherited_cases=25,host_added_cases=17,
  recovery_metadata_cases=10,original_recovery_full_streams=2,corrected_recovery_full_streams=1,
  opcode_port_cases=512,doc_links_checked=links,missing_links=missing,
  offline_blocker='Normal boot/background/persistent NOR mutation-producer address and predicate closure, especially selector2 and chip erase',
  H4='FAIL: no in-session unwind after NOR failure',hardware_access=False,MIDI_ports_opened=0,live_port_inventory=False,firmware_transmitted=False,
  candidate_regeneration_reason='Original exact native boundary test proved quarantine overwritten by SUCCESS; corrected separate artifact only',evidence_sha256=evidence)
 (O/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 sums=evidence|{'validation.json':digest(O/'validation.json')}
 (O/'SHA256SUMS.txt').write_text(''.join(h+'  '+n+'\n' for n,h in sorted(sums.items())),encoding='utf-8')
 print(json.dumps({k:v for k,v in result.items() if k not in ('evidence_sha256','candidate')},indent=2))
if __name__=='__main__':main()
