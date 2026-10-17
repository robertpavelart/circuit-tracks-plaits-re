"""Preserve 28 prior native cases and add exact status/mount cases."""
from pathlib import Path
import sys,json,importlib.util
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase61-final-geometry-gated-candidate'
sys.path.insert(0,str(P))
spec=importlib.util.spec_from_file_location('host',P/'host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host);sys.modules['host']=host
s=(P/'native_tests.py').read_text().replace("O/'circuittracks-final-geometry-gated-nor-test.syx'","O/'circuittracks-nor-defect-closure-development.syx'")
s=s.replace('self.frames=[];self.reads=[]','self.status_frames=[];self.frames=[];self.reads=[]')
s=s.replace("if pc==L['drain']:","if pc in (L['drain'],L['status_drain']):")
s=s.replace('self.frames.append(bytes(u.mem_read(bp,ln)))',"frame=bytes(u.mem_read(bp,ln));(self.status_frames if frame[4]==0x4f else self.frames).append(frame)")
s=s.replace("self.call(L['begin']);self.call(L['snapshot'],0)","self.call(L['begin'],0x20000ab0);self.u.reg_write(UC_ARM_REG_R4,0x20000aa0);self.call(L['snapshot'],0)")
s=s.replace("n.call(L['snapshot'],0);assert n.word()", "n.u.reg_write(UC_ARM_REG_R4,0x20000aa0);n.call(L['snapshot'],0);assert n.word()")
s=s.replace("len(n.frames)==1", "len(n.frames)==2")
ns=dict(__file__=str(O/'native_regression.py'),__name__='selected_native_cases');exec(compile(s,str(O/'selected-native-cases.py'),'exec'),ns)
N=ns['N'];L=ns['L'];S=ns['S'];SESSION=ns['SESSION'];UC_ARM_REG_R4=ns['UC_ARM_REG_R4']

def main():
 ns['main']()
 rows=[]
 from status_protocol import parse
 for word,status in [(0,'NOT_READY'),(0x16,'NOT_READY'),(0x17,'NOT_READY'),(0x1d,'INVALID'),(0x18,'UNSAFE'),(0x15,'FAILED'),(0x13,'AUTHORIZED'),(0x14,'SUCCESS')]:
  n=N();n.e.w32(S,word);before=n.record();n.send(host.request(SESSION));assert n.record()==before and not n.reads and not n.frames
  assert parse(n.status_frames[-1],SESSION)['status']==status
  rows.append(dict(case=status,control=hex(word),packet=n.status_frames[-1].hex(),passed=True))
 n=N().mounted();before=n.record()
 for _ in range(3):
  n.call(L['begin'],0x20001b04);n.u.reg_write(UC_ARM_REG_R4,0x20001af4);n.call(L['snapshot'],1);n.call(L['binding'],0x20001af4);n.call(L['stride'],512,0x20001aec)
  n.u.mem_write(ns['BUF'],b'1:\0');n.call(L['register'],0,ns['BUF']);assert n.record()==before
 rows.append(dict(case='SD mount/unmount/remount ignored by NOR lifecycle',passed=True))
 n.call(L['begin'],0x20000ab0);assert n.word()==0x17;n.u.reg_write(UC_ARM_REG_R4,0x20000aa0);n.call(L['snapshot'],0);assert n.record()==before
 rows.append(dict(case='preexport native NOR remount verifies unchanged first snapshot',passed=True))
 n.call(L['begin'],0x20000ab0);n.e.w32(0x20000ad4,n.e.r32(0x20000ad4)+1);n.u.reg_write(UC_ARM_REG_R4,0x20000aa0);n.call(L['snapshot'],0);assert n.word()==0x1d
 rows.append(dict(case='preexport changed NOR geometry invalidates',passed=True))
 n=N().mounted().export();n.call(L['begin'],0x20000ab0);assert n.word()==0x1d;n.authorize();assert not n.reads
 rows.append(dict(case='postexport NOR remount invalidates authorization',passed=True))
 n=N().mounted().export();assert parse(n.status_frames[-1],SESSION)['status']=='READY';n.authorize();assert [parse(f,SESSION)['status'] for f in n.status_frames]==['READY','AUTHORIZED','SUCCESS']
 rows.append(dict(case='READY -> AUTHORIZED -> SUCCESS actual dispatch',passed=True))
 (O/'status-mount-tests.json').write_text(json.dumps(dict(confidence='PROVEN',cases=rows,passed=True,candidate_sha256=ns['meta']['BIN_sha256'],unsafe_case='classifier input only: supported D4000 mapping cannot overlap fixed targets'),indent=2)+'\n')
 print('Status/mount cases PASS',len(rows))
if __name__=='__main__':main()
