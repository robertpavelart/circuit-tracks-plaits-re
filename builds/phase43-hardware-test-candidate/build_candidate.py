"""Clean pinned build and firmware serialization. Files only; no uploader."""
from pathlib import Path
import sys,os,json,hashlib,importlib.util
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase42-exact-rdiag-integration'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(n,x):(O/n).write_text(json.dumps(x,indent=2)+'\n')
def main():
 assert json.loads((O/'heap-preflight.json').read_text())['gate']=='PASS'
 pins=json.loads((P/'inputs.json').read_text());v=json.loads((P/'validation.json').read_text())
 for name,h in v['evidence_sha256'].items():assert sha((P/name).read_bytes())==h,name
 # A new hash-checked source tree, with no intermediate candidate BIN input.
 for x in pins['sources']:
  old=Path(x['local']);raw=old.read_bytes();assert sha(raw)==x['sha256']
  dest=O/'source'/old.relative_to(P/'source');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
 def guard(event,args):
  if event=='open':
   path,mode,flags=args
   if isinstance(path,(str,bytes,os.PathLike)) and ((isinstance(mode,str) and any(c in mode for c in 'wax+')) or isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC)):
    assert Path(os.fsdecode(path)).resolve().is_relative_to(O),'write outside phase43'
 sys.addaudithook(guard)
 sys.path.insert(0,str(O/'source/tools'));os.environ['DSP_ASM_CACHE_UPDATE']='0';os.environ['DSPTOOL']=str(O/'source/ext/bin/dsptool.exe')
 import ct_fw,build_sc35d8 as B
 official=Path(pins['rdiag']['path']).parents[1]/'stock/circuittracks-firmware-4486-STOCK.syx'
 syx=official.read_bytes();assert sha(syx)=='bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd'
 d=ct_fw.decode(syx);stock=d['image'];assert sha(stock)=='b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da'
 assert stock==(O/'source/stock/circuittracks-firmware-4486-STOCK.bin').read_bytes()
 (O/'official-4486-decoded.bin').write_bytes(stock)
 img,report=B.b182.b18.b6.b5.build(stock,O/'source/re/app.asm');img=bytearray(img)
 marker=B.b182.b18.sc.MARK_OFF;img[marker:marker+6]=b'SC35D8'
 B.linein3.patch_hook(img,report,B.linein3.L2.patch_p);B.extra(img,report)
 base=bytes(img);expect=pins['expected'];assert sha(base)==expect['image_sha256'] and len(base)==int(expect['image_size'],16) and ct_fw.crc32_mpeg2(base)==int(expect['crc32'],16)
 (O/'clean-sc35d8.bin').write_bytes(base)
 # Execute the exact phase42 emitter, without its main() or candidate BIN read.
 sys.path.insert(0,str(P))
 spec=importlib.util.spec_from_file_location('pinned_phase42_emitter',P/'integrate.py');I=importlib.util.module_from_spec(spec);spec.loader.exec_module(I);I.O=O
 integration=json.loads((P/'integration.json').read_text());L={k:int(x,16) for k,x in integration['layout'].items()};ns=I.factories(L)
 chunks={'gst':I.gst(L['gst']),'watch':I.watch(L['watch']),'entry':I.entry(L['entry'],L['command']),'command':ns['command'](),'crc':ns['crc_update'](),'drain':ns['drain']()}
 codec=(R/'builds/phase27-qspi-read/arm-diagnostic.fragment.bin').read_bytes()[0x2ca:]
 from evidence_protocol import request
 chunks.update(n32=codec[:16],bytes=codec[16:42],packet_crc=codec[42:],template=request(0))
 img=bytearray(base);img[I.POOL-I.BASE:I.END-I.BASE]=b'\xff'*(I.END-I.POOL)
 for k,b in chunks.items():
  assert len(b)==integration['components'][k]['bytes'] and sha(b)==integration['components'][k]['sha256']
  img[L[k]-I.BASE:L[k]-I.BASE+len(b)]=b
 for x in integration['hook_patches']:
  at=int(x['address'],16)-I.BASE;b=bytes.fromhex(x['after']);assert base[at:at+len(b)].hex()==x['before'];img[at:at+len(b)]=b
 image=bytes(img);assert sha(image)==integration['image_sha256'];assert len(image)<=0x70000
 candidate=ct_fw.encode(image);decoded=ct_fw.decode(candidate)
 assert decoded['image']==image and ct_fw.encode(decoded['image'])==candidate
 (O/'circuittracks-4486-nor-evidence-test.bin').write_bytes(image)
 (O/'circuittracks-4486-nor-evidence-test.syx').write_bytes(candidate)
 def identity(path,b):return dict(path=str(path),bytes=len(b),sha256=sha(b))
 inputs=dict(official_input_SYX=identity(official,syx),official_decoded_BIN=dict(**identity(O/'official-4486-decoded.bin',stock),CRC=hex(ct_fw.crc32_mpeg2(stock))),clean_SC35D8=dict(**identity(O/'clean-sc35d8.bin',base),CRC=hex(ct_fw.crc32_mpeg2(base))),candidate_BIN=dict(**identity(O/'circuittracks-4486-nor-evidence-test.bin',image),CRC=hex(ct_fw.crc32_mpeg2(image))),candidate_SYX=identity(O/'circuittracks-4486-nor-evidence-test.syx',candidate))
 result=dict(confidence='PROVEN',inputs=inputs,clean_sources=len(pins['sources']),input_intermediate_BIN_used=False,exact_phase42_match=True,roundtrip_BIN_equal=True,roundtrip_SYX_equal=True,application_start='0x08010000',application_end_exclusive=hex(0x08010000+len(image)),accepted_maximum_bytes=0x70000,remaining_bytes=0x70000-len(image),hardware_access=False,MIDI_ports_opened=0,uploader_launched=False)
 save('build-results.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
