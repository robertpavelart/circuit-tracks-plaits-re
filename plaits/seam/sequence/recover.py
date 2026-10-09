"""Bounded Phase20B5 static export. Reads existing evidence; never runs firmware."""
import argparse, csv, hashlib, json, struct, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools'))
from ct_phase4_trace import arm_evidence
BASE = ROOT/'builds/phase20b-sequence'
PREV = ROOT/'builds/phase20b-projectassoc/final-v2'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def obj(p): return json.loads(p.read_text(encoding='utf8'))
def dump(out, name, value):
    with (out/name).open('x', encoding='utf8', newline='\n') as f:
        json.dump(value, f, indent=2, sort_keys=True); f.write('\n')
def table(out, name, rows):
    with (out/name).open('x', encoding='utf8', newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def parse_pattern(project, offset=740):
    data=project[offset:offset+3240]
    if len(data)!=3240: raise ValueError('Truncated pattern')
    steps=[]
    for s in range(32):
        r=data[28*s:28*(s+1)]
        steps.append(dict(step=s, file_offset=offset+28*s, raw=list(r), occupancy_mask=r[0],
            occupancy_metadata=r[1:4].hex(), records=[dict(record=i, occupied=bool(r[0]&(1<<i)),
            raw=list(r[4+4*i:8+4*i]), note_key=r[4+4*i], duration_encoded=r[5+4*i],
            substep_encoded=r[6+4*i], level_encoded=r[7+4*i]) for i in range(6)]))
    lanes=[dict(lane=i, file_offset=offset+936+192*i,
        step_records=[list(data[936+192*i+6*s:942+192*i+6*s]) for s in range(32)]) for i in range(12)]
    return dict(status='VERIFIED serialized geometry; PARTIAL musical/runtime interpretation',
        project='project0', group=0, pattern=0, offset=offset, bytes=3240,
        patterns_per_group=8, steps_capacity=32, step_stride=28,
        pattern_header_offset=896, header_raw=list(data[896:936]),
        header_halfword=struct.unpack_from('<H',data,896)[0],
        active_pattern_length=None, length_hypothesis='HYPOTHESIS: halfword15 may encode last step, hence16; not admitted as playback length',
        header_evidence='3DC34..56 copies +380 halfword and +382/+383 bytes into property fields0/1/2',
        automation_offset=936, automation_lanes=12, lane_stride=192, automation_record_stride=6,
        duration_evidence='3F856..886 encodes min(96,6*quotient+floor(6*remainder/rate)), with zero changed to1',
        note_evidence='3F350..380 compares occupied note key and substep; 3F88A..89C writes duration/substep/seven-bit level',
        steps=steps, automation=lanes)
def admitted(event, ordering, slot, histories, modes, equivalence):
    return all((event,ordering,slot,histories,modes,equivalence=='MATERIALLY EQUIVALENT'))
def recover(out):
    out=out.resolve()
    if out.exists() or out==BASE or not out.is_relative_to(BASE): raise ValueError('Fresh phase20b-sequence child required')
    guards={ROOT/'original/circuittracks-firmware-4486.syx':'bd2d294bafa88fdec7ae1f5fcaaa13158323969c5a40f83405a72e4ad329a0bd',
      ROOT/'firmware/circuittracks-firmware-4486.bin':'b897e0f01c403974eafae32074876234f2da7ef834796a485993acf01423f8da',
      ROOT/'firmware/dsp/build-4486/selection0-channel0.payload24.bin':'b6bae7da85664372bb07e1499063aacfd695b0049cfa2e5eedc34353099e5855'}
    for p,h in guards.items(): assert sha(p)==h
    before={p:sha(p) for p in PREV.rglob('*') if p.is_file()}
    project_path=PREV/'immutable/project0.ncs'; project=project_path.read_bytes()
    assert sha(project_path)==obj(PREV/'patch-identity.json')['project_sha256']
    arm=(ROOT/'firmware/circuittracks-firmware-4486.bin').read_bytes()
    evidence=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p), byte_checked_rows=arm_evidence(p,arm))
        for p in sorted((BASE/'evidence').glob('*.asm'))]
    assert all(e['byte_checked_rows'] for e in evidence)
    # Reviewed vtable, not speculative direct-call matching.
    vtable=list(struct.unpack_from('<10I',arm,0x4a5b4))
    assert vtable==[0x803fc5f,0x803fcf5,0x803f61d,0x803f299,0x803f5b1,0x803f62b,0x803f67d,0x801d02b,0x802520b,0x803fe25]
    mapping=list(arm[0x49080:0x49094]); assert mapping==[0,0,0,1,0,2,0,3,0,4,0,5,0,6,0,7,0,255,0,255]
    pattern=parse_pattern(project)
    assert pattern['steps'][0]['occupancy_mask']==3
    assert pattern['steps'][0]['records'][0]['raw']==[51,18,0,106]
    assert pattern['steps'][0]['records'][1]['raw']==[82,2,0,106]
    consumers=[
      ('0800AF46','group accessor','project+6540*track+2E4 for literal0/1','VERIFIED'),
      ('0801FD34','constructor binding','literal group0 source -> 1FD84/2E2D8','VERIFIED'),
      ('0802E35C','child constructor','group0 source passed on stack ->3F1F0; child parent+0C','VERIFIED'),
      ('0803F260','retained source pointer','child+48 stores group source','VERIFIED'),
      ('0803DC16','editor/view binding','copies header; not a chronological playback witness','VERIFIED'),
      ('0803F298','note recording/state consumer','group+CA8*pattern+1C*step; occupied record key/substep match','VERIFIED'),
      ('0803F7BE','duration/record update','six-bit occupancy and key/substep match; writes four-byte note record','VERIFIED'),
      ('0801D02A','automation lane accessor','child+48 +CA8*pattern +C0*lane +3A8','VERIFIED'),
      ('0803FC20','pending automation setter','+34 bounds12 lanes; +28 staging array; +2C bitmap notification','VERIFIED'),
      ('0803FD32','time tuple derivation','current/previous tuples and rate/boundary/config state','VERIFIED'),
      ('0803FE24','property notification consumer','retained state gates calls and pending-value processing','VERIFIED'),
      ('080400A4','automation interpolation writer','old/current staged values; half or one-third weights; FF handling','VERIFIED'),
      ('08040188','automation record writer','write step*6+converted substep; retain prior interpolation state','VERIFIED'),
      ('0803F8D4','note property publication','same pointer notification after internal recording/state changes','VERIFIED'),
      ('UNRESOLVED','sound playback dispatch','complete timeline ->497CA/allocator/DSP not established','UNRESOLVED')]
    out.mkdir(parents=True)
    dump(out,'pattern0-structure.json',pattern)
    table(out,'sequencer-consumer.csv',[dict(address=a,role=b,dataflow=c,status=d) for a,b,c,d in consumers])
    edges=[('1FD34','AF46','direct group accessor'),('1FD84','2E2D8','direct constructor'),
      ('2E35C','3F1F0','direct group0 child'),('3F242','3FB10','base constructor; final stack count12, not note-domain139'),
      ('3FC5E','3FD32','tuple derivation'),('3FC5E','3F298','vtable+0C; storage/recording'),
      ('3FE24','3F62A','vtable+14; guarded boundary handling'),('3FF0E','400A4','pending interpolation'),
      ('3FF1A','40188','pending record write'),('400EA','1D02A','vtable+1C lane pointer'),
      ('401C6','1D02A','vtable+1C lane pointer'),('2E62C','3FC20','mapped staging, enable conditional')]
    dump(out,'playback-callgraph.json',dict(status='PARTIAL; constructor and storage consumer edges, not full audible playback timeline',
      edges=[dict(caller=a,callee=b,meaning=c) for a,b,c in edges],vtable_address='0805A5B4',vtable=vtable,
      caveats=['Editor2D7C4/3CF58 and second2E2D8/3F1F0 objects are distinct',
       '2E56A routes to recording vtable; not proven physical note-on',
       '2520A is BX LR stub; following unrelated file code is not a sequencer',
       'Linear evidence windows include literals and partial boundary instructions; byte checks alone do not prove code reachability']))
    dump(out,'track-association.json',dict(status='PARTIAL',literal_group=0,accessor_track_argument=0,
      group_source='projectbase+2E4',child='2E2D8 parent+0C ->3F1F0 child+48 source',
      associated_property_inputs=['r7+8','r7+48','editor child+0C'],
      logical_patch_bank=0,logical_bank_source='prior projectassoc F442/3BE60',
      physical_track_label=None,category_route_at_event=None,DSP_voice_slot=None,
      missing='Full event frontend/track route to497CA; group position alone is not Synth1 proof'))
    binding=obj(PREV/'patch-identity.json')
    binding.update(playback_active_patch=None,playback_branch=None,
      playback_status='UNRESOLVED: retained identity/active branch and scheduler context missing',
      conditional_partial_merge='If active authored bank0, macro/keyboard branch yields cached bytes; does not preserve authored patch')
    dump(out,'patch-playback-binding.json',binding)
    ordering=[('F442','F450/3BBE2','full-copy branch only','VERIFIED CONDITIONAL'),
      ('F454','F49C','macro/keyboard branch only','VERIFIED CONDITIONAL'),
      ('35F84','3602A publication','within original correction recompute','VERIFIED local arithmetic'),
      ('3FF0E/400A4','3FF1A/40188','same pending-value branch: interpolation write before current record write','VERIFIED local order'),
      ('patch load','first automation application','unknown active branch and notification timeline','UNRESOLVED'),
      ('automation callback','note-on scheduling','storage notification is not audible dispatch order','UNRESOLVED'),
      ('note dispatch','voice allocation/DSP publication','exact event and allocator history missing','UNRESOLVED')]
    table(out,'playback-ordering.csv',[dict(before=a,after=b,condition=c,status=d) for a,b,c,d in ordering])
    first=pattern['steps'][0]
    dump(out,'first-note-event.json',dict(status='PARTIAL serialized candidates; runtime event UNRESOLVED',qualified=False,
      group=0,pattern=0,first_occupied_serialized_step=0,
      candidates=[r for r in first['records'] if r['occupied']],
      exact_first_dispatched_note=None,exact_velocity=None,exact_gate_time=None,exact_microtime=None,
      probability_or_condition=None,track_route=None,bank_at_dispatch=None,voice_slot=None,
      reason='Simultaneous encoded substep0 candidates are not uniquely ordered; playhead, enabled state, traversal, note publication and allocator history missing'))
    auto=[]
    for lane in pattern['automation']:
        values=[v for row in lane['step_records'] for v in row]
        auto.append(dict(lane=lane['lane'],identity='numeric lane only; material callback identity UNRESOLVED',
          mapping_evidence='8059080 input pairs0..7 map group0 lanes0..7; lanes8/9 not mapped by these pairs',
          first_step_raw=' '.join(f'{v:02X}' for v in lane['step_records'][0]),
          non_FF_bytes=sum(v!=255 for v in values),stored_non_FF_values=' '.join(map(str,[v for v in values if v!=255])),
          interpolation='400A4 state-dependent mean/third-weight interpolation WRITES; not proof of playback interpolation mode',
          previous_value=None,effective_before_note=None,status='VERIFIED raw data; UNRESOLVED event-time value'))
    table(out,'automation-before-note.csv',auto)
    controls=[]
    with (PREV/'control-boundary.csv').open(newline='',encoding='utf8') as f:
        for r in csv.DictReader(f):
            controls.append(dict(field=r['field'],authored_stored_recompute=r['authored_DSP'],
              cached_stored_recompute=r['cached_DSP'],stored_relation=r['relation'],runtime_value=None,
              event_relation='UNRESOLVED',source=r['ARM_sink'],status='CALCULATED conditional prior result; no event recomputation'))
    with (PREV/'material-equivalence.csv').open(newline='',encoding='utf8') as f:
        for r in csv.DictReader(f):
            if r['field'].startswith('ID'):
                controls.append(dict(field=r['field'],authored_stored_recompute=r['authored'],cached_stored_recompute=r['cached'],
                  stored_relation=r['relation'],runtime_value=None,event_relation='UNRESOLVED',source=r['destination'],status='CONDITIONAL prior corrected value; runtime unknown'))
    table(out,'effective-controls.csv',controls)
    dump(out,'equivalence.json',dict(stored_load_context='MATERIALLY DIFFERENT',first_note_runtime='INSUFFICIENT EVIDENCE',
      effective_controls_recomputed=False,event_relations={r['field']:'UNRESOLVED' for r in controls},
      reason='No qualified first-event automation timeline; identity is not inferred from file name or unchanged assignments'))
    dump(out,'voice-allocation.json',dict(status='UNRESOLVED',slot=None,forced_slot0=False,
      recording_slots_are_not_DSP_voices=True,missing=['event frontend route','active/released notes','allocator age and occupancy','steal/reset history'],
      reused_source='notes/stock-note-history.md; no repeated P657 analysis'))
    dump(out,'history-origin.json',dict(status='UNRESOLVED',bounded_numerical_origin=False,
      Y_words=['5AB','5AC','5AD','5AE','5B7','5B8'],values=None,
      exclusion='Selected trigger clears [5AF,5B7) and [5BD,5C5); none of these six is included',
      candidates={k:'No numerical last-writer chain for selected invocation' for k in ['project start','patch load','allocation','algorithm reset','parameter recompute','voice steal']},
      y91=obj(PREV/'y91-provenance.json')))
    snapshot=dict(status='SPECIFICATION ONLY; NOT ACQUIRED',boundary='P:9D9 after original32-word generation, stop before P:A95 peripheral tail',
      purpose='Stock-only post seam replay; does not qualify generator/P657 replay or firmware integration',
      provenance=['unchanged firmware/payload/table hashes','actual patch bytes/hash and active bank','actual voice slot and Q/S pointers','project/pattern/step/subtick and event identity','single coherent epoch; timestamp/interrupt state; no invented reset defaults'],
      CPU=['PC=9D9','SR including arithmetic/scaling/sticky/loop flags','OMR/memory mapping','R0..R7,N0..N7,M0..M7','A/B full56-bit,X0/X1/Y0/Y1','SP,SC,LA,LC,LF,FV and all active SSH/SSL stack entries','pending interrupt state/eligibility or qualified exclusion throughA95'],
      minimal_replay_ranges=[dict(space='X',range='[Q+30,Q+43)',Q='57B+4A*i (hex)',slot0='[5AB,5BE)',why='prepared post selectors/targets and gain delta/current; X stride differs from Y'),
       dict(space='Y',range='[S+12,S+1A)',S='59F+28*i (hex)',slot0='[5AB,5B9)',why='six nonlinear/control histories plus eight recursive words'),
       dict(space='X',range='[2C46,2C67)',why='32 natural generator outputs plus material guard'),
       dict(space='Y',range='7,19,1A',why='coefficient pointer restore and modifier restore words'),
       dict(space='X',range='0,39,3A,3B,3C,40,CC; pointer-selected mode-specific scratch inputs',why='block/ramp/shift/context/group select; capture actual pointers, not baseline defaults'),
       dict(space='X',range='CC=0 ->[2DF0,2E10); CC!=0 ->[2E50,2E70)',why='A82..88 chooses group; A8E reads previous accumulation before MAC/store. For minimum capture only selected32 words'),
       dict(space='X',range='[1600,1940),[2200,2400)',why='coefficient/nonlinear uploaded tables; existing bytes only if exact runtime identity verified'),
       dict(space='Y',range='actual offset-selected sequences; selected5/5 ->[F64,F69)',why='conservative capture; may omit at9D9 only after originalC2D overwrite-before-read is qualified')],
      omitted_upstream_from_post_only=['X:[2D5,363) controls/mod rows; prepared per-voice post words suffice locally','Y:[8F,92) modulation results; prepared targets suffice locally','initial R0 is reloaded at9D9; capture for full state comparison only','already-overwritten scratch outputs; capture group accumulation INPUT buffer selected by live pointers'],
      extra_for_event_provenance=['X:[2D5+100*b,363+100*b) bank controls/mod rows','Y:[8F,92)','actual ARM activepatch/corrections/macros','player +0C..24 tuple/config sources,+28 staging13 bytes,+2C bitmap,+35 phase,+38 bitmap,+3C previous12 bytes,+40..43 state,+44 enable,+48 group pointer,+4C note publication,+50 rate source; relevant packed note records','allocator selected slot plus preceding lifecycle and voice source records'],
      unresolved_closure='Mode-specific scratch input pointers and table contents must be concretely included; no complete self-sufficient snapshot admitted yet',
      acquisition_plan='Request separately authorized, provenance-qualified coherent offline snapshot. Assess feasibility without acquiring it; no live debug/halting/readout authorized by this phase.')
    dump(out,'runtime-snapshot-minimum.json',snapshot)
    qualification=dict(status='PARTIAL',static_strategy='EXHAUSTED',conclusion='STATIC CHECKPOINT RECONSTRUCTION EXHAUSTED',
      event_admitted=admitted(False,False,False,False,False,'INSUFFICIENT EVIDENCE'),checkpoint_resume=False,
      blockers=['unavailable runtime scheduling/notification state','allocator/active patch state','long-lived DSP smoothing/envelope/filter histories','material CPU/AGU/loop/stack context'],
      original_instructions_executed=0,hardware_access=False,Plaits_input=False,
      next_step='Specify and obtain separate authorization for one provenance-qualified coherent original post-generation snapshot; do not run another broad static association phase')
    dump(out,'qualification.json',qualification)
    after={p:sha(p) for p in before}
    assert after==before
    for p,h in guards.items(): assert sha(p)==h
    dump(out,'validation.json',dict(status='TESTED static exporter checks; no firmware execution',
      input_hashes={str(p.relative_to(ROOT)):h for p,h in guards.items()},
      previous_report_hashes={str(p.relative_to(ROOT)):h for p,h in before.items()},
      inputs_unchanged=True,evidence=evidence,project_sha256=sha(project_path),
      vtable_validated=True,lane_mapping_validated=True,geometry_bounds_validated=True,
      header_length_not_guessed=True,exact_event_not_invented=True,event_admitted=False,stock_instructions_executed=0))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True)
    recover(Path(p.parse_args().output_dir))
