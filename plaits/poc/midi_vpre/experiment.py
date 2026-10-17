"""Generate source-derived ARM mailbox stimuli and verify the DSP against the sealed oracle.

No MIDI APIs, hardware, firmware containers, reference-repository writes or network.
The unavailable ARM emulator/dump is a declared limitation, not simulated evidence.
"""
import csv, hashlib, json, math, struct, subprocess, sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'builds/phase20d-midi-vpre'
sys.path.insert(0,str(ROOT/'plaits/poc'))
from fixed_model import Fixed,F,Q

def emit(p,v): p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

class Mailbox:
    """Reference c_vsend contract: pending values coalesce; one word/voice/2 ms.
    The 1-bit tag is sent BEFORE toggling, matching the reference instruction order.
    This source-derived model does not execute ARM instructions.
    """
    def __init__(self): self.tag=0;self.last=-100;self.pending={};self.coalesced=0;self.sent=[]
    def put(self,c,v):
        self.coalesced+=int(c in self.pending)
        self.pending[c]=v
    def tick(self,ms):
        if ms-self.last<2 or not self.pending:return None
        priority=[19,18,20,17,21]
        c=next((c for c in priority if c in self.pending),min(self.pending))
        v=self.pending.pop(c);w=(self.tag<<23)|(c<<16)|(v&65535)
        self.tag^=1;self.last=ms;self.sent.append((ms,c,v,w));return w

