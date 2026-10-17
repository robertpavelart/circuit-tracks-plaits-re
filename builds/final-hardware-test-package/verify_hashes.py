"""Read-only package verification; no MIDI, device, decoder or builder imports."""
from pathlib import Path
import hashlib
O=Path(__file__).resolve().parent
count=0
for line in (O/'HASHES.txt').read_text(encoding='utf-8').splitlines():
 if not line or line.startswith('#'):continue
 digest,name=line.split('  ',1);p=(O/name).resolve()
 assert p.is_relative_to(O.resolve()),'Manifest path escapes package'
 assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==digest,name
 count+=1
print('HASH MANIFEST VERIFIED:',count,'files; this does not unlock tools or authorize hardware.')
