"""Six prior failures as adverse SRAM-reset inputs; native prefix only.
Old peripheral/CPU contexts are discarded. No same-boot cleanup/retry occurs.
"""
from trace import *
prior=json.loads((R/'builds/phase33-preservation-powercycle/powercycle.json').read_text())
rows=[]
for case in prior['cases'][1:]:
 state=case['pre_power_loss'];assert state['semaphore']==0 and state['sync']==1
 seed=[(0x20000380,b'\0'),(0x2000aca4,struct.pack('<I',state['sync'])),
  (0x20008d40,struct.pack('<I',int(state['Storage_flags'],16))),
  (0x20007758,struct.pack('<I',int(state['Main_flags'],16))),
  (0x2000a070,bytes([0x80+state['active_chunk']])*64)]
 row=run('application','diagnostic',clock_model=True,nor_init=True,nor_identity=True,tick_model=True,seed=seed,limit=600000)
 row['prior_case']=case['case'];row['prior_state']=state
 owner=row['initialized_ownership_prefix'];assert owner['semaphore']==1 and owner['sync']==0 and owner['pending']==0 and owner['Storage_flags']==0
 assert int(row['runtime_fields']['0x400264b8'],16)&1==0 and int(row['runtime_fields']['0x400264bc'],16)==0
 row['full_P2']='UNKNOWN: prefix is before stable user state; Main/Storage task execution not qualified'
 row['full_P3']='UNKNOWN: future persistent operations not traced'
 rows.append(row);print(case['case']+': native prefix rebuilt semaphore/sync/pending; complete restart UNKNOWN',flush=True)
(O/'restart-prefix.json').write_text(json.dumps(rows,indent=2)+'\n')
