"""Exact 12-byte conceptual lifecycle. All event interception is an assumption."""
from pathlib import Path
import sys,json,struct,zlib
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'builds/phase56-geometry-snapshot-lifecycle'))
from compact import decode
BOOT,VALID,EXPORTED,ACTIVE,SUCCESS,FAILED,MOUNTING,UNSUPPORTED=range(8)
class State:
    def __init__(self):self.r=bytearray(12);self.limit=0x20044e58;self.submits=[]
    @property
    def word(self):return struct.unpack_from('<I',self.r)[0]
    @property
    def phase(self):return self.word&7
    @property
    def epoch(self):return self.word>>4
    def set(self,phase,epoch=None,unexpected=False):
        e=self.epoch if epoch is None else epoch
        struct.pack_into('<I',self.r,0,(e<<4)|(self.word&8)|(8 if unexpected else 0)|phase)
    def reserve(self,cursor=0x20044d68):
        if self.limit==0x20044d70:return True # Must preserve already initialized state.
        if self.limit!=0x20044e58 or cursor>0x20044d70:return False
        self.limit=0x20044d70;self.r[:]=bytes(12);return True
    def first_mount(self,expected_entry=True):
        if self.limit!=0x20044d70 or self.phase!=BOOT or self.epoch!=0 or not expected_entry:
            self.set(FAILED,unexpected=True);return False
        self.set(MOUNTING,epoch=1);return True
    def commit(self,packed,expected=1):
        if self.phase!=MOUNTING or self.epoch!=expected:return False
        try:decode(packed)
        except ValueError:self.set(UNSUPPORTED);return False
        self.r[4:]=packed;self.set(VALID);return True
    def changed(self):
        # Strict first-only policy; no subsequent epoch can become admissible.
        self.set(FAILED,unexpected=True);return False
    def export(self):
        if self.phase not in (VALID,EXPORTED):return None
        self.set(EXPORTED)
        return dict(epoch=self.epoch,crc=zlib.crc32(self.r[4:]),record=bytes(self.r[4:]))
    def authorize(self,t,now=0,mask=2,identity_ok=False):
        if self.phase!=EXPORTED or self.epoch!=1 or self.word&8 or t is None:return False
        if t['epoch']!=self.epoch or t['crc']!=zlib.crc32(self.r[4:]):return False
        if mask not in (1,2,3) or mask&1 and not identity_ok:return False
        self.set(ACTIVE);self.r[4:]=bytes((mask,37,0,1))+struct.pack('<I',now)
        self.submits.append(dict(target_mask=mask,epoch=self.epoch));return True
    def tick(self,now):
        if self.phase==ACTIVE and ((now-struct.unpack_from('<I',self.r,8)[0])&0xffffffff)>=5000:self.set(FAILED)
    def complete(self):
        if self.phase==ACTIVE:self.set(SUCCESS);self.r[7]=0
def main():
    packed=bytes.fromhex(json.loads((ROOT/'builds/phase56-geometry-snapshot-lifecycle/compact-tests.json').read_text())['round_trips'][0]['compact_hex'])
    results=[]
    def mounted():
        s=State();assert s.reserve() and s.first_mount() and s.commit(packed);return s
    s=mounted();before=bytes(s.r);assert s.reserve();assert bytes(s.r)==before
    for n in (0,5000,0xffffffff):s.tick(n);assert bytes(s.r)==before
    results.append(dict(name='lazy-init-and-nonactive-tick-preserve-geometry',passed=True))
    for event in ('before-mount','during-copy','after-valid','after-export','after-admission'):
        s=State();s.reserve();token=None
        if event!='before-mount':s.first_mount()
        if event not in ('before-mount','during-copy'):assert s.commit(packed)
        if event in ('after-export','after-admission'):token=s.export()
        if event=='after-admission':assert s.authorize(token)
        s.changed();before=bytes(s.r)
        assert not s.first_mount() and not s.commit(packed) and not s.authorize(token)
        s.complete();assert s.phase==FAILED and not s.export()
        results.append(dict(name='unexpected-'+event,passed=True,submits=len(s.submits),
            no_submission_after_quarantine=True,owner_retained_if_already_active=s.r[7]==1 if event=='after-admission' else None))
    for start in (0,0xfffffff0):
        s=mounted();t=s.export();assert s.authorize(t,start)
        s.tick((start+4999)&0xffffffff);assert s.phase==ACTIVE
        s.tick((start+5000)&0xffffffff);assert s.phase==FAILED and s.r[7]==1
        s.complete();assert s.phase==FAILED and not s.authorize(t)
        results.append(dict(name='timeout-and-late-success-'+hex(start),passed=True,submits=len(s.submits),owner_retained=True))
    s=mounted();t=s.export();assert s.authorize(t);s.complete();assert s.phase==SUCCESS and not s.authorize(t)
    results.append(dict(name='success-one-shot',passed=True,submits=len(s.submits)))
    s=State();assert not s.reserve(0x20044d74) and not s.submits
    results.append(dict(name='reservation-refusal',passed=True))
    for bad in ('epoch','digest','identity'):
        s=mounted();t=s.export()
        if bad=='epoch':t['epoch']+=1
        elif bad=='digest':t['crc']^=1
        assert not s.authorize(t,mask=1 if bad=='identity' else 2)
        results.append(dict(name='reject-'+bad,passed=True,submits=0))
    r=dict(confidence='PROVEN',scope='Pure 12-byte first-epoch union model; reservation, event interception, atomic publication/admission and external wrapper ownership are assumed contracts, not native proofs',
        state_bytes=12,cases=results,passed=True,native_old_owner_adaptation=False,
        full_boot_first_epoch_proven=False)
    (OUT/'epoch-model-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(results))))
if __name__=='__main__':main()
