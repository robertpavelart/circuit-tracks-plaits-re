#!/usr/bin/env python3
"""Phase15 static cursor-family ledger. No execution, packets, or device APIs.

Reuses existing inventories. Computes reviewed fixed-loop addresses; unknown
foreign aliases stay unknown. Requires a fresh explicit output directory.
"""
import argparse,csv,io,json,re
from pathlib import Path
from ct_static import ROOT,BIN_HASH,SYX_HASH,sha,save
from ct_resource_audit import read_rows
from ct_memory_ownership import affine_loop
import ct_fw_tool

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',required=True)
    out=Path(ap.parse_args().output_dir).resolve()
    if out.exists():raise SystemExit('Choose a fresh output directory')
    if out==ROOT/'original' or ROOT/'original' in out.parents:raise SystemExit('Protected original/')
    inputs={}
    def read(name):
        raw=(ROOT/name).read_bytes();inputs[name]=sha(raw);return raw
    def emit(name,obj):save(out/name,json.dumps(obj,indent=2,sort_keys=True)+'\n')
    arm=read('firmware/circuittracks-firmware-4486.bin')
    syx=read('original/circuittracks-firmware-4486.syx')
    assert sha(arm)==BIN_HASH and sha(syx)==SYX_HASH
    syxp=ROOT/'original/circuittracks-firmware-4486.syx'
    assert ct_fw_tool.decode_syx(syxp)['firmware']==arm
    assert ct_fw_tool.build_syx(syxp,arm)==syx
    manifest=json.loads(read('firmware/dsp/build-4486/manifest.json'))
    for block in manifest['blocks']:
        for kind in ('stream','payload'):
            raw=read('firmware/dsp/build-4486/'+block[kind+'_file'])
            assert sha(raw)==block[kind+'_sha256']
    payload=read('firmware/dsp/build-4486/selection0-channel0.payload24.bin')
    listing='builds/phase3-selection0-channel0.asm';read(listing)
    rows=read_rows(ROOT/listing,payload)
    def req(pc,text):assert rows[pc]['text']==text,(hex(pc),text)
    for pc,text in {
      0x1F5C:'move x:$1d40,r6',0x1F5E:'move x:$1d41,r5',0x1F60:'move x:$1d42,r4',
      0x1F64:'move #$fffffd,n4',0x1F66:'clr a #$fffffc,n5',
      0x1F68:'move y:>(r6+32),r1',0x1F6A:'move y:>(r6+33),r3',
      0x1F72:'do #$0010,$1f99',0x1F78:'jsr $0c9d',0x1F7F:'jsr $0c9d',
      0x1F89:'move y:>(r6+32),r7',0x1F8C:'move b,y:(r6)+',
      0x1F90:'do x:$003a,$1f98',0x1F93:'move x:(r7),b',
      0x1F95:'mac +y0,x0,b',0x1F97:'move b,x:(r7)+',
      0x1F98:'move a,y:(r6+47)',0x1F9A:'rts',
      0x1E80:'jsr $1f5c',0x1EE5:'jsr $1f5c',
      0x260A:'move #$001820,r0',0x260C:'move #$002ccc,x0',
      0x260E:'move #$002cec,x1',0x2610:'move #$001a10,r1',
      0x2612:'move #$002c02,y0',0x2614:'move #$002c24,y1',
      0x261A:'do #$0008,$2624',0x2780:'movec m0,m6',
      0x2781:'movec m0,m7',0x265:'movec #$0003ff,m7',
      0x27F:'movec y:$001a,m7',0x27FA:'move r0,y:$001a',
      0x25E4:'jsr $260a',0x1F13:'move x:$1d3d,a',
      0x1F28:'sub a,b x:$1d41,r0',0x1F2A:'move x:$1d40,r4',
      0x1F2D:'do #$0010,$1f5a',0x1F2F:'do #$0002,$1f55',
      0x1F4D:'move a,y:(r0)+',0x1F4F:'move x1,y:(r0)+',0x1F53:'move x1,y:(r0)+',
      0x148:'sub x1,a a,x:(r0)+ a,y0',0x149:'sub x1,b b,x:(r0)+',
    }.items():req(pc,text)
    c9=[r['text'] for p,r in rows.items() if 0xC9D<=p<=0xCB7]
    assert not any(re.search(r'\br[067]\b|\bm[67]\b',t) for t in c9)
    # N4=-3 makes the four coefficient reads return R4 to its initial value.
    # Only the four final Y stores then advance it. Inner DSP arithmetic is NOT
    # interpreted; address effects below are reviewed operands only.
    req(0xCA0,'move x1,x:(r1)+ y:(r4)+n4,b')
    assert sum('y:(r4)+' in t and ',y:(r4)+' not in t for t in c9)==4
    assert sum(bool(re.search(r',y:\(r4\)\+',t)) for t in c9)==4
    # Ten coefficient reads per reviewed two-sample DO body. The two -4
    # updates balance eight +1 updates, so R5 returns to its prefetched offset1.
    # Static operand arithmetic only, not instruction/data execution.
    coef_pos=1;coef_offsets=[]
    for p,r in sorted(rows.items()):
        if not 0xCA6<=p<0xCB0:continue
        for m in re.finditer(r'y:\(r5\)\+(n5)?',r['text']):
            coef_offsets.append(coef_pos);coef_pos+=-4 if m[1] else 1
    assert coef_pos==1 and set(coef_offsets)==set(range(5)) and len(coef_offsets)==10
    emit('helper-address-proof.json',{'C9D':'R6/R7/M6/M7/R0 not used/modified; preserves cursor source register',
       'R4_reads':'four reads atC..C+3, postincrements1+1+1-3=0',
       'R4_writes':'four stores CB2..CB5 atC..C+3, finalR4=C+4',
       'R5_prefetch':'CA3 reads coefficientC and incrementsR5 toC+1',
       'R5_DO_body_offsets':coef_offsets,'R5_DO_body_net_delta':0,
       'R5_after_return':'C+1; caller1F79/80 subtractN5=-4, giving next5-word coefficient set',
       'conditional_R5_read_regions':['Y[1840,18E0)','Y[1A30,1AD0)'],
       'cursor_table_read_or_write_in_helper':False,
       'stock_helper_DO_count_X3B':16,
       'count_source':'140..149 stores pre-subtractionB=16 atX3B; X3C=31 is a different field',
       'premises':'reviewed caller bases; N4=-3/N5=-4; stock X3B=16; linear M4/M5; normal entry/context preserved'})
    init=affine_loop(rows,0x261C,0x2624,8,{'r0':0x1820,'r1':0x1A10,'r3':0x1D53})
    emit('INIT-cursor-stores.json',{'loop':init,'caller':'25E4→260A','values':'alternating constants, eight pairs per table',
      'earlier_clear':'2789 zeroesY[0,6000) before pointer initialization; normal use requires later initialization'})
    cells=[]
    for tag,base,table,bases in [('A',0x1800,0x1820,(0x2CCC,0x2CEC)),('B',0x19F0,0x1A10,(0x2C02,0x2C24))]:
        for j in range(16):
            c=bases[j%2];linear=[c+i for i in range(32)]
            ring=[(c&~0x3FF)+((c+i)&0x3FF) for i in range(32)]
            assert linear==ring and not any(0x340<=a<0x360 for a in linear)
            cells.append({'family':tag,'outer_index':j,'Y_cell':hex(table+j),'initial_value':hex(c),
               'value_kind':'absolute X address, not relative/table index',
               'init_writer_PC':hex((0x261C if tag=='A' else 0x261E)+(j%2)),
               'consumer_PC':'0x1F89→0x1F93/0x1F97','conditional_X_start':hex(c),
               'conditional_X_end_exclusive':hex(c+32),'R7_after_inner_loop':hex(c+32),
               'cursor_Y_writeback':False,'runtime_delta_to_stored_cell':0,
               'linear_and_3FF_ring_same':True,'intersects_X_340_360':False,'writes_X35F':False,
               'global_runtime_value':'UNRESOLVED foreign aliases/entry/modifier/state preservation',
               'first_clear_reader':'1F68' if j==0 else '1F6A' if j==1 else 'not read by initial two-buffer clear'})
    emit('cursor-table.json',{'cells':cells,'count':32,'scope':'complete for recovered caller bases and linearM6; corrupted/arbitraryR6 source cells unclosed'})
    buf=io.StringIO();writer=csv.DictWriter(buf,fieldnames=list(cells[0]));writer.writeheader();writer.writerows(cells)
    save(out/'cursor-table.csv',buf.getvalue())
    emit('X-reach.json',{'family_A_union':[['0x2CCC','0x2D0C']],
         'family_B_union':[['0x2C02','0x2C22'],['0x2C24','0x2C44']],
         'words_written_per_invocation':512,'distinct_X_addresses_per_family':64,
         'stores_per_cursor':32,'outer_count':16,
         'reload_each_outer_iteration':True,'persistent_table_delta_within_function':0,
         'premises':'initialized cursor cells; X3A=32; R6/R7 modes legacy linear or reviewed3FF output ring; normal entry/context intact',
         'conditional_340_360_result':'VERIFIED NO','conditional_35F_result':'VERIFIED NO',
         'universal_normal_result':'NOT-YET-DETERMINED'})
    # Distinguish full interval intersection from hitting the count word alone.
    for c in [0x320,0x321,0x33F,0x340,0x35F,0x360,0xFFFFF0]:
        addresses=[(c+i)&0xFFFFFF for i in range(32)]
        assert any(0x340<=a<0x360 for a in addresses)==(0x321<=c<0x360)
        assert (0x35F in addresses)==(0x340<=c<0x360)
    assert not any(0x321<=q<<8<0x360 for q in range(65536))
    emit('alias-conditions.json',{'N':32,'modifier':'legacy linear,24-bit wrap',
         'interval_target':['0x340','0x360'],'forbidden_base_for_any_interval_overlap':['0x321','0x360'],
         'forbidden_base_for_X35F':['0x340','0x360'],
         'formula':'[c,c+32) intersects[340,360) iff321<=c<360; contains35F iff340<=c<360 (wrap does not add low340 addresses in32 steps)',
         'boundary_fixtures':'static address arithmetic, NOT normal-state counterexamples',
         '16bit_SHI_direct_cursor_write':'received word has low8bits zero; no multiple256 in either forbidden interval; excludes direct dangerous cursor publication under reviewed modes/count',
         'service5E_private_direct_cursor_write':'value0; with preserved base/count/linear mode writes[0,20), excludes target/count',
         'limitations':'neither lemma protects source-base/count/modifier redirection or24bit/DSP foreign writers'})
    # Local routine and coefficient-helper write footprints, not a global Y census.
    local=[]
    for tag,base,coef,state in [('A',0x1800,0x1840,0x18E0),('B',0x19F0,0x1A30,0x1AD0)]:
        table_lo=base+32;table_hi=table_lo+16
        bands=[('1F8C',base,base+16,'peak/state output; R6 increments once per outer iteration'),
               ('1F98',base+48,base+64,'A-state output after R6 increment; uses+47'),
               ('C9D→CB2..CB5',state,state+128,'two calls*four Y stores*16 outer iterations; R4 advances8 per outer'),
               ('1F13→1F4D/4F/53',coef,coef+160,'16*2*5 sequential Y stores; C3E does not modifyR0'),
               ('1E6C/1EBF',base+16,base+32,'16 coefficient/control writes preceding cursor table'),
               ('1E57',0x1830,0x1840,'16 state/control words for first family')]
        for pc,lo,hi,why in bands:
            assert not (lo<table_hi and hi>table_lo)
            local.append({'family':tag,'writer':pc,'Y_start':hex(lo),'Y_end_exclusive':hex(hi),
              'aliases_cursor_table':False,'premise':'reviewed fixed bases, loops and linear M0/M4/M6',
              'formula':why,'global_mode':'UNRESOLVED actual normal entry'})
    # C3E only writes to fixed temporary coefficient buffers on this path.
    assert not any(re.search(r'\br0\b',r['text']) for p,r in rows.items() if 0xC3E<=p<=0xC87)
    local.append({'writer':'1F43→C3E','Y_start':'0xF63','Y_end_exclusive':'0xF78',
       'aliases_cursor_table':False,'premise':'R5=F68/R6=F6D/R7=F77 at1F36/3D/40; decrement operands only',
       'formula':'conservative hull of temporary Y writes; not a full effect footprint'})
    emit('local-mutation-exclusions.json',local)
    # Verify there is no cursor writeback in the reviewed consumer, and no
    # hidden R6 assignment in callees that would invalidate j-based source cells.
    effect_refs=[]
    for pc,r in rows.items():
        if 0x1E15<=pc<=0x1F9A and re.search(r',y:',r['text']):
            effect_refs.append({'PC':hex(pc),'instruction':r['text'],'scope':'local reviewed write operand; full foreign closure separate'})
    emit('local-Y-store-operand-evidence.json',effect_refs)
    read('builds/phase14/current/possible-indirect-aliases.json')
    old_inventory=list(csv.DictReader(io.StringIO(read('builds/phase6b/indirect-origins.csv').decode())))
    # Reuse only pre-existing foreign Y write candidates, targeted to preservation
    # of32 watched cells. No new broad alias census is produced.
    inherited=[]
    for r in old_inventory:
        if r['program']!='selection0-channel0' or r['space']!='Y':continue
        if not re.search(r',y:',r['instruction']) and not r['instruction'].startswith(('bclr ','bset ','bchg ')):continue
        pc=int(r['pc'].split(':')[1],16)
        if 0x1E15<=pc<=0x1F9A or 0x2309<=pc<0x2599:continue
        inherited.append({'PC':r['pc'],'instruction':r['instruction'],'lexical_hint':r['lexical_constant_origin'],
           'status':'INHERITED UNRESOLVED possible foreign cursor-cell alias; not actual normal reachability',
           'source':'phase6b/indirect-origins.csv; not newly enumerated firmware'})
    emit('inherited-cursor-preservation-obligations.json',{'watched':['Y[1820,1830)','Y[1A10,1A20)'],
         'entries':inherited,'scope':'reused old Y-write candidates for watched cells only; old inventory may include other data decodes; no reachability claim'})
    params=list(csv.DictReader(io.StringIO(read('builds/phase9/verified/parameter-writes.csv').decode())))
    hits=[r for r in params if r['space']=='Y' and (0x1820<=int(r['address'])<0x1830 or 0x1A10<=int(r['address'])<0x1A20)]
    assert not hits
    emit('writers-readers.json',{'known_table_writers':[
         {'writer':'2789','class':'BOOT/INIT','value':0,'domain':'initialY[0,6000) clear'},
         {'writer':'261C/261D','class':'BOOT/INIT','domain':'1820..182F','value':'2CCC/2CEC alternating'},
         {'writer':'261E/261F','class':'BOOT/INIT','domain':'1A10..1A1F','value':'2C02/2C24 alternating'},
         {'writer':'SHI19B','class':'normal/service transport; complete normal endpoints UNRESOLVED',
          'value':'receivedX0','domain':'Y through X10/X11; accepts watched Y starts at instruction level'},
         {'writer':'5E→SHI19B','class':'SERVICE/DIAGNOSTIC','value':0,'domain':'private Y watched cells accepted; not normal publisher'},
         {'writer':'foreign DSP Y stores','class':'UNRESOLVED','domain':'see inherited watched-cell obligations','value':'UNRESOLVED'},
       ],'known_readers':['1F68: first cursor','1F6A: second cursor','1F89: all16 in selected family'],
       'recovered_normal_ARM_parameter_writers':hits,
       'runtime_local_cursor_update_formula':'c_next=c_old; no stores to table in reviewed path',
       'absolute_direct_operand_search':'watched-table direct operands not used; addresses constructed fromR6 orINITR0/R1; foreign indirect readers/writers not universally closed'})
    dispatch=json.loads(read('builds/phase12/final/effect-dispatch.json'))
    assert all(int(t['P_value'],16) not in (0x1E14,0x1E15,0x1F5C,0x1F97) for t in dispatch['table'])
    targets=[]
    for pc,r in rows.items():
        if r['text'].split()[0].startswith(('jsr','jmp','bsr','bra')) and re.search(r'\$1f5c\b',r['text']):
            targets.append({'PC':hex(pc),'instruction':r['text'],'class':'UNRESOLVED actual normal entry; local effect branch',
                            'role_if_parent_reached':'NORMAL EFFECT candidate, not boot initializer'})
    assert {int(r['PC'],16) for r in targets}=={0x1E80,0x1EE5}
    emit('entry-modifier-ledger.json',{'function':'1F5C..1F9A inclusive; end-exclusive1F9B',
       'parent':'1E15..1F10 effect routine; actual normal reachability unclosed',
       'direct_callers':targets,'direct_entry_to_1F97':'none;1F90 DO-end operand is not a call',
       'immutable_valid_dispatch_exclusion':'prior55-entry table and algorithm+1 targets exclude1E15; index/table preservation still unresolved',
       'INIT_only_related':'1F9B→1F13 coefficient setup, not a1F5C call;260A pointer initialization',
       'R6_source':'X1D40 overwritten1800 at1E76 or19F0 at1ED9 before local calls; async foreign clobber not globally excluded',
       'R5_source':'X1D41=1840/1A30','R4_source':'X1D42=18E0/1AD0',
       'M6':'explicit INIT2780=FFFF; local consumer/helper do not changeM6',
       'M7':'INIT2781=FFFF; temporary265=3FF restored27F fromY1A; local consumer/helper do not changeM7',
       'Y1A':'INIT27FA=FFFF; known parameter Y minimumFD excludes1A, foreign Y writer closure unresolved'})
    emit('async-ledger.json',[
       {'path':'SHI156→198/199→19B','cursor_mutation':'possible Y write through saved pointer; normal24bit endpoint exclusion unclosed',
        'registers':'saves/restoresR0/M0/X0/A as applicable; no directR6/R7/M6/M7 modification in reviewed ISR'},
       {'path':'audio ISR1B4..1D8','cursor_mutation':'reviewed low Y21/22/29/2A,F3F/F40,input ring1000..1400, not cursor tables',
        'registers':'reviewed R0/M0/N0,Y0/Y1 save/restore; no directR6/R7/M6/M7 update'},
       {'path':'mailbox1C53/1D41','cursor_mutation':'Y output through saved/generatedR5; recovered low/external jobs scoped, universal publisher/context/end exclusion unresolved'},
       {'path':'worker/channel1','cursor_mutation':'separate private state/shared queue; no direct watched Y publisher established; physical alias/queue state remains conditional'},
       {'path':'5E privateY utility','cursor_mutation':'SERVICE-only0 publication; no direct forbidden cursor under stock mode, but can corrupt other context; not normal proof blocker'}])
    plan={'performed':False,'firmware_modification_required_or_authorized':False,
       'availability':'UNRESOLVED nonhalting/read-only trace capability; no debug port, trace pins or address access verified',
       'minimum_invariant_event':['each normal PC203A entry','effective load address35F','24bit word read'],
       'minimum_family_event':['normal PC1F97 write','effective X address','24bit data written'],
       'optional_attribution':['R6 and source Y cell/value at1F89','M7 and SR mode','actual caller','inner countX3A/LC'],
       'coverage':'user-operated stock notes/release, patch/bank/effect, scene/project/transport and ordinary audio blocks; boot/service separated',
       'acceptance':'any nonzero35F at normal203A disproves invariant for that trace; all-zero finite trace supports only observed coverage',
       'constraints':'future explicit hardware-observation authorization needed; no activeMIDI/SysEx, firmware patches, logging writes, breakpoints/halts assumed safe',
       'insufficient':'occasional RAM snapshots or passive SPI alone cannot exclude transient internal DSP writes at the count load',
       'fallback':'if suitable passive trace unavailable, retainUNRESOLVED; do not substitute a firmware patch or debugger action'}
    emit('observation-plan.json',plan)
    emit('verdict.json',{'family_interval_normal':'NOT-YET-DETERMINED','family_X35F_normal':'NOT-YET-DETERMINED',
       'family_removed_from_blockers':False,'X35F_invariant':'NOT-YET-DETERMINED',
       'local_initialized_family_interval':'VERIFIED NO','local_initialized_family_X35F':'VERIFIED NO',
       'normal_dangerous_cursor_publisher':'none established','new_broad_alias_census':False,
       'static_stopping':'reviewed cursor routine closed locally; global question still rests on generic foreign writers/entry/modifier premises',
       'diminishing_returns':True,'another_broad_static_phase_justified':False,
       'static_impossibility_proved':False,
       'next':'assess whether an existing read-only nonhalting trace can capture203A count loads and1F97 effective writes; any hardware use requires new authorization'})
    windows=[(0x140,0x156),(0x1E15,0x1F9B),(0x260A,0x2624),(0xC3E,0xCB8),(0x265,0x280),
             (0x2779,0x278A),(0x27F8,0x27FC)]
    save(out/'dsp-witnesses.asm','\n'.join(rows[p]['line'] for p in sorted(rows) if any(a<=p<b for a,b in windows))+'\n')
    for name,h in inputs.items():assert sha((ROOT/name).read_bytes())==h
    emit('validation.json',{'inputs_SHA256':inputs,'script_SHA256':sha(Path(__file__).read_bytes()),
       'original_hashes_match':True,'all_five_extract_pairs_match':True,'decoded_BIN_equal':True,
       'SYX_roundtrip_equal':True,'DSP_listing_bytes_checked':True,'execution':'STATIC arithmetic and reviewed address operands only',
       'cursor_cells':32,'inherited_foreign_Y_write_candidates':len(inherited)})

if __name__=='__main__':main()
