#!/usr/bin/env python3
"""Offline host destination audit; unknown callers are not absence proofs.

Only straight-line constant argument suffixes are inferred automatically.
Computed arguments retain unknown bounds; inspected phase-specific witnesses
are exported separately. Does not execute firmware or access any device.
"""
import argparse,csv,io,json,re,struct
from pathlib import Path
from ct_static import ROOT,BASE,BIN_HASH,SYX_HASH,sha,save,engine
from ct_resource_audit import read_rows
import ct_fw_tool

HELPERS={0x80292f8:('write',2),0x8029344:('read',1),0x80292dc:('address',1),
 0x8029314:('extended write',2),0x80294ca:('extended address',1),0x80294ac:('paged address',1),
 0x8029528:('bulk read',1),0x80295ba:('extended read',1),
 0x80296b0:('bulk transfer',None),0x802968e:('bulk transfer',None),
 0x80295e4:('word width',None),0x8029626:('word width',None)}

def csvtext(items):
    keys=sorted(set().union(*(r.keys() for r in items))) if items else ['status']
    s=io.StringIO();w=csv.DictWriter(s,fieldnames=keys);w.writeheader();w.writerows(items);return s.getvalue()

def phase(site):
    # These are inspected local families, not a whole-application mode proof.
    if 0x8029050<=site<0x8029190:return 'SERVICE/DIAGNOSTIC','reviewed test helper family; all-mode ancestry not proved'
    if 0x8029200<=site<0x80296e0:return 'UNRESOLVED','transport wrapper; depends on callers'
    if 0x8029300<=site<0x8029460:return 'BOOT/INITIALIZATION','reviewed table setup, may be invoked again'
    if 0x8027000<=site<0x8029152:return 'NORMAL UI/PARAMETER RUNTIME','HYPOTHESIS family classification; complete reachability not proved'
    if 0x8021000<=site<0x8022000:return 'NORMAL AUDIO RUNTIME','reviewed slot/event family; entry reachability incomplete'
    if 0x8035e28<=site<0x8035f18:return 'BOOT/INITIALIZATION','reviewed table setup; runtime reentry not excluded'
    return 'UNRESOLVED','normal/service mode ancestry not proved'

