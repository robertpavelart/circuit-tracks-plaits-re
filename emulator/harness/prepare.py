"""Reproduce exact local overlays on a fresh pinned source copy. No firmware/device access."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser();ap.add_argument('--output-dir',default='emulator/upstream/dsp56300')
out=Path(ap.parse_args().output_dir).resolve()
if out.exists():raise SystemExit('Fresh source directory required')
if not out.is_relative_to(ROOT) or out.is_relative_to(ROOT/'original'):raise SystemExit('Workspace non-original destination required')
manifest=json.loads((ROOT/'emulator/harness/source-manifest.json').read_text())
src=ROOT/'builds/vendor/dsp56300';overlay=ROOT/'emulator/harness/overlay'
for name,entry in manifest['files'].items():
    raw=(src/name).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==entry['upstream_SHA256'],name
    if (overlay/name).exists():raw=(overlay/name).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==entry['local_SHA256'],name
    p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
print('Pinned source + exact overlays reproduced; no dependency or firmware execution.')
