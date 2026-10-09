#!/usr/bin/env python3
"""Generate reviewed vector/call summaries from bounded static code ranges.

Names are analyst labels, not recovered symbols. IRQ names are conditional
on the STM32F745 mapping. No whole-image linear sweep is treated as code.
"""
import argparse
import json
from pathlib import Path
import struct
from ct_static import ROOT, BASE, BIN_HASH, sha, save, engine

RANGES = {
    'dsp_mode_dispatch': (0x0801F51E,0x0801F552),
    'dsp_upload_wrapper': (0x0801F554,0x0801F5C6),
    'dsp_upload_select': (0x08029260,0x080292D0),
    'dsp_send_boot_stream': (0x08029200,0x08029260),
    'dsp_gpio_select_low': (0x080291B8,0x080291CA),
    'dsp_gpio_select_high': (0x080291CA,0x080291E0),
    'dsp_post_upload_tables': (0x08029492,0x080294AC),
    'spi_dma_send': (0x080377DE,0x08037808),
    'dsp_bulk_send': (0x0803BA96,0x0803BAA2),
    'dsp_transfer_24bit': (0x0803BAA2,0x0803BAD6),
    'spi_poll_transfer': (0x08037960,0x080379A0),
    'startup_data_decompress': (0x080596C4,0x0805973C),
}
IRQ_NAMES = {14:'DMA1_Stream3',15:'DMA1_Stream4',18:'ADC',24:'TIM1_BRK_TIM9',
             28:'TIM2',30:'TIM4',37:'USART1',38:'USART2',40:'EXTI15_10',41:'RTC_Alarm',
             49:'SDMMC1',50:'TIM5',56:'DMA2_Stream0',59:'DMA2_Stream3',60:'DMA2_Stream4',
             69:'DMA2_Stream6',70:'DMA2_Stream7',77:'OTG_HS',92:'QUADSPI'}
CORE = {1:'Reset',2:'NMI',3:'HardFault',4:'MemManage',5:'BusFault',6:'UsageFault',
        11:'SVCall',12:'DebugMonitor',14:'PendSV',15:'SysTick'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bin',default=str(ROOT/'firmware/circuittracks-firmware-4486.bin'))
    p.add_argument('--output',required=True)
    a=p.parse_args()
    data=Path(a.bin).read_bytes()
    if sha(data)!=BIN_HASH:
        raise SystemExit('Only verified build 4486 supported')
    cs=engine()
    from capstone.arm import ARM_OP_IMM
    vectors=[]
    for index in range(1,114):
        value=struct.unpack_from('<I',data,index*4)[0]
        address=value&~1
        classification='reserved_zero' if value==0 else 'non_default_handler'
        if value and data[address-BASE:address-BASE+4]==bytes.fromhex('fff7febf'):
            classification='self_branch_default'
        name=CORE.get(index,IRQ_NAMES.get(index-16,f'IRQ{index-16}') if index>=16 else 'Reserved')
        vectors.append(dict(index=index,irq=index-16 if index>=16 else None,
                            name=name,code=f'0x{address:08X}',vector=f'0x{value:08X}',
                            classification=classification,
                            name_status='core exception' if index<16 else 'conditional STM32F745 mapping'))
    calls=[]
    for name,(start,end) in RANGES.items():
        for i in cs.disasm(data[start-BASE:end-BASE],start):
            if i.mnemonic.startswith(('bl','b')):
                target=next((o.imm for o in i.operands if o.type==ARM_OP_IMM),None)
                calls.append(dict(function=name,entry=f'0x{start:08X}',site=f'0x{i.address:08X}',
                                  instruction=i.mnemonic+' '+i.op_str,
                                  target=f'0x{target:08X}' if target is not None else None,
                                  kind='call' if i.mnemonic.startswith('bl') else 'branch'))
    save(a.output,json.dumps(dict(source_sha256=sha(data),vectors=vectors,calls=calls,
                                 code_ranges={k:[f'0x{x:08X}' for x in v] for k,v in RANGES.items()}),indent=2)+'\n')

if __name__=='__main__':
    main()
