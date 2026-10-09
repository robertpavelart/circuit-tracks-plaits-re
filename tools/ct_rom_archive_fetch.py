"""Targeted historical Freescale archive discovery and primary manual retrieval.
Public read-only URLs only, no hardware, accounts or source execution.
"""
import argparse,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--output-dir',required=True,type=Path)
a=ap.parse_args();out=a.output_dir.resolve()
if out.exists() or not out.is_relative_to((ROOT/'builds/phase19b-rom').resolve()):raise ValueError('Fresh phase output required')
out.mkdir(parents=True)
urls={
 'freescale-community-index':'https://web.archive.org/cdx/search/cdx?url=community.freescale.com/*DSP56725-bootloader*&output=json&filter=statuscode:200&collapse=urlkey',
 'freescale-forums-index':'https://web.archive.org/cdx/search/cdx?url=forums.freescale.com/*DSP56725-bootloader*&output=json&filter=statuscode:200&collapse=urlkey',
 'DSP56720RM.pdf':'https://www.nxp.com/docs/en/reference-manual/DSP56720RM.pdf',
}
results=[]
for name,url in urls.items():
    try:
        with urllib.request.urlopen(url,timeout=15) as response:
            body=response.read()
            with (out/name).open('xb') as f:f.write(body)
            results.append(dict(name=name,url=url,status=response.status,bytes=len(body)))
    except Exception as e:results.append(dict(name=name,url=url,error=str(e)))
with (out/'retrieval.json').open('x',encoding='utf-8') as f:json.dump(results,f,indent=2)
print(json.dumps(results))
