"""Read pinned sources only; emit an auditable inventory, never firmware."""
import hashlib, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
UP = ROOT / 'plaits/upstream'
OUT = ROOT / 'builds/phase20e-full-plaits-audit'
REF = Path(r'C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main')
def clean(s):
    return re.sub(r'/\*.*?\*/|//[^\n]*', '', s, flags=re.S)
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((UP/'source-manifest.json').read_text())
    bad = []
    for f in manifest['files']:
        p = UP/f['path']
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != f['sha256']:
            bad.append(f['path'])
    assert not bad, bad
    voice = (UP/'plaits/dsp/voice.cc').read_text()
    models = re.findall(r'RegisterInstance\(&([a-z0-9_]+),\s*(true|false),\s*([^,]+),\s*([^\)]+)\)',voice)
    header = (UP/'plaits/dsp/voice.h').read_text()
    records = []
    for i, (member, env, gain, auxgain) in enumerate(models):
        cls = re.search(r'(\w+)\s+'+member+r';',header)[1]
        hp = next(p for p in (UP/'plaits/dsp').rglob('*.h') if re.search(r'class\s+'+cls+r'\b',p.read_text()))
        visited = set()
        def visit(p):
            if p in visited or not p.exists(): return
            visited.add(p)
            s = clean(p.read_text())
            for dep in re.findall(r'#include\s+"([^"]+)"',s): visit(UP/dep)
            if p.suffix == '.h': visit(p.with_suffix('.cc'))
        visit(hp)
        source = {str(p.relative_to(UP)).replace('\\','/'):clean(p.read_text()) for p in sorted(visited)}
        evidence = {'allocations':[], 'divisions':[], 'math':[], 'random':[], 'tables':[], 'arrays':[]}
        for path, s in source.items():
            # Counts are source occurrences, not execution costs. Keep evidence lines.
            raw = (UP/path).read_text().splitlines()
            for line, text in enumerate(raw,1):
                c = clean(text).strip()
                if not c: continue
                row = {'file':path,'line':line,'text':c}
                if 'Allocate<' in c: evidence['allocations'].append(row)
                if '/' in c and not c.startswith('#'): evidence['divisions'].append(row)
                if re.search(r'\b(sinf|cosf|sqrtf|powf|expf|logf|tanf|atanf|Sine|SemitonesToRatio|fast_pow2|fast_exp2|fast_rsqrt|SoftClip|Interpolate)\b',c): evidence['math'].append(row)
                if re.search(r'Random|random_state|rng_state',c): evidence['random'].append(row)
                if re.search(r'\b(lut_\w+|wav_\w+|syx_bank_\w+|word_banks_)',c): evidence['tables'].append(row)
                if re.search(r'\b(float|int\w*|uint\w*)\s+\w+\s*\[',c): evidence['arrays'].append(row)
        hs = clean(hp.read_text())
        records.append(dict(index=i,member=member,cls=cls,header=str(hp.relative_to(UP)).replace('\\','/'),already_enveloped=env=='true',out_gain=gain,aux_gain=auxgain,
            private_declarations=hs.split(' private:')[-1].split('DISALLOW_COPY')[0].strip(),
            dependencies=list(source),float_source_occurrences=sum(len(re.findall(r'\bfloat\b',s)) for s in source.values()),
            heap_source_occurrences=sum(len(re.findall(r'\b(new|malloc|calloc|realloc)\b',s)) for s in source.values()),evidence=evidence))
    rh=clean((UP/'plaits/resources.h').read_text())
    arrays=[]
    rc=clean((UP/'plaits/resources.cc').read_text())
    for typ,name,values in re.findall(r'const\s+(float|int16_t|int8_t|uint8_t|int32_t)\s+(\w+)\[\]\s*=\s*\{(.*?)\};',rc,re.S):
        n=len([v for v in values.split(',') if v.strip()])
        arrays.append(dict(name=name,type=typ,elements=n,bytes=n*{'float':4,'int16_t':2,'int8_t':1,'uint8_t':1,'int32_t':4}[typ],source='plaits/resources.cc'))
    labels=dict((k,int(v,16)) for k,v in (l.split() for l in (ROOT/'builds/phase20d-midi-vpre/fixture/labels.txt').read_text().splitlines()))
    ref_files=sorted(p for p in REF.rglob('*') if p.is_file() and '.git' not in p.parts)
    ref_hash={str(p.relative_to(REF)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in ref_files}
    data=dict(revision=manifest['revision'],stmlib_revision=manifest['stmlib_revision'],manifest_hashes_verified=len(manifest['files']),models=records,resources=arrays,
              labels={k:f'{v:04X}' for k,v in labels.items()},reference_before=ref_hash,
              limitations='Static source occurrence inventory and transitive include closure are not dynamic operation counts or DSP code sizes; shared header tables may overapproximate individual engine dependency sets.')
    (OUT/'source-inventory.json').write_text(json.dumps(data,indent=2)+'\n')
    cpp=['#include <cstdio>','#include <cmath>','#include <cstdint>','#include <vector>','#include <algorithm>','#include <chrono>','#include "plaits/dsp/voice.h"','#include "plaits/resources.h"',
         'template<class E> void probe(int index,const char* name,const uint8_t* data=nullptr) {',
         '  std::vector<uint64_t> arena(32768,0); stmlib::BufferAllocator a(arena.data(),arena.size()*8); E e{}; e.Init(&a); e.LoadUserData(data); e.Reset();',
         '  size_t used=arena.size()*8-a.free(), init_high=0; auto bytes=reinterpret_cast<const uint8_t*>(arena.data()); for(size_t i=0;i<arena.size()*8;++i) if(bytes[i]) init_high=i+1; float out[24]={},aux[24]={}; bool env=false; double energy=0; size_t nonfinite=0; double max_us=0;',
         '  for(int b=0;b<2048;++b) { plaits::EngineParameters p{}; p.note=24+(b%97); p.harmonics=(b%129)/128.f; p.timbre=((b*37)%129)/128.f; p.morph=((b*71)%129)/128.f; p.accent=.8f; p.trigger=(b%16==0)?5:((b%16<8)?4:0);',
         '    auto start=std::chrono::steady_clock::now(); e.Render(p,out,aux,24,&env); auto end=std::chrono::steady_clock::now(); max_us=std::max(max_us,std::chrono::duration<double,std::micro>(end-start).count());',
         '    for(int s=0;s<24;++s) { if(!std::isfinite(out[s])||!std::isfinite(aux[s])) ++nonfinite; else energy+=out[s]*out[s]+aux[s]*aux[s]; } }',
         '  printf("%d,%s,%zu,%zu,%zu,%zu,%.9g,%.9g\\n",index,name,sizeof(E),used,init_high,nonfinite,energy,max_us);','}',
         'int main(){ printf("index,class,host_object_bytes,arena_bytes,init_high_nonzero_byte,nonfinite,energy,host_max_us_not_DSP_cycles\\n");']
    for r in records:
        data=f'plaits::fm_patches_table[{r["index"]-2}]' if 2<=r['index']<=4 else 'nullptr'
        cpp.append(f'probe<plaits::{r["cls"]}>({r["index"]},"{r["cls"]}",{data});')
    cpp.extend(['printf("-1,Voice,%zu,0,0,0,0,0\\n",sizeof(plaits::Voice));','return 0;}'])
    (ROOT/'plaits/poc/full_audit/probe.cpp').write_text('\n'.join(cpp)+'\n')
    overlay=OUT/'host-overlay'
    ah=overlay/'plaits/dsp/fm/algorithms.h'
    ah.parent.mkdir(parents=True,exist_ok=True)
    original=(UP/'plaits/dsp/fm/algorithms.h').read_text()
    adapted=re.sub(r'template<> const [^;]+;', '', original)
    ah.write_text(adapted)
    (overlay/'plaits/resources.cc').write_text((UP/'plaits/resources.cc').read_text().replace('const int32_t* const lookup_table_i32_table[] = {\n};','const int32_t* const lookup_table_i32_table[] = {nullptr\n};'))
    print(json.dumps(dict(models=len(records),unique_classes=len(set(r['cls'] for r in records)),verified=len(manifest['files']),resources=arrays,reference_files=len(ref_hash)),indent=2))
if __name__=='__main__': main()
