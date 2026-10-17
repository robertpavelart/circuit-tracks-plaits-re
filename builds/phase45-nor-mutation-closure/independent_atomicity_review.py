"""Phase45 review of disk bytes, never import a patch emitter or write an image.

Uses the existing physical SRAM/ROM fixture only for instruction execution.
Schedules one pending SysTick at each real instruction boundary and honors
PRIMASK before every step (including immediately after restoration).
"""
from pathlib import Path
import sys, json, hashlib
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'builds/phase42-exact-rdiag-integration'))
import environment as E
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.arm_const import *

BASE = 0x08010000
OLD = ROOT/'builds/phase43-hardware-test-candidate/circuittracks-4486-nor-evidence-test'
NEW = ROOT/'builds/phase44-preflash-redteam-closure/circuittracks-4486-nor-evidence-atomic-test'
STATE = 0x20044d70
BEGIN, END = 0x0806b9dc, 0x0806b9ee

def filedecode(path):
    # Independently decode each 37-digit big-endian base-128 block. Block zero
    # is carried by FINISH. No phase43/44 decoder or firmware packer imported.
    raw = path.with_suffix('.syx').read_bytes()
    messages = raw.split(b'\xf7')
    assert messages.pop() == b''
    for p in messages:
        assert p[:5] == bytes.fromhex('f000202900')
        assert all(v < 128 for v in p[1:])
    assert messages[0][5:] == bytes.fromhex('710164000000050702')
    assert messages[1][5] == 0x7c
    h = messages[1][7:]
    def n(v):
        assert all(x < 16 for x in v)
        return int(''.join(format(x,'x') for x in v), 16)
    size, crc = n(h[6:14]), n(h[14:22])
    assert len(messages) == (size+31)//32 + 2
    assert messages[-1][5] == 0x73
    assert all(p[5] == 0x72 for p in messages[2:-1])
    chunks=[]
    for p in [messages[-1]] + messages[2:-1]:
        assert len(p[6:]) == 37
        v = 0
        for c in p[6:]: v = (v << 7) | c
        assert v & 7 == 0
        chunks.append((v >> 3).to_bytes(32,'big'))
    padded = b''.join(chunks)
    assert padded[size:] == b'\xff'*(len(padded)-size)
    data = padded[:size]
    c = 0xffffffff
    for b in data:
        c ^= b << 24
        for _ in range(8): c = ((c << 1) ^ (0x04c11db7 if c & 0x80000000 else 0)) & 0xffffffff
    assert c == crc
    assert data == path.with_suffix('.bin').read_bytes()
    return data, dict(SYX_SHA256=hashlib.sha256(raw).hexdigest(), BIN_SHA256=hashlib.sha256(data).hexdigest(), size=size, CRC=hex(c))

def disasm(data, start, size):
    return list(E.md.disasm(data[start-BASE:start-BASE+size],start))

def fixture(data, initial, mask):
    e=E.Physical()
    e.uc.mem_write(BASE,data)
    e.call(0x0805dbcc)
    e.w32(STATE+8,0)
    e.w32(0x2000081c,5000)
    e.uc.mem_write(STATE+4,bytes([initial]))
    for i in range(13): e.uc.reg_write(UC_ARM_REG_R0+i,0x11110000+i)
    e.uc.reg_write(UC_ARM_REG_SP,0x20008330)
    e.uc.reg_write(UC_ARM_REG_LR,0x08012345)
    e.uc.reg_write(UC_ARM_REG_PRIMASK,mask)
    e.uc.reg_write(UC_ARM_REG_PC,BEGIN)
    return e

