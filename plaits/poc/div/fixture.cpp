// Reuse untouched fallback assembler/deny-peripheral definitions, not its main.
#define main fallback_main
#include "../runner.cpp"
#undef main
int main(int argc,char**argv)try{
 std::set_terminate([](){std::fprintf(stderr,"DIV fixture rejected execution\n");std::_Exit(9);});
 if(argc!=4)throw std::runtime_error("assembly inputs.tsv fresh-output");
 const auto root=fs::path(__FILE__).parent_path().parent_path().parent_path().parent_path();
 const auto base=fs::weakly_canonical(root/"builds/phase20a-div"),out=fs::weakly_canonical(fs::absolute(argv[3]));
 auto rel=out.lexically_relative(base);
 if(rel.empty()||*rel.begin()==".."||fs::exists(out))throw std::runtime_error("Fresh DIV output required");
 Program p(argv[1]);std::ifstream input(argv[2]);if(!input)throw std::runtime_error("Input missing");
 fs::create_directories(out);
 std::ofstream states(out/"iterations.bin",std::ios::binary),results(out/"results.csv");
 results<<"id,n,d,initial_c,quotient,issued,div_count,SR,accumulator\n";
 {std::ofstream f(out/"program.be24",std::ios::binary);for(auto w:p.words)word24(f,w);}
 {std::ofstream f(out/"labels.json");f<<'{';bool first=true;for(auto [n,pc]:p.labels){if(!first)f<<',';first=false;f<<'"'<<n<<"\":"<<pc;}f<<"}\n";}
 DefaultMemoryValidator validator;Memory mem(validator,0x1000);mem.setExternalMemory(0x1000000,true);
 mem.replayRead=[&](auto area,auto at)->TWord{
  if(area!=MemArea_P)throw std::runtime_error("Data read forbidden");
  if(at==0||at==1||at==p.done||at==p.done+1)return 0;
  if(at<p.origin||at>=p.done)throw std::runtime_error("Unmapped P");return p.words[at-p.origin];};
 mem.replayWrite=[](auto,auto,auto){throw std::runtime_error("Memory write forbidden");};
 Deny px,py;DSP cpu(mem,&px,&py);px.constructing=py.constructing=false;
 unsigned issued=0,divs=0;
 cpu.setReplayBefore([&](auto pc,auto){
  if(!p.instructions.count(pc)||++issued>150)throw std::runtime_error("Instruction bound");
  const auto&s=p.instructions.at(pc);
  if(s=="div y0,a"||s=="move a0,a"){
   uint64_t acc=cpu.readRegs().a.var>>8;uint32_t sr=cpu.getSR().var;
   states.write(reinterpret_cast<char*>(&acc),8);states.write(reinterpret_cast<char*>(&sr),4);
   if(s=="div y0,a")++divs;
  }
 });
 unsigned id,n,d,c;
 while(input>>id>>n>>d>>c){
  if(n>0x7fffff||d>0x7fffff||c>1||(d&&uint64_t(n)>=4ull*d))throw std::runtime_error("Bad fixture domain");
  cpu.writeReg(Reg_SR,TReg24(0x300|c));cpu.writeReg(Reg_OMR,TReg24(0));
  cpu.writeReg(Reg_SP,TReg24(0));cpu.writeReg(Reg_SC,TReg5(0));
  cpu.writeReg(Reg_X0,TReg24(n));cpu.writeReg(Reg_Y0,TReg24(d));
  issued=divs=0;cpu.setPC(p.origin);while(cpu.getPC().var!=p.done)cpu.execInterpreter();
  if(cpu.readRegs().sc.var)throw std::runtime_error("Stack not restored");
  auto acc=cpu.readRegs().a.var>>8;
  results<<id<<','<<n<<','<<d<<','<<c<<','<<signed24(TWord(acc>>24))<<','<<issued<<','<<divs<<','<<cpu.getSR().var<<','<<acc<<'\n';
 }
 return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 9;}
