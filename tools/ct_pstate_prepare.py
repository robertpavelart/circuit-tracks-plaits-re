"""Fresh standalone P-state fixtures/renderer, using frozen REGOPT/core inputs.

Never loads, rewrites or repacks Circuit firmware. P:2D29 is a synthetic test
object, NOT a Circuit allocation. Generated runner changes are assertion-checked.
"""
import argparse, hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'builds/phase20c-pstate'
INIT = [0, 0, 0x200000, 0, 41943, 0x200000, 0]
STATE = 0x2D29

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()

def fresh(p):
    p = p.resolve()
    if p == BASE or not p.is_relative_to(BASE) or p.exists():
        raise ValueError('Fresh child of builds/phase20c-pstate required')
    p.mkdir(parents=True)
    return p

def write(p, s):
    with p.open('x', encoding='utf8', newline='\n') as f: f.write(s)

def guards():
    roots = ['original', 'firmware', 'emulator/upstream', 'plaits/poc',
             'builds/phase20a-regopt/final', 'builds/phase20a-regopt/timing',
             'builds/phase20c-fixedstate/final-v1',
             'builds/phase20c-livepatch-design/final-v2']
    pp = set()
    for r in roots:
        pp.update(p for p in (ROOT/r).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    pp.update([ROOT/'builds/phase19a/core-build/replay_core.lib',
               ROOT/'builds/phase19a/core-build/upstream/asmjit/asmjit.lib'])
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(pp)}