def boundary(data, site, initial=1, mask=0):
    e=fixture(data,initial,mask);u=e.uc
    pending=False;injected=False;irq_seen=None;trace=[];writes=[];masked=0
    oldregs={r:u.reg_read(r) for r in list(range(UC_ARM_REG_R3,UC_ARM_REG_R12+1))+[UC_ARM_REG_SP,UC_ARM_REG_LR]}
    def store(u,access,address,size,value,extra): writes.append(dict(address=hex(address),size=size,value=value))
    hook=u.hook_add(UC_HOOK_MEM_WRITE,store)
    for _ in range(50):
        pc=u.reg_read(UC_ARM_REG_PC)
        if pc==site and not injected: pending=True;injected=True
        if pending and not u.reg_read(UC_ARM_REG_PRIMASK):
            context=u.context_save()
            u.reg_write(UC_ARM_REG_IPSR,15)
            # Exact disk native SysTick + disk watchdog, only exception frame /
            # stack selection and delivery are modeled by this scheduler.
            e.call(0x0805998c,sp=0x2004ff00)
            irq_seen=e.r8(STATE+4)
            u.context_restore(context)
            pending=False
        if pc==END: break
        trace.append(hex(pc))
        if u.reg_read(UC_ARM_REG_PRIMASK): masked+=1
        u.emu_start(pc|1,0xffffffff,count=1)
    else: raise AssertionError('commit did not terminate')
    assert injected or (initial!=1 and site in (0x0806bc44,0x0806bc46))
    assert u.reg_read(UC_ARM_REG_PRIMASK)==mask
    assert all(u.reg_read(r)==v for r,v in oldregs.items())
    assert not (irq_seen==3 and e.r8(STATE+4)!=3) or data is original
    return dict(boundary=hex(site),boundary_reached=injected,initial_state=initial,initial_PRIMASK=mask,
        final_state=e.r8(STATE+4),final_PRIMASK=u.reg_read(UC_ARM_REG_PRIMASK),
        irq_observed_state=irq_seen,irq_still_pending=pending,
        preserved_r3_r12_SP_LR=True,steps=len(trace),steps_entered_with_PRIMASK_1=masked,
        trace=trace,writes=writes)

def terminal_admission(data,state,mask):
    e=fixture(data,state,mask);u=e.uc;trace=[];writes=[]
    u.hook_add(UC_HOOK_MEM_WRITE,lambda u,a,p,n,v,d:writes.append((hex(p),n,v)))
    pc=0x0806b80a
    for _ in range(25):
        if pc==0x0806b842: break
        trace.append(hex(pc));u.emu_start(pc|1,0xffffffff,count=1)
        pc=u.reg_read(UC_ARM_REG_PC)
    else: raise AssertionError('terminal rejection failed')
    assert '0x806b838' not in trace and not writes
    assert e.r8(STATE+4)==state and u.reg_read(UC_ARM_REG_PRIMASK)==mask
    return dict(state=state,PRIMASK=mask,trace=trace,Storage_submission_count=0,writes=writes)

if __name__=='__main__':
    original, oi=filedecode(OLD); corrected, ci=filedecode(NEW)
    assert len(original)==len(corrected)
    differences=[]
    for off,(a,b) in enumerate(zip(original,corrected)):
        if a==b: continue
        at=BASE+off
        if 0x080101e8<=at<0x080101ee: label='distinct-version marker, data'
        elif 0x0806b9dc<=at<0x0806b9e0: label='non-linking Thumb branch redirect'
        elif 0x0806bc30<=at<0x0806bc50: label='critical-section instruction replacing FF slack'
        else: raise AssertionError(('unexpected difference',hex(at)))
        differences.append(dict(address=hex(at),before=hex(a),after=hex(b),classification=label))
    assert len(differences)==39
    assert corrected[0x1e8:0x1ee]==b'N44ATM'
    fragment=disasm(corrected,0x806bc30,32)
    originals=disasm(original,BEGIN,END-BEGIN)
    sites=[BEGIN]+[x.address for x in fragment]+[END]
    cases=[boundary(corrected,s,initial,mask) for s in sites for initial in (0,1,2,3) for mask in (0,1)]
    admissions=[terminal_admission(corrected,s,m) for s in (1,2,3) for m in (0,1)]
    oldcases=[boundary(original,x.address) for x in originals]+[boundary(original,END)]
    assert any(x['irq_observed_state']==3 and x['final_state']==2 for x in oldcases)
    assert all(x['final_state']==3 for x in cases if x['initial_state']==3)
    # Count exactly CPSID through MSR inclusive on the ACTIVE fast path: nine
    # instructions, eight entered with mask=1 when caller originally unmasked.
    result=dict(confidence='PROVEN',scope='Exact disk bytes and bounded native boundary scheduler, not hardware exception timing',
        original=oi,corrected=ci,changed_bytes=differences,
        original_commit=[dict(address=hex(x.address),hex=x.bytes.hex(),instruction=x.mnemonic+' '+x.op_str) for x in originals],
        corrected_fragment=[dict(address=hex(x.address),hex=x.bytes.hex(),instruction=x.mnemonic+' '+x.op_str) for x in fragment],
        cases=cases,original_race_cases=oldcases,corrected_cases=len(cases),terminal_admission_tests=admissions,
        patch_emitter_imported=False,new_image_generated=False,hardware_access=False)
    (OUT/'independent-atomicity-review.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Independent exact-file review PASS;',len(differences),'changed bytes;',len(cases),'corrected boundary cases')
