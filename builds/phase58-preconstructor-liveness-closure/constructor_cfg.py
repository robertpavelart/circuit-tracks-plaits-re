"""Recursive constructor CFG including unexecuted direct branches; explicit indirect premises."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase46-msd-filesystem-closure'))
import inspect_storage as src
from capstone.arm import *
from constructor_probe import WATCH
def main():
    observed=json.loads((OUT/'constructor-cases.json').read_text())['cases'][0]
    indirect={0x0805b986:set(),0x0802428e:set()}
    for c in observed['calls']:
        pc=int(c['pc'],16)
        if pc in indirect:indirect[pc].add(int(c['target'],16))
    pending=[0x0805b958];nodes={};unknown=[];edges=[];calls=[]
    def enqueue(a,kind,pc):
        a&=~1;edges.append(dict(source=hex(pc),target=hex(a),kind=kind))
        if 0x08010000<=a<0x08010000+len(src.app):pending.append(a)
        else:unknown.append(dict(pc=hex(pc),reason='target outside application',target=hex(a)))
    while pending and len(nodes)<20000:
        pc=pending.pop()
        if pc in nodes:continue
        i=next(src.md.disasm(src.app[pc-0x08010000:pc-0x08010000+4],pc,count=1),None)
        if not i:unknown.append(dict(pc=hex(pc),reason='decode failed'));continue
        nodes[pc]=i;nextpc=pc+i.size
        if i.id in (ARM_INS_BKPT,ARM_INS_UDF):continue
        if i.id in (ARM_INS_BL,ARM_INS_BLX):
            if i.operands[0].type==ARM_OP_IMM:
                enqueue(i.operands[0].imm,'call',pc);calls.append(dict(pc=hex(pc),target=hex(i.operands[0].imm&~1)))
            elif pc in indirect:
                for t in indirect[pc]:enqueue(t,'indirect with declared constant-source premise',pc)
            else:unknown.append(dict(pc=hex(pc),reason='unresolved indirect call',instruction=i.mnemonic+' '+i.op_str))
            pending.append(nextpc);continue
        if i.id in (ARM_INS_B,ARM_INS_CBZ,ARM_INS_CBNZ):
            targets=[o.imm for o in i.operands if o.type==ARM_OP_IMM]
            for t in targets:enqueue(t,'branch',pc)
            if i.id!=ARM_INS_B or i.cc not in (ARM_CC_AL,ARM_CC_INVALID):pending.append(nextpc)
            continue
        if i.id==ARM_INS_BX:
            if i.operands[0].reg!=ARM_REG_LR:unknown.append(dict(pc=hex(pc),reason='unresolved BX',instruction=i.op_str))
            continue
        if ARM_REG_PC in i.regs_access()[1]:
            if i.mnemonic.startswith(('pop','ldm')):continue
            unknown.append(dict(pc=hex(pc),reason='unresolved PC write',instruction=i.mnemonic+' '+i.op_str));continue
        if i.id in (ARM_INS_TBB,ARM_INS_TBH):unknown.append(dict(pc=hex(pc),reason='unresolved table branch'));continue
        pending.append(nextpc)
    assert not pending,'CFG cap reached'
    hits=[dict(pc=hex(p),kind=WATCH[p]) for p in nodes if p in WATCH]
    (OUT/'constructor-cfg.asm').write_text('\n'.join(f'{p:08X}: {i.mnemonic} {i.op_str}' for p,i in sorted(nodes.items()))+'\n')
    result=dict(confidence='PROVEN',scope='Static constructor CFG covers both direct branch arms; indirect targets rely on the explicitly identified immutable-table/constant-callback premises, not general indirect-flow resolution',
        instructions=len(nodes),edges=edges,direct_calls=calls,unresolved=unknown,relevant_operations=hits,
        indirect_premises={hex(pc):[hex(t) for t in sorted(ts)] for pc,ts in indirect.items()},
        premise_details={'0x0805b986':'relative constructor table0805B5B8..0805B5E0 is authenticated flash',
                         '0x0802428e':'generic element constructor callback; actual caller0801E49E supplies constant08037AAD; audited separately'},
        registered_future_callbacks_not_executed_here=True)
    result['failure_callback_startup_premise']=dict(pointer='0x20006a38',value_after_authenticated_BSS_clear=0,
        PCs=['0x0801cfaa','0x08037386'],reason='Optional allocation-failure callbacks; native11 allocations succeed well below either admitted limit. Not arbitrary callback resolution.')
    (OUT/'constructor-cfg.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(instructions=len(nodes),unresolved=unknown,relevant_operations=hits),indent=2))
if __name__=='__main__':main()
