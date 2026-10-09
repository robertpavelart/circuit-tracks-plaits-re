"""Fail closed when the registered local source surface changes; static audit plus fixture coverage."""
from pathlib import Path
import json,hashlib,argparse
root=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser();ap.add_argument('--results',required=True);ap.add_argument('--output',required=True)
ap.add_argument('--source-dir',default=str(root/'emulator/upstream/dsp56300'))
a=ap.parse_args();manifest=json.loads((root/'emulator/harness/source-manifest.json').read_text())
local=Path(a.source_dir).resolve()
files={p.relative_to(local).as_posix():p for p in local.rglob('*') if p.is_file()}
assert set(files)==set(manifest['files']),'New/removed source: mandatory write-path review'
for name,p in files.items():assert hashlib.sha256(p.read_bytes()).hexdigest()==manifest['files'][name]['local_SHA256'],name
harness_manifest=root/'emulator/harness/harness-manifest.json'
assert harness_manifest.exists(),'Harness source registry required'
for name,h in json.loads(harness_manifest.read_text()).items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==h,name
dma=(local/'source/dsp56kEmu/dma.cpp').read_text()
assert 'memcpy(dst, src' not in dma and '*dst++ = data' not in dma
assert dma.count('getMemPtr(')==1,'Raw DMA pointer call appeared'
assert 'if(replayWrite)' in (local/'source/dsp56kEmu/memory.cpp').read_text()
assert 'replayBefore(repeatedOpPC,op)' in (local/'source/dsp56kEmu/dsp.cpp').read_text()
results=json.loads(Path(a.results).read_text());assert results['all_pass']
passed={r['name'] for r in results['results'] if r['passed']}
required={'direct','pwrite','indirect','postinc','postdec','predec','indexed','parallel','bit_store',
          'rep','do','nested','modulo','modulo_dec','same','peripheral','dma_copy','dma_fill',
          'dma_fixed','dma_p','dma_shared','dma_controller','dma_p_fill','dma_peripheral_fill','dma_peripheral_copy',
          'actors','invalid_read','invalid_write','interrupt'}
assert required<=passed
report=dict(source_files_registered=len(files),source_hashes_match=True,
    required_fixtures=sorted(required),fixture_coverage_match=True,
    scope='Enabled forced-interpreter fixture bus; no general chip/peripheral/stock replay certification',
    future_exclusions=['JIT DSP execution','Circuit startup/peripherals/worker','externalBusDevice adapter',
                       'OMF/bootROM loader API','unregistered peripheral APIs/raw pointer access'])
with Path(a.output).open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
