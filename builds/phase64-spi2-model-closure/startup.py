"""Flattened inherited continuous runner, exact unchanged Phase63 image."""
from pathlib import Path
import sys,json,hashlib,textwrap
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase63-defect-closure'
sys.path.insert(0,str(R/'builds/phase43-hardware-test-candidate'));from independent_validate import decode
from spi2_model import SPI2
from dsp_peer import BootPeer
c=json.loads((P/'development-identity.json').read_text());IMAGE=decode((P/(c['candidate']+'.syx')).read_bytes())[0];assert hashlib.sha256(IMAGE).hexdigest()==c['BIN_sha256']
CAPTURED={}
def CAPTURE(x):CAPTURED.update(x)
def replace(s,a,b):
 assert a in s,a
 return s.replace(a,b,1)

HOOK='''
instruction_clock[0]+=1
io_count=len(spi.tx_bytes)+len(spi.rx_bytes)
if io_count!=io_progress[0]:io_progress[:]=[io_count,instruction_clock[0]]
if pc==0x080292f8:peer.arm_write(u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2))
if pc==0x08029344:peer.arm_read(u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1))
if pc==0x08029190:peer.command=True;peer.core=u.reg_read(UC_ARM_REG_R0)
if pc==0x080291a2:peer.command=False;peer.core=u.reg_read(UC_ARM_REG_R0)
if pc==0x080291b8:peer.core=u.reg_read(UC_ARM_REG_R0)
if pc==0x0803baa2:peer.word(u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_LR)&~1)
if pc in (0x0801e2fa,0x0801e2f8):adc_stage[0]=0
if pc==0x0801e2da and adc_events[0]<128 and adc_stage[0]<2 and not u.reg_read(UC_ARM_REG_IPSR):
 action[0]=('adc-conversion' if adc_stage[0]==0 else 'adc-dma',pc);adc_stage[0]+=1;u.emu_stop();return
if pc==0x08057560 and u.reg_read(UC_ARM_REG_IPSR)==30:
 action[0]=('popr4return',pc);u.emu_stop();return
if pc==0x08023414 and not u.reg_read(UC_ARM_REG_IPSR) and e.r32(0x40026058)&1:
 action[0]=('spi2-dma',pc);u.emu_stop();return
if instruction_clock[0]>=next_tick[0] and not u.reg_read(UC_ARM_REG_IPSR) and not u.reg_read(UC_ARM_REG_PRIMASK) and not u.reg_read(UC_ARM_REG_BASEPRI):
 next_tick[0]=instruction_clock[0]+10000;action[0]=('early-tick',pc);u.emu_stop();return
if pc==0x0801ae14:
 events.append(dict(milestone='mount return',object=hex(u.reg_read(UC_ARM_REG_R4)),record=bytes(u.mem_read(0x20044d70,12)).hex(),index=instruction_clock[0]))
'''
IRQ='''
elif kind=='adc-conversion':
 e.w32(0x40012000,e.r32(0x40012000)|2);events.append(dict(event='synthetic ADC EOC actual IRQ34'));pc=exception_enter(34,value)
elif kind=='adc-dma':
 dest=e.r32(0x4002641c);count=e.r32(0x40026414);assert e.r32(0x40026410)&1 and 0<count<=192 and 0x20000000<=dest<0x20050000-count*2
 u.mem_write(dest,struct.pack('<H',1024)*count);e.w32(0x40026400,e.r32(0x40026400)|32);adc_events[0]+=1;pc=exception_enter(72,value)
elif kind=='spi2-dma':
 e.w32(0x40026070,e.r32(0x40026070)&~1);e.w32(0x40026074,0);stream=0x40026058;dest=e.r32(stream+12);count=e.r32(stream+4)
 width=1<<((e.r32(stream)>>13)&3);extent=count*width if e.r32(stream)&1024 else width
 assert 0<count<=512 and 0x20000000<=dest<0x20050000-extent
 u.mem_write(dest,bytes(extent));e.w32(stream,e.r32(stream)&~1);e.w32(stream+4,0);e.w32(0x40026000,e.r32(0x40026000)|(1<<27));pc=exception_enter(30,value)
elif kind=='popr4return':
 a=u.reg_read(UC_ARM_REG_MSP);r4,exc=struct.unpack('<2I',bytes(u.mem_read(a,8)));u.reg_write(UC_ARM_REG_R4,r4);u.reg_write(UC_ARM_REG_MSP,a+8);pc=exception_leave(exc)
'''
def source():
 s=(R/'builds/phase59-scheduler-first-mount-order/native_startup.py').read_text().replace('prior.source.app','IMAGE')
 s=replace(s,'e=prior.Physical();u=e.uc',"e=prior.Physical();u=e.uc;peer=BootPeer();spi=SPI2(response=peer.byte);spi.bind(u);u.mem_map(0x1ff0f000,0x1000);u.mem_write(0x1ff0f44a,struct.pack('<H',1500))")
 s=replace(s,'e.w32(0x20002b44,0x20044d70) # Phase58 authenticated early reservation model.','pass # actual installed constructor reserves record')
 s=replace(s,"marker=bytes.fromhex('0123456789abcdef55aa55aa');u.mem_write(0x20044d70,marker)","marker=bytes(12)")
 s=replace(s,'    marker=bytes(12)',"    prefix_record=bytes(u.mem_read(0x20044d70,12)).hex();marker=bytes(12)")
 s=replace(s,'calls=[];events=[];last=[]',"calls=[];events=[dict(milestone='reset prefix before constructors',record=prefix_record),dict(milestone='constructors complete',record=bytes(u.mem_read(0x20044d70,12)).hex(),heap_cursor=hex(e.r32(0x20002b48)),heap_limit=hex(e.r32(0x20002b44)))];last=[]")
 s=replace(s,"event='first scheduler architectural launch boundary',current=", "event='first scheduler architectural launch boundary',record=bytes(u.mem_read(0x20044d70,12)).hex(),current=")
 s=replace(s,'ins=cache[pc]','ins=cache[pc]\n'+textwrap.indent(HOOK.strip(),'        '))
 s=replace(s,"watch.update({","watch.update({0x0801cfa4:'allocation request',0x0801d7d8:'bounded allocator',")
 s=replace(s,'injected_tick=False;injected_queue=False','injected_tick=False;injected_queue=False;instruction_clock=[0];next_tick=[120000];adc_stage=[0];adc_events=[0];io_progress=[0,0]')
 s=replace(s,'if pc==0x0805999a and u.reg_read(UC_ARM_REG_IPSR)==15:', 'if pc in (0x0805999a,0x080574e6) and u.reg_read(UC_ARM_REG_IPSR) in (15,34):')
 s=replace(s,'if pc==0x0801ae06:','if pc==0x08020ea0:')
 s=s.replace("message='first native disk-mount return reached'","message='Main input-service boundary; USB configured readiness not assumed'")
 s=replace(s,"            elif kind=='early-tick':",textwrap.indent(IRQ.strip(),'            ')+"\n            elif kind=='early-tick':")
 s=replace(s,"if counts[pc]>10000:raise RuntimeError('unmodeled repeated native loop')","if counts[pc]>10000 and not 0x080224ba<=pc<=0x080224d0 and instruction_clock[0]-io_progress[1]>20000:raise RuntimeError('unmodeled repeated native loop without transfer progress')")
 s=s.replace('range(300)','range(2000)')
 s=replace(s,"    result['switches']=switches", "    CAPTURE(locals());result['SPI2']=spi.summary();result['peer_log']=peer.log;result['candidate_sha256']=CANDIDATE_SHA;result['record']=bytes(u.mem_read(0x20044d70,12)).hex();result['heap_cursor']=hex(e.r32(0x20002b48));result['heap_limit']=hex(e.r32(0x20002b44));result['switches']=switches")
 return s
