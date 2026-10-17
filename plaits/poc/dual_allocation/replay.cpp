// Source-regression replay utility; no firmware packaging or hardware interfaces.
#include "dsp56kEmu/dsp.h"
#include "dsp56kEmu/assembler.h"
#include <fstream>
#include <iostream>
#include <sstream>
#include <unordered_map>
#include <vector>
#include <iomanip>
#include <regex>
#include <stdexcept>
#include <crtdbg.h>
using namespace dsp56k;
int reportError(int,char*m,int*){std::cerr<<"Interpreter assertion: "<<m<<'\n';std::_Exit(9);}
struct Deny:IPeripherals{bool initial=true;Deny():IPeripherals(PeripheralType::PeripheralsNop){}TWord read(TWord,Instruction)override{throw std::runtime_error("Peripheral read");}const TWord*readAsPtr(TWord,Instruction)override{throw std::runtime_error("Peripheral pointer");}void write(TWord a,TWord v)override{if(!initial||v||(a!=0xfffffe&&a!=0xffffff))throw std::runtime_error("Peripheral write");}void reset()override{}void setSymbols(Disassembler&)const override{}void terminate()override{}};
int main(int argc,char**argv)try{
 _CrtSetReportHook(reportError);
 if(argc==2&&std::string(argv[1])=="asm"){Assembler a;std::string l;while(std::getline(std::cin,l)){auto q=a.assemble(l.c_str());if(!q.success()){std::cout<<"ERR "<<int(q.error)<<'\n';continue;}std::cout<<q.wordCount;for(unsigned j=0;j<q.wordCount;++j)std::cout<<' '<<std::hex<<std::setw(6)<<std::setfill('0')<<q.word[j]<<std::dec;std::cout<<'\n';}return 0;}
 if(argc!=2)throw std::runtime_error("replay job");std::vector<TWord>p(0x10000);std::unordered_map<TWord,TWord>x,y;DefaultMemoryValidator valid;Memory mem(valid,0x10000);Deny px,py;DSP cpu(mem,&px,&py);px.initial=py.initial=false;mem.setExternalMemory(0x1000000,true);
 bool running=false;uint64_t pwrites=0;TWord pc=0;std::ofstream access;
 mem.replayRead=[&](auto a,auto ad){if(a==MemArea_P){if(ad>=p.size())throw std::runtime_error("P extent");return p[ad];}auto&v=a==MemArea_X?x:y;auto i=v.find(ad);return i==v.end()?TWord(0):i->second;};
 mem.replayWrite=[&](auto a,auto ad,auto v){if(a==MemArea_P){if(running){++pwrites;throw std::runtime_error("Runtime P write");}p.at(ad)=v;return;}auto&d=a==MemArea_X?x:y;d[ad]=v&0xffffff;if(running&&access)access<<std::hex<<pc<<','<<(a==MemArea_X?'X':'Y')<<','<<ad<<','<<v<<'\n';};
 cpu.setReplayBefore([&](auto at,auto){pc=at;});
 std::ifstream job(argv[1]);if(!job)throw std::runtime_error("Missing job");std::string l;TWord stop=0;uint64_t maximum=2000000;
 while(std::getline(job,l)){std::istringstream s(l);std::string c;s>>c;
  if(c=="P"||c=="X"||c=="Y"){std::string a,w;s>>a;TWord ad=std::stoul(a,nullptr,16);while(s>>w){TWord v=std::stoul(w,nullptr,16)&0xffffff;if(c=="P")p.at(ad++)=v;else(c=="X"?x:y)[ad++]=v;}}
  else if(c=="PC"){std::string a;s>>a;cpu.setPC(std::stoul(a,nullptr,16));}
  else if(c=="STOP"){std::string a;s>>a;stop=std::stoul(a,nullptr,16);}
  else if(c=="MAX")s>>maximum;
  else if(c=="WRITES"){std::string a;std::getline(s,a);a.erase(0,a.find_first_not_of(' '));access.open(a);}
  else if(c=="RUN"){auto i=cpu.getInstructionCounter(),cy=cpu.getCycles();uint64_t n=0;running=true;while(cpu.getPC().var!=stop&&n<maximum){cpu.execInterpreter();++n;}running=false;std::cout<<"RAN "<<n<<" pc="<<std::hex<<std::setw(6)<<std::setfill('0')<<cpu.getPC().var<<std::dec<<" ins="<<cpu.getInstructionCounter()-i<<" cyc="<<cpu.getCycles()-cy<<" sp="<<cpu.readRegs().sp.var<<" pwrites="<<pwrites<<'\n';if(n==maximum)throw std::runtime_error("Instruction cap");}
  else if(c=="DUMPX"||c=="DUMPY"||c=="DUMPP"){std::string a;unsigned n;s>>a>>n;TWord ad=std::stoul(a,nullptr,16);std::cout<<c.back()<<' '<<std::hex<<std::setw(6)<<std::setfill('0')<<ad<<':';for(unsigned j=0;j<n;++j){TWord v=c.back()=='P'?p.at(ad+j):(c.back()=='X'?x:y)[ad+j];std::cout<<' '<<std::setw(6)<<v;}std::cout<<std::dec<<'\n';}
 }return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 9;}
