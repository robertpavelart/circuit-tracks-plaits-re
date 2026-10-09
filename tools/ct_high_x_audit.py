#!/usr/bin/env python3
"""Candidate-specific static evidence replay. No DSP emulation or free-RAM claim.

Byte-checks existing canonical DSP listings and ARM evidence; reviewed premises
are explicit. Direct/indirect inventories include data decodes and do not prove
reachability. Output directory must be new; originals never opened for writing.
"""
import argparse, json, re
from pathlib import Path
from ct_static import ROOT, BASE, BIN_HASH, SYX_HASH, sha, save
from ct_resource_audit import read_rows
import ct_fw_tool

def emit(out, name, obj):
    save(out/name, json.dumps(obj, indent=2, sort_keys=True)+'\n')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir', required=True)
    out=Path(ap.parse_args().output_dir).resolve()
    if out.exists(): raise SystemExit('Choose a fresh output directory')
    if out==ROOT/'original' or ROOT/'original' in out.parents: raise SystemExit('Protected original/')
    arm=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
    syxp=ROOT/'original/circuittracks-firmware-4486.syx'
    syx=syxp.read_bytes()
    assert sha(arm)==BIN_HASH and sha(syx)==SYX_HASH
    decoded=ct_fw_tool.decode_syx(syxp)
    fw=decoded['firmware']
    assert fw==arm and ct_fw_tool.build_syx(syxp,fw)==syx
    payload=(ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin').read_bytes()
    assert sha(payload)=='b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855'
    rows=read_rows(ROOT/'builds/phase3-selection0-channel0.asm',payload)
    manifest=json.loads((ROOT/'firmware/dsp/build-4486/manifest.json').read_text())
    protected={}
    for block in manifest['blocks']:
        for kind in ('stream','payload'):
            path=ROOT/'firmware/dsp/build-4486'/block[kind+'_file']
            digest=sha(path.read_bytes())
            assert digest==block[kind+'_sha256']
            protected[str(path.relative_to(ROOT))]=digest
    def require(pc, text):
        assert rows[pc]['text']==text, (hex(pc),rows[pc]['text'],text)
    require(0x1D26,'move #$001b16,r2')
    require(0x1D41,'move #$001b16,r2')
    require(0x1E15,'move r6,x:$1d3a')
    require(0x1E17,'move r7,x:$1d3b')
    require(0x1F68,'move y:>(r6+32),r1')
    require(0x1F6A,'move y:>(r6+33),r3')
    require(0x1F6E,'move a,x:(r1)+')
    require(0x1F6F,'move a,x:(r3)+')
    windows=[(0x100,0x202),(0x1C53,0x1FD1),(0x2779,0x278A),(0x2A2D,0x2A3F)]
    save(out/'dsp-witnesses.asm','\n'.join(r['line'] for pc,r in rows.items()
          if any(lo<=pc<hi for lo,hi in windows))+'\n')
    # Verify existing ARM windows, never decoding new instructions here.
    arm_inputs={}
    for directory in ('arm-traffic','arm-followup','arm-roots','arm-dispatch'):
        for path in sorted((ROOT/'builds/phase10'/directory).glob('*.asm')):
            for line in path.read_text().splitlines():
                m=re.match(r'([0-9A-F]{8})\s+([0-9a-f]+)\s+',line)
                if m:
                    pc=int(m[1],16);raw=bytes.fromhex(m[2])
                    assert arm[pc-BASE:pc-BASE+len(raw)]==raw
            arm_inputs[str(path.relative_to(ROOT))]=sha(path.read_bytes())
    fields=['R0 X coefficient cursor','R1 X modulo workspace cursor','M1 modifier',
        'R4 Y generator cursor','N4 generator stride','M4 modifier',
        'R5 Y output cursor','N5 Y stage stride','B1 harmonic/progress bound',
        'X0 stage/progress code','R3 X interpolation cursor']
    context=[]
    for i,name in enumerate(fields):
        context.append({'address':hex(0x1B16+i),'field':name,
         'save_PC':hex(0x1D32+i),'restore_PC':hex(0x1D48+i),
         'status':'VERIFIED instruction usage; upstream writer closure partial'})
    emit(out,'table-context.json',context)
    # Reviewed recurrence P:1D74..84: carry is the OLD bit for BSET/BCHG.
    stages={}
    for count in (16,18):
        flags=0;remaining=count;b=1;items=[];cursor=0xC00
        while remaining:
            items.append({'remaining':remaining,'coefficient_count':b,
                          'X_source_start':hex(cursor),'X_source_end':hex(cursor+b)})
            cursor+=b
            old2=bool(flags&4);flags|=4;double=False
            if old2:
                old1=bool(flags&2);flags|=2
                if old1:
                    old0=bool(flags&1);flags^=1;double=old0
            if double and remaining!=count:b*=2
            remaining-=1
        assert cursor-0xC00=={16:256,18:512}[count]
        stages[str(count)]={'stages':items,'source_end':hex(cursor),
         'premises':'initial flags X:43=0; X:42=16/18; B=1; no foreign state mutation; legacy AGU'}
    emit(out,'coefficient-stages.json',stages)
    # Concrete power-of-two ring, NOT generic modulo inference from M alone.
    ring={}
    for start in (0x2400,0x2500):
        addresses=[0x2400+((start-0x2400+i)%1024) for i in range(1024)]
        assert min(addresses)==0x2400 and max(addresses)==0x27FF
        ring[hex(start)]={'start':hex(min(addresses)),'end_exclusive':hex(max(addresses)+1),
         'premises':'M1=0x3FF; aligned 1024-word block at 2400; legacy modulo; EMA=0; +1 updates'}
    emit(out,'workspace-rings.json',ring)
    # Eight channels, DSP56724RM table 3-7. Never confuse Y ICC/EMBC with X DMA.
    registers={}
    for ch in range(8):
        base=0xFFFFEC-4*ch
        for delta,name in enumerate(('DCR','DCO','DDR','DSR')):
            registers[base+delta]=f'{name}{ch}'
    registers.update({0xFFFFF4:'DSTR',0xFFFFF3:'DOR0',0xFFFFF2:'DOR1',
                      0xFFFFF1:'DOR2',0xFFFFF0:'DOR3'})
    census=[];indirect=[];absolute=[];tracked=[]
    track={0x1B15,0x1B16,0x1B21,0x1D3A,0x1D3B,0x1D40,0x1D41,0x1D42,0x42,0x43}
    for pc,r in rows.items():
        text=r['text']
        for m in re.finditer(r'([xy]):\$([0-9a-f]+)',text):
            space,addr=m[1].upper(),int(m[2],16)
            item={'PC':hex(pc),'space':space,'address':hex(addr),'instruction':text,
                  'status':'VERIFIED decoded bytes; reachability/operand direction requires review'}
            if space=='X' and addr in registers:
                census.append(dict(item,register=registers[addr]))
            if space=='X' and 0x5F00<=addr<0x6000:absolute.append(item)
            if space=='X' and addr in track:tracked.append(item)
        if pc<0x2029 and re.search(r'x:(?:>)?\(',text):
            indirect.append({'PC':hex(pc),'instruction':text,
                             'status':'candidate inventory, not solved points-to/reachability'})
    emit(out,'DMA-register-census.json',census)
    emit(out,'tracked-state-references.json',tracked)
    emit(out,'direct-candidate-references.json',absolute)
    emit(out,'indirect-X-inventory.json',indirect)
    entry=[]
    for pc,r in rows.items():
        if r['text'].split()[0].startswith(('j','b')) and re.search(r'\$1e15\b',r['text']):
            entry.append({'PC':hex(pc),'instruction':r['text']})
    emit(out,'entry-census.json',{'entry':'P:1E15','decoded_direct_edge_candidates':entry,
      'aligned_word_occurrences':[hex(i//3) for i in range(0,len(payload),3)
                                  if payload[i:i+3]==bytes.fromhex('001e15')],
      'status':'absence is not dead-code proof; indirect transfers remain unresolved'})
    dma=[]
    for ch,dcr,src,dst in ((0,0x285AC4,0xFFFFA8,0x29),(1,0x286251,0x21,0xFFFFA4)):
        ss=dcr&3;ds=(dcr>>2)&3;sm=(dcr>>4)&7;dm=(dcr>>7)&7
        assert (dcr>>10)&1==0 and sm in (4,5) and dm in (4,5)
        require(0x2A2D+8*ch,f'movep #${dcr:06x},x:${0xFFFFEC-4*ch:06x}')
        dma.append({'channel':ch,'DCR':hex(dcr),'source_space':('X','Y','P')[ss],
          'destination_space':('X','Y','P')[ds],'source_start':hex(src),
          'source_end_exclusive':hex(src+(3 if sm==5 else 1)),
          'destination_start':hex(dst),'destination_end_exclusive':hex(dst+(3 if dm==5 else 1)),
          'source_mode':sm,'destination_mode':dm,'DCO':2,'transfers':3,
          'status':'SOURCE-DERIVED fields + VERIFIED stock words; reviewed configuration only'})
    emit(out,'DMA-reviewed-bounds.json',dma)
    unresolved=[
      {'mechanism':'ARM addressed utility','producer':'080269E4 -> 08026A3C..AD4; caller 0801F30A',
       'domain':'private input <8000 includes entire candidate; operation/mode ancestry unresolved'},
      {'mechanism':'effect indirect X output','producer':'P:1F68/1F6A reads Y:(R6+32/33); writes 1F6E/1F6F and 1F97',
       'domain':'R6=1800 or19F0 in reviewed paths; Y cursor producers and normal entry to1E15 unresolved'},
      {'mechanism':'selector7 X copy','producer':'P:1CBB..1CC7; X:C00 index',
       'domain':'normal publisher not established; index bound unresolved; abstract destination=1D8D+4*index'},
      {'mechanism':'global closure','producer':'indirect-X-inventory.json and DMA-register-census.json',
       'domain':'not a complete interprocedural AGU/normal mode/register-write proof; no universal scratch maximum'}]
    emit(out,'unresolved-mechanisms.json',unresolved)
    # Every prospective subrange is covered by the unclosed utility domain.
    searches=[]
    for size in (256,128,64):
        placements=[(s,s+size) for s in range(0x5F00,0x6000-size+1)]
        assert all(0<=s<e<=0x8000 for s,e in placements)
        searches.append({'words':size,'placements_checked':len(placements),
          'classification':'UNRESOLVED','verified_available_subranges':[],
          'reason':'unclosed utility address domain covers every placement; capability is not runtime occupancy'})
    emit(out,'allocation-search.json',searches)
    emit(out,'provenance.json',{'mode':'STATIC ONLY','BIN_SHA256':sha(arm),'SYX_SHA256':sha(syx),
      'DSP_payload_SHA256':sha(payload),'script_SHA256':sha(Path(__file__).read_bytes()),
      'protected_DSP_extract_hashes':protected,'CRC':hex(decoded['crc']),
      'ARM_inputs':arm_inputs,'decode_equals_BIN':True,'roundtrip_identical':True,
      'candidate':{'space':'channel-zero private X','start':'0x5F00','end_exclusive':'0x6000'},
      'verdict':'UNRESOLVED; no available subrange proved; no normal occupancy witness established'})

if __name__=='__main__':main()
