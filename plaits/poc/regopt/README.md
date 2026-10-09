# Exact standalone VariableSaw REGOPT

Offline synthetic program only. MIT notices remain in ../LICENSE; sealed core,
assembler, upstream and baseline sources stay unchanged.

Preferred:generate_final.py, runner_final.cpp, final_sources/CMakeLists.txt,
build_final.ps1, collect_final.py. Native DIV suffix is identical to the baseline.
First candidate:generate_opt.py, runner.cpp, core-probe/register-candidate.

CFG allocation retains16 scratch words in Y1/R1..7/N0..7, with3 short X spills.
Refinement proves A0=0 before removing reloads, retains A1 boundaries otherwise,
and folds only dead X0 constant preparation. Host guards verify deleted word
boundaries and helper register preservation. No arithmetic/event order change.

extended.py compares golden and optimized focused stress twice. timing_opt.py
reuses the frozen timing rules with documented immediate CMP forms. Completed
liveness is reused by report.py; stress_summary.py/finalize.py include the larger
focused peak in final scaling. No renderer/liveness rerun on continuation.

442P,7 persistentX,3 spillX+16 registers,3 inputX,32 outputY,0LUT, stackpeak3.
Matched mean7270.1787 cycles (-22.1511% STRONG), all-validated max12670,
structural upper23902. Conditional estimates, no physical timing or integration.

Report/commands:notes/plaits-register-optimization.md. Canonical delivery:
builds/phase20a-regopt/final-report/; numerical evidence:final/, extended/.
