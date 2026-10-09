#!/usr/bin/env python3
"""Phase13 scoped static ledger. Not an emulator or a global non-alias proof.

Byte-checks existing listings, exports the instruction-derived table layout,
boot-clear values and known ARM sink overlap. Fresh output directory required.
"""
import argparse, csv, io, json, re
from pathlib import Path
from ct_static import ROOT, BIN_HASH, SYX_HASH, sha, save
from ct_resource_audit import read_rows
import ct_fw_tool

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',required=True)
    out=Path(parser.parse_args().output_dir).resolve()
    if out.exists(): raise SystemExit('Choose a fresh output directory')
    if out==ROOT/'original' or ROOT/'original' in out.parents:
        raise SystemExit('Protected original/')
    def emit(name,obj): save(out/name,json.dumps(obj,indent=2,sort_keys=True)+'\n')
    arm=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
    syxp=ROOT/'original/circuittracks-firmware-4486.syx'; syx=syxp.read_bytes()
    assert sha(arm)==BIN_HASH and sha(syx)==SYX_HASH
    assert ct_fw_tool.decode_syx(syxp)['firmware']==arm
    assert ct_fw_tool.build_syx(syxp,arm)==syx
    manifest=json.loads((ROOT/'firmware/dsp/build-4486/manifest.json').read_text())
    protected={'firmware/circuittracks-firmware-4486.bin':sha(arm),
               'original/circuittracks-firmware-4486.syx':sha(syx)}
    for block in manifest['blocks']:
        for kind in ('stream','payload'):
            path=ROOT/'firmware/dsp/build-4486'/block[kind+'_file']
            assert sha(path.read_bytes())==block[kind+'_sha256']
            protected[str(path.relative_to(ROOT))]=sha(path.read_bytes())
    payload=(ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin').read_bytes()
    rows=read_rows(ROOT/'builds/phase3-selection0-channel0.asm',payload)
    def require(pc,text): assert rows[pc]['text']==text,(hex(pc),text)
    for pc,t in {
        0x2035:'asr a #$00035f,r0',0x203A:'move x:(r0)+,x1',
        0x203B:'move x:(r0)+,r5',0x203C:'move x:(r0)+,r6',
        0x203D:'move x:(r0)+,r7',0x203E:'move x:(r0)+,x0',
        0x2040:'do x1,$204c',0x2043:'mpy +y1,y0,a x:(r0)+,r4',
        0x2044:'move x:(r0)+,r5',0x2046:'mpy +x1,y0,a x:(r0)+,r6',
        0x2047:'move x:(r0)+,r7',0x2049:'mac +x0,y1,b x:(r0)+,x0',
        0x2048:'move x:(r4),b a,y1',0x204B:'move b,x:(r4)',
        0x2784:'move #$006000,x1',0x2788:'move x0,x:(r0)',
        0x2789:'move x0,y:(r0)+',0x1BA9:'move n0,y:$0030',
        0x28AC:'move #$00202b,r2',0x1A70:'move #$0002fe,r1',
        0x1A75:'move x:$02fa,n0',0x1B90:'move a,x:(r1)+n1',
    }.items(): require(pc,t)
    inputs={}
    arm_windows=[('builds/phase9/helper-closure/080286AA-0802872C.asm',0x286BC,0x28726),
                 ('builds/phase9/entry/080273E4-08027D1A.asm',0x27A10,0x27AF4)]
    arm_text=[]
    for name,lo,hi in arm_windows:
        path=ROOT/name; inputs[name]=sha(path.read_bytes())
        for line in path.read_text().splitlines():
            m=re.match(r'([0-9A-F]{8})\s+([0-9a-f]+)\s+(.*)',line)
            if not m: continue
            addr=int(m[1],16); raw=bytes.fromhex(m[2])
            assert arm[addr-0x08010000:addr-0x08010000+len(raw)]==raw
            if 0x08000000+lo<=addr<0x08000000+hi: arm_text.append(line)
    assert any('080286E0' in s and 'r1, #0' in s for s in arm_text)
    assert any('080286E4' in s and '#0x80292f8' in s for s in arm_text)
    save(out/'arm-witnesses.asm','\n'.join(arm_text)+'\n')
    windows=[(0x202B,0x204C),(0x2779,0x278A),(0x28AC,0x28D0),
             (0x1BA8,0x1BAC),(0x1A70,0x1AAB),(0x1B7B,0x1B93),
             (0x657,0x691),(0x4D5,0x4E5)]
    save(out/'dsp-witnesses.asm','\n'.join(rows[p]['line'] for p in sorted(rows)
         if any(lo<=p<hi for lo,hi in windows))+'\n')
    fields=[{'offset':i,'register':reg,'use':use} for i,reg,use in [
        (0,'R5','Y source address, indexed by N5'),
        (1,'R6','Y source address, indexed by N6'),
        (2,'R7','Y multiplicative-factor address, unindexed'),
        (3,'X0','MAC coefficient; value semantics unnamed'),
        (4,'R4','absolute X address: read 2048, write 204B')]]
    emit('table-layout.json',{'status':'VERIFIED instruction-derived layout, linear M0 premise',
        'count_X':'0x35F','record_base':'0x360+5*k','destination_field':'0x364+5*k',
        'fields':fields,'words_per_record':5,'known_live_count':0,
        'maximum_valid_k':'UNRESOLVED universally; empty under recovered zero-count invariant',
        'write_formula':'[X[0x364+5*k],X[0x364+5*k]+1)',
        'R4_post_increment':False,'M4_effect_on_unindexed_store':'none',
        'R0_increment_per_iteration':5,'prefetch_words_after_last_record':4,
        'prefetch_note':'not proven guard records; at N=20 reads X[3C4,3C8), separate smoothing-source state',
        'table_capacity':'HYPOTHESIS 20 from adjacent use at3C4; not a count bound'})
    buf=io.StringIO(); writer=csv.writer(buf)
    writer.writerow(['k','base_X','field0','field1','field2','field3','destination_field_X',
                     'destination_value','provenance','status'])
    for k in range(20):
        writer.writerow([k,hex(0x360+5*k),0,0,0,0,hex(0x364+5*k),0,
                         'P2779..2789 boot clear','VERIFIED immediately after clear; not full-runtime values'])
    save(out/'boot-clear-record-window.csv',buf.getvalue())
    writes_path=ROOT/'builds/phase9/verified/parameter-writes.csv'
    inputs[str(writes_path.relative_to(ROOT))]=sha(writes_path.read_bytes())
    writes=list(csv.DictReader(io.StringIO(writes_path.read_text())))
    overlap=[r for r in writes if r['space']=='X' and 0x35F<=int(r['address'])<0x3C4]
    assert all(int(r['address'])==0x35F for r in overlap)
    emit('normal-ARM-table-overlap.json',{'source':str(writes_path.relative_to(ROOT)),
         'overlap':overlap,'status':'VERIFIED within recovered parameter families, not all host traffic',
         'value_at_286E4':0,'separate_source_count':'X2FA+172*bank gets input count; normal27A10 supplies20',
         'compiled_count':'X35F+172*bank always gets zero'})
    # Census of literal operands is deliberately not a complete indirect-writer list.
    literals=[]
    for pc,r in rows.items():
        if 0x2309<=pc<0x2599: continue
        for m in re.finditer(r'[xy]:\$([0-9a-f]+)',r['text']):
            addr=int(m[1],16)
            if 0x35F<=addr<0x3C4 or (m[0].startswith('y:') and addr==0x30):
                literals.append({'pc':hex(pc),'operand':m[0],'instruction':r['text'],
                                 'status':'literal census only; indirect aliasing not excluded'})
    emit('literal-operand-census.json',literals)
    emit('mutation-ledger.json',[
        {'class':'INIT','writer':'P2788','domain':'X[0,6000)','value':0},
        {'class':'NORMAL RUNTIME recovered ARM','writer':'ARM286E4 via292F8','domain':'X35F/X4D1','value':0},
        {'class':'NORMAL RUNTIME separate source table','writer':'ARM27A5E/72/80/B8',
         'domain':'X2FB+172*bank+5*i+{0,1,2,4}; i0..19','compiled_table_overlap':False},
        {'class':'NORMAL RUNTIME separate smoothing','writer':'P1B90 via1A77/90',
         'domain':'X2FE+172*bank+5*i; recovered count20','compiled_table_overlap':False},
        {'class':'SERVICE','writer':'host5E private addressed writer','domain':'can mutate count/table; not normal blocker'},
        {'class':'UNRESOLVED','writer':'remaining normal indirect X stores / host transfer domains',
         'domain':'non-alias of X35F and table not globally proved; no recovered nonzero count publisher'}])
    emit('allocation-verdict.json',{'path_collision':'NOT-YET-DETERMINED universally',
         'recovered_zero_count_path_collision':'VERIFIED NO under documented zero-skip mode and count preservation',
         'normal_runtime_safe':'NOT-YET-DETERMINED','service_robust':'NO',
         'words_proven_available':0,'static_analysis_exhausted':False,
         'single_path_obligation':'preserve X35F==0 at each203A; if nonzero publication found, trace its destinations',
         'other_obligations':'existing effect-dispatch/cursor/modifier, paged-transfer and mode/persistence closure remain'})
    emit('sources.json',{'DO_zero_semantics':{'url':'https://www.nxp.com/docs/en/reference-manual/DSP56300FM.pdf',
         'section':'DO,13-57','fact':'initial LC zero skips if SR compatibility bit13 cleared; legacy set mode runs65536'},
         'conditional_part':{'url':'https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf',
         'section':'5.2 Table5-2','fact':'SR14..12 reserved, reset0; StackCount sc is a different register'}})
    for name,h in protected.items(): assert sha((ROOT/name).read_bytes())==h
    emit('validation.json',{'protected_hashes':protected,'decoded_BIN_equal':True,
        'SYX_roundtrip_equal':True,'canonical_DSP_bytes_checked':True,
        'ARM_witness_bytes_checked':True,'inputs':inputs,
        'RLE_P_2309_2599_excluded_from_instruction_census':True,
        'execution':'none; static formulas and existing evidence only'})

if __name__=='__main__': main()
