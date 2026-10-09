// Bounded whole-helper address projection. Original bytes, sealed19A core.
// Opaque prefix/data encodings are not recovered stock values.
#include "dsp56kEmu/dsp.h"
#define NOMINMAX
#include <windows.h>
#include <bcrypt.h>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
using namespace dsp56k;namespace fs=std::filesystem;
std::string hash(const std::vector<unsigned char>& b){BCRYPT_ALG_HANDLE a=nullptr;
 if(BCryptOpenAlgorithmProvider(&a,BCRYPT_SHA256_ALGORITHM,nullptr,0)<0)throw std::runtime_error("SHA provider");
 unsigned char d[32];auto s=BCryptHash(a,nullptr,0,const_cast<PUCHAR>(b.data()),ULONG(b.size()),d,32);BCryptCloseAlgorithmProvider(a,0);
 if(s<0)throw std::runtime_error("SHA failed");std::ostringstream o;o<<std::hex<<std::setfill('0');for(auto v:d)o<<std::setw(2)<<unsigned(v);return o.str();}
struct Cell{TWord backing;bool known;};
struct Case{int id,family,depth,encoding;TWord modifier;int inheritedLF;};
struct Bus{
 const std::vector<TWord>& p;std::ofstream& out;Case c;DSP* cpu=nullptr;TWord pc=0,op=0,base,coef,state,fill;
 unsigned count=0,peak=0;uint64_t& seq;std::map<TWord,Cell>x,y;
 std::map<TWord,unsigned> calls;std::vector<std::pair<TWord,TWord>> frames;
 std::set<TWord> controlReads;std::map<TWord,std::pair<unsigned,std::pair<TWord,TWord>>> loopEntries;
 TWord incomingLA,incomingLC;std::set<int>knownR;TWord previousPC=0xffffff;
 Bus(const std::vector<TWord>& pp,std::ofstream& o,Case cc,uint64_t& s):p(pp),out(o),c(cc),seq(s){
  base=c.family?0x19f0:0x1800;coef=c.family?0x1a30:0x1840;state=c.family?0x1ad0:0x18e0;fill=c.encoding?0x5a5a5a:0;
  incomingLA=c.encoding?0xab1234:0;incomingLC=c.encoding?0x512345:0;
  x[0x1d40]={base,true};x[0x1d41]={coef,true};x[0x1d42]={state,true};x[0x3a]={32,true};x[0x3b]={16,true};
  for(unsigned j=0;j<16;++j)y[base+32+j]={TWord(c.family?(j%2?0x2c24:0x2c02):(j%2?0x2cec:0x2ccc)),true};
 }
 bool contains(TWord a,TWord lo,TWord hi){return a>=lo&&a<hi;}
 int addressReg(EMemArea area,TWord at){
  const auto&r=cpu->readRegs();
  // Report all actual AGU candidates, rather than guessing a single register on parallel operations.
  for(int i=0;i<8;++i)if(r.r[i].var==at)return i;return -1;
 }
 void event(const char* t,EMemArea area,TWord at,Cell v){
  out<<"{\"type\":\""<<t<<"\",\"seq\":"<<seq++<<",\"case\":"<<c.id<<",\"count\":"<<count<<",\"PC\":"<<pc
   <<",\"opcode\":"<<op<<",\"space\":\""<<"PXY"[area]<<"\",\"address\":"<<at<<",\"value\":";
  if(v.known)out<<v.backing;else out<<"null";
  out<<",\"status\":\""<<(v.known?"PROVENANCE_VALUE":"SYMBOLIC_DATA")<<"\",\"R\":[";
  for(int i=0;i<8;++i){if(i)out<<',';if(knownR.count(i))out<<cpu->readRegs().r[i].var;else out<<"null";}out<<"],\"M\":[";
  for(int i=0;i<8;++i){if(i)out<<',';out<<cpu->readRegs().m[i].var;}out<<"],\"call_depth\":"<<frames.size()<<"}\n";
 }
 TWord read(EMemArea a,TWord at){
  if(a==MemArea_P){if(at>=p.size())throw std::runtime_error("Unloaded P");return p[at];}
  bool allowed=false;
  if(a==MemArea_X){allowed=x.count(at)||contains(at,0x1d43,0x1d53)||contains(at,0x2c02,0x2d0c);}
  else allowed=contains(at,base,base+64)||contains(at,coef,coef+160)||contains(at,state,state+128);
  if(!allowed)throw std::runtime_error("Read outside qualified local footprint");
  auto& mem=a==MemArea_X?x:y;if(!mem.count(at))mem[at]={fill,false};auto v=mem.at(at);
  bool control=pc==0x1f5c||pc==0x1f5e||pc==0x1f60||pc==0x1f68||pc==0x1f6a||pc==0x1f6c||pc==0x1f89||pc==0x1f85||pc==0x1f90||pc==0xca4;
  if(control&&!v.known)throw std::runtime_error("Symbolic data affects pointer/count");
  event("READ",a,at,v);return v.backing;
 }
 void write(EMemArea a,TWord at,TWord value){
  if(a==MemArea_P)throw std::runtime_error("P write forbidden");bool allowed=false;
  if(a==MemArea_X)allowed=contains(at,0x2c02,0x2d0c);
  else allowed=contains(at,base,base+16)||contains(at,base+48,base+64)||contains(at,state,state+128);
  if(!allowed)throw std::runtime_error("Write outside qualified footprint");
  Cell v{value&0xffffff,pc==0x1f6e||pc==0x1f6f};auto&mem=a==MemArea_X?x:y;
  mem[at]=v;event("WRITE",a,at,v);
 }
 void regs(const char* type){const auto&r=cpu->readRegs();
  out<<"{\"type\":\""<<type<<"\",\"seq\":"<<seq++<<",\"case\":"<<c.id<<",\"count\":"<<count<<",\"PC\":"<<pc
   <<",\"SP\":"<<r.sp.var<<",\"SC\":"<<unsigned(r.sc.var)<<",\"LF\":"<<((r.sr.var>>15)&1)
   <<",\"FV\":"<<((r.sr.var>>16)&1)<<",\"LA\":";
  if((r.sr.var>>15)&1)out<<r.la.var;else out<<"null";
  out<<",\"LC\":";if((r.sr.var>>15)&1)out<<r.lc.var;else out<<"null";
  out<<",\"R\":[";for(int i=0;i<8;++i){if(i)out<<',';if(knownR.count(i))out<<r.r[i].var;else out<<"null";}
  out<<"],\"call_depth\":"<<frames.size()<<"}\n";
 }
 void before(TWord at,TWord word){
  const std::map<TWord,int> defs={{0x1f5c,6},{0x1f5e,5},{0x1f60,4},{0x1f68,1},{0x1f6a,3},{0x1f70,0},{0x1f7e,2},{0x1f89,7}};
  if(defs.count(previousPC))knownR.insert(defs.at(previousPC));previousPC=at;pc=at;op=word;
  if(++count>20000)throw std::runtime_error("Instruction budget");
  const bool helper=at>=0x1f5c&&at<=0x1f9a,callee=at>=0xc9d&&at<=0xcb7;
  const TWord caller=c.family?0x1ee5:0x1e80;
  if(!helper&&!callee&&at!=caller)throw std::runtime_error("Unexpected qualified-function exit");
  if(p.at(at)!=word)throw std::runtime_error("Opcode identity");
  const auto&r=cpu->readRegs();if(r.sp.var<unsigned(c.depth)||r.sp.var>13||r.sc.var!=r.sp.var)throw std::runtime_error("Stack budget/consistency");
  peak=std::max(peak,unsigned(r.sp.var));
  regs("EXEC");
  if(at==caller||at==0x1f78||at==0x1f7f){
   TWord target=at==caller?0x1f5c:0xc9d,ret=at==caller?caller+2:at+1;
   frames.push_back({target,ret});++calls[at];
   out<<"{\"type\":\"CALL\",\"seq\":"<<seq++<<",\"case\":"<<c.id<<",\"PC\":"<<at<<",\"target\":"<<target<<",\"return\":"<<ret<<",\"pre_SP\":"<<r.sp.var<<"}\n";
  }
  if(at==0xcb7||at==0x1f9a){
   if(frames.empty())throw std::runtime_error("Missing proven return frame");
   const auto ret=frames.back().second;
   if(TWord(uint64_t(r.ss[r.sp.var&15].var)>>24)!=ret)throw std::runtime_error("Return frame mismatch");
   out<<"{\"type\":\"RETURN\",\"seq\":"<<seq++<<",\"case\":"<<c.id<<",\"PC\":"<<at<<",\"target\":"<<ret<<",\"pre_SP\":"<<r.sp.var<<"}\n";
   frames.pop_back();
  }
  if(at==0x1f6c||at==0x1f72||at==0x1f85||at==0x1f90||at==0xca4){
   unsigned n=at==0x1f72?16:at==0xca4?16:32;
   TWord end=at==0x1f6c?0x1f6f:at==0x1f72?0x1f98:at==0x1f85?0x1f87:at==0x1f90?0x1f97:0xcaf;
   out<<"{\"type\":\"DO\",\"seq\":"<<seq++<<",\"case\":"<<c.id<<",\"PC\":"<<at<<",\"iterations\":"<<n<<",\"LA\":"<<end<<",\"pre_SP\":"<<r.sp.var<<"}\n";
  }
 }
};
struct Deny:IPeripherals{bool constructing=true;Deny():IPeripherals(PeripheralType::PeripheralsNop){}
 TWord read(TWord,Instruction)override{throw std::runtime_error("Peripheral read refused");}
 const TWord*readAsPtr(TWord,Instruction)override{throw std::runtime_error("Pointer refused");}
 void write(TWord a,TWord v)override{if(!constructing||(a!=0xfffffe&&a!=0xffffff)||v)throw std::runtime_error("Peripheral write refused");}
 void reset()override{}void setSymbols(Disassembler&)const override{}void terminate()override{}};
