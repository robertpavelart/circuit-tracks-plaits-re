"""Resume inherited startup model with only corrected candidate selected."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1]
src=(R/'builds/phase62-final-preflight/startup_continuity.py').read_text()
src=src.replace("c=json.loads((O/'frozen-candidate-identity.json').read_text())", "c=json.loads((O/'construction.json').read_text());c['candidate']='circuittracks-nor-defect-closure-development'")
extra="""
 src=src.replace('count=1000000','count=5000000').replace('range(300)','range(2000)')
 src=src.replace('watch.update({',"watch.update({0x0801cfa4:'allocation request',0x0801d7d8:'bounded allocator',0x0801e2da:'startup readiness predicate',0x08026fec:'display progress callback',")
 src=src.replace('counts[pc]+=1;last.append(pc)', 'counts[pc]+=1;last.append(pc)'+chr(10)+"        if sum(counts.values())>=next_tick[0] and not u.reg_read(UC_ARM_REG_IPSR) and not u.reg_read(UC_ARM_REG_PRIMASK) and not u.reg_read(UC_ARM_REG_BASEPRI):"+chr(10)+"            next_tick[0]=sum(counts.values())+10000;action[0]=('early-tick',pc);u.emu_stop();return")
 src=src.replace('injected_tick=False;injected_queue=False','injected_tick=False;injected_queue=False;next_tick=[120000]')
 src=src.replace("result['timer_records_at_frontier']", "result['startup_readiness_objects']={hex(a):dict(pointer=hex(e.r32(a)),bytes=bytes(u.mem_read(e.r32(a),48)).hex()) for a in (0x20000834,0x2000083c,0x20000848)};result['timer_records_at_frontier']")
"""
src=src.replace("exec(compile(src,str(O/'selected-corrected-startup-runner.py')", extra+"\n exec(compile(src,str(O/'selected-corrected-startup-runner.py')")
exec(compile(src,str(O/'selected-startup-continuity.py'),'exec'),dict(__file__=str(O/'startup_continuity.py'),__name__='__main__'))
