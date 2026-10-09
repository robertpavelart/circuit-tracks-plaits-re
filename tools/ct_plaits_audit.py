#!/usr/bin/env python3
"""Static source inventories, not C++ sizeof, compilation, or DSP cycle mapping."""
import argparse,csv,hashlib,io,json,math,re
from pathlib import Path
from ct_static import ROOT,sha,save,BIN_HASH,SYX_HASH

def stripped(text):return re.sub(r'//[^\n]*|/\*.*?\*/','',text,flags=re.S)

def closure(root,initial):
    pending=list(initial);seen=set();missing=set()
    while pending:
        name=pending.pop()
        if name in seen:continue
        p=root/name
        if not p.is_file():missing.add(name);continue
        seen.add(name);text=p.read_text()
        pending+=re.findall(r'#include "([^"]+)"',text)
        if p.suffix=='.h' and p.with_suffix('.cc').is_file():pending.append(str(Path(name).with_suffix('.cc')).replace('\\','/'))
    return sorted(seen),sorted(missing)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True);out=Path(p.parse_args().output_dir).resolve()
    if out==ROOT/'original' or ROOT/'original' in out.parents:raise SystemExit('Protected original/')
    if out.exists():raise SystemExit('Choose a fresh output directory')
    upstream=ROOT/'plaits/upstream';manifest=json.loads((upstream/'source-manifest.json').read_text())
    for f in manifest['files']:assert sha((upstream/f['path']).read_bytes())==f['sha256'],f['path']
    assert sha((ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes())==BIN_HASH
    assert sha((ROOT/'original/circuittracks-firmware-4486.syx').read_bytes())==SYX_HASH
    tables=[]
    for name in ['plaits/resources.cc','stmlib/dsp/units.cc']:
        text=stripped((upstream/name).read_text())
        for m in re.finditer(r'const\s+(float|int16_t|int8_t|uint8_t|int32_t)\s+(\w+)\[\s*\]\s*=\s*\{([^{}]*)\}',text,re.S):
            values=[v.strip() for v in m[3].split(',') if v.strip()];width={'float':4,'int16_t':2,'int8_t':1,'uint8_t':1,'int32_t':4}[m[1]]
            header=(upstream/Path(name).with_suffix('.h')).read_text()
            declaration=re.search(r'\b'+re.escape(m[2])+r'\[(\d+)\]',header)
            elements=int(declaration[1]) if declaration else len(values)
            assert elements>=len(values)
            tables.append(dict(name=m[2],source=name,type=m[1],elements=elements,explicit_initializers=len(values),bytes=width*elements,
                packed_24bit_word_lower_bound=math.ceil(width*elements/3),element_addressed_bit_preserving_words=elements*(2 if width==4 else 1),
                status='SOURCE-DERIVED initializer count; no target layout or numerical conversion implied'))
    tablemap={t['name']:t for t in tables}
    assert tablemap['lut_sine']['elements']==641 and tablemap['lut_pitch_ratio_high']['elements']==257
    assert tablemap['lut_pitch_ratio_low']['elements']==257
    roots={'primitive':'plaits/dsp/oscillator/variable_saw_oscillator.h',
      'virtual_analog':'plaits/dsp/engine/virtual_analog_engine.h','fm':'plaits/dsp/engine/fm_engine.h',
      'waveshaping':'plaits/dsp/engine/waveshaping_engine.h','full_voice':'plaits/dsp/voice.h'}
    codes={};deps={}
    for name,entry in roots.items():
        files,missing=closure(upstream,[entry]);deps[name]=dict(files=files,missing=missing)
        total=0;functions=0
        for file in files:
            if file.endswith('resources.cc') or file.endswith('units.cc'):continue
            text=stripped((upstream/file).read_text());total+=sum(bool(l.strip()) for l in text.splitlines())
            matches=re.findall(r'\b(\w+)\s*\([^;{}]*\)\s*(?:const\s*)?\{',text)
            functions+=sum(x not in ['if','for','while','switch','catch'] for x in matches)
        codes[name]=dict(textual_dependency_files=len(files),noncomment_nonblank_lines=total,function_definition_candidates=functions,
            status='SOURCE-DERIVED lexical proxies; includes inactive variants/templates/unused header code; not emitted code',
            DSP_P_words=None,ARM_section_bytes=None)
    rate=[];fields=[];allocations=[]
    for f in manifest['files']:
        name=f['path']
        if not name.endswith(('.h','.cc')):continue
        text=(upstream/name).read_text()
        for lineno,line in enumerate(text.splitlines(),1):
            if re.search(r'kSampleRate|kCorrectedSampleRate|kMaxBlockSize|kBlockSize|48000|47872|44100|96000',line):
                rate.append(dict(file=name,line=lineno,text=line.strip()))
            if re.search(r'\b(?:float|bool|uint32_t|int|size_t)\s+\w+_\s*(?:\[.*\])?;',line):
                fields.append(dict(file=name,line=lineno,declaration=line.strip(),status='member candidate, not parsed C++ ABI'))
            if 'allocator->Allocate' in line:allocations.append(dict(file=name,line=lineno,text=line.strip()))
    state=[dict(name='VariableSaw primitive',floats=6,u32=0,bools=1,pointers=0,payload_bytes=25,fixed_scalar_words=7,bit_preserving_scalar_words=13,native_allocator_bytes=0,
              evidence='variable_saw_oscillator.h member fields; excludes parameters/stack/output'),
           dict(name='FMEngine',floats=7,u32=3,bools=0,pointers=0,payload_bytes=40,fixed_scalar_words=10,bit_preserving_scalar_words=20,native_allocator_bytes=0,
              evidence='fm_engine.h; excludes Engine metadata/vptr/controls/output; FIR fields not explicitly initialized in Init'),
           dict(name='VirtualAnalogEngine',floats=35,u32=0,bools=4,pointers=1,payload_bytes=148,fixed_scalar_words=40,bit_preserving_scalar_words=75,native_allocator_bytes=96,
              evidence='3 VariableShape objects + VariableSaw + 2 floats + pointer; excludes Engine metadata/vptr'),
           dict(name='WaveshapingEngine',floats=15,u32=0,bools=2,pointers=0,payload_bytes=62,fixed_scalar_words=17,bit_preserving_scalar_words=32,native_allocator_bytes=0,
              evidence='2 Oscillator objects + 3 floats; excludes Engine metadata/vptr')]
    # Fixed scalar mapping is an illustration requiring redesigned formats, not a sizeof result.
    for s in state:s['status']='SOURCE-DERIVED scalar payload; DSP scalar mappings ESTIMATE and require numeric design'
    required={'primitive_with_pitch':['lut_pitch_ratio_high','lut_pitch_ratio_low'],
       'fm':['lut_pitch_ratio_high','lut_pitch_ratio_low','lut_sine','lut_fm_frequency_quantizer','lut_4x_downsampler_fir'],
       'waveshaping':['lut_pitch_ratio_high','lut_pitch_ratio_low','lut_sine','lut_fold','lut_fold_2',
          'lut_ws_inverse_tan','lut_ws_inverse_sin','lut_ws_linear','lut_ws_bump','lut_ws_double_bump'],
       'virtual_analog':['lut_pitch_ratio_high','lut_pitch_ratio_low']}
    sets={n:dict(tables=names,total_source_data_bytes=sum(tablemap[t]['bytes'] for t in names),
         element_addressed_bit_preserving_words=sum(tablemap[t]['element_addressed_bit_preserving_words'] for t in names),
         status='SOURCE-DERIVED complete referenced arrays; includes trimmable sine tail; no pointer arrays/constants') for n,names in required.items()}
    result=dict(revision=manifest['revision'],stmlib_revision=manifest['stmlib_revision'],license='MIT for Plaits/selected stmlib code; notices preserved',
        source_verified_files=len(manifest['files']),sources_bytes=manifest['total_bytes'],native_block=12,max_voice_block=24,
        nominal_sample_rate=48000,corrected_sample_rate=47872.34,
        conditional_circuit_sample_rate=48046.875,pitch_error_cents_if_unchanged=1200*math.log2(48046.875/47872.34),
        trigger_delay_ms_nominal=5*12/48000*1000,trigger_delay_ms_at_32=5*32/48046.875*1000,
        source_code_proxies=codes,engine_scalar_payloads=state,table_sets=sets,
        all_generated_resources_bytes=sum(t['bytes'] for t in tables if t['source']=='plaits/resources.cc'),
        all_generated_resources_element_addressed_words=sum(t['element_addressed_bit_preserving_words'] for t in tables if t['source']=='plaits/resources.cc'),
        full_module_shared_pool_bytes=16384,
        conclusion='small derived oscillator plausibly compatible; safe fit UNRESOLVED; no target compilation or numeric adapter',
        source_notes=['float payload bytes assume32-bit float, bool byte; no sizeof or padding inferred',
                      '32-bit scalar bit preservation uses two24-bit addressable words; packed-byte floor is not a usable object layout',
                      'fixed words require per-field range/precision choices, not all Q1.23',
                      'dependency proxies do not predict DSP program words; include guards/unused branches not modeled'])
    out.mkdir(parents=True,exist_ok=False)
    for name,items in [('tables.csv',tables),('state-fields.csv',fields),('rate-block-references.csv',rate),('allocator-sites.csv',allocations)]:
        keys=sorted(set().union(*(x.keys() for x in items)));s=io.StringIO();w=csv.DictWriter(s,fieldnames=keys);w.writeheader();w.writerows(items);save(out/name,s.getvalue())
    save(out/'comparison.json',json.dumps(result,indent=2)+'\n');save(out/'dependency-closures.json',json.dumps(deps,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