def generate(out):
    out = fresh(out)
    write(out/'input-guards.json', json.dumps(guards(), indent=2, sort_keys=True)+'\n')
    assembly = (ROOT/'builds/phase20a-regopt/final/assembly/variablesaw.asm').read_text()
    for name, space, longx in [('low-p', 'p', False), ('high-p', 'p', True), ('high-x', 'x', True)]:
        folder = out/name; folder.mkdir()
        count = [0]
        def replace(m):
            address = int(m[1], 16)
            if 0x20 <= address < 0x27:
                count[0] += 1
                return f'{space}:>${STATE+address-0x20:06x}' if space=='p' else f'x:>${address:06x}'
            return f'x:>${address:06x}' if longx else m[0]
        s = re.sub(r'x:\$([0-9a-f]{6})', replace, assembly)
        if space=='p': s = '\n'.join(('movem '+line[5:] if line.startswith('move ') and 'p:' in line else line) for line in s.splitlines())+'\n'
        assert count[0] == 63
        # MOVE(M) is the manual's legal alias; assembler emits MOVEM_ea opcodes.
        write(folder/'variablesaw.asm', s)
        (folder/'state-init.be24').write_bytes(b''.join(v.to_bytes(3, 'big') for v in INIT))
    source = (ROOT/'plaits/poc/regopt/runner_final.cpp').read_text()
    def edit(a, b):
        nonlocal source
        assert source.count(a)==1, a[:80]
        source = source.replace(a,b)
    edit('struct Program{', '''// The pinned assembler cannot encode absolute MOVEM_ea (its EA parser
// only accepts Rn forms). This narrow encoder follows FM13-133 and12-18:
// 00000111 W1 MMMRRR 10 dddddd, absolute EA=110000 + 24-bit extension.
// No upstream core/assembler changes; only the three used data registers.
AssembleResult qualifiedAssemble(Assembler&assembler,const std::string&s){
 // FM PDF320/323/327, same absolute EA110000. The pinned EA parser also
 // rejects long absolute jumps. Preserve exact condition and destination.
 std::regex jump("(jmp|jsr|jlt|jge|jle|jne|jeq) \\\\$([0-9a-f]{6})");std::smatch jm;
 if(std::regex_match(s,jm,jump)&&std::stoul(jm[2].str(),nullptr,16)>0xfff){
  std::string mnemonic=jm[1];auto shortOp=assembler.assemble((mnemonic+" $001").c_str());
  if(!shortOp.success()||shortOp.wordCount!=1)throw std::runtime_error("Short branch qualification");
  AssembleResult result;result.wordCount=2;result.word[1]=std::stoul(jm[2].str(),nullptr,16);
  result.word[0]=mnemonic=="jmp"?0x0af080:mnemonic=="jsr"?0x0bf080:0x0af0a0|((shortOp.word[0]>>12)&15);return result;
 }
 if(s.rfind("movem ",0)!=0)return assembler.assemble(s.c_str());
 std::regex read("movem p:>\\\\$([0-9a-f]{6}),(a|x0|y0)"),write("movem (a),p:>\\\\$([0-9a-f]{6})");std::smatch m;
 AssembleResult op;bool isRead=std::regex_match(s,m,read);
 std::string reg;TWord address;
 if(isRead){address=std::stoul(m[1].str(),nullptr,16);reg=m[2];}
 else if(std::regex_match(s,m,write)){reg=m[1];address=std::stoul(m[2].str(),nullptr,16);}
 else throw std::runtime_error("Unsupported MOVEM fixture form");
 op.word[0]=(isRead?0x07f080:0x077080)|(reg=="a"?14:reg=="x0"?4:6);op.word[1]=address;op.wordCount=2;return op;
}
struct Program{''')
    edit('auto op=assembler.assemble(s.c_str());', 'auto op=qualifiedAssemble(assembler,s);')
    edit('std::vector<TWord> words;TWord origin=0x200,done=0;',
         'std::vector<TWord> words,initial;TWord origin=0x200,done=0;')
    edit('Program(const fs::path&path){', '''Program(const fs::path&path,TWord at){
  origin=at;std::ifstream seed(path.parent_path()/"state-init.be24",std::ios::binary);
  for(unsigned i=0;i<7;++i){TWord v=0;for(unsigned j=0;j<3;++j){int c=seed.get();if(c<0)throw std::runtime_error("Missing exact P-object seed");v=(v<<8)|c;}initial.push_back(v);}
  if(seed.get()!=EOF||initial!=std::vector<TWord>{0,0,0x200000,0,41943,0x200000,0})throw std::runtime_error("Bad initializer");''')
    edit('for(int pass=0;pass<2;++pass){', 'for(int pass=0;pass<12;++pass){\n   const auto previous=labels;')
    edit('if(pass&&!labels.count(m[1].str()))throw std::runtime_error("Unknown label");', '')
    edit('(pass?labels.at(m[1].str()):1)', '(labels.count(m[1].str())?labels.at(m[1].str()):origin)')
    edit('if(pass==1&&labels.at("done")!=pc)throw std::runtime_error("Assembly layout changed");',
         'if(pass&&labels==previous){if(labels.at("done")!=pc)throw std::runtime_error("Layout mismatch");break;}if(pass==11)throw std::runtime_error("Assembly relaxation failed");')
    edit('done=labels.at("done");if(done>=0x1000)throw std::runtime_error("P capacity");',
         'done=labels.at("done");if(done+2>=0x2d29)throw std::runtime_error("Code overlaps synthetic data object");')
    edit('const Program&p;DSP*cpu=nullptr;', 'const Program&p;DSP*cpu=nullptr;bool pstate;std::vector<TWord>persistent=std::vector<TWord>(7,0xa5a5a5);uint64_t pReads=0,pWrites=0;')
    edit('Bus(const Program&pp,std::ofstream&t,unsigned hi):p(pp),trace(t),scratchHi(hi)',
         'Bus(const Program&pp,std::ofstream&t,unsigned hi,bool isP):p(pp),pstate(isP),trace(t),scratchHi(hi)')
    edit('std::make_unique<Memory>(*validator,0x1000)', 'std::make_unique<Memory>(*validator,0x4000)')
    edit('if(a==MemArea_P){', 'if(a==MemArea_P){\n   if(pstate&&at>=0x2d29&&at<0x2d30){++pReads;return persistent.at(at-0x2d29);}')
    edit('if(a==MemArea_X&&((at>=0x20&&at<0x27)', 'if(a==MemArea_X&&((!pstate&&at>=0x20&&at<0x27)')
    edit('if(a==MemArea_P)throw std::runtime_error("P write forbidden");',
         '''if(a==MemArea_P){if(!pstate||at<0x2d29||at>=0x2d30)throw std::runtime_error("Unowned P write");persistent.at(at-0x2d29)=v&0xffffff;++pWrites;}
  else''')
    edit('if(!((at>=0x20&&at<0x27)', 'if(!((!pstate&&at>=0x20&&at<0x27)')
    edit('pc=at;op=word;', 'if(at>=0x2d29&&at<0x2d30)throw std::runtime_error("Mutable P data executed");pc=at;op=word;')
    edit('s.rfind("move a,x:",0)==0', '(s.rfind("move a,x:",0)==0||s.rfind("movem a,p:",0)==0)')
    edit('int main(int argc,char**argv)try{', 'int main(int argc,char**argv)try{\n if(argc==3&&std::string(argv[1])=="--fixtures")return fixtures(argv[2]);')
    edit('if(argc!=5)throw std::runtime_error("assembly cases.tsv fresh-output scratchHighHex");',
         'if(argc!=7)throw std::runtime_error("assembly cases.tsv fresh-output scratchHighHex originHex p|x");')
    edit('const fs::path root=fs::path(__FILE__).parent_path().parent_path().parent_path().parent_path();',
         'const fs::path root=PSTATE_ROOT;')
    edit('root/"builds/phase20a-regopt"', 'root/"builds/phase20c-pstate"')
    edit('Program program(argv[1]);', 'const bool isP=std::string(argv[6])=="p";if(!isP&&std::string(argv[6])!="x")throw std::runtime_error("Bad mode");Program program(argv[1],std::stoul(argv[5],nullptr,16));')
    edit('std::ofstream raw(out/"output.i32",std::ios::binary)', 'std::ofstream raw(out/"output.i32",std::ios::binary)')
    edit('writeHash=execHash=1469598103934665603ull;', 'writeHash=execHash=1469598103934665603ull;pReads=pWrites=0;')
    edit('div_issued\\n";', 'div_issued,P_state_reads,P_state_writes\\n";')
    edit('unsigned(std::stoul(argv[4],nullptr,16)))', 'unsigned(std::stoul(argv[4],nullptr,16)),isP)')
    edit('bus->x[0x22]=F/2;bus->x[0x24]=TWord(std::llround(.01*F));bus->x[0x25]=F/2;last=id;',
         'if(isP)bus->persistent=program.initial;else for(unsigned i=0;i<7;++i)bus->x[0x20+i]=program.initial[i];last=id;')
    edit("<<bus->divIssued<<'\\n';", "<<bus->divIssued<<','<<bus->pReads<<','<<bus->pWrites<<'\\n';")
    edit('signed24(bus->x[0x20+i])', 'signed24(isP?bus->persistent[i]:bus->x[0x20+i])')
    edit('<<",\\\"P_decoder_padding_words\\\":2', '<<",\\\"persistent_P_words\\\":"<<(isP?7:0)<<",\\\"persistent_X_words\\\":"<<(isP?0:7)<<",\\\"P_decoder_padding_words\\\":2')
    source=source.replace('int main(int argc,char**argv)try{', '#include "fixtures.inl"\nint main(int argc,char**argv)try{')
    write(out/'runner.cpp', source)
    write(out/'fixtures.inl', (ROOT/'plaits/poc/pstate/fixtures.inl').read_text())
    cmake='''cmake_minimum_required(VERSION 3.15)
project(pstate_standalone LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS_DEBUG "/MDd /Zi /O2 /Ob2")
set(ROOT "@ROOT@")
add_executable(pstate runner.cpp)
target_include_directories(pstate PRIVATE "${ROOT}/emulator/upstream/dsp56300/source" "${ROOT}/emulator/upstream/asmjit/src")
target_compile_definitions(pstate PRIVATE DSP56K_FORCE_INTERPRETER=1 DSP56300_DEBUGGER=0 PSTATE_ROOT="${ROOT}")
target_link_libraries(pstate PRIVATE "${ROOT}/builds/phase19a/core-build/replay_core.lib" "${ROOT}/builds/phase19a/core-build/upstream/asmjit/asmjit.lib" bcrypt)
'''.replace('@ROOT@', ROOT.as_posix())
    write(out/'CMakeLists.txt',cmake)
    write(out/'preparation.json', json.dumps(dict(synthetic_state_start=STATE,words=7,
        Circuit_ownership='UNRESOLVED/NOT RESERVED',initial=INIT,state_sites=63,
        renderer_changes='Only seven state operands change; high variants additionally long-address X operands and naturally high control targets',
        baseline_assembly_sha256=sha(ROOT/'builds/phase20a-regopt/final/assembly/variablesaw.asm'),
        baseline_runner_sha256=sha(ROOT/'plaits/poc/regopt/runner_final.cpp'),
        prepare_sha256=sha(Path(__file__))), indent=2)+'\n')
    print(out)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--output-dir',type=Path,required=True)
    generate(a.parse_args().output_dir)
