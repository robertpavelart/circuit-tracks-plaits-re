"""Check the shared-code deletion premise before any new renderer placement."""
import contextlib, hashlib, io, json, runpy, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'builds/phase20f-va-vpre-admission'
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    # Existing helper reconstructs from the read-only instruction cache, verifies
    # original bytes, and exports metadata only. Its instruction arrays stay local.
    with contextlib.redirect_stdout(io.StringIO()):
        d=runpy.run_path(str(ROOT/'plaits/poc/full_audit/reclaim.py'))
    core=d['core']; reduced=bytearray(core)
    start=d['labels']['vpre']; end=d['labels']['smp_post']
    new=d['D'].to_bytes(d['w3'])
    reduced[3*start:3*end]=new+b'\0'*(3*(end-start)-len(new))
    # Tail stays in its original P positions. Only the module's internal labels
    # move; repair the external vret entry. This is a DSP-only caller fixture.
    assert int.from_bytes(core[3*0xd22:3*0xd23],'big')==d['labels']['vret']
    reduced[3*0xd22:3*0xd23]=d['l3']['vret'].to_bytes(3,'big')
    for pc in range(0x2a5e):
        if pc!=0xd22: assert core[3*pc:3*pc+3]==reduced[3*pc:3*pc+3]
    assert core[3*end:]==reduced[3*end:]
    (OUT/'original-core0.be24').write_bytes(core)
    (OUT/'reduced-core0.be24').write_bytes(reduced)
    meta=dict(original_words=len(core)//3,conditional_deletion_words=len(d['words'])-len(d['w3']),
        physical_P_limit=0x4000,original_tail_words=0x4000-len(core)//3,
        conditional_free_words=1196,legacy_restoration_charge=1177,
        free_after_restoring_unchanged_legacy=19,
        module_original=[start,end],module_reduced=[start,start+len(d['w3'])],
        untouched_stock_generator_words=True,untouched_sampler_tail_words=True,
        external_vret_operand_fix=0xd22,
        limitations='DSP caller fixture only, no complete ARM relink/boot/core1. Reduced module deletes BOTH MIDI oscillator paths; not an admitted Plaits layout.',
        source_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'plaits/poc/full_audit/reclaim.py',d['REF']/'tools/vcf21_dsp.py',d['REF']/'tools/dsp_asm_cache.json']})
    (OUT/'placement.json').write_text(json.dumps(meta,indent=2)+'\n')
    # Same reference-style 2ms latest-value sender for all compared machines.
    sys.path.insert(0,str(ROOT/'plaits/poc/midi_vpre'))
    from experiment import Mailbox
    m=Mailbox();cases=[];controls=[]
    for b in range(4096):
        if b%512==0:
            flags=[0,512,1024,512,0,1024,512,0][b//512]
            for code,value in [(19,2|flags),(18,48+b//512*5),(20,100),(17,1),(21,1)]:m.put(code,value)
        if b%96==12:
            for code,value in [(18,36+(b//96)%72),(20,16+(b//96*7)%112),(17,1),(21,1)]:m.put(code,value)
        if b%96==63:m.put(17,0)
        if b%96 in (64,65,66):m.put(17,1);m.put(21,1)
        if b%21==0:m.put(24,[0,42,84,126][(b//21)%4]);m.put(25,(b//21*17)%101)
        word=m.tick(b*2//3)
        cases.append(f'{b} '+('0' if word is None else f'1 3bb0 {word:x}')+'\n')
        # Host Voice stream also exercises internal-envelope, external modulation,
        # level-patched/ping/bypass modes; fixed MODEL=8 throughout.
        note=36+(b%2048)/2048*72
        harm=(b%257)/256; timbre=((b*37)%257)/256; morph=((b*71)%257)/256
        trigger=1 if (b%96<63 or b%96 in (64,66)) else 0
        level=(b%129)/128
        controls.append(f'{b} {note:.9g} {harm:.9g} {timbre:.9g} {morph:.9g} {trigger} {level:.9g} {b//512%3}\n')
    (OUT/'cases.tsv').write_text(''.join(cases))
    (OUT/'controls.tsv').write_text(''.join(controls))
    print(json.dumps(meta,indent=2))
if __name__=='__main__': main()
