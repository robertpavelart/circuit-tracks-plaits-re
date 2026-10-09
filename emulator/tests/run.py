"""Run isolated synthetic fixtures twice; no Circuit firmware loading or device access."""
import argparse,hashlib,json,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser();ap.add_argument('--exe',required=True);ap.add_argument('--output-dir',required=True)
a=ap.parse_args();out=Path(a.output_dir).resolve()
if out.exists():raise SystemExit('Fresh output required')
out.mkdir(parents=True)
fixtures=json.loads((ROOT/'emulator/tests/fixtures.json').read_text())
results=[]
for name,fixture in fixtures.items():
    program=out/(name+'.asm');program.write_text('\n'.join(fixture['program'])+'\n')
    traces=[];exits=[]
    for repeat in range(2):
        path=out/f'{name}-{repeat}.jsonl'
        proc=subprocess.run([str(Path(a.exe).resolve()),name,str(program),str(path)]+fixture.get('watch',[]),capture_output=True,timeout=15)
        traces.append(path.read_bytes() if path.exists() else b'');exits.append(proc.returncode)
        (out/f'{name}-{repeat}.stderr.txt').write_bytes(proc.stderr)
    issues=[]
    if exits!=([42,42] if fixture.get('fault') else [0,0]):issues.append('exit:'+str(exits))
    if not traces[0] or traces[0]!=traces[1]:issues.append('nonidentical/empty')
    rows=[]
    try:rows=[json.loads(line) for line in traces[0].splitlines()]
    except Exception as e:issues.append('trace parse:'+str(e))
    writes=[r for r in rows if r.get('type')=='WRITE' and r.get('actor')==fixture.get('actor','CPU')]
    actual=[[r['memory_space'],r['effective_address'],r['new_value']] for r in writes]
    if actual!=fixture.get('writes',[]):issues.append('writes:'+str(actual))
    if fixture.get('fault') and not any(r.get('type')=='FAULT' for r in rows):issues.append('missing fault')
    snapshots=[r for r in rows if r.get('type')=='SNAPSHOT' and r.get('label')=='final']
    for key in ('R0','SP'):
        if key in fixture:
            got=None if not snapshots else snapshots[0]['R'][0] if key=='R0' else snapshots[0]['SP']
            if got!=fixture[key]:issues.append(key+':'+str(got))
    if 'read_count' in fixture and sum(r.get('type')=='READ' for r in rows)!=fixture['read_count']:issues.append('read count')
    if 'actors' in fixture:
        for actor in fixture['actors']:
            if sum(r.get('actor')==actor and r.get('type')=='WRITE' for r in rows)!=1:issues.append('actor:'+actor)
    if name=='same' and not all(r['old_value']==r['new_value']==0 for r in writes):issues.append('same-value missing')
    if name in ('rep','do','do_offset','nested'):
        if len(set(r['instruction_counter'] for r in writes))!=len(writes):issues.append('loop ordinal attribution')
    if name=='interrupt':
        pcs=[r['PC'] for r in rows if r.get('type')=='EXEC']
        if pcs!=[1024,32,1536,1538,1025,1026]:issues.append('IRQ control flow:'+str(pcs))
        if snapshots and (snapshots[0]['SR']!=0 or snapshots[0]['SC']!=0):issues.append('IRQ restore')
    results.append(dict(name=name,passed=not issues,issues=issues,trace_SHA256=hashlib.sha256(traces[0]).hexdigest(),exit_codes=exits,writes=len(writes)))
    print(name,'PASS' if not issues else 'FAIL '+repr(issues))
(out/'results.json').write_text(json.dumps(dict(results=results,all_pass=all(r['passed'] for r in results),
    executable_SHA256=hashlib.sha256(Path(a.exe).read_bytes()).hexdigest()),indent=2)+'\n')
raise SystemExit(0 if all(r['passed'] for r in results) else 1)
