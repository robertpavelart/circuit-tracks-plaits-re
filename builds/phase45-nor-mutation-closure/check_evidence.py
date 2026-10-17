"""Phase45 evidence integrity/link check, not gated final-candidate admission.

No emulator, builder, MIDI, WinMM or live API import. Completed tests are not
rerun. All interrupted-checkpoint files and original candidate evidence remain.
"""
from pathlib import Path
import ast,hashlib,json,re
O=Path(__file__).resolve().parent;R=O.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
 before=load(O/'resume-checkpoint.json')['files']
 for n,h in before.items():assert sha(O/n)==h,('interrupted evidence changed',n)
 previous=R/'builds/phase44-preflash-redteam-closure';protected=0
 for base in (R/'builds/phase43-hardware-test-candidate',previous):
  record=load(base/'validation.json')
  for n,h in record['evidence_sha256'].items():
   assert sha(base/n)==h,('previous evidence changed',base/n);protected+=1
 sources=load(R/'builds/phase42-exact-rdiag-integration/inputs.json')['sources']
 for row in sources:assert sha(Path(row['path']))==row['sha256'],row['path']
 atomic=load(O/'independent-atomicity-review.json')
 assert len(atomic['changed_bytes'])==39 and atomic['corrected_cases']==104
 assert not atomic['patch_emitter_imported'] and not atomic['hardware_access']
 assert all(c['final_state']==3 for c in atomic['cases'] if c['initial_state']==3)
 assert any(c['irq_observed_state']==3 and c['final_state']==2 for c in atomic['original_race_cases'])
 updates=load(O/'update-dependency-review.json')
 assert len(updates['transitions'])==3 and updates['all_requested_transition_headers_differ']
 for t in updates['transitions']:
  assert not t['prior_array_byte_dependencies']
  source=previous/('atomic-'+t['transition']+'-operations.json')
  assert sha(source)==t['trace_sha256'],source
 msd=load(O/'msd-writer-review.json');mapped=load(O/'mapped-write-review.json')
 assert len(msd['cases'])==8 and len(mapped['cases'])==5
 assert msd['default_mode']==1 and msd['callback_pointers']['0x8057ef5']==['0x2000379c']
 assert any(x.get('coeff_overlap') for c in msd['cases'] for x in c['operations'])
 assert mapped['cases'][-1]['operation']['coefficient_overlap']
 required=['findings.md','nor-mutation-callgraph.md','boot-to-idle-mutation-closure.md',
  'background-write-analysis.md','target-preservation.md','atomicity-patch-review.md',
  'update-noop-review.md','final-candidate-validation.md','heap-stack-status.md']
 for n in required:assert (O/n).stat().st_size>0,n
 assert (O/'findings.md').read_text(encoding='utf-8').rstrip().endswith('PREFLASH OFFLINE CLOSURE = UNQUALIFIED')
 for p in O.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
 links=0
 for p in [*O.glob('*.md'),*list((R/'docs').glob('*.md')),R/'README.md']:
  for target in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf-8')):
   assert Path(target).exists(),(p,target);links+=1
 assert not list(O.glob('*.syx')) and not list(O.glob('*.bin'))
 result=dict(confidence='PROVEN',scope='Saved-evidence consistency; NOT final candidate admission',
  overall_verdict='UNQUALIFIED',checkpoint_files_preserved=len(before),previous_evidence_files_verified=protected,
  reference_source_files_verified=len(sources),reports=required,local_links_verified=links,
  reused_atomicity_combinations=104,reused_terminal_admission_cases=6,reused_update_transitions=3,
  new_MSD_cases=8,new_mapper_cases=5,
  full_candidate_validation_gate='NOT ADMITTED: required prior mutation closure unresolved',final_candidate_designated=False,
  exact_remaining_obligations=['MSD57EF4 root/mode invariant through24918/248B4/38C54, SCSI/window and physical-address bounds',
   'Filesystem logical-block/count/object-binding bounds upstream of1AF1E across restore/save/flush',
   'Complete remaining computed callback/queue/controller-client root closure'],
  hardware_evidence='User reports physical recovery entry and normal B1.3 return only; rollback flashing not reported tested',
  hardware_access=False,MIDI_ports_opened=0,firmware_transmitted=False,firmware_generated=False)
 (O/'evidence-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 files={p.name:sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'}
 (O/'SHA256SUMS.txt').write_text(''.join(h+'  '+n+'\n' for n,h in sorted(files.items())),encoding='utf-8')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
