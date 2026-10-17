"""Read-only qualification boundaries, manufacturer references and provenance."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
from environment import REF,STOCK,sha
from entry import entry
from stream import command,crc_update,drain
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
base=read(REF/'firmware/sc35d8/manifest.json')
old=read(R/'builds/phase33-preservation-powercycle/installation.json')
overlaps={}
for label,lo,hi in [('81000',0x81000,0x81017),('82000',0x82000,0x82200)]:
 hits={kind:[x for x in old['operations'] if x['kind']==kind and int(x['start'],16)<hi and int(x['end_exclusive'],16)>lo] for kind in ('WRITE','ERASE')}
 assert not any(hits.values());overlaps[label]=dict(scope='Prior selected installer/staging graph only; not this exact SC35D8 derivative or complete boot',write_overlaps=0,erase_overlaps=0)
ref=read(R/'builds/phase20i-authentic-qualification/provenance.json')['reference_before']
assert len(ref)==451 and all(digest(Path(p))==h for p,h in ref.items())
pins=read(R/'plaits/upstream/source-manifest.json')['files']
assert len(pins)==183 and all(digest(R/'plaits/upstream'/p['path'])==p['sha256'] for p in pins)
prior=[]
for n in range(26,40):
 matches=list((R/'builds').glob(f'phase{n}-*/validation.json'))
 for path in matches:
  v=read(path)
  assert all(digest(path.parent/f)==h for f,h in v['evidence_sha256'].items()),str(path)
  prior.append(str(path.parent))
spans=[]
for name,a,b in [('entry',0x0807a414,entry()),('codec',0x0807a6de,(R/'builds/phase27-qspi-read/arm-diagnostic.fragment.bin').read_bytes()[0x2ca:]),('command',0x0807b000,command()),('incremental_crc',0x0807b600,crc_update()),('USB_drain',0x0807b800,drain())]:
 spans.append(dict(name=name,address=hex(a),end_exclusive=hex(a+len(b)),bytes=len(b),sha256=sha(b)))
assert sum(x['bytes'] for x in spans)==782
rollback=[]
for name,expect in [('circuittracks-firmware-4486-STOCK.bin','b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da'),('circuittracks-firmware-4486-STOCK.syx','bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd')]:
 p=REF/'stock'/name;assert digest(p)==expect
 rollback.append(dict(path=str(p),bytes=p.stat().st_size,sha256=expect))
sys.path.insert(0,str(REF/'tools'))
import ct_fw
decoded=ct_fw.decode((REF/'stock/circuittracks-firmware-4486-STOCK.syx').read_bytes())
assert decoded['image']==STOCK
result=dict(verdict='UNQUALIFIED',confidence='UNKNOWN',
 chosen_base=dict(marker=base['marker'],image_bytes=int(base['image_size'],16),image_sha256=base['image_sha256'],syx_sha256=base['syx_sha256'],hardware_evidence='Reference docs/NOTAS.md:1424, 2026-10-09; not repeated',reconstructed_or_generated=False),
 prototype=dict(native_fixture='B1.3 running RAM with original stock NOR methods; not SC35D8 integration',code_spans=spans,total_code_bytes=782,immutable_request_template_bytes=232,static_RAM=0,heap=0,live_frame_bytes=188,entry_saved_bytes=32,command_saved_bytes=20,vectors_changed=0,DSP_changes=0,bootloader_changes=0,application_image_exported=False,SYX_generated=False),
 buffer=dict(address='0x2000a070',end_exclusive='0x2000a0b0',bytes=64,alignment=16,owner='Main parser allocation 2000a050 +32; lent through synchronous callback to Storage/DMA',cacheability='Non-cacheable DTCM',DMA_accessibility='STM32F7 AHBS supports DMA to/from DTCM',DMA_element_bytes=1,ownership_begin='After fixed request validation, before queued op1',ownership_end='Only after backend release and USB output drain; NEVER after TEF/missing completion',concurrent_users='Main/Storage/DMA/USB lifetimes checked in bounded fixture; complete incoming USB queue/reentry remains UNKNOWN',full_buffer_qualification='UNKNOWN'),
 manufacturer_sources=[dict(url='https://www.st.com/resource/en/application_note/an4667-stm32f7-series-system-architecture-and-performance-stmicroelectronics.pdf',sections='1.3.3 pp8; memory map table3 pp14; DMA path pp18',claims='F74/F75 DTCM 20000000..2000ffff and DMA access through AHBS'),dict(url='https://www.st.com/resource/en/application_note/an4839-level-1-cache-on-stm32f7-series-and-stm32h7-series-stmicroelectronics.pdf',sections='section2 pp4; section3.2 pp5',claims='TCM non-cacheable; DMA destination DTCM example')],
 installation_selected_replay=overlaps,exact_candidate_installation='UNKNOWN: no SC35D8-derived image generated; earlier input/size/hash differs',complete_first_boot_preservation='UNKNOWN; no broad boot emulation required or attempted',
 rollback=rollback,rollback_official_SYX_decodes_exactly_to_stock=True,remaining_gates=['Native USB receive queue, parser aliasing and duplicate-after-return workload; do not count deferred-duplicate marker as execution','Exact SC35D8-derived integration, removal of legacy write-pad/remote mutation routes and relocation regression','Exact candidate update path for BOTH intervals; prior selected graph is insufficient for an exact-artifact claim'],
 reference_files_unchanged=451,pinned_sources_unchanged=183,prior_phases_unchanged=prior,hardware_access=False,phase40_continued=False,broad_cold_boot_run=False)
(O/'qualification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k in ('verdict','prototype','installation_selected_replay','reference_files_unchanged','pinned_sources_unchanged','rollback')},indent=2))
