"""Phase20A standalone gates, trace/output checks and immutable-input guards."""
import argparse,csv,hashlib,json,math,subprocess,sys,wave
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'plaits/poc'))
from ct_stock_load_audit import verify_inputs
from fixed_model import Q,F
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def obj(p):return json.loads(p.read_text(encoding='utf8'))
def rows(p):
 with p.open(encoding='utf8',newline='') as f:return list(csv.DictReader(f))
def verify(suite,build,out):
 out=out.resolve();base=(ROOT/'builds/phase20a-div').resolve()
 if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh Phase20A verification child required')
 for n,h in obj(suite/'hashes.json').items():assert sha(suite/n)==h,n
 for n,h in obj(suite/'implementation-provenance.json').items():assert sha(ROOT/n)==h,n
 res=obj(suite/'resource-manifest.json');result=obj(suite/'result.json');cases=obj(suite/'cases.json')
 assert res['persistent_X_words']==7 and res['persistent_Y_words']==0 and res['immutable_table_words']==0
 assert res['scratch_X_words']==44 and res['output_Y_words']==32 and res['total_data_words']==86
 assert res['P_words']==700 and res['native_DIV_P_words']==18 and res['peak_hardware_stack_entries']==3
 assert result['cases']==43 and result['blocks']==7520 and result['samples']==240640
 assert not result['stock_image_loaded'] and not result['hardware_access'] and not result['firmware_integration_readiness']
 assert result['DSP_integer_oracle_exact'] and result['all_final_states_exact']
 assert (suite/'reference-first.f32').read_bytes()==(suite/'reference-repeat.f32').read_bytes()
 assert (suite/'dsp-first/output.i32').read_bytes()==(suite/'oracle.i32').read_bytes()
 for n in result['DSP_twice_identical_files']:assert (suite/'dsp-first'/n).read_bytes()==(suite/'dsp-repeat'/n).read_bytes()
 # Full issued-PC stream, not a hash-only execution trace. Each opcode is recoverable
 # from immutable program.be24; all PCs must be actual instruction starts.
 lines=(suite/'dsp-first/program.asm').read_text().splitlines()
 starts={int(x.split()[0],16) for x in lines}
 p=np.memmap(suite/'dsp-first/execution-pc.u16',dtype='<u2',mode='r')
 assert len(p)==res['measured_issued_instructions']==sum(int(x['instructions']) for x in rows(suite/'dsp-first/blocks.csv'))
 assert set(np.unique(p))<=starts
 b=rows(suite/'dsp-first/blocks.csv');assert sum(int(x['instructions']) for x in b)==len(p)
 assert all(int(x['output_writes'])==32 and int(x['peak_stack'])<=3 for x in b)
 # The helper and renderer use verified signedMPY, never mixed-signed fallback.
 code=(suite/'dsp-first/program.be24').read_bytes();assert len(code)==700*3
 for line in lines:
  a,s=line.split(' ',1)
  if s=='mpy y0,x0,a':
   pos=(int(a,16)-0x200)*3;assert code[pos:pos+3]==bytes.fromhex('2000d0')
 metrics=obj(suite/'metrics.json')
 # Prototype acceptance, not bit-identical float fidelity: pitch<1.1cents over
 # testedMIDI0..120, rawRMS<.025, tinyDC/peak changes. Event timing may differ.
 assert max(x['RMS_difference'] for x in metrics)<.025
 assert max(abs(x['DC_difference']) for x in metrics)<.001
 assert max(abs(x['DSP_peak']-x['reference_peak']) for x in metrics)<.002
 assert result['maximum_absolute_cents_error']<1.1
 ref=np.fromfile(suite/'reference-first.f32',dtype='<f4').astype(float)
 dsp=np.fromfile(suite/'dsp-first/output.i32',dtype='<i4').astype(float)/Q
 spectra=[]
 for c in cases:
  if c['kind']!='constant':continue
  a=c['start']+32;z=c['start']+c['samples'];w=np.hanning(z-a)
  rr=ref[a:z]-np.mean(ref[a:z]);dd=dsp[a:z]-np.mean(dsp[a:z])
  r=np.abs(np.fft.rfft(rr*w));d=np.abs(np.fft.rfft(dd*w))
  sim=float(np.dot(r,d)/(np.linalg.norm(r)*np.linalg.norm(d)))
  assert sim>.999,'Magnitude-spectrum topology mismatch'
  spectra.append(dict(case=c['id'],name=c['name'],FFT_magnitude_cosine_similarity=sim))
 assert obj(suite/'reference-block-continuity.json')['steady64_vs_two32_max_difference']==0
 # All43 case DSP states exactlymatch independent integer oracle; boundary jumps
 # are therefore waveform events, not resets. Long case has2048 consecutivecalls.
 assert next(c for c in cases if c['name']=='long_continuity')['blocks']==2048
 rates=obj(suite/'sample-rate-contract.json');assert rates['exact_retuning_ratio']=='1024/1025'
 assert abs(rates['multiply_48k_increment_to_conditional']-1024/1025)<1e-15
 for x in rows(suite/'pitch-accuracy.csv'):
  f=float(x['DSP_phase_measured_Hz']);want=float(x['desired_Hz'])
  assert abs(float(x['cents_error'])-1200*math.log2(f/want))<1e-9
 for a in obj(suite/'audio-examples.json'):
  with wave.open(str(suite/a['path']),'rb') as w:
   assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,48000,a['samples'])
 dep=obj(suite/'dependencies.json');assert len(dep['headers'])==6 and not dep['Voice'] and not dep['random'] and not dep['LUTs']
 assert obj(suite/'reference-ABI.json')['sizeof_VariableSawOscillator']==28
 verify_inputs();import ct_fw_tool
 syx=ROOT/'original/circuittracks-firmware-4486.syx';fw=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
 assert ct_fw_tool.decode_syx(syx)['firmware']==fw and ct_fw_tool.build_syx(syx,fw)==syx.read_bytes()
 for x in obj(ROOT/'firmware/dsp/build-4486/manifest.json')['blocks']:
  for k in ['stream','payload']:assert sha(ROOT/'firmware/dsp/build-4486'/x[k+'_file'])==x[k+'_sha256']
 for x in obj(ROOT/'plaits/upstream/source-manifest.json')['files']:
  assert sha(ROOT/'plaits/upstream'/x['path'])==x['sha256']
 out.mkdir(parents=True)
 # Failed input tests exercise wrappers only. No synthetic positive Circuit state.
 bad=out/'invalid.tsv';bad.write_text('0 0 0 .5 .5\n')
 r=subprocess.run([str(build/'vs_dsp.exe'),str(suite/'assembly/variablesaw.asm'),str(bad),str(out/'invalid-run'),'ac'],capture_output=True)
 assert r.returncode and 'Invalid control domain' in r.stderr.decode()
 assert (out/'invalid-run/execution-pc.u16').stat().st_size==0
 refusals=[]
 for cmd in [[str(build/'vs_dsp.exe'),str(suite/'assembly/variablesaw.asm'),str(suite/'inputs.tsv'),str(suite/'dsp-first'),'ac'],
             [str(build/'vs_reference.exe'),str(suite/'inputs.tsv'),str(suite/'reference-first.f32')],
             [sys.executable,'-B',str(ROOT/'plaits/poc/div/collect_compact.py'),'--output-dir',str(suite),'--build-dir',str(build)]]:
  r=subprocess.run(cmd,capture_output=True);assert r.returncode;refusals.append(Path(cmd[0]).name)
 # Refusal did not alter existing evidence.
 for n,h in obj(suite/'hashes.json').items():assert sha(suite/n)==h,n
 subprocess.run([sys.executable,'-B',str(ROOT/'emulator/tests/audit_paths.py'),
  '--results',str(ROOT/'builds/phase19a/validated/results.json'),'--output',str(out/'unchanged-core-audit.json')],capture_output=True,check=True)
 with (out/'spectral-comparison.json').open('x',encoding='utf8') as f:json.dump(spectra,f,indent=2,sort_keys=True);f.write('\n')
 gates={k:True for k in 'ABCDEFGHIJK'}
 report=dict(status='PASS',success_gates=gates,gate_F_scope='Tested structural/spectral similarity and reported numerical error; not sample identity',
  cases=43,blocks=7520,samples=240640,issued_instructions_per_full_run=res['measured_issued_instructions'],
  full_PC_traces_byte_identical=True,DSP_vectors_and_states_exact_integer_oracle=True,
  DSP_native_repeated_files=8,reference_repeated=True,minimum_FFT_magnitude_cosine=min(x['FFT_magnitude_cosine_similarity'] for x in spectra),
  persistent_state_words=7,scratch_words=44,immutable_table_words=0,P_words=700,
  no_new_Circuit_RAM_invariant=True,no_Circuit_image_loaded=True,firmware_hardware_integration=False,
  original_firmware_roundtrip_all10_extracts183_upstream_sources_sealed_core='PASS',overwrite_refusals=refusals,
  invalid_frequency_refused_before_CPU_execution=True,verifier_SHA256=sha(Path(__file__)))
 with (out/'verification.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['suite-dir','build-dir','output-dir']:p.add_argument('--'+n,required=True,type=Path)
 a=p.parse_args();verify(a.suite_dir,a.build_dir,a.output_dir)
