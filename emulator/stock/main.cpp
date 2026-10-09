// Phase 19B1 ONLY. No DSP execution call exists in this executable.
// Input opened read-only. Exact identity checked before program memory loading.
#include "dsp56kEmu/dsp.h"
#include "dsp56kEmu/disasm.h"
#include <windows.h>
#include <bcrypt.h>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
using namespace dsp56k;
namespace fs=std::filesystem;

std::string sha(const std::vector<unsigned char>& bytes) {
    BCRYPT_ALG_HANDLE alg=nullptr;
    if(BCryptOpenAlgorithmProvider(&alg,BCRYPT_SHA256_ALGORITHM,nullptr,0)<0)
        throw std::runtime_error("SHA256 provider failed");
    unsigned char digest[32];
    const auto status=BCryptHash(alg,nullptr,0,const_cast<PUCHAR>(bytes.data()),
                               ULONG(bytes.size()),digest,32);
    BCryptCloseAlgorithmProvider(alg,0);
    if(status<0) throw std::runtime_error("SHA256 failed");
    std::ostringstream out; out<<std::hex<<std::setfill('0');
    for(auto v:digest)out<<std::setw(2)<<unsigned(v);
    return out.str();
}
std::vector<unsigned char> read(const fs::path& p) {
    std::ifstream in(p,std::ios::binary);
    if(!in)throw std::runtime_error("Cannot read input");
    return {std::istreambuf_iterator<char>(in),std::istreambuf_iterator<char>()};
}
std::ofstream output(const fs::path& p) {
    if(fs::exists(p))throw std::runtime_error("Output exists");
    std::ofstream out(p,std::ios::binary);
    if(!out)throw std::runtime_error("Cannot create output");
    return out;
}
// A constructor-only implementation probe: never a stock initial state.
struct DenyPeripheral:IPeripherals {
    DenyPeripheral():IPeripherals(PeripheralType::PeripheralsNop){}
    TWord read(TWord,Instruction)override{throw std::runtime_error("Peripheral read denied");}
    const TWord* readAsPtr(TWord,Instruction)override{throw std::runtime_error("Pointer read denied");}
    void write(TWord a,TWord v)override{
        // Constructor-only probe permits the two explicit reset priority writes.
        // This adapter is NEVER attached to a CPU containing the stock image.
        if((a!=0xfffffe&&a!=0xffffff)||v!=0)throw std::runtime_error("Peripheral write denied");
    }
    void reset()override{} void setSymbols(Disassembler&)const override{} void terminate()override{}
};
void resetProbe(const fs::path& dest) {
    DefaultMemoryValidator v; Memory m(v,0x100); DenyPeripheral x,y;
    DSP cpu(m,&x,&y); // no program loaded and no instruction executed
    const auto& r=cpu.readRegs(); auto out=output(dest);
    out<<"{\"scope\":\"EMULATOR VERIFIED constructor reset only; not stock handoff\","
       <<"\"PC\":"<<r.pc.var<<",\"SR\":"<<r.sr.var<<",\"OMR\":"<<r.omr.var
       <<",\"SP\":"<<r.sp.var<<",\"SC\":"<<unsigned(r.sc.var)
       <<",\"LA\":"<<r.la.var<<",\"LC\":"<<r.lc.var
       <<",\"VBA\":"<<r.vba.var<<",\"SZ\":"<<r.sz.var<<",\"EP\":"<<r.ep.var
       <<",\"A\":"<<uint64_t(r.a.var)<<",\"B\":"<<uint64_t(r.b.var)
       <<",\"X\":"<<uint64_t(r.x.var)<<",\"Y\":"<<uint64_t(r.y.var);
    for(const char* n:{"R","N","M"}){
        out<<",\""<<n<<"\":[";
        for(int i=0;i<8;++i){if(i)out<<',';out<<(n[0]=='R'?r.r[i].var:n[0]=='N'?r.n[i].var:r.m[i].var);}
        out<<']';
    }
    out<<",\"stack\":[";
    for(int i=0;i<16;++i){if(i)out<<',';out<<uint64_t(r.ss[i].var);}
    out<<"]}\n";
}
int main(int argc,char** argv)try {
    static_assert(!g_useJIT,"Interpreter configuration required");
    if(argc!=3)throw std::runtime_error("Usage: ct_stock_load ORIGINAL_PAYLOAD FRESH_OUTPUT_DIR");
    const fs::path root=fs::path(__FILE__).parent_path().parent_path().parent_path();
    const auto allowed=fs::canonical(root/"builds/phase19b");
    const auto dest=fs::weakly_canonical(fs::absolute(argv[2]));
    auto rel=dest.lexically_relative(allowed);
    if(rel.empty()||rel=="."||*rel.begin()==".."||fs::exists(dest))
        throw std::runtime_error("Fresh output directory inside builds/phase19b required");
    const auto original=read(argv[1]); // const host bytes, separate from mutable P state
    constexpr auto expected="b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855";
    if(original.size()!=32538||sha(original)!=expected)
        throw std::runtime_error("Stock identity mismatch: ABORT before load");
    std::vector<TWord> words;
    for(size_t i=0;i<original.size();i+=3)
        words.push_back((TWord(original[i])<<16)|(TWord(original[i+1])<<8)|original[i+2]);
    if(words.size()!=0x2a5e)throw std::runtime_error("Word count mismatch");
    fs::create_directories(dest);
    auto tx=output(dest/"load-transactions.jsonl");
    // Host allocation is not a silicon capacity claim. Unknowns cannot be read.
    DefaultMemoryValidator validator; Memory memory(validator,0x6000);
    memory.setExternalMemory(0x1000000,true);
    std::vector<TWord> p(0x4000); std::vector<bool> known(0x4000,false);
    size_t stores=0;
    memory.replayWrite=[&](auto area,auto addr,auto value){
        if(area!=MemArea_P||addr>=words.size())throw std::runtime_error("Load store outside original image");
        tx<<"{\"actor\":\"LOADER\",\"space\":\"P\",\"address\":"<<addr
          <<",\"old\":null,\"value\":"<<(value&0xffffff)<<",\"seq\":"<<stores++<<"}\n";
        p[addr]=value&0xffffff;known[addr]=true;
    };
    memory.replayRead=[&](auto area,auto addr)->TWord{
        if(area!=MemArea_P||addr>=p.size()||!known[addr])
            throw std::runtime_error("Uninitialized/unmapped read denied");
        return p[addr];
    };
    for(TWord i=0;i<words.size();++i)if(!memory.set(MemArea_P,i,words[i]))throw std::runtime_error("P load failed");
    std::vector<unsigned char> copy;
    for(TWord i=0;i<words.size();++i){
        auto v=memory.get(MemArea_P,i);
        if(v!=words[i])throw std::runtime_error("P readback mismatch");
        copy.push_back(v>>16);copy.push_back(v>>8);copy.push_back(v);
    }
    if(copy!=original||sha(copy)!=expected)throw std::runtime_error("P copy mismatch");
    auto image=output(dest/"P.loaded24.bin");image.write(reinterpret_cast<const char*>(copy.data()),copy.size());
    // Disassembly has explicit formatting arguments, NOT an initialized CPU.
    Opcodes ops; Disassembler dis(ops); auto listing=output(dest/"loaded-vectors-startup.asm");
    for(auto range:{std::pair<TWord,TWord>{0,1},{0x3e,0x40},{0x44,0x46},{0x100,0x113}}){
        for(auto pc=range.first;pc<range.second;){
            Disassembler::Line l;
            const auto len=dis.disassemble(l,memory.get(MemArea_P,pc),memory.get(MemArea_P,pc+1),0,0,pc);
            if(!len)throw std::runtime_error("Undecodable audited instruction");
            listing<<"P:"<<std::uppercase<<std::hex<<std::setfill('0')<<std::setw(6)<<pc
                   <<"  "<<std::setw(6)<<l.opA;
            if(len==2)listing<<' '<<std::setw(6)<<l.opB;
            else listing<<"       ";
            listing<<"  "<<Disassembler::formatLine(l)<<'\n';pc+=len;
        }
    }
    int guards=0;
    for(auto a:{MemArea_X,MemArea_Y,MemArea_P})try{memory.get(a,a==MemArea_P?0x2a5e:0);}
        catch(const std::runtime_error&){++guards;}
    if(guards!=3)throw std::runtime_error("Unknown-state guard failed");
    if(read(argv[1])!=original)throw std::runtime_error("Source changed during load");
    auto report=output(dest/"native-load-report.json");
    report<<"{\"status\":\"MATCH\",\"words\":"<<stores
          <<",\"source_SHA256\":\""<<sha(original)<<"\",\"loaded_SHA256\":\""<<sha(copy)
          <<"\",\"stock_instructions_executed\":0,\"unknown_read_guards_passed\":"<<guards
          <<",\"source_unchanged\":true,\"DSP_CPU_constructed_for_stock\":false}\n";
    resetProbe(dest/"emulator-reset-probe.json");
    return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 42;}
