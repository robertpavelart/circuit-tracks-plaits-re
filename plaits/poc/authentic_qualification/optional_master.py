"""Additional real ARM mixer/send automation and active FX coverage."""
from environment import ROOT,MAN
from master_path import OUT
from live_master import Bridge
from pair_master import run
from unicorn.arm_const import UC_ARM_REG_R0
import json,math
def main():
 p=Bridge('mixer-send-FX-probe');s=p.s;e=s.e
 v={k:int(v,16) for k,v in MAN['report']['vcf20']['labels'].items()}
 g={k:int(v,16) for k,v in MAN['report']['sc17']['labels'].items()}
 listener=e.r32(e.r32(e.r32(0x200069e4)+0x10))+4
 e.call(g['c_gfst']);gf=e.uc.reg_read(UC_ARM_REG_R0)
 p.midi([0x90,60,100]);p.midi([0x91,67,100]);events=[]
 for b in range(64):
  s.events=[]
  if b%16==0:
   # Deliberate UI automation, after unmodified snapshot restoration has
   # already established audio. Values are inputs to the real parameter setter.
   for idx,val in [(46,41 if b%32==0 else 100),(47,100 if b%32==0 else 41),(50,32 if b%32==0 else 96),(51,96 if b%32==0 else 32),(11,41),(12,100)]:
    s.capture('actual project parameter automation',0x8034d92,listener,0x20,idx,val)
   s.capture('actual global parameter send',0x8028ef2)
  e.uc.mem_write(gf+6,bytes([0x3b if b>=32 else 0]));e.w32(0x2000081c,2000+2*b//3)
  s.capture('actual FX and retained-mode service',v['c_vtick']);events.append([b,s.events]);p.writes(s.events)
  p.send([f'BLOCK {b}','CORE 0','Y ffd 001000','PC 7000','STOP 7002','COUPLE','DUMPX 1000 64','CHECK','SUMMARY'])
 p.close();(p.d/'actual-ARM-events.json').write_text(json.dumps(dict(listener=listener,MasterFX=gf,events=events),indent=2))
 run('mixer-send-FX-probe','mixer-send-FX-baseline','mixer-send-FX-layout-A')
if __name__=='__main__':main()
