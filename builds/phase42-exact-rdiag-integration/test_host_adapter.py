"""Framed Link reuse containment: no live Link construction or port calls."""
from test_end_to_end import FakeLink,Clock,O,request
from host import FramedTransport,DeviceLease,OneShot
from evidence_protocol import synthetic_packets
import tempfile,json
def main():
 rows=[];data=bytes(((i*73)^(i>>1)^0xa6)&255 for i in range(535));wire=b''.join(synthetic_packets(37,data))
 with tempfile.TemporaryDirectory(dir=O) as d:
  for i,(label,b) in enumerate([('normal',wire),('silence',b''),('truncated',wire[:-1]),('duplicate completion',wire+synthetic_packets(37,data)[-1])]):
   clock=Clock();link=FakeLink(clock,b);transport=FramedTransport(link,clock);lease=DeviceLease(transport,clock);capture=OneShot(lease,37);dest=O/d/str(i)
   result=capture.run(dest)
   assert result['status']==('SUCCESS' if label=='normal' else 'FAILED')
   try:FramedTransport(link,clock)
   except RuntimeError:pass
   else:raise AssertionError('same link rearmed')
   try:OneShot(lease,38).run(O/d/'retry')
   except RuntimeError:pass
   else:raise AssertionError('same lease reused')
   assert len(link.sent)==1 and link.sent[0]==request(37)
   rows.append(dict(case=label,confidence='PROVEN',requests=1,same_Link_rearm_rejected=True,same_lease_reuse_rejected=True,result=result))
 (O/'host-adapter-results.json').write_text(json.dumps(dict(confidence='PROVEN',cases=rows,case_count=len(rows),hardware_access=False),indent=2)+'\n');print('Host adapter cases PASS:',len(rows))
if __name__=='__main__':main()
