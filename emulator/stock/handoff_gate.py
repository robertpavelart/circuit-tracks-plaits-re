"""Inspect the audited partial handoff contract without constructing/executing CPU.
This phase only establishes an explicit PC assignment. Unknown register values
cannot silently acquire emulator defaults; no execution path is exposed.
"""
import argparse
import json
from pathlib import Path

def inspect(manifest):
    if manifest.get('execution_allowed') is not False or manifest.get('instruction_limit')!=0:
        raise ValueError('This audited handoff remains blocked; no execution enable accepted')
    fields={f['field']:f for f in manifest['fields']}
    for name,f in fields.items():
        if not f.get('provenance'):
            raise ValueError(f'Missing provenance: {name}')
        if name!='PC' and f['value'] is not None:
            raise ValueError(f'No proven numeric handoff value in this audit: {name}')
    if fields['PC']['value']!=0 or fields['PC']['classification']!='DOCUMENTED HANDOFF VALUE':
        raise ValueError('PC must come from the verified P0 boot-record entry')
    for required in ['SR','OMR','Y:PCRG','Y:PRRG','Y:ICDR4']:
        if fields[required]['value'] is not None:
            raise ValueError(f'Blocking unknown was replaced: {required}')
    assignments={a['field']:a['value'] for a in manifest['explicit_assignments']}
    if assignments!={'PC':0} or any(not a.get('provenance') for a in manifest['explicit_assignments']):
        raise ValueError('Only proven, explicitly sourced PC0 may be assigned; no constructor defaults')
    return dict(status='BLOCKED',explicit_assignments=assignments,
                stock_instructions_executed=0,CPU_constructed=False,
                reason='Minimum ROM/GPIO/live control contract still incomplete')

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('manifest',type=Path)
    a=ap.parse_args();print(json.dumps(inspect(json.loads(a.manifest.read_text())),sort_keys=True))
