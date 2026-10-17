"""Phase64 continuous ARM runner plus bounded SHI wire/DMA recipient model."""
from pathlib import Path
import sys,json,hashlib,importlib.util,textwrap,shutil
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
spec=importlib.util.spec_from_file_location('phase64_startup',R/'builds/phase64-spi2-model-closure/startup.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
from dsp_peer import BootPeer
from native_dsp import NativeDSP
from spi2_model import SPI2
from unicorn.arm_const import UC_ARM_REG_PC
CAPTURED={}
def CAPTURE(x):CAPTURED.update(x)
def replace(s,a,b):
 assert a in s,a
 return s.replace(a,b,1)
def main():
 incomplete='--incomplete' in sys.argv
 output=O/'incomplete-transfer' if incomplete else O;output.mkdir(exist_ok=True)
 if incomplete:
  for n in ('loaded-core0.be24','loaded-core1.be24'):shutil.copyfile(O/n,output/n)
 s=old.source()
 s=replace(s,'OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]','OUT=SCENARIO_OUT;ROOT=PROJECT_ROOT')
 # Observe and deliver actual TX bytes before the inherited DMA completion IRQ.
 a="e.w32(0x40026070,e.r32(0x40026070)&~1);e.w32(0x40026074,0);stream=0x40026058;dest=e.r32(stream+12);count=e.r32(stream+4)"
 b="""txcr=e.r32(0x40026070);txcount=e.r32(0x40026074);txsrc=e.r32(0x4002607c)
             assert 0<txcount<=65536 and (txcr>>13)&3==0
             txdata=bytes(u.mem_read(txsrc,txcount)) if txcr&1024 else bytes(u.mem_read(txsrc,1))*txcount
             rxdata=peer.dma(txdata);peer.dmas[-1].update(source=hex(txsrc),TX_CR=hex(txcr),index=instruction_clock[0])
             e.w32(0x40026070,txcr&~1);e.w32(0x40026074,0);stream=0x40026058;dest=e.r32(stream+12);count=e.r32(stream+4)"""
 s=replace(s,a,b)
 if incomplete:
  s=replace(s,'io_progress=[0,0]',"io_progress=[0,0];fault_started=[False];fault_visits=[0]")
  s=replace(s,"if pc==0x08023414 and not u.reg_read(UC_ARM_REG_IPSR) and e.r32(0x40026058)&1:","if fault_started[0] and pc==0x08023414:\n         fault_visits[0]+=1\n         if fault_visits[0]>=256:raise RuntimeError('bounded incomplete coefficient DMA: native completion wait persists')\n        if pc==0x08023414 and not fault_started[0] and not u.reg_read(UC_ARM_REG_IPSR) and e.r32(0x40026058)&1:")
  s=replace(s,'rxdata=peer.dma(txdata);',"if peer.native and peer.width==2 and not peer.command and txcount==512:\n              peer.dma(txdata[:-2]);peer.dmas[-1].update(source=hex(txsrc),expected_bytes=512,remaining=2,completion_IRQ_delivered=False);e.w32(0x40026074,2);e.w32(0x4002605c,2);fault_started[0]=True;pc=value;continue\n             rxdata=peer.dma(txdata);")
 s=replace(s,'u.mem_write(dest,bytes(extent));e.w32(stream',"assert count==txcount and width==1\n             u.mem_write(dest,rxdata if e.r32(stream)&1024 else rxdata[-1:]);e.w32(stream")
 # Increase observation bound to cover genuine long main-loop/native DSP uploads.
 s=replace(s,'range(2000)','range(10000)')
 s=replace(s,"if counts[pc]>10000 and not 0x080224ba<=pc<=0x080224d0 and instruction_clock[0]-io_progress[1]>20000:","if counts[pc]>10000 and last.count(pc)>5 and not 0x080224ba<=pc<=0x080224d0 and instruction_clock[0]-io_progress[1]>1000000:")
 (output/'selected-startup.py.txt').write_text(s)
 sys.argv=[__file__,'--peripheral-completion-model','--valid-bpb','--case=continuity']
 ns=dict(__file__=str(O/'startup.py'),__name__='__main__',SCENARIO_OUT=output,PROJECT_ROOT=R,IMAGE=old.IMAGE,SPI2=SPI2,BootPeer=lambda:BootPeer(lambda m:NativeDSP(m,output)),CAPTURE=CAPTURE,CANDIDATE_SHA=old.c['BIN_sha256'])
 exec(compile(s,str(output/'selected-startup.py.txt'),'exec'),ns)
 e=CAPTURED['e'];peer=CAPTURED['peer'];u=e.uc
 (output/'frontier-sram.bin').write_bytes(bytes(u.mem_read(0x20000000,0x50000)))
 (output/'shi-evidence.json').write_text(json.dumps(dict(log=peer.log,DMAs=peer.dmas,jobs=[hex(w) for w in peer.jobs],width=peer.width,native_turns=peer.native.turns if peer.native else 0),indent=2)+'\n')
 if incomplete:
  assert CAPTURED['fault_started'][0] and CAPTURED['fault_visits'][0]==256
  (output/'negative-result.json').write_text(json.dumps(dict(confidence='PROVEN',passed=True,native_wait_visits=256,PC=hex(u.reg_read(UC_ARM_REG_PC)),TX_remaining=e.r32(0x40026074),RX_remaining=e.r32(0x4002605c),TX_EN=e.r32(0x40026070)&1,RX_EN=e.r32(0x40026058)&1,record=bytes(u.mem_read(0x20044d70,12)).hex(),mailbox_jobs=[hex(w) for w in peer.jobs],completion_delivered=False,scope='same continuous reset prefix, first512-byte coefficient DMA truncated after510; no selector0 issued'),indent=2)+'\n')
 peer.close()
 x=json.loads((output/'continuity.json').read_text());print(json.dumps(dict(frontier=x['frontier'],record=x['record'],heap=x['heap_cursor'],jobs=len(peer.jobs),DMAs=len(peer.dmas)),indent=2))
if __name__=='__main__':main()
