from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
out=(O/'peer-mailbox-observed-output.txt').read_text();status=[l for l in out.splitlines() if l.startswith('Y 00002c:')]
assert len(status)==3104 and all(l=='Y 00002c: 800000 800000' for l in status[:32])
completed={'080002':1}
for i,word in enumerate(('094403','0a8804','0bcc05')):
 deferred=status[32+i*1024:32+(i+1)*1024];first_idle=deferred.index('Y 00002c: 800000 800000')
 assert first_idle==326
 assert all(l=='Y 00002c: c00000 800000' for l in deferred[:first_idle])
 assert all(l=='Y 00002c: 800000 800000' for l in deferred[first_idle:])
 completed[word]=first_idle+1
assert out.count('pc=007002')==3104
memory=json.loads((O/'peer-memory.json').read_text())['memory']['X']
canonical=json.dumps({k:int(v,16) for k,v in memory.items()},sort_keys=True).encode()
job=(O/'peer-mailbox-observed-job.txt').read_text().splitlines()
written={hex(int(s.split()[1],16)):int(s.split()[2],16) for s in job if s.startswith('X ')}
assert json.dumps(written,sort_keys=True).encode()==canonical
assert [int(s.split()[2],16) for s in job if s.startswith('Y 2c ')]==[0x080002,0x094403,0x0a8804,0x0bcc05]
proof=dict(confidence='PROVEN',job_word='080002',program_sha256=sha((O/'loaded-core0.be24').read_bytes()),init_X_sha256=sha(canonical),native_output_sha256=sha((O/'peer-mailbox-observed-output.txt').read_bytes()),first_service_status='800000',next_exact_job='094403',next_job_qualified=True,next_job_first_idle_service=first_idle+1,next_job_bounded_services=1024,scope='Original DSP init plus observed ARM-delivered X values; emulator-only caller invokes original1C53; no silicon timing or complete peer scheduler qualification')
proof['completed_exact_jobs']=completed
(O/'peer-contract-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print('Native exact-job proof pinned')
