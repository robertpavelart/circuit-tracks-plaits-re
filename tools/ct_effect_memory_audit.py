#!/usr/bin/env python3
"""Phase12 static, scoped effect-memory proof ledger. Not an ISA emulator.

Parses an instruction-established INIT RLE table; replays reviewed affine loops
and caller/target conditions. Unknown normal producers remain unknown. No
firmware writes, device APIs, service packets, Plaits implementation or execution.
"""
import argparse,csv,json,re
from pathlib import Path
from ct_static import ROOT,BIN_HASH,SYX_HASH,sha,save
from ct_resource_audit import read_rows
from ct_memory_ownership import affine_loop
import ct_fw_tool

def emit(out,name,data):save(out/name,json.dumps(data,indent=2,sort_keys=True)+'\n')
def merge(intervals):
    result=[]
    for lo,hi in sorted(intervals):
        if result and lo<=result[-1][1]:result[-1][1]=max(hi,result[-1][1])
        else:result.append([lo,hi])
    return [{'start':hex(lo),'end_exclusive':hex(hi)} for lo,hi in result]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True)
    out=Path(p.parse_args().output_dir).resolve()
    if out.exists():raise SystemExit('Choose a fresh output directory')
    if out==ROOT/'original' or ROOT/'original' in out.parents:raise SystemExit('Protected original/')
    arm=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
    syxp=ROOT/'original/circuittracks-firmware-4486.syx';syx=syxp.read_bytes()
    assert sha(arm)==BIN_HASH and sha(syx)==SYX_HASH
    d=ct_fw_tool.decode_syx(syxp);assert d['firmware']==arm and ct_fw_tool.build_syx(syxp,arm)==syx
    manifest=json.loads((ROOT/'firmware/dsp/build-4486/manifest.json').read_text());hashes={}
    for block in manifest['blocks']:
        for kind in ('stream','payload'):
            f=ROOT/'firmware/dsp/build-4486'/block[kind+'_file'];h=sha(f.read_bytes())
            assert h==block[kind+'_sha256'];hashes[str(f.relative_to(ROOT))]=h
    payload=(ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin').read_bytes()
    rows=read_rows(ROOT/'builds/phase3-selection0-channel0.asm',payload)
    words=[int.from_bytes(payload[i:i+3],'big') for i in range(0,len(payload),3)]
    def require(pc,text):assert rows[pc]['text']==text,(hex(pc),text)
    require(0x22F8,'move #$002309,r1');require(0x22FA,'do #$001f,$2308')
    require(0x22FC,'movem p:(r1)+,r0');require(0x22FD,'movem p:(r1)+,x1')
    require(0x2304,'move x0,x:(r0)+')
    pos=0x2309;rle=[]
    for i in range(31):
        start=pos;dest,count=words[pos:pos+2];pos+=2;runs=[];length=0
        assert 0<count<=16
        for j in range(count):
            value,n=words[pos:pos+2];pos+=2;assert 0<n<=1024
            runs.append({'value':hex(value),'words':n});length+=n
        assert length==1024
        rle.append({'record':i,'P_start':hex(start),'P_end_exclusive':hex(pos),
            'X_start':hex(dest),'X_end_exclusive':hex(dest+length),'runs':runs,'words':length,
            'class':'VERIFIED INIT table parse; linear startup destination premise'})
    assert pos==0x2599
    assert merge([(int(r['X_start'],16),int(r['X_end_exclusive'],16)) for r in rle])==[
        {'start':'0x74000','end_exclusive':'0x7bc00'}]
    emit(out,'INIT-external-RLE.json',{'P_data_start':'0x2309','P_data_end_exclusive':'0x2599',
      'records':rle,'X_union':[{'start':'0x74000','end_exclusive':'0x7BC00'}],
      'encoding':'31 dest/run-count records; value/repeat pairs; not DSP boot compression'})
    pairs=[(0xDBD,0xDB8,0x840,0xDBA,0x840),(0xDC5,0xDC0,0x800,0xDC2,0x880),
           (0xDCD,0xDC8,0x880,0xDCA,0x880),(0xDEC,0xDE6,0x880,0xDE8,0x9C0),
           (0xDF9,0xDF3,0x840,0xDF5,0x9C0)]
    wrappers=[]
    for call,spc,src,dpc,dst in pairs:
        require(spc,f'move #${src:06x},r6');require(dpc,f'move #${dst:06x},r7')
        require(call,'jsr (r0)')
        addresses=[]
        for i in range(64):addresses.append(dst+i)
        assert not any(0x1820<=a<0x1830 or 0x1A10<=a<0x1A20 for a in addresses)
        wrappers.append({'call_PC':hex(call),'R6_base':hex(src),'R7_base':hex(dst),
          'Y_output_start':hex(dst),'Y_output_end_exclusive':hex(dst+64),
          'count':32,'stores_per_iteration':2,'modifier':'M7=FFFF linear, or3FF same aligned low ring for these starts',
          'scope':'VERIFIED register setup; conditional if1E15 called from this family; actual target closure pending'})
    emit(out,'R7-caller-families.json',wrappers)
    bases={'r0':0x2C02,'r1':0x2C24,'r2':0x1B50,'r3':0x1D6E,
           'r4':0x2CCC,'r5':0x2CEC,'r6':0x840,'r7':0x840}
    require(0x1EF1,'move #$02,n6');require(0x1F01,'do x:$003a,$1f0f')
    tail=affine_loop(rows,0x1F03,0x1F0F,32,bases,{'n6':2},
                    'VERIFIED conditional N=32/linear AGU/reviewed wrapper input')
    emit(out,'effect-tail-accesses.json',tail)
    xunion=merge([(int(r['start'],16),int(r['end_exclusive'],16)) for r in tail if r['space']=='X']+
                 [(0x1D6D,0x1D6E)])
    assert max(int(r['end_exclusive'],16) for r in xunion)==0x2D0C
    emit(out,'effect-X-union.json',{'scope':'selected1E15 tail and initialized cursor buffers only; NOT all normal effects',
      'intervals':xunion,'lowest':'0x1D6D','highest':'0x2D0B',
      'unresolved':['entry/dispatch index and table writer closure','other state-loaded effects/private-X accesses'],
      'no_candidate_overlap_under_premises':True})
    require(0x1FB2,'move #$002d70,r3')
    prefix=affine_loop(rows,0x1FBB,0x1FBE,32,{'r3':0x2D70,'r4':0x840},{'n3':2},
                      'VERIFIED conditional N=32/linear AGU')
    emit(out,'effect-prefix-accesses.json',prefix)
    # Signed24 y0 divided by2^17; ASL/ASR cancel in this small resulting range.
    require(0xC4E,'asr #$11,a,a')
    indices=range(-64,64);lookups=set()
    for band in range(8):
        for index in indices:
            for base in (0x1600+64*band,0x1640+64*band):lookups.update((base+index,base+index+1))
    for index in indices:
        for base in (0x1840,0x1880,0x18C0,0x1900):lookups.update((base+index,base+index+1))
    assert min(lookups)==0x15C0 and max(lookups)==0x1940
    emit(out,'coefficient-lookup-bounds.json',{'N1_N3_minimum':-64,'N1_N3_maximum':63,
      'X_read_hull_start':'0x15C0','X_read_hull_end_exclusive':'0x1941',
      'premises':'signed24 y0; band masked700000; legacy linear M1/M3; includes conservative lookahead beyond uploaded coefficients',
      'scope':'VERIFIED arithmetic bound, not a valid-preset coefficient-value proof'})
    resolved=merge([(int(r['start'],16),int(r['end_exclusive'],16)) for r in tail+prefix if r['space']=='X']+
        [(0,2),(0x7D,0x85),(0x15C0,0x1941),(0x1D3A,0x1D65),(0x1D6D,0x1D6E),
         (0x2C44,0x2CAA)])
    emit(out,'bounded-effect-subset.json',{'intervals':resolved,'lowest':'0x0','highest':'0x2DAE',
      'scope':'reviewed tail, scratch, coefficient helper and prefix subset; not universal normal union',
      'premises':'stock32/16 counts, initialized low cursors, linear modifiers; scalar state intervals are conservative hulls',
      'unknown_normal_owners':'effect-chain dispatch/table value producers and other state-loaded effect cursors'})
    targets=words[0x29F6:0x2A2D];assert len(targets)==55
    table=[{'index':i,'X_cell':hex(0x9DB+i),'P_value':hex(v),
       'algorithm_entry_plus_one':hex(v+1) if i<15 else None} for i,v in enumerate(targets)]
    assert 0x1E15 not in targets and all(v+1!=0x1E15 for v in targets)
    indirect=[{'PC':hex(pc),'instruction':r['text']} for pc,r in rows.items()
                if re.search(r'\b(?:jsr|jmp|bra|bsr) \(r[0-7]\)',r['text']) and not 0x2309<=pc<0x2599]
    assert len(indirect)==7
    emit(out,'effect-dispatch.json',{'table':table,'indirect_sites':indirect,
      'required_normal_domains':{'X95A':'0..7 (eight5-wrapper rows)','X95B..95F':'0..14 (algorithm marker entries)'},
      'factory':'zero-init supplies valid0 defaults; no literal store to95A..95F found, not an indirect-writer proof',
      'target_result':'1E15 absent from valid immutable table and its+1 algorithm entries',
      'unclosed':'normal producer/index domains, table preservation, and arbitrary computed entries; no dead-code assertion'})
    mods=[]
    for pc,r in rows.items():
        if re.search(r'\bm[1367]\b',r['text']) and not 0x2309<=pc<0x2599:
            mods.append({'PC':hex(pc),'instruction':r['text'],
             'scope':'byte-checked canonical reference; classify value producer/return path separately'})
    # M3 temporary mode584 torestore5BE is a branch/call-free segment.
    segment=[r for pc,r in rows.items() if 0x584<=pc<0x5BE]
    assert all(r['text'].split()[0] not in ('jsr','bsr','jmp','bra','rts','rti','do','dor','rep')
               and not r['text'].split()[0].startswith(('j','bs')) for r in segment)
    require(0x5BE,'movec y:$001a,m3')
    emit(out,'modifier-evidence.json',{'references':mods,'M3_local_restore':'VERIFIED584→5BE has no control transfer',
      'M6':'only explicit canonical modification is startup2780; direct census, not poisoned-code proof',
      'M7':'startuplinear;265=3FF restored27F; reviewed low output intervals exclude cursor tables in either mode',
      'architectural_premises':'SOURCE-DERIVED legacy EMA=0; concrete base/block needed for modulo; normal Y1A preservation still scoped'})
    dma_regs={0xFFFFEC-4*c+d:f'{name}{c}' for c in range(8)
              for d,name in enumerate(('DCR','DCO','DDR','DSR'))}
    dma=[]
    for pc,r in rows.items():
        for m in re.finditer(r'x:\$([0-9a-f]+)',r['text']):
            addr=int(m[1],16)
            if addr in dma_regs:
                dma.append({'PC':hex(pc),'register':dma_regs[addr],'instruction':r['text'],
                   'class':'INIT TABLE DATA, not instruction' if 0x2309<=pc<0x2599 else
                           'NORMAL ISR fixed rearm' if pc in (0x1BC,0x1BE) else
                           'INIT setup/enable' if 0x2A2D<=pc<=0x2A3E else 'UNRESOLVED'})
    assert all(x['class']!='UNRESOLVED' for x in dma)
    emit(out,'DMA-classified-census.json',{'entries':dma,
      'reviewed_targets':'DMA0Y[29,2C); DMA1fixedXperipheralFFFFA4; no privateX target',
      'normal_direct_reconfiguration':'VERIFIED only fixed DDR0/DSR1 rearm in this canonical census',
      'global_normal_indirect_configuration':'UNRESOLVED; e.g. P204B X:(R4) producer closure is separate'})
    pointer=int.from_bytes(arm[0x25F20:0x25F24],'little');assert pointer==0x80567EC
    wave=[]
    for i in range(9):
        off=pointer-0x8010000+12*i;count=int.from_bytes(arm[off+4:off+6],'little')
        assert count==256
        wave.append({'record':i,'ARM_record':hex(pointer+12*i),'word_count':count,
                    'X_stage_start':'0xC00','X_stage_end_exclusive':'0xD00'})
    emit(out,'mailbox-staging.json',{'records':wave,'loop':'ARM35EAA=9, recordstride12 at35ED8;16-bit transfer512bytes',
      'known_selectors':'0/2/3/4/5 Y output;7 X dest max1E8B; backup writes[C00,E00); workspace[2400,2800)',
      'candidate_exclusion':'VERIFIED recovered normal publisher families under retained modifier/staging premises',
      'universal_publisher_state_closure':'UNRESOLVED other normal indirect writes, not blocked byservice5E'})
    normal=list(csv.DictReader((ROOT/'builds/phase9/verified/normal-parameter-intervals.csv').open()))
    watched=[('X',0x95A,0x960),('X',0x9DB,0xA12),('Y',0x1820,0x1830),('Y',0x1A10,0x1A20)]
    coverage=[]
    for space,lo,hi in watched:
        hits=[r for r in normal if r['space']==space and int(r['start'],16)<hi and int(r['end_exclusive'],16)>lo]
        assert not hits
        coverage.append({'space':space,'start':hex(lo),'end_exclusive':hex(hi),'overlapping_recovered_parameter_intervals':hits})
    emit(out,'normal-parameter-exclusions.json',coverage)
    # Include concrete newly identified normal table-driven X write, not full-space guesses.
    emit(out,'normal-open-mechanisms.json',[
      {'PC':'P:DA3/DAD/DB2','source':'X95A..95F + X9DB..A12','unknown':'valid normal dispatch indices/table preservation'},
      {'PC':'P:2043/204B','source':'X364+5*k after X35F count/header; origin/count/record producer needed',
       'unknown':'R4 destination values must exclude candidate and DMA registers; algorithm arithmetic does not clamp addresses'},
      {'PC':'P:1EEF/1F0D/0E','source':'X1D3B saved incomingR7','unknown':'all actual entries, beyond recovered low wrapper family'},
      {'PC':'ARM48DAA','source':'paged external transfer count','unknown':'all normal count/end/wrap constraints; not service5E'},
      {'PC':'P:584/Y1A','source':'modifier state','unknown':'complete normal indirect producer closure and physical alias map'}])
    save(out/'dsp-witnesses.asm','\n'.join(r['line'] for pc,r in rows.items() if any(a<=pc<b for a,b in
       [(0x584,0x5BF),(0xD87,0xE18),(0x1E15,0x1F9B),(0x202B,0x204C),(0x22F8,0x2309),(0x260A,0x262B)]))+'\n')
    emit(out,'allocation-verdict.json',{'candidate':'X:[5F00,6000)','normal_runtime_safe':'NOT-YET-DETERMINED',
      'service_robust':'NO','service_overlap_is_normal_blocker':False,
      'normal_occupancy_witness':'none established','largest_verified_safe_subrange':None,
      'search':[{'words':n,'placements':257-n,'normal_verified_safe':[]} for n in (256,128,64)],
      'reason':'remaining NORMAL producer/AGU/stream and persistence closures; not service capability'})
    emit(out,'provenance.json',{'BIN_SHA256':sha(arm),'SYX_SHA256':sha(syx),'CRC':hex(d['crc']),
      'roundtrip_identical':True,'extract_hashes':hashes,'script_SHA256':sha(Path(__file__).read_bytes()),
      'mode':'STATIC ONLY; no ISA execution or firmware modification'})

if __name__=='__main__':main()
