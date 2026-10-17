"""Inspect only DSP boot-ready producer requested by native SPI2 polling."""
from pathlib import Path
import subprocess,json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[1];P=R/'builds/phase63-defect-closure'
REF=Path(r'C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main')
image=(P/'circuittracks-nor-defect-closure-development.bin').read_bytes();out=[]
for core in (0,1):
 address=int.from_bytes(image[0x19700+8*core:0x19704+8*core],'little');off=address-0x08010000;n=int.from_bytes(image[off:off+3],'big');b=image[off+6:off+6+3*n]
 assert len(b)==3*n and n>0
 name=f'loaded-core{core}.be24';(O/name).write_bytes(b)
 r=subprocess.run([str(REF/'ext/bin/dsptool.exe'),'dis',name],cwd=O,capture_output=True,text=True);assert r.returncode==0
 (O/f'loaded-core{core}.asm').write_text(r.stdout)
 lines=r.stdout.splitlines();matches=[dict(line=i+1,context=lines[max(0,i-3):i+4]) for i,l in enumerate(lines) if any(x in l.lower() for x in ('y:$2b','y:$00002b','y:<$2b','y:>$2b','y:$002b'))]
 out.append(dict(core=core,ARM_bootstrap_address=hex(address),words=n,sha256=hashlib.sha256(b).hexdigest(),ready_references=matches))
(O/'peer-ready-static.json').write_text(json.dumps(dict(confidence='PROVEN',scope='Exact candidate DSP image extraction/disassembly only; no firmware generation, no complete DSP boot replay',cores=out),indent=2)+'\n');print(json.dumps(out,indent=2))
job='LOADP loaded-core0.be24 0\nMAX 2000000\nPC 107\nSTOP 25f3\nRUN\nDUMPY 2c 1\nWATCHFILE ready-writes.txt\nWATCH Y 2b 1\nMAX 10000\nSTOP 2602\nRUN\nDUMPY 2b 1\nX fff 000001\nRUN\nDUMPY 2b 1\n'
(O/'peer-ready-job.txt').write_text(job)
r=subprocess.run([str(REF/'ext/bin/dsptool.exe'),'run','peer-ready-job.txt'],cwd=O,capture_output=True,text=True)
(O/'peer-ready-output.txt').write_text(r.stdout+r.stderr);print(r.stdout+r.stderr)
for selector in (0,2,3,4,5):
 job='LOADP loaded-core0.be24 0\nMAX 2000000\nPC 107\nSTOP 25f3\nRUN\nP 7000 0bf080 001c53 0c7002\nY 2c '+f'{0x080000|selector:06x}'+'\nWATCHFILE mailbox-'+str(selector)+'.txt\nWATCH Y 2c 1\nPC 7000\nSTOP 7002\nRUN\nDUMPY 2c 1\n'
 (O/f'mailbox-{selector}-job.txt').write_text(job)
 r=subprocess.run([str(REF/'ext/bin/dsptool.exe'),'run',f'mailbox-{selector}-job.txt'],cwd=O,capture_output=True,text=True)
 (O/f'mailbox-{selector}-output.txt').write_text(r.stdout+r.stderr);print(selector,r.stdout+r.stderr)
