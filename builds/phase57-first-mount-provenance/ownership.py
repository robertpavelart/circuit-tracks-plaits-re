"""Existing owners first: exact-byte field accesses and reset/constructor provenance."""
from pathlib import Path
import sys,json,struct,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase46-msd-filesystem-closure'))
import inspect_storage as src
from capstone.arm import ARM_OP_MEM,ARM_OP_IMM,ARM_OP_REG,ARM_REG_PC
S=0x20044d70
RANGES=[(0x0806b6cc,0x7c,'getter'),(0x0806b748,0x50,'watch'),(0x0806b798,0xb8,'admission'),
 (0x0806b850,0x220,'raw-command'),(0x0806bc30,0x20,'corrected-terminal')]
def accesses(a,n,owner):
    regs={};rows=[]
    for i in src.md.disasm(src.app[a-0x08010000:a-0x08010000+n],a):
        ops=i.operands
        for o in ops:
            if o.type==ARM_OP_MEM and o.mem.base in regs and not o.mem.index:
                at=regs[o.mem.base]+o.mem.disp
                if S<=at<S+12:
                    width=1 if i.mnemonic.startswith(('ldrb','strb')) else 2 if i.mnemonic.startswith(('ldrh','strh')) else 4
                    rows.append(dict(pc=hex(i.address),owner=owner,instruction=i.mnemonic+' '+i.op_str,
                        access='write' if i.mnemonic.startswith('str') else 'read',address=hex(at),bytes=width,
                        scope='Known owner linear constant-propagation candidate; branch reachability checked separately'))
        _,writes=i.regs_access();new={}
        if len(ops)>=2 and ops[0].type==ARM_OP_REG:
            d=ops[0].reg
            if i.mnemonic=='movw':new[d]=ops[1].imm
            elif i.mnemonic=='movt' and d in regs:new[d]=(regs[d]&65535)|(ops[1].imm<<16)
            elif i.mnemonic in ('mov','mov.w') and ops[1].type==ARM_OP_REG and ops[1].reg in regs:new[d]=regs[ops[1].reg]
            elif i.mnemonic.startswith('ldr') and ops[1].type==ARM_OP_MEM and ops[1].mem.base==ARM_REG_PC:
                p=((i.address+4)&~3)+ops[1].mem.disp
                if 0x08010000<=p<=0x08010000+len(src.app)-4:new[d]=struct.unpack_from('<I',src.app,p-0x08010000)[0]
        for r in writes:regs.pop(r,None)
        regs.update(new)
        if i.mnemonic in ('bl','blx'):
            for r in list(regs):
                if i.reg_name(r) in ('r0','r1','r2','r3','ip'):regs.pop(r,None)
    return rows
def main():
    rows=[r for a,n,o in RANGES for r in accesses(a,n,o)]
    ledger=[]
    meanings=['magic0','magic1','magic2','magic3','IDLE/ACTIVE/SUCCESS/FAILED','session','chunk','buffer owner','start-tick0','start-tick1','start-tick2','start-tick3']
    for j in range(12):
        addr=S+j
        ledger.append(dict(address=hex(addr),meaning=meanings[j],
            readers=[r['pc'] for r in rows if r['access']=='read' and int(r['address'],16)<=addr<int(r['address'],16)+r['bytes']],
            writer_candidates=[r['pc'] for r in rows if r['access']=='write' and int(r['address'],16)<=addr<int(r['address'],16)+r['bytes']]))
    constructors=[]
    for a in range(0x0805b5b8,0x0805b5e0,4):
        relative=struct.unpack_from('<I',src.app,a-0x08010000)[0]
        constructors.append(dict(record=hex(a),target=hex((a+relative)&0xffffffff)))
    r=dict(confidence='PROVEN',scope='Exact existing-owner accesses, not complete indirect/global liveness',
        image_sha256=hashlib.sha256(src.app).hexdigest(),region=['0x20044d70','0x20044d7b'],accesses=rows,byte_ledger=ledger,
        unreachable_legacy_success_store='0x0806b9ec: bypassed by corrected branch at0x0806b9dc',
        constructor_table=dict(start='0x0805b5b8',end_exclusive='0x0805b5e0',entries=constructors),
        scatter_zero=dict(handler='0x0801a7ea',record='0x0805b7b8',start='0x20003d04',bytes=0x2d50,end_exclusive=hex(0x20003d04+0x2d50),overlaps_private_state=False),
        initialized_data=src.descriptor,
        first_Main_task_direct_call_order=['0x0801ec80 (identity)','0x0801eeaa ->0x08025ac6 (peripheral/display path)','0x0801f0a8 (NOR then SD mount)'],
        pre_Main_tasks_constructor='0x0801ddd4',content_queue_constructor='0x08022a0c ->0x080366e0',
        complete_reset_to_first_mount=False,complete_old_owner_alias_proof=False)
    (OUT/'ownership.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(access_candidates=len(rows),bytes=len(ledger),constructors=len(constructors))))
if __name__=='__main__':main()
