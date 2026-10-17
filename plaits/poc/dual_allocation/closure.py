"""Add source producer closure, exact relocation ledger and sender qualifications."""
import ast, base64, hashlib, json
from pathlib import Path
from study import ROOT,REF,OUT
def main():
    a=json.loads((OUT/'allocation.json').read_text())
    original=(ROOT/'builds/phase20d-midi-vpre/fixture/reference-core0.be24').read_bytes()
    old=dict((k,int(v,16)) for k,v in (l.split() for l in (ROOT/'builds/phase20d-midi-vpre/fixture/labels.txt').read_text().splitlines()))
    ledger=[]
    for profile in ('osc_only','osc_va'):
        new=(OUT/f'{profile}.be24').read_bytes();nl=json.loads((OUT/f'{profile}-labels.json').read_text())
        # All prefix changes are externally targeted relocations, not stock DSP
        # synthesis arithmetic. There are no other prefix word changes.
        diff=[pc for pc in range(old['vpre']) if original[3*pc:3*pc+3]!=new[3*pc:3*pc+3]]
        assert diff==[0xd22,0x2acf],diff
        ledger.append(dict(profile=profile,changed_prefix_words=[dict(P=pc,before=int.from_bytes(original[3*pc:3*pc+3],'big'),after=int.from_bytes(new[3*pc:3*pc+3],'big')) for pc in diff],
            relocations=[dict(symbol=k,before=v,after=nl[k]) for k,v in old.items() if k in nl and v!=nl[k]],
            bootstrap_word_count_required=len(new)//3,untouched_prefix_except_two_target_operands=True,
            free_half_open=[len(new)//3,0x4000],free_inclusive=[len(new)//3,0x3fff]))
    # Extract only the existing core1 bootstrap block from uploader COPY/ADD
    # spans. Never reconstruct, package or save an ARM application image.
    man=json.loads((REF/'firmware/b1.3/manifest.json').read_text())
    at=int(man['report']['granular']['core1_block'],16)-0x08010000
    n=man['report']['granular']['core1_words'];need=(at,at+6+3*n)
    line=next(l for l in (REF/'tools/rc_uploader.html').read_text(encoding='utf-8').splitlines() if l.startswith('const PATCHES = '))
    patch=json.loads(line[len('const PATCHES = '):].rstrip(';'))['B1.3']
    stock=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes();parts=[];cursor=0
    for op in patch['ops']:
        chunk=stock[op[1]:op[1]+op[2]] if op[0]==0 else base64.b64decode(op[1])
        lo=max(cursor,need[0]);hi=min(cursor+len(chunk),need[1])
        if lo<hi:parts.append(chunk[lo-cursor:hi-cursor])
        cursor+=len(chunk)
    block=b''.join(parts);assert len(block)==6+3*n
    assert int.from_bytes(block[:3],'big')==n
    (OUT/'retained-core1.be24').write_bytes(block[6:])
    import study
    V,S,GD,D,B=study.setup()
    off=int.from_bytes(stock[0x19708:0x1970c],'little')-0x08010000
    sn=int.from_bytes(stock[off:off+3],'big');sp=[int.from_bytes(stock[i:i+3],'big') for i in range(off+6,off+6+sn*3,3)]
    w,ls=GD.core1_code(sn);sp[0x12a]=0x0c0000|ls['c1loop']
    assert D.to_bytes(sp+w)==block[6:]
    producer=[]
    for file in ('vcf21_dsp.py','masterfx_dsp.py','drums2_dsp.py','sampler_dsp.py','granular_dsp.py'):
        tree=ast.parse((REF/'tools'/file).read_text())
        def walk(nodes,scope=''):
            for node in nodes:
                if isinstance(node,ast.FunctionDef):
                    name=scope+node.name
                    calls=sorted(set((q.func.id if isinstance(q.func,ast.Name) else ast.unparse(q.func)) for q in ast.walk(node) if isinstance(q,ast.Call)))
                    cls='REMOVE' if file=='vcf21_dsp.py' and node.name in ('osc_ctrl','waves','fold','modterm','ox') else 'SHARED-INFRASTRUCTURE' if file=='vcf21_dsp.py' else 'KEEP'
                    producer.append(dict(file=str(REF/'tools'/file),symbol=name,line=node.lineno,end_line=node.end_lineno,classification=cls,role='assembly producer (may be inlined, not a physical DSP callable)',calls=calls))
                    walk(node.body,name+'/')
                else:
                    for field in ('body','orelse','finalbody'):
                        if isinstance(getattr(node,field,None),list):walk(getattr(node,field),scope)
        walk(tree.body)
    c1graph=[];cl={k:int(v,16) for k,v in man['report']['granular']['labels'].items()};sl=sorted(cl.items(),key=lambda x:x[1])
    for i,(name,start) in enumerate(sl):
        end=sl[i+1][1] if i+1<len(sl) else n
        c1graph.append(dict(symbol=name,core=1,start=start,end=end,classification='KEEP',reason='granular/glitch or stock gather service dependency'))
    result=dict(core0_manifest_blocks=a['graph'],source_producers=producer,core1_manifest_blocks=c1graph,relocation_ledger=ledger,
        retained_core1_words=n,retained_core1_sha256=hashlib.sha256(block[6:]).hexdigest(),retained_core1_source_matches_existing_uploader_block=True,
        VA_control_classification='CONDITIONAL REMOVE under the legal ARM sender contract; stale line/VA and gran/VA negative fixtures fail. Keep ARM VA signature/selector logic because FXSEQ and GRAN depend on it.',
        indirect_closure_policy='Entire stock DSP prefix, all untouched source-selection/drum/MasterFX/capture/core1 regions, and all shared indexed tables are kept. Stock dynamic dispatch targets remain unresolved but none is reclaimed.',
        scope='Complete edited-module source producer inventory and all manifest mod block/table symbols; not a claimed complete recovered stock dynamic call graph.')
    (OUT/'dependency-closure.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(core0_blocks=len(a['graph']),source_producers=len(producer),core1_blocks=len(c1graph),prefix_changed_words=[hex(q['P']) for q in ledger[1]['changed_prefix_words']],core1_source_match=True,free_range=[hex(x) for x in ledger[1]['free_half_open']]),indent=2))
if __name__=='__main__':main()
