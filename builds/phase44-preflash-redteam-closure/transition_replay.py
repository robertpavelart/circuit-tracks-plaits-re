"""Reuse the phase43 native runner with explicitly selected installed image.

No candidate rebuild, SYX output, hardware or live transport. The B1.3 rollback
stream is reconstructed IN MEMORY and admitted only on manifest SYX hash match.
Writes are limited to phase44 evidence. RTOS/peripheral seams stay explicit.
"""
from pathlib import Path
import sys, json, hashlib
sys.dont_write_bytecode = True
O = Path(__file__).resolve().parent
R = O.parents[1]
S = R / 'builds/phase43-hardware-test-candidate'
P = R / 'builds/phase42-exact-rdiag-integration'
sys.path.insert(0, str(P))
from environment import PUBLISHED, REF
sys.path.insert(0, str(S/'source/tools'))
import ct_fw

def run(which):
    atomic = '--atomic' in sys.argv
    candidate = ((O/'circuittracks-4486-nor-evidence-atomic-test.bin') if atomic else (S/'circuittracks-4486-nor-evidence-test.bin')).read_bytes()
    b13 = PUBLISHED[:]
    manifest = json.loads((REF/'firmware/b1.3/manifest.json').read_text())
    if which == 'b13-to-candidate':
        current = b13
        stream = ((O/'circuittracks-4486-nor-evidence-atomic-test.syx') if atomic else (S/'circuittracks-4486-nor-evidence-test.syx')).read_bytes()
    elif which == 'candidate-to-official':
        current = candidate
        stream = (S/'rollback/circuittracks-firmware-4486-STOCK.syx').read_bytes()
    elif which == 'candidate-to-b13':
        current = candidate
        stream = ct_fw.encode(b13)
        assert hashlib.sha256(stream).hexdigest() == manifest['syx_sha256']
    else:
        raise ValueError(which)
    src = (S/'install_exact_syx.py').read_text()
    src = src.replace("sys.path.insert(0,str(O))", "sys.path.insert(0,str(S))")
    src = src.replace("raw_SYX=(O/'circuittracks-4486-nor-evidence-test.syx').read_bytes()", "raw_SYX=STREAM")
    src = src.replace("sys.path.insert(0,str(O/'source/tools'))", "sys.path.insert(0,str(S/'source/tools'))")
    src = src.replace('e=Physical();u=e.uc;u.mem_write(0x08010000,image)',
        "e=Physical();u=e.uc;u.mem_write(0x08010000,b'\\xff'*0x70000);u.mem_write(0x08010000,CURRENT)")
    src = src.replace("assert hashlib.sha256(image).hexdigest()=='9b29180ff7f88c9c982c60abdfd5e5b296e8f2240ad57580366a5a7f797930a6'",
        "assert ct_fw.decode(raw_SYX)['image']==image")
    src = src.replace('u.mem_write(0x08010000,PUBLISHED[:])',
        "u.mem_write(0x08010000,b'\\xff'*0x70000);u.mem_write(0x08010000,CURRENT)")
    src = src.replace("(O/'installation.json').write_text", "(O/(WHICH+'-operations.json')).write_text")
    # Record all executed instruction PCs and selector/table bytes, without
    # skipping original native instructions or changing its address algorithm.
    src = src.replace('program={};reached={}', 'program={};reached={};executed=set();version_decisions=[]')
    src = src.replace('global app_crc,unpack_calls,worker_flag_checks',
        "global app_crc,unpack_calls,worker_flag_checks\n executed.add(pc)\n if pc in (0x08003ba6,0x08003bce,0x08003bf6):version_decisions.append(dict(pc=hex(pc),r0=hex(reg(0)),r1=hex(reg(1)),r2=hex(reg(2))))")
    src = src.replace("print(json.dumps({k:v for k,v in result.items() if k not in ('operations','internal_operations','native_message_log','native_request_records')},indent=2))", '')
    output_name = ('atomic-' if atomic else '') + which
    ns = dict(__file__=str(O/'transition_replay.py'), S=S, STREAM=stream,
              CURRENT=current, WHICH=output_name)
    exec(compile(src, str(S/'install_exact_syx.py')+'[phase44-selected-image]', 'exec'), ns)
    result = ns['result']
    ops = ns['ops']; internal = ns['internal']; executed = ns['executed']
    def ranges(kind, seq):
        intervals = sorted((int(x['start'],16),int(x['end_exclusive'],16)) for x in seq if x['kind']==kind)
        merged=[]
        for lo,hi in intervals:
            if merged and lo <= merged[-1][1]:merged[-1][1]=max(merged[-1][1],hi)
            else:merged.append([lo,hi])
        return [[hex(a),hex(b)] for a,b in merged]
    table = ns['u'].mem_read(0x08039180,0x100)
    # Native code equality recorded for executed halfwords, not broad name-based
    # assumptions that B1.3's updater equals stock.
    executed_app = sorted(pc for pc in executed if 0x08010000<=pc<0x08010000+len(current))
    app_code_hash = hashlib.sha256(b''.join(pc.to_bytes(4,'little')+current[pc-0x08010000:pc-0x08010000+2] for pc in executed_app)).hexdigest()
    summary = dict(transition=which,atomic_candidate=atomic,confidence='PROVEN',
        scope='Actual selected installed image native application updater and authenticated bootloader validator/installer; original phase43 RTOS/peripheral seams retained, not full cold boot or recovery intake',
        accepted=True,actual_install_performed=True,silent_noop=False,
        installed_before_sha256=hashlib.sha256(current).hexdigest(),incoming_SYX_sha256=hashlib.sha256(stream).hexdigest(),
        incoming_image_sha256=hashlib.sha256(ns['image']).hexdigest(),incoming_bytes=len(ns['image']),
        final_installed_sha256=hashlib.sha256(bytes(ns['u'].mem_read(0x08010000,len(ns['image'])))).hexdigest(),
        selector=0,staging_base='0x0',capacity='0x80000',
        external_erase_ranges=ranges('ERASE',ops),external_program_ranges=ranges('WRITE',ops),
        metadata=bytes(ns['nor'][0x80000:0x80017]).hex(),
        metadata_erase_range=['0x80000','0x81000'],metadata_program_range=['0x80000','0x80017'],
        staged_image_sha256=hashlib.sha256(bytes(ns['nor'][:len(ns['image'])])).hexdigest(),
        internal_erase_ranges=ranges('ERASE',internal),internal_program_ranges=ranges('WRITE',internal),
        exact_internal_erase_calls=[x for x in internal if x['kind']!='WRITE'],
        preservation=result['preservation'],version_decisions=ns['version_decisions'],
        executed_app_instruction_addresses=[hex(pc) for pc in executed_app],executed_app_halfwords_sha256=app_code_hash,
        b13_SYX_reconstructed_in_memory_only=(which=='candidate-to-b13'),hardware_access=False,candidate_regenerated=False,
        seams=result['gaps'])
    (O/(output_name+'-summary.json')).write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('executed_app_instruction_addresses','preservation')},indent=2),flush=True)

if __name__=='__main__':
    run(sys.argv[1])
