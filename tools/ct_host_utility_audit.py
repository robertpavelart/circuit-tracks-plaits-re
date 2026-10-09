#!/usr/bin/env python3
"""Phase11 offline request/cursor/selector evidence replay, not an emulator.

No hardware APIs, packet transmission, firmware edits, or implementation code.
Byte-checks reviewed evidence, exports scoped facts and explicit open premises.
Requires fresh output directory. No free-RAM inference from absent references.
"""
import argparse,json,re,struct
from pathlib import Path
from ct_static import ROOT,BASE,BIN_HASH,SYX_HASH,sha,save
from ct_resource_audit import read_rows
import ct_fw_tool

def emit(out,name,obj):
    save(out/name,json.dumps(obj,indent=2,sort_keys=True)+'\n')

def unpack_group(e):
    assert len(e)==8 and all(0<=x<128 for x in e)
    return bytes((((e[i]<<(i+1))+(e[i+1]>>(6-i)))&255) for i in range(7))

def pack_group(d):
    assert len(d)==7
    out=[d[0]>>1]
    out.extend(((d[i-1]&((1<<i)-1))<<(7-i))+(d[i]>>(i+1)) for i in range(1,7))
    out.append(d[6]&127)
    return bytes(out)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir',required=True)
    out=Path(ap.parse_args().output_dir).resolve()
    if out.exists():raise SystemExit('Choose a fresh output directory')
    if out==ROOT/'original' or ROOT/'original' in out.parents:raise SystemExit('Protected original/')
    arm=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
    syxp=ROOT/'original/circuittracks-firmware-4486.syx';syx=syxp.read_bytes()
    assert sha(arm)==BIN_HASH and sha(syx)==SYX_HASH
    decoded=ct_fw_tool.decode_syx(syxp)
    assert decoded['firmware']==arm and ct_fw_tool.build_syx(syxp,arm)==syx
    manifest=json.loads((ROOT/'firmware/dsp/build-4486/manifest.json').read_text())
    extracts={}
    for b in manifest['blocks']:
        for kind in ('stream','payload'):
            p=ROOT/'firmware/dsp/build-4486'/b[kind+'_file'];digest=sha(p.read_bytes())
            assert digest==b[kind+'_sha256'];extracts[str(p.relative_to(ROOT))]=digest
    inputs={};instructions={}
    evidence=sorted((ROOT/'builds/phase11').rglob('*.asm'))
    evidence.append(ROOT/'builds/phase10/arm-dispatch/0801F2A0-0801F326.asm')
    for p in evidence:
        # DSP exports are generated below, and a repeat must not ingest itself.
        if p.parent.name.startswith(('replay','verified')):continue
        for line in p.read_text().splitlines():
            m=re.match(r'([0-9A-F]{8})\s+([0-9a-f]+)\s+(.+)',line)
            if not m:continue
            pc=int(m[1],16);raw=bytes.fromhex(m[2])
            assert arm[pc-BASE:pc-BASE+len(raw)]==raw,(p,hex(pc))
            instructions.setdefault(pc,[]).append(m[3].split(' ; ')[0])
        inputs[str(p.relative_to(ROOT))]=sha(p.read_bytes())
    def has(pc,mnemonic,fragment):
        assert any(t.startswith(mnemonic) and fragment in t for t in instructions[pc]),(hex(pc),fragment)
    has(0x801F28E,'cmp','#0x5e');has(0x801F290,'beq','0x801f308')
    has(0x801F30A,'bl','0x80269e4');has(0x8024880,'bleq','0x801f284')
    has(0x8026A08,'ldrh','#0xa');has(0x8026A94,'uxth','r2, r5')
    has(0x8026A9A,'bl','0x80292f8');has(0x8026AD4,'bl','0x8029344')
    has(0x80291F2,'lsrs','r0, r5, #0x18')
    has(0x8049A6E,'cmp','#0x40');has(0x8049C0A,'bl','0x80292f8')
    def u32(addr):return struct.unpack_from('<I',arm,addr-BASE)[0]
    assert arm[0x80248AC-BASE:0x80248AC-BASE+5]==bytes.fromhex('f000202901')
    assert u32(0x801EDE0)==0x801EB31 and u32(0x8049C2C)==0x74000700
    assert u32(0x8049C30)==0x7FFFF0
    fields=[
      {'offset':0,'bytes':1,'name':'operation:0 write,1 read; others response status4'},
      {'offset':1,'bytes':1,'name':'mode:0 port0/X,1 port0/Y,2 port1/X,3 port1/Y; others port0/X fallback'},
      {'offset':2,'bytes':4,'name':'opaque echoed cookie; unaligned little-endian'},
      {'offset':6,'bytes':4,'name':'requested initial address; unaligned little-endian'},
      {'offset':10,'bytes':2,'name':'unsigned transfer count; little-endian'},
      {'offset':12,'stride_bytes':4,'name':'write consumes one byte per slot; read replies store32-bit return per slot'}]
    emit(out,'request-schema.json',{'entry':'0x080269E4','signature':'void-like utility(Context *ctx); return value not a stable status ABI',
      'context_fields':{'0':'reply routing mask','4':'Buffer * containing pointer+0, byte length+4'},
      'outer_header':{'prefix5':'F0 00 20 29 01','byte5':'0x63','byte6':'0x70','byte7':'request ID0x5E','minimum_bytes':9},
      'decoded_fields':fields,'reply_statuses':{'2':'accepted (including zero count)','3':'invalid starting address','4':'unsupported operation'},
      'codec':'8 seven-bit bytes ->7 bytes; reverse for replies; group-rounded reads/writes',
      'count_checks':'no local <=32 check, complete backing-buffer/publisher length constraints unresolved',
      'write_reply_payload':'write branches do not fill the read-response scratch area; content unspecified by this routine'})
    emit(out,'dispatch-map.json',[
      {'consumer':'0x0801EB30','condition':'input identifier0 or1','next':'0x0802484C','class':'external framed-message callback'},
      {'consumer':'0x0802484C','condition':'prefix5, byte5=63, byte6=70, length>=9','next':'0x0801F284','class':'service protocol family'},
      {'consumer':'0x0801F284','condition':'byte7=5E','next':'0x080269E4','class':'SERVICE/DIAGNOSTIC; no Selection1 guard'},
      {'consumer':'0x0801F284','condition':'byte7=60','next':'selection/flag controls; restoration branch','class':'mode control; separate from5E'},
      {'consumer':'0x0801F30E','condition':'global flag bit4','next':'other command consumers','class':'guard occurs AFTER utility call'},
      {'consumer':'0x080269E4','condition':'reply','next':'0x0803924E ->0x08037B0C (ID5E)','class':'response, not an internal request publisher'}])
    modes=[]
    for mode in range(256):
        modes.append({'mode':mode,'port':1 if mode in (2,3) else 0,'private_space':'Y' if mode in (1,3) else 'X',
                      'validated_mode':mode in (0,1,2,3),'other_mode_behavior':'fallback, not rejection' if mode>=4 else ''})
    emit(out,'mode-domains.json',modes)
    # Every candidate word is individually within accepted private start bounds.
    candidate=list(range(0x5F00,0x6000));assert all(x<0x8000 for x in candidate)
    assert all((value>>8)==0 for value in range(256))
    emit(out,'utility-domains.json',{'private_start':{'minimum':0,'maximum':0x7FFF},
      'shared_start':{'minimum':0x30000,'maximum':0x37FFF},'count':{'minimum':0,'maximum':0xFFFF,'local_clamp':False},
      'stride_words':1,'alignment':'word address; no multiword alignment check',
      'private_effective_header':'UXTH(start + space_flag + i); DSP address=header&7FFF; space=header bit15',
      'end_check':False,'candidate_word_count_with_valid_single_word_start':len(candidate),
      'private_write_DSP_word':0,'private_write_reason':'LDRB gives0..255;291E0 serializes bits31..8',
      'shared_write_DSP_word':'input byte <<8 after the two ARM shifts and upper24 serialization',
      'reachability':'SERVICE-ONLY in recovered call graph; structurally callable with Selection0 active',
      'assumptions':'well-formed backed buffer and initialized transport/cursor state; no request sent or firmware executed',
      'ordinary_audio_UI_publishers':'none established for request5E; not a universal indirect-call proof'})
    # Deterministic codec mechanics tests: no outer packet or candidate request generated.
    for seed in range(256):
        d=bytes((seed+31*i)&255 for i in range(7));assert unpack_group(pack_group(d))==d
    emit(out,'codec-checks.json',{'fixtures':256,'roundtrip_equal':True,
      'scope':'one full group; does not prove malformed-length or buffer safety'})
    payload=(ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin').read_bytes()
    rows=read_rows(ROOT/'builds/phase3-selection0-channel0.asm',payload)
    for pc,t in ((0x260A,'move #$001820,r0'),(0x260C,'move #$002ccc,x0'),
                 (0x260E,'move #$002cec,x1'),(0x2610,'move #$001a10,r1'),
                 (0x2612,'move #$002c02,y0'),(0x2614,'move #$002c24,y1'),
                 (0x1F68,'move y:>(r6+32),r1'),(0x1F6A,'move y:>(r6+33),r3')):
        assert rows[pc]['text']==t
    cursors=[]
    for bank,table,bases in ((0,0x1820,(0x2CCC,0x2CEC)),(1,0x1A10,(0x2C02,0x2C24))):
        for i in range(16):
            base=bases[i%2];cursors.append({'bank':bank,'Y_cell':hex(table+i),
              'initial_X_cursor':hex(base),'X_start':hex(base),'X_end_exclusive':hex(base+32),
              'status':'VERIFIED init value + conditional32/linear-AGU footprint; foreign writers/global entry unresolved'})
    assert max(int(r['X_end_exclusive'],16) for r in cursors)==0x2D0C
    emit(out,'effect-cursors.json',{'init_PC':'P:260A..2623; eight iterations, two cells per table',
      'cells':cursors,'max_conditional_X_address':'0x2D0B',
      'local_preservation':'1F8C/1F98 write other Y fields; 1F13 writes coefficient region, not cursor table, under linear setup',
      'global_closure':'UNRESOLVED all indirect Y writers and modifiers/reachability; not universal max',
      'modifier_census':[{'PC':hex(pc),'instruction':r['text']} for pc,r in rows.items()
                         if re.search(r'\bm[1367]\b',r['text'])]})
    selector=[]
    for index in range(64):
        base=0x1D8D+4*index;selector.append({'index':index,'X_start':hex(base),'X_end_exclusive':hex(base+3)})
    assert selector[-1]['X_end_exclusive']=='0x1e8c'
    emit(out,'selector7.json',{'publisher':'ARM49C0A writes Y2C; data low nibble7 in both branches',
      'index_producer':'49A50/64/66/6C/6E: first argument0..63 ->49BBC writes X:C00',
      'data_source':'X:C01..C03 from49BCC/49BDC/49BEA','DSP_copy':'P:1CBB..1CC7; three words, +1',
      'destinations':selector,'maximum_X_address':'0x1E8B',
      'mode':'recovered loader path49A1C->49A80; outer loader reachability classification partial',
      'exclusion':'VERIFIED local publisher bound excludes candidate under retained linear M1 and unmodified staging',
      'foreign_publisher_closure':'UNRESOLVED full arbitrary addressed writes/interleaving; not disproved by no direct publisher'})
    save(out/'dsp-witnesses.asm','\n'.join(r['line'] for pc,r in rows.items()
      if any(lo<=pc<hi for lo,hi in ((0x156,0x1B4),(0x1C53,0x1CCF),(0x1E15,0x1FA8),(0x260A,0x262B))))+'\n')
    emit(out,'allocation-verdict.json',{'candidate':'channel-zero X:[5F00,6000)',
      'service_overlap':'VERIFIED protocol path admits each word individually; not an observed request',
      'normal_runtime_occupancy':'not established','after_init_availability':'UNRESOLVED / POTENTIALLY AVAILABLE',
      'search':[{'words':n,'placements':257-n,'verified_available':[]} for n in (256,128,64)],
      'remaining':'global effect cursor/AGU, nonparameter traffic and reconfiguration/alias closure',
      'alternative_search':'not triggered: no disqualification or proved single unavoidable unknown',
      'static_limit':'remaining proofs potentially static; actual request occurrence/physical alias assignment unobserved'})
    emit(out,'provenance.json',{'BIN_SHA256':sha(arm),'SYX_SHA256':sha(syx),'CRC':hex(decoded['crc']),
      'roundtrip_identical':True,'extracts':extracts,'ARM_inputs':inputs,
      'script_SHA256':sha(Path(__file__).read_bytes()),'mode':'STATIC ONLY; no full outer packets generated'})

if __name__=='__main__':main()
