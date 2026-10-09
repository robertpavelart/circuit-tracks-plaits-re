#!/usr/bin/env python3
"""Reproduce selected authoritative manual evidence from locally archived PDFs.
No network/downloads. Extracts text only; classifications are a reviewed audit.
"""
import argparse
import hashlib
import json
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--output-dir',required=True,type=Path)
a=ap.parse_args();out=a.output_dir.resolve()
if out.exists() or not out.is_relative_to((ROOT/'builds/phase19b').resolve()):
    raise ValueError('Fresh output under builds/phase19b required')
out.mkdir(parents=True)
index=[]
for name,pages in [
    ('DSP56300FM.pdf',[43,44,72,88,89,90,91,92,93,95,97,98,99,100]),
    ('DSP56724RM.pdf',[96,97,98,99,100,101,102,142,143,253,254,255,256])]:
    p=ROOT/'builds/phase19b/documentation'/name
    r=PdfReader(p)
    text='\n'.join(f'PDF PAGE {i+1} (one-based)\n'+r.pages[i].extract_text() for i in pages)
    with (out/(name+'.pages.txt')).open('xb') as f:f.write(text.encode('utf-8'))
    with (out/(name+'.layout.txt')).open('xb') as f:
        f.write(('\n'.join(f'PDF PAGE {i+1}\n'+r.pages[i].extract_text(extraction_mode='layout')
                          for i in pages)).encode('utf-8'))
    index.append(dict(file=name,SHA256=hashlib.sha256(p.read_bytes()).hexdigest(),
         URL='https://www.nxp.com/docs/en/reference-manual/'+name,pdf_pages_one_based=[i+1 for i in pages],
         note='Direct primary manual; text extraction may lose table alignment. Retain PDF/layout evidence.'))
with (out/'sources.json').open('x',encoding='utf-8',newline='\n') as f:
    json.dump(index,f,indent=2,sort_keys=True);f.write('\n')
print('Manual evidence exported; no DSP execution')
