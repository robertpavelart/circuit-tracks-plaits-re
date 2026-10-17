"""Actual stock router/USB MIDI packetizer; modeled USB IN completion/OS tick.
No QSPI call, new diagnostic assembly, WinMM or physical USB activity.
"""
from inspect_code import *
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
P=R/'builds/phase27-qspi-read';sys.path.insert(0,str(P));from protocol import split_stream,Receiver
frames=list(split_stream((P/'synthetic-transcript.syx').read_bytes()))
class Sleep(Exception):pass
class Stalled(Exception):pass
def run(delay,disconnect=False):
 s=authentic_session();e=s.e;u=e.uc;router=e.r32(w(0x0801edd0));port=e.r32(e.r32(router+0x14));pipe=e.r32(port+0x14)
 iface=e.r32(pipe+4);stream=e.r32(iface+4);dev=e.r32(stream+0x10)
 e.uc.mem_write(dev+0x274,b'\3');e.uc.mem_write(stream+0xc,b'\0')
 assert e.r8(stream+0x1c)==1
 cap=int.from_bytes(u.mem_read(pipe+0x1e,2),'little');assert cap==64
 ticks=0;pending=None;tx=[];wait_calls=0;maxpending=0;canarybuf=e.r32(e.r32(pipe+0x18)+4)
 # Stock endpoint scratch has a separate 64-byte staging buffer. No ownership
 # is inferred beyond the producer's capacity and this bounded model.
 def ret(v=0):u.reg_write(UC_ARM_REG_R0,v);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR)|1)
 def h(u,pc,n,d):
  nonlocal ticks,pending,wait_calls,maxpending
  if pc==0x08024754:
   ptr=u.reg_read(UC_ARM_REG_R2);size=u.reg_read(UC_ARM_REG_R3)
   assert 0<size<=64 and size%4==0
   assert pending is None,'more than one modeled USB IN transfer'
   pending=(bytes(u.mem_read(ptr,size)),ticks+delay);maxpending=max(maxpending,size)
   ret(0)
  elif pc==0x0801be78:
   assert u.reg_read(UC_ARM_REG_R0)==1
   wait_calls+=1;raise Sleep()
  elif pc==0x0801b3b8:ret(0)
 u.hook_add(UC_HOOK_CODE,h)
 def completion():
  nonlocal ticks,pending
  ticks+=1
  if disconnect:
   u.mem_write(dev+0x274,b'\0');pending=None
   return
  if pending is not None and ticks>=pending[1]:
   b=pending[0];pending=None;tx.append(b)
   e.call(0x0801e624,stream,maxins=10000) # actual USB transfer-release callback
 def invoke(fn,*args):
  for i,v in enumerate(args):u.reg_write(UC_ARM_REG_R0+i,v)
  u.reg_write(UC_ARM_REG_SP,0x2006f000);u.reg_write(UC_ARM_REG_LR,0x0807ff01)
  pc=fn|1
  while True:
   try:
    u.emu_start(pc,0xffffffff,count=1000000)
    assert u.reg_read(UC_ARM_REG_PC)==0x0807ff00
    return
   except Sleep:
    ctx=u.context_save();completion();u.context_restore(ctx)
    if ticks>100:raise Stalled()
    # Explicit OS delay endpoint model; the caller actually requested sleep(1).
    u.reg_write(UC_ARM_REG_R0,0);pc=u.reg_read(UC_ARM_REG_LR)|1
 def service():
  completion();invoke(0x08035a50,port)
 status='router returned after disconnect; no capture' if disconnect else 'completed'
 try:
  for f in frames:
   u.mem_write(0x20060100,f);u.mem_write(0x20060000,struct.pack('<II',0x20060100,len(f)))
   invoke(0x08020c90,router,1,0x20060000)
  for _ in range(100):
   countp=e.r32(port+0x10)
   left=(int.from_bytes(u.mem_read(countp+2,2),'little')-int.from_bytes(u.mem_read(countp,2),'little'))&65535
   if not left and pending is None:break
   service()
  else:raise Stalled()
 except Stalled:status='no completion within 101 modeled ticks; not success'
 raw=b''.join(tx);decoded=bytearray()
 for at in range(0,len(raw),4):
  packet=raw[at:at+4];cin=packet[0]&15;n={4:3,5:1,6:2,7:3}.get(cin)
  assert n is not None
  decoded+=packet[1:1+n]
 if not disconnect and delay<1000:
  assert bytes(decoded)==b''.join(frames)
  r=Receiver(39)
  for f in split_stream(decoded):r.accept(f)
  assert r.result()==(P/'synthetic-data.bin').read_bytes()
 return dict(delay_ticks_per_USB_completion=delay,disconnect=disconnect,status=status,ticks=ticks,
  actual_sleep_1_calls=wait_calls,sysex_bytes=len(decoded),USB_MIDI_bytes=len(raw),USB_transfers=len(tx),
  USB_staging_capacity=cap,max_USB_IN_inflight_bytes=maxpending,max_inflight_transfers=1,
  model='USB IN completion and OS sleep ticks modeled; actual router/packetizer executed; ticks are not hardware measurements')
results=[run(1),run(3),run(1000),run(1,True)]
(O/'midi-schedule-result.json').write_text(json.dumps(dict(confidence='PROVEN',scope='bounded scheduler model, no audio workload',cases=results,hardware_latency='UNKNOWN'),indent=2)+'\n')
print(json.dumps(results,indent=2))
