"""Build a CIRCUIT-only audit wrapper linked to the installed pinned DSP libraries."""
import json,subprocess
from environment import *
s=(REF/'tools/dsptool/dsptool.cpp').read_text()
s=s.replace('#include <cstdio>','#include <cstdio>\n#include <stdexcept>')
s=s.replace('static uint64_t g_watchMax = 200000;','static uint64_t g_watchMax = 2000000000; static TWord g_freeTail=0x4000; static uint64_t g_pWrites=0;')
s=s.replace('if (!g_watchOut || !g_watchMax) return;', 'if(a==MemArea_P && w){++g_pWrites;if(addr>=g_freeTail && addr<0x4000)throw std::runtime_error("Reclaimed P write");}\n    if(a==MemArea_P && !w)return;\n    if (!g_watchOut || !g_watchMax) return;')
s=s.replace('std::vector<uint8_t> wX(0x80000), wY(0x80000);','std::vector<uint8_t> wX(0x80000), wY(0x80000), wP(0x80000,1);')
s=s.replace('else if (c == "MAX") { s >> maxi; }','else if (c == "MAX") { s >> maxi; }\n        else if(c=="FREETAIL"){std::string v;s>>v;g_freeTail=strtoul(v.c_str(),nullptr,16);}\n        else if(c=="REGDUMP"){const auto&r=dsp.readRegs();printf("REG:");')
s=s.replace('else if (c == "HIST")', 'else if(c=="RESETTRACE"){std::fill(trX.begin(),trX.end(),0);std::fill(trY.begin(),trY.end(),0);}\n        else if (c == "HIST")')
fields=['a0','a1','a2','b0','b1','b2','x0','x1','y0','y1','pc','sr','omr','la','lc','sp','sc']+[f'{prefix}{i}' for prefix in ('r','n','m') for i in range(8)]
snippet=''.join(f'{{int64_t v=0;dsp.readRegToInt(Reg_{n.upper()},v);printf(" {n}=%llx",(unsigned long long)v);}}' for n in fields)+'printf("\\n");}'
s=s.replace('printf("REG:");', 'printf("REG:");'+snippet)
s=s.replace('if (watching) { g_memWatch', 'g_memWatch[MemArea_P]=wP.data();g_memWatchCb=watchCb;\n            if (watching) { g_memWatch')
s=s.replace('g_curPC = dsp.getPC().toWord(); if', 'g_curPC = dsp.getPC().toWord();if(g_curPC>=g_freeTail && g_curPC<0x4000)throw std::runtime_error("Reclaimed P execution"); if')
s=s.replace('g_memWatch[MemArea_X] = g_memWatch[MemArea_Y] = nullptr;', 'g_memWatch[MemArea_X] = g_memWatch[MemArea_Y] = g_memWatch[MemArea_P] = nullptr;')
s=s.replace('if (!histFile.empty()) { FILE* h', 'printf("PWRITES %llu\\n",(unsigned long long)g_pWrites);\n    if (!histFile.empty()) { FILE* h')
source=OUT/'dsptool-audit.cpp';source.write_text(s)
cache=(REF/'ext/dsp56300/build/CMakeCache.txt').read_text();cxx=next(l.split('=',1)[1] for l in cache.splitlines() if l.startswith('CMAKE_CXX_COMPILER:FILEPATH='))
libs=[REF/'ext/dsp56300/build/source'/name for name in ('dsp56kEmu/libdsp56kEmu.a','dsp56kBase/libdsp56kBase.a','asmjit/libasmjit.a','vtuneSdk/libvtuneSdk.a')]
exe=OUT/'dsptool-audit.exe'
args=[cxx,'-O2','-std=c++17','-I'+str(REF/'ext/dsp56300/source'),'-I'+str(REF/'ext/dsp56300/source/asmjit/src'),str(source),*[str(p) for p in libs],'-static','-lpthread','-o',str(exe)]
r=subprocess.run(args,capture_output=True,text=True);(OUT/'audit-tool-build.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr[-1500:]
(OUT/'audit-tool-provenance.json').write_text(json.dumps(dict(compiler=cxx,source_sha256=sha(source.read_bytes()),exe_sha256=sha(exe.read_bytes()),libraries={str(p):sha(p.read_bytes()) for p in libs},command=args,modifications=['P-tail execution/write guard','Register dumps','Untruncated audit watch log'],emulator_commit='44353be2f0156cac970c6ab4f467ea1998b40605'),indent=2)+'\n')
print('Built pinned-library audit tool',flush=True)
