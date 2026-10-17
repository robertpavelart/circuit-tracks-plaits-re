"""Offline-only: override pinned Memory translation, retaining its class ABI.

Windows fibers suspend at EVERY opcode fetch, including recursive DO bodies.
No instruction or wait in either loaded DSP program is patched.
"""
import json, subprocess
from environment import ROOT, REF, sha
OUT=ROOT/'builds/phase20j-coupled-replay';OUT.mkdir(exist_ok=True)
src=REF/'ext/dsp56300/source'
s=(src/'dsp56kEmu/memory.cpp').read_text()
s=s.replace('namespace dsp56k\n{','namespace dsp56k\n{\nextern bool replayAccess(const Memory*, EMemArea, TWord, bool, TWord&);\nextern void replayObserve(const Memory*, EMemArea, TWord, TWord);\nextern void replayFetch(const Memory*, TWord&);',1)
s=s.replace('bool Memory::dspWrite( EMemArea& _area, TWord& _offset, TWord _value )\n\t{','bool Memory::dspWrite( EMemArea& _area, TWord& _offset, TWord _value )\n\t{\n        if(replayAccess(this,_area,_offset,true,_value))return true;')
s=s.replace('TWord Memory::get( EMemArea _area, TWord _offset ) const\n\t{','TWord Memory::get( EMemArea _area, TWord _offset ) const\n\t{\n        TWord hooked=0;if(replayAccess(this,_area,_offset,false,hooked))return hooked;')
s=s.replace('void Memory::getOpcode(TWord _offset, TWord& _wordA, TWord& _wordB) const\n\t{','void Memory::getOpcode(TWord _offset, TWord& _wordA, TWord& _wordB) const\n\t{\n        replayFetch(this,_offset);')
s=s.replace('const auto res = m_mem[_area][_offset];','const auto res = m_mem[_area][_offset];\n        replayObserve(this,_area,_offset,res);')
assert s.count('if(replayAccess(')==2 and 'replayFetch(this,_offset)' in s
(OUT/'memory.cpp').write_text(s)
d=(src/'dsp56kEmu/dsp.cpp').read_text()
d=d.replace('assert(false && "Peripherals configuration is not supported");\n\t\treturn nullptr;', '// Offline ICC adapter has synchronous read/write only; no scheduled peripheral work.\n        return &dspExecNop;')
assert 'return &dspExecNop;' in d
(OUT/'dsp.cpp').write_text(d)
cache=(REF/'ext/dsp56300/build/CMakeCache.txt').read_text()
cxx=next(l.split('=',1)[1] for l in cache.splitlines() if l.startswith('CMAKE_CXX_COMPILER:FILEPATH='))
libs=[REF/'ext/dsp56300/build/source'/n for n in ('dsp56kEmu/libdsp56kEmu.a','dsp56kBase/libdsp56kBase.a','asmjit/libasmjit.a','vtuneSdk/libvtuneSdk.a')]
args=[cxx,'-O2','-std=c++17','-DNDEBUG','-DDSP56300_DEBUGGER=0','-DDSP56K_USE_VTUNE_JIT_PROFILING_API','-DASMJIT_STATIC','-I'+str(src),'-I'+str(src/'dsp56kEmu'),'-I'+str(src/'asmjit/src'),str(OUT/'memory.cpp'),str(OUT/'dsp.cpp'),str(ROOT/'plaits/poc/authentic_qualification/coupled.cpp'),*[str(p) for p in libs],'-static','-lpthread','-o',str(OUT/'coupled.exe')]
r=subprocess.run(args,capture_output=True,text=True)
(OUT/'build.log').write_text(r.stdout+r.stderr)
assert r.returncode==0,r.stderr[-4000:]
(OUT/'build-provenance.json').write_text(json.dumps(dict(command=args,inputs={str(p):sha(p.read_bytes()) for p in [src/'dsp56kEmu/memory.cpp',src/'dsp56kEmu/dsp.cpp',ROOT/'plaits/poc/authentic_qualification/coupled.cpp',*libs]},memory_override=sha(s.encode()),dsp_override=sha(d.encode()),exe=sha((OUT/'coupled.exe').read_bytes())),indent=2))
print('Built coupled runner',flush=True)
