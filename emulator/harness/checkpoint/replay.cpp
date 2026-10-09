// ORIGINAL P bytes only. Address-only symbolic projection over sealed19A core.
// Unknown data/control backing encodings are NOT concrete checkpoint values.
// Whitelist prohibits their use for branches, addresses, counts or modifiers.
#include "dsp56kEmu/dsp.h"
#include <windows.h>
#include <bcrypt.h>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <map>
#include <stdexcept>
using namespace dsp56k;
namespace fs=std::filesystem;
std::string hash(const std::vector<unsigned char>& b) {
    BCRYPT_ALG_HANDLE a=nullptr;
    if(BCryptOpenAlgorithmProvider(&a,BCRYPT_SHA256_ALGORITHM,nullptr,0)<0)throw std::runtime_error("SHA provider");
    unsigned char d[32];auto s=BCryptHash(a,nullptr,0,const_cast<PUCHAR>(b.data()),ULONG(b.size()),d,32);
    BCryptCloseAlgorithmProvider(a,0);if(s<0)throw std::runtime_error("SHA failed");
    std::ostringstream o;o<<std::hex<<std::setfill('0');for(auto v:d)o<<std::setw(2)<<unsigned(v);return o.str();
}
struct Case { int id,kind,family,j,i; TWord modifier,encoding; };
TWord cursor(const Case& c) {return c.family==0?(c.j%2?0x2cec:0x2ccc):(c.j%2?0x2c24:0x2c02);}
struct Bus {
    const std::vector<TWord>& p;std::ofstream& out;Case c;DSP* cpu=nullptr;
    TWord pc=0,op=0;unsigned count=0;bool running=false;uint64_t& seq;
    std::map<TWord,TWord> x,y;TWord dataFill=0;
    Bus(const std::vector<TWord>& pp,std::ofstream& o,Case cc,uint64_t& s):p(pp),out(o),c(cc),seq(s){
        dataFill=c.encoding?0x5a5a5a:0;
        if(c.kind==1)y[(c.family?0x1a10:0x1820)+c.j]=cursor(c);
        if(c.kind==2){for(TWord a=0x35f;a<0x364;++a)x[a]=0;y[0]=0;}
        if(c.kind==3)x[0]=0;
    }
    void event(const char* type,EMemArea area,TWord at,bool known,TWord value,int reg=-1){
        out<<"{\"type\":\""<<type<<"\",\"seq\":"<<seq++<<",\"case\":"<<c.id<<",\"PC\":"<<pc
           <<",\"opcode\":"<<op<<",\"instruction_counter\":"<<count<<",\"memory_space\":\""<<"PXY"[area]
           <<"\",\"effective_address\":"<<at<<",\"value\":";
        if(known)out<<value;else out<<"null";
        out<<",\"value_status\":\""<<(known?"CONCRETE_PROVENANCE":"SYMBOLIC_DATA")<<"\",\"address_register\":";
        if(reg>=0)out<<reg;else out<<"null";
        out<<",\"modifier\":";if(reg>=0&&cpu)out<<cpu->readRegs().m[reg].var;else out<<"null";
        out<<",\"call_path\":\"checkpoint/body-slice; callers not executed\"}\n";
    }
    TWord read(EMemArea area,TWord at){
        if(area==MemArea_P){if(at>=p.size())throw std::runtime_error("Unloaded P read");return p[at];}
        int reg=-1;bool known=false;TWord val=dataFill;
        auto& mem=area==MemArea_X?x:y;auto it=mem.find(at);
        if(it!=mem.end()){known=true;val=it->second;}
        if(c.kind==0){
            if(area!=MemArea_X||!((pc==0x1f92&&at==0x2c8a+unsigned(c.i))||(pc==0x1f93&&at==cursor(c)+unsigned(c.i))))
                throw std::runtime_error("Unknown read outside audited data-only operands");
            reg=pc==0x1f92?3:7;
        }else if(c.kind==1){if(area!=MemArea_Y||!known)throw std::runtime_error("Unknown cursor EA/value");reg=6;}
        else if(c.kind==2){if(!known)throw std::runtime_error("Unknown record address/value");reg=area==MemArea_X?0:5;}
        else throw std::runtime_error("Unexpected calibration read");
        event("READ",area,at,known,val,reg);return val;
    }
    void write(EMemArea area,TWord at,TWord){
        if(area==MemArea_P)throw std::runtime_error("P modification forbidden");
        if(c.kind==0&&area==MemArea_X&&pc==0x1f97&&at==cursor(c)+unsigned(c.i)){event("WRITE",area,at,false,0,7);return;}
        if(c.kind==3&&area==MemArea_X&&pc==0x204b&&at==0){event("WRITE",area,at,false,0,4);return;}
        throw std::runtime_error("Write outside audited symbolic-data store");
    }
    void before(TWord at,TWord word){
        pc=at;op=word;++count;
        static const std::map<TWord,TWord> body={{0x1f92,0x44db60},{0x1f93,0x57e700},{0x1f94,0x21c600},{0x1f95,0x2000da},{0x1f96,0},{0x1f97,0x575f00}};
        bool ok=c.kind==0&&body.count(at)&&body.at(at)==word;
        ok|=c.kind==1&&at==0x1f89&&word==0x0b76d7;
        ok|=c.kind==2&&at>=0x203a&&at<=0x2040;
        ok|=c.kind==3&&at==0x204b&&word==0x576400;
        if(!ok||count>16)throw std::runtime_error("Unsupported instruction/unknown control dependency");
        if(c.kind==0){const auto& r=cpu->readRegs();
            if(r.r[7].var!=cursor(c)+unsigned(c.i)||r.r[3].var!=0x2c8a+unsigned(c.i)+(at>0x1f92))
                throw std::runtime_error("Address-state divergence");}
        out<<"{\"type\":\"EXEC\",\"seq\":"<<seq++<<",\"case\":"<<c.id<<",\"PC\":"<<at<<",\"opcode\":"<<word
           <<",\"instruction_counter\":"<<count<<",\"execution\":\"ORIGINAL_OPCODE_SYMBOLIC_DATA_PROJECTION\"}\n";
        if(at==0x203a)event("ENTRY_X35F",MemArea_X,0x35f,true,x.at(0x35f));
    }
};
struct Deny:IPeripherals {
    bool constructing=true;
    Deny():IPeripherals(PeripheralType::PeripheralsNop){}
    TWord read(TWord,Instruction)override{throw std::runtime_error("Peripheral read forbidden");}
    const TWord* readAsPtr(TWord,Instruction)override{throw std::runtime_error("Raw peripheral pointer forbidden");}
    void write(TWord a,TWord v)override{if(!constructing||(a!=0xfffffe&&a!=0xffffff)||v!=0)throw std::runtime_error("Peripheral write forbidden");}
    void reset()override{}void setSymbols(Disassembler&)const override{}void terminate()override{}
};
int main(int argc,char** argv)try{
    static_assert(!g_useJIT,"Interpreter required");
    if(argc!=4)throw std::runtime_error("original-payload cases.tsv fresh-trace.jsonl");
    fs::path dest=fs::absolute(argv[3]);
    auto root=fs::path(__FILE__).parent_path().parent_path().parent_path().parent_path();
    auto allowed=fs::weakly_canonical(root/"builds/phase19c-checkpoint");
    auto rel=fs::weakly_canonical(dest).lexically_relative(allowed);
    if(rel.empty()||*rel.begin()==".."||fs::exists(dest))throw std::runtime_error("Fresh checkpoint output only");
    std::ifstream in(argv[1],std::ios::binary);if(!in)throw std::runtime_error("Input unavailable");
    const std::vector<unsigned char> bytes{std::istreambuf_iterator<char>(in),{}};
    if(bytes.size()!=32538||hash(bytes)!="b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855")throw std::runtime_error("Original identity mismatch");
    std::vector<TWord> p;for(size_t i=0;i<bytes.size();i+=3)p.push_back((TWord(bytes[i])<<16)|(TWord(bytes[i+1])<<8)|bytes[i+2]);
    std::ifstream cases(argv[2]);if(!cases)throw std::runtime_error("Cases missing");
    std::ofstream out(dest);uint64_t seq=0;unsigned total=0,n=0;Case c;
    while(cases>>c.id>>c.kind>>c.family>>c.j>>c.i>>c.modifier>>c.encoding){
        if(c.kind<0||c.kind>3||c.family<0||c.family>1||c.j<0||c.j>15||c.i<0||c.i>31||
           (c.modifier!=0xffff&&c.modifier!=0x3ff)||c.encoding>1)throw std::runtime_error("Nondefensible bounded case");
        Bus bus(p,out,c,seq);DefaultMemoryValidator validator;Memory mem(validator,0x6000);
        mem.setExternalMemory(0x1000000,true);
        mem.replayRead=[&](auto a,auto at){return bus.read(a,at);};
        mem.replayWrite=[&](auto a,auto at,auto v){bus.write(a,at,v);};
        Deny px,py;DSP dsp(mem,&px,&py);bus.cpu=&dsp;px.constructing=py.constructing=false;
        // Partial SR/OMR are externally tagged. These are backing encodings,
        // not guessed checkpoint words. No eligible event is injected in this isolated test.
        dsp.writeReg(Reg_SR,TReg24(c.encoding?0x340c00:0));
        dsp.writeReg(Reg_OMR,TReg24(0x400080)); // partial shim-derived memory-mode relation; remaining bits backing only
        // SA/RM/SM/scaling affect unknown DATA only here; reserved device SC stays0.
        dsp.writeReg(Reg_A,TReg56(c.encoding?0x123456789abc:0));
        dsp.writeReg(Reg_B,TReg56(c.encoding?0x654321000000:0));
        dsp.writeReg(Reg_X1,TReg24(bus.dataFill));
        TWord entry=0,stop=0;
        if(c.kind==0){entry=0x1f92;stop=0x1f98;
            dsp.writeReg(Reg_R3,TReg24(0x2c8a+c.i));dsp.writeReg(Reg_M3,TReg24(0xffff));
            dsp.writeReg(Reg_R7,TReg24(cursor(c)+c.i));dsp.writeReg(Reg_M7,TReg24(c.modifier));}
        else if(c.kind==1){entry=0x1f89;stop=0x1f8b;
            dsp.writeReg(Reg_R6,TReg24((c.family?0x19f0:0x1800)+c.j));dsp.writeReg(Reg_M6,TReg24(0xffff));}
        else if(c.kind==2){entry=0x203a;stop=0x204c;
            dsp.writeReg(Reg_R0,TReg24(0x35f));dsp.writeReg(Reg_M0,TReg24(0xffff));
            dsp.writeReg(Reg_N5,TReg24(0));dsp.writeReg(Reg_M5,TReg24(0xffff));}
        else {entry=0x204b;stop=0x204c;dsp.writeReg(Reg_R4,TReg24(0));}
        dsp.setPC(entry);dsp.setReplayBefore([&](auto at,auto op){bus.before(at,op);});
        while(dsp.getPC().var!=stop){dsp.execInterpreter();if(bus.count>16)throw std::runtime_error("Budget");}
        if(c.kind==1&&dsp.readRegs().r[7].var!=cursor(c))throw std::runtime_error("Cursor load mismatch");
        if(c.kind==0&&dsp.readRegs().r[7].var!=cursor(c)+c.i+1)throw std::runtime_error("Cursor advance mismatch");
        out<<"{\"type\":\"END\",\"case\":"<<c.id<<",\"count\":"<<bus.count<<",\"PC\":"<<stop
           <<",\"scope\":\"bounded slice; no inherited-loop edge, boot or scheduler execution\"}\n";
        total+=bus.count;++n;
    }
    if(!cases.eof())throw std::runtime_error("Malformed case file");
    out.flush();std::cout<<n<<" cases; "<<total<<" original opcodes in bounded slices\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 2;}
