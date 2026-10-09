// Independent 24-bit data model, manual opcode fields and long-X differential.
// No stock memory/image/boot/peripherals; sealed interpreter only.
struct FixtureResult{TWord data,sr,sc,sp,x0,y0;uint64_t a,b;};
FixtureResult fixtureExecute(const std::string&s,TWord value,bool read,unsigned sr){
 Assembler assembler;auto op=qualifiedAssemble(assembler,s);if(!op.success()||op.wordCount!=2)throw std::runtime_error("Fixture assembly "+s+" error="+std::to_string(int(op.error)));
 bool isp=s.find("p:")!=std::string::npos;
 if(isp){unsigned reg=s.find(",x0")!=std::string::npos?4:s.find(",y0")!=std::string::npos?6:14;
  TWord expected=(read?0x07f080:0x077080)|reg;
  if(op.word[0]!=expected||op.word[1]!=0x2d29)throw std::runtime_error("FM MOVEM encoding mismatch");}
 DefaultMemoryValidator validator;Memory mem(validator,0x4000);mem.setExternalMemory(0x1000000,true);
 TWord data=value;bool live=false;
 mem.replayRead=[&](EMemArea area,TWord at)->TWord{
  if(area==MemArea_P){if(at==0||at==1||at==0x202||at==0x203)return 0;if(at==0x200)return op.word[0];if(at==0x201)return op.word[1];if(isp&&at==0x2d29)return data;}
  if(!isp&&area==MemArea_X&&at==0x20)return data;
  throw std::runtime_error("Fixture unowned read");};
 mem.replayWrite=[&](EMemArea area,TWord at,TWord v){if(!live||read||area!=(isp?MemArea_P:MemArea_X)||at!=(isp?0x2d29:0x20))throw std::runtime_error("Fixture unowned write");data=v&0xffffff;};
 Deny px,py;DSP cpu(mem,&px,&py);px.constructing=py.constructing=false;
 cpu.writeReg(Reg_SR,TReg24(sr));cpu.writeReg(Reg_A0,TReg24(0x654321));cpu.writeReg(Reg_A1,TReg24(value));cpu.writeReg(Reg_A2,TReg8(value&0x800000?0xff:0));
 cpu.writeReg(Reg_B0,TReg24(0x112233));cpu.writeReg(Reg_B1,TReg24(0x234567));cpu.writeReg(Reg_B2,TReg8(0));
 cpu.writeReg(Reg_X0,TReg24(0x123456));cpu.writeReg(Reg_Y0,TReg24(0x345678));
 live=true;cpu.setPC(0x200);cpu.execInterpreter();
 if(cpu.getPC().var!=0x202)throw std::runtime_error("Fixture PC increment");
 const auto&r=cpu.readRegs();
 TReg24 rs,rx,ry;cpu.readReg(Reg_SR,rs);cpu.readReg(Reg_X0,rx);cpu.readReg(Reg_Y0,ry);
 return {data,TWord(rs.var),TWord(r.sc.var),TWord(r.sp.var),TWord(rx.var),TWord(ry.var),uint64_t(r.a.var),uint64_t(r.b.var)};
}
int fixtures(const fs::path&out){
 const auto base=fs::weakly_canonical(fs::path(PSTATE_ROOT)/"builds/phase20c-pstate"),dest=fs::weakly_canonical(fs::absolute(out));
 auto rel=dest.lexically_relative(base);if(rel.empty()||*rel.begin()==".."||fs::exists(dest))throw std::runtime_error("Fresh fixture output required");fs::create_directories(dest);
 std::ofstream f(dest/"movem-fixtures.csv");f<<"value,initial_SR,operation,opcode,expected_word,actual_word,CCR_equal,all_checked_registers_equal\n";
 std::vector<TWord>values={0,1,0x7fffff,0x800000,0xffffff,0x200000,41943,0x123456};TWord seed=0x56300;
 for(unsigned i=0;i<128;++i){seed=(1664525u*seed+1013904223u)&0xffffff;values.push_back(seed);}
 unsigned count=0;
 for(auto value:values)for(unsigned sr:{0x300u,0x30fu,0x340u,0x3c0u})for(auto spec:{"a","x0","y0","store-a"}){
  bool read=std::string(spec)!="store-a";std::string r=read?spec:"a";
  auto ps=read?"movem p:>$002d29,"+r:"movem a,p:>$002d29";
  auto xs=read?"move x:>$000020,"+r:"move a,x:>$000020";
  auto p=fixtureExecute(ps,value,read,sr),x=fixtureExecute(xs,value,read,sr);
  // Independent memory word/model. A read sign extends the 24-bit word into
  // A2:A1, clears A0; core's 56-bit accumulator is left aligned by 8 bits.
  uint64_t expectedA=read&&r=="a"?uint64_t(int64_t(signed24(value))*0x100000000ll):(uint64_t(value&0x800000?0xff:0)<<56)|(uint64_t(value)<<32)|(uint64_t(0x654321)<<8);
  if(p.data!=value||p.a!=expectedA||(read&&r=="x0"&&p.x0!=value)||(read&&r=="y0"&&p.y0!=value))throw std::runtime_error("Independent 24-bit model mismatch");
  if(p.data!=x.data||p.sr!=x.sr||p.sc!=x.sc||p.sp!=x.sp||p.x0!=x.x0||p.y0!=x.y0||p.a!=x.a||p.b!=x.b)throw std::runtime_error("P/X fixture differential mismatch");
  Assembler assembler;auto op=qualifiedAssemble(assembler,ps);f<<value<<','<<sr<<','<<spec<<','<<op.word[0]<<','<<value<<','<<p.data<<",true,true\n";++count;
 }
 std::ofstream j(dest/"result.json");j<<"{\"fixtures\":"<<count<<",\"manual_encoding_matches\":true,\"independent_raw24_model_matches\":true,\"long_X_differential_matches\":true,\"code_mutation_allowed\":false,\"stock_ownership_proved\":false}\n";
 return 0;
}
