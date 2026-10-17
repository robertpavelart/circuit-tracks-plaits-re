// Offline fixture only. Links the immutable Phase19A interpreter.
#include "dsp56kEmu/dsp.h"
#include "dsp56kEmu/assembler.h"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <map>
#include <set>
#include <vector>
#include <regex>
#include <stdexcept>
#include <algorithm>
#include <crtdbg.h>
using namespace dsp56k; namespace fs=std::filesystem;
TWord diagnosticPC=0;std::string diagnosticAssembly;
int reportHook(int,char*message,int*){std::fprintf(stderr,"Core assertion PC=%x %s: %s\n",diagnosticPC,diagnosticAssembly.c_str(),message);std::fflush(stderr);std::_Exit(9);}
constexpr TWord STATE=0x3e00,WS=0x3e20,CTRL=0x3e50,SPILL=0x3e58,OUTY=0x3e00,RING=0x1000;
int32_t s24(TWord x){return int32_t(x<<8)>>8;}
struct Deny:IPeripherals{bool constructing=true;Deny():IPeripherals(PeripheralType::PeripheralsNop){}
 TWord read(TWord,Instruction)override{throw std::runtime_error("Peripheral read rejected");}
 const TWord*readAsPtr(TWord,Instruction)override{throw std::runtime_error("Peripheral pointer rejected");}
 void write(TWord a,TWord v)override{if(!constructing||(a!=0xfffffe&&a!=0xffffff)||v)throw std::runtime_error("Peripheral write rejected");}
 void reset()override{}void setSymbols(Disassembler&)const override{}void terminate()override{}};
std::vector<TWord> load(const fs::path&p){std::ifstream f(p,std::ios::binary);std::vector<TWord>w;int a;while((a=f.get())!=EOF){int b=f.get(),c=f.get();if(b<0||c<0)throw std::runtime_error("Truncated be24");w.push_back((a<<16)|(b<<8)|c);}return w;}
std::string hex(TWord v){std::ostringstream s;s<<'$'<<std::hex<<std::setw(6)<<std::setfill('0')<<v;return s.str();}
AssembleResult assemble(Assembler&a,const std::string&s){std::smatch m;
 if(std::regex_match(s,m,std::regex("(jmp|jsr|jlt|jge|jle|jne|jeq) \\$([0-9a-f]{6})"))&&std::stoul(m[2],nullptr,16)>0xfff){
  auto q=a.assemble((m[1].str()+" $001").c_str());if(!q.success())throw std::runtime_error("branch encoding");
  AssembleResult r;r.wordCount=2;r.word[1]=std::stoul(m[2],nullptr,16);r.word[0]=m[1]=="jmp"?0x0af080:m[1]=="jsr"?0x0bf080:0x0af0a0|((q.word[0]>>12)&15);return r;}
 return a.assemble(s.c_str());}
