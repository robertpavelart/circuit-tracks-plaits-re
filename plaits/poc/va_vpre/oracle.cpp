// Host-only oracle: actual pinned Voice, fixed MODEL=8, VA_VARIANT=2.
// Independent reference stream and FIFO adapter use separate Voice instances.
#include <cstdio>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <vector>
#include <array>
#include <deque>
#include <filesystem>
#define private public
#include "plaits/dsp/voice.h"
#undef private
namespace fs=std::filesystem;
struct Control {int block;float note,h,t,m,trigger,level;int mode;};
struct HostVoice {
 std::array<uint64_t,2050> arena{};plaits::Voice v{};size_t calls=0;bool reset_done=false;
 HostVoice(){arena.front()=0x51234abcdef67890ull;arena.back()=0x67890abcdef51234ull;stmlib::BufferAllocator a(arena.data()+1,16384);v.Init(&a);}
 void render(const Control&c,plaits::Voice::Frame*out){if(c.block>=2048&&!reset_done){stmlib::BufferAllocator a(arena.data()+1,16384);v.Init(&a);reset_done=true;}plaits::Patch p{};p.engine=8;p.note=0;p.harmonics=c.h;p.timbre=c.t;p.morph=c.m;p.decay=.4f;p.lpg_colour=.3f;
  p.frequency_modulation_amount=.08f;p.timbre_modulation_amount=.2f;p.morph_modulation_amount=-.2f;
  plaits::Modulations m{};m.note=c.note;m.trigger=c.trigger;m.level=c.level;m.trigger_patched=c.mode!=2;m.level_patched=c.mode==1;
  m.frequency_patched=(c.block/128)%2;m.timbre_patched=(c.block/256)%2;m.morph_patched=(c.block/384)%2;
  m.frequency=std::sin(c.block*.013f)*3.f;m.timbre=std::sin(c.block*.017f)*.4f;m.morph=std::cos(c.block*.011f)*.4f;
  v.Render(p,m,out,12);++calls;
  if(arena.front()!=0x51234abcdef67890ull||arena.back()!=0x67890abcdef51234ull)throw std::runtime_error("Host arena canary");
  if(v.active_engine()!=8)throw std::runtime_error("Unexpected model");
 }
 std::vector<uint32_t> state(){std::vector<uint32_t>o;auto f=[&](float x){uint32_t b;std::memcpy(&b,&x,4);o.push_back(b);};
  auto shape=[&](const plaits::VariableShapeOscillator&s){f(s.master_phase_);f(s.slave_phase_);f(s.next_sample_);f(s.previous_pw_);o.push_back(s.high_);f(s.master_frequency_);f(s.slave_frequency_);f(s.pw_);f(s.waveshape_);f(s.phase_modulation_);};
  auto&e=v.virtual_analog_engine_;shape(e.primary_);shape(e.auxiliary_);shape(e.sync_);
  auto&s=e.variable_saw_;f(s.phase_);f(s.next_sample_);f(s.previous_pw_);o.push_back(s.high_);f(s.frequency_);f(s.pw_);f(s.waveshape_);f(e.auxiliary_amount_);f(e.xmod_amount_);
  f(v.previous_note_);f(v.engine_cv_);o.push_back(v.trigger_state_);f(v.decay_envelope_.value_);f(v.lpg_envelope_.vactrol_state_);f(v.lpg_envelope_.gain_);f(v.lpg_envelope_.frequency_);f(v.lpg_envelope_.hf_bleed_);o.push_back(v.lpg_envelope_.ramp_up_);
  for(auto x:v.trigger_delay_line_)f(x);
  for(auto*p:{&v.out_post_processor_,&v.aux_post_processor_}){f(p->limiter_.peak_);f(p->lpg_.previous_gain_);auto&s=p->lpg_.filter_;f(s.g_);f(s.r_);f(s.h_);f(s.state_1_);f(s.state_2_);}
  o.push_back(uint32_t(v.trigger_delay_.write_ptr_));o.push_back(v.previous_engine_index_);o.push_back(v.engine_quantizer_.quantized_value_);o.push_back(v.reload_user_data_);return o;
 }
};
int main(int argc,char**argv)try{
 if(argc!=3)throw std::runtime_error("controls fresh-output");fs::path out=argv[2];if(fs::exists(out))throw std::runtime_error("Fresh oracle output");fs::create_directories(out);
 std::ifstream in(argv[1]);std::vector<Control>cs;Control c;while(in>>c.block>>c.note>>c.h>>c.t>>c.m>>c.trigger>>c.level>>c.mode)cs.push_back(c);if(cs.size()!=4096)throw std::runtime_error("4096 controls required");
 // A renders the natural original 12-sample stream without using the FIFO.
 HostVoice reference;std::vector<plaits::Voice::Frame>stream;std::vector<std::vector<uint32_t>>states;
 for(size_t sample=0;sample<cs.size()*32;sample+=12){plaits::Voice::Frame b[12];reference.render(cs[sample/32],b);stream.insert(stream.end(),b,b+12);states.push_back(reference.state());}
 // B requests 32 samples, reusing prior FIFO remainder, rendering full blocks only.
 HostVoice adapter;std::deque<plaits::Voice::Frame>fifo;size_t generated=0,index=0,compared=0;int maxerr=0;double sum=0,dc=0;
 std::ofstream blocks(out/"blocks.csv"),raw(out/"main_aux.i16",std::ios::binary);blocks<<"block,renders,fifo_remainder,state_equal,outputs_equal,arena_canaries\n";
 for(size_t b=0;b<cs.size();++b){int renders=0;while(fifo.size()<32){plaits::Voice::Frame frames[12];adapter.render(cs[generated/32],frames);generated+=12;for(auto x:frames)fifo.push_back(x);
    if(adapter.state()!=states.at(index++))throw std::runtime_error("Host state divergence");++renders;}
  for(int s=0;s<32;++s){auto a=fifo.front();fifo.pop_front();auto r=stream[b*32+s];for(auto e:{int(a.out)-int(r.out),int(a.aux)-int(r.aux)}){maxerr=std::max(maxerr,std::abs(e));sum+=double(e)*e;dc+=e;++compared;}raw.write(reinterpret_cast<char*>(&a),sizeof(a));}
  blocks<<b<<','<<renders<<','<<fifo.size()<<",1,1,1\n";
 }
 if(maxerr||reference.calls!=adapter.calls)throw std::runtime_error("Host FIFO mismatch");
 std::ofstream j(out/"verification.json");j<<"{\"blocks\":4096,\"model\":8,\"VA_VARIANT\":2,\"original_render_size\":12,\"render_calls\":"<<adapter.calls<<",\"sample_pairs\":131072,\"max_absolute_error_i16\":"<<maxerr<<",\"rms_error_i16\":"<<std::sqrt(sum/compared)<<",\"dc_error_i16\":"<<dc/compared<<",\"state_fields_compared_per_render\":"<<adapter.state().size()<<",\"state_transitions_exact\":true,\"host_arena_canaries\":true,\"DSP_implementation\":false,\"scope\":\"Pinned MSVC host Voice stream vs independent 12-to-32 FIFO scheduler; not ARM-vs-DSP fidelity\"}\n";
 std::cout<<"Pinned host FIFO exact: 4096 blocks, "<<adapter.calls<<" original render calls.\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 9;}
