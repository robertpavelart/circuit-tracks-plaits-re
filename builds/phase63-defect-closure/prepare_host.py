"""Create new host from reviewed prior transport; never import WinMM here."""
from pathlib import Path
O=Path(__file__).resolve().parent;P=O.parent/'phase62-final-preflight'
s=(P/'live_host.py').read_text()
s=s.replace('Phase62','Phase63')
s=s.replace("GEOMETRY_SECONDS=10.;", "from status_protocol import parse as status_response\nGEOMETRY_SECONDS=10.;")
start=s.index("  frame=tx.receive(gd)")
end=s.index(" except (Exception,KeyboardInterrupt)",start)
s=s[:start]+'''  frame=tx.receive(gd)
  if clock()>=gd:raise TimeoutError('status deadline')
  status=status_response(frame,session)['status'];state=status
  if status=='FAILED':raise RuntimeError('device FAILED: full power cycle required')
  if status in ('NOT_READY','INVALID','UNSAFE'):
   # Observe the whole query window; reject duplicates/trailing replies.
   try:tx.receive(gd)
   except TimeoutError:
    if clock()<gd or tx.buffer:raise
   else:raise ValueError('duplicate/unexpected status')
   if status=='NOT_READY':marker.unlink();begun=False
   result=dict(message=('NOT_READY: query again later; no raw attempt consumed' if status=='NOT_READY' else status+': no authorization or raw request'))
  elif status!='READY':raise ValueError('unexpected initial status')
  else:
   frame=tx.receive(gd)
   if clock()>=gd:raise TimeoutError('geometry deadline')
   epoch,g,domains=validator(frame,session)
   if domains['targets_reachable']['0x82000'] or identity and domains['targets_reachable']['0x81000']:
    state='UNSAFE';result=dict(message='UNSAFE: no authorization or raw request')
   elif geometry_only:
    state='READY';result=dict(epoch=epoch,geometry=g.hex(),domains=domains)
   else:
    start=clock();deadline=start+RAW_SECONDS;emit(C.request(session,15,epoch,g,identity))
    if clock()-start>=AUTH_SEND_SECONDS:raise TimeoutError('authorization transmission deadline')
    state='AUTHORIZATION_SENT';receiver=C.Receiver(session,identity);authorized=False;success=False
    while True:
     try:frame=tx.receive(deadline)
     except TimeoutError:
      if clock()<deadline or tx.buffer or not receiver.done or not success:raise
      break
     if clock()>=deadline:raise TimeoutError('packet outside stage deadline')
     if frame[4]==0x4f:
      code=status_response(frame,session)['status']
      if code=='FAILED':raise RuntimeError('device FAILED: full power cycle required')
      if code=='AUTHORIZED' and not authorized and not receiver.parts and not success:authorized=True;state=code
      elif code=='SUCCESS' and authorized and receiver.done and not success:success=True
      else:raise ValueError('duplicate/out-of-order status')
     else:
      if not authorized or success:raise ValueError('raw before authorization / after success')
      receiver.accept(frame)
    h=C.Session(lambda b:(_ for _ in ()).throw(AssertionError('no send during publication')),clock,session,identity)
    h.state='ACTIVE';h.deadline=clock()+1;h.receiver=receiver;digest=h.finish(output)
    if digest is None:raise OSError('atomic publication failed')
    state='SUCCESS';result=dict(SHA256=digest,bytes=512)
''' +s[end:]
s=s.replace("state='FAILED_POST_SEND' if begun else 'FAILED_PRE_SEND'", "state='FAILED' if begun else 'FAILED_PRE_SEND'")
s=s.replace("state=='FAILED_POST_SEND'", "state=='FAILED'")
s=s.replace("state='UNSAFE';result=dict(message='UNSAFE: no authorization or raw request')", "state='UNSAFE';quiet(gd);result=dict(message='UNSAFE: no authorization or raw request')")
s=s.replace("state='READY';result=dict(epoch=epoch,geometry=g.hex(),domains=domains)", "state='READY';quiet(gd);result=dict(epoch=epoch,geometry=g.hex(),domains=domains)")
s=s.replace(" try:\n  if not preflight_pass:", " def quiet(deadline):\n  try:tx.receive(deadline)\n  except TimeoutError:\n   if clock()<deadline or tx.buffer:raise\n  else:raise ValueError('unexpected trailing response')\n try:\n  if not preflight_pass:")
s=s.replace("('SUCCESS','GEOMETRY_SAFE','UNSAFE')", "('SUCCESS','READY','NOT_READY','INVALID','UNSAFE')")
(O/'live_host.py').write_text(s)
(O/'ctremote_transport.py').write_bytes((P/'ctremote_transport.py').read_bytes())
print('New explicit-status host written; live CLI remains gated')
if __name__=='__main__':pass
