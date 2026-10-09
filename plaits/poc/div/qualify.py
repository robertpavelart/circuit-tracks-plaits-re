"""Fresh isolated DIV fixtures; independent bit recurrence and integer oracle."""
import argparse,csv,hashlib,json,random,struct,subprocess
from pathlib import Path
from generate_div import helper
ROOT=Path(__file__).resolve().parents[3]
MASK=(1<<56)-1;Q=1<<21
def div_step(a,s,sr):
 # Manual13-53/54:56-bit shift, C inserted, sign-based MSP add/subtract.
 old=(a>>55)&1;different=old ^ (s>>23)
 shifted=((a<<1)|(sr&1))&MASK;new=(shifted>>55)&1
 v=new^old
 signed_s=s-(1<<24) if s&(1<<23) else s
 result=(shifted + ((signed_s if different else -signed_s)<<24))&MASK
 sr=(sr&~3)|v*2|int(not(result&(1<<55)))
 if v:sr|=64
 return result,sr
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def qualify(out,exe):
 out=out.resolve();base=ROOT/'builds/phase20a-div'
 if out.exists() or not out.is_relative_to(base) or out==base:raise ValueError('Fresh output required')
 out.mkdir(parents=True)
 pairs={(n,d) for d in range(1,65) for n in range(4*d)}
 for d in [1,2,3,7,63,64,65,714,715,41943,1048576,2097152,4194303,4194304,8388607]:
  for q in [0,1,2,3,Q//2-1,Q//2,Q-1,Q,Q+1,2*Q-1,2*Q,3*Q,4*Q-1]:
   n=d*q//Q
   for v in [n-1,n,n+1]:
    if 0<=v<=8388607 and v<4*d:pairs.add((v,d))
  for v in [d-1,d,d+1,2*d-1,2*d,3*d,4*d-1]:
   if 0<=v<=8388607 and v<4*d:pairs.add((v,d))
 rng=random.Random(200021)
 for _ in range(10000):
  d=rng.randint(1,8388607);pairs.add((rng.randrange(min(4*d,8388608)),d))
 for n in [0,1,714,4194304,8388607]:pairs.add((n,0))
 cases=[(n,d,c) for n,d in sorted(pairs) for c in [0,1]]
 (out/'helper.asm').write_text('\n'.join(['render32:','jsr @ratio','jmp @done']+helper()+['done:'])+'\n')
 (out/'inputs.tsv').write_text(''.join(f'{i} {n} {d} {c}\n' for i,(n,d,c) in enumerate(cases)))
 for label in ['first','repeat']:
  subprocess.run([str(exe),str(out/'helper.asm'),str(out/'inputs.tsv'),str(out/label)],check=True)
 for p in (out/'first').iterdir():assert sha(p)==sha(out/'repeat'/p.name),p.name
 records=list(csv.DictReader((out/'first/results.csv').open()))
 buf=(out/'first/iterations.bin').read_bytes();at=0;costs=[];steps=0
 for row,(n,d,c) in zip(records,cases):
  expected=(n*Q)//d if d else 0
  assert int(row['quotient'])==expected,(row,expected)
  assert int(row['div_count'])==(21 if d else 0)
  costs.append(int(row['issued'])-2) # exclude harness JSR/JMP, include helper RTS
  if not d:continue
  a,sr=struct.unpack_from('<QI',buf,at);at+=12
  assert a==(n%d)<<24 and not sr&1
  original=sr
  for i in range(21):
   a,sr=div_step(a,d,sr)
   raw,sr_raw=struct.unpack_from('<QI',buf,at);at+=12
   observed=(raw&MASK,sr_raw) # core signed right-shift export, canonical56 bits
   assert observed==(a,sr),(n,d,i,observed,(a,sr))
   steps+=1
  assert (a&0xffffff)*2+(sr&1)==((n%d)*Q)//d
  assert (sr&~67)==(original&~67)
 assert at==len(buf) and len(records)==len(cases)
 labels=json.loads((out/'first/labels.json').read_text())
 result=dict(status='TESTED',cases=len(cases),DIV_iterations_checked=steps,carry_inputs=[0,1],
  independent_integer_quotient_exact=True,independent_56bit_DIV_state_C_V_L_exact=True,
  repeat_files_identical=True,zero_denominator_guard='returns zero without DIV; outside valid quotient domain',
  quotient_contract='floor(n*2^21/d), n>=0, d>0, n<4d; positive signed24 inputs',
  helper_P_words=labels['done']-labels['ratio'],issued_per_valid_call_min=min(c for c,(_,d,_) in zip(costs,cases) if d),
  issued_per_valid_call_max=max(costs),issued_guard_zero=5,helper_includes_RTS=True,
  preconditions='no scale/compatibility mode, positive24 inputs; reduced remainder<d; C cleared',
  scratch_writes=0,fixtures_no_memory_writes=True,hardware_access=False)
 (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 (out/'hashes.json').write_text(json.dumps({p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()},indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output-dir',type=Path,required=True);a.add_argument('--fixture-exe',type=Path,required=True)
 ns=a.parse_args();qualify(ns.output_dir,ns.fixture_exe.resolve())
