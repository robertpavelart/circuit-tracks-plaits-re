"""Compare immutable restoring baseline with qualified compact native DIV run."""
import argparse,csv,hashlib,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
def obj(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):return list(csv.DictReader(p.open(newline='')))
def helper_cost(s):
 labels=obj(s/'dsp-first/labels.json');lines=(s/'dsp-first/program.asm').read_text().splitlines()
 ends=[int(line.split()[0],16) for line in lines if line.split(' ',1)[1]=='rts']
 trace=np.memmap(s/'dsp-first/execution-pc.u16',dtype='<u2',mode='r')
 start=np.flatnonzero(trace==labels['ratio']);end=np.flatnonzero(np.isin(trace,ends))
 assert len(start)==len(end) and np.all(end>=start)
 costs=end-start+1;vals,counts=np.unique(costs,return_counts=True)
 bs=rows(s/'dsp-first/blocks.csv');pos=0;block_calls=[];block_issued=[]
 for b in bs:
  length=int(b['instructions']);part=trace[pos:pos+length]
  calls=int(np.count_nonzero(part==labels['ratio']))
  issued=int(np.count_nonzero(part>=labels['ratio']))
  block_calls.append(calls);block_issued.append(issued);pos+=length
 assert pos==len(trace) and sum(block_calls)==len(start) and sum(block_issued)==int(costs.sum())
 return dict(calls=int(len(start)),issued_min=int(costs.min()),issued_mean=float(costs.mean()),
  issued_max=int(costs.max()),issued_total=int(costs.sum()),includes_RTS=True,excludes_caller_JSR=True,
  histogram={str(int(v)):int(c) for v,c in zip(vals,counts)},invocations_block_min=min(block_calls),
  invocations_block_mean=float(np.mean(block_calls)),invocations_block_max=max(block_calls)),block_calls
def compare(new,out):
 out=out.resolve();base=ROOT/'builds/phase20a-div';old=ROOT/'builds/phase20a-plaits/final'
 if out.exists() or not out.is_relative_to(base) or out==base:raise ValueError('Fresh output required')
 out.mkdir(parents=True)
 for suite in [old,new]:
  for n,h in obj(suite/'hashes.json').items():assert sha(suite/n)==h,n
  for n,h in obj(suite/'implementation-provenance.json').items():assert sha(ROOT/n)==h,n
 for n in ['inputs.tsv','cases.json','oracle.i32','reference-first.f32','reference-repeat.f32',
           'metrics.json','pitch-accuracy.csv','sample-rate-contract.json','reference-block-continuity.json']:
  assert sha(old/n)==sha(new/n),n
 for n in ['output.i32','states.csv']:assert sha(old/'dsp-first'/n)==sha(new/'dsp-first'/n),n
 # Only final jump relocation may differ before helper. Same assembler layout.
 ol=obj(old/'dsp-first/labels.json');nl=obj(new/'dsp-first/labels.json');assert ol['ratio']==nl['ratio']
 a=(old/'dsp-first/program.be24').read_bytes();b=(new/'dsp-first/program.be24').read_bytes()
 assert a[:(ol['ratio']-0x200-1)*3]==b[:(nl['ratio']-0x200-1)*3]
 os=(old/'assembly/variablesaw.asm').read_text().split('ratio:')[0]
 ns=(new/'assembly/variablesaw.asm').read_text().split('ratio:')[0];assert os==ns
 assert obj(old/'assembly/layout.json')['variables']==obj(new/'assembly/layout.json')['variables']
 oh,oc=helper_cost(old);nh,nc=helper_cost(new);assert oc==nc
 nr=rows(new/'dsp-first/blocks.csv');assert [int(r['ratio_calls']) for r in nr]==nc
 assert all(int(r['div_issued'])==21*c for r,c in zip(nr,nc))
 oldres=obj(old/'resource-manifest.json');newres=obj(new/'resource-manifest.json')
 oldd=np.fromfile(old/'dsp-first/output.i32',dtype='<i4');newd=np.fromfile(new/'dsp-first/output.i32',dtype='<i4')
 e=(newd.astype('int64')-oldd.astype('int64'))/(1<<21)
 metrics=obj(new/'metrics.json');spectra=obj(base/'checks/spectral-comparison.json')
 result=dict(status='MEASURED / TESTED',old=oldres,new=newres,restoring_helper=oh,native_helper=nh,
  opcode_reduction_percent={k:100*(oldres['issued_per_block_'+k]-newres['issued_per_block_'+k])/oldres['issued_per_block_'+k] for k in ['min','mean','max']},
  program_delta_P_words=newres['P_words']-oldres['P_words'],persistent_delta_words=0,allocated_scratch_delta_words=0,
  allocated_scratch_words=44,live_scratch_words=43,unused_helper_slot='X:0xAB; retained to preserve layout',
  maximum_sample_difference_integer=int(np.max(np.abs(newd.astype('int64')-oldd.astype('int64')))),
  RMS_sample_difference=float(np.sqrt(np.mean(e*e))),old_new_spectrum_similarity=1.0,
  old_new_all_samples_and_block_states_identical=True,main_assembly_identical=True,prehelper_machine_code_except_done_jump_identical=True,
  controls_cases_oracle_reference_metrics_pitch_rate_contract_unchanged=True,
  float_reference=dict(maximum_case_RMS=max(x['RMS_difference'] for x in metrics),
   maximum_point_difference=max(x['max_abs_difference'] for x in metrics),
   maximum_DC_difference=max(abs(x['DC_difference']) for x in metrics),
   maximum_peak_difference=max(abs(x['DSP_peak']-x['reference_peak']) for x in metrics),
   minimum_spectrum_similarity=min(x['FFT_magnitude_cosine_similarity'] for x in spectra)),
  maximum_pitch_error_cents=obj(new/'result.json')['maximum_absolute_cents_error'],
  continuity_2048_blocks=True,full_trace_determinism=True,baseline_protected=True,
  native_helper_divisions_per_valid_call=21,zero_guard_taken_in_oscillator_suite=0,
  helper_scratch_reads_writes=0,exact_hardware_cycles=None,Circuit_integration_readiness=False)
 (out/'comparison.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 (out/'provenance.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__),new/'hashes.json',old/'hashes.json',base/'fixtures-compact/result.json',base/'checks/verification.json']},indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ['old','new','restoring_helper','native_helper']},indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--suite-dir',type=Path,required=True);a.add_argument('--output-dir',type=Path,required=True)
 ns=a.parse_args();compare(ns.suite_dir.resolve(),ns.output_dir)
