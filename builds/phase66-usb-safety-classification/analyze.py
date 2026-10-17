from pathlib import Path
import json,hashlib,struct,collections
O=Path(__file__).resolve().parent;R=O.parents[1];S=0x20044d70
load=lambda n:json.loads((O/n).read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
x=load('continuity.json');u=load('usb-evidence.json');a=load('allocation-returns.json');f=load('fault-and-R9.json')
assert f['faults'][-1]['address']=='0xe0001004' and f['faults'][-1]['PC']=='0x801d5a4'
assert f['faults'][-1]['registers']['R9']=='0xe0001004'
completed=[e for e in a['entries'] if 'returned' in e]
failed=[e for e in completed if int(e['returned'],16) in(0,0xffffffff) and e['bytes']>0]
overlap=[e for e in completed if 0<int(e['returned'],16)<0xffffffff and int(e['returned'],16)<S+12 and int(e['returned'],16)+e['bytes']>S]
counts=collections.Counter(e['kind'] for e in a['entries'])
large=sorted([e for e in completed if e['kind']=='bounded bump'],key=lambda e:e['bytes'],reverse=True)[:5]
usb_events=[e for e in x['events'] if e.get('event')=='USB init boundary']
alloc_requests=[e for e in x['operations'] if e['kind']=='allocation request']
assert int(u['registers']['0x40040008'],16)==1 and not u['endpoint_DMA']
assert not u['pending_reset_flush']
assert x['record']=='110000000180003480908f01'
assert not overlap
state_writes_after=[e for e in x['private_writes'] if 0x08038000<=int(e['pc'],16)<0x08039000 or 0x08048000<=int(e['pc'],16)<0x08048c00]
assert not state_writes_after
mutations_after_USB=[e for e in x['operations'] if e['instruction_index']>=4421081 and e['kind'] in ('wrapper program','wrapper erase','backend program','backend erase','NOR program','NOR erase','NOR chip erase','identity write')]
assert not mutations_after_USB
assert all(int(e['returned'],16)+e['bytes']<=S for e in completed if int(e['returned'],16)>0)
ram=(O/'frontier-sram.bin').read_bytes()
USB_handle=dict(base='0x20004d44',device_endpoints=struct.unpack_from('<I',ram,0x4d48)[0],DMA_enable=struct.unpack_from('<I',ram,0x4d54)[0],DMA_enable_offset='0x10: native by-value ABI field3; cfg begins at handle+4',PCD_state=ram[0x4d44+0x3bd])
assert USB_handle['DMA_enable']==0 and USB_handle['PCD_state']==1
preserved={}
for phase in ('phase63-defect-closure','phase64-spi2-model-closure','phase65-shi-model-closure'):
 d=R/'builds'/phase;rows=(d/'SHA256SUMS.txt').read_text().splitlines()
 for row in rows:
  h,n=row.split('  ',1);assert sha(d/n)==h,(phase,n)
 preserved[phase]=len(rows)
result=dict(confidence='PROVEN',generic_requests=len(alloc_requests),allocator_entry_counts=dict(counts),completed_returns=len(completed),pending_returns=len(a['pending']),positive_request_failures=failed,diagnostic_record_overlapping_returns=overlap,largest_bump_requests=large,heap_cursor=x['heap_cursor'],heap_limit=x['heap_limit'],record=x['record'],USB_init_events=usb_events,USB_handle=USB_handle,USB_global_interrupt_enabled=True,USB_controller_DMA_enabled=False,USB_endpoint_DMA_programming_seen=False,NOR_mutation_entries_after_USB=mutations_after_USB,USB_host_configured=False,raw_buffer_live=False,authorization_observed=False,raw_capture_entry_observed=False,new_frontier=f['faults'][-1],prior_manifests=preserved)
(O/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('generic_requests','allocator_entry_counts','completed_returns','pending_returns','positive_request_failures','diagnostic_record_overlapping_returns','largest_bump_requests','heap_cursor','prior_manifests')},indent=2))
