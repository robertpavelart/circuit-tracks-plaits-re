#!/usr/bin/env python3
"""Copy pinned official Plaits/shared source for static study; no builds.

Only selected text source is fetched, not hardware CAD, firmware binaries or
toolchains. Files are exclusive-create and verified against Git blob hashes.
"""
import argparse,concurrent.futures,hashlib,json,urllib.request
from pathlib import Path
from ct_static import ROOT,save

def request(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Circuit-Tracks-static-source-study'})
    with urllib.request.urlopen(req,timeout=45) as response:return response.read()

def tree(repo,commit):
    value=json.loads(request(f'https://api.github.com/repos/{repo}/git/trees/{commit}?recursive=1'))
    if value.get('truncated'):raise ValueError('Truncated tree')
    return value['tree']

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True)
    p.add_argument('--commit',required=True);args=p.parse_args()
    out=Path(args.output_dir).resolve()
    if ROOT/'original'==out or ROOT/'original' in out.parents:raise SystemExit('Protected original/')
    if out.exists():raise SystemExit('Choose a fresh source directory')
    repo='pichenettes/eurorack';entries=tree(repo,args.commit)
    sub=next(e for e in entries if e['path']=='stmlib' and e['type']=='commit')
    stmlib_commit=sub['sha'];shared=tree('pichenettes/stmlib',stmlib_commit)
    tasks=[]
    for e in entries:
        path=e['path']
        if e['type']=='blob' and ((path.startswith('plaits/') and (path.endswith(('.h','.cc','.c','.py','.mk','.md')) or Path(path).name in ('makefile','Makefile'))) or path in ('.gitmodules','README.md','LICENSE')):
            tasks.append((repo,args.commit,e,path))
    for e in shared:
        path=e['path']
        relevant=path.startswith(('dsp/','utils/','algorithms/')) or '/' not in path
        if relevant and e['type']=='blob' and (path.endswith(('.h','.cc','.c','.py','.mk','.md')) or Path(path).name in ('LICENSE','Makefile','makefile')):
            tasks.append(('pichenettes/stmlib',stmlib_commit,e,'stmlib/'+path))
    total=sum(e.get('size',0) for _,_,e,_ in tasks)
    if total>25*1024*1024:raise SystemExit(f'Selected source exceeds 25 MiB ({total}); review before downloading')
    def fetch(task):
        repo,commit,e,dest=task;data=request(f"https://raw.githubusercontent.com/{repo}/{commit}/{e['path']}")
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if blob!=e['sha']:raise ValueError(f'Blob mismatch {dest}')
        return dest,data,dict(path=dest,repository=repo,revision=commit,git_blob_sha1=blob,size=len(data),sha256=hashlib.sha256(data).hexdigest())
    # Fetch into memory before creating the destination so failures leave no partial checkout.
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(fetch,tasks))
    out.mkdir(parents=True,exist_ok=False)
    for path,data,_ in results:save(out/path,data)
    manifest=dict(status='official source snapshot for static study; not compiled',repository=f'https://github.com/{repo}',
       revision=args.commit,stmlib_repository='https://github.com/pichenettes/stmlib',stmlib_revision=stmlib_commit,
       selection='Plaits text source plus stmlib text dependencies; CAD/binaries/toolchains excluded',
       files=sorted([info for _,_,info in results],key=lambda x:x['path']),total_bytes=total)
    save(out/'source-manifest.json',json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k!='files'}|{'file_count':len(results)},indent=2))

if __name__=='__main__':main()
