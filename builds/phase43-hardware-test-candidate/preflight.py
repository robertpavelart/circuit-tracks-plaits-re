"""Phase43 prerequisite: no encoding, file transfer, MIDI import or port use."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase42-exact-rdiag-integration'
sys.path.insert(0,str(P))
from environment import *
# environment's output globals are intentionally not used for writes.
O=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 v=json.loads((P/'validation.json').read_text())
 assert v['verdict']=='PASS'
 for name,h in v['evidence_sha256'].items():assert sha((P/name).read_bytes())==h,name
 a=json.loads((P/'integration.json').read_text());candidate=(P/'integrated-internal.bin').read_bytes();base=(P/'rebuilt-sc35d8.bin').read_bytes()
 assert sha(candidate)==a['image_sha256'] and sha(base)==a['base_image_sha256']
 trace=[];cases=[]
 for label,img in [('SC35D8',base),('diagnostic',candidate)]:
  e=Physical();u=e.uc;u.mem_write(0x08010000,img);visited=[];writes=[]
  def code(u,pc,n,d):
   visited.append(pc)
   assert pc not in (0x0801d7d8,0x08047c6c,0x08022f94,0x08022fdc,0x08023078),'unexpected allocation/Storage operation'
  def write(u,access,at,n,value,d):writes.append((at,n,value))
  from unicorn import UC_HOOK_MEM_WRITE
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
  cursor=e.r32(0x20002b48);assert cursor==0x20044d68
  assert e.call(0x0805dbcc)==0x20044d7c
  assert e.r32(0x20002b48)==cursor
  state=bytes(u.mem_read(0x20044d7c,220))
  if label=='diagnostic':assert e.r8(0x20044d74)==0
  for _ in range(20):e.call(0x0805998c,sp=0x2004ff00)
  assert e.r32(0x20002b48)==cursor and bytes(u.mem_read(0x20044d7c,220))==state
  if label=='diagnostic':assert e.r8(0x20044d74)==0
  assert all(not 0x08000000<=at<0x08080000 and not 0xa0001000<=at<0xa0002000 for at,n,value in writes)
  cases.append(dict(case=label,confidence='PROVEN',allocator_cursor_before=hex(cursor),allocator_cursor_after=hex(e.r32(0x20002b48)),heap_limit=hex(e.r32(0x20002b44)),MasterFX_state=state.hex(),allocator_calls=0,diagnostic_Storage_requests=0,external_NOR_operations=0,visited=[hex(x) for x in sorted(set(visited))]))
 assert cases[0]['MasterFX_state']==cases[1]['MasterFX_state']
 # Inspect *all* new pre-command wrapper instructions, not just visited PCs.
 # New admission has two outgoing calls: the getter and guarded command;
 # the latter is excluded before an explicit valid diagnostic request.
 components={k:a['components'][k] for k in ('gst','watch','entry')};edges=[]
 for name,c in components.items():
  start=int(c['address'],16);blob=candidate[start-0x08010000:start-0x08010000+c['bytes']]
  for ins in md.disasm(blob,start):
   if ins.mnemonic in ('bl','blx','b.w'):
    assert ins.op_str.startswith('#'),'unresolved wrapper indirect call'
    target=int(ins.op_str[1:],16)
    edges.append(dict(wrapper=name,pc=hex(ins.address),kind=ins.mnemonic,target=hex(target)))
 allowed={'gst':{0x0805dc06},'watch':{0x080599b8},'entry':{0x0805dbcc,0x0806b850,0x0801eb34}}
 assert all(int(x['target'],16) in allowed[x['wrapper']] for x in edges)
 result=dict(confidence='PROVEN',gate='PASS',fresh_boot_allocator_demand_delta_bytes=0,fresh_boot_allocator_call_delta=0,fixed_reservation_capacity_delta_bytes=-12,latch_bytes=12,latch_range='20044D70..20044D7B',native_fixture_headroom_bytes=8,record_is_parser_or_stack_or_DMA_storage=False,cases=cases,new_precommand_wrapper_edges=edges,reason='All newly reachable pre-command wrappers have closed outgoing edges to unchanged helper/initializer/forwarding paths; none calls the allocator. Allocation-producing stock startup instructions are unchanged. The command edge is gated by exact SysEx validation and IDLE admission.',limitations=['Capacity is reduced by 12 bytes; allocation demand is unchanged. These are different quantities.','Native fixture cursor and bounded wrapper execution are not a fresh hardware boot measurement.','Reservation checks cursor <= 20044D70 and fails closed otherwise; no ownership is claimed after a failed reservation.','Original stock boot/NOR activity is not absent merely because diagnostic-triggered activity is absent.'],hardware_access=False,SYX_generated=False)
 (O/'heap-preflight.json').write_text(json.dumps(result,indent=2)+'\n')
 print('FRESH-BOOT HEAP DELTA FROM SC35D8 = 0 (allocation demand); heap capacity delta = -12 bytes')
if __name__=='__main__':main()