int main(int argc,char**argv)try{
 static_assert(!g_useJIT,"Interpreter only");if(argc!=4)throw std::runtime_error("payload cases.tsv fresh-trace");
 auto root=fs::path(__FILE__).parent_path().parent_path().parent_path().parent_path();
 auto rel=fs::weakly_canonical(fs::absolute(argv[3])).lexically_relative(fs::weakly_canonical(root/"builds/phase19c-fullhelper"));
 if(rel.empty()||*rel.begin()==".."||fs::exists(argv[3]))throw std::runtime_error("Fresh fullhelper trace required");
 std::ifstream in(argv[1],std::ios::binary);if(!in)throw std::runtime_error("Input missing");
 const std::vector<unsigned char>bytes{std::istreambuf_iterator<char>(in),{}};
 if(bytes.size()!=32538||hash(bytes)!="b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855")throw std::runtime_error("Original hash mismatch");
 std::vector<TWord>p;for(size_t i=0;i<bytes.size();i+=3)p.push_back((TWord(bytes[i])<<16)|(TWord(bytes[i+1])<<8)|bytes[i+2]);
 std::ifstream cases(argv[2]);if(!cases)throw std::runtime_error("Cases missing");std::ofstream out(argv[3]);uint64_t seq=0,total=0;Case c;
 while(cases>>c.id>>c.family>>c.depth>>c.encoding>>c.modifier>>c.inheritedLF){
  // Refine the finite architectural stack domain to extension-independent
  // healthy SP=SC prefix3..7, leaving enough room for caller+DO+JSR+DO.
  // Other classes are refused, not claimed impossible in normal firmware.
  if(c.family<0||c.family>1||c.depth<3||c.depth>7||c.encoding<0||c.encoding>1||
    (c.modifier!=0xffff&&c.modifier!=0x3ff)||c.inheritedLF!=0)throw std::runtime_error("Unqualified stack/loop/descriptor checkpoint");
  Bus bus(p,out,c,seq);DefaultMemoryValidator validator;Memory mem(validator,0x6000);mem.setExternalMemory(0x1000000,true);
  mem.replayRead=[&](auto a,auto at){return bus.read(a,at);};mem.replayWrite=[&](auto a,auto at,auto v){bus.write(a,at,v);};
  Deny px,py;DSP dsp(mem,&px,&py);bus.cpu=&dsp;px.constructing=py.constructing=false;
  // Unknown arithmetic backing: SR LF/FV/SC explicitly0 for admitted class;
  // other numerical modes are not material to addresses/branches.
  dsp.writeReg(Reg_SR,TReg24(c.encoding?0x300c00:0));dsp.writeReg(Reg_OMR,TReg24(0x400080|(c.encoding?0x100000:0)));
  dsp.writeReg(Reg_LA,TReg24(bus.incomingLA));dsp.writeReg(Reg_LC,TReg24(bus.incomingLC));
  for(int j=0;j<=c.depth;++j){dsp.writeReg(Reg_SP,TReg24(j));dsp.writeReg(Reg_SSH,TReg24(c.encoding?0x987600+j:0));dsp.writeReg(Reg_SSL,TReg24(c.encoding?0x123400+j:0));}
  dsp.writeReg(Reg_SP,TReg24(c.depth));dsp.writeReg(Reg_SC,TReg5(c.depth));
  const auto initialPrefix=dsp.readRegs().ss;
  for(int j=0;j<8;++j)dsp.writeReg(EReg(Reg_M0+j),TReg24(j==7?c.modifier:0xffff));
  TWord caller=c.family?0x1ee5:0x1e80,stop=caller+2;dsp.setPC(caller);
  dsp.setReplayBefore([&](auto at,auto op){bus.before(at,op);});
  while(dsp.getPC().var!=stop)dsp.execInterpreter();
  const auto&r=dsp.readRegs();
  if(!bus.frames.empty()||r.sp.var!=unsigned(c.depth)||r.sc.var!=c.depth||r.la.var!=bus.incomingLA||r.lc.var!=bus.incomingLC||(r.sr.var&0x18000))throw std::runtime_error("Stack/loop restoration mismatch");
  for(int j=0;j<=c.depth;++j)if(r.ss[j].var!=initialPrefix[j].var)throw std::runtime_error("Opaque prefix mutated");
  bus.pc=stop;bus.regs("FINAL");
  for(auto area:{MemArea_X,MemArea_Y})for(auto&item:area==MemArea_X?bus.x:bus.y)bus.event("FINAL_CELL",area,item.first,item.second);
  out<<"{\"type\":\"SUMMARY\",\"case\":"<<c.id<<",\"count\":"<<bus.count<<",\"peak_SP\":"<<bus.peak
   <<",\"opaque_prefix_preserved\":true,\"LA_LC_preserved\":true,\"return_PC\":"<<stop<<"}\n";
  total+=bus.count;
 }
 if(!cases.eof())throw std::runtime_error("Malformed cases");out.flush();std::cout<<total<<" original opcodes; complete helper returned\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}
