#!/usr/bin/env python3
"""Phase16 offline service-read assessment. NO hardware reader or transmitter.

Exports schemas, byte-checked evidence and a FAILED strict read-only gate.
Does not construct service packets, import device APIs, or run firmware.
"""
import argparse,json,re,struct
from pathlib import Path
from ct_static import ROOT,BASE,BIN_HASH,SYX_HASH,sha,save
from ct_resource_audit import read_rows
from ct_host_utility_audit import pack_group,unpack_group
import ct_fw_tool

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',required=True)
    out=Path(ap.parse_args().output_dir).resolve()
    if out.exists():raise SystemExit('Choose a fresh output directory')
    if out==ROOT/'original' or ROOT/'original' in out.parents:raise SystemExit('Protected original/')
    inputs={}
    def read(name):
        raw=(ROOT/name).read_bytes();inputs[name]=sha(raw);return raw
    def emit(name,obj):save(out/name,json.dumps(obj,indent=2,sort_keys=True)+'\n')
    arm=read('firmware/circuittracks-firmware-4486.bin')
    syx=read('original/circuittracks-firmware-4486.syx')
    assert sha(arm)==BIN_HASH and sha(syx)==SYX_HASH
    syxp=ROOT/'original/circuittracks-firmware-4486.syx'
    assert ct_fw_tool.decode_syx(syxp)['firmware']==arm
    assert ct_fw_tool.build_syx(syxp,arm)==syx
    manifest=json.loads(read('firmware/dsp/build-4486/manifest.json'))
    for b in manifest['blocks']:
        for kind in ('stream','payload'):
            raw=read('firmware/dsp/build-4486/'+b[kind+'_file']);assert sha(raw)==b[kind+'_sha256']
    payload=read('firmware/dsp/build-4486/selection0-channel0.payload24.bin')
    read('builds/phase3-selection0-channel0.asm')
    rows=read_rows(ROOT/'builds/phase3-selection0-channel0.asm',payload)
    for pc,t in {
      0x156:'move x0,y:$2000',0x158:'move r0,y:$2001',0x15A:'movec m0,y:$2002',
      0x15C:'movec #$00ffff,m0',0x168:'move a0,y:$2003',0x16A:'move a1,y:$2004',
      0x16C:'move a2,y:$2005',0x189:'move x0,x:$0011',
      0x18C:'movep x:(r0)+,x:$ffff93',0x18F:'movep y:(r0)+,x:$ffff93',
      0x190:'move r0,x:$0010',0x1A4:'move x:(r0)+,x0',0x1A9:'move y:(r0)+,x0',
      0x1AC:'move r0,x:$0010',0x1B1:'movec y:$2002,m0',0x1B3:'rti',
    }.items():assert rows[pc]['text']==t,(hex(pc),t)
    instructions={};arm_text=[]
    old=[ROOT/'builds/phase11/arm-initial/080269E4-08026B1E.asm',
         ROOT/'builds/phase3-arm-transport.asm',ROOT/'builds/phase11/arm-ingress/0801EAE0-0801EB74.asm',
         ROOT/'builds/phase11/arm-buffer/0801EC54-0801ED3C.asm',
         ROOT/'builds/phase11/arm-dispatch/0801F30E-0801F358.asm']
    new=[p for d in sorted((ROOT/'builds/phase16').glob('arm-*')) for p in sorted(d.glob('*.asm'))]
    for p in old+new:
        read(str(p.relative_to(ROOT)))
        for line in p.read_text().splitlines():
            m=re.match(r'([0-9A-F]{8})\s+([0-9a-f]+)\s+(.*)',line)
            if not m:continue
            pc=int(m[1],16);raw=bytes.fromhex(m[2]);assert arm[pc-BASE:pc-BASE+len(raw)]==raw
            instructions.setdefault(pc,[]).append(m[3].split(' ; ')[0])
            if p in new or '269E4' in p.name:arm_text.append(line)
    def has(pc,mnemonic,fragment):assert any(t.startswith(mnemonic) and fragment in t for t in instructions[pc]),(hex(pc),fragment)
    for pc,op,frag in [(0x8026A58,'cmp','#1'),(0x8026AD4,'bl','0x8029344'),
       (0x8026AF4,'strh','#0xa'),(0x8026B08,'bl','0x803924e'),
       (0x8037B30,'strb','#5'),(0x8037B32,'strb','#6'),
       (0x8037B38,'strb','#7'),(0x8037B40,'uxtb','r5'),
       (0x8037B4A,'strb','#-0x1'),(0x8037B5C,'bl','0x8020c90'),
       (0x803B9DA,'b','0x8023414'),(0x8023422,'beq','0x8023414'),
       (0x802950E,'bl','0x803baa2')]:
        if op:has(pc,op,frag)
    def u32(a):return struct.unpack_from('<I',arm,a-BASE)[0]
    assert arm[0x80248AC-BASE:0x80248B1-BASE]==bytes.fromhex('f000202901')
    assert arm[0x8037B70-BASE:0x8037B76-BASE]==bytes.fromhex('f00020290164')
    assert u32(0x8037B68)==0x20006180 and u32(0x8029674)==0x20003D00
    schema={'scope':'NON-EXECUTING description only; strict read-only gate FAILED',
      'outer_request':'F0 00 20 29 01 63 70 5E | packed body | F7',
      'request_minimum_enforced_bytes':9,'well_formed_small_read_request_bytes':25,
      'request_decoded_fields':[
        {'offset':0,'bytes':1,'name':'operation','READ_value':1,'WRITE_value':0,'policy':'never emit WRITE'},
        {'offset':1,'bytes':1,'name':'address selector','values':{'0':'port0 X','1':'port0 Y','2':'port1 X','3':'port1 Y'},'other':'fallback port0 X; future spec rejects'},
        {'offset':2,'bytes':4,'name':'cookie','endian':'little'},
        {'offset':6,'bytes':4,'name':'DSP word starting address','endian':'little'},
        {'offset':10,'bytes':2,'name':'word count','endian':'little','protocol_max':65535,'local_cap_enforced':False}],
      'request_READ_data_slots':'none; complete12-byte header padded to14 raw bytes for two full7-byte groups',
      'request_decode':'269F6 UXTH(frame_length-9);391C6 decodes8 seven-bit bytes to7 raw bytes, whole groups',
      'reply_outer':'F0 00 20 29 01 63 70 5E | packed response | F7',
      'reply_decoded_fields':[{'offset':0,'bytes':1,'name':'status','values':{'2':'accepted, includes count0','3':'invalid starting address','4':'unsupported operation'}},
        {'offset':1,'bytes':1,'name':'echoed selector'},
        {'offset':2,'bytes':4,'name':'echoed cookie','endian':'little'},
        {'offset':6,'bytes':4,'name':'echoed starting address','endian':'little'},
        {'offset':10,'bytes':2,'name':'echoed requested count','endian':'little'},
        {'offset':12,'stride':4,'name':'READ helper return slots','endian':'little','value':'unsigned24-bit DSP word <<8; decode slot>>8'}],
      'reply_padding':'3924E encodes complete7-byte groups including up to6 bytes beyond nominal body; trailing bytes not initialized by read handler; trim by count and discard error payload',
      'reply_frame_length':'37B40 truncates packed_length+9 to8bits; no general large-count safety',
      'no_checksum_field':'none in the reconstructed5E payload; transport integrity not proved here',
      'word_transport':'private read29344 emits address-read plus read-next using six SPI bytes in assumed24bitSHI mode',
      'current_SHI_width':'read handler does not establish24bit mode; interleaving/width preservation UNRESOLVED',
      'maximum_safe_transfer':'NONE certified under strict no-state-change requirement;32 only conditional local scratch capacity'}
    emit('read-protocol-schema.json',schema)
    # Arithmetic fixtures use arbitrary complete groups, NOT service requests.
    for seed in range(256):
        data=bytes((seed+31*i)&255 for i in range(7));assert unpack_group(pack_group(data))==data
    sizes=[]
    for n in [0,1,2,4,8,16,31,32,33,256]:
        raw=12+4*n;groups=(raw+6)//7;packed=8*groups
        if n<=32:
            # Actual small-length group arithmetic from39254..3926A.
            g=(((raw+1)*0x9249)>>18)&255
            if g*7<raw:g=(g+1)&255
            assert g==groups
        sizes.append({'count':n,'nominal_reply_raw_bytes':raw,'rounded_encoder_source_bytes':7*groups,
          'reply_padding_bytes':7*groups-raw,'packed_bytes_small_length_formula':packed,
          'logical_reply_frame_bytes_small_formula':packed+9,
          'private_SPI_bytes':6*n,'SHI_interrupts':2*n,'DSP_target_word_reads':2*n,
          'Y_save_word_writes':9*n,'X_protocol_state_word_writes':3*n,
          'fits_local_scratch_and_encoder_slots':n<=32,
          'status':'capacity arithmetic only; not permission/safety; general large encoder arithmetic wraps'})
    emit('granularity-and-cost.json',{'entries':sizes,
       'scratch_slots':'read dataSP[10,90):128 bytes; encoder outputSP[90,130):160 bytes',
       'nominal32':'32 words fill read scratch;140 raw bytes pack160 bytes with no tail padding',
       'single1':'16 nominal response bytes pack24 bytes;5 unspecified raw pad bytes; full reply33 bytes',
       'strict_safe_positive_count':None,'wall_time_bound':None,
       'wire_time_lower_bound':'48*N/f_SPI for six bytes perprivate read, ignoring GPIO, waits, USB/MIDI, ISR preemption; no frequency/time assumed',
       'atomic_snapshot':False,'freshness':'UNRESOLVED DSP HTX ready timing; STM32 poll is not a proof of sampled epoch'})
    side=[
      {'state':'DSP X10 saved SHI cursor','PC':'190/1AC','class':'PERSISTENT SIDE EFFECT','value':'last_requested_private_address+2 for one word, or A+N+1 for boundedcontiguousN; not restored'},
      {'state':'DSP X11 address/space flags','PC':'189','class':'PERSISTENT SIDE EFFECT','value':'read-address word, bit23 read plus address/bit15space; no restoration'},
      {'state':'DSP Y2000..2002','PC':'156/158/15A','class':'PERSISTENT SIDE EFFECT','value':'savedCPU context perinterrupt; overwritten9 savewords/word total withA save below'},
      {'state':'DSP Y2003..2005','PC':'168/16A/16C','class':'PERSISTENT SIDE EFFECT','value':'A save on address command; CPU registers restored, RAMsavecontents not restored'},
      {'state':'DSP R0,M0,X0,A and hardware interrupt context','PC':'156..1B3','class':'TRANSIENT INTERNAL STATE ONLY','value':'reviewed save/restore plusRTI; M0 temporarilyFFFF'},
      {'state':'DSP HTX/HRX status/FIFO and interrupt servicing','PC':'15E/18C/18F/1A5/1AA','class':'TRANSIENT INTERNAL STATE ONLY','value':'commands consumed, returned andprefetched words queued; timing/preemption incurred'},
      {'state':'requested data word(s), voice/effect/mailbox/scheduler/DMA data','PC':'readbranch only','class':'VERIFIED NO SIDE EFFECT','value':'no direct targetstore/voice/mailbox/DMA setter on valid24bitprivate read; genericdispatcher/concurrency/cache fallout UNRESOLVED'},
      {'state':'normal scheduler/voice/effect/mailbox/DMA end-to-end guarantees','PC':'caller/postdispatch and interleaving','class':'UNRESOLVED','value':'do not promote local absence of directstores to globalnoninterference'},
      {'state':'Selection0/1 on utility branch','PC':'1F308→269E4','class':'VERIFIED NO SIDE EFFECT','value':'no read-mode selection switch; noSelection1 prerequisite; outer housekeeping closure separatelyUNRESOLVED'},
      {'state':'ARM stack/returned value/cookie/reply global20006180','PC':'269E4..26B1A,37B0C','class':'PERSISTENT SIDE EFFECT','value':'scratch/temp stack written; replybuffer contents survive function; receive/transmit queues andGPIO/SPI state modified'},
      {'state':'explicit software interrupt masks/debughalt','PC':'reviewedhandler/SPIread/SHIpaths','class':'VERIFIED NO SIDE EFFECT','value':'no explicitCPSID/PRIMASK/debugHALT/STOP/WAIT on reviewedwell-formedpath; hardwareISRpreemptsDSP andhighercalleeclosure not universal'},
      {'state':'ARM cached destination20003D00 vsDSP X10/X11','PC':'29344/29504..26 compared292F8/29340','class':'UNRESOLVED','value':'scalarread hasno explicitcacheinvalidation, unlikebulk295A4; possible subsequent cachedwrite redirection'}]
    emit('read-side-effects.json',side)
    fixtures=[]
    for space,a in [('X',0x35F),('Y',0x1820),('Y',0x1A1F),('X',0x5F00),('X',0x5FFE),('X',0x5FFF)]:
        fixtures.append({'space':space,'requested':hex(a),'returned_word_address':hex(a),
            'unreturned_prefetch_address':hex(a+1),'saved_X10_after_read':hex(a+2),
            'private_RAM_boundary_concern':space=='X' and a+1>=0x6000,
            'status':'static29344+DSPreadpath formula; no requestconstructed/executed'})
    emit('prefetch-and-boundaries.json',{'entries':fixtures,'actual_map':'conditional part/core0 X6000/Y4000; physical identification remains open',
       'last_X_word5FFF':'extra read6000 outside conditionalprivateRAM; cannot certifyreadinglastword via this helper',
       'read_block_union':'desired[A,A+N); actual[A,A+N+1), underprivateframe/mode/linear assumptions'})
    emit('cache-coherence-obligation.json',{
       'cache':'ARM halfword20003D00; literal29674',
       'writer':'292F8 compares requestedencodedaddress against cache; skips292DC whenequal;29340 publishesrequested+1',
       'scalar_reader':'29344→29504..26 changesDSP cursor/space; no explicitcache update on thiswrapper/genericGPIOpolledSPI chain',
       'contrast':'bulk29528 clearscacheFFFF at2959E/295A4',
       'conditional_example':{'before':'cacheC equalsnextnormalwrite address; read highX A=5F00','after_read':'DSP X10=5F02, ARMcachestillC',
            'next_cached_write':'if callerrequestsC and no invalidatorintervenes, skipaddresssetup and write through DSP saved5F02'},
       'proof_class':'VERIFIED conditionalhelper sequence; actualnormalinterleaving, hiddenaliases/postdispatch invalidation UNRESOLVED',
       'implication':'service sampling may confoundnormalhighX ownership; absence of a serviceWRITE opcode doesnot eliminate protocolstate effects'})
    emit('transport-and-scheduling.json',{
       'logical_transport':'VERIFIED F0/F7 framedMIDI SysEx/service envelope; ingress1EB30 IDs0/1→2484C→1F284→1F30A',
       'callback_registration':'1EC92..96 installs1EB31 via251E8 in200008F0; staticincomingcallback bridge51968/51974 also present',
       'reply_route':'37B0C→20C90 validatesF0/F7/interior7bit and queues throughroutingmask',
       'physical_USB_vs_DIN_vs_proprietary_endpoint':'UNRESOLVED completephysicalingress/descriptor/driverassignment; no hardwareenumeration',
       'Components_origin':'HYPOTHESIS only; exact envelope doesnot identify theapplication',
       'externally_reachable_gate':'NOT-YET-DETERMINED physically; installedframedmessagehandler isVERIFIED',
       'ARM_blocking':'VERIFIED synchronous loops and37960 pollingSPI TX/RX;23414 waits completionflagwithout timeout/yield',
       'DSP_audio':'reviewedSHI ISR preemptsforeground andRTI resumes; no explicitdebughalt/audiostop; glitch-free/schedulability UNRESOLVED',
       'selection':'5E executesbeforelateenableguard andrequiresnoSelection1',
       'additional_postdispatch':'24884→38BA0,1F30Econditionalfanout andotheringresscallbacks; globalside-effectclosure notclaimed',
       'width':'no24bitestablishment inutilityprivate read; mode/interleaving/freshness must bequalified'})
    scenarios=['idle','Synth1 notes','Synth2 notes','bothsynths active','polyphonic notes','patch/preset change',
       'Macro movement','filter/resonance','envelope parameters','effects parameters','transport start/stop',
       'scene/session/project change','MIDI input, only if separatelyauthorized later']
    emit('future-observation-set.json',{'status':'PROPOSED ONLY; blocked by strictgate, no runtimeutility implemented',
       'priority1':{'space':'X','address':'0x35F','count':1,'expected':0,'trigger':'anynonzero: lograwreply/timing/UIstate; stopallocation andsampling, no reset/write/clear'},
       'priority2':[{'space':'Y','start':'0x1820','count':16,'expected':'alternating2CCC/2CEC'},
                    {'space':'Y','start':'0x1A10','count':16,'expected':'alternating2C02/2C24'}],
       'priority3':{'space':'X','sparse_addresses':['0x5F00','0x5F40','0x5F80','0x5FC0','0x5FFE'],
                    'count_per_probe':1,'avoid5FFF':'prefetch6000 boundaryunresolved'},
       'sampling_policy':'initiallymanualsingleword only if a compliantmechanism isestablished; noauto polling now; hypothetical ceiling one totalrequest per2seconds is anESTIMATE, notvalidatedsafe rate',
       'scenarios':scenarios,'time_logging':'hostmonotonicrequest/reply timestamps bound ISRsampletime, notaudioPC203A time',
       'invariant_limit':'5E reads occurinSHI ISR, notat203A; zeros cannot proveeveryentry; nonzero activeprobe mayreflectobserver/cacheeffects or staleHTX, notpure normaldisproof',
       'persistence_limit':'nonzero/change is concern; unchangedzeros misssame-valuewrites, transients, unsampledwords; no sentinels ormathematicalallocationproof'})
    emit('high-X-options.json',[
       {'option':'A all256 inone request','status':'REJECTED localcapacity;5FFFprefetch6000','work':'count256 exceeds32-word scratch; notsafe evenoccasionally'},
       {'option':'B sparse count1','status':'preferredconceptual minimumload IF future compliantpath exists; blockedfor5E now',
        'work':'5 samplewords:30 SPIbytes,10 SHIinterrupts,290 logicalMIDIrequest+replybytes; no timingguarantee',
        'coverage':'missesunsampledwords/transients; rotate offsets onlyafterqualification; neverclaimfreeRAM'},
       {'option':'C smallchunks over time','status':'conditionalfuturealternative, stillblockedfor5E',
        'work':'16x16 wouldtotal1536 SPIbytes,512 SHIinterrupts,1952 logicalframebytes for256wordcoverage, and includesunsafe5FFFprefetch',
        'coverage':'widercoverage, nonatomicsnapshot, higher cumulativeload; lastwordmustnotbeprobed until boundary resolved'}])
    tool={'implemented':False,'file_created':'NO ct_read_dsp.py because mechanism failedstrictgate',
       'architecture_only':'fixedoperationREAD=1; noWRITE constructor/API/rawcommand escape; X/Y explicit,port0 only untilotherportsverified',
       'validation':'allowlistedaddresses/count1 initially; validateinitial/end AND extra prefetchedword againstcorroboratedmap; rejectshared/peripheral/reserved,unknownselectors,count>32',
       'target_identification':'bindexplicitunit/transport andindependentlyconfirmedfirmware/build; protocolprefix/portnamealone insufficient; noactiveprobe generated',
       'dry_run':'defaultofflinefieldsummary/validation only; noport discovery/open/transmit',
       'logging':'timestamps,cookie,status,echoedaddress/space/count,raw32slot and24word,UIscenario; discarderrorpayload/padding, rejectstale/mismatchedframes',
       'rate':'oneinflight; manualinitially; noauto fastpoll/retry; anyrate requiresqualification; provisional2sec intervalnotasafetyproof',
       'excluded':'firmwareupdate,bootloader,writeops,instrumentation,DSPmemorywrites byclient API',
       'limit':'client cannot make stockREAD internally RAM-write-free orsolveHTX/cache/coherence byconstruction'}
    emit('tool-spec-only.json',tool)
    gates={'A_READ_structurally_distinct':'YES','B_no_DSP_private_RAM_modification':'NO',
       'C_persistent_side_effects_excluded':'NO','D_Selection0_allowed':'YES',
       'E_external_stock_transport_verified':'NOT-YET-DETERMINED',
       'F_tool_can_omit_service_WRITE':'YES','G_passive_observation_via5E_justified':'NO'}
    emit('safety-gate.json',{'answers':gates,'strict_route_verdict':'NO compliant5E read route; no hardwareactionrecommended',
       'F_scope':'tool neveremits WRITE subcommand; doesNOT makeDSPramwritesimpossible',
       'other_passive_route':'UNRESOLVED; standardOnCE peek isnotprovednonhalting/stateless',
       'candidate_availability':'NOT-YET-DETERMINED','X35F_invariant':'NOT-YET-DETERMINED',
       'next':'useexact-chip andboarddocumentation to assess a genuinelypassive data-observationfacility; do notuse5E orhalt/inject viaOnCE'})
    emit('primary-documentation.json',{'part_premise':'exactDSP chip/core assignment stillunverified',
       'DSP56724RM':{'url':'https://www.nxp.com/docs/en/reference-manual/DSP56724RM.pdf','section':'4.3.5','fact':'OnCE/JTAG described, but genericnonintrusive wording alone doesnot satisfy strictstate/nohaltcriteria'},
       'DSP56300FM':{'url':'https://www.nxp.com/docs/en/reference-manual/DSP56300FM.pdf','sections':['7.2.4 OGDBR','7.2.5 tracebuffer','7.2.6 serialprotocol'],
         'fact':'documented memoryinspection forcesinstruction intoOGDBR; debugprotocol waitsDebugmodeack; tracebuffer storesflowaddresses andreadsadvancepointer, notprivateRAM datatrace',
         'conclusion':'documentedpeek/tracefeatures areNOT a verifiedstrictread-only,nonhalting solution; otherhardwarefacilities unresolved'}})
    save(out/'arm-witnesses.asm','\n'.join(arm_text)+'\n')
    save(out/'dsp-witnesses.asm','\n'.join(rows[p]['line'] for p in sorted(rows) if 0x156<=p<0x1B4)+'\n')
    for name,h in inputs.items():assert sha((ROOT/name).read_bytes())==h
    emit('validation.json',{'inputs_SHA256':inputs,'script_SHA256':sha(Path(__file__).read_bytes()),
       'baseline_hashes_match':True,'extract_hashes_match':True,'decoded_equals_BIN':True,'SYX_roundtrip_equal':True,
       'ARM_DSP_bytes_checked':True,'codec_fullgroup_fixtures':256,'mode':'STATICONLY; no servicepacket/hardwarecode constructed orrun'})

if __name__=='__main__':main()
