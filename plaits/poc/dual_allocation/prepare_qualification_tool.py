"""Create an explicitly separate guarded replay tool from the prior utility."""
from pathlib import Path
from study import ROOT
out=ROOT/'builds/phase20h-budget-qualification';out.mkdir(exist_ok=True)
s=(ROOT/'plaits/poc/dual_allocation/replay.cpp').read_text()
s=s.replace('TWord pc=0;std::ofstream access;','TWord pc=0,freeTail=0x4000;std::ofstream access;')
s=s.replace('pc=at;});','pc=at;if(running&&at>=freeTail&&at<0x4000)throw std::runtime_error("Execution entered free P tail");});')
s=s.replace('else if(c=="MAX")s>>maximum;','else if(c=="MAX")s>>maximum;\n  else if(c=="FREETAIL"){std::string a;s>>a;freeTail=std::stoul(a,nullptr,16);}')
(out/'guarded-replay.cpp').write_text(s)
ps=(ROOT/'plaits/poc/dual_allocation/build.ps1').read_text().replace('builds/phase20g-dual-allocation/host','builds/phase20h-budget-qualification/host').replace('plaits/poc/dual_allocation/replay.cpp','builds/phase20h-budget-qualification/guarded-replay.cpp')
(out/'build-guarded.ps1').write_text(ps)
