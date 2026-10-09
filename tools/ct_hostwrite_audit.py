"""Targeted offline HOSTWRITE ledger and interval algebra. No CPU/packets/devices.
Uses existing byte-checked ARM probe and prior finite-domain evidence. Does not
declare a complete NORMAL graph from a syntactic direct-edge inventory.
"""
import argparse,csv,io,json,re
from pathlib import Path
from ct_stock_load_audit import ROOT,verify_inputs,rows,sha
from ct_arm_init_cache import recover

MOD=1<<24
WATCH={'selectors':[0x95a,0x960],'effect_table':[0x9db,0xa12]}
DESCRIPTORS=[0xeb+8*i for i in range(14)]


def intervals(start,count):
    if not 0<=start<MOD or count<0:raise ValueError('Require24-bit start and nonnegative count')
    if count==0:return []
    if count>=MOD:return [[0,MOD]]
    end=start+count
    return [[start,end]] if end<=MOD else [[start,MOD],[0,end-MOD]]


def hits(parts):
    result=[name for name,(a,b) in WATCH.items() if any(lo<b and hi>a for lo,hi in parts)]
    result.extend('descriptor'+str(i) for i,a in enumerate(DESCRIPTORS) if any(lo<=a<hi for lo,hi in parts))
    return result


def asset_advance(length):
    if not 0<=length<1<<32:raise ValueError('Require32-bit metadata length')
    return ((length&~511)>>1)+256


