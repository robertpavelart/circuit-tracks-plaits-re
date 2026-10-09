#!/usr/bin/env python3
"""Replay reviewed Phase9 selector-boundary proof and candidate host exclusions.

All proof scopes/premises are explicit. This is a static evidence report, not
firmware execution, a universal alias solver or a persistent-RAM proof.
"""
import argparse,csv,io,json,struct
from pathlib import Path
from ct_static import ROOT,BASE,BIN_HASH,SYX_HASH,sha,save
from ct_phase4_trace import arm_evidence
import ct_fw_tool

def csvtext(rows):
    s=io.StringIO();keys=sorted(set().union(*(r.keys() for r in rows))) if rows else ['status']
    w=csv.DictWriter(s,fieldnames=keys);w.writeheader();w.writerows(rows);return s.getvalue()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ranges-dir',required=True)
    p.add_argument('--output-dir',required=True);a=p.parse_args()
    src=Path(a.ranges_dir).resolve();out=Path(a.output_dir).resolve()
    if out.exists():raise SystemExit('Choose a fresh output directory')
    if out==ROOT/'original' or ROOT/'original' in out.parents:raise SystemExit('Protected original/')
    arm=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes();syxp=ROOT/'original/circuittracks-firmware-4486.syx'
    assert sha(arm)==BIN_HASH and sha(syxp.read_bytes())==SYX_HASH
    assert ct_fw_tool.decode_syx(syxp)['firmware']==arm
    assert ct_fw_tool.build_syx(syxp,arm)==syxp.read_bytes()
    def word(a):return struct.unpack_from('<I',arm,a-BASE)[0]
    assert word(0x80220cc)==0x200067fc
    assert ((0x8021f94+4)&~3)+0x134==0x80220cc
    assert ((0x8021fb2+4)&~3)+0x118==0x80220cc
    assert word(0x80219d4)==0x200067fc and word(0x8021fc8)==0x805a384
    assert word(0x801f5c8)==word(0x803be50)==0x2000030c
    assert arm[0x1f4b4-0x10000:0x1f4b6-0x10000]==bytes.fromhex('0121')
    assert arm[0x1f4b8-0x10000:0x1f4bc-0x10000]==bytes.fromhex('01734173')
    assert word(0x805b860)==0x8029a09 and word(0x805b864)==0x8029a13
    assert word(0x80299d0)==0x805b858
    summary=json.loads((src/'summary.json').read_text())
    assert summary['BIN_SHA256']==BIN_HASH and summary['unknown_destinations']==0 and summary['unsupported_paths']==0
    tables=list(csv.DictReader((src/'callback-tables.csv').open()))
    formulas=list(csv.DictReader((src/'constructor-formulas.csv').open()))
    writes=list(csv.DictReader((src/'parameter-writes.csv').open()))
    assert all(r['status'].startswith('VERIFIED') for r in formulas)
    global_roots={t['function'] for t in tables if t['kind'].startswith('namespace')}
    assert all(int(r['bank_stride'],16)==0 and int(r['slot_stride'],16)==0
               for r in formulas if hex(int(r['root'],16)) in global_roots)
    callers=[]
    for path in sorted((ROOT/'builds/phase9').glob('*/calls.json')):
        for row in json.loads(path.read_text()):
            item={k:row[k] for k in ('site','target','instruction')}
            if item not in callers:callers.append(item)
    assert {r['site'] for r in callers if r['target']=='0x0802148C'}=={'0x080214C2','0x080214CC','0x0804966E'}
    assert {r['site'] for r in callers if r['target']=='0x08049634'}=={'0x0803BE0E','0x0803BE18'}
    assert not any(r['target'] in ('0x08029A08','0x08029A12','0x08027A10') for r in callers)
    evidence=[]
    for path in sorted((ROOT/'builds/phase9').rglob('*.asm')):
        evidence.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes()),
                         'checked_instructions':arm_evidence(path,arm)})
    graph=[
      {'from':'virtual producer (not fully recovered)','to':'805B860 +0 / +4','mode':'UNRESOLVED upstream input origin',
       'bound':'no direct caller; pointer identities and constructor recovered, not complete object-flow closure'},
      {'from':'805B860+0 ->29A08','to':'3BD58 ->497CA','mode':'NORMAL SYNTH/AUDIO event sink; upstream MIDI/UI origin UNRESOLVED',
       'bound':'r1 namespace ->r0; r2 key ->r1; r3 level ->r2; no clamp in thunk'},
      {'from':'805B860+4 ->29A12','to':'3BD94 ->49758','mode':'NORMAL SYNTH/AUDIO release sink; upstream MIDI/UI origin UNRESOLVED',
       'bound':'r1 namespace ->r0; r2 key ->r1; no clamp in thunk'},
      {'from':'2AB48 (r0=FF)','to':'3BD58 ->497CA ->28FC2','mode':'NORMAL UI/PARAMETER special update witness',
       'bound':'FF bypasses selector store; namespace21 parameter9 ->Y:111'},
      {'from':'1D5D4 lock ->21392','to':'213D4 -> five slot callbacks','mode':'NORMAL SYNTH/AUDIO service',
       'bound':'bank=loop index0,1; slot=loop index0..11, matching saved event bank'},
      {'from':'1F4E4 lock ->213B0','to':'214BE ->2148C','mode':'NORMAL UI/PARAMETER periodic service',
       'bound':'214C0/14C2 bank0;214C6/14CC bank1'},
      {'from':'29A00 ->3BDF2 (3BE04 lock)','to':'3BE0E/18 ->49634 ->2148C','mode':'NORMAL UI/PARAMETER bank refresh',
       'bound':'flag bit0 suppliesbank0; bit1 suppliesbank1; mask is not a channel argument'},
      {'from':'2148C storesbank at21496','to':'214AC BLX table805A384[index]','mode':'NORMAL UI/PARAMETER',
       'bound':'index0..15 from pending bits; cached bank0/1; index6 ->27A10'},
      {'from':'27A10 ->2872C','to':'286BC immediate /286F6 deferred','mode':'NORMAL UI/PARAMETER deferred work',
       'bound':'bank passed inr1; deferred callsites2870C/2871E independently supply0/1'},
      {'from':'1E03C ->1F4B0;1E044 store','to':'*[2000030C]+C/D','mode':'BOOT/INIT guard construction',
       'bound':'initial count=capacity=1; normal wrappers acquire/release same address'},
      {'from':'1F6FE ->2989C','to':'vptr805B860; five child views at+344','mode':'BOOT/INIT object construction',
       'bound':'child parameter IDs0,1,10,20,21; this alone is not a note-event input bound'}]
    domains=[]
    for t in tables:
        domains.append({'function':t['function'],'table':t['table'],'index':t['index'],
           'local_domain':t['selector_domain'],'status':'VERIFIED recovered normal callback boundary',
           'notes':'not a global20006800 domain; valid stock object/guard/dispatch paths assumed'})
    # Global special update is outside the callback tables.
    extras=[{'root':'0x08028FC2','mode':'NORMAL UI/PARAMETER FF event branch',
       'space':'Y','start':'0x111','end_exclusive':'0x112','words':1,
       'status':'VERIFIED local fixed destination; originaleventFF is not a synthbank'},
       {'root':'0x080286BC','mode':'NORMAL UI/PARAMETER immediate/deferred',
        'space':'X','start':'0x2FA','end_exclusive':'0x2FB','words':1,'status':'VERIFIED bank0 destination'},
       {'root':'0x080286BC','mode':'NORMAL UI/PARAMETER immediate/deferred',
        'space':'X','start':'0x35F','end_exclusive':'0x360','words':1,'status':'VERIFIED bank0 destination'},
       {'root':'0x080286BC','mode':'NORMAL UI/PARAMETER immediate/deferred',
        'space':'X','start':'0x46C','end_exclusive':'0x46D','words':1,'status':'VERIFIED bank1 destination'},
       {'root':'0x080286BC','mode':'NORMAL UI/PARAMETER immediate/deferred',
        'space':'X','start':'0x4D1','end_exclusive':'0x4D2','words':1,'status':'VERIFIED bank1 destination'}]
    normal=[];bounds=[]
    for sp in ('X','Y'):
        points={int(w['address']) for w in writes if w['space']==sp}
        for e in extras:
            if e['space']==sp:points.update(range(int(e['start'],16),int(e['end_exclusive'],16)))
        ordered=sorted(points);first=previous=None
        for x in ordered+[None]:
            if previous is not None and (x is None or x!=previous+1):
                normal.append({'space':sp,'start':hex(first),'end_exclusive':hex(previous+1),
                   'words':previous+1-first,'mode':'NORMAL recovered parameter families',
                   'status':'VERIFIED finite destination union under local domains; not all firmware traffic'})
                first=None
            if x is not None:
                if first is None:first=x
                previous=x
        bounds.append({'space':sp,'minimum':hex(min(points)),'maximum':hex(max(points)),
                       'distinct_words':len(points),'status':'enclosing bounds; holes in normal-parameter-intervals.csv'})
    candidates=[]
    for sp,lo,hi in (('X',0x4000,0x6000),('Y',0x3000,0x4000)):
        overlap=[r for r in normal if r['space']==sp and int(r['start'],16)<hi and int(r['end_exclusive'],16)>lo]
        assert not overlap
        for size in (64,128,256,512):
            candidates.append({'space':sp,'candidate_start':hex(lo),'candidate_end':hex(hi),'words':size,
              'starts_excluded_by_recovered_parameter_writes':0,'starts_not_excluded_by_this_path':hi-lo-size+1,
              'HOST_BANK_blocker':'removed for recovered normal parameter paths',
              'persistent_available':'NOT-YET-DETERMINED; remaining other host/DSP/DMA/worker/scratch exclusions not rerun'})
    report={'date':'2026-10-06','mode':'STATIC ONLY','scope':'recovered stock normal parameter boundaries; upstream event producer closure remains incomplete',
      'bank_at_2148C_callbacks':[0,1],'slot_at_213D4_callbacks':[0,11],
      'selector_at_27A10':{'0':'NORMAL REACHABLE','1':'NORMAL REACHABLE',
        '0x10':'IMPOSSIBLE BY CALLER BOUNDS in recovered normal graph',
        '0x40':'IMPOSSIBLE BY CALLER BOUNDS in recovered normal graph',
        'other_values_2_to_255':'IMPOSSIBLE BY CALLER BOUNDS in recovered normal graph'},
      'proof_premises':['normal guard object initialized successfully with capacity1',
        'identified normal event/service wrappers honor shared semaphore',
        'recovered immutable callback tables and entry paths; no arbitrary corruption/injected entry',
        'reviewed numeric/getter helper summaries; pending flag valid-entry domains separately retained'],
      'global_byte_domain':'UNRESOLVED; wider event byte values need not be excluded globally',
      'correction':'Phase8 dirtyflag alias separation was wrong:21F94/21FB2 both load220CC ->200067FC',
      'callback_tables':len({t['table'] for t in tables}),'callback_entries':len(tables),
      'bound_summaries':bounds,'largest_verified_persistent_allocation':None,
      'unresolved':['upstream callers/source domains of virtual note event thunks',
        'namespace21 bit3 dispatch would read D0002800 at215C4 (instruction bytes), not a fourth callback; producer condition not closed',
        'slot dispatcher tests8 bits but five adjacent function pointers; reserved pending-bit producer closure incomplete',
        'complete other normal addressed/bulk/extended host destinations',
        'exact candidate DSP/worker/DMA/save/scratch exclusions'],
      'track_identity':'0/1 verified stock synth allocation/parameter banks; UI Synth1/2 ordering HYPOTHESIS; MIDI1/2 mapping UNRESOLVED',
      'integrity':{'BIN':sha(arm),'SYX':sha(syxp.read_bytes()),'roundtrip_identical':True,
                   'report_script_SHA256':sha(Path(__file__).read_bytes())}}
    for name in ('callback-tables.csv','constructor-formulas.csv','parameter-writes.csv','summary.json','unsupported-paths.csv'):
        save(out/name,(src/name).read_bytes())
    save(out/'caller-tree.json',json.dumps(graph,indent=2)+'\n')
    save(out/'local-domains.csv',csvtext(domains));save(out/'special-destinations.csv',csvtext(extras))
    save(out/'normal-parameter-intervals.csv',csvtext(normal));save(out/'candidate-host-exclusion.csv',csvtext(candidates))
    save(out/'bank-domain-proof.json',json.dumps(report,indent=2)+'\n')
    save(out/'evidence-integrity.json',json.dumps(evidence,indent=2)+'\n')
    print(json.dumps({'tables':report['callback_tables'],'entries':report['callback_entries'],
                     'bounds':bounds,'result':'local recovered normal bank domain0/1; no persistent allocation proof'},indent=2))

if __name__=='__main__':main()
