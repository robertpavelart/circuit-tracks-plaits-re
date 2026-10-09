"""Offline standalone reference/DSP/oracle differential suite; fresh outputs only."""
import argparse,csv,hashlib,json,math,random,struct,subprocess,sys,wave
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'tools'))
from ct_stock_load_audit import verify_inputs
sys.path.insert(0,str(ROOT/'plaits/poc'))
from generate_final import generate
from fixed_model import Fixed,Q,F,mul,quant
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(out,n,v):
 with (out/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def csvout(out,n,rs):
 with (out/n).open('x',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def csvread(p):
 with p.open(encoding='utf8',newline='') as f:return list(csv.DictReader(f))
def cases():
 ds=[];inputs=[]
 def add(name,rate,blocks,fn,midi=None,kind='constant'):
  i=len(ds);start=len(inputs)*32
  for b in range(blocks):
   f,p,s=fn(b,blocks);inputs.append((i,b,f,p,s))
  ds.append(dict(id=i,name=name,rate=rate,blocks=blocks,start=start,samples=blocks*32,midi=midi,kind=kind))
 for note in [21,69,108]:
  hz=440*2**((note-69)/12)
  for pw in [0,.5,1]:
   for shape in [0,.5,1]:add(f'midi{note}_pw{pw}_shape{shape}',48000,96,
    lambda b,n,hz=hz,pw=pw,shape=shape:(hz/48000,pw,shape),note)
 for rate in [48000,48046.875]:
  for note in [0,21,60,69,96,120]:
   hz=440*2**((note-69)/12);add(f'pitch{note}_{rate}',rate,192,
    lambda b,n,hz=hz,rate=rate:(hz/rate,.5,.5),note)
 add('long_continuity',48000,2048,lambda b,n:(440/48000,.5,.5),69)
 add('joint_sweep',48000,256,lambda b,n:(440*2**(((21+87*b/(n-1))-69)/12)/48000,b/(n-1),1-b/(n-1)),kind='sweep')
 rng=random.Random(20)
 stress=[(440*2**((rng.choice([0,21,36,60,69,96,108,120])-69)/12)/48000,
  rng.choice([0,.01,.5,.99,1]),rng.choice([0,.25,.5,.75,1])) for _ in range(256)]
 add('bounded_stress',48000,256,lambda b,n:stress[b],kind='stress')
 add('frequency_cap',48000,64,lambda b,n:(.3,.01,1),kind='cap')
 return ds,inputs
def run(cmd):
 r=subprocess.run([str(x) for x in cmd],capture_output=True)
 if r.returncode:raise RuntimeError((cmd,r.returncode,r.stdout.decode(errors='replace'),r.stderr.decode(errors='replace')))
 return r.stdout
def collect(out,build):
 out=out.resolve();base=(ROOT/'builds/phase20a-regopt').resolve();build=build.resolve()
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh Phase20A suite child required')
 _,protected=verify_inputs();manifest=json.loads((ROOT/'plaits/upstream/source-manifest.json').read_text())
 assert manifest['revision']=='08460a69a7e1f7a81c5a2abcc7189c9a6b7208d4'
 assert manifest['stmlib_revision']=='e3bd7c9cc00e4364166f9905c0509b6ffd0535ec'
 for x in manifest['files']:assert sha(ROOT/'plaits/upstream'/x['path'])==x['sha256']
 out.mkdir(parents=True);generate(out/'assembly');layout=json.loads((out/'assembly/layout.json').read_text())
 ds,seq=cases();emit(out,'cases.json',ds)
 with (out/'inputs.tsv').open('x',encoding='utf8') as f:
  for i,b,v,p,s in seq:f.write(f'{i} {b} {v:.17g} {p:.17g} {s:.17g}\n')
 # Independent oracle preflight: no DSP/stock state constructed here.
 oracle=[];ostates=[];model=None;last=-1
 for i,b,v,p,s in seq:
  if i!=last:model=Fixed();last=i
  oracle+=model.render32(v,p,s);ostates.append(model.state())
 np.asarray(oracle,dtype='<i4').tofile(out/'oracle.i32')
 ref=build/'vs_reference.exe';dsp=build/'vs_dsp.exe'
 for v in ['first','repeat']:
  run([ref,out/'inputs.tsv',out/f'reference-{v}.f32'])
  print(f'Reference {v} complete',flush=True)
  run([dsp,out/'assembly/variablesaw.asm',out/'inputs.tsv',out/f'dsp-{v}',f"{layout['scratch_X'][1]:x}"])
  print(f'DSP {v} complete',flush=True)
 assert (out/'reference-first.f32').read_bytes()==(out/'reference-repeat.f32').read_bytes()
 native=out/'dsp-first';repeat=out/'dsp-repeat'
 identical=[]
 for p in native.iterdir():
  assert p.read_bytes()==(repeat/p.name).read_bytes(),p.name;identical.append(p.name)
 d=np.fromfile(native/'output.i32',dtype='<i4');r=np.fromfile(out/'reference-first.f32',dtype='<f4').astype('float64')
 assert len(d)==len(r)==len(oracle) and np.array_equal(d,np.asarray(oracle)), 'DSP integer/oracle sample mismatch'
 states=csvread(native/'states.csv');blocks=csvread(native/'blocks.csv')
 assert len(states)==len(blocks)==len(seq)
 for st,expected in zip(states,ostates):
  assert [int(st[k]) for k in ['phase','next','previous_pw','high','frequency','pw','shape']]==expected
  assert 0<=int(st['phase'])<5*F//4 and int(st['high']) in [0,1]
 metrics=[];pitch=[];counts=[];maxerr=0
 for case in ds:
  a=case['start'];b=a+case['samples'];dv=d[a:b].astype(float)/Q;rv=r[a:b];e=dv-rv
  warm=32;dd=dv[warm:];rr=rv[warm:];ee=dd-rr
  m=dict(case=case['id'],name=case['name'],sample_rate=case['rate'],kind=case['kind'],
   reference_dc=float(np.mean(rr)),DSP_dc=float(np.mean(dd)),DC_difference=float(np.mean(ee)),
   reference_peak=float(np.max(np.abs(rr))),DSP_peak=float(np.max(np.abs(dd))),
   RMS_difference=float(np.sqrt(np.mean(ee*ee))),max_abs_difference=float(np.max(np.abs(ee))),
   max_boundary_jump=float(np.max(np.abs(np.diff(dv)[31::32]))),
   max_nonboundary_jump=float(np.max(np.abs(np.diff(dv)[np.arange(len(dv)-1)%32!=31]))),
   block_continuity='EXACT integer oracle/state match, no phase reset',DSP_oracle_exact=True)
  metrics.append(m);maxerr=max(maxerr,m['RMS_difference'])
  cs=[x for x in blocks if int(x['case'])==case['id']];ins=[int(x['instructions']) for x in cs]
  counts.append(dict(case=case['id'],name=case['name'],blocks=case['blocks'],minimum=min(ins),
   maximum=max(ins),mean=float(np.mean(ins)),total=sum(ins),unit='Issued opcodes per32; not hardware cycles'))
  if case['midi'] is not None:
   ss=[x for x in states if int(x['case'])==case['id']]
   # Latched stable frequency measured from phase differences plus actual DSP
   # wrap-event PCs across blocks; not estimated from coarse FFT bins.
   advance=sum(int(x['wrap_events'])*F for x in cs[1:])+int(ss[-1]['phase'])-int(ss[0]['phase'])
   measured=advance/F/((len(cs)-1)*32)*case['rate'];desired=440*2**((case['midi']-69)/12)
   fq=int(ss[-1]['frequency'])/F*case['rate'];assert abs(measured-fq)<1e-9
   pitch.append(dict(case=case['id'],name=case['name'],rate=case['rate'],MIDI=case['midi'],
    desired_Hz=desired,DSP_phase_measured_Hz=measured,frequency_error_Hz=measured-desired,
    cents_error=1200*math.log2(measured/desired),frequency_cap_applied=False))
 assert np.all(np.isfinite(r)) and np.max(np.abs(d.astype(float)/Q))<3
 emit(out,'metrics.json',metrics);csvout(out,'comparison-metrics.csv',metrics);csvout(out,'pitch-accuracy.csv',pitch)
 csvout(out,'instruction-counts.csv',counts)
 info=json.loads(run([ref,'--info']));continuity=json.loads(run([ref,'--continuity']))
 assert continuity['steady64_vs_two32_max_difference']<1e-5
 emit(out,'reference-ABI.json',info);emit(out,'reference-block-continuity.json',continuity)
 # Optional audio has one common gain. Raw vectors preserve the unscaled contract.
 audio=out/'audio';audio.mkdir();examples=[]
 for c in [next(x for x in ds if x['name']=='long_continuity'),
           next(x for x in ds if x['name']=='midi69_pw0.5_shape0'),
           next(x for x in ds if x['name']=='midi69_pw0.5_shape1')]:
  a,b=c['start'],c['start']+c['samples']
  for name,vec in [('reference',r[a:b]),('DSP',d[a:b].astype(float)/Q)]:
   assert np.max(np.abs(vec*.75))<1
   pcm=np.round(vec*.75*32767).astype('<i2')
   n=f"{c['id']}-{name}.wav"
   with wave.open(str(audio/n),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000);w.writeframes(pcm.tobytes())
   examples.append(dict(path='audio/'+n,case=c['id'],signal=name,gain=.75,rate=48000,samples=len(vec)))
 emit(out,'audio-examples.json',examples)
 native_info=json.loads((native/'native-resources.json').read_text());labels=json.loads((native/'labels.json').read_text())
 resources=dict(status='MEASURED standalone DSP interpreter',P_words=native_info['P_words'],
  P_prefetch_padding=2,persistent_X_words=7,persistent_Y_words=0,immutable_table_words=0,
  control_input_X_words=3,scratch_X_words=layout['scratch_words'],output_Y_words=32,
  total_data_words=7+3+layout['scratch_words']+32,register_scratch_words=layout['register_scratch_words'],
  peak_hardware_stack_entries=native_info['peak_stack_entries'],hardware_stack_words=2*native_info['peak_stack_entries'],
  native_DIV_P_words=labels['done']-labels['ratio'],
  issued_per_block_min=min(x['minimum'] for x in counts),issued_per_block_max=max(x['maximum'] for x in counts),
  issued_per_block_mean=native_info['issued_instructions']/native_info['blocks'],
  measured_issued_instructions=native_info['issued_instructions'],blocks=native_info['blocks'],
  exact_hardware_cycles=None,cycle_estimate='At least issued opcode count; pipeline/memory/clock costs UNRESOLVED',
  tables_shared='No LUT needed; embedded constants/program can be shared in a future design',
  persistent_state_gate='<=64 words',stock_RAM_reserved=False,firmware_integration_ready=False)
 emit(out,'resource-manifest.json',resources)
 dependencies=[]
 subset=['plaits/dsp/oscillator/variable_saw_oscillator.h','plaits/dsp/oscillator/oscillator.h',
  'stmlib/dsp/dsp.h','stmlib/dsp/parameter_interpolator.h','stmlib/dsp/polyblep.h','stmlib/stmlib.h']
 for n in subset:dependencies.append(dict(path=n,SHA256=sha(ROOT/'plaits/upstream'/n)))
 emit(out,'dependencies.json',dict(headers=dependencies,used=['VariableSawOscillator.Init/Render/ComputeNaiveSample',
  'ParameterInterpolator.Init/Next/destructor','ThisBlepSample/NextBlepSample',
  'ThisIntegratedBlepSample/NextIntegratedBlepSample','CONSTRAIN/DISALLOW_COPY_AND_ASSIGN','kMaxFrequency'],
  standard_headers=['algorithm','cmath/math.h','inttypes.h','stddef.h'],
  LUTs=[],random=False,Voice=False,pitch_conversion='Caller Hz/rate; not NoteToFrequency or pitch LUT',
  pinned_eurorack=manifest['revision'],pinned_stmlib=manifest['stmlib_revision']))
 # Candidate cost comparison is a math experiment, not another DSP variant.
 table=[quant(1/(.5+i/128),Q) for i in range(65)];worst0=worst1=0
 for den in [1,2,3,7,100,714,41943,100000]+list(range(1,F,997)):
  k=den.bit_length()-1;shift=20-k;m=den<<shift if shift>=0 else den>>(-shift)
  idx=min((m-Q//2)>>14,63);frac=(m-Q//2)-(idx<<14)
  seed=table[idx]+((table[idx+1]-table[idx])*frac>>14)
  refined=mul(seed,2*Q-mul(m,seed));true=Q/(den/(2**(k+1)))
  worst0=max(worst0,abs(seed/true-1));worst1=max(worst1,abs(refined/true-1))
 with (out/'reciprocal-candidate.be24').open('xb') as f:
  for v in table:f.write(v.to_bytes(3,'big'))
 emit(out,'division-strategies.json',dict(selected='Table-free exact21-bit nativeDIV ratios; oscillator algebra unchanged',
  selected_P_words=resources['native_DIV_P_words'],selected_table_words=0,
  LUT_candidate=dict(status='TESTED host integer math only; NOT DSP implementation',words=65,
   mutable_state_words=0,extra_scratch_estimate='2..4 words plus exponent/index registers',
   normalization='positive denominator normalized to[.5,1);21-bit mantissa',
   maximum_sampled_relative_error_linear=worst0,maximum_sampled_relative_error_one_Newton=worst1,
   extra_P_words=None,extra_P_cost='UNRESOLVED until assembled; not measured instruction savings'),
  algebra='Use f/pw+f/(1-pw), not standalone enormous1/pw slopes',
  anti_alias_variant='One complete step+integratedBLEP implementation; no dropped-correction variant',
  decision='Exact golden arithmetic with liveness-colored register scratch and explicit24-bit transfers'))
 emit(out,'sample-rate-contract.json',dict(reference_rate=48000,conditional_Circuit_rate=48046.875,
  normalized_frequency='Hz/sampleRate, rounded Q2.22; sourcemax.25',
  multiply_48k_increment_to_conditional=48000/48046.875,
  exact_retuning_ratio='1024/1025',unretuned_rate_error_cents=1200*math.log2(48046.875/48000),
  Mutable_note_frequency_table_used=False,pinned_MI_pitch_correction_rate=47872.34,
  MI_converter_unmodified_error_at_conditional_cents=1200*math.log2(48046.875/47872.34),
  conditional_Circuit_rate_is_measured_hardware=False))
 audit=out/'unchanged-core-audit.json'
 run([sys.executable,'-B',ROOT/'emulator/tests/audit_paths.py','--results',ROOT/'builds/phase19a/validated/results.json','--output',audit])
 for n,h in json.loads((ROOT/'builds/phase19c-fullhelper/final/source-manifest.json').read_text()).items():assert sha(ROOT/n)==h
 verify_inputs()
 source={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'plaits/poc/regopt').iterdir() if p.is_file()}
 source.update({p.relative_to(ROOT).as_posix():sha(p) for p in [ref,dsp,ROOT/'builds/phase19a/core-build/replay_core.lib',ROOT/'builds/phase19a/core-build/upstream/asmjit/asmjit.lib']})
 emit(out,'implementation-provenance.json',source)
 emit(out,'result.json',dict(status='TESTED standalone closest-source oscillator',cases=len(ds),blocks=len(seq),samples=len(d),
  DSP_integer_oracle_exact=True,all_final_states_exact=True,reference_twice_identical=True,
  DSP_twice_identical_files=sorted(identical),execution_trace='Complete issuedPC u16stream; immutable opcodes inprogram.be24; authoritative writes hashed perblock',
  maximum_case_RMS_difference=maxerr,maximum_absolute_cents_error=max(abs(x['cents_error']) for x in pitch),
  stress_overflow_saturation_bad_ratio_lookup_phase_failures=0,reference_block_continuity=continuity,
  Circuit_RAM_ownership='FROZEN/UNRESOLVED',stock_image_loaded=False,hardware_access=False,
  persistent_gate_le64=True,firmware_integration_readiness=False))
 emit(out,'hashes.json',{p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
 print(json.dumps(resources,indent=2),flush=True)
 print('Differential pass; worstcaseRMS',maxerr,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True,type=Path);p.add_argument('--build-dir',required=True,type=Path)
 a=p.parse_args();collect(a.output_dir,a.build_dir)
