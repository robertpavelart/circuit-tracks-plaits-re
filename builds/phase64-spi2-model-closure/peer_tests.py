"""Wire completion and prefetch tests; no firmware mutation or device I/O."""
from pathlib import Path
import json
from dsp_peer import BootPeer,UnknownPeerRead
O=Path(__file__).resolve().parent
def transfer(p,word,command,lr=0x080291f8):
 p.command=command;p.word(word>>16,(word>>8)&255,word&255,lr)
 return int.from_bytes(bytes(p.byte(b) for b in word.to_bytes(3,'big')),'big')
def read(p,address):
 transfer(p,0x800000|address,True,0x08029508)
 return transfer(p,0x400000,True,0x08029512)
def main():
 rows=[]
 p=BootPeer();assert read(p,0x802b)==0;rows.append(dict(case='boot-ready absent without XFFF wire write',passed=True))
 p.arm_write(0,0x100,0xfff);assert read(p,0x802b)==0;rows.append(dict(case='uncompleted ARM request cannot make DSP ready',passed=True))
 transfer(p,0x000fff,True);transfer(p,1,False);assert read(p,0x802b)==1;rows.append(dict(case='ready after completed marker word',passed=True))
 assert read(p,0x802c)==0x800000;rows.append(dict(case='native boot mailbox idle',passed=True))
 p.memory['X']={int(k,16):int(v,16) for k,v in json.loads((O/'peer-memory.json').read_text())['memory']['X'].items()} # isolated contract fixture, never startup state
 transfer(p,0x00802c,True);transfer(p,0x080002,False)
 assert read(p,0x802c)==0x080002 and read(p,0x802c)==0x800000;rows.append(dict(case='qualified exact job2 busy before completion',passed=True))
 transfer(p,0x00802c,True);transfer(p,0x094403,False)
 assert read(p,0x802c)==0x094403 and read(p,0x802c)==0x800000;rows.append(dict(case='qualified exact job3 busy before completion',passed=True))
 for word in (0x0a8804,0x0bcc05):
  transfer(p,0x00802c,True);transfer(p,word,False)
  assert read(p,0x802c)==word and read(p,0x802c)==0x800000;rows.append(dict(case=f'qualified exact job{word&255} busy before completion',passed=True))
 try:transfer(p,0x00802c,True);transfer(p,0x0d1000,False)
 except UnknownPeerRead:rows.append(dict(case='unsupported deferred job blocks model',passed=True))
 else:raise AssertionError('fabricated deferred completion')
 p=BootPeer()
 try:transfer(p,0x200100,True)
 except UnknownPeerRead:rows.append(dict(case='unmodeled 16-bit bulk transition blocks model',passed=True))
 else:raise AssertionError('silently ignored width transition')
 p=BootPeer()
 try:read(p,0x8030)
 except UnknownPeerRead:rows.append(dict(case='unknown consumed readback blocks model',passed=True))
 else:raise AssertionError('fabricated readback')
 (O/'peer-tests.json').write_text(json.dumps(dict(confidence='PROVEN',passed=True,cases=rows,scope='contract tests plus separately recorded native DSP producer tests; no full DSP task scheduler assertion'),indent=2)+'\n');print('Peer contract cases PASS',len(rows))
if __name__=='__main__':main()
