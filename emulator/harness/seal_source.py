"""Archive exact local instrumentation overlays and audited source hashes (offline)."""
from pathlib import Path
import json,hashlib,difflib
root=Path(__file__).resolve().parents[2]
source=root/'builds/vendor/dsp56300';local=root/'emulator/upstream/dsp56300'
overlay=root/'emulator/harness/overlay'
if overlay.exists():raise SystemExit('Overlay already exists; refuse overwrite')
entries={};patch=[]
for p in sorted(local.rglob('*')):
    if not p.is_file():continue
    rel=p.relative_to(local).as_posix();raw=p.read_bytes();up=(source/rel).read_bytes()
    entries[rel]={'upstream_SHA256':hashlib.sha256(up).hexdigest(),'local_SHA256':hashlib.sha256(raw).hexdigest()}
    if raw!=up:
        target=overlay/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        patch.extend(difflib.unified_diff([s+'\n' for s in up.decode('utf-8').splitlines()],
                     [s+'\n' for s in raw.decode('utf-8').splitlines()],fromfile='a/'+rel,tofile='b/'+rel))
(root/'emulator/harness/instrumentation.patch').write_text(''.join(patch),encoding='utf-8')
(root/'emulator/harness/source-manifest.json').write_text(json.dumps(dict(
    core_revision='44353be2f0156cac970c6ab4f467ea1998b40605',
    asmjit_revision='3577608cab0bc509f856ebf6e41b2f9d9f71acc4',files=entries),indent=2,sort_keys=True)+'\n')
