"""Read-only byte sources; phase33 outputs only. No firmware files or ports."""
from pathlib import Path
import sys,json,struct,hashlib
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'builds/phase30-chunked-storage'))
from environment import Physical,REF,PUBLISHED,STOCK,md
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROM=(REF/'ctre/Firmware-Analysis/dumpCT_flash_0x08000000.bin').read_bytes()
def sha(b):return hashlib.sha256(b).hexdigest()
def candidate(e):
 import stream
 u=e.uc;end=stream.TEMPLATE+232;size=end-0x08010000;base=len(PUBLISHED)
 u.mem_write(0x08010000+base,b'\xff'*(size-base))
 u.mem_write(0x0807a414,(R/'builds/phase27-qspi-read/arm-diagnostic.fragment.bin').read_bytes())
 u.mem_write(0x0807a59e,stream.bl(0x0807a59e,stream.COMMAND))
 for a,fn in ((stream.COMMAND,stream.command),(stream.CRC_UPDATE,stream.crc_update),(stream.DRAIN,stream.drain)):u.mem_write(a,fn())
 sys.path.insert(0,str(R/'builds/phase27-qspi-read'));from protocol import request
 u.mem_write(stream.TEMPLATE,request(0))
 plan=json.loads((R/'builds/phase27-qspi-read/patch-plan.json').read_text())
 for key in ('hook','installation_marker'):
  p=plan[key];u.mem_write(int(p['address'],16),bytes.fromhex(p['after']))
 return bytes(u.mem_read(0x08010000,size))
def dump(a,n):
 raw=ROM[a-0x08000000:a-0x08000000+n] if a<0x08010000 else PUBLISHED[a-0x08010000:a-0x08010000+n]
 lines=[]
 for i in md.disasm(raw,a):
  suffix=''
  for op in i.operands:
   if op.type==3 and op.mem.base==11:
    at=((i.address+4)&~3)+op.mem.disp
    b=ROM[at-0x08000000:at-0x08000000+4] if at<0x08010000 else PUBLISHED[at-0x08010000:at-0x08010000+4]
    if len(b)==4:suffix=f' ; [{at:08x}]={int.from_bytes(b,"little"):08x}'
  lines.append(f'{i.address:08x}: {i.mnemonic:8} {i.op_str}'+suffix)
 (O/f'{a:08x}.asm').write_text('\n'.join(lines)+'\n');return '\n'.join(lines)
if __name__=='__main__':
 print('Boot vectors',struct.unpack_from('<II',ROM));print('App vectors',struct.unpack('<II',PUBLISHED[:8]))
 for x in sys.argv[1:]:a,n=x.split(':');print(dump(int(a,16),int(n,16)))
