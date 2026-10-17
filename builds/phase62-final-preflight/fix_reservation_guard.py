"""Minimal guard-only correction after persisted native counterexample.
Preserves Phase61 files. Builds a distinct, explicitly unqualified candidate.
No device, MIDI or uploader imports. No architecture/schema/transport redesign.
"""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase61-final-geometry-gated-candidate'
sys.path.insert(0,str(R/'builds/phase42-exact-rdiag-integration/source/tools'))
from thumb import *
import ct_fw
sys.path.insert(0,str(R/'builds/phase43-hardware-test-candidate'))
from independent_validate import decode,crc
BASE=0x08010000;ENTRY=0x0806d510;STUB=0x0806d800;CONTINUE=0x0806d518;OUT=0x0806d698
S=0x20044d70;LIMIT=0x20002b44
NAME='circuittracks-geometry-gated-nor-reservation-fix-unqualified'
def sha(b):return hashlib.sha256(b).hexdigest()
def imm(a,r,v):a.emit(movw,r,v&65535);a.emit(movt,r,v>>16)
def main():
 failure=json.loads((O/'original-reservation-tests.json').read_text());assert not failure['passed']
 raw=(P/'circuittracks-final-geometry-gated-nor-test.syx').read_bytes();old,_,_=decode(raw)
 assert sha(raw)=='fe36e18bc83448b0e25cc21b8323e0e64e153f6e04abc042546f4a20e83731d3'
 assert sha(old)=='af5b62e371c1f9e6972b573e766088e54da6fadfcba911e62f25bd0edb0c763f'
 assert old[ENTRY-BASE:ENTRY-BASE+8]==movw(4,S&65535)+movt(4,S>>16)
 a=Asm(STUB);imm(a,4,S);imm(a,1,LIMIT);a.emit(ldr_imm,2,1,0);a.emit(cmp_reg,2,4);a.emit(b_cond,'reject','ne')
 a.emit(ldr_imm,2,1,4);a.emit(cmp_reg,2,4);a.emit(b_cond,'reject','hi');a.emit(b_w,CONTINUE)
 a.label('reject');a.emit(b_w,OUT);body=a.assemble()[0]
 assert old[STUB-BASE:STUB-BASE+len(body)]==b'\xff'*len(body)
 fixed=bytearray(old);fixed[ENTRY-BASE:ENTRY-BASE+4]=b_w(ENTRY,STUB);fixed[STUB-BASE:STUB-BASE+len(body)]=body
 # A new marker within the38-byte native updater comparison prevents silent
 # no-op versus Phase61. It does not claim this new image's install is validated.
 fixed[0x1e8:0x1ee]=b'N62RSV';fixed=bytes(fixed);syx=ct_fw.encode(fixed)
 decoded,_,details=decode(syx);assert decoded==fixed and crc(decoded)==ct_fw.crc32_mpeg2(fixed)
 (O/(NAME+'.bin')).write_bytes(fixed);(O/(NAME+'.syx')).write_bytes(syx)
 diff=[];start=None
 for i in range(len(fixed)+1):
  changed=i<len(fixed) and old[i]!=fixed[i]
  if changed:assert 0x1e8<=i<0x1ee or ENTRY-BASE<=i<ENTRY-BASE+4 or STUB-BASE<=i<STUB-BASE+len(body)
  if changed and start is None:start=i
  if not changed and start is not None:diff.append(dict(start=hex(BASE+start),end_exclusive=hex(BASE+i),bytes=i-start));start=None
 from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
 md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);ins=list(md.disasm(body,STUB));assert sum(i.size for i in ins)==len(body)
 (O/'reservation-guard.asm').write_text('\n'.join(f'{i.address:08X}: {i.mnemonic} {i.op_str}' for i in ins)+'\n')
 result=dict(confidence='PROVEN',designation='UNQUALIFIED CORRECTION — DO NOT FLASH',candidate=NAME,BIN_bytes=len(fixed),BIN_sha256=sha(fixed),SYX_bytes=len(syx),SYX_sha256=sha(syx),CRC=f'{crc(fixed):08X}',application_end_exclusive=hex(BASE+len(fixed)),headroom_bytes=0x70000-len(fixed),marker='N62RSV',original_BIN_sha256=sha(old),original_SYX_sha256=sha(raw),phase61_hardware_designation_withdrawn=True,guard_entry=hex(ENTRY),guard_address=hex(STUB),guard_bytes=len(body),checks=['heap limit exactly20044D70','heap cursor<=20044D70'],reject='existing restore tail without any private-record read/store',diff_ranges=diff,changed_bytes=sum(x['bytes'] for x in diff),independent_decode=details,firmware_architecture_changed=False,full_preflight_complete=False,hardware_access=False,MIDI_ports_opened=0)
 (O/'correction-identity.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
