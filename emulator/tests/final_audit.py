"""Offline fixture/build reproducibility and protected input integrity report."""
from pathlib import Path
import hashlib,json,subprocess,sys

root=Path(__file__).resolve().parents[2];base=root/'builds/phase19a'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
results=[json.loads((base/d/'results.json').read_text()) for d in ('validated','validated-repeat')]
assert all(r['all_pass'] for r in results)
hashes={}
for r in results[0]['results']:
    name=r['name'];traces=[(base/d/f'{name}-{n}.jsonl').read_bytes() for d in ('validated','validated-repeat') for n in (0,1)]
    assert traces[0] and all(t==traces[0] for t in traces)
    hashes[name]=hashlib.sha256(traces[0]).hexdigest()
expected={'original/circuittracks-firmware-4486.syx':'bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd',
          'firmware/circuittracks-firmware-4486.bin':'b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da'}
for name,h in expected.items():assert sha(root/name)==h
manifest=json.loads((root/'firmware/dsp/build-4486/manifest.json').read_text())
for block in manifest['blocks']:
    for kind in ('stream','payload'):
        p=root/'firmware/dsp/build-4486'/block[kind+'_file'];assert sha(p)==block[kind+'_sha256'];expected[str(p.relative_to(root))]=sha(p)
source=json.loads((root/'emulator/harness/source-manifest.json').read_text())
for name,hashes1 in source['files'].items():
    assert sha(root/'builds/vendor/dsp56300'/name)==hashes1['upstream_SHA256'],name
    assert sha(root/'emulator/upstream/dsp56300'/name)==hashes1['local_SHA256'],name
    assert sha(base/'source-repeat'/name)==hashes1['local_SHA256'],name
report=dict(fixture_count=len(hashes),runs_per_fixture=4,independent_builds=2,
            all_expected_results_pass=True,all_traces_byte_identical=True,trace_SHA256=hashes,
            protected_inputs_SHA256=expected,vendor_source_unchanged=True,source_overlay_reproduction=True,
            compiler='MSVC19.44.35228, x64',configuration='Debug C++17; DSP56K_FORCE_INTERPRETER=1; DSP56300_DEBUGGER=0',
            note='Build recipe/source reproduced; Debug binary hashes may differ with build paths/PDB metadata. Trace determinism verified.',
            binaries={d:sha(base/d/'ct_replay_fixture.exe') for d in ('core-build','repeat-build')})
with (base/'reproducibility-final.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(f'{len(hashes)} fixtures ×4 runs: identical traces from2 independent builds; protected hashes unchanged.')
