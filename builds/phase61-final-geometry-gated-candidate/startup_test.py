"""Existing architectural startup runner, new SYX-derived bytes and installed hooks.
Only peripheral predicates listed by Phase59 are supplied. No hardware I/O.
"""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
sys.path.insert(0,str(R/'builds/phase43-hardware-test-candidate'))
from independent_validate import decode
image,_,_=decode((O/'circuittracks-final-geometry-gated-nor-test.syx').read_bytes())
src=(R/'builds/phase59-scheduler-first-mount-order/native_startup.py').read_text()
src=src.replace('prior.source.app','IMAGE')
src=src.replace('e.w32(0x20002b44,0x20044d70) # Phase58 authenticated early reservation model.','pass # reservation now executes in the installed constructor hook')
src=src.replace("marker=bytes.fromhex('0123456789abcdef55aa55aa');u.mem_write(0x20044d70,marker)","marker=bytes(12)")
src=src.replace('if pc==0x0801ae06:', 'if pc==0x0801ae14:')
src=src.replace('if u.reg_read(UC_ARM_REG_PC)==0x0801ae06 else None','if u.reg_read(UC_ARM_REG_PC)==0x0801ae14 else None')
src=src.replace("result['timer_records_at_frontier']", "result['control']=hex(e.r32(0x20044d70));result['compact_geometry']=bytes(u.mem_read(0x20044d74,8)).hex();result['heap_limit']=hex(e.r32(0x20002b44));result['timer_records_at_frontier']")
sys.argv=[__file__,'--peripheral-completion-model','--valid-bpb','--case=candidate-startup']
ns=dict(__file__=str(O/'startup_test.py'),__name__='__main__',IMAGE=image)
exec(compile(src,str(O/'startup-runner-selected-image.py'),'exec'),ns)
r=json.loads((O/'candidate-startup.json').read_text())
assert r['frontier']['type']=='checkpoint' and r['frontier']['pc']=='0x801ae14',r['frontier']
assert r['control']=='0x11' and r['heap_limit']=='0x20044d70',r['control']
assert r['fs_type']==2 and not any(x['kind'] in ('NOR program','NOR erase','NOR chip erase') for x in r['operations'])
print('Installed native startup and snapshot PASS',r['compact_geometry'])
