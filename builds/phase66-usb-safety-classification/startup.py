"""Continue Phase65 using only bounded USB initialization register semantics."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase63-defect-closure';A=R/'builds/phase65-shi-model-closure'
sys.path.insert(0,str(A));from dsp_peer import BootPeer
from native_dsp import NativeDSP
from spi2_model import SPI2
from unicorn import UC_HOOK_MEM_INVALID
from unicorn import arm_const as ARM
sys.path.insert(0,str(O));from usb_model import USBInit
sys.path.insert(0,str(R/'builds/phase43-hardware-test-candidate'));from independent_validate import decode
c=json.loads((P/'development-identity.json').read_text());IMAGE=decode((P/(c['candidate']+'.syx')).read_bytes())[0];assert hashlib.sha256(IMAGE).hexdigest()==c['BIN_sha256']
CAPTURED={}
ALLOC=[];PENDING=[];FAULTS=[];SB=[];LAST=[None,None];SB_ACTIVE=[False]
def CAPTURE(x):CAPTURED.update(x)
def observe(e,u,pc):
 sp=u.reg_read(ARM.UC_ARM_REG_SP);r9=u.reg_read(ARM.UC_ARM_REG_R9)
 if pc==0x0801d57e:SB_ACTIVE[0]=True
 if SB_ACTIVE[0] and r9!=LAST[1]:SB.append(dict(previous_PC=None if LAST[0] is None else hex(LAST[0]),PC=hex(pc),R9=hex(r9),SP=hex(sp),IPSR=u.reg_read(ARM.UC_ARM_REG_IPSR),TCB=hex(e.r32(0x20006138))))
 LAST[:]=[pc,r9]
 for entry in list(PENDING):
  if entry['return_PC']==pc and entry['SP']==sp:
   p=u.reg_read(ARM.UC_ARM_REG_R0);entry.update(returned=hex(p),end=hex((p+entry['bytes'])&0xffffffff),return_instruction=hex(pc),heap_after=hex(e.r32(0x20002b48)));PENDING.remove(entry)
 if pc in(0x0801cfa4,0x0801d7d8):
  entry=dict(kind='generic allocation' if pc==0x0801cfa4 else 'bounded bump',bytes=u.reg_read(ARM.UC_ARM_REG_R0),return_PC=u.reg_read(ARM.UC_ARM_REG_LR)&~1,SP=sp,heap_before=hex(e.r32(0x20002b48)),TCB=hex(e.r32(0x20006138)))
  ALLOC.append(entry);PENDING.append(entry)
def invalid(u,access,address,size,value,data):
 FAULTS.append(dict(access=access,address=hex(address),size=size,PC=hex(u.reg_read(ARM.UC_ARM_REG_PC)),registers={n:hex(u.reg_read(getattr(ARM,'UC_ARM_REG_'+n))) for n in ['R0','R1','R2','R3','R4','R5','R6','R7','R8','R9','R10','R11','R12','SP','LR','CONTROL','MSP','PSP','IPSR','XPSR']}))
 return False
def replace(s,a,b):
 assert a in s,a
 return s.replace(a,b,1)
def main():
 s=(A/'selected-startup.py.txt').read_text()
 s=replace(s,'spi.bind(u);u.mem_map', 'spi.bind(u);usb=USBInit();usb.bind(u);u.mem_map')
 s=replace(s,'usb.bind(u);u.mem_map','usb.bind(u);u.hook_add(UC_HOOK_MEM_INVALID,invalid);u.mem_map')
 s=replace(s,'counts[pc]+=1;last.append(pc)','observe(e,u,pc);counts[pc]+=1;last.append(pc)')
 # Record additional relevant state, without changing its values.
 hook="""if pc in (0x08038154,0x08038256,0x08048316,0x0804830e):
         events.append(dict(event='USB init boundary',PC=hex(pc),record=bytes(u.mem_read(0x20044d70,12)).hex(),R0=hex(u.reg_read(UC_ARM_REG_R0)),R4=hex(u.reg_read(UC_ARM_REG_R4))))
        """
 s=replace(s,'if pc==0x080292f8:',hook+'if pc==0x080292f8:')
 s=replace(s,"CAPTURE(locals());result['SPI2']", "CAPTURE(locals());result['USB']=usb.summary();result['SPI2']")
 (O/'selected-startup.py.txt').write_text(s)
 sys.argv=[__file__,'--peripheral-completion-model','--valid-bpb','--case=continuity']
 ns=dict(__file__=str(O/'startup.py'),__name__='__main__',SCENARIO_OUT=O,PROJECT_ROOT=R,IMAGE=IMAGE,USBInit=USBInit,SPI2=SPI2,BootPeer=lambda:BootPeer(lambda m:NativeDSP(m,O)),CAPTURE=CAPTURE,observe=observe,invalid=invalid,UC_HOOK_MEM_INVALID=UC_HOOK_MEM_INVALID,CANDIDATE_SHA=c['BIN_sha256'])
 exec(compile(s,str(O/'selected-startup.py.txt'),'exec'),ns)
 e=CAPTURED['e'];peer=CAPTURED['peer'];u=e.uc
 (O/'frontier-sram.bin').write_bytes(bytes(u.mem_read(0x20000000,0x50000)))
 (O/'usb-evidence.json').write_text(json.dumps(CAPTURED['usb'].summary(),indent=2)+'\n')
 (O/'shi-summary.json').write_text(json.dumps(dict(jobs=[hex(w) for w in peer.jobs],DMAs=peer.dmas,log=peer.log),indent=2)+'\n')
 (O/'allocation-returns.json').write_text(json.dumps(dict(entries=ALLOC,pending=PENDING),indent=2)+'\n')
 (O/'fault-and-R9.json').write_text(json.dumps(dict(faults=FAULTS,R9_transitions=SB),indent=2)+'\n')
 (O/'registers.json').write_text(json.dumps({n:hex(u.reg_read(getattr(ARM,'UC_ARM_REG_'+n))) for n in ['R0','R1','R2','R3','R4','R5','R6','R7','R8','R9','R10','R11','R12','SP','LR','CONTROL','MSP','PSP','IPSR','XPSR']},indent=2)+'\n')
 peer.close();x=json.loads((O/'continuity.json').read_text());print(json.dumps(dict(frontier=x['frontier'],record=x['record'],heap=x['heap_cursor'],USB_reads=len(x['USB']['trace'])),indent=2))
if __name__=='__main__':main()
