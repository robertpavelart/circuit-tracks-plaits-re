"""Offline normal-layout and rejection tests; no live acquisition."""
from pathlib import Path
import json,struct,hashlib
from geometry_parser import decode
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
REF=Path(r'C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main')

def main():
    ram=(REF/'ctre/Firmware-Analysis/ram_dump_firmware_0x08037988.bin').read_bytes()
    assert hashlib.sha256(ram).hexdigest()=='26a29670c0c1918217b7eadf8f89fe6df97994d3cc6e1c0ed65ac522e161094c'
    spans=[(0xa98,8),(0xab0,14),(0xad0,24)]
    record=b''.join(ram[a:a+n] for a,n in spans)
    ref=decode(record);assert ref['total_sectors']==7980
    assert all(not t['intersects_normal_writable_mapping'] for t in ref['targets'])
    passed=[dict(name='authenticated public reference RAM, NOT current unit',record_hex=record.hex(),result=ref)]
    old=json.loads((ROOT/'builds/phase48-current-unit-geometry/geometry-review.json').read_text())
    for c in old['bounded_normal_mount_cases']:
        b=bytearray(record);b[8]=c['FAT_type'];b[10]=c['FAT_count']
        struct.pack_into('<H',b,16,c['root_entries']);struct.pack_into('<H',b,18,c['sectors_per_cluster'])
        for off,key in [(22,'n_fatent'),(26,'FAT_sectors'),(30,'volume_base'),(34,'FAT_base'),(38,'root_base'),(42,'data_base')]:
            struct.pack_into('<I',b,off,c[key])
        r=decode(b);assert r['total_sectors_possible_range'][0]<=7980<=r['total_sectors_possible_range'][1]
        passed.append(dict(name='previous bounded mount model',record_hex=b.hex(),result=r))
    cases=[('short',record[:-1]),('long',record+b'\0')]
    mutations=[('unmounted type',8,'B',0),('invalid type',8,'B',4),('wrong drive',9,'B',1),
       ('bad base',0,'I',0),('bad stride',4,'I',512),('bad sector size',20,'H',2048),
       ('zero cluster',18,'H',0),('nonpower cluster',18,'H',3),('oversize cluster',18,'H',256),
       ('dirty window',11,'B',1),('dirty FSInfo',12,'B',1),('ambiguous mount',14,'H',0),
       ('bad FAT count',10,'B',3),('empty FAT',26,'I',0),('small FAT',26,'I',1),
       ('empty clusters',22,'I',2),('class mismatch',8,'B',1),('no reserved sectors',34,'I',0),
       ('bad root',38,'I',10),('bad data',42,'I',14),('overflow/outside partition',22,'I',0xffffffff),
       ('root misalignment',16,'H',513)]
    for name,off,fmt,v in mutations:
        b=bytearray(record);struct.pack_into('<'+fmt,b,off,v);cases.append((name,bytes(b)))
    rejected=[]
    for name,b in cases:
        try:decode(b)
        except ValueError as e:rejected.append(dict(name=name,reason=str(e)))
        else:raise AssertionError('accepted '+name)
    result=dict(confidence='PROVEN',scope='Local decoder tests only',positive_cases=passed,rejected_cases=rejected,
                hardware_access=False,current_unit_geometry_authenticated=False)
    (OUT/'parser-tests.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(accepted=len(passed),rejected=len(rejected),reference_result=ref),indent=2))
if __name__=='__main__':main()
