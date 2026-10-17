from pathlib import Path
import hashlib,json
O=Path(__file__).resolve().parent;R=O.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=[]
for name in ('phase63-defect-closure','phase64-spi2-model-closure','phase65-shi-startup-closure','phase66-usb-safety-classification'):
 p=R/'builds'/name
 if not p.exists():
  candidates=list((R/'builds').glob(name.split('-')[0]+'-*'));assert len(candidates)==1,candidates;p=candidates[0]
 manifest=p/'SHA256SUMS.txt';count=0
 for line in manifest.read_text().splitlines():
  digest,filename=line.split('  ',1);assert sha(p/filename)==digest,(name,filename);count+=1
 old.append(dict(directory=p.name,verified=count))
r=json.loads((O/'callback-results.json').read_text());assert r['passed'] and not r['allocation_entries'];assert r['rows'][-1]['pc']=='0x8070b00'
assert sha(R/'builds/phase63-defect-closure/circuittracks-nor-defect-closure-development.bin')=='edf4f267030a6c5e8198213372086b89b4ccaaae74741e80ce7c241129a91cd9'
result=dict(confidence='PROVEN',historical_manifests=old,callback_pass=True,candidate_unchanged=True,disposition='B',verdict='PASS',hardware_access=False,MIDI_access=False,firmware_generated=False,scope='Final safety-relevance disposition, not real enumeration or uninterrupted reset-to-capture proof')
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
(O/'SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in sorted(O.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'))
print(json.dumps(result,indent=2))
