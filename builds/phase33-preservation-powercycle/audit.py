"""Address-map and caller evidence; all unknown suffixes explicit."""
from support import *
from collections import defaultdict
r=json.loads((O/'installation.json').read_text());e=Physical()
groups=defaultdict(list)
for op in r['operations']:groups[(op['phase'],op['kind'],op.get('command',''))].append(op)
footprints=[]
for (phase,kind,cmd),ops in groups.items():
 intervals=sorted((int(x['start'],16),int(x['end_exclusive'],16)) for x in ops)
 merged=[]
 for a,b in intervals:
  if merged and a<=merged[-1][1]:merged[-1][1]=max(merged[-1][1],b)
  else:merged.append([a,b])
 footprints.append(dict(phase=phase,kind=kind,command=cmd,count=len(ops),ranges=[[hex(a),hex(b)] for a,b in merged]))
raw_banks=[dict(selector=i,base=hex(e.r32(e.r32(0x20003cc8+4*i)+8)),capacity=hex(e.r32(e.r32(0x20003cc8+4*i)+12))) for i in range(4)]
# Exhaustive halfword decoding is a candidate census, not all reachable code.
targets={0x08005db4:'boot identity write',0x08003c24:'boot installer',0x08003b9a:'boot validation',0x08003b2a:'boot metadata read',
 0x08025228:'application metadata write',0x08035e28:'coefficient/table initializer',0x0805dbdc:'B1.3 lazy state allocation'}
callers={hex(a):dict(label=n,candidates=[]) for a,n in targets.items()}
for start,b in ((0x08000000,ROM[:0x10000]),(0x08010000,PUBLISHED[:])):
 for off in range(0,len(b)-3,2):
  i=next(md.disasm(b[off:off+4],start+off),None)
  if i and i.mnemonic in ('bl','b.w') and i.operands[0].type==2 and i.operands[0].imm in targets:
   callers[hex(i.operands[0].imm)]['candidates'].append(hex(i.address))
for a,n in ((0x08003ab0,0x7a),(0x08003b2a,0xfa),(0x08003c24,0xe0),(0x08003d06,0x40),(0x08005d98,0x38),(0x08006020,0x80),
 (0x08035e28,0x100),(0x0802520c,0x38),(0x08023078,0x80),(0x08037494,0x66),(0x080374d4,0x86),(0x0805dbdc,0x70)):
 dump(a,n)
result=dict(confidence='PROVEN',scope='Exact selected storage footprints; static candidates do not close all persistent-write reachability',footprints=footprints,
 bundle_descriptors=raw_banks,caller_candidates=callers,
 physical_map=[
  dict(storage='internal STM32 flash',range=['0x08000000','0x08010000'],purpose='unchanged bootloader'),
  dict(storage='internal STM32 flash',range=['0x08010000','0x08080000'],purpose='application sector allocation; marker at 0x080101e8'),
  dict(storage='external NOR chip byte offsets',range=['0x0','0x80000'],purpose='selector0 staging capacity; not CPU internal flash addresses'),
  dict(storage='external NOR chip byte offsets',range=['0x80000','0x80017'],erase_range=['0x80000','0x81000'],purpose='23-byte updater metadata'),
  dict(storage='external NOR chip byte offsets',range=['0x81000','0x81017'],erase_range=['0x81000','0x82000'],purpose='23-byte identity/settings metadata, separate from normal update finalize'),
  dict(storage='external NOR chip byte offsets',range=['0x82000','0x94000'],purpose='selector2 resource bundle; first512 bytes are target'),
  dict(storage='external NOR chip byte offsets',range=['0x94000','0xd4000'],purpose='selector3 bundle'),
  dict(storage='external NOR chip byte offsets',range=['0xd4000','0x2000000'],purpose='selector1 bundle; stock storage bindings'),
  dict(storage='SD',range=None,purpose='separate backend 0x20000338; complete startup/write graph UNKNOWN')],
 erratum='Phase31 findings mislabeled low helpers: 0x08037494 is ERASE, 0x080374d4 is PROGRAM, as executed here and correctly recorded in phase28. Prior evidence preserved.',
 first_boot_reachability=dict(initialization='Reset prefix executed; startup scatter decompressor incomplete',
  table_setup='0x08035e28 -> 0x08047c6c reads target; complete init still needs original coefficient/resource service',
  settings='0x08025228 writes identity metadata at 0x81000; 4KiB sector ends exactly at target start',
  packs_projects_patches='Global constructor/load/save/format predicates and background scheduling not closed; generic NOR/SD writers remain possible',
  B13_first_use='0x0805dbdc reservation itself tested earlier, does not establish all first-use write reachability',
  background_workers='0x08024014 dispatch can write/erase; queue producer address closure incomplete'),
 H1='UNKNOWN complete install',H2='UNKNOWN complete first boot',P4='PROVEN bootloader bytes unchanged; actual recovery availability UNKNOWN',
 manufacturer_sources=[
  dict(url='https://www.mxic.com.tw/Lists/Datasheet/Attachments/8906/MX25L25645G%2C%203V%2C%20256Mb%2C%20v2.0.pdf',support='Search-indexed official sector erase section: 4KiB, WREN required; full PDF retrieval unsuccessful'),
  dict(url='https://raw.githubusercontent.com/STMicroelectronics/cmsis-device-f7/master/Include/stm32f745xx.h',support='DMA/QSPI/RCC reset bit and register identities')],
 unit_NOR_identity='UNKNOWN on user unit; reference ctre/README.md:7 identifies MX25L25645G',hardware_access=False)
(O/'address-and-reachability.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(footprints=footprints,caller_candidates=callers),indent=2))
