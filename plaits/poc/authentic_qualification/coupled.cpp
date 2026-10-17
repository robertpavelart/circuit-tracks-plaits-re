// CIRCUIT-only experiment. No firmware generation and no hardware interfaces.
#include <windows.h>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <vector>
#include <map>
#include <array>
#include <string>
#include <memory>
#include <iostream>
#include <cstring>
#include "dsp56kEmu/dsp.h"
#include "dsp56kEmu/memory.h"
#include "dsp56kEmu/peripherals.h"
using namespace dsp56k;
static Memory* mems[2];static DSP* dsps[2];
static TWord instructionPC[2]={};
static void* host;static void* fibers[2];static int running=-1;
static bool audit=false;static unsigned block=0;static TWord freeStart=0x4000;
static uint64_t fetches[2]={},pwrites=0,accesses=0,iccReads=0,iccWrites=0;
static std::map<unsigned,uint64_t> pcs[2];
static FILE* trace=nullptr;
static FILE* stageFile=nullptr;
static TWord regword(int c,EReg r){int64_t v=0;dsps[c]->readRegToInt(r,v);return TWord(v)&0xffffff;}
static void stage(TWord pc,const char*name,EMemArea area,TWord base,TWord n){
 if(!stageFile||base+n>0x80000)return;
 auto*x=mems[0]->getMemAreaPtr(MemArea_X);auto*p=mems[0]->getMemAreaPtr(area);
 fprintf(stageFile,"S %u %06x %06x %06x %s %c %06x %u",block,x[0xcc],x[0xcb],pc,name,area==MemArea_X?'X':'Y',base,n);
 for(TWord i=0;i<n;++i)fprintf(stageFile," %06x",p[base+i]);fprintf(stageFile,"\n");
 fprintf(stageFile,"C %u %06x %06x %06x r0=%06x r4=%06x sr=%06x",block,x[0xcc],x[0xcb],pc,regword(0,Reg_R0),regword(0,Reg_R4),regword(0,Reg_SR));
 auto r0=regword(0,Reg_R0);for(TWord i=0;i<12&&r0+i<0x80000;++i)fprintf(stageFile," x%06x=%06x",r0+i,x[r0+i]);fprintf(stageFile,"\n");
}
static const EReg contract[]={Reg_X0,Reg_X1,Reg_Y0,Reg_Y1,Reg_R0,Reg_R1,Reg_R6,Reg_R7,Reg_N0,Reg_M0,Reg_R2,Reg_R3,Reg_R4,Reg_M2,Reg_M4};
static std::array<int64_t,15> savedContract;static bool contractPending=false;static uint64_t contractChecks=0;
static int64_t c1R5,c1M5;static bool c1Pending=false;static uint64_t c1Checks=0;
[[noreturn]] static void fail(const char* why,int core,EMemArea area,TWord a){
 fprintf(stderr,"FAIL %s block=%u core=%d pc=%06x space=%d addr=%06x\n",why,block,core,core>=0?dsps[core]->getPC().toWord():0,int(area),a);fflush(stderr);if(trace)fflush(trace);std::exit(3);
}
struct Region {
 std::string name;TWord lo,hi,mask;std::vector<TWord> words;std::vector<uint8_t> known;
 Region(std::string n,TWord l,TWord h,TWord m):name(n),lo(l),hi(h),mask(m),words(h-l+2,0x5a1234),known(h-l,0){for(size_t i=1;i+1<words.size();++i)words[i]=0;}
 bool contains(TWord a)const{return a>=lo&&a<hi;}
 void check()const{if(words.front()!=0x5a1234||words.back()!=0x5a1234)fail("REGION_CANARY",running,MemArea_Y,lo);}
};
static std::vector<Region> regions;
static std::array<TWord,0x8000+2> shared;
static std::map<TWord,TWord> bootRegister[2]; // DSP56724 low peripheral bank; behavior beyond latching UNKNOWN.
static uint64_t hashes[4]={1469598103934665603ull,1469598103934665603ull,1469598103934665603ull,1469598103934665603ull};
static std::vector<TWord> exactTraffic;
struct Gather {bool pending=false;uint64_t issue0=0,issue1=0,done0=0,done1=0;unsigned issueBlock=0;};
static std::map<TWord,Gather> gather;static uint64_t issued=0,completed=0,consumed=0;
static void hashword(int i,TWord a,TWord v,bool w){for(TWord x:{a,v,TWord(w)}){hashes[i]^=x;hashes[i]*=1099511628211ull;}}
static int cid(const Memory*m){return m==mems[0]?0:m==mems[1]?1:-1;}
namespace dsp56k {
 void replayObserve(const Memory*m,EMemArea area,TWord a,TWord v){int c=cid(m);if(c>=0&&audit&&trace)fprintf(trace,"%u %d %06x %c %06x R %06x %s\n",block,c,instructionPC[c],area==MemArea_P?'P':area==MemArea_X?'X':'Y',a,v,running==c?"DSP":"HOST");}
 bool replayAccess(const Memory*m,EMemArea area,TWord a,bool w,TWord&v){
  int c=cid(m);if(c<0)return false;
  if(a>0xffffff)fail("ADDRESS_WIDTH",c,area,a);
  ++accesses;
  if(area==MemArea_P){if(audit&&w){++pwrites;if(c==0&&a>=0x3bba&&a<0x4000)fail("CANDIDATE_P_WRITE",c,area,a);}
   if(audit&&a>=freeStart&&a<0x4000&&c==0)fail("FREE_P_DATA_ACCESS",c,area,a);
  }
  bool handled=false;
  if(area==MemArea_X&&a>=0xfffe00&&a<0xffff80){if(w)bootRegister[c][a]=v&0xffffff;else {if(!bootRegister[c].count(a))fail("UNKNOWN_LOW_PERIPHERAL_READ",c,area,a);v=bootRegister[c][a];}handled=true;}
  if(a>=0x30000&&a<0x38000){
   // DSP56724RM 1.4.12 / 4.3.4: shared SRAM aliases X and Y (and P).
   if(audit&&running==c&&a>=0x30002&&a<0x37000){
    if(c==0&&w&&area==MemArea_X){auto&g=gather[a];g={true,fetches[0],fetches[1],0,0,block};++issued;}
    if(c==1&&w&&area==MemArea_X&&gather.count(a)){auto&g=gather[a];g.pending=false;g.done0=fetches[0];g.done1=fetches[1];++completed;if(trace)fprintf(trace,"GATHER DONE %u %06x %llu %llu %llu %llu\n",block,a,(unsigned long long)g.issue0,(unsigned long long)g.issue1,(unsigned long long)g.done0,(unsigned long long)g.done1);}
    if(c==0&&!w&&area==MemArea_Y&&gather.count(a)){auto&g=gather[a];if(g.pending)fail("STALE_GATHER_CONSUMPTION",c,area,a);++consumed;if(trace)fprintf(trace,"GATHER CONSUME %u %06x %llu %u\n",block,a,(unsigned long long)fetches[0],g.issueBlock);}
   }
   auto&x=shared[a-0x30000+1];if(w)x=v&0xffffff;else v=x;handled=true;if(audit)hashword(0,a,v,w);
  }
  if(!handled&&area!=MemArea_P&&a>=0x80000){
   for(auto&r:regions)if(r.contains(a)){size_t i=a-r.lo;
    if(w){r.words[i+1]=v&r.mask;r.known[i]=1;}else{if(!r.known[i])fail("UNKNOWN_EXTERNAL_READ",c,area,a);v=r.words[i+1];}
    handled=true;if(audit)hashword(1,a,v,w);break;
   }
   if(!handled)fail("UNBACKED_EXTERNAL_ACCESS",c,area,a);
  }
  if(audit&&(handled||w)){exactTraffic.push_back(a|(TWord(c)<<24)|(TWord(area)<<25)|(TWord(w)<<28)|(TWord(running==c)<<29));exactTraffic.push_back(v);}
  if(audit&&trace&&(handled||w)){fprintf(trace,"%u %d %06x %c %06x %c %06x %s\n",block,c,instructionPC[c],area==MemArea_P?'P':area==MemArea_X?'X':'Y',a,w?'W':'R',v,running==c?"DSP":"HOST");}
  if(!handled&&audit&&w)hashword(c+2,a,v,w);
  return handled;
 }
 void replayFetch(const Memory*m,TWord&pc){
  int c=cid(m);if(c<0)return;
  if(running==c){SwitchToFiber(host);pc=dsps[c]->getPC().toWord();}
  instructionPC[c]=pc;
  if(audit&&c==0&&stageFile){
   switch(pc){
   case 0x9d9:stage(pc,"raw_mono",MemArea_X,0x2c46,32);break;
   case 0xbdf:stage(pc,"normalized",MemArea_X,regword(0,Reg_R1),32);break;
   case 0xbe8:stage(pc,"filter_input_scaled",MemArea_X,0x2c68,32);break;
   case 0xc1a:stage(pc,"filter_pass1",MemArea_X,0x2c8a,32);break;
   case 0xc24:stage(pc,"filter_output",MemArea_X,mems[0]->getMemAreaPtr(MemArea_X)[0]+2,32);break;
   case 0xa89:stage(pc,"voice_gain_input",MemArea_X,0x2c46,32);break;
   case 0xa95:stage(pc,"voice_bank_sum",MemArea_X,mems[0]->getMemAreaPtr(MemArea_X)[0xcc]?0x2e50:0x2df0,32);break;
   case 0x20c:stage(pc,"bank0_pre_strip",MemArea_X,0x2df0,32);stage(pc,"bank1_pre_strip",MemArea_X,0x2e50,32);break;
   case 0x216:stage(pc,"bank0_post_eq",MemArea_X,0x2df0,32);break;
   case 0x21c:stage(pc,"bank0_stereo_strip",MemArea_Y,0x840,64);break;
   case 0x226:stage(pc,"bank1_post_eq",MemArea_X,0x2e50,32);break;
   case 0x230:stage(pc,"bank1_stereo_strip",MemArea_Y,0x880,64);break;
   case 0x24f:stage(pc,"stock_mixer",MemArea_Y,0x800,64);break;
   case 0x25c:stage(pc,"mixer_plus_bus",MemArea_Y,0x800,64);break;
   case 0x262:stage(pc,"sends_return",MemArea_Y,0x9c0,64);stage(pc,"pre_master",MemArea_X,0x2e10,64);break;
   case 0x274:stage(pc,"pre_MasterFX",MemArea_X,0x2e10,64);break;
   case 0x276:stage(pc,"post_MasterFX",MemArea_X,0x2e10,64);break;
   case 0x278:stage(pc,"post_output_staging",MemArea_X,0x2e10,64);stage(pc,"output_ring",MemArea_X,0x1000,64);break;
   }
  }
  if(audit&&c==0&&pc==0x336e){for(size_t i=0;i<15;++i)dsps[c]->readRegToInt(contract[i],savedContract[i]);contractPending=true;}
  if(audit&&c==0&&pc==0x23e&&contractPending){for(size_t i=0;i<15;++i){int64_t v;dsps[c]->readRegToInt(contract[i],v);if(v!=savedContract[i])fail("VPRE_REGISTER",c,MemArea_X,TWord(i));}contractPending=false;++contractChecks;}
  if(audit&&c==1&&pc==0x16c){dsps[c]->readRegToInt(Reg_R5,c1R5);dsps[c]->readRegToInt(Reg_M5,c1M5);c1Pending=true;}
  if(audit&&c==1&&pc==0x10e&&c1Pending){int64_t r5,m5;dsps[c]->readRegToInt(Reg_R5,r5);dsps[c]->readRegToInt(Reg_M5,m5);if(r5!=c1R5||m5!=c1M5)fail("CORE1_R5_M5",c,MemArea_X,0);c1Pending=false;++c1Checks;}
  ++fetches[c];if(audit){++pcs[c][pc];if(c==0&&pc>=freeStart&&pc<0x4000)fail("FREE_P_EXECUTION",c,MemArea_P,pc);}
  if(c==0&&pc==0x25ee&&getenv("CIRCUIT_DEBUG_LOOP")){int64_t lc,la,sc;dsps[c]->readRegToInt(Reg_LC,lc);dsps[c]->readRegToInt(Reg_LA,la);dsps[c]->readRegToInt(Reg_SC,sc);fprintf(stderr,"LOOP lc=%llx la=%llx sc=%llx\n",(long long)lc,(long long)la,(long long)sc);}
 }
}
// Model only peer ICC state/progress actually consumed by the two stock loops.
// D0 local request/ack, D1 peer D0, D7 local gather progress, D4 peer D7.
class ICC final:public IPeripherals{
 public:int core;bool y;std::array<TWord,128> data{};ICC(int c,bool yy):IPeripherals(PeripheralType::PeripheralsNop),core(c),y(yy){}
 ICC*peer=nullptr;
 TWord read(TWord a,Instruction)override{++iccReads;TWord v=0;if(y&&a==0xffffd1)v=peer->data[0x50];else if(y&&a==0xffffd4)v=peer->data[0x57];else if(a>=0xffff80)v=data[a-0xffff80];if(audit&&trace)fprintf(trace,"ICC %u %d R %06x %06x\n",block,core,a,v);return v;}
 const TWord*readAsPtr(TWord a,Instruction i)override{static TWord temp;temp=read(a,i);return &temp;}
 void write(TWord a,TWord v)override{++iccWrites;if(a>=0xffff80)data[a-0xffff80]=v&0xffffff;if(audit&&trace)fprintf(trace,"ICC %u %d W %06x %06x\n",block,core,a,v);}
 void reset()override{}void setSymbols(Disassembler&)const override{}void terminate()override{}
};
static VOID WINAPI cpu(void*arg){int c=int(reinterpret_cast<intptr_t>(arg));while(true)dsps[c]->execInterpreter();}
static void step(int c){running=c;SwitchToFiber(fibers[c]);running=-1;}
static void load(Memory&m,std::string fn,TWord a){std::ifstream f(fn,std::ios::binary);if(!f)fail("MISSING_PROGRAM",-1,MemArea_P,a);std::vector<unsigned char>d((std::istreambuf_iterator<char>(f)),{});for(size_t i=0;i+2<d.size();i+=3)m.set(MemArea_P,a++,(d[i]<<16)|(d[i+1]<<8)|d[i+2]);}
int main(int argc,char**argv){
 if(argc!=2)return 2;
 DefaultMemoryValidator mv;Memory m0(mv,0x80000),m1(mv,0x80000);mems[0]=&m0;mems[1]=&m1;
 ICC x0(0,false),y0(0,true),x1(1,false),y1(1,true);y0.peer=&y1;y1.peer=&y0;x0.peer=&x1;x1.peer=&x0;
 DSP d0(m0,&x0,&y0),d1(m1,&x1,&y1);dsps[0]=&d0;dsps[1]=&d1;
 shared.fill(0);shared.front()=shared.back()=0x5a1234;
 host=ConvertThreadToFiber(nullptr);fibers[0]=CreateFiber(16*1024*1024,cpu,reinterpret_cast<void*>(0));fibers[1]=CreateFiber(16*1024*1024,cpu,reinterpret_cast<void*>(1));
 if(!host||!fibers[0]||!fibers[1])return 4;
 int c=0;TWord stop=0xffffff;uint64_t limit=2000000;
 std::ifstream f(argv[1]);std::istream&input=std::string(argv[1])=="-"?std::cin:f;std::string line;
 while(std::getline(input,line)){std::istringstream s(line);std::string op;s>>op;if(op.empty()||op[0]=='#')continue;
  auto number=[&](){std::string v;s>>v;return TWord(strtoul(v.c_str(),nullptr,16));};
  if(op=="SYNC"){printf("SYNC\n");fflush(stdout);}
  else if(op=="CORE")s>>c;
  else if(op=="LOADP"){std::string fn;s>>fn;load(*mems[c],fn,number());}
  else if(op=="LOADY"){std::string fn;s>>fn;TWord a=number();std::ifstream b(fn,std::ios::binary);if(!b)fail("MISSING_DATA",-1,MemArea_Y,a);std::vector<unsigned char>d((std::istreambuf_iterator<char>(b)),{});for(size_t i=0;i+2<d.size();i+=3)mems[c]->set(MemArea_Y,a++,(d[i]<<16)|(d[i+1]<<8)|d[i+2]);}
  else if(op=="PC")dsps[c]->setPC(number());
  else if(op=="STOP")stop=number();
  else if(op=="MAX")s>>limit;
  else if(op=="SERVICE"){
   // Actual stock Y:2C dispatcher, including its persistent multi-call job.
   TWord stub=number();uint64_t calls=0,steps=0;
   do{dsps[c]->setPC(stub);if(!fetches[c])step(c);while(dsps[c]->getPC().toWord()!=stub+2&&steps<limit){step(c);++steps;}++calls;
    if(steps>=limit)fail("SERVICE_LIMIT",c,MemArea_Y,0x2c);
   }while(mems[c]->get(MemArea_Y,0x2c)!=0x800000);
   printf("SERVICE calls=%llu steps=%llu mailbox=%06x\n",(unsigned long long)calls,(unsigned long long)steps,mems[c]->get(MemArea_Y,0x2c));fflush(stdout);
  }
  else if(op=="SAVEY"){
   std::string fn;s>>fn;auto a=number(),n=number();FILE*out=fopen(fn.c_str(),"wb");for(TWord i=0;i<n;++i){TWord v=mems[c]->get(MemArea_Y,a+i);unsigned char b[]={static_cast<unsigned char>(v>>16),static_cast<unsigned char>(v>>8),static_cast<unsigned char>(v)};fwrite(b,1,3,out);}fclose(out);
  }
  else if(op=="STEPS"){uint64_t n;s>>n;while(n--)step(c);}
  else if(op=="BLOCK")s>>block;
  else if(op=="STAGES"){std::string fn;s>>fn;stageFile=fopen(fn.c_str(),"w");}
  else if(op=="FREE")freeStart=number();
  else if(op=="AUDIT")audit=true;
  else if(op=="TRACE"){if(trace)fclose(trace);std::string name;s>>name;trace=fopen(name.c_str(),"w");}
  else if(op=="TRACEOFF"){if(trace)fclose(trace);trace=nullptr;}
  else if(op=="STATEWRITE"||op=="STATECHECK"){
   std::string fn;s>>fn;bool ram=fn=="SHARED";FILE*out=nullptr;static HANDLE mapping=nullptr;static unsigned char*view=nullptr;
   if(ram){if(!mapping){mapping=CreateFileMappingA(INVALID_HANDLE_VALUE,nullptr,PAGE_READWRITE,0,64*1024*1024,"Local\\CIRCUIT-phase20l-exact-state");view=(unsigned char*)MapViewOfFile(mapping,FILE_MAP_ALL_ACCESS,0,0,64*1024*1024);}if(!view)fail("STATE_MAPPING",c,MemArea_X,0);}
   else{out=fopen(fn.c_str(),op=="STATEWRITE"?"wb":"rb");if(!out)fail("STATE_FILE",c,MemArea_X,0);}
   uint64_t offset=0,diff=0;
   auto part=[&](const void*p,size_t size){if(offset+size>64*1024*1024)fail("STATE_SIZE",c,MemArea_X,0);if(op=="STATEWRITE"){if(ram)memcpy(view+offset,p,size);else fwrite(p,1,size,out);}else{std::vector<unsigned char>b;if(!ram){b.resize(size);if(fread(b.data(),1,size,out)!=size)fail("STATE_SHORT",c,MemArea_X,0);}auto*expected=ram?view+offset:b.data();auto*q=(const unsigned char*)p;if(memcmp(q,expected,size))for(size_t i=0;i<size;++i)if(q[i]!=expected[i]){if(diff<8)printf("STATE_DIFF byte=%llu expected=%02x actual=%02x\n",(unsigned long long)(offset+i),expected[i],q[i]);++diff;}}offset+=size;};
   for(int k=0;k<2;++k)for(auto a:{MemArea_X,MemArea_Y})part(mems[k]->getMemAreaPtr(a),0x80000*sizeof(TWord));
   part(shared.data(),shared.size()*sizeof(TWord));
   for(auto&r:regions){part(r.words.data(),r.words.size()*sizeof(TWord));part(r.known.data(),r.known.size());}
   // Full architectural register set supported by the interpreter, excluding
   // performance counters. Unused popped stack slots are not live state.
   for(int k=0;k<2;++k)for(int r=0;r<int(Reg_HIT);++r){int64_t v=0;if(dsps[k]->readRegToInt(EReg(r),v))part(&v,sizeof(v));}
   uint64_t count=exactTraffic.size();part(&count,sizeof(count));part(exactTraffic.data(),count*sizeof(TWord));exactTraffic.clear();
   if(out)fclose(out);printf("STATE %u bytes=%llu differences=%llu\n",block,(unsigned long long)offset,(unsigned long long)diff);fflush(stdout);
  }
  else if(op=="REGION"){std::string name;s>>name;auto lo=number(),hi=number(),mask=number();regions.emplace_back(name,lo,hi,mask);}
  else if(op=="P"||op=="X"||op=="Y"){TWord a=number();std::string v;auto area=op=="P"?MemArea_P:op=="X"?MemArea_X:MemArea_Y;while(s>>v)mems[c]->set(area,a++,strtoul(v.c_str(),nullptr,16));}
  else if(op=="RUN"||op=="COUPLE"){
   // Prime fibers to their first fetch (no instruction has executed).
   if(!fetches[c])step(c);
   if(op=="COUPLE"&&!fetches[1-c])step(1-c);
   uint64_t n=0;while(dsps[c]->getPC().toWord()!=stop&&n<limit){step(c);if(op=="COUPLE")step(1-c);++n;}
   printf("RAN %llu core=%d pc=%06x peer=%06x fetch=%llu,%llu\n",(unsigned long long)n,c,dsps[c]->getPC().toWord(),dsps[1-c]->getPC().toWord(),(unsigned long long)fetches[0],(unsigned long long)fetches[1]);fflush(stdout);
   if(n==limit)fail("DEADLOCK_OR_INSTRUCTION_LIMIT",c,MemArea_P,stop);
  }
  else if(op=="CHECK"){for(auto&r:regions)r.check();if(shared.front()!=0x5a1234||shared.back()!=0x5a1234)fail("SHARED_CANARY",c,MemArea_X,0x30000);for(TWord a=freeStart;a<0x4000;++a)if(mems[0]->getMemAreaPtr(MemArea_P)[a]!=0x5a1234)fail("P_CANARY",0,MemArea_P,a);printf("CHECK %u OK\n",block);}
  else if(op=="DUMPX"||op=="DUMPY"||op=="DUMPP"){TWord a=number(),n;s>>n;printf("%d %c %06x:",c,op[4],a);auto area=op[4]=='X'?MemArea_X:op[4]=='Y'?MemArea_Y:MemArea_P;for(TWord i=0;i<n;++i)printf(" %06x",mems[c]->get(area,a+i));printf("\n");}
  else if(op=="SUMMARY"){printf("SUMMARY block=%u pwrite=%llu accesses=%llu icc=%llu,%llu vpre=%llu c1contract=%llu gather=%llu,%llu,%llu hash=%llx,%llx,%llx,%llx\n",block,(unsigned long long)pwrites,(unsigned long long)accesses,(unsigned long long)iccReads,(unsigned long long)iccWrites,(unsigned long long)contractChecks,(unsigned long long)c1Checks,(unsigned long long)issued,(unsigned long long)completed,(unsigned long long)consumed,(unsigned long long)hashes[0],(unsigned long long)hashes[1],(unsigned long long)hashes[2],(unsigned long long)hashes[3]);}
  else fail("UNKNOWN_COMMAND",c,MemArea_P,0);
 }
 for(int c1=0;c1<2;++c1){std::string fn="pc"+std::to_string(c1)+".txt";FILE*out=fopen(fn.c_str(),"w");for(auto&kv:pcs[c1])fprintf(out,"%06x %llu\n",kv.first,(unsigned long long)kv.second);fclose(out);}
 if(trace)fclose(trace);if(stageFile)fclose(stageFile);return 0;
}
