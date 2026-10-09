// Wrapper only: pinned Mutable Instruments VariableSaw header remains unchanged.
#define TEST 1
#include "plaits/dsp/oscillator/variable_saw_oscillator.h"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <cmath>
int main(int argc,char**argv)try{
 if(argc==2&&std::string(argv[1])=="--continuity"){
  plaits::VariableSawOscillator a,b;a.Init();b.Init();float t[32],u[32],x[64],y[64];
  for(int i=0;i<128;++i){a.Render(.007654f,.82f,.37f,t,32);b.Render(.007654f,.82f,.37f,u,32);}
  a.Render(.007654f,.82f,.37f,x,64);b.Render(.007654f,.82f,.37f,y,32);b.Render(.007654f,.82f,.37f,y+32,32);
  double e=0;for(int i=0;i<64;++i)e=std::max(e,std::abs(double(x[i])-y[i]));
  std::cout<<std::setprecision(17)<<"{\"steady64_vs_two32_max_difference\":"<<e<<"}\n";return 0;
 }
 if(argc==2&&std::string(argv[1])=="--info"){
  std::cout<<"{\"sizeof_VariableSawOscillator\":"<<sizeof(plaits::VariableSawOscillator)<<",\"float_bytes\":"<<sizeof(float)<<",\"upstream_source_modified\":false}\n";return 0;
 }
 if(argc!=3||std::filesystem::exists(argv[2]))return 2;
 std::ifstream in(argv[1]);std::ofstream out(argv[2],std::ios::binary);
 int id,block;double f,pw,shape;int last=-1;
 plaits::VariableSawOscillator osc;float v[32];
 while(in>>id>>block>>f>>pw>>shape){
  if(id!=last){osc.Init();last=id;}
  if(!(f>0&&std::isfinite(f)&&pw>=0&&pw<=1&&shape>=0&&shape<=1))return 3;
  osc.Render(float(f),float(pw),float(shape),v,32);
  for(float x:v)if(!std::isfinite(x))return 4;
  out.write(reinterpret_cast<char*>(v),sizeof(v));
 }
 return out?0:5;
}catch(const std::exception&e){std::cerr<<e.what();return 9;}
