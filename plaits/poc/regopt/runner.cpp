// Standalone synthetic oscillator only; links sealed Phase19A interpreter.
// No stock image, hardware, OS audio/MIDI, shared memory or device peripherals.
#include "dsp56kEmu/dsp.h"
#include "dsp56kEmu/assembler.h"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <map>
#include <vector>
#include <regex>
#include <cmath>
#include <stdexcept>
using namespace dsp56k;namespace fs=std::filesystem;
constexpr int Q=1<<21,F=1<<22;
int32_t signed24(TWord v){return int32_t(v<<8)>>8;}
void word24(std::ostream&o,TWord v){for(int s:{16,8,0})o.put(char(v>>s));}
struct Deny:IPeripherals{
 bool constructing=true;
 Deny():IPeripherals(PeripheralType::PeripheralsNop){}
 TWord read(TWord,Instruction)override{throw std::runtime_error("No peripherals");}
 const TWord* readAsPtr(TWord,Instruction)override{throw std::runtime_error("No pointers");}
 void write(TWord a,TWord v)override{if(!constructing||(a!=0xfffffe&&a!=0xffffff)||v)throw std::runtime_error("No peripheral writes");}
 void reset()override{}void setSymbols(Disassembler&)const override{}void terminate()override{}
};
struct Program{
 std::map<TWord,std::string> instructions;std::map<std::string,TWord> labels;
 std::vector<TWord> words;TWord origin=0x200,done=0;
 Program(const fs::path&path){
  std::ifstream in(path);if(!in)throw std::runtime_error("Assembly missing");
  std::vector<std::string> lines;std::string line;while(std::getline(in,line)){if(!line.empty()&&line.back()=='\r')line.pop_back();if(!line.empty())lines.push_back(line);}
  Assembler assembler;std::regex sym("@([A-Za-z_][A-Za-z_0-9]*)");
  for(int pass=0;pass<2;++pass){
   TWord pc=origin;words.clear();instructions.clear();
   for(auto s:lines){
    if(s.back()==':'){labels[s.substr(0,s.size()-1)]=pc;continue;}
    std::smatch m;while(std::regex_search(s,m,sym)){
     if(pass&&!labels.count(m[1].str()))throw std::runtime_error("Unknown label");
     std::ostringstream v;v<<'$'<<std::hex<<std::setw(6)<<std::setfill('0')<<(pass?labels.at(m[1].str()):1);
     s.replace(size_t(m.position()),size_t(m.length()),v.str());
    }
    auto op=assembler.assemble(s.c_str());
    if(!op.success())throw std::runtime_error("Assembler error "+std::to_string(int(op.error))+" at "+s);
    if(s=="mpy y0,x0,a"&&(op.wordCount!=1||op.word[0]!=0x2000d0))
     throw std::runtime_error("SignedMPY opcode qualification failed");
    instructions[pc]=s;for(unsigned i=0;i<op.wordCount;++i){words.push_back(op.word[i]);++pc;}
   }
   if(pass==1&&labels.at("done")!=pc)throw std::runtime_error("Assembly layout changed");
  }
  done=labels.at("done");if(done>=0x1000)throw std::runtime_error("P capacity");
 }
};
struct Bus{
 const Program&p;DSP*cpu=nullptr;std::vector<TWord>x=std::vector<TWord>(256),y=std::vector<TWord>(32);
 std::ofstream&trace;uint64_t issued=0,blockCount=0,writes=0,writeHash=0,execHash=0;
 std::vector<EReg> retainedRegs={Reg_Y1,Reg_R1,Reg_R2,Reg_R3,Reg_R4,Reg_R5,Reg_R6,Reg_R7,Reg_N0,Reg_N1,Reg_N2,Reg_N3,Reg_N4,Reg_N5,Reg_N6,Reg_N7};
 std::vector<TWord> savedRegs;
 TWord pc=0,op=0;unsigned maxStack=0,outputWrites=0,phaseWraps=0,ratioCalls=0,ratioIssued=0,divIssued=0;
 int maxX=0;bool running=false;unsigned scratchHi=0xc0;
 Bus(const Program&pp,std::ofstream&t,unsigned hi):p(pp),trace(t),scratchHi(hi){}
 static void mix(uint64_t&h,uint64_t v){for(int i=0;i<8;++i){h^=(v>>(i*8))&255;h*=1099511628211ull;}}
 TWord read(EMemArea a,TWord at){
  if(a==MemArea_P){
   // Reset/decoder speculative second-word reads see ownedNOP padding only.
   if(at==0||at==1||at==p.done||at==p.done+1)return 0;
   if(at<p.origin||at>=p.done)throw std::runtime_error("Unloaded P read");return p.words[at-p.origin];
  }
  if(a==MemArea_X&&((at>=0x20&&at<0x27)||(at>=0x30&&at<0x33)||(at<scratchHi)))return x[at];
  if(a==MemArea_Y&&at<y.size())return y[at];
  throw std::runtime_error("Unmapped read");
 }
 void write(EMemArea a,TWord at,TWord v){
  if(!running)throw std::runtime_error("Unexpected initializer through CPU bus");
  if(a==MemArea_P)throw std::runtime_error("P write forbidden");
  if(a==MemArea_X){
   if(!((at>=0x20&&at<0x27)||(at>=0x30&&at<0x33)||(at<scratchHi)))throw std::runtime_error("X write outside owned layout");
   x[at]=v&0xffffff;maxX=std::max(maxX,std::abs(signed24(v)));
  }else{
   if(at>=32||at!=outputWrites)throw std::runtime_error("Y output ordering/buffer overflow");y[at]=v&0xffffff;++outputWrites;
  }
  ++writes;mix(writeHash,a);mix(writeHash,at);mix(writeHash,v&0xffffff);
 }
 void before(TWord at,TWord word){
  pc=at;op=word; if(at==p.labels.at("ratio"))++ratioCalls; if(at>=p.labels.at("ratio"))++ratioIssued; if(p.instructions.at(at)=="div y0,a")++divIssued;if(!p.instructions.count(at))throw std::runtime_error("PC not an instruction boundary");
  if(++issued-blockCount>30000)throw std::runtime_error("Block instruction budget");
  trace.put(char(at));trace.put(char(at>>8));mix(execHash,at);mix(execHash,word);
  if(at==p.labels.at("wrap_event"))++phaseWraps;
  maxStack=std::max(maxStack,unsigned(cpu->readRegs().sc.var));
  const auto&s=p.instructions.at(at);
  if(at==p.labels.at("ratio")){savedRegs.clear();for(auto reg:retainedRegs){TReg24 v;cpu->readReg(reg,v);savedRegs.push_back(v.var);}}
  if(at>=p.labels.at("ratio")&&s=="rts")for(size_t i=0;i<retainedRegs.size();++i){TReg24 v;cpu->readReg(retainedRegs[i],v);if(v.var!=savedRegs[i])throw std::runtime_error("Helper clobbered allocated register");}
  if(s.rfind("move a,x:",0)==0||s.rfind("move a,y:",0)==0||s.rfind("move a1,",0)==0){
   // The sealed core left-aligns its56-bit accumulator in64 bits (8 pad bits).
   auto a=int64_t(cpu->readRegs().a.var);
   auto hi=a>>32;if(hi>=8388608||hi<-8388608)throw std::runtime_error("Accumulator narrowing saturation PC="+std::to_string(at)+" hi="+std::to_string(hi));
  }
 }
 void begin(){blockCount=issued;writes=0;writeHash=execHash=1469598103934665603ull;outputWrites=phaseWraps=ratioCalls=ratioIssued=divIssued=0;running=true;}
};
int main(int argc,char**argv)try{
 // Emulator execution is noexcept: report rejected bus state and exit without
 // a Windows runtime dialog if a strict callback raises an exception.
 std::set_terminate([](){std::fprintf(stderr,"Standalone fail-closed termination\n");try{if(auto e=std::current_exception())std::rethrow_exception(e);}
  catch(const std::exception&e){std::cerr<<"Rejected standalone execution: "<<e.what()<<'\n';}
  std::_Exit(9);});
 static_assert(!g_useJIT,"Interpreter required");
 if(argc!=5)throw std::runtime_error("assembly cases.tsv fresh-output scratchHighHex");
 const fs::path root=fs::path(__FILE__).parent_path().parent_path().parent_path().parent_path();
 const auto base=fs::weakly_canonical(root/"builds/phase20a-regopt"),out=fs::weakly_canonical(fs::absolute(argv[3]));
 const auto rel=out.lexically_relative(base);
 if(rel.empty()||*rel.begin()==".."||fs::exists(out))throw std::runtime_error("Fresh standalone Phase20A-DIV output required");
 Program program(argv[1]);std::ifstream cases(argv[2]);if(!cases)throw std::runtime_error("Cases missing");
 fs::create_directories(out);
 std::ofstream raw(out/"output.i32",std::ios::binary),trace(out/"execution-pc.u16",std::ios::binary),report(out/"blocks.csv"),states(out/"states.csv");
 report<<"case,block,instructions,write_count,execution_hash,write_hash,peak_stack,output_writes,wrap_events,ratio_calls,ratio_issued,div_issued\n";
 states<<"case,block,phase,next,previous_pw,high,frequency,pw,shape\n";
 {std::ofstream f(out/"program.be24",std::ios::binary);for(auto w:program.words)word24(f,w);}
 {std::ofstream f(out/"program.asm");for(auto [pc,s]:program.instructions)f<<std::hex<<pc<<' '<<s<<'\n';}
 {std::ofstream f(out/"labels.json");f<<'{';bool first=true;for(auto [name,pc]:program.labels){if(!first)f<<',';first=false;f<<'"'<<name<<"\":"<<pc;}f<<"}\n";}
 std::unique_ptr<Bus>bus;std::unique_ptr<DefaultMemoryValidator>validator;std::unique_ptr<Memory>mem;
 std::unique_ptr<Deny>px,py;std::unique_ptr<DSP>dsp;
 int id,block,last=-1,totalBlocks=0;double f,pw,shape;
 uint64_t totalIssued=0;unsigned peak=0;
 while(cases>>id>>block>>f>>pw>>shape){
  if(!(f>0&&f<=.5&&std::llround(f*F)>=1&&pw>=0&&pw<=1&&shape>=0&&shape<=1))throw std::runtime_error("Invalid control domain");
  if(id!=last){
   dsp.reset();mem.reset();validator.reset();px.reset();py.reset();bus.reset();
   bus=std::make_unique<Bus>(program,trace,unsigned(std::stoul(argv[4],nullptr,16)));
   validator=std::make_unique<DefaultMemoryValidator>();mem=std::make_unique<Memory>(*validator,0x1000);
   mem->setExternalMemory(0x1000000,true);
   mem->replayRead=[&](auto a,auto at){return bus->read(a,at);};mem->replayWrite=[&](auto a,auto at,auto v){bus->write(a,at,v);};
   px=std::make_unique<Deny>();py=std::make_unique<Deny>();dsp=std::make_unique<DSP>(*mem,px.get(),py.get());bus->cpu=dsp.get();
   px->constructing=py->constructing=false;
   dsp->writeReg(Reg_SR,TReg24(0x300));dsp->writeReg(Reg_OMR,TReg24(0));dsp->writeReg(Reg_SP,TReg24(0));dsp->writeReg(Reg_SC,TReg5(0));
   dsp->writeReg(Reg_M0,TReg24(0xffffff));dsp->writeReg(Reg_M1,TReg24(0xffffff));
   dsp->writeReg(Reg_M2,TReg24(0xffffff));dsp->writeReg(Reg_M3,TReg24(0xffffff));
   dsp->writeReg(Reg_M4,TReg24(0xffffff));dsp->writeReg(Reg_M5,TReg24(0xffffff));
   dsp->writeReg(Reg_M6,TReg24(0xffffff));dsp->writeReg(Reg_M7,TReg24(0xffffff));
   dsp->setReplayBefore([&](auto pc,auto op){bus->before(pc,op);});
   bus->x[0x22]=F/2;bus->x[0x24]=TWord(std::llround(.01*F));bus->x[0x25]=F/2;last=id;
  }
  bus->x[0x30]=TWord(std::llround(f*F));bus->x[0x31]=TWord(std::llround(pw*F));bus->x[0x32]=TWord(std::llround(shape*Q));
  bus->begin();dsp->setPC(program.origin);
  try{while(dsp->getPC().var!=program.done)dsp->execInterpreter();}
  catch(const std::exception&e){std::cerr<<e.what()<<" PC="<<std::hex<<dsp->getPC().var<<" issued="<<std::dec<<bus->issued<<'\n';std::_Exit(9);}
  bus->running=false;
  if(bus->outputWrites!=32||dsp->readRegs().sc.var!=0)throw std::runtime_error("Block/stack contract");
  for(auto v:bus->y){int32_t x=signed24(v);raw.write(reinterpret_cast<char*>(&x),4);}
  report<<id<<','<<block<<','<<bus->issued-bus->blockCount<<','<<bus->writes<<','<<bus->execHash<<','<<bus->writeHash<<','<<bus->maxStack<<','<<bus->outputWrites<<','<<bus->phaseWraps<<','<<bus->ratioCalls<<','<<bus->ratioIssued<<','<<bus->divIssued<<'\n';
  states<<id<<','<<block;for(int i=0;i<7;++i)states<<','<<signed24(bus->x[0x20+i]);states<<'\n';
  totalIssued+=bus->issued-bus->blockCount;peak=std::max(peak,bus->maxStack);++totalBlocks;
 }
 std::ofstream manifest(out/"native-resources.json");
 manifest<<"{\"P_words\":"<<program.words.size()<<",\"blocks\":"<<totalBlocks<<",\"issued_instructions\":"<<totalIssued
  <<",\"P_decoder_padding_words\":2,\"peak_stack_entries\":"<<peak<<",\"hardware_access\":false,\"stock_image_loaded\":false,\"peripheral_events\":0,\"saturation_failures\":0}\n";
 return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 9;}