def suffix_arguments(cs,arm,site,targets):
    """Longest valid contiguous decode ending at site, cut at branch/call/IT.

    Values prove only this suffix. Inbound edges into it and alternative
    function entries prevent unconditional caller-argument claims.
    """
    best=[]
    for start in range(max(BASE,site-96),site,2):
        seq=list(cs.disasm(arm[start-BASE:site-BASE],start))
        if seq and seq[-1].address+seq[-1].size==site:
            best=seq;break
    cut=0
    for n,i in enumerate(best):
        mn=i.mnemonic.split('.')[0]
        if mn.startswith(('b','it','cb')) or mn in ('pop','tbb','tbh'):cut=n+1
    seq=best[cut:];regs={};origins={};evidence=[]
    from capstone.arm import ARM_OP_IMM,ARM_OP_REG,ARM_OP_MEM,ARM_REG_PC
    for i in seq:
        mn=i.mnemonic.split('.')[0];ops=i.operands;written=i.regs_access()[1]
        old=dict(regs);old_origins=dict(origins)
        for rr in written:
            regs.pop(i.reg_name(rr),None);origins.pop(i.reg_name(rr),None)
        if not ops or ops[0].type!=ARM_OP_REG:continue
        dst=i.reg_name(ops[0].reg)
        value=None;origin=i.address
        if mn in ('mov','movs','movw') and len(ops)==2:
            if ops[1].type==ARM_OP_IMM:value=ops[1].imm&0xffffffff
            elif ops[1].type==ARM_OP_REG and not ops[1].shift.type:
                src=i.reg_name(ops[1].reg);value=old.get(src);origin=old_origins.get(src,i.address)
        elif mn=='movt' and dst in old and len(ops)==2 and ops[1].type==ARM_OP_IMM:
            value=(old[dst]&0xffff)|((ops[1].imm&0xffff)<<16)
            origin=old_origins[dst]
        elif mn in ('ldr','ldrh','ldrb') and len(ops)==2 and ops[1].type==ARM_OP_MEM and ops[1].mem.base==ARM_REG_PC:
            address=((i.address+4)&~3)+ops[1].mem.disp;size={'ldr':4,'ldrh':2,'ldrb':1}[mn]
            if BASE<=address<=BASE+len(arm)-size:value=int.from_bytes(arm[address-BASE:address-BASE+size],'little')
        if value is not None:
            regs[dst]=value;origins[dst]=origin;evidence.append(f'{i.address:08X}: {i.mnemonic} {i.op_str}')
    inbound={r:any(origin<t<site for t in targets) for r,origin in origins.items()}
    return regs,evidence,inbound

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True);out=Path(p.parse_args().output_dir).resolve()
    if out==ROOT/'original' or ROOT/'original' in out.parents:raise SystemExit('Protected original/')
    if out.exists():raise SystemExit('Choose a fresh output directory')
    arm=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes();syxp=ROOT/'original/circuittracks-firmware-4486.syx';syx=syxp.read_bytes()
    assert sha(arm)==BIN_HASH and sha(syx)==SYX_HASH
    decoded=ct_fw_tool.decode_syx(syxp)['firmware'];assert decoded==arm and ct_fw_tool.build_syx(syxp,decoded)==syx
    cs=engine();hits=[];targets=set()
    from capstone.arm import ARM_OP_IMM
    # All halfword starts, including possible data/alternate-alignment hits.
    for off in range(0,len(arm)-3,2):
        for i in cs.disasm(arm[off:off+4],BASE+off,count=1):
            if i.mnemonic.startswith(('b','cb')):
                imm=[o.imm for o in i.operands if o.type==ARM_OP_IMM]
                if imm:
                    target=imm[-1];targets.add(target)
                    if target in HELPERS:hits.append((i.address,target,i.mnemonic+' '+i.op_str))
    callers=[];normal=[];service=[];boot=[];unresolved=[]
    for site,target,instruction in hits:
        regs,ev,inbound_regs=suffix_arguments(cs,arm,site,targets);kind,arg=HELPERS[target];value=regs.get(f'r{arg}') if arg is not None else None
        inbound=inbound_regs.get(f'r{arg}',False)
        mode,mode_status=phase(site)
        # Fix classification ordering for reviewed table builders.
        if 0x80293bc<=site<0x802945e:mode,mode_status='BOOT/INITIALIZATION','reviewed numeric table upload; runtime reentry not excluded'
        status='constant on straight-line suffix; no complete interprocedural proof' if value is not None and not inbound else 'UNRESOLVED argument/control-flow bounds'
        entry=dict(site=f'0x{site:08X}',helper=f'0x{target:08X}',operation=kind,argument=f'r{arg}' if arg is not None else 'cached/previous address',
            destination_value=None if value is None else f'0x{value:X}',mode=mode,mode_evidence=mode_status,bounds_status=status,
            suffix_has_inbound_target=inbound,register_constants={r:f'0x{v:X}' for r,v in regs.items()},evidence=ev,instruction=instruction)
        callers.append(entry)
        if value is not None and target in (0x80292f8,0x8029344,0x80292dc) and not inbound:
            address=value&0x7fff;space='Y' if value&0x8000 else 'X'
            row=dict(site=entry['site'],space=space,start=f'0x{address:X}',end_exclusive=f'0x{address+1:X}',operation=kind,
                mode=mode,status='selected constant suffix only; mode/reachability premises retained',
                overlaps_candidate=(0x4000<=address<0x6000 if space=='X' else 0x3000<=address<0x4000))
            {'BOOT/INITIALIZATION':boot,'SERVICE/DIAGNOSTIC':service,'NORMAL AUDIO RUNTIME':normal,'NORMAL UI/PARAMETER RUNTIME':normal}.get(mode,unresolved).append(row)
        else:unresolved.append(dict(site=entry['site'],space='unresolved',start='0x0',end_exclusive='0x1000000',mode=mode,
            status='unknown destination or cached/bulk extent; not a claimed actual full-space access'))
    # Reviewed interval families, independent of suffix hints, with explicit premises.
    witnesses=[dict(space='X',start='0xEB',end_exclusive='0x14B',stride=8,field='descriptor bank +7',evidence='ARM 08021A08; slot i=0..11; individual addresses F2+8*i',status='VERIFIED bounded slot publication; hull includes gaps'),
      dict(space='X',start='0x57A',end_exclusive='0x8A9',stride=0x4a,field='event mailbox',evidence='0802126E/219E8; i=0..11',status='VERIFIED bounded slot family; hull includes gaps'),
      dict(space='Y',start='0x11F',end_exclusive='0x59F',stride=0x60,field='slot control family',evidence='Phase4 event/control map; twelve 60-word contexts',status='VERIFIED context extent; not all words ARM-written'),
      dict(space='X',start='0x2000',end_exclusive='0x2200',stride=1,field='frequency table',evidence='080293BC; 512 words',status='VERIFIED initialization upload; reentry not excluded'),
      dict(space='X',start='0x2200',end_exclusive='0x2400',stride=1,field='normalization table',evidence='080293F0; 512 words',status='VERIFIED initialization upload; reentry not excluded'),
      dict(space='X',start='0x1600',end_exclusive='0x1940',stride=1,field='filter table',evidence='08029430; 832 words',status='VERIFIED initialization upload; reentry not excluded')]
    # Table source storage: exact pointer matches, no assumptions about blank space.
    offsets=[0x1f0,0x44efc,0x8110,0x4587c];table=0x19700
    ptrs=[BASE+x for x in offsets];assert [struct.unpack_from('<I',arm,table+4*i)[0] for i in range(4)]==ptrs
    references=[]
    for index,ptr in enumerate(ptrs):
        raw=struct.pack('<I',ptr)
        matches=[m.start() for m in re.finditer(re.escape(raw),arm)]
        count=int.from_bytes(arm[offsets[index]:offsets[index]+3],'big');size=6+3*count
        references.append(dict(table_index=index,payload_address=f'0x{ptr:X}',offset=f'0x{offsets[index]:X}',
            count=count,stream_bytes=size,end_offset=f'0x{offsets[index]+size:X}',
            exact_u32_matches=[f'0x{BASE+x:X}' for x in matches],status='VERIFIED exact pointer/table scan; constructed pointers not excluded'))
    assert arm[0x801b8f2-BASE:0x801b8f8-BASE].hex()=='01f001010843'
    references[0]['incidental_instruction_byte_match']='0x0801B8F3 spans AND/OR instructions; not a pointer load'
    dsp_payload=(ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin').read_bytes()
    rows=read_rows(ROOT/'builds/phase3-selection0-channel0.asm',dsp_payload)
    assert 'move x:(r1)+,x0' in rows[0xbe6]['text'] and 'move x:(r5)+,y0' in rows[0xa93]['text']
    assert '#$01,x1' in rows[0x1cf9]['text'] and 'do x1,$1db9' in rows[0x1db1]['text']
    mailbox=[dict(selector=s,normal_constructor_observed=s in [0,2,3,4,5],
        full_destination_interval='UNRESOLVED except selected bounded witnesses') for s in range(8)]
    mailbox[2].update(space='Y',words_written=1,origin='P:1CF9 x1=1; 1CFA r4=r5; 1DB1 DO x1; 1DB4 store',
        coefficient_not_count='X0=0x324 at P:1CF7',status='VERIFIED single-word destination at host-derived base')
    mailbox[6].update(space='Y',words_written=512,source='X:[0xC00,0xE00)',status='VERIFIED branch capability; normal caller not proved')
    mailbox[7].update(space='X',words_written=3,status='VERIFIED copy length; destination index bound unresolved')
    # Independent domains, never union normal and service maps into a free-space proof.
    dsp_intervals=list(csv.DictReader((ROOT/'builds/phase6b/reachable-intervals.csv').open()))
    summary=dict(status='static audit; complete runtime ownership NOT proved',syx_sha256=sha(syx),bin_sha256=sha(arm),roundtrip_identical=True,
       host_call_candidates=len(callers),constant_suffix_intervals=len(normal)+len(boot)+len(service),unresolved_callers=len(unresolved),
       semantics=dict(init_touched='not disqualified',runtime_owned='normal dependency proved',runtime_available='normal dependencies excluded after initialization'),
       largest_verified_available_after_init=dict(X=0,Y=0),allocations=[dict(words=n,status='NOT-YET-DETERMINED') for n in [256,512,1024,2048,4096]],
       relocation=dict(table_address='0x08029700',selector_order=['S0ch0','S1ch0','S0ch1','S1ch1'],
          ARM_selector_sites=['0x0802928E','0x080292A4'],table_pointer_formed_at='0x08029276',
          max_conditional_P_words=0x4000,additional_words=5538,additional_packed_bytes=16614,
          stream_source_alignment='byte-addressed source; pointer table uses 4-byte entries',
          update_size_field_bits=32,device_acceptance_of_larger_container='UNRESOLVED; encoder capability not bootloader proof',
          in_place_growth_crosses_ARM_code='VERIFIED overlaps ARM 0x0801B1A8 at raw offset 0xB1A8, below hypothetical end 0xC1F6',
          stored_space_verified_free_bytes=0,status='LIKELY POSSIBLE structurally; complete reference/space/physical-capacity proof unresolved'),
       guard=dict(address='X:0x2C66',readable=True,arbitrary_value_safe_all_modes='UNRESOLVED',duplicate_last_sample_required='not established',policy='retain stock neighboring scratch behavior until every consumer/status effect is proved'),
       gates=dict(RAM512='NOT-YET-DETERMINED',RAM1024='NOT-YET-DETERMINED',RAM2048='NOT-YET-DETERMINED',normal_exclusion='NOT-YET-DETERMINED',
         worker_isolation='conditional private/shared isolation; global queue bounds unresolved',P_capacity='YES conditionally, 5538 extra words; no algorithm-fit claim',
         storage_relocation='NOT-YET-DETERMINED',seam_complete='NOT-YET-DETERMINED',read_Plaits_for_resource_comparison='YES; conditional constraint comparison only, no implementation/fit proof'))
    out.mkdir(parents=True,exist_ok=False)
    save(out/'host-callers.json',json.dumps(callers,indent=2)+'\n')
    for name,data in [('normal-host-intervals.csv',normal),('boot-host-intervals.csv',boot),('service-host-intervals.csv',service),
      ('unresolved-host-intervals.csv',unresolved),('reviewed-host-families.csv',witnesses),('dsp-reviewed-intervals.csv',dsp_intervals)]:save(out/name,csvtext(data))
    save(out/'payload-references.json',json.dumps(references,indent=2)+'\n');save(out/'runtime-ownership.json',json.dumps(summary,indent=2)+'\n')
    save(out/'mailbox-witnesses.json',json.dumps(mailbox,indent=2)+'\n')
    normaldsp=[r for r in dsp_intervals if r.get('program')=='selection0-channel0' and r.get('phase')!='startup']
    bootdsp=[r for r in dsp_intervals if r.get('phase')=='startup']
    workerdsp=[r for r in dsp_intervals if r.get('program')=='selection0-channel1']
    service_dsp=[r for r in csv.DictReader((ROOT/'builds/phase6b/absolute-intervals.csv').open()) if r['program'].startswith('selection1')]
    for name,data in [('boot-dsp-intervals.csv',bootdsp),('normal-dsp-intervals.csv',normaldsp),('service-dsp-intervals.csv',service_dsp),('worker-private-intervals.csv',workerdsp)]:save(out/name,csvtext(data))
    print(json.dumps(dict(call_candidates=len(callers),normal_constant_intervals=len(normal),boot_constant_intervals=len(boot),service_constant_intervals=len(service),unresolved=len(unresolved)),indent=2))

if __name__=='__main__':main()
