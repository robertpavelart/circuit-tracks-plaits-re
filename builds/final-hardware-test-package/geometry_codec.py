"""Offline auditable geometry encoding. No transport/device/builder imports."""
from pathlib import Path
import json,struct
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
BASE=0xd4000;STRIDE=4096;LIMIT=(0x2000000-BASE)//STRIDE
def fields(raw):
    if len(raw)!=46:raise ValueError('record size')
    b,s=struct.unpack_from('<II',raw)
    typ,drive,nf=raw[8:11];spc,bps=struct.unpack_from('<HH',raw,18)
    entries,fatsz,vol,fat,root,data=struct.unpack_from('<6I',raw,22)
    return dict(base=b,stride=s,type=typ,drive=drive,nfats=nf,csize=spc,bps=bps,
        entries=entries,fatsz=fatsz,vol=vol,fat=fat,root=root,data=data)
def encode(f):
    if (f['base'],f['stride'],f['bps'],f['drive'])!=(BASE,STRIDE,STRIDE,0):raise ValueError('binding/stride not supported')
    if f['type'] not in (1,2):raise ValueError('only FAT12/16 supported')
    c=f['csize'];nf=f['nfats']
    if c not in (1,2,4,8,16,32,64,128) or nf not in (1,2):raise ValueError('invalid factors')
    scalars=[f[k] for k in ('fat','fatsz','data','entries')]
    if any(v<0 or v>8191 for v in scalars):raise ValueError('not losslessly representable')
    if f['root']!=f['fat']+nf*f['fatsz']:raise ValueError('native fixed-root relationship failed')
    v=sum(s<<(13*i) for i,s in enumerate(scalars))
    v|=(c.bit_length()-1)<<52;v|=(nf-1)<<55;v|=(f['type']-1)<<56
    return v.to_bytes(8,'little')
def decode(raw):
    if len(raw)!=8:raise ValueError('compact size')
    v=int.from_bytes(raw,'little')
    if v>>57:raise ValueError('reserved bits')
    fat,fatsz,data,entries=[(v>>(13*i))&8191 for i in range(4)]
    c=1<<((v>>52)&7);nf=1+((v>>55)&1);typ=1+((v>>56)&1)
    if entries<=2 or c>128 or not fatsz:raise ValueError('invalid native counts')
    n=entries-2;expected=1 if n<0xff6 else 2 if n<0xfff6 else 3
    if typ!=expected:raise ValueError('FAT class mismatch')
    endfat=fat+nf*fatsz;end=data+n*c
    if not 0<fat<endfat<data<end<=LIMIT:raise ValueError('normal domains unbounded/unsupported')
    need=(entries*3+1)//2 if typ==1 else entries*2
    if need>fatsz*STRIDE:raise ValueError('FAT too small')
    domains=[('FAT',fat,endfat),('root',endfat,data),('data',data,end)]
    physical=[dict(kind=k,start=BASE+a*STRIDE,end_exclusive=BASE+z*STRIDE) for k,a,z in domains]
    targets={hex(t):any(t<r['end_exclusive'] and z>r['start'] for r in physical) for t,z in ((0x81000,0x81017),(0x82000,0x82200))}
    return dict(type=typ,fat=fat,fatsz=fatsz,data=data,entries=entries,csize=c,nfats=nf,
        domains=physical,targets_reachable=targets)
def main():
    prior=json.loads((ROOT/'builds/phase55-precleanup-geometry-snapshot/mount-cases.json').read_text())['cases']
    rows=[]
    for c in prior:
        if c['boundary']['status']!=0:continue
        f=fields(bytes.fromhex(c['boundary']['record']));packed=encode(f);got=decode(packed)
        assert all(got[k]==f[k] for k in ('type','fat','fatsz','data','entries','csize','nfats'))
        assert not any(got['targets_reachable'].values())
        rows.append(dict(name=c['name'],source=f,compact_hex=packed.hex(),decoded=got,lossless_required_fields=True))
    rejected=[];base=rows[0]['source']
    for name,changes in [('FAT32',{'type':3}),('large-field',{'data':8192}),('wrong-stride',{'stride':512}),
        ('wrong-base',{'base':0}),('root-mismatch',{'root':123}),('unbounded',{'entries':8191}),('FAT-too-small',{'fatsz':1,'root':3})]:
        try:decode(encode(base|changes))
        except ValueError as e:rejected.append(dict(name=name,error=str(e)))
        else:raise AssertionError(name)
    # Exercise complete small scalar encoding boundary dimensions without device I/O.
    factor_tests=0
    for csize in (1,2,4,8,16,32,64,128):
        for nfats in (1,2):
            f=base|dict(type=1,csize=csize,nfats=nfats,entries=32,fatsz=1,fat=1,root=1+nfats,data=2+nfats)
            d=decode(encode(f));assert d['csize']==csize and d['nfats']==nfats;factor_tests+=1
    result=dict(confidence='PROVEN',scope='Lossless bounded FAT12/16 representation and supplied-model arithmetic, not unit acquisition or globally minimal information theorem',
        bytes=8,used_bits=57,spare_bits=7,comparison_general_scalars_bytes=23,
        round_trips=rows,rejections=rejected,factor_cases=factor_tests,passed=True)
    (OUT/'compact-tests.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,round_trips=len(rows),rejections=len(rejected),factors=factor_tests)))
if __name__=='__main__':main()
