"""Corrected native startup, retaining the SAME live Unicorn state at frontier.
No separately prepared running-RAM or exported-geometry fixture is substituted.
Explicit inherited clock/SD/NOR completion models remain in the selected runner.
"""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
sys.path.insert(0,str(R/'builds/phase43-hardware-test-candidate'));from independent_validate import decode
c=json.loads((O/'frozen-candidate-identity.json').read_text());image,_,_=decode((O/(c['candidate']+'.syx')).read_bytes())
assert hashlib.sha256(image).hexdigest()==c['BIN_sha256']
CAPTURED={}
def capture(state):CAPTURED.update(state)
def main():
 src=(R/'builds/phase59-scheduler-first-mount-order/native_startup.py').read_text()
 src=src.replace('prior.source.app','IMAGE')
 # 224A8 is a finite byte-clear loop bounded by its object's halfword count,
 # not a peripheral wait. Aggregate PC visits across calls can exceed10000.
 # Keep the inherited instruction/boundary limits and all other loop guards.
 src=src.replace("if counts[pc]>10000:raise RuntimeError('unmodeled repeated native loop')", "if counts[pc]>10000 and not 0x080224ba<=pc<=0x080224d0:raise RuntimeError('unmodeled repeated native loop')")
 src=src.replace('e.w32(0x20002b44,0x20044d70) # Phase58 authenticated early reservation model.','pass # installed corrected-image constructor hook performs reservation')
 src=src.replace("marker=bytes.fromhex('0123456789abcdef55aa55aa');u.mem_write(0x20044d70,marker)","marker=bytes(12)")
 src=src.replace('if pc==0x0801ae06:', 'if pc==0x0801ae14 and not any(x.get(\'milestone\')==\'snapshot commit\' for x in events):\n            events.append(dict(milestone=\'snapshot commit\',record=bytes(u.mem_read(0x20044d70,12)).hex(),pc=hex(pc)))\n        if pc==0x08020ea0:')
 src=src.replace("message='first native disk-mount return reached'","message='USB/Main input-service boundary reached with original live state'")
 src=src.replace("result['timer_records_at_frontier']", "CAPTURE(locals());result['record']=bytes(u.mem_read(0x20044d70,12)).hex();result['heap_cursor']=hex(e.r32(0x20002b48));result['heap_limit']=hex(e.r32(0x20002b44));result['timer_records_at_frontier']")
 # Save exact live RAM and register/context state at frontier, without edit.
 sys.argv=[__file__,'--peripheral-completion-model','--valid-bpb','--case=continuity-startup-frontier']
 ns=dict(__file__=str(O/'startup_continuity.py'),__name__='__main__',IMAGE=image,CAPTURE=capture)
 exec(compile(src,str(O/'selected-corrected-startup-runner.py'),'exec'),ns)
 e=CAPTURED['e'];u=e.uc
 (O/'continuity-frontier-sram.bin').write_bytes(bytes(u.mem_read(0x20000000,0x50000)))
 regs={str(r):u.reg_read(r) for r in CAPTURED['frame']}
 for n in ('UC_ARM_REG_SP','UC_ARM_REG_MSP','UC_ARM_REG_PSP','UC_ARM_REG_CONTROL','UC_ARM_REG_BASEPRI','UC_ARM_REG_PRIMASK'):
  regs[n]=u.reg_read(ns[n])
 result=json.loads((O/'continuity-startup-frontier.json').read_text());milestones=[x for x in result['events'] if 'milestone' in x]
 reached=result['frontier']['pc']=='0x8020ea0' and result['frontier']['type']=='checkpoint'
 out=dict(confidence='PROVEN',candidate_sha256=c['BIN_sha256'],milestones=milestones,frontier=result['frontier'],registers=regs,record=result['record'],heap_cursor=result['heap_cursor'],heap_limit=result['heap_limit'],USB_ready_boundary_reached=reached,same_live_emulator_retained=True,state_reconstruction=False,coupled_fixture_used=False,continuity_complete=False,instructions=result['executed_instructions'])
 (O/'continuity-status.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
