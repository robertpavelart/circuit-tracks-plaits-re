"""Read known public ROM-source discovery endpoints; archive responses unchanged.
No authentication, hardware, external state mutation, installation or execution.
"""
import argparse,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--output-dir',required=True,type=Path)
a=ap.parse_args();out=a.output_dir.resolve()
if out.exists() or not out.is_relative_to((ROOT/'builds/phase19b-rom').resolve()):
    raise ValueError('Fresh output under phase19b-rom required')
out.mkdir(parents=True)
urls={
 'nxp-public-attachments':'https://community.nxp.com/restapi/vc/messages/id/217564/attachments',
 'archive-index':'https://web.archive.org/cdx/search/cdx?url=community.nxp.com/t5/Other-NXP-Products/DSP56725-bootloader/*&output=json&filter=statuscode:200&collapse=urlkey',
 'archive-availability':'https://archive.org/wayback/available?url=https%3A%2F%2Fcommunity.nxp.com%2Ft5%2FOther-NXP-Products%2FDSP56725-bootloader%2Ftd-p%2F217563',
}
results=[]
for name,url in urls.items():
    try:
        with urllib.request.urlopen(url,timeout=15) as response:
            body=response.read()
            with (out/(name+'.response')).open('xb') as f:f.write(body)
            results.append(dict(name=name,url=url,status=response.status,bytes=len(body),
                preview=body[:700].decode('utf-8','replace')))
    except Exception as e:results.append(dict(name=name,url=url,error=str(e)))
with (out/'public-retrieval.json').open('x',encoding='utf-8') as f:json.dump(results,f,indent=2)
print(json.dumps(results))
