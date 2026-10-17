from inspect_code import *
s=authentic_session();e=s.e
def record(a,n):return dict(address=hex(a),words={hex(i):hex(e.r32(a+i)) for i in range(0,n,4)})
result={}
ad=w(0x08039108)
result['update_bundles']=[record(e.r32(ad+4*i),16) for i in range(4)]
result['update_bundle_interface']=record(e.r32(e.r32(ad)+4),48)
k=w(0x0801cf90);t=e.r32(k+0x64)
result['kernel']=record(k,0x84);result['captured_current_thread']=record(t,0x60)
result['Main_stack_base']=hex(e.r32(t+0x30));result['Main_stack_top_candidate']=hex(t&~7)
base=e.r32(t+0x30);buf=bytes(e.uc.mem_read(base,(t&~7)-base));first=next((i for i,v in enumerate(buf) if v!=0xa5),len(buf))
result['captured_Main_watermark']=dict(first_non_A5_offset=first,dirty_span_bytes=len(buf)-first,meaning='Single early snapshot; not worst-case, not proof of untouched words after coincidental A5 writes')
router=e.r32(w(0x0801edd0));result['router']=record(router,0x28)
ports=e.r32(router+0x14);n=e.r8(router+0x18)
result['ports']=[]
for i in range(n):
 p=e.r32(ports+4*i);v=e.r32(p)
 result['ports'].append(dict(index=i,object=record(p,48),methods=record(v,24)))
ctx=e.r32(e.r32(e.r32(0x20006968)+4)+4)
result['QSPI_context']=record(ctx,0x38)
result['controller']=record(e.r32(ctx),0x28)
for name in ['0x18','0x1c','0x20','0x24']:
 p=e.r32(ctx+int(name,16))
 if 0x20000000<=p<0x20050000:result['context_pointer_'+name]=record(p,24)
(O/'object-evidence.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
