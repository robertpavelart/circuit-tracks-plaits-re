"""Static producer/caller/latch checks only; no CPU, positive seed or records."""
import argparse,csv,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from ct_stock_load_audit import verify_inputs,rows

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def obj(p):return json.loads(p.read_text(encoding='utf8'))
def csvrows(p):
 with p.open(encoding='utf8',newline='') as f:return list(csv.DictReader(f))

def verify(first,repeat,out):
 out=out.resolve();base=(ROOT/'builds/phase19c-p204b').resolve()
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh P204B checks child required')
 files={p.name for p in first.iterdir() if p.is_file()}
 assert files=={p.name for p in repeat.iterdir() if p.is_file()}
 for n in files:assert (first/n).read_bytes()==(repeat/n).read_bytes(),n
 for n,h in obj(first/'hashes.json').items():assert sha(first/n)==h,n
 for n,h in obj(first/'inputs.json').items():assert sha(ROOT/n)==h,n
 payload,protected=verify_inputs();dsp=rows(ROOT/'builds/phase3-selection0-channel0.asm',payload)
 # Independently walk literal N0/N1/R1 at the actual caller sites. Register
 # values are compiler-source state, never inserted into an emulator/memory.
 state={};callers={}
 for pc,r in sorted(dsp.items()):
  if not 0x1a70<=pc<0x1ad0:continue
  for m in re.finditer(r'move #\$([0-9a-f]+),(r1|n0|n1)\b',r['text']):state[m[2]]=int(m[1],16)
  if r['text']=='jsr $1b7b':callers[hex(pc)]=state.copy()
 domain=obj(first/'smoothing-domains.json');assert len(domain)==20 and len(callers)==9
 for d in domain:
  if d['bank'] is not None:
   s=callers[d['caller']]
   expected=[s['r1']+0x172*d['bank']+s['n1']*i for i in range(s['n0'])]
   assert d['addresses']==expected
  else:
   expected=[int(dsp[p]['text'].split('#$')[1].split(',')[0],16)
    for p in ([0x1a70] if d['caller']=='0x1a77' else [0x1a89])][0]
   assert d['base']==expected and d['stride']==5 and d['count']==20
   assert d['addresses']==[expected+5*i for i in range(20)]
  assert all(a!=0x35f and not 0x360<=a<0x3c4 for a in d['addresses'])
 source=obj(first/'source-table-separation.json')
 for bank,a in enumerate(source['source_addresses']):
  assert len(a)==80 and len(set(a))==80
  assert all(not 0x35f<=v<0x3c4 for v in a)
  assert sorted(a)==[0x2fb+0x172*bank+5*i+j for i in range(20) for j in [0,1,2,4]]
 assert source['last_bank0_source_word']==0x35e and not source['positive_count20_is_compiled']
 schema=obj(first/'record-schema.json')
 assert schema['base']==0x360 and schema['stride']==5 and len(schema['fields'])==5
 assert [f['offset'] for f in schema['fields']]==list(range(5))
 assert [f['register'] for f in schema['fields']]==['R5','R6','R7','X0','R4']
 assert schema['normal_positive_min'] is schema['normal_positive_max'] is None
 assert schema['capacity_status'].startswith('HYPOTHESIS') and schema['architectural_LC_bits']==24
 # Direct original instruction evidence establishes count read once before DO;
 # body mutates X1, but neither reloads X35F nor assigns LC or postupdates R4.
 assert dsp[0x203a]['text']=='move x:(r0)+,x1' and dsp[0x2040]['text']=='do x1,$204c'
 assert dsp[0x2045]['text']=='move a,x1 y:(r7),y0'
 body=[dsp[p]['text'] for p in sorted(dsp) if 0x2042<=p<=0x204b]
 assert len(body)==10 and body[-1]=='move b,x:(r4)'
 assert sum(',x:(r4)' in t for t in body)==1
 assert all('lc' not in t and '$035f' not in t and '(r4)+' not in t for t in body)
 latch=obj(first/'count-latching.json');assert not latch['all_async_exclusion']
 readers=csvrows(first/'scalar-read-count-preimages.csv')
 assert len(readers)==19 and all(x['normal_positive_witness']=='False' for x in readers)
 fixed=[x for x in readers if x['encoded_read']]
 assert len(fixed)==6 and all(int(x['encoded_read'])!=0x35d for x in fixed)
 assert next(x for x in readers if x['site']=='0x8026ad4')['count_preimage'].startswith('SERVICE-ONLY')
 assert next(x for x in readers if x['site']=='0x8049ba8')['count_preimage'].startswith('FROZEN')
 aliases=obj(first/'count-alias-preconditions.json')
 assert aliases['status'].startswith('VERIFIED necessary') and 'r=35D' in aliases['host19D']['scalar_read_preimage']
 # Reviewed IRQ bodies never directly assignX1/LC; their indirect memory writes
 # remain explicitly open. This is no proof against every interrupt source.
 for lo,hi in [(0x156,0x1b4),(0x1b4,0x1d9)]:
  for p,r in dsp.items():
   if lo<=p<hi:assert not re.search(r',(?:x1|lc)(?:\s|$)',r['text']),r
 collision=csvrows(first/'collision-results.csv');assert len(collision)==46
 for c in collision:
  if c['state']=='All normal Selection0':
   assert c['result']=='NOT-YET-DETERMINED' and c['exact_reachable_addresses']=='UNKNOWN'
  else:assert c['result']=='VERIFIED NO' and c['exact_reachable_addresses']=='[]'
 result=obj(first/'result.json')
 assert result['result_class']=='D' and result['normal_destination_set'] is None
 assert not result['positive_checkpoint_admitted'] and result['CPU_instructions_executed']==0
 assert not result['P204B_removed_as_blocker'] and not result['parent_replay_admitted']
 assert not result['asset_branch_reopened'] and not result['persistent_256_word_reservation']
 zero=obj(first/'zero-path-preserved.json')
 assert zero['entries']==obj(ROOT/'builds/phase19c-checkpoint/final/x35f-entries.json')
 assert all(x['value']==0 for x in zero['entries']) and zero['new_CPU_instructions']==0
 # Complete immutable prior evidence guards, with no prior replay invocation.
 prior_files=0
 for folder in ['builds/phase19c-checkpoint/final','builds/phase19c-fullhelper/final',
                'builds/phase19c-packlink/final-v2']:
  for n,h in obj(ROOT/folder/'hashes.json').items():assert sha(ROOT/folder/n)==h,n;prior_files+=1
 for n,h in obj(ROOT/'builds/phase19c-fullhelper/final/source-manifest.json').items():assert sha(ROOT/n)==h,n
 import ct_fw_tool
 syx=ROOT/'original/circuittracks-firmware-4486.syx';b=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
 assert ct_fw_tool.decode_syx(syx)['firmware']==b and ct_fw_tool.build_syx(syx,b)==syx.read_bytes()
 for x in obj(ROOT/'firmware/dsp/build-4486/manifest.json')['blocks']:
  for k in ['stream','payload']:assert sha(ROOT/'firmware/dsp/build-4486'/x[k+'_file'])==x[k+'_sha256']
 refused=[]
 for script,args in [('tools/ct_p204b_provenance.py',['--output-dir',str(first)]),
  ('emulator/tests/verify_p204b.py',['--first',str(first),'--repeat',str(repeat),'--output-dir',str(first)])]:
  r=subprocess.run([sys.executable,'-B',str(ROOT/script),*args],capture_output=True,text=True)
  assert r.returncode and 'Fresh P204B' in r.stderr,(script,r.stderr)
  refused.append(script)
 for n in files:assert (first/n).read_bytes()==(repeat/n).read_bytes(),n
 out.mkdir(parents=True)
 subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/audit_paths.py'),
  '--results',str(ROOT/'builds/phase19a/validated/results.json'),'--output',str(out/'unchanged-core-audit.json')],
  capture_output=True,check=True)
 report=dict(status='PASS',repeat_identical_files=len(files),source_SHA256=sha(Path(__file__)),
  bounded_smoothing_domains=20,recovered_wrapper_callers=9,
  source_table_nominal_writes=160,record_fields=5,collision_scope_checks=46,
  existing_scalar_read_edges_reused=19,fixed_read_count_preimages_excluded=6,
  zero_path_entries_preserved=2,prior_canonical_files_guarded=prior_files,
  overwrite_refusals=refused,original_firmware_roundtrip_all10_extracts_core_helper='PASS',
  CPU_instructions_executed=0,positive_count_seeded=False,destination_records_fabricated=False,
  asset_analysis_performed=False,result_class='D')
 with (out/'reproducibility.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps(report,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['first','repeat','output-dir']:p.add_argument('--'+n,required=True,type=Path)
 a=p.parse_args();verify(a.first,a.repeat,a.output_dir)