struct Program{std::map<TWord,std::string>ins;std::map<std::string,TWord>labels;std::vector<TWord>w;TWord origin,done;
 Program(const std::vector<std::string>&lines,TWord at):origin(at){Assembler a;std::regex sym("@([A-Za-z_][A-Za-z_0-9]*)");
  for(int pass=0;pass<14;++pass){auto old=labels;TWord pc=at;w.clear();ins.clear();
   for(auto s:lines){if(s.empty())continue;if(s.back()==':'){labels[s.substr(0,s.size()-1)]=pc;continue;}
    std::smatch m;while(std::regex_search(s,m,sym))s.replace(m.position(),m.length(),hex(labels.count(m[1])?labels.at(m[1]):at));
    auto op=assemble(a,s);if(!op.success())throw std::runtime_error("Assembler "+std::to_string(int(op.error))+": "+s);
    ins[pc]=s;for(unsigned i=0;i<op.wordCount;++i){w.push_back(op.word[i]);++pc;}}
   done=pc;if(pass&&old==labels)break;if(pass==13)throw std::runtime_error("Relaxation failed");}}
};
std::vector<std::string> lines(const fs::path&p){std::ifstream f(p);if(!f)throw std::runtime_error("Source missing");std::vector<std::string>v;std::string s;while(std::getline(f,s)){if(!s.empty()&&s.back()=='\r')s.pop_back();v.push_back(s);}return v;}
const std::vector<std::string> names={"sr","a0","a1","a2","b0","b1","b2","x0","x1","y0","y1","r0","r1","r2","r3","r4","r5","r6","r7","n0","n1","n2","n3","n4","n5","n6","n7","m0","m1","m2","m3","m4","m5","m6","m7","la","lc"};
const std::vector<EReg> regs={Reg_SR,Reg_A0,Reg_A1,Reg_A2,Reg_B0,Reg_B1,Reg_B2,Reg_X0,Reg_X1,Reg_Y0,Reg_Y1,Reg_R0,Reg_R1,Reg_R2,Reg_R3,Reg_R4,Reg_R5,Reg_R6,Reg_R7,Reg_N0,Reg_N1,Reg_N2,Reg_N3,Reg_N4,Reg_N5,Reg_N6,Reg_N7,Reg_M0,Reg_M1,Reg_M2,Reg_M3,Reg_M4,Reg_M5,Reg_M6,Reg_M7,Reg_LA,Reg_LC};
struct Machine{
 std::vector<TWord>p,x=std::vector<TWord>(0x40000),y=std::vector<TWord>(0x40000);Deny px,py;DefaultMemoryValidator validator;Memory mem;DSP cpu;
 std::map<TWord,std::string>dis;std::map<TWord,unsigned>sizes;std::ofstream trace,access;bool active=false;int block=-1,phase=0;uint64_t issued=0,writes=0,reads=0,violations=0;TWord pc=0;std::vector<TWord>pcs;
 Machine(const std::vector<TWord>&prog,const fs::path&out):p(prog),mem(validator,0x4000),cpu(mem,&px,&py){
  mem.setExternalMemory(0x1000000,true);px.constructing=py.constructing=false;
  mem.replayRead=[this](auto a,auto ad){if(a==MemArea_P){if(ad>=p.size())throw std::runtime_error("P read extent");return p[ad];}auto&v=a==MemArea_X?x:y;if(ad>=v.size())throw std::runtime_error("Data read extent");
   if(active){++reads; log(a,ad,v[ad],false);}return v[ad];};
  mem.replayWrite=[this](auto a,auto ad,auto v){if(a==MemArea_P)throw std::runtime_error("P mutation rejected");auto&d=a==MemArea_X?x:y;if(ad>=d.size())throw std::runtime_error("Data write extent");if(active){++writes;log(a,ad,v,true);}d[ad]=v&0xffffff;};
  cpu.setReplayBefore([this](auto at,auto op){pc=at;diagnosticPC=at;pcs.push_back(at);++issued;uint16_t v=uint16_t(at);trace.write(reinterpret_cast<char*>(&v),2);
   if(!dis.count(at)){std::string s;auto n=cpu.disassembler().disassemble(s,op,p.at(at+1),cpu.getCurrentInstructionSR(),cpu.readRegs().omr.var,at);dis[at]=s;sizes[at]=n;}
   diagnosticAssembly=dis[at];if(issued>200000000)throw std::runtime_error("Execution budget");});
  trace.open(out/"pc.u16",std::ios::binary);access.open(out/"access.csv");access<<"block,phase,pc,space,address,write,value\n";
  for(auto r:{Reg_M0,Reg_M1,Reg_M2,Reg_M3,Reg_M4,Reg_M5,Reg_M6,Reg_M7})cpu.writeReg(r,TReg24(0xffffff));
  cpu.writeReg(Reg_SR,TReg24(0x300));cpu.writeReg(Reg_OMR,TReg24(0));
 }
 void log(EMemArea a,TWord ad,TWord v,bool wr){
  // Only reference vpre/strip objects and explicitly owned fixture objects.
  bool allowed=a==MemArea_X? ((ad>=0x3400&&ad<0x3c00)||(ad>=STATE&&ad<STATE+7)||(ad>=WS&&ad<0x3e60)||ad==0x3703e||ad==0x3706e||ad==0x3a||ad==0x3bf1||(ad>=0x200&&ad<0x300)||(ad>=0x59&&ad<0x80)||(ad>=0x2e10&&ad<0x2e50)):
    (ad==0xffd||(ad>=RING&&ad<RING+64)||(ad>=0x1100&&ad<0x1180)||(ad>=OUTY&&ad<OUTY+32)||(ad>=0x800&&ad<0x840));
  if(!allowed){++violations;throw std::runtime_error("Ownership access "+std::to_string(a)+":"+hex(ad)+" pc "+hex(pc));}
  // Complete writes plus new-object reads. Aggregate other reference reads.
  if(wr||(a==MemArea_X&&ad>=STATE&&ad<0x3e60)||(a==MemArea_Y&&ad>=OUTY&&ad<OUTY+32))access<<block<<','<<phase<<','<<std::hex<<pc<<','<<(a==MemArea_X?'X':'Y')<<','<<ad<<','<<wr<<','<<v<<std::dec<<'\n';
 }
 void seed(){x[0x3a]=32;y[0xffd]=RING;for(int t=0;t<2;++t){int b=0x3b80+48*t;x[b+8]=127;x[b+11]=0;x[b+16]=127;x[b+18]=1;x[b+19]=t?67:60;x[b+20]=2;x[b+21]=100;x[b+22]=1;x[b+42]=0x7f0000;
   x[0x3900+48*t+3]=64;x[0x3900+48*t+2]=84;}
  for(auto a:{0x3dff,0x3e07,0x3e1f,0x3e60})x[a]=0x5a1234;
  for(auto a:{0x3dff,0x3e20})y[a]=0x6b2345;
  for(int i=0;i<7;++i)x[STATE+i]=0xa5a5a5;
 }
 std::vector<TWord>snapshot(){std::vector<TWord>v;for(auto r:regs){TReg24 a;cpu.readReg(r,a);v.push_back(a.var);}return v;}
 std::vector<TWord>caller(){std::vector<TWord>v;for(auto r:{Reg_X0,Reg_X1,Reg_Y0,Reg_Y1,Reg_R0,Reg_R1,Reg_R6,Reg_R7,Reg_N0,Reg_M0,Reg_R2,Reg_R3,Reg_R4,Reg_M2,Reg_M4,Reg_M1,Reg_M3,Reg_M5,Reg_M6,Reg_M7,Reg_N1,Reg_N2,Reg_N3,Reg_N4,Reg_N5,Reg_N6,Reg_N7,Reg_LA,Reg_LC,Reg_OMR,Reg_SP,Reg_SC}){TReg24 a;cpu.readReg(r,a);v.push_back(a.var);}return v;}
 void callerFixture(unsigned b){
  for(auto r:{Reg_X0,Reg_X1,Reg_Y0,Reg_Y1,Reg_R0,Reg_R1,Reg_R2,Reg_R3,Reg_R4,Reg_R6,Reg_R7,Reg_N0,Reg_N1,Reg_N2,Reg_N3,Reg_N4,Reg_N5,Reg_N6,Reg_N7,Reg_LA,Reg_LC})cpu.writeReg(r,TReg24((0x123457u*unsigned(r)+0xabcdu*b)&0xffffff));
  for(auto r:{Reg_M0,Reg_M1,Reg_M2,Reg_M3,Reg_M4,Reg_M5,Reg_M6,Reg_M7})cpu.writeReg(r,TReg24((b&1)?0x00ffff:0xffffff));
  cpu.writeReg(Reg_SR,TReg24(0x300));cpu.writeReg(Reg_OMR,TReg24(0));
 }
 void strip(){
  // Original stock P:$23E..$24E, four strip stems. Silent synth stems are
  // explicit fixture objects; constant L/R gains stay identical between runs.
  for(int j=0;j<256;++j)x[0x200+j]=0x100000;
  cpu.writeReg(Reg_R0,TReg24(0x200));cpu.writeReg(Reg_R1,TReg24(0x240));cpu.writeReg(Reg_R2,TReg24(0x280));cpu.writeReg(Reg_R3,TReg24(0x2c0));
  cpu.writeReg(Reg_R5,TReg24(RING));cpu.writeReg(Reg_R6,TReg24(0x1100));cpu.writeReg(Reg_R7,TReg24(0x1140));
  for(auto r:{Reg_M0,Reg_M1,Reg_M2,Reg_M3,Reg_M4,Reg_M5,Reg_M6,Reg_M7})cpu.writeReg(r,TReg24(0xffffff));
  phase=2;run(0x23e,0x24f);
 }
 void canaries(){for(auto a:{0x3dff,0x3e07,0x3e1f,0x3e60})if(x[a]!=0x5a1234)throw std::runtime_error("X canary");for(auto a:{0x3dff,0x3e20})if(y[a]!=0x6b2345)throw std::runtime_error("Y canary");}
 void run(TWord begin,TWord end,bool guarded=true){cpu.setPC(begin);active=guarded;uint64_t start=issued;while(cpu.getPC().var!=end){if(issued-start>80000)throw std::runtime_error("Call budget PC "+hex(cpu.getPC().var));cpu.execInterpreter();}active=false;}
};
int main(int argc,char**argv)try{
 _CrtSetReportHook(reportHook);
 std::set_terminate([](){try{if(auto e=std::current_exception())std::rethrow_exception(e);}catch(const std::exception&e){std::cerr<<"REJECTED: "<<e.what()<<'\n';}std::_Exit(9);});
 if(argc<3)throw std::runtime_error("fixture output [cases]");fs::path fixture=argv[1],out=argv[2];if(fs::exists(out))throw std::runtime_error("Fresh run output required");fs::create_directories(out);
 auto reference=load(fixture/"reference-core0.be24");reference.resize(0x4000);std::map<std::string,TWord>L;std::ifstream lf(fixture/"labels.txt");std::string k;TWord v;while(lf>>k>>std::hex>>v)L[k]=v;
 Machine inspect(reference,out);
 if(argc==3){for(TWord at: {0x23e,0x3999}){for(int i=0;i<(at==0x23e?80:12);){std::string s;auto n=inspect.cpu.disassembler().disassemble(s,reference[at+i],reference[at+i+1],0x300,0,at+i);std::cout<<std::hex<<at+i<<' '<<s<<'\n';i+=n?n:1;}}return 0;}
 Program render(lines(fixture/"variablesaw.asm"),0x400);
 std::vector<std::string>a;
 auto e=[&](std::string s){a.push_back(s);};auto restore=[&](){for(size_t i=1;i<names.size();++i)e("move x:>"+hex(WS+TWord(i))+","+names[i]);e("move x:>"+hex(WS)+",sr");};
 e("entry:");for(size_t i=0;i<names.size();++i)e("move "+names[i]+",x:>"+hex(WS+TWord(i)));
 e("move r6,a");e("cmp #>"+hex(0x3b80)+",a");e("jeq @selected");restore();e("displaced:");e("nop");e("nop");e("nop");e("nop");e("jmp "+hex(L.at("vc2_ngr")+4));
 e("selected:");e("move #>$000300,sr");e("move #>$ffffff,m0");e("move x:>"+hex(0x390b)+",a");e("lsr #$02,a");e("move a,x:>"+hex(CTRL));
 e("move x:>"+hex(0x3903)+",a");e("asl #$0f,a,a");e("move a,x:>"+hex(CTRL+1));
 e("move x:>"+hex(0x3902)+",a");e("asl #$0e,a,a");e("move a,x:>"+hex(CTRL+2));e("jsr "+hex(render.origin));
 e("render_return:");e("move #>"+hex(OUTY)+",r0");e("move x:>"+hex(WS+11)+",r1");e("move #>$000002,n1");e("move #>$ffffff,m1");e("nop");e("do #$20,@copy_end");
 e("move y:(r0)+,x0");e("copy_end:");e("move x0,y:(r1)+n1");restore();e("adapter_return:");e("jmp "+hex(L.at("vc2_nosc")));
 e("init:");std::vector<TWord>initial={0,0,0x200000,0,41943,0x200000,0};for(size_t i=0;i<initial.size();++i){e("move #>"+hex(initial[i])+",x0");e("move x0,x:>"+hex(STATE+TWord(i)));}e("rts");
 e("call:");e("jsr "+hex(L.at("vpre")));e("stop:");e("nop");e("call_init:");e("jsr @init");e("init_stop:");e("nop");
 Program adapter(a,0x800);if(render.done>=adapter.origin||adapter.done>=0xc00)throw std::runtime_error("Synthetic overlay extent");
 auto patched=reference;std::copy(render.w.begin(),render.w.end(),patched.begin()+render.origin);std::copy(adapter.w.begin(),adapter.w.end(),patched.begin()+adapter.origin);
 TWord hook=L.at("vc2_ngr"),disp=adapter.labels.at("displaced");std::copy(reference.begin()+hook,reference.begin()+hook+4,patched.begin()+disp);
 patched[hook]=0x0af080;patched[hook+1]=adapter.origin;
 auto control=reference;std::copy(adapter.w.begin(),adapter.w.end(),control.begin()+adapter.origin);
 {std::ofstream f(out/"adapter.asm");for(auto [pc,s]:adapter.ins)f<<std::hex<<pc<<' '<<s<<'\n';}
 {std::ofstream f(out/"renderer.asm");for(auto [pc,s]:render.ins)f<<std::hex<<pc<<' '<<s<<'\n';}
 {std::ofstream f(out/"layout.txt");f<<std::hex<<"renderer "<<render.origin<<' '<<render.done<<"\nadapter "<<adapter.origin<<' '<<adapter.done<<"\n";}
 fs::create_directory(out/"baseline");fs::create_directory(out/"replacement");Machine base(control,out/"baseline"),mod(patched,out/"replacement");base.seed();mod.seed();
 for(auto*m:{&base,&mod}){m->phase=0;m->run(adapter.labels.at("call_init"),adapter.labels.at("init_stop"));m->canaries();}
 std::ifstream cases(argv[3]);if(!cases)throw std::runtime_error("Cases missing");std::ofstream report(out/"blocks.csv"),states(out/"states.csv"),samples(out/"raw.i32",std::ios::binary),rings(out/"rings.i32",std::ios::binary),mixed(out/"mixed.i32",std::ios::binary);
 report<<"block,baseline_instructions,replacement_instructions,baseline_emulator_cycles,replacement_emulator_cycles,baseline_vpre_instructions,replacement_vpre_instructions,baseline_vpre_cycles,replacement_vpre_cycles,rendered,frequency_q22,pw_q22,shape_q21,canaries,adapter_registers,caller_registers,other_track,wrap_events,pw_events,reads,writes\n";
 states<<"block,phase,next,previous_pw,high,frequency,pw,shape\n";
 int block,n;unsigned addr,word;size_t count=0,renderCount=0,adapterChecks=0;unsigned wrapEvents=0,pwEvents=0;std::vector<TWord>expected;
 // The original vpre ABI preserves its declared set; adapter restores all 37 saved fields.
 std::vector<TWord>entry;
 auto oldBefore=std::function<void(TWord,TWord)>();
 mod.cpu.setReplayBefore([&](auto at,auto op){mod.pc=at;diagnosticPC=at;mod.pcs.push_back(at);++mod.issued;uint16_t vv=uint16_t(at);mod.trace.write(reinterpret_cast<char*>(&vv),2);
  if(!mod.dis.count(at)){std::string s;auto len=mod.cpu.disassembler().disassemble(s,op,mod.p.at(at+1),mod.cpu.getCurrentInstructionSR(),mod.cpu.readRegs().omr.var,at);mod.dis[at]=s;mod.sizes[at]=len;}
  diagnosticAssembly=mod.dis[at];TReg24 rv;mod.cpu.readReg(Reg_R6,rv);if(at==hook&&rv.var==0x3b80){entry=mod.snapshot();++renderCount;}
  if(at==render.labels.at("wrap_event"))++wrapEvents;if(at==render.labels.at("pw_event"))++pwEvents;
  if(at==adapter.labels.at("adapter_return")){if(mod.snapshot()!=entry)throw std::runtime_error("Adapter register preservation");++adapterChecks;}
 });
 while(cases>>block>>n){wrapEvents=pwEvents=0;for(auto*m:{&base,&mod}){m->block=block;m->pcs.clear();m->callerFixture(unsigned(block));for(int j=0;j<64;++j)m->y[RING+j]=(0x111*j+block)&0xffffff;}
  for(int j=0;j<n;++j){cases>>std::hex>>addr>>word>>std::dec;base.x[addr]=mod.x[addr]=word;}
  auto bi=base.cpu.getInstructionCounter(),mi=mod.cpu.getInstructionCounter(),bc=base.cpu.getCycles(),mc=mod.cpu.getCycles();size_t before=renderCount;
  for(auto*m:{&base,&mod}){auto before=m->caller();m->phase=1;m->run(adapter.labels.at("call"),adapter.labels.at("stop"));m->canaries();if(m->caller()!=before)throw std::runtime_error("vpre declared caller register preservation");}
  bool same=true;for(int j=0;j<48;++j)same&=base.x[0x3bb0+j]==mod.x[0x3bb0+j]&&base.x[0x3930+j]==mod.x[0x3930+j];for(int j=1;j<64;j+=2)same&=base.y[RING+j]==mod.y[RING+j];if(!same)throw std::runtime_error("Other MIDI track changed");
  bool rendered=renderCount>before;
  auto bvi=base.cpu.getInstructionCounter()-bi,mvi=mod.cpu.getInstructionCounter()-mi,bvc=base.cpu.getCycles()-bc,mvc=mod.cpu.getCycles()-mc;
  for(auto*m:{&base,&mod}){m->strip();m->canaries();for(int j=0;j<64;++j){int32_t sample=s24(m->y[0x800+j]);mixed.write(reinterpret_cast<char*>(&sample),4);}}
  report<<block<<','<<base.cpu.getInstructionCounter()-bi<<','<<mod.cpu.getInstructionCounter()-mi<<','<<base.cpu.getCycles()-bc<<','<<mod.cpu.getCycles()-mc<<','<<bvi<<','<<mvi<<','<<bvc<<','<<mvc<<','<<rendered<<','<<mod.x[CTRL]<<','<<mod.x[CTRL+1]<<','<<mod.x[CTRL+2]<<",1,1,1,1,"<<wrapEvents<<','<<pwEvents<<','<<mod.reads<<','<<mod.writes<<'\n';
  states<<block;for(int j=0;j<7;++j)states<<','<<s24(mod.x[STATE+j]);states<<'\n';
  for(int j=0;j<32;++j){int32_t value=s24(mod.y[OUTY+j]);samples.write(reinterpret_cast<char*>(&value),4);for(auto*m:{&base,&mod}){int32_t l=s24(m->y[RING+2*j]),r=s24(m->y[RING+2*j+1]);rings.write(reinterpret_cast<char*>(&l),4);rings.write(reinterpret_cast<char*>(&r),4);}}
  ++count;
 }
 for(auto*m:{&base,&mod}){std::ofstream f((m==&base?out/"baseline":out/"replacement")/"executed.asm");for(auto[pc,s]:m->dis)f<<std::hex<<pc<<' '<<m->sizes[pc]<<' '<<s<<'\n';}
 std::ofstream summary(out/"native.json");summary<<"{\"blocks\":"<<count<<",\"renders\":"<<renderCount<<",\"adapter_checks\":"<<adapterChecks<<",\"access_violations\":"<<mod.violations<<",\"flash_image\":false,\"hardware\":false}\n";
 std::cout<<"blocks "<<count<<" renders "<<renderCount<<" ABI checks "<<adapterChecks<<'\n';return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 9;}