def main():
 s=source();(O/'selected-startup.py.txt').write_text(s)
 sys.argv=[__file__,'--peripheral-completion-model','--valid-bpb','--case=continuity']
 ns=dict(__file__=str(O/'startup.py'),__name__='__main__',IMAGE=IMAGE,SPI2=SPI2,BootPeer=BootPeer,CAPTURE=CAPTURE,CANDIDATE_SHA=c['BIN_sha256']);exec(compile(s,str(O/'selected-startup.py.txt'),'exec'),ns)
 x=json.loads((O/'continuity.json').read_text());e=CAPTURED['e'];u=e.uc
 spi=CAPTURED['spi']
 (O/'frontier-sram.bin').write_bytes(bytes(u.mem_read(0x20000000,0x50000)))
 (O/'spi2-trace.json').write_text(json.dumps(x['SPI2'],indent=2)+'\n')
 peer=CAPTURED['peer'];(O/'peer-memory.json').write_text(json.dumps(dict(memory={k:{hex(a):hex(v) for a,v in m.items()} for k,m in peer.memory.items()},log=peer.log),indent=2)+'\n')
 print(json.dumps(dict(frontier=x['frontier'],state=x['record'],heap=x['heap_cursor'],SPI2_polls=spi.now,SPI2_tx_bytes=len(spi.tx_bytes)),indent=2))
if __name__=='__main__':main()
