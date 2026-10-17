"""Finite volatile 12-byte union model; no native patch/transport implemented."""
from pathlib import Path
import json,struct,zlib
from compact import encode,fields,decode
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
EMPTY,VALID,EXPORTED,ACTIVE,SUCCESS,FAILED,INVALID,UNSUPPORTED=range(8)
class Gate:
    def __init__(self):self.r=bytearray(12);self.submits=[];self.pending=False
    @property
    def word(self):return struct.unpack_from('<I',self.r)[0]
    @property
    def phase(self):return self.word&7
    @property
    def generation(self):return self.word>>4
    @property
    def tainted(self):return bool(self.word&8)
    def set(self,phase,gen=None,taint=None):
        gen=self.generation if gen is None else gen;taint=self.tainted if taint is None else taint
        struct.pack_into('<I',self.r,0,(gen<<4)|(8 if taint else 0)|phase)
    def changing(self):
        if self.phase in (ACTIVE,SUCCESS,FAILED):
            # Future implementation must intercept BEFORE geometry changes,
            # defer/reject them while a one-shot raw transaction is admitted.
            self.pending=True;return False
        if self.generation==0xfffffff:self.set(FAILED);return False
        self.set(INVALID,self.generation+1,self.generation!=0 or self.tainted);return True
    def mounted(self,packed):
        if self.phase!=INVALID:return False
        try:decode(packed)
        except ValueError:self.set(UNSUPPORTED);return False
        self.r[4:]=packed;self.set(VALID);return True
    def export(self):
        if self.phase not in (VALID,EXPORTED):return None
        self.set(EXPORTED)
        return dict(generation=self.generation,history_tainted=self.tainted,
            record=bytes(self.r[4:]),digest=zlib.crc32(self.r[4:]))
    def authorize(self,token,mask=2,identity_ok=False):
        if token is None or self.phase!=EXPORTED or self.tainted:return False
        if token['generation']!=self.generation or token['digest']!=zlib.crc32(self.r[4:]):return False
        if mask not in (1,2,3) or mask&1 and not identity_ok:return False
        d=decode(bytes(self.r[4:]));assert not any(d['targets_reachable'].values())
        # This atomic admission is an assumption of the model. During ACTIVE,
        # every geometry-changing producer must honor changing() before writes.
        self.set(ACTIVE);self.r[4:]=bytes([mask,0,0,0])+struct.pack('<I',0)
        self.submits += ([0x81000] if mask&1 else [])+([0x82000] if mask&2 else [])
        return True
def main():
    old=json.loads((ROOT/'builds/phase55-precleanup-geometry-snapshot/mount-cases.json').read_text())['cases'][0]
    p=encode(fields(bytes.fromhex(old['boundary']['record'])));rows=[]
    def start():
        g=Gate();assert g.changing() and g.mounted(p);return g
    g=start();t=g.export();assert g.authorize(t) and g.submits==[0x82000]
    rows.append(dict(name='coefficients-independent-of-identity',submits=g.submits))
    g=start();t=g.export();assert not g.authorize(t,1) and not g.submits
    rows.append(dict(name='identity-needs-separate-gate',submits=g.submits))
    g=start();t=g.export();assert g.changing();assert not g.authorize(t);assert g.mounted(p)
    assert not g.authorize(t);new=g.export();assert new['generation']!=t['generation'] and new['history_tainted']
    assert not g.authorize(new) and not g.submits
    rows.append(dict(name='remount-rejects-old-token-and-taints-history',old=t['generation'],new=new['generation'],submits=[]))
    g=start();t=g.export();assert g.authorize(t);assert not g.changing() and g.pending
    rows.append(dict(name='active-admission-defers-mutation',submits=g.submits,producer_deferred=True))
    g=start();t=g.export();bad=dict(t);bad['digest']^=1;assert not g.authorize(bad)
    rows.append(dict(name='wrong-digest',submits=g.submits))
    g=start();g.set(FAILED);assert not g.export() and not g.authorize(None)
    rows.append(dict(name='failure-absorbs',submits=g.submits))
    g=start();g.set(INVALID,0xfffffff);assert not g.changing() and g.phase==FAILED
    rows.append(dict(name='generation-exhaustion-fails-closed',submits=g.submits))
    # All event insertion positions around export/admission; no stale token
    # accepted, or admission wins and the producer is deferred before mutation.
    interleavings=[]
    for pos in range(4):
        g=start();t=None;admitted=False;mutated=False
        for i,action in enumerate(('export','authorize','complete')):
            if i==pos:mutated=g.changing()
            if action=='export':t=g.export()
            elif action=='authorize':admitted=g.authorize(t)
            else:
                if admitted:g.set(SUCCESS)
        if pos==3:mutated=g.changing()
        assert not (admitted and mutated)
        interleavings.append(dict(position=pos,admitted=admitted,geometry_mutated=mutated))
    result=dict(confidence='PROVEN',scope='Abstract 12-byte union/gating contract with ALL geometry writers intercepted and atomic admission assumed; not firmware liveness or asynchronous closure',
        bytes=12,cases=rows,interleavings=interleavings,
        historical_counterexample='Unsafe initial geometry may mutate evidence before a later safe remount. Generation matching alone does not recover original bytes.',
        passed=True)
    (OUT/'lifecycle-tests.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(rows),interleavings=len(interleavings))))
if __name__=='__main__':main()
