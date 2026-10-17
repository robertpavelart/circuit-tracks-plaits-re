"""Read-only reference consumption; creates DSP-only offline fixtures in CIRCUIT."""
import base64, hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REF = Path(r'C:\Proj SSD\CODEX\CIRCUITS-HACKS-RC-main\CIRCUITS-HACKS-RC-main')
OUT = ROOT / 'builds/phase20d-midi-vpre/fixture'

def sha(b): return hashlib.sha256(b).hexdigest()

def main():
    if OUT.exists(): raise RuntimeError('Fresh fixture required')
    stock = (ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
    assert sha(stock) == 'b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da'
    page = (REF/'tools/rc_uploader.html').read_text(encoding='utf-8')
    line = next(x for x in page.splitlines() if x.startswith('const PATCHES = '))
    patch = json.loads(line[len('const PATCHES = '):].rstrip(';'))['B1.3']
    img = b''.join(stock[o[1]:o[1]+o[2]] if o[0] == 0 else base64.b64decode(o[1]) for o in patch['ops'])
    man = json.loads((REF/'firmware/b1.3/manifest.json').read_text())
    assert sha(img) == man['image_sha256']
    ptr = int.from_bytes(img[0x19700:0x19704], 'little') - 0x08010000
    words = int.from_bytes(img[ptr:ptr+3], 'big')
    core = img[ptr+6:ptr+6+3*words]
    labels = {k:int(v,16) for k,v in man['report']['sc16']['dsp_labels'].items()}
    # Freeze the seven-word arithmetic and allocation. Only address operands,
    # output base and the top-level return convention change.
    source = ROOT/'builds/phase20c-pstate/source-v7/high-x/variablesaw.asm'
    text = source.read_text()
    mapping = {**{0x20+i:0x3e00+i for i in range(7)},
               **{0x30+i:0x3e50+i for i in range(3)},
               **{i:0x3e58+i for i in range(3)}}
    text = re.sub(r'x:>\$([0-9a-f]{6})', lambda m:f'x:>${mapping[int(m[1],16)]:06x}', text)
    assert text.count('move #>$000000,r0') == 1
    text = text.replace('move #>$000000,r0','move #>$003e00,r0')
    assert text.count('jmp @done') == 1
    text = text.replace('jmp @done','rts')
    OUT.mkdir(parents=True)
    (OUT/'reference-core0.be24').write_bytes(core)
    (OUT/'variablesaw.asm').write_text(text,encoding='utf-8')
    (OUT/'labels.txt').write_text('\n'.join(f'{k} {v:x}' for k,v in labels.items())+'\n')
    protected = [ROOT/'plaits/poc/fixed_model.py', source,
                 ROOT/'builds/phase19a/core-build/replay_core.lib',
                 REF/'tools/vcf21.py',REF/'tools/vcf21_dsp.py',REF/'tools/dsp_session.py',
                 REF/'tools/rc_uploader.html',REF/'firmware/b1.3/manifest.json']
    info = dict(reference_image_sha256=sha(img),core0_sha256=sha(core),words=words,
                sealed_renderer_source=str(source),sealed_renderer_sha256=sha(source.read_bytes()),
                adapter_changes='Absolute X operands, output base, top-level JMP done -> RTS only; arithmetic and instruction order unchanged',
                protected={str(p):sha(p.read_bytes()) for p in protected},
                reference_files_written=False,flash_image_written=False,
                layout={'state_X':[0x3e00,0x3e07],'workspace_X':[0x3e20,0x3e60],
                        'controls_X':[0x3e50,0x3e53],'spills_X':[0x3e58,0x3e5b],
                        'output_Y':[0x3e00,0x3e20], 'ring_Y':[0x1000,0x1040],
                        'state_canaries_X':[0x3dff,0x3e07], 'workspace_canaries_X':[0x3e1f,0x3e60],
                        'output_canaries_Y':[0x3dff,0x3e20],
                        'renderer_P_origin':0x400,'adapter_P_origin':0x800,
                        'P_qualification':'Synthetic fixture overlay of retired stock synth code; not a deployable allocation. No firmware container generated.'})
    (OUT/'preparation.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps({'fixture':str(OUT),'words':words,'labels':{k:hex(labels[k]) for k in ['vpre','vchan','vc2_ngr','vc2_nosc','sc_init']}}))

if __name__ == '__main__': main()
