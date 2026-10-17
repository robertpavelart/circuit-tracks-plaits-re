#include <cstdio>
#include <cmath>
#include <cstdint>
#include <vector>
#include <algorithm>
#include <chrono>
#include "plaits/dsp/voice.h"
#include "plaits/resources.h"
template<class E> void probe(int index,const char* name,const uint8_t* data=nullptr) {
  std::vector<uint64_t> arena(32768,0); stmlib::BufferAllocator a(arena.data(),arena.size()*8); E e{}; e.Init(&a); e.LoadUserData(data); e.Reset();
  size_t used=arena.size()*8-a.free(), init_high=0; auto bytes=reinterpret_cast<const uint8_t*>(arena.data()); for(size_t i=0;i<arena.size()*8;++i) if(bytes[i]) init_high=i+1; float out[24]={},aux[24]={}; bool env=false; double energy=0; size_t nonfinite=0; double max_us=0;
  for(int b=0;b<2048;++b) { plaits::EngineParameters p{}; p.note=24+(b%97); p.harmonics=(b%129)/128.f; p.timbre=((b*37)%129)/128.f; p.morph=((b*71)%129)/128.f; p.accent=.8f; p.trigger=(b%16==0)?5:((b%16<8)?4:0);
    auto start=std::chrono::steady_clock::now(); e.Render(p,out,aux,24,&env); auto end=std::chrono::steady_clock::now(); max_us=std::max(max_us,std::chrono::duration<double,std::micro>(end-start).count());
    for(int s=0;s<24;++s) { if(!std::isfinite(out[s])||!std::isfinite(aux[s])) ++nonfinite; else energy+=out[s]*out[s]+aux[s]*aux[s]; } }
  printf("%d,%s,%zu,%zu,%zu,%zu,%.9g,%.9g\n",index,name,sizeof(E),used,init_high,nonfinite,energy,max_us);
}
int main(){ printf("index,class,host_object_bytes,arena_bytes,init_high_nonzero_byte,nonfinite,energy,host_max_us_not_DSP_cycles\n");
probe<plaits::VirtualAnalogVCFEngine>(0,"VirtualAnalogVCFEngine",nullptr);
probe<plaits::PhaseDistortionEngine>(1,"PhaseDistortionEngine",nullptr);
probe<plaits::SixOpEngine>(2,"SixOpEngine",plaits::fm_patches_table[0]);
probe<plaits::SixOpEngine>(3,"SixOpEngine",plaits::fm_patches_table[1]);
probe<plaits::SixOpEngine>(4,"SixOpEngine",plaits::fm_patches_table[2]);
probe<plaits::WaveTerrainEngine>(5,"WaveTerrainEngine",nullptr);
probe<plaits::StringMachineEngine>(6,"StringMachineEngine",nullptr);
probe<plaits::ChiptuneEngine>(7,"ChiptuneEngine",nullptr);
probe<plaits::VirtualAnalogEngine>(8,"VirtualAnalogEngine",nullptr);
probe<plaits::WaveshapingEngine>(9,"WaveshapingEngine",nullptr);
probe<plaits::FMEngine>(10,"FMEngine",nullptr);
probe<plaits::GrainEngine>(11,"GrainEngine",nullptr);
probe<plaits::AdditiveEngine>(12,"AdditiveEngine",nullptr);
probe<plaits::WavetableEngine>(13,"WavetableEngine",nullptr);
probe<plaits::ChordEngine>(14,"ChordEngine",nullptr);
probe<plaits::SpeechEngine>(15,"SpeechEngine",nullptr);
probe<plaits::SwarmEngine>(16,"SwarmEngine",nullptr);
probe<plaits::NoiseEngine>(17,"NoiseEngine",nullptr);
probe<plaits::ParticleEngine>(18,"ParticleEngine",nullptr);
probe<plaits::StringEngine>(19,"StringEngine",nullptr);
probe<plaits::ModalEngine>(20,"ModalEngine",nullptr);
probe<plaits::BassDrumEngine>(21,"BassDrumEngine",nullptr);
probe<plaits::SnareDrumEngine>(22,"SnareDrumEngine",nullptr);
probe<plaits::HiHatEngine>(23,"HiHatEngine",nullptr);
printf("-1,Voice,%zu,0,0,0,0,0\n",sizeof(plaits::Voice));
return 0;}
