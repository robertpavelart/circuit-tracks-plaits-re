"""Narrow extension: feed only actual ADC/DMA IRQ roots already mapped in Phase60.
Never sets readiness counters, geometry fields, task contexts or heap cursors.
Synthetic zero ADC samples and peripheral event timing are explicit models.
"""
from pathlib import Path
import sys,shutil
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
checkpoint=O/'startup-before-adc-model';checkpoint.mkdir(exist_ok=True)
for name in ['continuity-status.json','continuity-startup-frontier.json','continuity-frontier-sram.bin']:
 if not (checkpoint/name).exists():shutil.copyfile(O/name,checkpoint/name)
checkpoint2=O/'startup-before-calibration-model';checkpoint2.mkdir(exist_ok=True)
for name in ['continuity-status.json','continuity-startup-frontier.json','continuity-frontier-sram.bin']:
 if not (checkpoint2/name).exists():shutil.copyfile(O/name,checkpoint2/name)
s=(O/'startup_continuity.py').read_text()
addition="""
 src=src.replace('sum(counts.values())>=next_tick[0]','instruction_clock[0]>=next_tick[0]').replace('next_tick[0]=sum(counts.values())+10000','next_tick[0]=instruction_clock[0]+10000')
 src=src.replace('counts[pc]+=1;last.append(pc)','counts[pc]+=1;last.append(pc);instruction_clock[0]+=1')
 src=src.replace('next_tick=[120000]','next_tick=[120000];instruction_clock=[0];adc_stage=[0];adc_events=[0]')
 src=src.replace('e=prior.Physical();u=e.uc',"e=prior.Physical();u=e.uc;u.mem_map(0x1ff0f000,0x1000);u.mem_write(0x1ff0f44a,struct.pack('<H',1500)) # SYNTHETIC factory-calibration model, not unit evidence")
 src=src.replace('if early_tick and switches', "if pc in (0x0801e2fa,0x0801e2f8):adc_stage[0]=0"+chr(10)+"        if pc==0x0801e2da and adc_events[0]<128 and adc_stage[0]<2 and not u.reg_read(UC_ARM_REG_IPSR):"+chr(10)+"            action[0]=('adc-conversion' if adc_stage[0]==0 else 'adc-dma',pc);adc_stage[0]+=1;u.emu_stop();return"+chr(10)+"        if early_tick and switches")
 src=src.replace('if pc==0x0805999a and', 'if pc in (0x0805999a,0x080574e6) and')
 src=src.replace('u.reg_read(UC_ARM_REG_IPSR)==15:', 'u.reg_read(UC_ARM_REG_IPSR) in (15,34):')
 src=src.replace("elif kind=='early-tick':", "elif kind=='adc-conversion':"+chr(10)+"                e.w32(0x40012000,e.r32(0x40012000)|2);events.append(dict(event='synthetic ADC EOC through actual IRQ34',PC=hex(value)));pc=exception_enter(34,value)"+chr(10)+"            elif kind=='adc-dma':"+chr(10)+"                dest=e.r32(0x4002641c);count=e.r32(0x40026414);enabled=e.r32(0x40026410)&1;assert enabled and 0<count<=192 and 0x20000000<=dest<0x20050000-count*2,(hex(dest),count,enabled);u.mem_write(dest,struct.pack('<H',1024)*count);e.w32(0x40026400,e.r32(0x40026400)|32);events.append(dict(event='synthetic ADC value1024 DMA completion through actual IRQ72',destination=hex(dest),halfwords=count));adc_events[0]+=1;pc=exception_enter(72,value)"+chr(10)+"            elif kind=='early-tick':")
"""
s=s.replace("src=src.replace(\"exec(compile(src,str(O/'selected-corrected-startup-runner.py')\", extra+", "extra+="+repr(addition)+"\nsrc=src.replace(\"exec(compile(src,str(O/'selected-corrected-startup-runner.py')\", extra+")
exec(compile(s,str(O/'selected-startup-adc-extension.py'),'exec'),dict(__file__=str(O/'startup_continuity.py'),__name__='__main__'))