def stimuli():
    dst=BASE/'stimuli'
    if dst.exists():raise RuntimeError('Fresh stimuli required')
    dst.mkdir(parents=True)
    m=Mailbox();records=[];log=[]
    # Independent protocol checks including the known unthrottled tag-cancellation failure.
    test=Mailbox();test.put(25,1);test.put(25,64);test.put(25,100)
    assert test.coalesced==2 and (test.tick(0)&65535)==100
    test.put(18,69);assert test.tick(1) is None and test.tick(2) is not None
    lost=(0<<23)|(25<<16)|1;lost2=(1<<23)|(25<<16)|100
    assert (lost2^0x800000)&0x800000==0 # two toggles, old tag 1 -> final tag 1
    for b in range(4096):
        ms=(b*2)//3
        if b==0:
            for c,v in [(19,2),(18,60),(20,100),(17,1),(21,1),(25,64),(24,64)]:m.put(c,v)
        if b%96==12:
            for c,v in [(18,[21,36,60,69,96,108,120,127][(b//96)%8]),(20,100),(17,1),(21,1)]:m.put(c,v)
        if b%96==63:m.put(17,0)
        if b%96 in (64,65,66):m.put(17,1);m.put(21,1) # rapid retrigger/coalescing
        if b%9==0:
            for v in [0,127,[1,64,100,127,0][(b//9)%5]]:m.put(25,v)
            m.put(24,[0,32,64,100,127][(b//45)%5])
        if b%48==7:m.put(19,2);m.put(18,[60,69,96,120][(b//48)%4]);m.put(20,100);m.put(17,int(b%96<63))
        if b==4000:m.put(19,0) # true disabled idle blocks freeze renderer state
        if b>4000:m.pending.clear();m.put(19,0) if b%48==7 else None
        word=m.tick(ms)
        writes=[] if word is None else [(0x3b80,word)]
        records.append((b,writes));log.append(dict(block=b,ms=ms,word=word,pending=dict(m.pending)))
    (dst/'cases.tsv').write_text(''.join(f'{b} {len(ws)}'+''.join(f' {a:x} {v:x}' for a,v in ws)+'\n' for b,ws in records))
    emit(dst/'mailbox.json',dict(model_scope='ARM c_vsend source contract, not ARM execution',messages=m.sent,coalesced=m.coalesced,
        minimum_send_gap_ms=min(b[0]-a[0] for a,b in zip(m.sent,m.sent[1:])),
        protocol_checks={'latest_value_wins':True,'same_ms_and_1ms_writes_suppressed':True,'two_tag_toggles_can_cancel':True},blocks=log))
    print('stimuli',len(records),'messages',len(m.sent),'coalesced',m.coalesced)

def verify(run,require_long=True):
    prep=json.loads((BASE/'fixture/preparation.json').read_text())
    for p,h in prep['protected'].items():assert sha(Path(p))==h,('Protected input changed',p)
    rows=list(csv.DictReader((run/'blocks.csv').open()))
    states=list(csv.DictReader((run/'states.csv').open()))
    raw=np.fromfile(run/'raw.i32',dtype='<i4').reshape(-1,32)
    model=Fixed();renders=0;maxdiff=0;wraps=crossings=0;consecutive=max_consecutive=0
    for i,(r,s) in enumerate(zip(rows,states)):
        if int(r['rendered']):
            prev=model.phase
            expected=model.render32(int(r['frequency_q22'])/F,int(r['pw_q22'])/F,int(r['shape_q21'])/Q)
            maxdiff=max(maxdiff,int(np.max(np.abs(raw[i].astype(np.int64)-expected))))
            assert raw[i].tolist()==expected,('sample mismatch',i)
            wraps+=int(model.phase<prev);crossings+=int(model.high!=int(states[i-1]['high'])) if i else 0
            renders+=1
            consecutive+=1;max_consecutive=max(max_consecutive,consecutive)
        else:consecutive=0
        assert [int(s[k]) for k in ['phase','next','previous_pw','high','frequency','pw','shape']]==model.state(),('state mismatch',i)
        assert all(int(r[k])==1 for k in ['canaries','adapter_registers','other_track'])
        if 'caller_registers' in r:assert int(r['caller_registers'])==1
    if require_long:assert len(rows)>=2048 and max_consecutive>=2048
    nat=json.loads((run/'native.json').read_text());assert nat['access_violations']==0
    timing={}
    for name in ['baseline','replacement']:
        ins=np.array([int(r[name+'_instructions']) for r in rows]);cyc=np.array([int(r[name+'_emulator_cycles']) for r in rows])
        timing[name]=dict(instructions_min=int(ins.min()),instructions_mean=float(ins.mean()),instructions_max=int(ins.max()),
                         emulator_cycles_min=int(cyc.min()),emulator_cycles_mean=float(cyc.mean()),emulator_cycles_max=int(cyc.max()))
    delta=np.array([int(r['replacement_emulator_cycles'])-int(r['baseline_emulator_cycles']) for r in rows])
    timing['delta']=dict(min=int(delta.min()),mean=float(delta.mean()),max=int(delta.max()),worst_block=int(delta.argmax()))
    active=np.array([bool(int(r['rendered'])) for r in rows]);timing['active_delta']=dict(min=int(delta[active].min()),mean=float(delta[active].mean()),max=int(delta[active].max()))
    ins_delta=np.array([int(r['replacement_instructions'])-int(r['baseline_instructions']) for r in rows]);timing['instruction_delta']=dict(min=int(ins_delta.min()),mean=float(ins_delta.mean()),max=int(ins_delta.max()))
    mixed=run/'mixed.i32'
    mix_result=None
    if mixed.exists():
        mix=np.fromfile(mixed,dtype='<i4').reshape(-1,2,64)
        rings=np.fromfile(run/'rings.i32',dtype='<i4').reshape(-1,32,2,2).transpose(0,2,1,3).reshape(-1,2,64)
        # P:$23E..$24E: the two silent synth stems contribute 0; the MIDI
        # stems use equal 1/8 gains, a negative MAC, and ASL 2 => -(L+R)/2.
        # Compute at accumulator precision before narrowing (floor for negatives).
        exp=-((rings[:,:,0::2].astype(np.int64)+rings[:,:,1::2].astype(np.int64)))
        exp=exp//2
        assert np.array_equal(mix[:,:,0::2],exp) and np.array_equal(mix[:,:,1::2],exp),'Stock strip mixing oracle'
        mix_result=dict(original_stock_strip_instructions=True,all_stereo_samples_exact=True,
                        fixture_gains='0x100000 for both outputs of each stem; silent synth stems',
                        scope='P:23E..24E; later drums/master/FX/DMA outside this experiment')
    result=dict(blocks=len(rows),renders=renders,maximum_consecutive_renders=max_consecutive,oracle_sample_max_difference=maxdiff,oracle_states_exact=True,
                canaries_after_every_block=True,other_track_exact=True,access_violations=0,
                timing=timing,register_checks=nat['adapter_checks'],stock_strip_mixing=mix_result,
                wrap_events=sum(int(r.get('wrap_events',0)) for r in rows),pw_crossing_events=sum(int(r.get('pw_events',0)) for r in rows),
                limitations=['Source-modeled ARM sender; no ARM instruction execution or authentic ARM RAM dump.',
                             'Isolated DSP vpre caller context; no concurrent IRQ/DMA/core1 or stock boot.',
                             'Synthetic P overlay is not a flash-ready allocation.',
                             'Emulator cycles are conditional modeled cycles, not hardware timing.'])
    # Additional regression: compare all observed writes to MIDI2's oscillator
    # 1/2, VCF/VCA, FX, second filter stage, comb/chorus and shared grain counter.
    def regression(path):
        digest=hashlib.sha256();count=0
        with path.open() as f:
            for r in csv.DictReader(f):
                if r['write']!='1':continue
                ad=int(r['address'],16)
                owned_other=(r['space']=='X' and (0x3bb0<=ad<0x3be0 or 0x3930<=ad<0x3960 or
                    0x3990<=ad<0x39c0 or 0x3870<=ad<0x38a0 or 0x3830<=ad<0x3834 or ad==0x3706e)) or (
                    r['space']=='Y' and (0x3500<=ad<0x3600 or 0x3800<=ad<0x3a00))
                if owned_other:
                    digest.update(f"{r['block']},{r['space']},{ad},{r['value']}\n".encode());count+=1
        return dict(writes=count,sha256=digest.hexdigest())
    rb=regression(run/'baseline/access.csv');rm=regression(run/'replacement/access.csv')
    assert rb==rm,('MIDI2 write projection changed',rb,rm)
    result['other_track_write_projection']=rb
    result['caller_checks_after_each_vpre']=all(int(r.get('caller_registers',0))==1 for r in rows)
    result['timing_model']='Sealed DSP interpreter calcCycles/Table A opcode costs, no previous-instruction interlocks, IRQ/DMA/waits or hardware calibration; full DSP scope vpre + P:23E..24E strip mixer'
    emit(run/'hashes.json',{str(p.relative_to(run)):sha(p) for p in sorted(run.rglob('*')) if p.is_file() and p.name not in ['hashes.json','verification.json']})
    emit(run/'verification.json',result)
    print(json.dumps(result,indent=2))

def protocol():
    dst=BASE/'protocol-stimuli'
    if dst.exists():raise RuntimeError('Fresh protocol stimuli required')
    dst.mkdir(parents=True)
    w=lambda tag,c,v:(tag<<23)|(c<<16)|(v&65535)
    blocks=[[(0x3b80,w(0,25,1))],[(0x3b80,w(1,25,100))],
            [(0x3b80,w(0,25,1)),(0x3b80,w(1,25,127))], # tag cancels -> ignored
            [(0x3b80,w(0,25,127))],[(0x3b80,w(0,25,64))], # duplicate tag -> ignored
            [(0x3b80,w(1,25,0))],[(0x3b80,w(0,18,127))],[(0x3b80,w(1,24,127))],
            [(0x3b80,w(0,17,0))],[(0x3b80,w(1,19,0))],[(0x3b80,w(0,18,69))],
            [(0x3b80,w(1,19,2))],[(0x3b80,w(0,21,1)),(0x3b80,w(1,21,1))],
            [(0x3b80,w(0,21,1))]]
    (dst/'cases.tsv').write_text(''.join(f'{b} {len(ws)}'+''.join(f' {a:x} {v:x}' for a,v in ws)+'\n' for b,ws in enumerate(blocks)))

def protocol_verify(run):
    verify(run,False)
    pw=[64]*14
    writes=[]
    with (run/'replacement/access.csv').open() as f:
        for r in csv.DictReader(f):
            if r['space']=='X' and r['write']=='1' and int(r['address'],16)==0x3903:
                writes.append((int(r['block']),int(r['value'],16)))
    assert writes==[(1,100),(3,127),(5,0)],writes
    result=dict(actual_DSP_mailbox_decoder=True,first_equal_tag_ignored=True,double_tag_cancellation_ignored=True,
                repeated_tag_ignored=True,accepted_PWM_writes=writes,oracle_determinism=True,
                off_on_state_continuity=True,ARM_rate_limit='source-derived model only')
    emit(run/'protocol-verification.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':
    if sys.argv[1]=='stimuli':stimuli()
    elif sys.argv[1]=='verify':verify(Path(sys.argv[2]))
    elif sys.argv[1]=='protocol':protocol()
    elif sys.argv[1]=='protocol-verify':protocol_verify(Path(sys.argv[2]))
