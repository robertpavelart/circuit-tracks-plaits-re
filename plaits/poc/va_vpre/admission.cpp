// Reuse the sealed interpreter fixture infrastructure, not its overlay main.
#define main unused_phase20d_overlay_entry
#include "../midi_vpre/runner.cpp"
#undef main
int main(int argc,char**argv)try{
 _CrtSetReportHook(reportHook);
 if(argc!=3)throw std::runtime_error("admission fixture fresh-output");
 fs::path f=argv[1],out=argv[2];if(fs::exists(out))throw std::runtime_error("Fresh output required");fs::create_directories(out);
 auto orig=load(f/"original-core0.be24"),red=load(f/"reduced-core0.be24");orig.resize(0x4000);red.resize(0x4000);
 // Three-word caller stub entirely in the original 19-word tail. No stock overlay.
 for(auto*p:{&orig,&red}){(*p)[0x3ff0]=0x0bf080;(*p)[0x3ff1]=0x336e;(*p)[0x3ff2]=0;}
 fs::create_directory(out/"original");fs::create_directory(out/"reduced");fs::create_directory(out/"restored");
 Machine base(orig,out/"original"),mod(red,out/"reduced"),restored(orig,out/"restored");
 auto seed=[](Machine&m){m.x[0x3a]=32;m.y[0xffd]=RING;int b=0x3bb0;m.x[b+8]=127;m.x[b+11]=0;m.x[b+16]=127;m.x[b+18]=1;m.x[b+19]=67;m.x[b+20]=2;m.x[b+21]=100;m.x[b+22]=1;m.x[b+42]=0x7f0000;m.x[0x3933]=64;m.x[0x3932]=84;
  for(auto a:{0x1ff,0x300})m.x[a]=0x5a1234;
  for(auto a:{0xfff,0x1040,0x7ff,0x840,0x10ff,0x1180})m.y[a]=0x6b2345;
 };
 for(auto*m:{&base,&mod,&restored})seed(*m);
 auto guards=[](Machine&m){for(auto a:{0x1ff,0x300})if(m.x[a]!=0x5a1234)throw std::runtime_error("Gain canary");for(auto a:{0xfff,0x1040,0x7ff,0x840,0x10ff,0x1180})if(m.y[a]!=0x6b2345)throw std::runtime_error("Ring/mixer/stem canary");};
 auto state=[](Machine&m){std::vector<TWord>v;for(auto b:{0x3bb0,0x3930,0x3990,0x3830,0x3870})for(int j=0;j<48;++j)v.push_back(m.x[b+j]);return v;};
 std::ifstream cases(f/"cases.tsv");std::ofstream csv(out/"blocks.csv"),samples(out/"midi2.i32",std::ios::binary);
 csv<<"block,original_instructions,reduced_instructions,original_nominal_cycles,reduced_nominal_cycles,original_vpre_instructions,reduced_vpre_instructions,original_vpre_cycles,reduced_vpre_cycles,state_equal,output_equal,restored_equal,caller_and_stack,canaries,mixer_same_instruction_path\n";
 int b,n;unsigned ad,w;size_t count=0,stateBad=0,outputBad=0,firstBad=4096,firstSample=4096*32;uint64_t hitsControl=0,hitsRender=0;
 while(cases>>b>>n){for(auto*m:{&base,&mod,&restored}){m->block=b;m->pcs.clear();m->callerFixture(b);for(int j=0;j<64;++j)m->y[RING+j]=(0x111*j+b)&0xffffff;}
  for(int j=0;j<n;++j){cases>>std::hex>>ad>>w>>std::dec;for(auto*m:{&base,&mod,&restored})m->x[ad]=w;}
  uint64_t ins[3],cyc[3],vins[3],vcyc[3];int k=0;
  for(auto*m:{&base,&mod,&restored}){auto caller=m->caller();ins[k]=m->cpu.getInstructionCounter();cyc[k]=m->cpu.getCycles();m->phase=1;m->run(0x3ff0,0x3ff2);guards(*m);if(m->caller()!=caller)throw std::runtime_error("Caller/modifier/stack regression");vins[k]=m->cpu.getInstructionCounter()-ins[k];vcyc[k]=m->cpu.getCycles()-cyc[k];++k;}
  // MIDI1 is disabled, so every executed oscillator island belongs to MIDI2.
  for(auto pc:base.pcs){hitsControl+=(pc>=0x36ad&&pc<0x3876);hitsRender+=(pc>=0x3999&&pc<0x3b82);}
  bool se=state(base)==state(mod),oe=true,re=state(base)==state(restored);
  for(int j=0;j<32;++j){int pos=RING+2*j+1;oe&=base.y[pos]==mod.y[pos];re&=base.y[pos]==restored.y[pos];if(base.y[pos]!=mod.y[pos]&&firstSample==4096*32)firstSample=b*32+j;for(auto*m:{&base,&mod,&restored}){int32_t v=s24(m->y[pos]);samples.write(reinterpret_cast<char*>(&v),4);}}
  stateBad+=!se;outputBad+=!oe;if((!se||!oe)&&firstBad==4096)firstBad=b;
  if(!re)throw std::runtime_error("Restoring legacy code failed exact regression");
  std::vector<std::vector<TWord>>mixpc;
  k=0;for(auto*m:{&base,&mod,&restored}){m->pcs.clear();m->strip();guards(*m);mixpc.push_back(m->pcs);ins[k]=m->cpu.getInstructionCounter()-ins[k];cyc[k]=m->cpu.getCycles()-cyc[k];++k;}
  if(mixpc[0]!=mixpc[1]||mixpc[0]!=mixpc[2])throw std::runtime_error("Stock mixer instruction path changed");
  for(int j=0;j<64;++j)if(base.y[0x800+j]!=restored.y[0x800+j])throw std::runtime_error("Restored mixer output differs");
  csv<<b<<','<<ins[0]<<','<<ins[1]<<','<<cyc[0]<<','<<cyc[1]<<','<<vins[0]<<','<<vins[1]<<','<<vcyc[0]<<','<<vcyc[1]<<','<<se<<','<<oe<<','<<re<<",1,1,1\n";++count;
 }
 if(count!=4096||stateBad==0||outputBad==0||hitsControl==0||hitsRender==0)throw std::runtime_error("Shared-deletion negative control not demonstrated");
 for(auto*m:{&base,&mod,&restored}){std::ofstream dis((m==&base?out/"original":m==&mod?out/"reduced":out/"restored")/"executed.asm");for(auto [pc,s]:m->dis)dis<<std::hex<<pc<<' '<<m->sizes[pc]<<' '<<s<<'\n';}
 std::ofstream sum(out/"native.json");sum<<"{\"blocks\":"<<count<<",\"midi2_state_mismatch_blocks\":"<<stateBad<<",\"midi2_output_mismatch_blocks\":"<<outputBad<<",\"first_mismatch_block\":"<<firstBad<<",\"first_sample_mismatch\":"<<firstSample<<",\"midi2_control_island_instructions\":"<<hitsControl<<",\"midi2_renderer_island_instructions\":"<<hitsRender<<",\"restored_legacy_exact_blocks\":4096,\"stock_overlays_used\":false,\"flash_container\":false}\n";
 std::cout<<"Admission rejected: MIDI2 state differs in "<<stateBad<<" blocks, samples differ in "<<outputBad<<" blocks; restored code exact.\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 9;}
