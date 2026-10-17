"""Exact patch, retained input and selected-install consistency. No builder run."""
from environment import *
import hashlib
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 a=read(O/'integration.json');before=(O/'rebuilt-sc35d8.bin').read_bytes();after=(O/'integrated-internal.bin').read_bytes()
 assert digest(O/'rebuilt-sc35d8.bin')==a['base_image_sha256'] and digest(O/'integrated-internal.bin')==a['image_sha256']
 assert len(before)==len(after)==int(a['image_size'],16)==0x5bc8c
 allowed=[(0x0806b6cc,0x0806bc8c)]+[(int(x['address'],16),int(x['address'],16)+len(bytes.fromhex(x['after']))) for x in a['hook_patches']]
 changed=[i for i,(x,y) in enumerate(zip(before,after)) if x!=y]
 assert all(any(lo<=0x08010000+i<hi for lo,hi in allowed) for i in changed)
 runs=[]
 for i in changed:
  if runs and runs[-1][1]==0x08010000+i:runs[-1][1]+=1
  else:runs.append([0x08010000+i,0x08010000+i+1])
 for x in a['hook_patches']:
  i=int(x['address'],16)-0x08010000;n=len(bytes.fromhex(x['after']))
  assert before[i:i+n].hex()==x['before'] and after[i:i+n].hex()==x['after']
 for x in a['components'].values():
  i=int(x['address'],16)-0x08010000
  assert sha(after[i:i+x['bytes']])==x['sha256']
 assert before[:0x1e8]==after[:0x1e8]
 # Entire pre-ARM payload span, including both embedded DSP bootstraps.
 assert before[0x1f0:0x855a]==after[0x1f0:0x855a]
 # Enumerate all potential wide direct branches, including untrusted data.
 # The scan deliberately over-approximates; it is not a whole-image ARM CFG.
 edges=[]
 for at in range(0x08010000,0x0806b6cc,2):
  raw=after[at-0x08010000:at-0x08010000+4]
  if len(raw)<4 or raw[1]&0xf8!=0xf0:continue
  for ins in md.disasm(raw,at,count=1):
   if ins.mnemonic in ('b.w','bl') and ins.op_str.startswith('#'):
    dest=int(ins.op_str[1:],16)
    if 0x0806b6cc<=dest<0x0806bc8c:edges.append((hex(at),ins.mnemonic,hex(dest)))
 assert [int(x[0],16) for x in edges]==[0x0801eb30,0x0805998e,0x0805dbcc]
 # Search unaligned as well as aligned literal pointers into the retired pool.
 literal=[]
 for i in range(len(after)-3):
  if i>=0x5b6cc:continue
  if 0x0806b6cc<=int.from_bytes(after[i:i+4],'little')<0x0806bc8c:literal.append(hex(0x08010000+i))
 assert not literal
 # The command has only its admission-filter direct BL entry.
 command=int(a['layout']['command'],16);callers=[]
 for at in range(0x0806b6cc,0x0806bc8c,2):
  for ins in md.disasm(after[at-0x08010000:at-0x08010000+4],at,count=1):
   if ins.mnemonic=='bl' and ins.op_str==f'#{hex(command)}':callers.append(hex(at))
 assert callers==['0x806b838']
 pins=read(O/'inputs.json')['sources']
 assert all(digest(Path(x['path']))==x['sha256'] and digest(Path(x['local']))==x['sha256'] for x in pins)
 ref=read(R/'builds/phase20i-authentic-qualification/provenance.json')['reference_before']
 assert len(ref)==451 and all(digest(Path(p))==h for p,h in ref.items())
 upstream=read(R/'plaits/upstream/source-manifest.json')['files']
 assert len(upstream)==183 and all(digest(R/'plaits/upstream'/p['path'])==p['sha256'] for p in upstream)
 prior=[]
 for n in range(26,42):
  for p in (R/'builds').glob(f'phase{n}-*/validation.json'):
   assert all(digest(p.parent/f)==h for f,h in read(p)['evidence_sha256'].items()),str(p)
   prior.append(str(p.parent))
 install=read(O/'installation.json');assert install['candidate']['sha256']==a['image_sha256'] and install['installed_exact']
 assert all(x['writes']==x['erase_overlaps']==0 for x in install['preservation'].values())
 rollback=[]
 for name,h in [('circuittracks-firmware-4486-STOCK.bin','b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da'),('circuittracks-firmware-4486-STOCK.syx','bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd')]:
  p=REF/'stock'/name;assert digest(p)==h;rollback.append(dict(path=str(p),sha256=h,bytes=p.stat().st_size))
 assert not list(O.rglob('*.syx'))
 # Native first-use MFX initialization remains byte-exact in the fixture.
 controls=[]
 for candidate in (False,True):
  e=Physical();u=e.uc
  if not candidate:u.mem_write(0x08010000,before)
  for reg in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1):u.reg_write(reg,0x77550000+reg)
  assert e.call(0x0805dbcc)==0x20044d7c
  controls.append(dict(state=bytes(u.mem_read(0x20044d7c,220)).hex(),regs=[u.reg_read(r) for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)],sp=u.reg_read(UC_ARM_REG_SP)))
 assert controls[0]==controls[1]
 patch=dict(confidence='PROVEN',image_sha256=a['image_sha256'],declared_replaced_ranges_end_exclusive=[[hex(lo),hex(hi)] for lo,hi in allowed],changed_bytes=len(changed),exact_changed_runs_end_exclusive=[[hex(lo),hex(hi)] for lo,hi in runs],external_wide_branch_candidates=edges,external_literal_pointer_candidates=literal,command_BL_callers=callers,previous_function_ends_with_return='0806B6CA pop {r4,r5,r6,r7,pc}',vectors_changed=0,DSP_changes=0,bootloader_changes=0,option_byte_changes=0,image_growth_bytes=0,scope='Changed bytes and conservative branch/literal scans; no claim of universal indirect execution closure')
 (O/'patch-map.json').write_text(json.dumps(patch,indent=2)+'\n')
 (O/'masterfx-init-results.json').write_text(json.dumps(dict(confidence='PROVEN',original_and_integrated_initialization_equal=True,observables=controls[1]),indent=2)+'\n')
 result=dict(confidence='PROVEN',SC35D8_reproduction_reused=True,candidate_sha256=a['image_sha256'],reference_files_unchanged=451,pinned_sources_unchanged=183,phase42_source_inputs_unchanged=len(pins),prior_evidence_unchanged=prior,rollback=rollback,patch=patch,installation_preservation=install['preservation'],hardware_access=False,SYX_generated=False,broad_cold_boot_run=False)
 (O/'audit-results.json').write_text(json.dumps(result,indent=2)+'\n')
 print('Audit PASS:',len(changed),'changed bytes;',len(pins),'phase42 inputs;',len(prior),'prior phases')
if __name__=='__main__':main()

