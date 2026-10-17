"""Native SPI2 DMA completion model for the exact pending loader wait only."""
from pathlib import Path
import sys,shutil
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
checkpoint=O/'startup-before-spi-model';checkpoint.mkdir(exist_ok=True)
for n in ['continuity-status.json','continuity-startup-frontier.json','continuity-frontier-sram.bin']:
 if not (checkpoint/n).exists():shutil.copyfile(O/n,checkpoint/n)
bad=O/'startup-spi-increment-model-invalid';bad.mkdir(exist_ok=True)
for n in ['continuity-status.json','continuity-startup-frontier.json','continuity-frontier-sram.bin']:
 if not (bad/n).exists():shutil.copyfile(O/n,bad/n)
s=(O/'startup_adc_completion.py').read_text()
addition="""
 src=src.replace('if early_tick and switches',"if pc==0x08057560 and u.reg_read(UC_ARM_REG_IPSR)==30:"+chr(10)+"            action[0]=('popr4return',pc);u.emu_stop();return"+chr(10)+"        if early_tick and switches")
 src=src.replace('if early_tick and switches',"if pc==0x08023414 and not u.reg_read(UC_ARM_REG_IPSR) and e.r32(0x40026058)&1:"+chr(10)+"            action[0]=('spi2-dma',pc);u.emu_stop();return"+chr(10)+"        if early_tick and switches")
 src=src.replace("elif kind=='adc-conversion':", "elif kind=='spi2-dma':"+chr(10)+"                stream=0x40026058;dest=e.r32(stream+12);count=e.r32(stream+4);assert 0<count<=512 and 0x20000000<=dest<0x20050000-count,(hex(dest),count);u.mem_write(dest,bytes(count));e.w32(stream,e.r32(stream)&~1);e.w32(stream+4,0);e.w32(0x40026000,e.r32(0x40026000)|(1<<27));events.append(dict(event='synthetic SPI2 RX DMA completion through actual IRQ30',destination=hex(dest),bytes=count));pc=exception_enter(30,value)"+chr(10)+"            elif kind=='adc-conversion':")
 src=src.replace("elif kind=='popreturn':", "elif kind=='popr4return':"+chr(10)+"                a=u.reg_read(UC_ARM_REG_MSP);r4,exc=struct.unpack('<2I',bytes(u.mem_read(a,8)));u.reg_write(UC_ARM_REG_R4,r4);u.reg_write(UC_ARM_REG_MSP,a+8);pc=exception_leave(exc)"+chr(10)+"            elif kind=='popreturn':")
 src=src.replace('stream=0x40026058;dest=', 'e.w32(0x40026070,e.r32(0x40026070)&~1);e.w32(0x40026074,0);stream=0x40026058;dest=')
 src=src.replace('u.mem_write(dest,bytes(count));e.w32(stream', 'width=1<<((e.r32(stream)>>13)&3);extent=count*width if e.r32(stream)&1024 else width;u.mem_write(dest,bytes(extent));e.w32(stream')
"""
s=s.replace('s=s.replace("src=src.replace(', 'addition+='+repr(addition)+'\ns=s.replace("src=src.replace(',1)
exec(compile(s,str(O/'selected-startup-spi-extension.py'),'exec'),dict(__file__=str(O/'startup_adc_completion.py'),__name__='__main__'))
