// Offline synthetic fixtures only. No firmware loader, devices, MIDI, sockets or audio API.
#include "dsp56kEmu/dsp.h"
#include "dsp56kEmu/assembler.h"
#include <fstream>
#include <iostream>
#include <sstream>
#include <map>
#include <vector>
#include <filesystem>
#include <cstdlib>
using namespace dsp56k;

struct Bus {
    std::ofstream out;
    std::vector<TWord> p,x,y,shared;
    std::map<TWord,TWord> ports;
    std::map<TWord,std::string> assembly;
    DSP* cpu=nullptr;
    uint64_t seq=0,ordinal=0;
    TWord pc=0,opcode=0;
    std::string actor="INITIALIZATION",kind="INITIALIZATION";
    struct Watch {EMemArea space;TWord lo,hi;};
    std::vector<Watch> watches;
    Bus(const char* path):out(path),p(0x800),x(0x800),y(0x800),shared(32) {}
    char space(EMemArea a) {return "PXY"[a];}
    void fault(EMemArea a,TWord addr,const char* why) {
        out<<"{\"type\":\"FAULT\",\"seq\":"<<seq++<<",\"instruction_counter\":"<<ordinal
           <<",\"PC\":"<<pc<<",\"space\":\""<<space(a)<<"\",\"address\":"<<addr
           <<",\"reason\":\""<<why<<"\"}\n";out.flush();std::exit(42);
    }
    TWord& ref(EMemArea a,TWord addr,const char* access="UNMAPPED") {
        if(addr>=0x30000 && addr<0x30020 && a!=MemArea_P) return shared[addr-0x30000];
        auto& v=a==MemArea_P?p:(a==MemArea_X?x:y);
        if(addr>=v.size()) fault(a,addr,access);
        return v[addr];
    }
    void event(const char* type,EMemArea a,TWord addr,TWord old,TWord val) {
        std::string k=kind;int rn=-1;
        if(actor=="CPU") {
            k="UNKNOWN";
            auto it=assembly.find(pc);
            if(it!=assembly.end()) {
                const auto& s=it->second;
                auto pos=s.find("(r");
                if(pos!=std::string::npos && pos+2<s.size()) rn=s[pos+2]-'0';
                k=pos==std::string::npos?"CPU_DIRECT":"CPU_AGU";
                if(s.find("x:")!=std::string::npos&&s.find("y:")!=std::string::npos){k="CPU_PARALLEL";rn=-1;}
                if(s.find("REP_LOOP")!=std::string::npos)k="REP_LOOP";
                if(s.find("DO_LOOP")!=std::string::npos)k="DO_LOOP";
            }
            if(addr>=0xffe000)k="PERIPHERAL";
        }
        out<<"{\"type\":\""<<type<<"\",\"seq\":"<<seq++<<",\"instruction_counter\":"<<ordinal
           <<",\"PC\":"<<(actor=="CPU"?std::to_string(pc):"null")<<",\"actor\":\""<<actor
           <<"\",\"memory_space\":\""<<space(a)<<"\",\"effective_address\":"<<addr
           <<",\"backing\":\""<<(addr>=0xffe000?"PERIPHERAL":addr>=0x30000&&addr<0x30020?"SHARED":std::string(1,space(a)))
           <<"\",\"old_value\":"<<old<<",\"new_value\":"<<val<<",\"instruction_word\":"
           <<(actor=="CPU"?std::to_string(opcode):"null")<<",\"address_register\":"
           <<(rn>=0&&rn<8?std::to_string(rn):"null")<<",\"modifier\":";
        if(cpu && rn>=0&&rn<8)out<<cpu->readRegs().m[rn].var;else out<<"null";
        out<<",\"write_kind\":\""<<k<<"\"}\n";
    }
    TWord read(EMemArea a,TWord addr) {
        auto v=ref(a,addr,"UNMAPPED_READ");
        for(auto w:watches)if(w.space==a&&addr>=w.lo&&addr<w.hi){event("READ",a,addr,v,v);break;}
        return v;
    }
    void write(EMemArea a,TWord addr,TWord val){auto& dst=ref(a,addr,"UNMAPPED_WRITE");event("WRITE",a,addr,dst,val&0xffffff);dst=val&0xffffff;}
    void port(TWord addr,bool wr,TWord val) {
        // Intentionally modeled fixture control ports only; no general permissive bank.
        if(addr!=0xffffff && addr!=0xfffffe && addr!=0xffff90)
            fault(MemArea_X,addr,"UNSUPPORTED_PERIPHERAL");
        if(wr){event("WRITE",MemArea_X,addr,ports[addr],val&0xffffff);ports[addr]=val&0xffffff;}
    }
    void before(TWord at,TWord op){actor="CPU";pc=at;opcode=op;++ordinal;
        if(ordinal>10000)fault(MemArea_P,pc,"INSTRUCTION_BUDGET");
        out<<"{\"type\":\"EXEC\",\"seq\":"<<seq++<<",\"instruction_counter\":"<<ordinal
           <<",\"PC\":"<<pc<<",\"opcode\":"<<opcode<<"}\n";}
    void snapshot(const char* label) {
        const auto& r=cpu->readRegs();
        out<<"{\"type\":\"SNAPSHOT\",\"label\":\""<<label<<"\",\"instruction_counter\":"<<ordinal
           <<",\"PC\":"<<r.pc.var<<",\"SR\":"<<r.sr.var<<",\"OMR\":"<<r.omr.var<<",\"SP\":"<<r.sp.var
           <<",\"SC\":"<<unsigned(r.sc.var)<<",\"LA\":"<<r.la.var<<",\"LC\":"<<r.lc.var
           <<",\"X_raw\":"<<uint64_t(r.x.var)<<",\"Y_raw\":"<<uint64_t(r.y.var)
           <<",\"VBA\":"<<r.vba.var<<",\"SZ\":"<<r.sz.var<<",\"EP\":"<<r.ep.var
           <<",\"A_raw\":"<<uint64_t(r.a.var)<<",\"B_raw\":"<<uint64_t(r.b.var);
        for(const char* n:{"R","N","M"}){
            out<<",\""<<n<<"\":[";for(int i=0;i<8;++i){if(i)out<<',';out<<(n[0]=='R'?r.r[i].var:n[0]=='N'?r.n[i].var:r.m[i].var);}out<<']';
        }
        out<<",\"stack\":[";for(int i=0;i<16;++i){if(i)out<<',';out<<uint64_t(r.ss[i].var);}out<<"]}\n";
    }
};
struct StrictY:IPeripherals {
    Bus& bus;StrictY(Bus& b):IPeripherals(PeripheralType::PeripheralsNop),bus(b){}
    TWord read(TWord a,Instruction)override{bus.fault(MemArea_Y,a,"UNSUPPORTED_PERIPHERAL");return 0;}
    const TWord* readAsPtr(TWord a,Instruction)override{bus.fault(MemArea_Y,a,"UNSUPPORTED_POINTER");return nullptr;}
    void write(TWord a,TWord)override{bus.fault(MemArea_Y,a,"UNSUPPORTED_PERIPHERAL");}
    void reset()override{} void setSymbols(Disassembler&)const override{} void terminate()override{}
};
int main(int argc,char** argv) {
    static_assert(!g_useJIT,"JIT must be disabled");
    if(argc<4){std::cerr<<"fixture-name program.asm fresh-trace.jsonl [X:lo:hi watches]\n";return 2;}
    if(std::filesystem::exists(argv[3]))return 3;
    Bus bus(argv[3]);
    if(!bus.out)return 2;
    for(int i=4;i<argc;++i){std::string w=argv[i];
        if(w.rfind("--sizes=",0)==0){auto sizes=w.substr(8);auto c=sizes.find(',');auto d=sizes.find(',',c+1);
            bus.p.resize(std::stoul(sizes.substr(0,c),nullptr,16));bus.x.resize(std::stoul(sizes.substr(c+1,d-c-1),nullptr,16));bus.y.resize(std::stoul(sizes.substr(d+1),nullptr,16));continue;}
        auto colon=w.find(':');auto end=w.find(':',colon+1);
        if(colon==std::string::npos||end==std::string::npos)return 2;
        bus.watches.push_back({w[0]=='X'?MemArea_X:w[0]=='Y'?MemArea_Y:MemArea_P,
            TWord(std::stoul(w.substr(colon+1,end-colon-1),nullptr,16)),TWord(std::stoul(w.substr(end+1),nullptr,16))});}
    DefaultMemoryValidator validator;Memory mem(validator,TWord(std::max(bus.p.size(),std::max(bus.x.size(),bus.y.size()))));
    mem.setExternalMemory(0x1000000,true); // disable upstream generic bridge; only the bus declares aliases
    mem.replayRead=[&](auto a,auto at){return bus.read(a,at);};
    mem.replayWrite=[&](auto a,auto at,auto v){bus.write(a,at,v);};
    Peripherals56362 px;StrictY py(bus);px.replayPeripheral=[&](auto a,bool w,auto v){bus.port(a,w,v);};
    DSP dsp(mem,&px,&py);bus.cpu=&dsp;
    dsp.setReplayBefore([&](auto pc,auto op){bus.before(pc,op);});
    const std::string name=argv[1];
    dsp.writeReg(Reg_R0,TReg24(0x40));dsp.writeReg(Reg_R4,TReg24(0x50));
    dsp.writeReg(Reg_N0,TReg24(2));dsp.writeReg(Reg_X0,TReg24(7));dsp.writeReg(Reg_Y0,TReg24(9));
    dsp.writeReg(Reg_M0,TReg24(0xffffff));
    if(name=="same")dsp.writeReg(Reg_X0,TReg24(0));
    if(name=="modulo"||name=="modulo_dec"){dsp.writeReg(Reg_M0,TReg24(3));dsp.writeReg(Reg_R0,TReg24(name=="modulo"?0x43:0x40));}
    if(name=="legacy")dsp.writeReg(Reg_M0,TReg24(0xffff));
    Assembler assembler;std::ifstream input(argv[2]);if(!input)return 2;
    TWord cursor=0x400,end=0x400;std::string line;
    while(std::getline(input,line)) {
        auto semi=line.find(';');std::string comment=semi==std::string::npos?"":line.substr(semi);
        if(semi!=std::string::npos)line.resize(semi);
        if(line.find_first_not_of(" \r\t")==std::string::npos)continue;
        if(line.rfind(".org ",0)==0){cursor=std::stoul(line.substr(5),nullptr,16);continue;}
        if(line.rfind(".words ",0)==0){bus.assembly[cursor]=comment;std::istringstream raw(line.substr(7));std::string word;
            while(raw>>word)mem.set(MemArea_P,cursor++,std::stoul(word,nullptr,16));
            if(cursor>=0x400&&cursor<0x600)end=cursor;continue;}
        auto op=assembler.assemble(line.c_str());
        if(!op.success()){std::cerr<<"Assembly failure "<<line<<" error "<<int(op.error)<<'\n';return 4;}
        bus.assembly[cursor]=line+comment;
        for(unsigned i=0;i<op.wordCount;++i)mem.set(MemArea_P,cursor++,op.word[i]);
        if(cursor>=0x400&&cursor<0x600)end=cursor;
    }
    dsp.setPC(0x400);bus.snapshot("initial");
    if(name.rfind("dma_",0)==0){
        for(unsigned i=0;i<4;++i)bus.write(MemArea_X,0x60+i,i+1);
        bus.actor="DMA";bus.kind=name=="dma_fill"?"DMA_FILL":"DMA_COPY";
        auto& ch=px.getDMA().replayChannel(0);
        if(name=="dma_peripheral_fill"){
            bus.actor="INITIALIZATION";px.write(0xfffffe,5);bus.actor="DMA";bus.kind="DMA_FILL";
            ch.replayFill(MemArea_Y,0x70,MemArea_X,0xfffffe,4);
        }
        else if(name=="dma_p_fill"){bus.kind="DMA_FILL";ch.replayFill(MemArea_P,0x70,MemArea_X,0x60,4);}
        else if(name=="dma_peripheral_copy")ch.replayCopy(MemArea_X,0xfffffe,MemArea_X,0x60,1);
        else if(name=="dma_controller"){
            ch.setDSR(0x60);ch.setDDR(0x70);ch.setDCO(3);
            ch.setDCR((1u<<23)|(3u<<19)|(5u<<7)|(5u<<4)|(1u<<2)); // sourceX=0,destinationY=1
        }
        else if(name=="dma_fill")ch.replayFill(MemArea_Y,0x70,MemArea_X,0x60,4);
        else if(name=="dma_fixed")ch.replayFixed(MemArea_Y,0x70,MemArea_X,0x60,4);
        else if(name=="dma_p")ch.replayCopy(MemArea_P,0x70,MemArea_X,0x60,4);
        else if(name=="dma_shared")ch.replayCopy(MemArea_Y,0x30000,MemArea_X,0x60,4);
        else ch.replayCopy(MemArea_Y,0x70,MemArea_X,0x60,4);
    }else if(name=="actors"){
        for(auto actor:{"HOST","WORKER","PERIPHERAL"}){bus.actor=actor;bus.kind=actor;bus.write(MemArea_X,0x30000,5);}
        bus.actor="HOST";if(bus.read(MemArea_Y,0x30000)!=5)return 5;
    }else{
        for(unsigned budget=0;dsp.getPC().var!=end && budget<300;++budget){
            if(name=="interrupt"&&budget==1){dsp.writeReg(Reg_SR,TReg24(0));dsp.injectInterrupt(0x20);}
            dsp.execInterpreter();
        }
        if(dsp.getPC().var!=end){std::cerr<<"Instruction budget/end mismatch PC="<<dsp.getPC().var<<" end="<<end<<'\n';return 6;}
        if(name=="direct"&&(bus.read(MemArea_X,64)!=7||bus.read(MemArea_Y,64)!=9||bus.read(MemArea_P,64)!=0))return 7;
    }
    bus.snapshot("final");bus.out.flush();return 0;
}
