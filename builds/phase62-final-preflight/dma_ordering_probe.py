"""Adversarial TCF-before-DMA-release probe, NOT an asserted hardware ordering.
Tests the requested software ownership invariant without assuming normal DMA
auto-disable before the QSPI completion IRQ, which prior normal models supplied.
"""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));import stack_dma_tests as S
def main():
 m=S.Measured();m.start()
 for _ in range(1500):
  if m.active and m.active['chunk']==8 and not m.active['issued']:break
  m.tick()
 else:raise AssertionError('last pending DMA not reached')
 buf=m.rawbuf;before=dict(DMA_EN=m.e.r32(0x400264b8)&1,NDTR=m.e.r32(0x400264bc),Main_returned=m.done)
 # Keep DMA EN/NDTR outstanding while delivering the real native QSPI IRQ.
 # Bytes are supplied only to let CPU CRC/packet code continue; they are
 # synthetic and not claimed immutable/completed physical DMA output.
 m.u.mem_write(buf,m.payload[23+7*64:23+8*64]);m.e.w32(0xa0001008,2);m.active['issued']=True
 m.run_cpu('IRQ',0x080573e0,SP=0x20050000,LR=0x0807ff01)
 error=None
 try:m.finish(1500)
 except Exception as ex:error=repr(ex)
 after=dict(DMA_EN=m.e.r32(0x400264b8)&1,NDTR=m.e.r32(0x400264bc),DMA_destination=hex(m.e.r32(0x400264c4)),raw_buffer=hex(buf),Main_returned=m.done,request_active=m.e.r32(m.wrapper+16),semaphore=m.e.r8(m.backend+8),record=bytes(m.u.mem_read(0x20044d70,12)).hex())
 violation=bool(m.done and after['DMA_EN'] and after['DMA_destination']==hex(buf))
 result=dict(confidence='PROVEN',candidate_sha256=S.c['BIN_sha256'],software_no_return_invariant=not violation,before=before,after=after,error=error,scope='Adversarial peripheral register ordering; physical possibility/timing UNKNOWN. Unlike the normal model, does not clear DMA EN or NDTR before native TCF IRQ',actual_hardware_ordering_proven=False,hardware_access=False)
 (O/'dma-ordering-probe.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
