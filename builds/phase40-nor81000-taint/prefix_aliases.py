"""Authentic prefix re-observation for pointer escapes only; no array service.

Does not install RAM hooks, fill the raw record, or run a completion fixture.
"""
from pathlib import Path
import sys, json, struct
sys.dont_write_bytecode = True
O = Path(__file__).resolve().parent
R = O.parents[1]
sys.path.insert(0, str(R / 'builds/phase38-nor81000'))
from request_trace import ReadTrace, run
from support import sha

class Aliases(ReadTrace):
    def finalize(self, u, stop):
        super().finalize(u, stop)
        raw = bytes(u.mem_read(0x20000000, 0x50000))
        needle = struct.pack('<I', 0x2000546c)
        self.aliases = [hex(0x20000000+i) for i in range(len(raw)-3)
                        if raw[i:i+4] == needle]
        self.publications = {hex(a): hex(int.from_bytes(u.mem_read(a,4),'little'))
                             for a in (0x200004a4, 0x20000984, 0x400264c4)}

if __name__ == '__main__':
    rows = []
    for variant in ('stock', 'diagnostic'):
        m = Aliases()
        row = run('bootloader', variant, clock_model=True, nor_init=True,
                  nor_identity=True, tick_model=True, limit=600000, svc_model=m)
        prior = json.loads((R/f'builds/phase38-nor81000/{variant}-request.json').read_text())
        assert row['stop'] == prior['stop']
        assert row['RAM_sha256'] == prior['RAM_sha256']
        assert m.final_state == prior['final_architecture']
        out = dict(variant=variant, confidence='PROVEN', stop=row['stop'],
                   instructions=row['instructions'], RAM_sha256=row['RAM_sha256'],
                   same_prior_checkpoint=True, SRAM_pointer_occurrences=m.aliases,
                   publications=m.publications, architecture=m.final_state,
                   NOR_commands=row['NOR_commands'], target_counts=row['target_counts_observed_prefix'],
                   completion_executed=False, payload_assigned=False,
                   scope='Pre-completion aliases; raw DMA bytes not supplied or consumed')
        (O/f'{variant}-prefix.json').write_text(json.dumps(out,indent=2)+'\n')
        rows.append(out)
        print(variant, m.aliases, m.publications, flush=True)
    assert rows[0]['SRAM_pointer_occurrences'] == rows[1]['SRAM_pointer_occurrences']
    assert rows[0]['architecture'] == rows[1]['architecture']
    assert rows[0]['NOR_commands'] == rows[1]['NOR_commands']
    print('stock/diagnostic prefix equivalent; no read completion', flush=True)
