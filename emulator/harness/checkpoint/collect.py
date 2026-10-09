"""Build provenance-tagged checkpoints and audit original-opcode slice traces.
No ROM search, device API, patching, or normal-reachability claim.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from ct_stock_load_audit import verify_inputs, rows

def sha(b):return hashlib.sha256(b).hexdigest()
def save(out,name,v):
    with (out/name).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def known(v,p):return dict(value=v,status='VERIFIED_STATIC_CONDITIONAL',provenance=p)
def unknown(p):return dict(value=None,status='SYMBOLIC',provenance=p)
def cursor(f,j):return ([0x2ccc,0x2cec] if f==0 else [0x2c02,0x2c24])[j%2]
def cases():
    result=[]
    def add(kind,f=0,j=0,i=0,m=0xffff,e=0):result.append(dict(id=len(result),kind=kind,family=f,j=j,i=i,modifier=m,encoding=e))
    for f in range(2):
        for j in range(16):
            for m in [0xffff,0x3ff]:
                for i in range(32):
                    for e in [0,1]:add(0,f,j,i,m,e)
            for e in [0,1]:add(1,f,j,0,0xffff,e)
    for e in [0,1]:add(2,e=e);add(3,e=e)
    return result
def snapshot(c):
    k,f,j,i,m=c['kind'],c['family'],c['j'],c['i'],c['modifier']
    cpu={name:unknown('Not consumed by audited slice; native backing omitted from concrete state') for name in
         ['SR','OMR','A','B','X0','X1','Y0','Y1','LA','LC','SP','SC','SSH','SSL','SZ','EP','VBA']}
    cpu.update({n+str(i):unknown('Unconsumed by slice') for n in ['R','N','M'] for i in range(8)})
    # Reserved candidate-device SR.SC is fixed0. Other control/data mode bits
    # remain unknown; no full word is checkpointed as0.
    cpu['SR']['known_mask']=1<<13;cpu['SR']['known_value']=0
    cpu['SR']['provenance']='Candidate DSP56724/25 reserved SR13 (Table5-2); all other bits symbolic in address projection'
    cpu['OMR']['known_mask']=0x600080;cpu['OMR']['known_value']=0x400080
    cpu['OMR']['provenance']='Original shim sets7/22,clears21; retained memory-mode relation is a checkpoint premise, not proved ROM preservation'
    x={};y={};entry=0;stop=0
    if k==0:
        entry,stop=0x1f92,0x1f98
        cpu['R3']=known(0x2c8a+i,'P1F8D constant + P1F92 prior postincrements, i0..31')
        cpu['R7']=known(cursor(f,j)+i,'P260A cursor initializer -> P1F89 -> P1F97 prior postincrements')
        cpu['M3']=known(0xffff,'P2779..2781 init, conditioned on retained modifier')
        cpu['M7']=known(m,'P2781 legacyFFFF or P265 temporary3FF; preservation remains premise')
        x['symbolic_regions']=[[0x2c8a,0x2caa],[cursor(f,j),cursor(f,j)+32]]
        cpu['A']['provenance']='Previous ramp arithmetic; numerical state not recovered'
        cpu['X1']['provenance']='P1F8F coefficient, not concretized'
    elif k==1:
        entry,stop=0x1f89,0x1f8b
        cpu['R6']=known((0x1800 if f==0 else 0x19f0)+j,'P1E76/1ED9 caller base plus P1F8C j previous advances')
        cpu['M6']=known(0xffff,'P2780; conditioned on preservation')
        y[str((0x1820 if f==0 else 0x1a10)+j)]=known(cursor(f,j),'P260A..261F alternating initializer')
    elif k==2:
        entry,stop=0x203a,0x204c
        cpu['R0']=known(0x35f,'Original P2035 constant')
        cpu['M0']=known(0xffff,'P2779 init; retained modifier premise')
        cpu['N5']=known(0,'Y30=0 at P1BA8/1BA9 -> P2034..2038')
        cpu['M5']=known(0xffff,'P277F init; retained modifier premise')
        for a in range(0x35f,0x364):x[str(a)]=known(0,'P2788 clear; no intervening foreign write premise')
        y['0']=known(0,'P2789 Y clear; no intervening foreign write premise')
    else:
        entry,stop=0x204b,0x204c
        cpu['R4']=known(0,'P2043 consumes X364; that record field has init-clear value0')
        x['0']=known(0,'P2788 clear; arithmetic result remains symbolic')
    cpu['PC']=known(entry,'Selected later checkpoint, not executed boot/caller path')
    return dict(id=c['id'],kind=k,CPU=cpu,X=x,Y=y,P_sha256='b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855',
        stop_before_PC=stop,parameters=c,
        scope='CONSUMER_CALIBRATION_ONLY; positive-count publisher/reachability unproved' if k==3 else 'BOUNDED_LOCAL_CHECKPOINT_DOMAIN',
        execution_projection='Address/read/write effects only; unknown DATA represented by tagged backing encodings, never treated as concrete results',
        scheduling='Isolated synchronous slice; no asynchronous IRQ/worker/host events; not a firmware invariant',
        loop='Body iteration i derived from static N32. No inherited loop edge/stack/return is replayed; stop at last body word boundary')

def run(out,exe):
    out=out.resolve()
    if out.exists() or not out.is_relative_to((ROOT/'builds/phase19c-checkpoint').resolve()):raise ValueError('Fresh checkpoint output required')
    main,_=verify_inputs();dsp=ROOT/'firmware/dsp/build-4486'
    manifest=json.loads((dsp/'manifest.json').read_text());identities={}
    for b in manifest['blocks']:
        for k,h in [('stream_file','stream_sha256'),('payload_file','payload_sha256')]:
            identities[b[k]]=sha((dsp/b[k]).read_bytes());assert identities[b[k]]==b[h]
    listing=rows(ROOT/'builds/phase3-selection0-channel0.asm',main)
    required=[0x1f89,*range(0x1f92,0x1f98),*range(0x203a,0x2041),0x204b,0x260a,0x261c,0x261d,0x261e,0x261f,0x2035,0x2788,0x2789]
    for pc in required:assert pc in listing
    out.mkdir(parents=True);cs=cases();save(out,'checkpoints.json',dict(schema='ct-checkpoint-v1',snapshots=[snapshot(c) for c in cs]))
    save(out,'static-witnesses.json',[listing[p] for p in required])
    save(out,'cursor-table.json',[dict(Y=(0x1820 if f==0 else 0x1a10)+j,value=cursor(f,j),provenance='OriginalP260A..261F') for f in range(2) for j in range(16)])
    tsv=out/'cases.tsv'
    with tsv.open('x',encoding='ascii',newline='\n') as p:
        for c in cs:p.write(' '.join(str(c[n]) for n in ['id','kind','family','j','i','modifier','encoding'])+'\n')
    p=subprocess.run([str(exe),str(dsp/'selection0-channel0.payload24.bin'),str(tsv),str(out/'trace.jsonl')],capture_output=True,text=True)
    if p.returncode:raise ValueError('Replay blocked: '+p.stderr)
    events=[json.loads(line) for line in (out/'trace.jsonl').read_text().splitlines()]
    assert [e['seq'] for e in events if 'seq' in e]==list(range(sum('seq' in e for e in events)))
    per={c['id']:[] for c in cs}
    for e in events:per[e['case']].append(e)
    exec_counts={str(k):0 for k in range(4)};writes=[];entry=[];ranges={};projections={}
    for c in cs:
        es=per[c['id']];xs=[e for e in es if e['type']=='EXEC'];wr=[e for e in es if e['type']=='WRITE']
        exec_counts[str(c['kind'])]+=len(xs)
        assert es[-1]['type']=='END' and es[-1]['count']==len(xs)
        for e in xs:assert main[e['PC']*3:e['PC']*3+3]==e['opcode'].to_bytes(3,'big')
        k=c['kind']
        if k==0:
            assert [e['PC'] for e in xs]==list(range(0x1f92,0x1f98))
            assert len(wr)==1 and wr[0]['PC']==0x1f97 and wr[0]['effective_address']==cursor(c['family'],c['j'])+c['i']
            assert wr[0]['value'] is None and wr[0]['value_status']=='SYMBOLIC_DATA'
            key=f"family{c['family']}-j{c['j']}-M{c['modifier']}-encoding{c['encoding']}"
            ranges.setdefault(key,[]).append(wr[0]['effective_address'])
        elif k==1:
            assert len(xs)==1 and not wr
            rd=[e for e in es if e['type']=='READ'];assert len(rd)==1 and rd[0]['value']==cursor(c['family'],c['j'])
        elif k==2:
            assert [e['PC'] for e in xs]==list(range(0x203a,0x2041)) and not wr
            assert es[-1]['PC']==0x204c
            entry.extend(e for e in es if e['type']=='ENTRY_X35F')
        elif k==3:assert len(xs)==1 and len(wr)==1 and wr[0]['effective_address']==0
        if k!=3:writes.extend(wr)
        projection=[(e['type'],e['PC'],e.get('memory_space'),e.get('effective_address'),e.get('value_status'),e.get('modifier')) for e in es if e['type']!='END']
        key=tuple(c[n] for n in ['kind','family','j','i','modifier'])
        if key in projections:assert projections[key]==projection,'Unknown backing encoding influenced observed address/control'
        else:projections[key]=projection
    for addrs in ranges.values():assert len(addrs)==32 and addrs==list(range(addrs[0],addrs[0]+32))
    assert len(entry)==2 and all(e['value']==0 for e in entry)
    xy=[e for e in events if e['type'] in ['READ','WRITE'] and e['memory_space'] in ['X','Y']]
    watched=[e for e in xy if e['memory_space']=='X' and (0x340<=e['effective_address']<0x360 or (e['type']=='WRITE' and 0x5f00<=e['effective_address']<0x6000))]
    save(out,'watched-accesses.json',watched);save(out,'x35f-entries.json',entry)
    save(out,'cursor-ranges.json',ranges)
    save(out,'result.json',dict(status='TESTED BOUNDED-PROOF for address-only checkpoint slices; universal stock UNRESOLVED',
        runs=len(cs),original_opcode_executions=exec_counts,total_original_opcode_executions=sum(exec_counts.values()),
        data_values='SYMBOLIC, no numerical sample/gain claim',cursor_stores=len(writes),
        cursor_loop='32 independently checkpointed body iterations per cell; full DO/helper/caller not executed',
        zero_count_consumer='PROVEN FOR CHECKPOINT DOMAIN: X35F0, five pre-DO X reads, one Y prefetch, DO0 skip, no204B',
        X35F_writes='PROVEN FOR CHECKPOINT DOMAIN: none',X35F_nonzero_entry='PROVEN FOR CHECKPOINT DOMAIN: none; no positive producer recovered',
        high_X_writes='PROVEN FOR CHECKPOINT DOMAIN: none',
        target_interval_writes='PROVEN FOR CHECKPOINT DOMAIN: none; two X35F reads logged',
        record_store_calibration='TESTED one original204B writes one X word at R4=0; NOT a reachable positive-record case',
        validation=dict(initialized_cursor_loads=True,thirty_two_addresses_per_cell=True,modifier_domains_match=True,
            zero_count_skip=True,one_word204B_calibration=True,paired_backing_address_equivalence=True),
        blockers=['Full helper DO/stack/control entry and caller reachability not recovered',
            'Foreign cursor/count/record/modifier mutations remain unclosed','No normal positive-count publisher/complete record constructor',
            'Unknown arithmetic values/results are not concretely modeled','Async/worker/host/IRQ interference excluded from slice experiment, not proved absent in stock'],
        usefulness=dict(A='YES cursor load/body slices; full helper UNRESOLVED',B='YES initialized zero-count consumer; positive-count UNRESOLVED',
            C='YES every X/Y slice access uses sealed19A bus hooks',D='NO within tested slice domain; universal UNRESOLVED',
            E='NO within tested slice domain; universal UNRESOLVED',F='YES validates local address argument; does not close persistence',G='YES full authentic boot remains independently unresolved'),
        Plaits_PoC='NO allocation/safety gate passed; no integration authorized',
        best_next_step='Qualify the full1F5C nested-loop checkpoint stack/control relation, retaining symbolic data, to join the isolated iterations without invented state'))
    save(out,'integrity.json',dict(inputs=identities,main_hash=sha(main),native_binary_hash=sha(exe.read_bytes()),original_unmodified=True))
    save(out,'source-manifest.json',{p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in [Path(__file__),ROOT/'emulator/harness/checkpoint/replay.cpp',ROOT/'emulator/harness/checkpoint/CMakeLists.txt',ROOT/'emulator/harness/checkpoint/build.ps1',ROOT/'emulator/tests/test_checkpoint_state.py',ROOT/'emulator/tests/verify_checkpoint.py']})
    save(out,'linked-substrate.json',{p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in [ROOT/'builds/phase19a/core-build/replay_core.lib',ROOT/'builds/phase19a/core-build/upstream/asmjit/asmjit.lib',ROOT/'builds/phase19a/core-build/ct_replay_fixture.exe']})
    verify_inputs();save(out,'hashes.json',{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())})
    print(p.stdout.strip());print('All differential gates PASS; bounded address conclusions only')

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',required=True,type=Path)
    ap.add_argument('--exe',type=Path,default=ROOT/'builds/phase19c-checkpoint/core-build/ct_checkpoint.exe')
    a=ap.parse_args();run(a.output_dir,a.exe.resolve())
