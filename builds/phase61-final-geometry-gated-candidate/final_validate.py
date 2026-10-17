"""Final checkpoint verification and exact classified diff; never builds firmware.
Reads saved native/update results, authenticates inputs, emits Phase61 evidence.
"""
from pathlib import Path
import sys,json,hashlib,collections
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
sys.path.insert(0,str(R/'builds/phase43-hardware-test-candidate'))
from independent_validate import decode,crc
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
from capstone.arm import ARM_OP_IMM
def sha(b):return hashlib.sha256(b).hexdigest()
def load(name):return json.loads((O/name).read_text())
def main():
 name='circuittracks-final-geometry-gated-nor-test';raw=(O/(name+'.syx')).read_bytes()
 image,_,details=decode(raw);assert image==(O/(name+'.bin')).read_bytes()
 build=load('construction.json');fv=load('file-validation.json')
 assert sha(image)==build['BIN_sha256']==fv['BIN_sha256'] and sha(raw)==build['SYX_sha256']==fv['SYX_sha256']
 base=(R/'builds/phase43-hardware-test-candidate/clean-sc35d8.bin').read_bytes()
 assert sha(base)==build['source_sha256']
 # Reconstruct exactly the reviewed structure independently of the emitter.
 expected=bytearray(base);expected.extend(b'\xff'*(len(image)-len(base)))
 expected[0x5b6cc:0x5bc8c]=b'\xff'*(0x5bc8c-0x5b6cc)
 regions=[]
 for group in ('components','trampolines'):
  for k,x in build[group].items():
   at=int(x['address'],16)-0x08010000;n=x['bytes'];b=image[at:at+n];assert sha(b)==x['sha256'];expected[at:at+n]=b
   regions.append((at,at+n,group+':'+k))
 for x in build['patches']:
  at=int(x['address'],16)-0x08010000;b=bytes.fromhex(x['after']);assert base[at:at+len(b)].hex()==x['before'];expected[at:at+len(b)]=b
  regions.insert(0,(at,at+len(b),'hook/marker:'+x['address']))
 assert bytes(expected)==image,'unexpected gap/padding/code byte'
 regions.append((0x5b6cc,0x5bc8c,'obsolete diagnostic pool cleared'))
 ranges=[];begin=None;last=None
 for i in range(len(image)+1):
  changed=i<len(image) and (i>=len(base) or base[i]!=image[i]);kind=None
  if changed:
   kind=next((k for a,z,k in regions if a<=i<z),None)
   if kind is None:assert i>=len(base) and image[i]==255;kind='appended FF alignment/reserved padding'
  if begin is not None and (kind!=last or not changed):ranges.append(dict(start=hex(0x08010000+begin),end_exclusive=hex(0x08010000+i),bytes=i-begin,classification=last));begin=None
  if changed and begin is None:begin=i;last=kind
 (O/'classified-diff.json').write_text(json.dumps(dict(confidence='PROVEN',base_sha256=sha(base),candidate_sha256=sha(image),ranges=ranges,classification_bytes=dict(collections.Counter({k:sum(x['bytes'] for x in ranges if x['classification']==k) for k in {x['classification'] for x in ranges}})),unexplained_bytes=0),indent=2)+'\n')
 # Full M-class disassembly; earlier diagnostic .asm views stopped at privileged
 # MRS instructions. Preserve those checkpoint files and write separate views.
 md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);md.detail=True;calls=[];instructions={}
 for group in ('components','trampolines'):
  for k,x in build[group].items():
   at=int(x['address'],16);b=image[at-0x08010000:at-0x08010000+x['bytes']];ins=list(md.disasm(b,at));assert sum(i.size for i in ins)==len(b),(k,len(b))
   instructions[k]=ins;(O/('reviewed-'+group+'-'+k+'.asm')).write_text('\n'.join(f'{i.address:08X}: {i.mnemonic} {i.op_str}' for i in ins)+'\n')
   for i in ins:
    if i.mnemonic in ('bl','blx'):
     assert i.operands[0].type==ARM_OP_IMM,(k,i.op_str)
     calls.append(dict(component=k,address=hex(i.address),target=hex(i.operands[0].imm)))
 app_calls={int(x['target'],16) for x in calls if int(x['target'],16)<0x0806bd00}
 # Includes only logging/ctor-return tails through non-BL branches separately
 # listed in reviewed trampolines; command path has no writer/erase call.
 assert app_calls=={0x080599b8,0x08020c90,0x08047c6c,0x08035a50,0x0801be60},app_calls
 # Literal address pairs are independently read from decoded raw code.
 loads=[]
 for k,ins in instructions.items():
  for i,j in zip(ins,ins[1:]):
   if i.mnemonic=='movw' and j.mnemonic=='movt' and i.operands[0].reg==j.operands[0].reg:
    v=i.operands[1].imm|(j.operands[1].imm<<16)
    if v in (0x81000,0x82000):loads.append(dict(component=k,address=hex(i.address),value=hex(v)))
 assert {x['value'] for x in loads if x['component']=='raw'}=={'0x81000','0x82000'}
 native=load('native-tests.json');host=load('host-tests.json');coupled=load('coupled-tests.json');startup=load('candidate-startup.json')
 assert native['all_passed'] and len(native['cases'])==28 and host['passed'] and len(host['cases'])==19 and coupled['passed']
 assert startup['control']=='0x11' and startup['frontier']['pc']=='0x801ae14'
 # Results were persisted after these exact candidate bytes were generated.
 for n in ('native-tests.json','host-tests.json','coupled-tests.json','candidate-startup.json'):
  assert (O/n).stat().st_mtime >= (O/(name+'.bin')).stat().st_mtime,n
 transitions=[]
 for which in ('b13-to-candidate','candidate-to-official','candidate-to-b13'):
  t=load(which+'-summary.json');ops=load(which+'-operations.json')
  assert t['accepted'] and t['actual_install_performed'] and not t['silent_noop']
  assert t['incoming_image_sha256']==t['final_installed_sha256']==t['staged_image_sha256']
  assert ops['bootloader_unchanged'] and ops['installed_exact']
  if which=='b13-to-candidate':assert t['incoming_image_sha256']==sha(image) and t['incoming_SYX_sha256']==sha(raw)
  else:assert t['installed_before_sha256']==sha(image)
  for lo,hi in ((0x81000,0x81017),(0x82000,0x82200)):
   assert not [x for x in ops['operations'] if x['kind'] in ('WRITE','ERASE') and int(x['start'],16)<hi and int(x['end_exclusive'],16)>lo]
  transitions.append({k:t[k] for k in ('transition','incoming_image_sha256','incoming_bytes','external_erase_ranges','external_program_ranges','internal_program_ranges','silent_noop')})
 pins=json.loads((R/'builds/phase42-exact-rdiag-integration/inputs.json').read_text())
 for p in pins['sources']:assert sha(Path(p['local']).read_bytes())==p['sha256']
 historical={}
 for phase in ('phase60-final-triage','phase60-irq-liveness-final','phase59-scheduler-first-mount-order','phase58-preconstructor-liveness-closure','phase57-first-mount-provenance','phase45-nor-mutation-closure'):
  folder=R/'builds'/phase;count=0
  for line in (folder/'SHA256SUMS.txt').read_text().splitlines():
   h,n=line.split('  ',1);assert sha((folder/n).read_bytes())==h,(phase,n);count+=1
  historical[phase]=count
 negatives={}
 for label,change in [('wrong product',lambda b:b.__setitem__(7,0x65)),('truncated',lambda b:b.__delitem__(-1)),('trailing garbage',lambda b:b.extend(b'\x00')),('corrupt block',lambda b:b.__setitem__(60,b[60]^1))]:
  b=bytearray(raw);change(b)
  try:decode(bytes(b))
  except (AssertionError,ValueError,IndexError):negatives[label]='rejected'
  else:raise AssertionError(label)
 r=dict(confidence='PROVEN',verdict='PASS',candidate=name,SYX_bytes=len(raw),SYX_sha256=sha(raw),BIN_bytes=len(image),BIN_sha256=sha(image),CRC=f'{crc(image):08X}',application_end_exclusive=hex(0x08010000+len(image)),headroom_bytes=0x70000-len(image),native_cases=28,host_cases=19,startup_executed_instructions=startup['executed_instructions'],diff_changed_bytes=sum(x['bytes'] for x in ranges),unexplained_diff_bytes=0,direct_native_calls=calls,fixed_address_loads=loads,transitions=transitions,historical_manifests_preserved=historical,pinned_sources_preserved=len(pins['sources']),serialization_negatives=negatives,hardware_access=False,MIDI_ports_opened=0,firmware_transmitted=False)
 (O/'final-validation.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ('direct_native_calls','transitions','fixed_address_loads')},indent=2))
if __name__=='__main__':main()