def collect(out,probe):
    out=out.resolve();base=(ROOT/'builds/phase19c-hostwrite').resolve();probe=probe.resolve()
    if out.exists() or out==base or not out.is_relative_to(base):raise ValueError('Fresh HOSTWRITE child required')
    payload,protected=verify_inputs();inputs={}
    def read(n):
        p=ROOT/n;raw=p.read_bytes();inputs[n]=sha(raw);return raw
    def old(n):return json.loads(read(n))
    def csvread(n):return list(csv.DictReader(io.StringIO(read(n).decode())))
    def emit(n,v):
        with (out/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
    def csvout(n,v):
        keys=sorted(set().union(*(x.keys() for x in v))) if v else ['status']
        with (out/n).open('x',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(v)
    arm=read('firmware/circuittracks-firmware-4486.bin')
    read('original/circuittracks-firmware-4486.syx')
    manifest=old('firmware/dsp/build-4486/manifest.json')
    for x in manifest['blocks']:
        for k in ['stream','payload']:assert sha(read('firmware/dsp/build-4486/'+x[k+'_file']))==x[k+'_sha256']
    import ct_fw_tool
    syx=ROOT/'original/circuittracks-firmware-4486.syx'
    assert ct_fw_tool.decode_syx(syx)['firmware']==arm and ct_fw_tool.build_syx(syx,arm)==syx.read_bytes()
    for n,h in json.loads((probe/'hashes.json').read_text()).items():
        raw=read((probe/n).relative_to(ROOT).as_posix());assert sha(raw)==h,n
    pmeta=old((probe/'provenance.json').relative_to(ROOT).as_posix())
    assert pmeta['source_sha256']==sha(read('tools/ct_hostwrite_probe.py'))
    calls=old((probe/'targeted-calls.json').relative_to(ROOT).as_posix())
    instructions=old((probe/'instructions.json').relative_to(ROOT).as_posix())
    bypc={x['PC']:x for x in instructions}
    for x in instructions+calls:
        raw=bytes.fromhex(x['raw']);assert arm[x['PC']-0x8010000:x['PC']-0x8010000+len(raw)]==raw
    def req(pc,mn,fragment):
        x=bypc[pc];assert x['mnemonic']==mn and fragment in x['operands'],(hex(pc),x)
    for pc,mn,fragment in [(0x8029300,'ldrh','[r7]'),(0x8029306,'cmp','r6, r1'),
        (0x8029340,'strh','[r7]'),(0x80293c2,'mov.w','#0x2000'),
        (0x802942c,'strh','[r7]'),(0x8029488,'strh.w','[r8]'),(0x80295a4,'strh','[r1]'),
        (0x80596e4,'subs','r1, r1, #1'),(0x8059716,'ldrb','[r3], #1'),
        (0x8049a24,'mov.w','#0x580000'),(0x8049a6a,'adds','r4, r0, r4'),
        (0x8049afc,'lsls','r6, r6, #9'),(0x8049b06,'add.w','#0x100'),
        (0x8049b14,'cmp.w','#0xe80000'),(0x8049b58,'bl','#0x80296b0'),
        (0x8049b94,'bl','#0x802968e')]:req(pc,mn,fragment)
    cache,tokens,init=recover();assert init['cache_value']==0xffff
    assert init['decoded_sha256']=='2db584abde65123402067c89720f5a10e12c40650b700d6af2f13ed93743e04f'
    oldcallers=old('builds/phase6c/final/host-callers.json');oldby={int(x['site'],16):x for x in oldcallers}
    params=csvread('builds/phase9/verified/parameter-writes.csv')
    special=csvread('builds/phase9/verified/special-destinations.csv')
    suffixes=csvread('builds/phase6c/final/normal-host-intervals.csv')
    staging=old('builds/phase12/final/mailbox-staging.json')
    stream=old('builds/phase14/current/host-stream-count-proof.json')
    bridge=old('builds/phase19c-targetbridge/final-v2/result.json')
    read('builds/phase3-selection0-channel0.asm');dsp=rows(ROOT/'builds/phase3-selection0-channel0.asm',payload)
    for n in ['builds/phase4-arm-events.asm','builds/phase4-arm-release.asm','builds/phase4-arm-inputs.asm']:
        raw=read(n).decode()
        for l in raw.splitlines():
            m=re.match(r'([0-9A-F]{8})\s+([0-9a-f]+)\s+',l)
            if m:
                pc=int(m[1],16);b=bytes.fromhex(m[2]);assert arm[pc-0x8010000:pc-0x8010000+len(b)]==b
    out.mkdir(parents=True)
    with (out/'arm-initialized-data.bin').open('xb') as f:f.write(cache)
    emit('arm-cache-init.json',init);emit('arm-init-codec-records.json',tokens)
    copy=(probe/'arm-windows.asm').read_bytes()
    with (out/'arm-witnesses.asm').open('xb') as f:f.write(copy)
    callledger=[]
    for c in calls:
        pc=c['PC'];prior=oldby.get(pc)
        pmap=[p for p in params if (m:=re.search(r'0x([0-9a-fA-F]+)',p['site'])) and int(m[1],16)==pc]
        mode='UNRESOLVED';evidence='No complete normal ancestry/argument proof'
        if pmap:mode='NORMAL UI/PARAMETER';evidence='Recovered Phase9 serialized bank/slot callback domains; helper reuse not universal'
        elif 0x80269e4<=pc<0x8026b24:mode='SERVICE';evidence='Recovered5E utility only'
        elif 0x8029050<=pc<0x8029190:mode='SERVICE';evidence='Diagnostic wrapper family; all alternate ancestry not globally closed'
        elif 0x8029382<=pc<0x8029492:mode='BOOT/INIT';evidence='Original numeric-table upload loop; reentry can repeat it'
        elif prior and prior['mode'].startswith('NORMAL AUDIO'):mode='NORMAL AUDIO';evidence=prior['mode_evidence']
        elif pc in [0x803cc46,0x805bfd0]:evidence='Asset-loader caller; exact normal project/init ancestry requires upstream proof'
        elif pc==0x8049a66:evidence='Asset loop49A1C, index0..63; actual normal transition ancestry incomplete'
        dest=prior.get('destination_value') if prior else None
        callledger.append(dict(c,classification=mode,classification_evidence=evidence,
            caller_function=sorted({p['root'] for p in pmap}) if pmap else None,
            address_argument=prior.get('argument') if prior else None,
            destination_source=dest or 'See helper/family summary; inherited/cached/computed remains explicit',
            space='encodedbit15/private, retainedX11/page, or inherited caller context',
            payload_width='24 scalar / upper16 extended /16or24 bulk as selected by helper',
            count='1 per scalar; byte-length/width for bulk; see transaction rows',
            cache_reuse='292F8/29314 share halfword cache; primitive data sinks inherit DSP cursor',
            parameter_cases=len(pmap),complete_NORMAL_graph=False))
    emit('caller-ledger.json',dict(status='VERIFIED targeted direct-edge inventory; complete all-NORMAL caller set UNRESOLVED',
        candidates=len(calls),entries=callledger,actual_normal_indirect_ancestry_closed=False,
        note='Family labels classify reviewed code/premises; candidates are not all actual reachable normal calls'))
    scalar=[]
    for p in params:
        a=int(p['address']);n=int(p['words']);parts=intervals(a,n)
        scalar.append(dict(p,kind='24bit scalar',target_hits=hits(parts) if p['space']=='X' else [],
            destination_start=a,count=n,stride=1,end_exclusive=a+n,
            endpoint_status='EXCLUDED nominal endpoints under recovered bank/slot premises',
            effective_cached_destination='UNRESOLVED until corresponding cache/DSP cursor context coherent'))
    for x in special:
        a=int(x['start'],16);n=int(x['words']);parts=intervals(a,n)
        scalar.append(dict(x,kind='24bit scalar special/deferred',target_hits=hits(parts) if x['space']=='X' else [],
            destination_start=a,count=n,stride=1,end_exclusive=a+n,
            endpoint_status='EXCLUDED nominal fixed special destinations',effective_cached_destination='UNRESOLVED context preservation'))
    # Endpoint-only rows avoid treating sparse +7 publication as a descriptor hull.
    for i in range(12):
        for a,site,why in [(0xf2+8*i,0x8021a08,'descriptor+7 bank field'),(0x57a+0x4a*i,0x802126e,'normal event mailbox')]:
            scalar.append(dict(kind='24bit scalar event',site=hex(site),slot=i,space='X',destination_start=a,
                count=1,stride=1,end_exclusive=a+1,target_hits=hits(intervals(a,1)),
                endpoint_status='EXCLUDED recovered slot0..11 nominal address',effective_cached_destination='UNRESOLVED all-normal cursor retention',source=why))
    for a in range(0x9f,0xa3):
        scalar.append(dict(kind='24bit scalar localmask',site='0x08051B6C',space='X',destination_start=a,
            count=1,stride=1,end_exclusive=a+1,target_hits=hits(intervals(a,1)),endpoint_status='EXCLUDED for any input:r0&3 plus9F',effective_cached_destination='UNRESOLVED caller/cursor context'))
    for a in range(0x99,0x9d):
        scalar.append(dict(kind='24bit scalar localmask',site='0x08051B7C',space='X',destination_start=a,
            count=1,stride=1,end_exclusive=a+1,target_hits=hits(intervals(a,1)),endpoint_status='EXCLUDED for any input:r0&3 plus99',effective_cached_destination='UNRESOLVED caller/cursor context'))
    for x in suffixes:
        if x['operation']!='write':continue
        a=int(x['start'],16);n=int(x['end_exclusive'],16)-a
        scalar.append(dict(x,kind='24bit scalar constant suffix',destination_start=a,count=n,stride=1,end_exclusive=a+n,
            target_hits=hits(intervals(a,n)) if x['space']=='X' else [],
            endpoint_status='EXCLUDED nominal suffix only; code/caller context retained',effective_cached_destination='UNRESOLVED cache retention'))
    assert all(not x['target_hits'] for x in scalar)
    csvout('scalar-endpoints.csv',scalar)
    emit('scalar-summary.json',dict(status='EXCLUDED recovered nominal endpoints; not universal effective-destination exclusion',
        parameter_expansions=len(params),parameter_unique_X=len({p['encoded'] for p in params if p['space']=='X'}),
        parameter_unique_Y=len({p['encoded'] for p in params if p['space']=='Y'}),
        maximum_parameter_X=max(int(p['address']) for p in params if p['space']=='X'),rows=len(scalar),target_hits=[],
        known_sink_51B54=dict(mask=3,destinations1=[0x9f,0xa3],destinations2=[0x99,0x9d],caller=0x8049826),
        unresolved='All-normal caller coverage, cursor/cache hits, aliases and bulk interleaving'))
    bulk=[]
    for x in staging['records']:
        s=0xc00;n=x['word_count'];bulk.append(dict(family='35E28 fixed staging',classification='BOOT/INIT or recovered table-builder reentry',
            record=x['record'],sink=0x8035eee,start=s,count=n,stride=1,end_exclusive=s+n,wire_bytes=n*2,width=16,
            nominal_hits=hits(intervals(s,n)),status='EXCLUDED transaction footprint if explicit privateC00 setup/width/cursor retained',
            continuity='C00 address explicitly reset at35EC8 before each record; no automaticcache update in bulk sink'))
    s=int(stream['initial_pointer_after_page_compensation'],16);end=int(stream['end_exclusive'],16)
    bulk.append(dict(family='395BC→395EC→48DAA',classification='UNRESOLVED complete normal/init mode ancestry',
        sink=0x8048e26,start=s,count=end-s,stride=1,end_exclusive=end,width=16,
        wire_bytes=stream['bytes']+4,prefill_words=2,nominal_hits=hits(intervals(s,end-s)),
        status='EXCLUDED recovered2740C-byte record; global count/cursor preservation UNRESOLVED',
        continuity='48DCA page setter; two actual prefills48DE6..48E02; then <=4096-byte continued chunks'))
    bulk.append(dict(family='49A1C→49A66→49A80',classification='UNRESOLVED normal project/session or INIT ancestry',
        sink=[0x8049b58,0x8049b94],initial_argument=0x580000,initial_effective_start=0x57fffe,
        count='Successful main chunks +256 unconditional padding words',stride=1,width=16,
        address_formula='A[j+1]=(A[j]+advance(L[j])) mod2^32; page=((A[j]>>8)&FFFF); start=(page<<8)-2 mod2^24',
        length_formula='R8=256+((L&FFFFFE00)>>1) for valid header; invalid header retains256',
        main_guard='VirtualR4+chunk_bytes/2 <E80000 before emission; chunk_bytes<=2048',
        padding='49B94 sends512 bytes=256 zero words without new address; guard does not cover padding',
        status='First retained580000 transaction excludes requested cells under ordered protocol; all64 starts/count/cursor contexts UNRESOLVED',
        nominal_hits=None,copy_prefill_48DAA=False,normal_length_limits=None))
    emit('bulk-endpoints.json',bulk)
    emit('width-endpoints.json',dict(status='UNRESOLVED universal normal width/bulk closure',
        extended_scalar_29314=dict(direct_caller=0x8026a76,classification='SERVICE-ONLY recovered5E',normal_direct_caller_recovered=False,
            word_value='(source&FFFF)<<8',destination='Explicit18-bit header on cache miss; retainedX11.bit15 and cursor on cache hit',
            width_constraint_not_destination_safety=True),
        switch_to16=dict(ARM=0x80295e4,command='X12 bit21/bit8; foreground12D chooses HCSR0010A4'),
        restore24=dict(ARM=0x8029626,command='16-bit command2000 left-aligned200000; foreground12D HCSR0010A8'),
        frame_predicate='Ordered complete words in correct mode, synchronized framing/controller state; not stock IRQ/timing replay',
        bulk='See exact staging/selected stream and unresolved asset transactions; never exclude by data width alone'))
    emit('cache-semantics.json',dict(status='VERIFIED INIT/local instructions; all-normal coherence UNRESOLVED',
        address=0x20003d00,size_bytes=2,initialized_value=0xffff,init_evidence='Decoded original ARM record ending20003D02',
        comparison_sites=[0x8029306,0x802932a],predicate='requested32-bitR6 == zero-extended cached16-bit halfword',
        cache_hit='No address setup; data sink uses current selected-port DSP X10/X11',
        scalar_update=0x8029340,formula='low16(requested+1)',
        other_updates=[dict(PC=0x802942c,value='low16(loop address+1)'),dict(PC=0x8029488,value='low16(filter loop address+1)')],
        bulk_read_invalidation=dict(PC=0x80295a4,value=0xffff),
        reviewed_no_invalidation=['29344 scalarread','295BA extended scalarread','292DC/294AC/294CA address setters','295E4/29626 width controls','2968E/296B0 bulk writes'],
        keys=['address halfword only'],missing_keys=['DSP port','memory space as independent state','word width','DSP-read cursor generation'],
        scalar24='Explicit private header sets X10/X11 when miss; hit inherits both',
        scalar16='18-bit address setter writesX10; write form retainsX11; R6>FFFF can never equal cache',
        lifetime='Across independent operations; reviewed setters/read/write paths do not universally synchronize it',
        literal_census='Only aligned/exact literal20003D00 at29674; not proof against constructed/indirect ARM writes',
        unresolved=['All normal call ordering and cache-hit start domains','cross-port/width reuse','indirect ARM cache aliases','DSP foreign X10/X11 writers independent of host']))
    direct={a:[] for a in [0x10,0x11]}
    excluded_data=[]
    for pc,x in dsp.items():
        if x['text'].split()[0] in ['jclr','jset','brclr','brset','btst','do']:continue
        for a in direct:
            if re.search(r',[xl]:\$'+f'{a:04x}'+r'\b',x['text']):
                if 0x2309<=pc<0x2599:excluded_data.append(x)
                else:direct[a].append(x)
    assert [x['PC'] for x in direct[0x10]]==[0x175,0x17d,0x186,0x190,0x19e,0x1ac]
    assert [x['PC'] for x in direct[0x11]]==[0x185,0x189]
    emit('DSP-cursor-lifecycle.json',dict(status='VERIFIED valid handler semantics; foreign indirect aliases not closed',
        INIT_clear=dict(PC=0x2788,X10=0,X11=0),direct_writers={hex(a):x for a,x in direct.items()},excluded_DATA=excluded_data,
        private_setup='181..186: X10=header&7FFF; X11=header; bit15 selectsY, otherwiseX',
        extended_write_setup='179..180: X10=header&3FFFF; X11 NOT rewritten unless readflag bit23 takes188',
        page_write_setup='171..178: X10=page<<8 minus2; X11 NOT rewritten unless readflag bit23 takes188',
        address_read='188..190: X11=header, target prefetch then cursor+1 storedX10',
        data_write='198..19E: target store19D(X) or19B(Y), then X10=R0postinc',
        read_next='1A0..1AC: currentX11 selects space, prefetch and cursor+1',
        scalar_read='29344/29504 combines address-read and read-next; requesteda returned, extraa+1 fetched, cursora+2; ARMcachenot explicitly invalidated',
        per_word='One received data word→one target-space24-bit store plus X10 publication; register-save RAM traffic separate',
        increment='legacy linear M0FFFF forced15C;24-bit wrap under reviewed EMA0; no per-transaction count/end clamp',
        persistence='RTI/command boundaries/GPIO do not restore/reset cursor; next header or data/read advance changes it',
        widths='24-bit scalarupper24;16-bit bulk/width values left-aligned8; incomplete/mixed frame behavior not simulated',
        foreign_writers='INIT clear +possible indirect aliases remain separate; no broad DSP alias census or204B closure performed'))
    formula=dict(status='VERIFIED address algebra; actual normal start/count/space can remain UNRESOLVED',
        transaction='Accesses (S+j) mod2^24,j0..N-1; counter/space persist afterN; split intervals onwrap',
        cached='Ifcachehit,S=DSPX10 andspace=X11.bit15; requestedARMaddress alone does not determine effective interval',
        count='N=wire_bytes/3 in24-bit mode orwire_bytes/2 in16-bit mode, for complete aligned frames; switches/headers excluded from dataN',
        crossing='Intersect intervals with[95A,960),[9DB,A12), or exact sparse EB+8*i; start below target alone is not exclusion',
        unknown_policy='UnknownS/N/space/order meansNOT-YET-DETERMINED, never empty/no-hit set')
    emit('transaction-formulas.json',formula)
    crossing=[dict(family=x['family'],start=x.get('start'),count=x.get('count'),nominal_hits=x['nominal_hits'],
        cached_continuation='EXCLUDED for recorded retained explicit-base interval' if x['nominal_hits']==[] else 'UNRESOLVED',
        all_normal_status='NOT-YET-DETERMINED: cursor/record/caller retention not universal') for x in bulk]
    emit('cached-crossing-results.json',dict(cases=crossing,scalar_cases='Every nominal endpoint CSV row tested; cache-hit start may differ',
        port_width_space_retention='UNRESOLVED',global_host_excluded=False))
    classifications=[dict(name='X95A',start=0x95a,end_exclusive=0x95b),
        dict(name='X95B..95F',start=0x95b,end_exclusive=0x960),dict(name='X[9DB,A12)',start=0x9db,end_exclusive=0xa12)]
    classifications += [dict(name=f'descriptor{i}+0',start=a,end_exclusive=a+1) for i,a in enumerate(DESCRIPTORS)]
    for x in classifications:x.update(classification='NOT-YET-DETERMINED',service_write_capability=True,
        normal_nominal_endpoint_hit=False,normal_effective_host_domain_closed=False)
    emit('requested-cell-classification.json',classifications)
    emit('transition-paths.json',dict(status='Recovered patch/parameter families bounded; full project/session/scene closure UNRESOLVED',
        patch_and_effect_parameters='Phase9 serialized callbacks/slotdispatch finite nominal endpoints; cache/cursor relation separate',
        project_asset_loader=dict(parent=0x8049a1c,callers=[0x803cc46,0x805bfd0],initial_page=0x580000,
            later_page='Cumulative metadata-derived R8 advance; no proven64-record total length bound',ancestry='Normal project/session vs init complete caller ancestry UNRESOLVED'),
        external_stream=dict(parent=0x80395bc,sink=0x80395ec,base=0xe80000,record='20006990+4',count='Recovered2740C bytes; all writer/retention closure separate'),
        scene='No additional exact requested-cell publisher established; no whole application transition proof',
        service='5E/diagnostic paths kept SERVICE, not inserted into normal endpoint set'))
    emit('result.json',dict(status='Normal host preservation NOT-YET-DETERMINED; targeted local semantics and nominal exclusions strengthened',
        complete_normal_call_graph=False,normal_host_can_produce_1E15='NOT-YET-DETERMINED',
        real_target_producing_state=None,parent_DSP_instructions=0,host_CPU_instructions=0,
        target_bridge_recomputed=False,active_parent_replay_justified=False,
        cache_INITFFFF_verified=True,normal_nominal_scalar_hits=[],service_contamination_of_normal_set=False,
        independent_mutators=['P204B positive count/record destinations preservedUNRESOLVED','other DSP indirect contexts, including foreign cursor state'],
        host_blockers=['Normal cache-hit cursor/order/port/width coherence','asset-loader cumulative metadata length/page and padding bounds','remaining indirect caller/transition ancestry'],
        best_next_step='Bound normal asset metadata length/total advance49C34→51B80→R8→49A6A across64 records, including page truncation and unconditional padding; keep cache ordering and204B independent',
        earlier_target_bridge_status=bridge['status'],authentic_boot=False,firmware_modified=False))
    with (out/'DSP-witnesses.asm').open('x',encoding='utf-8',newline='\n') as f:
        for pc,x in dsp.items():
            if 0x113<=pc<0x1b4 or 0x2779<=pc<0x278a:f.write(x['line']+'\n')
    for p in protected:inputs[p.relative_to(ROOT).as_posix()]=sha(p.read_bytes())
    for n in ['tools/ct_hostwrite_audit.py','tools/ct_arm_init_cache.py','emulator/tests/test_hostwrite.py','emulator/tests/verify_hostwrite.py']:read(n)
    verify_inputs()
    for n,h in inputs.items():assert sha((ROOT/n).read_bytes())==h,n
    emit('provenance.json',dict(inputs=inputs,probe=pmeta,offline=True,codec_roundtrip=True,all_ten_extracts=True,
        new_CPU_execution=False,complete_normal_domains=False))
    emit('hashes.json',{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()})
    print('Host cacheINITFFFF verified; targeted call edges',len(calls),'scalar endpoint rows',len(scalar),'; normal effective host domain UNRESOLVED')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir',required=True,type=Path);ap.add_argument('--probe-dir',required=True,type=Path)
    a=ap.parse_args();collect(a.output_dir,a.probe_dir)
