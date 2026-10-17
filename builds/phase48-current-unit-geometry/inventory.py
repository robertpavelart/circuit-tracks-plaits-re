"""Local evidence inventory only. Never opens ports, imports transports or builds firmware."""
from pathlib import Path
import os,json,hashlib,zipfile,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    paths=[];candidates=[];groups={};archive_rows=[]
    pattern=re.compile(r'ram|qspi|nor[_-]|capture|snapshot|dump|geometry|hardware|device|midi|storage',re.I)
    for base,dirs,files in os.walk(ROOT,followlinks=False):
        dirs[:]=[d for d in dirs if d!='.git']
        for name in files:
            p=Path(base)/name
            if OUT==p.parent:continue
            rel=p.relative_to(ROOT).as_posix();paths.append(rel)
            group=rel.split('/')[0];groups[group]=groups.get(group,0)+1
            binary=p.suffix.lower() in ('.bin','.img','.raw','.dmp','.syx','.mid')
            if binary or (pattern.search(name) and p.suffix.lower() in ('.json','.log','.txt','.csv','.zip')):
                row=dict(path=rel,bytes=p.stat().st_size)
                if '/vendor/' in rel or '/wxWidgets/' in rel:row['provenance_class']='vendor dependency, not a unit capture'
                elif '/synthetic' in rel:row['provenance_class']='explicit synthetic capture'
                elif '/phase' in rel:row['provenance_class']='phase artifact; producer/provenance needs review, not presumed hardware'
                else:row['provenance_class']='candidate, no current-unit attribution established'
                if p.suffix.lower() in ('.bin','.img','.raw','.dmp') and p.stat().st_size<4*1024*1024:row['sha256']=sha(p)
                candidates.append(row)
            if p.suffix.lower()=='.zip' and '/vendor/' not in rel:
                try:
                    with zipfile.ZipFile(p) as z:
                        hits=[dict(name=x.filename,bytes=x.file_size) for x in z.infolist() if (pattern.search(x.filename) or Path(x.filename).suffix.lower() in ('.bin','.img','.raw','.dmp','.syx','.mid')) and not x.is_dir()]
                    archive_rows.append(dict(path=rel,sha256=sha(p),candidate_entries=hits))
                except (zipfile.BadZipFile,OSError) as exc:archive_rows.append(dict(path=rel,error=str(exc)))
    (OUT/'project-file-inventory.txt').write_text('\n'.join(sorted(paths))+'\n',encoding='utf8')
    result=dict(confidence='PROVEN',scope='Whole project file-name inventory excluding .git and Phase48 output; names are not provenance',
        files=len(paths),top_level_counts=groups,candidates=candidates,archives=archive_rows,
        current_unit_geometry_found=False)
    (OUT/'existing-evidence-inventory.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(files=len(paths),groups=groups,candidates=len(candidates),archives=len(archive_rows)),indent=2))
if __name__=='__main__':main()
