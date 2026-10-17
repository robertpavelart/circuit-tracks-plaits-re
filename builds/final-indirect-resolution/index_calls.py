"""Halfword candidate xrefs: evidence candidates, not a function boundary proof."""
from inspect_bytes import A,O,listing
from capstone.arm import ARM_OP_IMM
import json
targets={0x803ca34,0x803caa4,0x803cade,0x803ca52,0x803cbd6,0x803cbf0,0x803cc16,0x803cc54,0x803ccfa,0x80499ac,0x80499e8,0x8022a5c,0x8022a46,0x801e538,0x80251e8,0x801cfa4,0x801d7d0,0x8037380}
index={};rows=[]
for at in range(0x8010000,0x8010000+len(A.image)-4,2):
    i=next(A.md.disasm(A.read(at,4),at,count=1),None)
    if not i or i.mnemonic not in ('bl','blx','b','b.w') or i.operands[0].type!=ARM_OP_IMM:continue
    target=i.operands[0].imm
    index.setdefault(hex(target),[]).append(dict(at=hex(at),instruction=i.mnemonic))
    if target in targets:
        rows.append(dict(target=hex(target),at=hex(at),instruction=i.mnemonic))
        if target not in (0x801cfa4,0x801d7d0):listing(max(at-72,0x8010000),80)
(O/'call-index.json').write_text(json.dumps(index,indent=2)+'\n')
(O/'focused-xrefs.json').write_text(json.dumps(rows,indent=2)+'\n')
print('indexed',sum(map(len,index.values())),'candidate branches;',len(rows),'focused sites')
